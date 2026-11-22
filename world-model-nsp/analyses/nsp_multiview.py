#!/usr/bin/env python3
"""
E2 多投影监督 —— 合成数据方法学诊断（synthetic diagnostic）。

检验的命题（H2，源自 CF-WAM arXiv:2609.34414 的动态多投影监督）：
  单一固定 next-state 表征是当前瓶颈；视觉/语义/几何/交互多投影监督能提升跨本体泛化。

合成类比：
  - 潜状态 s (ds 维) 通过 4 个互补投影观测：visual/semantic/geometric/interaction。
    每个投影只耦合 s 的一个子空间（信息互补，模拟不同传感模态看到状态的不同侧面）。
  - 任务：给定 4 视图历史窗口 + action 历史，预测下一潜状态 s_next。
  - 跨本体 (cross-embodiment)：eval 时把 visual 投影矩阵换成扰动版本（模拟换相机/本体
    导致的观测量纲/视角变化），其他投影不变。

两臂：
  - single : 只用 visual 视图（信息只覆盖 1/4 子空间）
  - multi  : 4 个视图各自投影后 concat（信息覆盖全部子空间）

诚实边界：这不是 CF-WAM 数值复现，也不假装参数量严格相等（multi 输入维度更大，记录之）。
它只回答两个可证伪子问题：
  Q1 信息互补是否让 multi 的 in-dist 状态预测误差更低（预期是，但不免费）。
  Q2 multi 对单一投影扰动是否更鲁棒（误差上升比例更小）——这才是"跨本体泛化"的核心类比。

用法:
  python3 nsp_multiview.py --mode smoke  --out /tmp/mv_smoke.json
  python3 nsp_multiview.py --mode full   --out /tmp/mv_full.json
  python3 nsp_multiview.py --selftest
"""
import argparse, json, math, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

ACTS = 4
NVIEW = 4
VIEW_NAMES = ('visual', 'semantic', 'geometric', 'interaction')

# ----------------------------- data ----------------------------------------
def make_dynamics(seed, ds, act_dim, rho=0.9, act_scale=1.0):
    """稳定线性动力 + 4 个互补投影。每个投影只看 s 的一个子空间块。"""
    rng = np.random.default_rng(seed)
    Q, _ = np.linalg.qr(rng.normal(size=(ds, ds)))
    A = rho * Q
    B = rng.normal(size=(ds, ACTS)) / math.sqrt(ACTS) * act_scale
    assert ds % NVIEW == 0, 'ds 必须被 4 整除（4 个投影各看一块）'
    block = ds // NVIEW
    Cs = []
    for v in range(NVIEW):
        Cv = np.zeros((block, ds), dtype=np.float32)
        lo, hi = v * block, (v + 1) * block
        Qv, _ = np.linalg.qr(rng.normal(size=(block, block)))
        Cv[:, lo:hi] = Qv / math.sqrt(block)   # 只观测本块子空间
        Cs.append(Cv.astype(np.float32))
    return A.astype(np.float32), B.astype(np.float32), Cs

def gen_traj(A, B, Cs, seed, n_traj, T, view_noise=0.05):
    rng = np.random.default_rng(seed)
    ds = A.shape[0]
    S = np.zeros((n_traj, T + 1, ds), dtype=np.float32)
    VIEWS = np.zeros((NVIEW, n_traj, T, Cs[0].shape[0]), dtype=np.float32)
    AC = np.zeros((n_traj, T), dtype=np.int64)
    eye = np.eye(ACTS, dtype=np.float32)
    for i in range(n_traj):
        S[i, 0] = rng.normal(size=ds) * 0.3
        for t in range(T):
            AC[i, t] = rng.integers(0, ACTS)
            S[i, t + 1] = A @ S[i, t] + B @ eye[AC[i, t]] + 0.02 * rng.normal(size=ds)
            for v in range(NVIEW):
                VIEWS[v, i, t] = Cs[v] @ S[i, t] + view_noise * rng.normal(size=Cs[v].shape[0])
    return S, VIEWS, AC

def perturb_view(C, seed, eps=0.3):
    """跨本体类比：给一个投影矩阵加结构性扰动（旋转+幅度变化）。"""
    rng = np.random.default_rng(seed)
    d_out, d_state = C.shape
    Q, _ = np.linalg.qr(rng.normal(size=(d_out, d_out)))
    # 幅度扰动逐元素 + 旋转扰动左乘正交阵，两者都保持 (d_out, d_state)
    return (C * (1 + eps * rng.normal(size=C.shape)) + eps * 0.1 * Q @ C).astype(np.float32)

# ----------------------------- model ---------------------------------------
class Arm(nn.Module):
    def __init__(self, mode, view_dim, ds, K, dm, layers, heads):
        super().__init__()
        self.mode, self.K, self.ds = mode, K, ds
        self.view_proj = nn.ModuleList([nn.Linear(view_dim, dm // NVIEW if mode == 'multi' else dm)
                                         for _ in range(NVIEW if mode == 'multi' else 1)])
        self.act_emb = nn.Embedding(ACTS, dm)
        self.pos = nn.Parameter(torch.randn(K, dm) * 0.02)
        enc = nn.TransformerEncoderLayer(d_model=dm, nhead=heads, dim_feedforward=dm * 2,
                                         dropout=0.0, batch_first=True, norm_first=False)
        self.tr = nn.TransformerEncoder(enc, layers, norm=nn.LayerNorm(dm))
        self.head = nn.Linear(dm, ds)

    def forward(self, views, acts):
        # views: (nview, B, K, view_dim)
        vs = self.view_proj[0](views[0])
        if self.mode == 'multi':
            parts = [vs] + [self.view_proj[i](views[i]) for i in range(1, NVIEW)]
            vs = torch.cat(parts, dim=-1)
        x = vs + self.act_emb(acts) + self.pos
        return self.head(self.tr(x)[:, -1, :])

# ----------------------------- train ---------------------------------------
def train_arm(mode, cfg, S, VIEWS, AC, seed, device):
    torch.manual_seed(seed)
    m = Arm(mode, cfg['view_dim'], cfg['ds'], cfg['K'], cfg['dm'], cfg['layers'], cfg['heads']).to(device)
    opt = torch.optim.AdamW(m.parameters(), lr=cfg['lr'], weight_decay=1e-4)
    n_traj, T, K = S.shape[0], S.shape[1] - 1, cfg['K']
    g = torch.Generator(device=device).manual_seed(seed + 999)
    S_t = torch.as_tensor(S, device=device)
    V_t = torch.as_tensor(VIEWS, device=device)
    A_t = torch.as_tensor(AC, device=device)
    for step in range(cfg['steps']):
        idx = torch.randint(0, n_traj, (cfg['batch'],), generator=g, device=device)
        t = torch.randint(0, T - K, (cfg['batch'],), generator=g, device=device)
        win_v = torch.stack([V_t[:, idx, t + j] for j in range(K)], dim=2)  # (nview,B,K,vd)
        win_a = torch.stack([A_t[idx, t + j] for j in range(K)], dim=1)
        out = m(win_v, win_a)
        loss = F.mse_loss(out, S_t[idx, t + K])
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    return m

# ----------------------------- eval ----------------------------------------
@torch.no_grad()
def eval_mse(model, cfg, VIEWS_eval, AC_eval, S_eval, device):
    """一次性teacher-forcing式的单步预测 MSE + 短程自回归 MSE（state 空间）。"""
    m = model.eval()
    K = cfg['K']
    V = torch.as_tensor(VIEWS_eval, device=device)
    A = torch.as_tensor(AC_eval, device=device)
    St = torch.as_tensor(S_eval, device=device)
    # 单步预测 MSE：用前 K 步视图预测第 K 步之后的 state
    win_v = V[:, :, :K]
    win_a = A[:, :K]
    pred = m(win_v, win_a)
    mse1 = F.mse_loss(pred, St[:, K]).item()
    return {'mse_step1': round(mse1, 6)}

def run(cfg, device):
    t0 = time.time()
    A, B, Cs = make_dynamics(cfg['seed'], cfg['ds'], ACTS, rho=cfg['rho'])
    # 训练集
    S, VIEWS, AC = gen_traj(A, B, Cs, cfg['seed'] + 777, cfg['n_traj'], cfg['T'])
    # 评测集：同一动力学/投影，不同初值+action（in-dist）
    Se, Ve, Ae = gen_traj(A, B, Cs, cfg['eval_seed'], cfg['n_eval'], cfg['K'] + 1)
    # 跨本体评测：扰动 visual 投影，重新生成视图（state 轨迹相同）
    Cs_p = [c.copy() for c in Cs]
    Cs_p[0] = perturb_view(Cs[0], cfg['eval_seed'] + 1, eps=cfg['perturb_eps'])
    _, Vp, Ap = gen_traj(A, B, Cs_p, cfg['eval_seed'], cfg['n_eval'], cfg['K'] + 1)
    per_seed = []
    for sd in range(cfg['seeds']):
        row = {'seed': sd}
        for mode in ('single', 'multi'):
            mcfg = dict(cfg); mcfg['mode'] = mode
            m = train_arm(mode, mcfg, S, VIEWS, AC, cfg['seed'] * 100 + sd, device)
            ind = eval_mse(m, mcfg, Ve, Ae, Se, device)
            cross = eval_mse(m, mcfg, Vp, Ap, Se, device)   # 同一 Se（真 state 不变）
            row[mode] = {
                'in_dist_mse': ind['mse_step1'],
                'cross_emb_mse': cross['mse_step1'],
                'degradation_ratio': round(cross['mse_step1'] / max(ind['mse_step1'], 1e-9), 3),
                'n_params': sum(p.numel() for p in m.parameters()),
            }
        per_seed.append(row)
    # 聚合
    agg = {}
    for mode in ('single', 'multi'):
        rows = [r[mode] for r in per_seed]
        agg[mode] = {k: round(float(np.mean([r[k] for r in rows])), 6)
                     for k in ('in_dist_mse', 'cross_emb_mse', 'degradation_ratio')}
        agg[mode]['degradation_std'] = round(float(np.std([r['degradation_ratio'] for r in rows])), 6)
        agg[mode]['n_params'] = rows[0]['n_params']
    verdict = {
        'q1_multi_better_indist': agg['multi']['in_dist_mse'] < agg['single']['in_dist_mse'],
        'q2_multi_more_robust': agg['multi']['degradation_ratio'] < agg['single']['degradation_ratio'],
    }
    return {'cfg': cfg, 'device': torch.cuda.get_device_name(0) if device.type == 'cuda' else 'cpu',
            'elapsed_s': round(time.time() - t0, 2),
            'per_seed': per_seed, 'aggregate': agg, 'verdict': verdict}

def selftest():
    rng = np.random.default_rng(0)
    C = rng.normal(size=(6, 12)).astype(np.float32)
    Cp = perturb_view(C, 1, eps=0.3)
    assert Cp.shape == C.shape and not np.allclose(C, Cp), 'perturb failed'
    # 扰动要温和：相对 Frobenius 变化 0.05~2.0
    rel = np.linalg.norm(Cp - C) / np.linalg.norm(C)
    assert 0.01 < rel < 2.0, f'perturb magnitude odd: {rel}'
    print(json.dumps({'selftest': 'PASS', 'perturb_rel_fro': round(float(rel), 4)}))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['smoke', 'full'], default='smoke')
    ap.add_argument('--out', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if a.mode == 'smoke':
        cfg = dict(seed=23, eval_seed=923, ds=12, view_dim=3, K=5, dm=48, layers=2, heads=4,
                   n_traj=256, T=60, steps=150, batch=96, seeds=1, n_eval=16,
                   rho=0.9, perturb_eps=0.3, lr=2e-3)
    else:
        cfg = dict(seed=23, eval_seed=923, ds=12, view_dim=3, K=6, dm=64, layers=2, heads=4,
                   n_traj=512, T=80, steps=800, batch=128, seeds=3, n_eval=32,
                   rho=0.9, perturb_eps=0.3, lr=2e-3)
    torch.cuda.set_per_process_memory_fraction(0.15)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    res = run(cfg, device)
    txt = json.dumps(res, indent=2, ensure_ascii=False)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(txt + '\n')
        print('WROTE', a.out)
    print(json.dumps({'mode': a.mode, 'device': res['device'], 'elapsed_s': res['elapsed_s'],
                      'aggregate': res['aggregate'], 'verdict': res['verdict']},
                     indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
