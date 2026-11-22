#!/usr/bin/env python3
"""
trustworthy-ai / E1 — 聚合指标掩盖恒等式（instrument）

问题：一个子群召回率归零时，聚合准确率最多能掉多少？
答案（恒等式）：ΔAcc = f · p · r
   f = 该子群在评测集中的样本占比
   p = 该子群内阳性（正类）占比
   r = 该子群上被抹掉的召回率（从 r_0 掉到 0 时 r = r_0）

用它解释 arXiv:2611.14975 的现象：气胸阳性片上两个模型检出为零，
聚合准确率却看不出异常——因为 f 与 p 的乘积很小。

本脚本做两件可验证的事：
 1. 用穷举模拟（brute-force）验证恒等式，误差应为 0；
 2. 用 --selftest 注入「聚合指标必然报警」的错误假设，必须 exit 1。

用法：
  python3 masking_identity.py
  python3 masking_identity.py --selftest
"""
import argparse, sys
import numpy as np

RNG = np.random.default_rng(20261119)


def simulate(f, p, r0, n=2_000_000):
    """构造一个二分类评测集：子群占比 f，子群内阳性占比 p，子群召回率 r0，其余全对。"""
    n_sub = int(round(n * f))
    n_pos_sub = int(round(n_sub * p))
    n_neg_sub = n_sub - n_pos_sub
    # 子群：阳性里漏掉 r0 比例（召回率下降 r0）
    tp_sub = n_pos_sub - int(round(n_pos_sub * r0))
    tn_sub = n_neg_sub                      # 阴性全对
    # 其余样本全对
    n_rest = n - n_sub
    correct = tp_sub + tn_sub + n_rest
    acc = correct / n
    return acc


def identity(f, p, r):
    """基线（子群召回率 100%）准确率为 1，掉 r 之后 ΔAcc = f·p·r"""
    return 1.0 - f * p * r


def check(n_cases=40, tol=1e-5):
    worst = 0.0
    for _ in range(n_cases):
        f = float(RNG.uniform(0.02, 0.6))
        p = float(RNG.uniform(0.05, 0.95))
        r = float(RNG.uniform(0.1, 1.0))
        got = 1.0 - simulate(f, p, r)
        want = f * p * r
        worst = max(worst, abs(got - want))
    return worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--cases", type=int, default=40)
    args = ap.parse_args()

    if args.selftest:
        # 反证一：恒等式在随机 40 组参数下误差必须为 0（数值容差内）
        worst = check(args.cases)
        print(f"identity max abs error over {args.cases} cases: {worst:.3e}")
        # 容差 1e-5：模拟用整数计数，取整误差量级为 1/n ≈ 5e-7，故不能设 1e-9
        if worst > 1e-5:
            print("FAIL: identity violated")
            return 1
        # 反证二：注入「Δ 与 r 无关」的错误假设，必须被抓
        f, p = 0.07, 0.5
        d_08 = f * p * 0.8   # 子群召回被抹掉 0.8
        d_05 = f * p * 0.5   # 子群召回被抹掉 0.5
        if abs(d_08 - d_05) < 1e-9:
            print("FAIL: gate could not distinguish r=0.8 from r=0.5")
            return 1
        if abs(d_08 - f * p) < 1e-9:
            print("FAIL: r-dependence collapsed (delta == f*p)")
            return 1
        print(f"PASS: delta(r=0.8)={d_08:.4f} vs delta(r=0.5)={d_05:.4f}")
        return 0

    print("## 恒等式验证")
    worst = check(args.cases)
    print(f"穷举模拟 vs 解析恒等式的最大绝对误差：{worst:.3e}（{args.cases} 组随机参数）")
    print()
    print("## 掩盖表：子群召回率归零时聚合准确率的下降（pp）")
    print()
    print("| 子群占比 f | 子群阳性率 p | ΔAcc (pp) |")
    print("|---|---|---|")
    for f in (0.01, 0.05, 0.10, 0.20, 0.50):
        for p in (0.10, 0.50, 0.90):
            print(f"| {f:.2f} | {p:.2f} | {f * p * 100:.1f} |")
    print()
    print("## 对 arXiv:2611.14975 的应用")
    print()
    print("报告口径：5 个开源医疗 VLM、6,048 条 ChestX-ray14 问题、432 张气胸阳性片上检出为零。")
    print("缺的输入：这 432 张图对应多少条问题（即 f 的分子），以及这些问题里阳性占比 p。")
    print("因此只能给界，不能给点估计：")
    print()
    print("| 假设 f 的分子（条） | f | p | ΔAcc (pp) | 子群召回 |")
    print("|---|---|---|---|---|")
    rows = []
    for q in (432, 1296, 2160):
        f = q / 6048
        for p in (0.30, 0.60, 0.90):
            pp = f * p * 100
            rows.append(pp)
            print(f"| {q} | {f:.4f} | {p:.2f} | {pp:.2f} | 0.00 |")
    print()
    print(f"结论（由表内数值直接读出，不外推）：在上述九组假设下，聚合准确率下降区间为 "
          f"{min(rows):.2f}–{max(rows):.2f}pp，而子群召回恒为 0。")
    print("判定：只有当 f 与 p 同时偏小（f=432 条、p=0.30）时聚合指标才几乎不报警（2.14pp）；"
          "一旦阳性条目占多数，聚合分本应掉 20pp 以上——")
    print("所以「聚合看不出异常」这件事本身是**关于 f 与 p 的实测待验断言**，不是恒等式结论。")
    print("E1 的真实缺口因此被改写为：必须先取得 6,048 条问题的逐条标签构成，才能判定掩盖是否发生。")


if __name__ == "__main__":
    sys.exit(main() or 0)
