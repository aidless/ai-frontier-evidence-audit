#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embodied E2: ACE-CaP-0 (arXiv:2611.16872) Table 1 分层复算诊断
================================================================
设计卡 (E2-offline-code-closed-loop) 判据逐字：
    「92.1% 是否为少数场景的高均值，长尾是否稳定」

本脚本是对论文【已报告聚合数字】的分层复算（零底物、无真机、无 GR00T2 权重），
不是独立真机复现。ACE-CaP-0 在 8 个真实世界操作任务上各评测 30 trials（共 240），
Table 1 给出逐任务 成功数/30、mean time、output token。本脚本据此复算：

  C1 聚合一致性   Σ成功/Σ总数 == 221/240 == 0.9208，与论文 92.1% 一致（复算自洽）
  C2 balanced   所有场景 trial 数相同(30) => 加权均值 == 未加权均值，
                排除「少数场景因样本量大而拉动整体」的结构基础
  C3 留一稳健    去掉任一场景后整体成功率的极差 <= 3pp => 无单一场景拉动
  C4 长尾稳定    最低场景(83.3%) 的 Wilson 95%CI 是否覆盖整体 92.1%
                (覆盖 => 长尾不显著偏离，但 n=30 功效有限)

另报场景间异质性检验：Pearson chi-square (df=7) 对「8 场景同成功率」原假设的 p 值。

诚实边界（写进报告与 JSON）：
  · 只用了论文报告的聚合分层数字（每场景成功数/30），没有逐 trial 序列
    => 可复算场景间方差，无法复算场景内 trial 级方差 / 失败聚集 / 学习效应
  · 每场景仅 n=30，Wilson CI 宽约 ±14pp，长尾「稳定」是「样本量下不显著」而非「证明稳定」
  · 是论文报告数字的算术一致性复算，不是独立真机复现

selftest 注入反证（必须全部判红/判对，否则装置是装饰）：
  B1 聚合不符 (220/240)            => C1 = false
  B2 不平衡设计 (某场景 n!=30)      => C2 = false
  B3 单一场景拉动 (Charger 30/30 拉高, 余下大幅下降) => C3 = false
  B4 长尾显著偏离 (最低场景远低于整体) => C4 = false
  B5 Wilson 已知值对表            => 数值吻合

usage:
  python3 acecap0_stratified_recompute.py --selftest
  python3 acecap0_stratified_recompute.py --run --out ../evidence/acecap0-stratified-recompute.json
"""
import argparse
import json
import math
import sys

# ---- Table 1 逐任务 (成功数 k, trials n, mean time min, output token M) ----
# 来源: arXiv:2611.16872v1 Table 1 (curl 2026-11-21, .tmp/fulltext/2611.16872.txt)
TABLE1 = [
    ("Charger Insertion",   30, 30, 1.65, 1.09),
    ("Bread Packing",       25, 30, 1.93, 2.14),
    ("Bottle Uncapping",    27, 30, 2.23, 1.17),
    ("Cup Nesting",         28, 30, 1.58, 0.95),
    ("Flower Insertion",    27, 30, 1.37, 0.92),
    ("Chicken Plating",     29, 30, 1.12, 0.75),
    ("Parcel Reorientation", 28, 30, 0.97, 1.07),
    ("Shoe Packing",        27, 30, 2.27, 1.87),
]
PAPER_OVERALL_K = 221
PAPER_OVERALL_N = 240
PAPER_OVERALL_RATE = 0.921
Z = 1.96


def wilson(k, n, z=Z):
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def chi2_heterogeneity(table):
    """Pearson chi-square test that all scenarios share one success prob.

    Returns (chi2, df, pvalue). Under H0 (homogeneous p), each scenario's
    successes ~ Binomial(n_i, p_pool). With equal n_i this reduces to the
    standard k-sample proportion test.
    """
    total_k = sum(k for _, k, _, _, _ in table)
    total_n = sum(n for _, _, n, _, _ in table)
    p_pool = total_k / total_n
    chi2 = 0.0
    df = 0
    for name, k, n, _, _ in table:
        exp = n * p_pool
        var = n * p_pool * (1.0 - p_pool)
        if var <= 0:
            continue
        chi2 += (k - exp) ** 2 / var
        df += 1
    df -= 1  # one constraint: p_pool estimated
    pvalue = _chi2_sf(chi2, df)
    return chi2, df, pvalue


def _chi2_sf(x, df):
    """Survival function of chi-square via regularized upper incomplete gamma."""
    if x <= 0:
        return 1.0
    if df <= 0:
        return float("nan")
    a = df / 2.0
    z = x / 2.0
    return _gammaincc(a, z)


def _gammaincc(a, x):
    """Upper regularized incomplete gamma Q(a,x) via continued fraction / series."""
    if x < 0 or a <= 0:
        return float("nan")
    if x == 0:
        return 1.0
    # use series for small x, continued fraction for large x
    if x < a + 1.0:
        # lower series then 1 - P
        term = 1.0 / a
        total = term
        ap = a
        for _ in range(1000):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        p_lower = total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return 1.0 - p_lower
    else:
        # Lentz continued fraction for Q
        tiny = 1e-300
        b = x + 1.0 - a
        c = 1.0 / tiny
        d = 1.0 / b
        h = d
        for i in range(1, 1000):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < tiny:
                d = tiny
            c = b + an / c
            if abs(c) < tiny:
                c = tiny
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-15:
                break
        q = h * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return q


def analyze(table, leave_one_out_thresh=0.03):
    """Run the four pre-registered checks on a table of (name,k,n,...)."""
    total_k = sum(k for _, k, _, _, _ in table)
    total_n = sum(n for _, _, n, _, _ in table)
    overall = total_k / total_n

    # C1 aggregate consistency
    c1 = (total_k == PAPER_OVERALL_K and total_n == PAPER_OVERALL_N
          and abs(overall - PAPER_OVERALL_RATE) < 0.005)

    # C2 balanced design (all n equal)
    ns = [n for _, _, n, _, _ in table]
    c2 = len(set(ns)) == 1

    # C3 leave-one-out robustness
    loo_rates = {}
    for name, k, n, _, _ in table:
        rk = total_k - k
        rn = total_n - n
        loo_rates[name] = rk / rn if rn > 0 else float("nan")
    loo_vals = list(loo_rates.values())
    loo_range = max(loo_vals) - min(loo_vals)
    c3 = loo_range <= leave_one_out_thresh

    # C4 long-tail stability: lowest scenario Wilson CI covers overall
    lowest = min(table, key=lambda r: r[1] / r[2])
    lo_k, lo_n = lowest[1], lowest[2]
    lo_rate = lo_k / lo_n
    lo_ci = wilson(lo_k, lo_n)
    c4 = (lo_ci[0] <= overall <= lo_ci[1])

    # chi-square heterogeneity
    chi2, df, pval = chi2_heterogeneity(table)

    # scenario-level dispersion
    rates = [k / n for _, k, n, _, _ in table]
    mean_rate = sum(rates) / len(rates)
    if len(rates) > 1:
        var = sum((r - mean_rate) ** 2 for r in rates) / (len(rates) - 1)
        sd = math.sqrt(var)
    else:
        var = sd = 0.0

    # expected binomial sampling sd at n=30, p~overall (noise floor)
    noise_var = overall * (1 - overall) / (30.0)
    noise_sd = math.sqrt(noise_var)

    return {
        "total_k": total_k, "total_n": total_n, "overall_rate": overall,
        "balanced": c2, "n_values": ns,
        "unweighted_mean_rate": mean_rate,
        "scenario_sd": sd, "scenario_range_pp": (max(rates) - min(rates)) * 100.0,
        "binomial_noise_sd_at_n30": noise_sd,
        "observed_var": var, "noise_var": noise_var,
        "var_ratio": (var / noise_var) if noise_var > 0 else float("inf"),
        "leave_one_out": loo_rates, "leave_one_out_range_pp": loo_range * 100.0,
        "lowest": {"name": lowest[0], "k": lo_k, "n": lo_n, "rate": lo_rate, "wilson_ci": lo_ci},
        "highest": {"name": max(table, key=lambda r: r[1] / r[2])[0]},
        "chi2": chi2, "chi2_df": df, "chi2_pvalue": pval,
        "C1": c1, "C2": c2, "C3": c3, "C4": c4,
    }


def selftest():
    """Inject falsifications; every checker must flip exactly as expected."""
    failures = []

    # B5 Wilson known-value cross-check (z=1.96)
    lo, hi = wilson(25, 30)
    # canonical Wilson for 25/30 ~ (0.664, 0.933)
    if not (abs(lo - 0.664) < 0.01 and abs(hi - 0.933) < 0.02):
        failures.append(f"B5 wilson(25,30)=({lo:.4f},{hi:.4f}) out of expected range")

    # B1 aggregate mismatch: flip one success 30->29
    bad1 = [(n, k if n != "Charger Insertion" else k - 1, nt, t, o) for n, k, nt, t, o in TABLE1]
    r1 = analyze(bad1)
    if r1["C1"] is not False:
        failures.append("B1 aggregate mismatch NOT caught (C1 should be False)")

    # B2 unbalanced design: change one n
    bad2 = [(n, k, nt if n != "Cup Nesting" else 28, t, o) for n, k, nt, t, o in TABLE1]
    r2 = analyze(bad2)
    if r2["C2"] is not False:
        failures.append("B2 unbalanced design NOT caught (C2 should be False)")

    # B3 single-scenario pull: Charger stays 30/30, degrade the rest heavily
    bad3 = []
    for n, k, nt, t, o in TABLE1:
        if n == "Charger Insertion":
            bad3.append((n, 30, nt, t, o))
        else:
            bad3.append((n, max(0, k - 8), nt, t, o))
    r3 = analyze(bad3)
    if r3["C3"] is not False:
        failures.append(f"B3 single-scenario pull NOT caught (C3 should be False, LOO range={r3['leave_one_out_range_pp']:.2f}pp)")

    # B4 long-tail significant: make lowest scenario much worse
    bad4 = []
    for n, k, nt, t, o in TABLE1:
        if n == "Bread Packing":
            bad4.append((n, 15, nt, t, o))  # 50%, far below overall
        else:
            bad4.append((n, k, nt, t, o))
    r4 = analyze(bad4)
    if r4["C4"] is not False:
        failures.append(f"B4 long-tail divergence NOT caught (C4 should be False, lowest CI={r4['lowest']['wilson_ci']})")

    # positive anchor: real table must pass all four
    r0 = analyze(TABLE1)
    if not (r0["C1"] and r0["C2"] and r0["C3"] and r0["C4"]):
        failures.append(f"real TABLE1 should pass C1-C4, got {r0['C1']},{r0['C2']},{r0['C3']},{r0['C4']}")

    # chi2 sanity: real table p should be non-trivial (not extreme)
    if not (0.0 <= r0["chi2_pvalue"] <= 1.0):
        failures.append(f"chi2 pvalue out of range: {r0['chi2_pvalue']}")

    if failures:
        print("SELFTEST FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("SELFTEST PASS")
    print(f"  B1 aggregate mismatch caught (C1 False)")
    print(f"  B2 unbalanced design caught (C2 False)")
    print(f"  B3 single-scenario pull caught (C3 False, LOO range={r3['leave_one_out_range_pp']:.2f}pp)")
    print(f"  B4 long-tail divergence caught (C4 False)")
    print(f"  B5 wilson(25,30)=({lo:.4f},{hi:.4f}) matches canonical")
    print(f"  real TABLE1 passes C1-C4: {r0['C1']},{r0['C2']},{r0['C3']},{r0['C4']}")
    print(f"  chi2={r0['chi2']:.3f} df={r0['chi2_df']} p={r0['chi2_pvalue']:.3f}")
    return 0


def run(out=None):
    r = analyze(TABLE1)
    result = {
        "source": "arXiv:2611.16872v1 Table 1 (ACE-CaP-0, frozen-code robot manipulation, coding agent=Claude Opus 5.5)",
        "recomputed": "2026-11-21 (billion-context session, zero-substrate stratified recompute; NOT a physical reproduction)",
        "table1": [{"name": n, "k": k, "n": nt, "rate": k / nt, "mean_time_min": t, "output_token_M": o}
                   for n, k, nt, t, o in TABLE1],
        "criteria": {
            "C1_aggregate_consistency": r["C1"],
            "C2_balanced_design": r["C2"],
            "C3_leave_one_out_robust": r["C3"],
            "C4_long_tail_stable": r["C4"],
        },
        "metrics": {
            "total_k": r["total_k"], "total_n": r["total_n"],
            "overall_rate": r["overall_rate"],
            "unweighted_mean_scenario_rate": r["unweighted_mean_rate"],
            "scenario_sd": r["scenario_sd"],
            "scenario_range_pp": r["scenario_range_pp"],
            "binomial_noise_sd_at_n30": r["binomial_noise_sd_at_n30"],
            "observed_scenario_var": r["observed_var"],
            "noise_var": r["noise_var"],
            "var_ratio_observed_over_noise": r["var_ratio"],
            "leave_one_out": r["leave_one_out"],
            "leave_one_out_range_pp": r["leave_one_out_range_pp"],
            "lowest": r["lowest"], "highest_name": r["highest"]["name"],
            "chi2": r["chi2"], "chi2_df": r["chi2_df"], "chi2_pvalue": r["chi2_pvalue"],
        },
        "honest_boundaries": [
            "Uses only aggregate per-scenario success counts from Table 1 (k/30 each); no per-trial sequences. Scenario-level variance is recomputable; within-scenario trial-level variance / failure clustering / learning effects are NOT.",
            "Each scenario has only n=30 trials; Wilson CI ~ +/-14pp. 'Long tail stable' means 'not significantly divergent at this sample size', not 'proven stable'.",
            "This is an arithmetic consistency recompute of the paper's own reported numbers, NOT an independent physical reproduction.",
            "The design card's blocking note ('GR00T2 weights unreleased') refers to a DIFFERENT, more ambitious closed-loop experiment; this recompute answers the card's actual criterion (is 92.1% pulled by a few scenarios, is the long tail stable) using only ACE-CaP-0 Table 1.",
        ],
        "verdict": _verdict(r),
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {out}")
    print(json.dumps(result["metrics"], indent=2, ensure_ascii=False))
    print("criteria:", result["criteria"])
    print("verdict:", result["verdict"])
    return result


def _verdict(r):
    parts = []
    if r["C1"] and r["C2"]:
        parts.append("92.1% is NOT pulled by a few high-volume scenarios: design is balanced (30 trials each) so weighted == unweighted mean")
    if r["C3"]:
        parts.append(f"leave-one-out range only {r['leave_one_out_range_pp']:.2f}pp (<=3pp): no single scenario drives the aggregate")
    if r["C4"]:
        lo = r["lowest"]
        parts.append(f"lowest scenario {lo['name']} {lo['rate']*100:.1f}% Wilson CI [{lo['wilson_ci'][0]*100:.1f}%, {lo['wilson_ci'][1]*100:.1f}%] covers overall 92.1%: long tail not significantly divergent")
    if r["chi2_pvalue"] is not None:
        if r["chi2_pvalue"] > 0.05:
            parts.append(f"chi-square heterogeneity p={r['chi2_pvalue']:.3f} (>0.05): scenario variation consistent with binomial sampling noise alone; observed var/noise var = {r['var_ratio']:.2f}")
        else:
            parts.append(f"chi-square heterogeneity p={r['chi2_pvalue']:.3f} (<=0.05): significant between-scenario heterogeneity detected")
    core = "STRATIFIED_RECOMPUTE_PASS" if (r["C1"] and r["C2"] and r["C3"] and r["C4"]) else "STRATIFIED_RECOMPUTE_FINDING"
    return core + "; " + "; ".join(parts) + ". (n=30/scenario => low power; arithmetic recompute not physical reproduction.)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.run:
        run(args.out)
        sys.exit(0)
    ap.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()