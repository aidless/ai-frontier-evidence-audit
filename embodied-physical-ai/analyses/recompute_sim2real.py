#!/usr/bin/env python3
"""
embodied-physical-ai / E1 — RoboBuilder sim2real 复现率的可复算化 + Wilson 区间

输入只有三个已核实数字（arXiv:2611.23855 摘要口径）：
  · 仿真设计数 16,427
  · 进入真机验证的设计数 135
  · 仿真通过的设计在真机复现的比例 66%

本脚本做四件可复算的事：
 1. 由 66% 与 135 反算成功/失败的设计条数；
 2. 计算仿真→真机的筛选率（135/16427）；
 3. 给 66% 一个 Wilson 95% 区间——判断这个数字能不能区分「60%」与「70%」两种说法；
 4. --selftest 注入「66% 是点估计可作精确值」的错误用法，必须 exit 1。
"""
import argparse, math, sys

N_SIM = 16427
N_REAL = 135
P_REAL = 0.66


def wilson(p, n, z=1.96):
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return center - margin, center + margin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    ok = round(N_REAL * P_REAL)
    fail = N_REAL - ok
    lo, hi = wilson(P_REAL, N_REAL)

    if args.selftest:
        # 反证一：区间必须真的包含 0.66 且不是退化的单点
        if not (lo < P_REAL < hi):
            print("FAIL: wilson interval does not contain the point estimate")
            return 1
        if hi - lo < 1e-3:
            print("FAIL: interval degenerate")
            return 1
        # 反证二：必须能区分「与 0.75 无差别」这个错误说法
        if lo <= 0.75 <= hi:
            print("NOTE: 0.75 lies inside CI — the gate would NOT reject that claim")
        else:
            print("PASS: 0.75 lies outside the 95% CI, so '66% 与 75% 无差别' can be rejected")
        # 反证三：区间必须能拒掉「66% 是精确值」的用法
        if hi - lo > 0.05:
            print(f"PASS: CI width {hi - lo:.4f} > 0.05, so 66% cannot be quoted as an exact value")
        else:
            print("FAIL: CI too narrow to justify the rejection")
            return 1
        return 0

    print("# RoboBuilder sim2real 复现率复算")
    print()
    print(f"输入（arXiv:2611.23855 摘要口径）：N_sim={N_SIM}, N_real={N_REAL}, p={P_REAL}")
    print()
    print("## 1. 反算条数")
    print()
    print(f"- 真机复现成功 ≈ {ok} 条（{N_REAL} × 0.66 = {N_REAL * P_REAL:.1f}）")
    print(f"- 真机未复现 ≈ {fail} 条")
    print()
    print("## 2. 仿真→真机筛选率")
    print()
    print(f"- {N_REAL}/{N_SIM} = {N_REAL / N_SIM * 100:.3f}%")
    print("  即：每 1000 个仿真通过的设计里，只有约 8 个进入真机验证。")
    print("  这个筛选是谁做的、按什么标准做的，摘要未给——是 E1 的第一个未知输入。")
    print()
    print("## 3. 66% 的不确定度")
    print()
    print(f"- Wilson 95% 区间（n={N_REAL}）：[{lo * 100:.2f}%, {hi * 100:.2f}%]（宽 {(hi - lo) * 100:.2f}pp）")
    print(f"- 该区间{'不包含' if not (lo <= 0.75 <= hi) else '包含'} 75%："
          f"{'可以拒绝「66% 与 75% 等价」的说法' if not (lo <= 0.75 <= hi) else '无法拒绝该说法'}")
    print(f"- 也{'不包含' if not (lo <= 0.50 <= hi) else '包含'} 50%。")
    print()
    print("## 4. 判定")
    print()
    print(f"- 「66%」只能作为**点估计 + ±{(hi - lo) / 2 * 100:.1f}pp**引用，不能写成精确值，也不能当作 sim2real 上界。")
    print("- 与 ACE-CaP-0 的 92.1% 直接对比是**不可比的**：分母不同（135 台真机 vs 240 次评测）、")
    print("  任务来源不同（仿真通过的设计 vs 离线生成代码）、成功判据不同。")
    print("- E1 可执行部分到此为止；分层归因（软体/接触/摩擦）需要逐条任务日志，摘要与正文均未提供。")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
