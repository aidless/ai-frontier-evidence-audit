#!/usr/bin/env python3
"""
NSP 三臂对照 —— 合成数据方法学诊断（synthetic diagnostic）。

检验的可证伪命题（H1 收窄版，源自 arXiv:2505.14892 的反证）：
  在同一个 backbone、同一数据、同一算力预算下，"预测下一潜状态(action-conditioned NSP)"
  相对于 "预测下一 token" / "预测下一 frame"，在长时程自回归 rollout 上的误差累积斜率更低。

三臂唯一差别 = 监督目标/输出头：
  - token : 输出 frame 的每维 16 级离散 id（交叉熵）；rollout 时反量化
  - frame : 输出 frame 向量（MSE）；rollout 时直接喂回
  - state : 输出生成该 frame 的潜状态 s（MSE）；rollout 时经 C 映射回 frame

公平性控制：三臂看到完全相同的输入(frame 历史窗口 + action 历史窗口)、相同 eval 集、
相同的真实 action 未来序列；评测统一在 frame 空间的 MSE 上(horizon 10/100/1000)。

诚实边界：这是合成线性动力系统上的方法学诊断，不是复现任何论文的数值结果。
它只回答"目标抽象层级是否影响长时程稳定性"，不回答"某模型是否真的在做 NSP"。

用法:
  python3 nsp_three_arm.py --mode smoke  --out /tmp/nsp_smoke.json
  python3 nsp_three_arm.py --mode full   --out /tmp/nsp_full.json
  python3 nsp_three_arm.py --selftest
"""
import argparse, json, math, time, sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

LEVELS = 16
QLO, QHI = -3.0, 3.0
ACTS = 4
# 密 horizon 网格：slope 用多点回归，避免两点连线的假斜率
KS_GRID = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

# ----------------------------- data ----------------------------------------
def make_dynamics(seed, ds, df, rho=0.75, act_scale=1.0):
    """生成一套固定动力学 (A,B,C)。train/eval 必须共享同一套，公平性前提。"""
    rng = np.random.default_rng(seed)
    Q, _ = np.linalg.qr(rng.normal(size=(ds, ds)))
    A = rho * Q                                          # stable: 谱半径 rho<1
    B = rng.normal(size=(ds, ACTS)) / math.sqrt(ACTS) * act_scale
    C_raw = rng.normal(size=(df, ds)) / math.sqrt(ds)
    # 把 frame 幅度归一到 std≈1，避开 16 级量化(Q=±3)饱和区
    sigma_s = math.sqrt((act_scale ** 2 + 0.02 ** 2) / (1 - rho ** 2))
    C = (C_raw / sigma_s).astype(np.float32)
    return A.astype(np.float32), B.astype(np.float32), C

def gen_traj(A, B, C, seed, n_traj, T):
    """用给定动力学生成 n_traj 条轨迹（不同初值/action，但共享 A/B/C）。"""
    rng = np.random.default_rng(seed)
    ds, df = A.shape[0], C.shape[0]
    S = np.zeros((n_traj, T + 1, ds), dtype=np.float32)
    FR = np.zeros((n_traj, T, df), dtype=np.float32)
    AC = np.zeros((n_traj, T), dtype=np.int64)
    eye = np.eye(ACTS, dtype=np.float32)
    for i in range(n_traj):
        S[i, 0] = rng.normal(size=ds) * 0.3
        for t in range(T):
            AC[i, t] = rng.integers(0, ACTS)
            S[i, t + 1] = A @ S[i, t] + B @ eye[AC[i, t]] + 0.02 * rng.normal(size=ds)
            FR[i, t] = C @ S[i, t] + 0.02 * rng.normal(size=df)
    return S, FR, AC

def gen_data(seed, n_traj, T, ds, df, K, rho=0.75):
    """兼容旧诊断脚本的 wrapper：返回轨迹 + 动力学。"""
    A, B, C = make_dynamics(seed, ds, df, rho=rho)
    S, FR, AC = gen_traj(A, B, C, seed + 777, n_traj, T)
    return S, FR, AC, (A, B, C)

def quantize(f):
    q = np.clip(np.round((f - QLO) / (QHI - QLO) * (LEVELS - 1)), 0, LEVELS - 1)
    return torch.as_tensor(q, dtype=torch.long)

def dequant(q):
    return q.to(torch.float32) / (LEVELS - 1) * (QHI - QLO) + QLO

# ----------------------------- model ---------------------------------------
class Arm(nn.Module):
    def __init__(self, mode, df, ds, K, dm, layers, heads):
        super().__init__()
        self.mode, self.K, self.df, self.ds = mode, K, df, ds
        self.frame_proj = nn.Linear(df, dm)
        self.act_emb = nn.Embedding(ACTS, dm)
        self.pos = nn.Parameter(torch.randn(K, dm) * 0.02)
        enc = nn.TransformerEncoderLayer(d_model=dm, nhead=heads,
                                         dim_feedforward=dm * 2, dropout=0.0,
                                         batch_first=True, norm_first=False)
        self.tr = nn.TransformerEncoder(enc, layers, norm=nn.LayerNorm(dm))
        if mode == 'token':
            self.head = nn.Linear(dm, df * LEVELS)
        elif mode == 'frame':
            self.head = nn.Linear(dm, df)
        elif mode == 'state':
            self.head = nn.Linear(dm, ds)
        else:
            raise ValueError(mode)

    def forward(self, frames, acts):
        x = self.frame_proj(frames) + self.act_emb(acts) + self.pos
        h = self.tr(x)[:, -1, :]
        return self.head(h)

# ----------------------------- train ---------------------------------------
def train_arm(mode, cfg, S, FR, AC, seed, device):
    torch.manual_seed(seed)
    m = Arm(mode, cfg['df'], cfg['ds'], cfg['K'], cfg['dm'], cfg['layers'], cfg['heads']).to(device)
    opt = torch.optim.AdamW(m.parameters(), lr=cfg['lr'], weight_decay=1e-4)
    n_traj, T, K = FR.shape[0], FR.shape[1], cfg['K']
    g = torch.Generator(device=device).manual_seed(seed + 999)
    S_t = torch.as_tensor(S, device=device)
    FR_t = torch.as_tensor(FR, device=device)
    AC_t = torch.as_tensor(AC, device=device)
    qFR = quantize(FR).to(device)   # (n,T,df) token ids
    for step in range(cfg['steps']):
        idx = torch.randint(0, n_traj, (cfg['batch'],), generator=g, device=device)
        t = torch.randint(0, T - K, (cfg['batch'],), generator=g, device=device)
        win_f = torch.stack([FR_t[idx, t + j] for j in range(K)], dim=1)
        win_a = torch.stack([AC_t[idx, t + j] for j in range(K)], dim=1)
        out = m(win_f, win_a)
        if mode == 'token':
            tgt = torch.stack([qFR[idx, t + K, d] for d in range(cfg['df'])], dim=1)  # (B,df)
            loss = F.cross_entropy(out.view(-1, LEVELS), tgt.reshape(-1))
        elif mode == 'frame':
            loss = F.mse_loss(out, FR_t[idx, t + K])
        else:  # state: frame[t] = C s[t], so target state is S[..., t+K]
            loss = F.mse_loss(out, S_t[idx, t + K])
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    return m

# ----------------------------- rollout -------------------------------------
@torch.no_grad()
def rollout_mse(model, cfg, FR0, ACpast, ACfuture, Strue, FRtrue, C_t, device,
                action_ablate=False):
    """批量自回归 rollout，统一在 frame 空间测 MSE。返回 {horizon: mse}。"""
    m = model.eval()
    E, K = FR0.shape[0], cfg['K']
    H = ACfuture.shape[1]
    Ks = [h for h in KS_GRID if h <= H]
    win_f = FR0.to(device)
    win_a = ACpast.to(device)
    acf = ACfuture.to(device)
    if action_ablate:                       # 反证：打乱未来 action，证明模型确实用了它
        acf = acf[torch.randperm(E, device=device)]
    fr_true = FRtrue.to(device)
    mse_at = {}
    for h in range(1, H + 1):
        out = m(win_f, win_a)
        if cfg['mode'] == 'token':
            fhat = dequant(out.view(E, cfg['df'], LEVELS).argmax(-1))
        elif cfg['mode'] == 'frame':
            fhat = out
        else:
            fhat = out @ C_t.to(device).T
        if h in Ks:
            mse_at[h] = F.mse_loss(fhat, fr_true[:, h - 1]).item()  # FRtrue[:,0]=step1
        win_f = torch.cat([win_f[:, 1:, :], fhat.unsqueeze(1)], dim=1)
        win_a = torch.cat([win_a[:, 1:], acf[:, h - 1:h]], dim=1)
    return mse_at

def make_eval(cfg, A, B, C, device):
    """取 eval 轨迹：前 K 步作 warmup，之后 H 步作 rollout(记录真值)。
    关键：用训练时的同一套 (A,B,C)，只换随机初值与 action 流——否则 state 臂
    用训练 C 映射回 frame 时 C 错位，三臂不公平。"""
    K, H = cfg['K'], cfg['H']
    n = cfg['n_eval']
    Se, Fe, Ae = gen_traj(A, B, C, cfg['eval_seed'], n, K + H)
    FR0 = torch.as_tensor(Fe[:, :K], dtype=torch.float32)
    ACp = torch.as_tensor(Ae[:, :K], dtype=torch.long)
    ACf = torch.as_tensor(Ae[:, K:K + H], dtype=torch.long)
    FRtrue = torch.as_tensor(Fe[:, K:K + H], dtype=torch.float32)   # (n,H,df)
    return FR0, ACp, ACf, torch.as_tensor(Se), FRtrue

# ----------------------------- metrics -------------------------------------
def slope(mse):
    """log10(MSE) 对 log10(horizon) 的斜率。"""
    hs = sorted(mse)
    if len(hs) < 2:
        return float('nan')
    x = np.log10(hs); y = np.log10([mse[h] for h in hs])
    return float(np.polyfit(x, y, 1)[0])

def run(cfg, device):
    t0 = time.time()
    S, FR, AC, (A, B, C) = gen_data(cfg['seed'], cfg['n_traj'], cfg['T'],
                                   cfg['ds'], cfg['df'], cfg['K'], rho=cfg.get('rho', 0.75))
    C_t = torch.as_tensor(C, dtype=torch.float32)
    eval_pack = make_eval(cfg, A, B, C, device)   # 三臂共享同一动力学，公平性前提
    # smoke 的 H 可能 < 1000，取密网格里实际存在的最远 horizon
    max_h = max(h for h in KS_GRID if h <= cfg['H'])
    min_h = min(h for h in KS_GRID if h <= cfg['H'])
    per_seed = []
    for sd in range(cfg['seeds']):
        row = {'seed': sd}
        models = {}
        for mode in ('token', 'frame', 'state'):
            mcfg = dict(cfg); mcfg['mode'] = mode
            m = train_arm(mode, mcfg, S, FR, AC, cfg['seed'] * 100 + sd, device)
            models[mode] = m
            ms = rollout_mse(m, mcfg, *eval_pack, C_t, device)
            row[mode] = {'mse': {str(k): round(v, 6) for k, v in ms.items()},
                         'slope': round(slope(ms), 4),
                         'n_params': sum(p.numel() for p in m.parameters())}
        # selftest A: 三臂 eval 集一致（同一 FRtrue）——由构造保证，显式断言
        assert eval_pack[4].shape == (cfg['n_eval'], cfg['H'], cfg['df'])
        # selftest B: 单调性 —— 长 horizon 误差应大于短 horizon
        assert row['state']['mse'][str(max_h)] > row['state']['mse'][str(min_h)], 'state arm non-monotone'
        # selftest C: action 消融 —— 打乱 action 后 state 臂长程误差应上升(非空性反证)
        mstate = models['state']
        mcfg = dict(cfg); mcfg['mode'] = 'state'
        ms_abl = rollout_mse(mstate, mcfg, *eval_pack, C_t, device, action_ablate=True)
        row['action_ablation'] = {'max_horizon': max_h,
                                  'state_mse_far_normal': row['state']['mse'][str(max_h)],
                                  'state_mse_far_shuffled_action': round(ms_abl[max_h], 6),
                                  'ratio': round(ms_abl[max_h] / row['state']['mse'][str(max_h)], 3)}
        per_seed.append(row)
    # 聚合（mse_far = 实际最远 horizon，smoke=100 / full=1000）
    agg = {}
    for mode in ('token', 'frame', 'state'):
        ss = [r[mode]['slope'] for r in per_seed]
        mfar = [r[mode]['mse'][str(max_h)] for r in per_seed]
        agg[mode] = {'slope_mean': round(float(np.mean(ss)), 4),
                     'slope_std': round(float(np.std(ss)), 4),
                     'mse_far_horizon': max_h,
                     'mse_far_mean': round(float(np.mean(mfar)), 6),
                     'mse_far_std': round(float(np.std(mfar)), 6),
                     'n_params': per_seed[0][mode]['n_params']}
    verdict = {
        'state_slope_lower_than_token': agg['state']['slope_mean'] < agg['token']['slope_mean'],
        'state_slope_lower_than_frame': agg['state']['slope_mean'] < agg['frame']['slope_mean'],
        'action_ablation_ratio_mean': round(float(np.mean(
            [r['action_ablation']['ratio'] for r in per_seed])), 3),
    }
    return {'cfg': {k: v for k, v in cfg.items() if k not in ()},
            'device': torch.cuda.get_device_name(0) if device.type == 'cuda' else 'cpu',
            'elapsed_s': round(time.time() - t0, 2),
            'per_seed': per_seed, 'aggregate': agg, 'verdict': verdict}

def selftest():
    """轻量结构测试：不训练，只验证 quantize/dequant 与 slope 的尺度行为。"""
    f = np.linspace(QLO, QHI, 10, dtype=np.float32).reshape(1, -1)
    q = quantize(f)
    assert q.shape == f.shape and int(q.min()) >= 0 and int(q.max()) < LEVELS
    d = dequant(q).numpy()
    assert np.all(np.abs(d - f) < 0.25), 'dequant error too large'
    s_inc = slope({10: 0.01, 100: 0.1, 1000: 1.0})
    s_flat = slope({10: 0.5, 100: 0.5, 1000: 0.5})
    assert s_inc > 0.9 and abs(s_flat) < 1e-6, f'slope broken: {s_inc},{s_flat}'
    print(json.dumps({'selftest': 'PASS', 'slope_increasing': round(s_inc, 3),
                      'slope_flat': round(s_flat, 6), 'dequant_max_err': round(float(np.abs(d-f).max()), 4)}))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['smoke', 'full'], default='smoke')
    ap.add_argument('--out', default=None)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        selftest(); return
    if args.mode == 'smoke':
        cfg = dict(seed=11, eval_seed=911, ds=10, df=40, K=6, dm=64, layers=2, heads=4,
                   n_traj=256, T=140, steps=150, batch=96, seeds=1, n_eval=8,
                   H=200, lr=2e-3, rho=0.95)
    else:
        cfg = dict(seed=11, eval_seed=911, ds=12, df=48, K=8, dm=96, layers=2, heads=4,
                   n_traj=512, T=1120, steps=1200, batch=128, seeds=3, n_eval=24,
                   H=1000, lr=2e-3, rho=0.95)
    torch.cuda.set_per_process_memory_fraction(0.15)  # 共享机器，礼貌限显存
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    res = run(cfg, device)
    txt = json.dumps(res, indent=2, ensure_ascii=False)
    if args.out:
        open(args.out, 'w', encoding='utf-8').write(txt + '\n')
        print(f'WROTE {args.out}')
    print(json.dumps({'mode': args.mode, 'device': res['device'],
                      'elapsed_s': res['elapsed_s'], 'aggregate': res['aggregate'],
                      'verdict': res['verdict']}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
