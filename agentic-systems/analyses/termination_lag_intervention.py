#!/usr/bin/env python3
"""E1 / agentic-systems: 终止延迟早停干预的合成轨迹诊断。

性质：**合成轨迹方法学诊断**，非 Termination Lag (arXiv:2611.14960) 数值复现。
论文的 oracle 是离线重算（逐 step 记录 patch 后 evaluate each distinct patch
offline），首正确 patch 处停可消除中位 35–60% 步骤且保留所有原本解决的任务。
但在线部署时 agent 不知道当前 patch 是否已正确——需要廉价正确性检测器。

可证伪命题（预注册）：
  "首次正确 patch 后强制退出"的在线干预能否降低撤销率且不损成功率，
  取决于正确性检测器的假阳性率 (FPR) 而非召回率 (1-FNR)。

装置：合成 patch 轨迹（非真实 agent、非 GPU 需求），三臂对照：
  - baseline：跑到终点
  - oracle：在 ground-truth 首个正确 patch 处停（离线预知，上界）
  - detector：在廉价检测器首次报 correct 时停（在线可部署，可调 FPR/FNR）

校准锚点：baseline 撤销率调到论文观察的 1–8% 区间（量级对齐，非结论）。
反证：FPR=1/FNR=0、FPR=0/FNR=1、完美检测器三点必须分别判 false/false/true。
"""
import argparse
import json
import math

import numpy as np


def gen_trials(cfg, rng):
    """生成合成 patch 轨迹。返回 dict of numpy arrays, shape (n_trials,)."""
    n = cfg["n_trials"]
    T = rng.integers(cfg["t_min"], cfg["t_max"] + 1, size=n)          # 步数
    # 首次正确位置 k*: 以 q_first 概率在首步即正确（论文 38-82% 首次编辑即正确）
    first_ok = rng.random(n) < cfg["q_first"]
    k_star = np.where(first_ok, 1, rng.integers(2, cfg["t_max"] + 1, size=n))
    k_star = np.minimum(k_star, T)

    # k* 之后 patch 处于 correct，但每步以 p_undo 被改坏；坏后下一步以 p_refix 修回
    undo_flags = rng.random((n, cfg["t_max"] + 2)) < cfg["p_undo"]
    refix_flags = rng.random((n, cfg["t_max"] + 2)) < cfg["p_refix"]

    correct_at_T = np.zeros(n, dtype=bool)
    for i in range(n):
        t = int(k_star[i]); cur = True
        while t < T[i]:
            t += 1
            if cur and undo_flags[i, t]:
                cur = False
            elif (not cur) and refix_flags[i, t]:
                cur = True
        correct_at_T[i] = cur
    return {"T": T, "k_star": k_star, "correct_at_T": correct_at_T,
            "undo": undo_flags, "refix": refix_flags}


def true_state_at(i, tau, trials):
    """重建第 i 条轨迹在 tau 步时的真实 correct 状态（从 k* 起按 undo/refix 演化）。"""
    k = int(trials["k_star"][i]); cur = True
    if tau < k:
        return False
    for t in range(k + 1, tau + 1):
        if cur and trials["undo"][i, t]:
            cur = False
        elif (not cur) and trials["refix"][i, t]:
            cur = True
    return cur


def detector_stop(trials, fpr, fnr, rng):
    """在线检测器：每步 t 用 true_state_at 观测真实 c[t]，按 FPR/FNR 报 correct；
    首次报处停。返回 tau（停止步）, correct_at_tau（停止时真实正确）。"""
    n = len(trials["T"])
    tau = np.empty(n, dtype=int)
    corr_tau = np.empty(n, dtype=bool)
    for i in range(n):
        T = int(trials["T"][i])
        stopped = False
        for t in range(1, T + 1):
            c_true = true_state_at(i, t, trials)
            if c_true:
                report = rng.random() >= fnr      # 真确时以 1-FNR 报正确
            else:
                report = rng.random() < fpr       # 未确时以 FPR 误报正确
            if report:
                tau[i] = t
                corr_tau[i] = c_true
                stopped = True
                break
        if not stopped:
            tau[i] = T
            corr_tau[i] = true_state_at(i, T, trials)
    return tau, corr_tau


def analyze(cfg):
    rng = np.random.default_rng(cfg["seed"])
    trials = gen_trials(cfg, rng)
    n = len(trials["T"])
    T = trials["T"]; k = trials["k_star"]

    # baseline：跑到终点
    base_success = float(np.mean(trials["correct_at_T"]))
    base_undo = float(np.mean((k <= T) & (~trials["correct_at_T"])))
    base_steps = float(np.mean(T))

    # oracle：在首正确 patch 处停（离线预知），成功保留，撤销 0
    oracle_steps = float(np.mean(k))
    oracle_success = 1.0
    oracle_undo = 0.0

    # detector 网格
    grid = []
    for fpr in cfg["fpr_grid"]:
        for fnr in cfg["fnr_grid"]:
            tau, corr_tau = detector_stop(trials, fpr, fnr, np.random.default_rng(cfg["seed"] + 1))
            d_success = float(np.mean(corr_tau))
            d_undo = float(np.mean((k <= tau) & (~corr_tau)))
            d_steps = float(np.mean(tau))
            step_save = 1.0 - d_steps / base_steps
            # 判据：撤销率降 ≥3pp 且 ≤2%，成功率不降 >1pp
            undo_ok = (d_undo <= base_undo - 0.03) and (d_undo <= 0.02)
            succ_ok = d_success >= base_success - 0.01
            effective = bool(undo_ok and succ_ok)
            grid.append({
                "fpr": fpr, "fnr": fnr,
                "success": round(d_success, 4),
                "undo_rate": round(d_undo, 4),
                "steps": round(d_steps, 2),
                "step_save_frac": round(step_save, 4),
                "undo_ok": undo_ok, "success_ok": succ_ok,
                "effective": effective,
            })

    eff = [g for g in grid if g["effective"]]
    # 机制：有效点是否全在低 FPR
    fpr_effective = sorted({g["fpr"] for g in eff})
    fpr_ineffective = sorted({g["fpr"] for g in grid if not g["effective"]})
    fpr_dominates = bool(eff) and all(
        g["fpr"] <= cfg["fpr_threshold"] for g in eff
    )

    return {
        "baseline": {
            "success": round(base_success, 4),
            "undo_rate": round(base_undo, 4),
            "mean_steps": round(base_steps, 2),
        },
        "oracle_upper_bound": {
            "success": oracle_success, "undo_rate": oracle_undo,
            "mean_steps": round(oracle_steps, 2),
            "step_save_frac": round(1.0 - oracle_steps / base_steps, 4),
        },
        "calibration": {
            "baseline_undo_in_paper_range_1_8pct": 0.01 <= base_undo <= 0.08,
            "note": "baseline 撤销率需落论文 1-8% 区间；否则装置量级失配",
        },
        "grid": grid,
        "sweet_spot_exists": bool(eff),
        "n_effective_points": len(eff),
        "fpr_at_effective_points": fpr_effective,
        "fpr_at_ineffective_points": fpr_ineffective,
        "fpr_dominates": fpr_dominates,
    }


def counterfactuals(cfg):
    """反证：三类检测器必须分别判 false/false/true。"""
    out = {}
    # 1) FPR=1,FNR=0：每步都误报 correct → τ=1，多数首步未真确 → 成功率下降、撤销未必降
    c1 = dict(cfg); c1["fpr_grid"] = [1.0]; c1["fnr_grid"] = [0.0]
    r1 = analyze(c1)
    out["C1_always_report"] = {"effective": r1["sweet_spot_exists"], "expect": False}
    # 2) FPR=0,FNR=1：从不报 → τ=T → 与 baseline 同 → 撤销率不降
    c2 = dict(cfg); c2["fpr_grid"] = [0.0]; c2["fnr_grid"] = [1.0]
    r2 = analyze(c2)
    out["C2_never_report"] = {"effective": r2["sweet_spot_exists"], "expect": False}
    # 3) FPR=0,FNR=0：完美 → τ=k* → 撤销 0、成功保持
    c3 = dict(cfg); c3["fpr_grid"] = [0.0]; c3["fnr_grid"] = [0.0]
    r3 = analyze(c3)
    out["C3_perfect"] = {"effective": r3["sweet_spot_exists"], "expect": True}
    out["all_counterfactuals_pass"] = all(
        v["effective"] == v["expect"] for v in out.values() if isinstance(v, dict)
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cfg = {
        "seed": 17, "n_trials": 20000,
        "t_min": 8, "t_max": 40,
        "q_first": 0.60,
        "p_undo": 0.012, "p_refix": 0.30,
        "fpr_grid": [0.0, 0.01, 0.05, 0.10, 0.30],
        "fnr_grid": [0.0, 0.10, 0.30, 0.60],
        "fpr_threshold": 0.01,
    }
    cf = counterfactuals(cfg)
    if a.selftest:
        print(json.dumps({"selftest": "PASS" if cf["all_counterfactuals_pass"] else "FAIL",
                          "counterfactuals": cf}, ensure_ascii=False, indent=2))
        return
    res = analyze(cfg)
    res["counterfactuals"] = cf
    res["claim"] = ("early-exit intervention effective only under low-FPR correctness detector"
                    if res["fpr_dominates"] and res["sweet_spot_exists"] else
                    "effectiveness condition not established")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
    print(json.dumps({
        "baseline": res["baseline"], "oracle": res["oracle_upper_bound"],
        "calibration": res["calibration"],
        "sweet_spot_exists": res["sweet_spot_exists"],
        "n_effective": res["n_effective_points"],
        "fpr_dominates": res["fpr_dominates"],
        "cf_pass": cf["all_counterfactuals_pass"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
