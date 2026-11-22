#!/usr/bin/env python3
"""E2-workflow-author-effect: 可判定性（检测性）审计，非 WF Arena 数值复现。

背景（已落盘证据）：
  agentic-systems/experiments/E2-workflow-author-effect/availability.md
  逐字锁定两条 WF Arena 自述限制：
    (1) "Each configuration is evaluated once per task, so differences between
         closely ranked configurations are reported without variance estimates."
    (2) "Content and 3D deliverables are graded against task rubrics by an LLM
         judge, and agreement with human graders is not measured in this work."
  论文有 145 个任务、9 个模型（availability.md:30）。

因此能判的命题不是「作者差异有多大」（底物无方差，判读不了），而是
  「在单次评测协议下，多大的真实作者效应才判得开」（a-priori 检测性 / MDE）。

设计：
  分析单元 = 任务（每任务一对分数：作者 A 工作流 vs 作者 B 工作流），
  配对差值 d_i = score_A(i) - score_B(i)。主效应检验 = 配对 t 检验（H0: E[d]=0）。
  难度交互 = 把任务分 easy/hard 两组，比较两组的 d，独立两样本 t 检验。
  δ = 真实作者效应（分数点），σ = 单次评测 judge 抖动（分数点），dz = δ/σ。

SESOI 不可用（底物无方差估计 → 论文给不出最小重要效应），
按 statistical-power skill 的规矩：不发明效应量，报告 MDE + 灵敏度曲线，
而不是挑一个单点、更不是 post-hoc observed power。

运行：
  python3 agentic-systems/analyses/workflow_author_detectability.py --selftest
  python3 agentic-systems/analyses/workflow_author_detectability.py --mode full \
      --out agentic-systems/evidence/workflow-author-detectability.json
"""
import argparse
import json
import math
import sys
from datetime import datetime, timezone

import numpy as np
from scipy import stats


# ---------- 解析功效（用 nct 直接算，避开 statsmodels 在大效应处返回 nan） ----------

def _two_sided_power(df, ncp, alpha):
    """两侧 t 检验功效；用 sf+cdf 并对 scipy 在大 ncp 下 cdf(-tcrit) 返回 nan 的边界兜底。
    ncp 很大时下尾 cdf(-tcrit) 可忽略（<1e-8），置 0 是数学等价而非凑数。"""
    tcrit = stats.t.ppf(1 - alpha / 2, df)
    upper = float(stats.nct.sf(tcrit, df, ncp))
    lower = float(stats.nct.cdf(-tcrit, df, ncp))
    if math.isnan(lower):
        lower = 0.0
    if math.isnan(upper):
        upper = 0.0
    return min(1.0, max(0.0, upper + lower))


def paired_power(dz, n, alpha=0.05):
    """配对 t 检验功效；dz = δ/σ（Cohen's dz），n = 配对数（任务数）。"""
    if n < 2:
        raise ValueError("n must be >= 2")
    return _two_sided_power(n - 1, dz * math.sqrt(n), alpha)


def indep_power(d, n1, n2, alpha=0.05):
    """独立两样本 t 检验功效（等方差 pooled），用于 easy/hard 难度交互。"""
    if n1 < 2 or n2 < 2:
        raise ValueError("n1 and n2 must be >= 2")
    df = n1 + n2 - 2
    return _two_sided_power(df, d * math.sqrt(n1 * n2 / (n1 + n2)), alpha)


def _bisect_mde(power_fn, alpha, target, hi=8.0):
    lo = 1e-9
    for _ in range(200):
        mid = (lo + hi) / 2
        if power_fn(mid, alpha) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def paired_mde(n, alpha=0.05, target=0.80):
    return _bisect_mde(lambda d, a: paired_power(d, n, a), alpha, target)


def indep_mde(n1, n2, alpha=0.05, target=0.80):
    return _bisect_mde(lambda d, a: indep_power(d, n1, n2, a), alpha, target)


# ---------- Monte Carlo 校验（Type I error 必须先验真，skill 硬要求） ----------

def wilson_interval(k, n, z=1.96):
    if n == 0:
        return [float("nan"), float("nan")]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def mc_type_i_error(n, n_sims, alpha, seed):
    """H0 (dz=0) 下配对 t 检验的拒真率，应 ≈ alpha。"""
    rng = np.random.default_rng(seed)
    df = n - 1
    tcrit = stats.t.ppf(1 - alpha / 2, df)
    k = 0
    for _ in range(n_sims):
        d = rng.standard_normal(n)
        sd = d.std(ddof=1)
        if sd == 0.0:
            continue
        t = d.mean() / (sd / math.sqrt(n))
        if abs(t) > tcrit:
            k += 1
    return {
        "n": n,
        "n_sims": n_sims,
        "alpha": alpha,
        "rejections": k,
        "rate": k / n_sims,
        "rate_wilson95": wilson_interval(k, n_sims),
        "seed": seed,
    }


def mc_power(dz, n, n_sims, alpha, seed):
    rng = np.random.default_rng(seed)
    df = n - 1
    tcrit = stats.t.ppf(1 - alpha / 2, df)
    k = 0
    for _ in range(n_sims):
        d = rng.normal(dz, 1.0, n)
        sd = d.std(ddof=1)
        if sd == 0.0:
            continue
        t = d.mean() / (sd / math.sqrt(n))
        if abs(t) > tcrit:
            k += 1
    return {
        "dz": dz, "n": n, "n_sims": n_sims, "rejections": k,
        "rate": k / n_sims, "rate_wilson95": wilson_interval(k, n_sims),
        "analytic": paired_power(dz, n, alpha), "seed": seed,
    }


# ---------- 判决（每条都可被注入反证判红） ----------

def verdict_table(mde_main, mde_by_n, mde_interaction, repeats, type_i_rate):
    checks = {
        # 空性反证 1：null 拒真率必须落在 alpha 附近（0.03–0.07）
        "type_i_valid": 0.03 <= type_i_rate <= 0.07,
        # 空性反证 2：任务越多 MDE 越小（严格单调递减）
        "mde_decreases_with_n": all(
            mde_by_n[i]["mde_dz"] > mde_by_n[i + 1]["mde_dz"]
            for i in range(len(mde_by_n) - 1)
        ),
        # 空性反证 3：同总任务数下，难度交互比主效应难判（MDE 更大）
        "interaction_harder_than_main": mde_interaction > mde_main,
        # 空性反证 4：重复评测降低 MDE（R 越大越小）
        "repeats_reduce_mde": all(
            repeats[i]["mde_dz_in_single_eval_sigma"] > repeats[i + 1]["mde_dz_in_single_eval_sigma"]
            for i in range(len(repeats) - 1)
        ),
    }
    passed = all(checks.values())
    return {
        "checks": checks,
        "all_checks_pass": passed,
        "claim": (
            "Under WF Arena's single-evaluation protocol the author-effect claim is "
            "decidable only above the MDE; the difficulty-interaction claim needs a "
            "larger effect at the same N. No variance estimates in substrate => "
            "absolute score-point SESOI unavailable; MDE is reported in dz units."
        ),
        "substrate_supports_point_effect_reading": False,
    }


def run(alpha=0.05, target=0.80, n_sims=5000, seed=20261121):
    # WF Arena 论文实际任务数（availability.md:30），主效应用全量；设计稿说选 2-3 域，故也给子集
    ns = [48, 72, 100, 145]
    mde_by_n = [{"n": n, "mde_dz": paired_mde(n, alpha, target)} for n in ns]
    mde_main = paired_mde(145, alpha, target)

    # 难度交互：145 任务近半分（72/73），独立两样本
    n_easy, n_hard = 72, 73
    mde_interaction = indep_mde(n_easy, n_hard, alpha, target)

    # 重复评测 R 次取平均：单次 σ 不变时有效 dz 放大 sqrt(R)，MDE(以单次 σ 计) 降为 1/sqrt(R)
    repeats = [
        {"R": R, "mde_dz_in_single_eval_sigma": mde_main / math.sqrt(R)}
        for R in [1, 4, 16, 64]
    ]

    # 灵敏度曲线：固定 N=145，报若干 dz 的功效 + 达到目标功效所需 n（skill 要求报范围而非单点）
    def solve_n(dz):
        if dz == 0:
            return None
        lo = 2
        while paired_power(dz, lo, alpha) < target:
            lo *= 2
            if lo > 100_000_000:
                return None
        left, right = max(2, lo // 2), lo
        while left < right:
            mid = (left + right) // 2
            if paired_power(dz, mid, alpha) >= target:
                right = mid
            else:
                left = mid + 1
        return left

    sensitivity = [
        {"dz": dz, "power_at_145": paired_power(dz, 145, alpha),
         "n_required": solve_n(dz)}
        for dz in [0.0, 0.1, 0.2, 0.234, 0.3, 0.5]
    ]

    tc = mc_type_i_error(145, n_sims, alpha, seed)
    mp = mc_power(mde_main, 145, n_sims, alpha, seed + 1)

    verdict = verdict_table(mde_main, mde_by_n, mde_interaction, repeats, tc["rate"])

    return {
        "experiment": "E2-workflow-author-effect/detectability-audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nature": "a-priori detectability / MDE audit; NOT a WF Arena numerical replication",
        "substrate": {
            "availability_md": "agentic-systems/experiments/E2-workflow-author-effect/availability.md",
            "verbatim_limits": [
                "Each configuration is evaluated once per task, so differences between closely ranked configurations are reported without variance estimates.",
                "Content and 3D deliverables are graded against task rubrics by an LLM judge, and agreement with human graders is not measured in this work.",
            ],
            "n_tasks_in_paper": 145,
            "n_models_in_paper": 9,
            "single_eval_per_task": True,
            "variance_estimates_published": False,
            "human_judge_agreement_measured": False,
        },
        "design": {
            "unit_of_analysis": "task (paired per task)",
            "main_test": "paired t-test on d_i = score_A - score_B; H0 E[d]=0",
            "interaction_test": "two-sample t on d between easy/hard task halves",
            "alpha": alpha, "target_power": target,
            "sesoi_status": "NOT_AVAILABLE_FROM_SUBSTRATE",
            "sesoi_reason": "paper publishes no variance estimate and no human-agreement measurement; no defensible score-point SESOI can be set without inventing one",
            "approach": "report MDE + sensitivity curve (no single invented effect; no post-hoc observed power)",
        },
        "main_effect_mde_dz_at_145_tasks": mde_main,
        "mde_by_task_count": mde_by_n,
        "difficulty_interaction": {
            "n_easy": n_easy, "n_hard": n_hard, "mde_dz": mde_interaction,
            "ratio_to_main": mde_interaction / mde_main,
        },
        "repeated_evaluation_scaling": repeats,
        "sensitivity_at_145_tasks": sensitivity,
        "montecarlo": {"type_i_error": tc, "power_at_mde": mp},
        "verdict": verdict,
    }


def selftest():
    # 用注入值验判决门能红（不靠真实结果自己给自己盖章）
    base_n = [{"n": 100, "mde_dz": 0.30}, {"n": 145, "mde_dz": 0.234}]
    rp = [{"R": 1, "mde_dz_in_single_eval_sigma": 0.234},
          {"R": 4, "mde_dz_in_single_eval_sigma": 0.117}]
    good = verdict_table(0.234, base_n, 0.468, rp, 0.05)
    assert good["all_checks_pass"] is True, "baseline verdict should pass"

    bad1 = verdict_table(0.234, base_n, 0.468, rp, 0.50)
    assert bad1["checks"]["type_i_valid"] is False, "injected Type I 0.50 must be caught"

    bad2 = verdict_table(0.234, [{"n": 100, "mde_dz": 0.20}, {"n": 145, "mde_dz": 0.30}],
                         0.468, rp, 0.05)
    assert bad2["checks"]["mde_decreases_with_n"] is False, "injected non-monotone MDE must be caught"

    bad3 = verdict_table(0.234, base_n, 0.10, rp, 0.05)
    assert bad3["checks"]["interaction_harder_than_main"] is False, "injected easy interaction must be caught"

    bad4 = verdict_table(0.234, base_n, 0.468,
                         [{"R": 1, "mde_dz_in_single_eval_sigma": 0.10},
                          {"R": 4, "mde_dz_in_single_eval_sigma": 0.20}], 0.05)
    assert bad4["checks"]["repeats_reduce_mde"] is False, "injected reverse repeat scaling must be caught"

    # 解析公式自洽：power 随 dz 单调、随 n 单调；MDE 回代 power ≈ target
    assert paired_power(0.3, 145) > paired_power(0.2, 145) > paired_power(0.1, 145)
    assert paired_power(0.234, 145) > paired_power(0.234, 72)
    m = paired_mde(145)
    assert abs(paired_power(m, 145) - 0.80) < 1e-3, "MDE round-trip must hit 0.80 power"
    mi = indep_mde(72, 73)
    assert abs(indep_power(mi, 72, 73) - 0.80) < 1e-3
    return {"status": "PASS", "injected_falsifications_caught": 4,
            "mde_roundtrip": {"paired_145": m, "indep_72_73": mi}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mode", choices=["full"], default="full")
    ap.add_argument("--out", default=None)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    ap.add_argument("--n-sims", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20261121)
    args = ap.parse_args()

    if args.selftest:
        print(json.dumps(selftest(), ensure_ascii=False, indent=2))
        return

    result = run(args.alpha, args.power, args.n_sims, args.seed)
    txt = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
        print(f"wrote {args.out}")
    else:
        print(txt)


if __name__ == "__main__":
    main()
