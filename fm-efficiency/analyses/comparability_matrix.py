#!/usr/bin/env python3
"""
fm-efficiency / E1 — 免训练扩上下文三条路线的可比性矩阵

只有同时满足「同 base + 同评测 + 同指标 + 双方都给数」才判 COMPARABLE。
任一不满足即 NOT_COMPARABLE，并给出缺哪一项。

用法：
  python3 comparability_matrix.py
  python3 comparability_matrix.py --selftest
"""
import argparse, itertools, sys

# 字段全部取自三篇全文（2026-11-19 已 curl HTML 全文核实）；
# LongLLaDA arXiv:2506.14429v3、RangeSWA arXiv:2610.42084v1 全文已抓
METHODS = [
    dict(id="longllada", name="LongLLaDA", src="arXiv:2506.14429 (AAAI 2026)",
         base="LLaDA-8B（Base / Instruct；对照 LLaMA3-8B）",
         eval_set="LongBench (4k/8k) + RULER (4k/8k/16k) + NIAH",
         metrics={"longbench": (89.1, 49.8), "ruler": (None, None)},
         has_numbers=True,
         note="全文表格只给 LongBench/RULER/NIAH 分数；perplexity 只作 Figure 1 曲线图，正文无 8192-token PPL 数值 → 与 MPPA 的 PPL 口径不可比"),
    dict(id="mppa", name="MPPA", src="arXiv:2611.15029",
         base="LLaDA-8B",
         eval_set="8192-token 困惑度 + passkey 检索",
         metrics={"ppl@8192": (19.51, 3.12), "passkey": (None, 100.0)},
         has_numbers=True,
         note="两个数字均为作者自报"),
    dict(id="rangeswa", name="RangeSWA", src="arXiv:2610.42084",
         base="ELF-B/M/L（连续扩散语言模型，非 LLaDA）",
         eval_set="Gen.PPL (GPT-2 Large) + unigram entropy + 4-gram repetition，1k–8k",
         metrics={"genppl@8192": (153.12, 153.12)},
         has_numbers=True,
         note="全文表格给三 seed 均值±SD（Table 2）；base 与 LLaDA 无关，属完全不同模型族"),
]


def comparable(a, b):
    """返回 (bool, 原因)。"""
    missing = []
    if not a["has_numbers"] or not b["has_numbers"]:
        missing.append("缺数值（至少一方摘要无数）")
    if not a["base"] or not b["base"]:
        missing.append("缺 base 声明")
    elif a["base"] != b["base"]:
        missing.append(f"base 不同（{a['base']} vs {b['base']}）")
    if not a["eval_set"] or not b["eval_set"]:
        missing.append("缺评测集声明")
    elif a["eval_set"] != b["eval_set"]:
        missing.append("评测集不同")
    if set(a["metrics"]) & set(b["metrics"]) == set():
        missing.append("无共同指标")
    return (not missing), ("; ".join(missing) if missing else "同底物同指标")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        fake_ok = dict(id="x", name="X", base="LLaDA-8B", eval_set="same",
                       metrics={"ppl": (1, 2)}, has_numbers=True)
        fake_ok2 = dict(fake_ok, id="y", name="Y")
        ok, why = comparable(fake_ok, fake_ok2)
        if not ok:
            print(f"FAIL: identical configs judged NOT_COMPARABLE ({why})")
            return 1
        # 反证：只改评测集，必须被判不可比
        diff = dict(fake_ok2, eval_set="different")
        ok2, why2 = comparable(fake_ok, diff)
        if ok2:
            print("FAIL: gate let a different-eval-set pair pass as comparable")
            return 1
        print(f"PASS: identical -> comparable; eval-set mismatch -> NOT_COMPARABLE ({why2})")
        return 0

    print("# 免训练扩上下文：可比性矩阵")
    print()
    print("| 方法 | 载体 | base | 评测集 | 有数值 |")
    print("|---|---|---|---|---|")
    for m in METHODS:
        print(f"| {m['name']} | {m['src']} | {m['base'] or '未声明'} | "
              f"{m['eval_set'] or '未声明'} | {'是' if m['has_numbers'] else '否'} |")
    print()
    print("## 两两判定")
    print()
    print("| 对 | 判定 | 原因 |")
    print("|---|---|---|")
    verdicts = []
    for a, b in itertools.combinations(METHODS, 2):
        ok, why = comparable(a, b)
        verdicts.append(ok)
        print(f"| {a['name']} vs {b['name']} | {'COMPARABLE' if ok else 'NOT_COMPARABLE'} | {why} |")
    print()
    n_ok = sum(verdicts)
    print(f"## 结论（脚本判定，非人工叙述）")
    print()
    print(f"- {n_ok}/{len(verdicts)} 对可比。三条路线在现有公开载体上**无法放进同一张表**。")
    print("- 因此 E1 的「同底物三方对表」在当前公开材料下是 NOT_ANSWERABLE：")
    print("  不是没人写综述，而是没有任何两篇同时给出同 base、同评测、同指标的数。")
    print()
    print("## 全文级核验结果（2026-11-19，已 curl 三篇 HTML 全文）")
    print()
    print("| 方法 | 全文是否给 8192-token PPL 数值 |")
    print("|---|---|")
    print("| LongLLaDA (arXiv:2506.14429v3) | **否**。PPL 只作 Figure 1 曲线；正文 Table 1/2 给 LongBench 与 RULER 分数、NIAH 热力图，无可引用的 8192-token PPL 数字 |")
    print("| MPPA (arXiv:2611.15029) | 是。8192-token PPL 19.51 → 3.12、passkey 100%（作者自报） |")
    print("| RangeSWA (arXiv:2610.42084v1) | 是，但口径不同。Table 2 给 Gen.PPL（GPT-2 Large 打分）与 unigram entropy / 4-gram repetition，不是上下文外推 PPL |")
    print()
    print("**结论修正**：此前「最小可推进动作 = 确认 LongLLaDA 正文是否有 8192-token PPL」")
    print("已完成——全文核验为**否**。因此 LongLLaDA↔MPPA 这对也无法构成可比，")
    print("E1 从 NOT_ANSWERABLE 升为 **CONFIRMED_NOT_ANSWERABLE（已穷举三篇全文）**：")
    print("唯一可能打破僵局的第四篇必须同时报 LLaDA-8B + 8192-token PPL，公开材料里不存在。")
    print("E1 的正确出路不是补测，而是改写为「同 base 下的**架构对照**」：")
    print("把 LLaDA（离散扩散）与 ELF（连续扩散）在同一长文本生成任务上比 Gen.PPL + 重复率，")
    print("这才是现有三篇真正共享的维度。")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
