#!/usr/bin/env python3
"""
trustworthy-ai / E1 — 掩盖点估计：从 arXiv:2611.14975 全文实测构成收缩区间

上一版（masking_identity.py）因缺 f/p 只给区间 2.14–32.14pp。
全文 §3.1 + Table 1/2 给出实测设计常量，可算点估计。

实测常量（逐字取自 https://arxiv.org/html/2611.14975v1）：
  §3.1: "crossed 2 sexes, 3 age bands (0–40, 40–60, and 60+), 7 findings,
         and 2 labels ... 84 cells, sampling 72 images per cell ... 6,048 items
         ... 432 positives and 432 negatives per finding."
  Table 1: HuatuoGPT-7B acc=0.534, Qwen2.5-VL-7B acc=0.518,
           MedGemma-4B acc=0.698, Lingshu-7B acc=0.620
  Table 2: pneumothorax recall: HuatuoGPT=0.000, Qwen=0.000,
           MedGemma=0.377, Lingshu=0.671

恒等式（沿用 masking_identity.py）：ΔAcc = f · p · r
  f = 气胸子群占全部问题比例 = 864/6048 = 1/7
  p = 子群阳性率 = 432/864 = 1/2
  r = 被抹掉的召回率（对照模型的气胸检出 − 失败模型的 0）
  ⇒ f·p = 432/6048，与"只按阳性 item 算 f=432/6048,p=1"等价。

用法：
  python3 masking_point_estimate.py
  python3 masking_point_estimate.py --selftest
"""
import argparse, sys

N_ITEMS = 6048
N_FINDINGS = 7
POS_PER_FINDING = 432          # = N_ITEMS / (7 findings × 2 labels)
NEG_PER_FINDING = 432
SUBGROUP = POS_PER_FINDING + NEG_PER_FINDING   # 气胸相关问题 = 864
F = SUBGROUP / N_ITEMS                          # 1/7
P = POS_PER_FINDING / SUBGROUP                  # 1/2

# Table 2 逐字气胸召回
RECALL = {"HuatuoGPT-7B": 0.000, "Qwen2.5-VL-7B": 0.000,
          "MedGemma-4B": 0.377, "Lingshu-7B": 0.671}
# Table 1 逐字聚合准确率
ACC = {"HuatuoGPT-7B": 0.534, "Qwen2.5-VL-7B": 0.518,
       "MedGemma-4B": 0.698, "Lingshu-7B": 0.620}


def masked_delta(r_norm, r_fail=0.0):
    """把失败模型气胸召回从 r_fail 提到对照 r_norm，聚合 accuracy 的增量。"""
    return F * P * (r_norm - r_fail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        # 反证 1：设计常数必须自洽（7 findings × 864 = 6048，且正负各半）
        assert N_FINDINGS * SUBGROUP == N_ITEMS, "subgroup accounting broken"
        assert POS_PER_FINDING == NEG_PER_FINDING, "set not balanced"
        # 反证 2：f·p 两条等价路径必须给出同一个数
        assert abs(F * P - POS_PER_FINDING / N_ITEMS) < 1e-12
        # 反证 3：r_norm=r_fail ⇒ delta=0（门不虚报）
        assert abs(masked_delta(0.0, 0.0)) < 1e-12
        # 反证 4：换成不完整的子群分母会给出不同的数（证明 f 的选取是可判别的）
        wrong = (POS_PER_FINDING / 6048) * 0.5 * 0.671
        assert abs(wrong - masked_delta(0.671)) > 1e-6, "f definition not discriminative"
        print("PASS: balanced design self-consistent; f·p dual-path equal; "
              "zero-r gives zero delta; wrong-f discriminated")
        return 0

    print("# 掩盖点估计 — arXiv:2611.14975 (prevalence-matched 完全平衡设计)")
    print()
    print(f"实测常量：N={N_ITEMS}，{N_FINDINGS} findings × (432 阳 + 432 阴) = 6048")
    print(f"  f = 864/6048 = {F:.6f}（气胸子群占比）")
    print(f"  p = 432/864 = {P:.6f}（子群阳性率）")
    print(f"  f·p = {F*P:.6f} = 432/6048")
    print()
    print("## 气胸完全失败对聚合 accuracy 的代价")
    print()
    print("失败模型 HuatuoGPT / Qwen 气胸召回 = 0.000（Table 2）；")
    print("把召回从 0 提到对照水平的聚合 accuracy 增量 ΔAcc = f·p·r：")
    print()
    print("| 对照（气胸召回 r） | ΔAcc | 失败模型聚合 acc → 修复后 |")
    print("|---|---|---|")
    for name in ["MedGemma-4B", "Lingshu-7B"]:
        r = RECALL[name]
        d = masked_delta(r)
        print(f"| {name} (r={r:.3f}) | {d*100:.2f} pp | "
              f"0.534 → {0.534+d:.3f} (对 HuatuoGPT) |")
    print()
    print("## 结论（数值直接读出，不外推）")
    print()
    d_lo = masked_delta(0.377) * 100
    d_hi = masked_delta(0.671) * 100
    print(f"- 气胸**单一 finding 的彻底失败**，在 7-finding 聚合 accuracy 上只值 "
          f"**{d_lo:.2f}–{d_hi:.2f} pp**。")
    print(f"- 这解释了 HuatuoGPT 聚合 acc 0.534 / Qwen 0.518 为何仍'接近但不难看'："
          f"灾难被 {N_FINDINGS} 个 finding 平均稀释约 7 倍。")
    print("- **诚实边界**：气胸不是 HuatuoGPT 的唯一失败——Table 2 中它在 effusion")
    print("  (0.007)、mass (0.007)、nodule (0.002) 也近乎为零。修复气胸一项后 acc 只到")
    print(f"  {0.534+masked_delta(0.671):.3f}，仍远低于 MedGemma 0.698。所以聚合掩盖机制")
    print("  被证明存在且可量化，但 HuatuoGPT 的整体落后是系统性的，不是单点造成。")
    print()
    print("## 与上一版区间对照")
    print()
    print("上一版（f/p 未知）：ΔAcc ∈ [2.14, 32.14] pp（9 组假设）")
    print(f"本版（f/p 实测）：单一 finding 完全失败 = {d_lo:.2f}–{d_hi:.2f} pp（点估计）")
    print("差异来源：上一版把 f 的上界设到 0.357（2160 条假设），实测 f=0.1429；")
    print("且上一版 r 假设为'全部召回被抹掉(1.0)'，实测对照 r 仅 0.377–0.671。")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
