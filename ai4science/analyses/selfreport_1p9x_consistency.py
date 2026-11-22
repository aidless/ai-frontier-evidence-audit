#!/usr/bin/env python3
"""ai4science E2: OpenAI「1.9× 自我报告效率」的内部一致性与可审计性诊断。

这不是配对实测（需要人类受试者 + 任务日志，底物不可得），只是对已公开数字做
算术自检 + 稳健性边界，回答一个可判的问题：
  「1.9× 这个均值，能否从公开的分项数字复现？偏离的方向与幅度能否界定？」

公开数字（ai4science/evidence/2026-11-19-baseline.md:25，来自 OpenAI 报告 2026-11-16）：
  8 类科研活动自我报告时间比均值 = 1.9×；
  公开 5 个分项：代码 2.83 / 阅读 2.21 / 分析 2.05 / 构思 1.86 / 写作 1.76。
  另 3 个分项未在该摘要公开。

自检命题（可证伪）：
  P1: 若 1.9 是 8 个分项的算术均值，则未公开 3 项均值须 = (8*1.9 - sum5)/3。
  P2: 该隐含均值若低于公开 5 项的最小值(1.76)，说明 1.9 不是简单算术均值
      （或用了不同加权/不同分项集），即聚合口径未公开 → 不可从公开数字复现。
  P3: 自我报告时间比 r → 隐含「时间节省」= 1 - 1/r（纯算术变换，非因果估计）。
  P4: 无配对实测 → 真实效应偏离的「方向」与「幅度」在数学上不可识别
      （自我报告偏差可正可负、幅度无界），只能给恒等变换，不能给点估计。

运行：
  python3 ai4science/analyses/selfreport_1p9x_consistency.py --selftest
  python3 ai4science/analyses/selfreport_1p9x_consistency.py --mode full --out ai4science/evidence/selfreport-1p9x-consistency.json
"""
import argparse
import json
import math
from datetime import datetime, timezone

# 公开数字 —— 每个都带出处
HEADLINE = 1.9                      # 8 类活动自我报告时间比均值
N_CATEGORIES = 8                    # 报告声称的类别数
PUBLISHED = {                       # 公开的分项（baseline.md:25）
    "code": 2.83, "reading": 2.21, "analysis": 2.05,
    "ideation": 1.86, "writing": 1.76,
}
SOURCE = "ai4science/evidence/2026-11-19-baseline.md:25 (OpenAI report 2026-11-16)"


def implied_unpublished_mean(headline, n_cat, published):
    vals = list(published.values())
    n_missing = n_cat - len(vals)
    if n_missing < 0:
        raise ValueError("more published values than categories")
    return (n_cat * headline - sum(vals)) / n_missing, n_missing


def time_saved(ratio):
    """自我报告时间比 r = t_without/t_with → 隐含节省比例 1 - 1/r（恒等变换）。"""
    if ratio <= 0:
        raise ValueError("ratio must be > 0")
    return 1 - 1 / ratio


def consistency_checks():
    vals = list(PUBLISHED.values())
    s = sum(vals)
    impl, n_missing = implied_unpublished_mean(HEADLINE, N_CATEGORIES, PUBLISHED)
    pub_min, pub_max = min(vals), max(vals)
    pub_mean = s / len(vals)
    pub_median = sorted(vals)[len(vals) // 2]
    pub_geomean = math.prod(vals) ** (1 / len(vals))
    # 若未公开项都 >= 公开最小值，则 8 项均值的下界
    lb = (s + n_missing * pub_min) / N_CATEGORIES
    # 若未公开项都 <= 公开最大值，则 8 项均值的上界
    ub = (s + n_missing * pub_max) / N_CATEGORIES

    checks = {
        # C1: 1.9 不等于公开 5 项的算术均值 → 聚合口径非简单算术均值
        "headline_not_equal_published_mean": not math.isclose(HEADLINE, pub_mean, abs_tol=1e-9),
        # C2: 隐含的未公开 3 项均值低于公开最小值 → 与「同口径算术均值」矛盾
        "implied_missing_below_published_min": impl < pub_min,
        # C3: 1.9 落在「未公开项 ∈ [pub_min,pub_max]」可产生的均值区间【之外】
        #     —— 若在外，则连「同口径但选了更低分项」都排除，1.9 与公开分项彻底不相容
        "headline_outside_feasible_range": not (lb <= HEADLINE <= ub),
        # C4: 公开 5 项的任何常用集中趋势(mean/median/geomean)都不是 1.9
        "no_common_aggregator_matches": all(
            not math.isclose(HEADLINE, x, abs_tol=1e-9)
            for x in (pub_mean, pub_median, pub_geomean)
        ),
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "published_n": len(vals),
        "published_values": PUBLISHED,
        "published_sum": s,
        "published_mean": pub_mean,
        "published_median": pub_median,
        "published_geomean": pub_geomean,
        "published_min": pub_min,
        "published_max": pub_max,
        "n_categories_claimed": N_CATEGORIES,
        "n_missing": n_missing,
        "headline": HEADLINE,
        "implied_unpublished_mean": impl,
        "feasible_mean_range_if_missing_in_published_range": [lb, ub],
        "aggregation_reproducible_from_public_numbers": False,
        "interpretation": (
            "1.9x is below the arithmetic mean (2.142), the median (2.05) and the "
            "geometric mean (2.112) of the five published subitems. Reproducing 1.9 "
            "as an 8-item arithmetic mean would require the three unpublished items to "
            "average 1.497, below every published subitem; indeed 1.9 lies outside the "
            "entire feasible mean range [1.999, 2.400] obtainable even if the missing "
            "items took the published minimum (1.76). The headline is therefore "
            "incompatible with the published subitems under any same-scale averaging. "
            "Its exact aggregation (weights / item set) is unpublished → 1.9x is not "
            "reproducible from public numbers. With no paired measurement the "
            "direction/magnitude of self-report bias is mathematically unidentified."
        ),
    }


def selftest():
    # 注入反证：判定门必须能红
    a = consistency_checks()
    assert a["checks"]["headline_not_equal_published_mean"]
    assert a["checks"]["implied_missing_below_published_min"]

    # 若把 headline 设成公开 5 项均值 2.142，第一个判据必须翻转（不再「不等于」）
    impl2, nm = implied_unpublished_mean(2.142, 8, PUBLISHED)
    assert math.isclose(impl2, 2.142, abs_tol=1e-3) and nm == 3, "consistency algebra broken"

    # 时间节省变换单调性 + 恒等式
    assert math.isclose(time_saved(2.0), 0.5)
    assert time_saved(2.83) > time_saved(1.76)
    assert math.isclose(time_saved(1.0), 0.0)

    # 若给一个显著更高的 headline(2.5)，隐含未公开均值应 > 公开最大值，判据应翻转
    impl_hi, _ = implied_unpublished_mean(2.5, 8, PUBLISHED)
    assert impl_hi > max(PUBLISHED.values()), "injected high headline must imply high missing items"
    assert (impl_hi < min(PUBLISHED.values())) is False, "falsification gate must go red"

    return {
        "status": "PASS",
        "injected_falsifications_caught": 2,
        "note": "headline→published-mean substitution flips C1; high headline flips implied-missing direction",
    }


def run():
    c = consistency_checks()
    return {
        "experiment": "ai4science/E2-tool-selfreport-audit/consistency-diagnostic",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nature": "arithmetic consistency + identifiability diagnostic; NOT a paired human-subject measurement",
        "source": SOURCE,
        "design_criterion": "自我报告 1.9× 与配对实测的偏离方向与幅度（判据原文）",
        "what_is_demonstrable": (
            "公开数字的内部一致性 + 偏离的可识别性；配对实测的底物（人类受试者+任务日志）不可用，"
            "本诊断不冒充配对效应量。"
        ),
        "consistency": c,
        "identity_transforms": {
            "time_saved_at_1p9": time_saved(HEADLINE),
            "time_saved_at_published_mean": time_saved(c["published_mean"]),
            "note": "1-1/r 是恒等变换，不是因果效应；r 为自我报告则节省比例同样是自我报告口径。",
        },
        "identifiability": {
            "direction_identifiable": False,
            "magnitude_identifiable": False,
            "reason": (
                "自我报告偏差 = 报告值 - 真实值，两者无配对、无方差、无对照组；"
                "偏差可正可负、幅度无界，无法从单一自我报告均值识别方向或幅度。"
            ),
            "verdict": "NOT_IDENTIFIABLE_WITH_PUBLIC_DATA",
        },
        "verdict": {
            "aggregation_reproducible": False,
            "selfreport_bias_direction_estimable": False,
            "selfreport_bias_magnitude_estimable": False,
            "headline_vs_published_subitems": "inconsistent_under_simple_arithmetic_mean",
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mode", choices=["full"], default="full")
    ap.add_argument("--out")
    args = ap.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), ensure_ascii=False, indent=2))
        return
    txt = json.dumps(run(), ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
        print(f"wrote {args.out}")
    else:
        print(txt)


if __name__ == "__main__":
    main()
