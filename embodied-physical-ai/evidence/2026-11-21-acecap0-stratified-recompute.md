# ACE-CaP-0 92.1% 分层复算（embodied E2）

> 复算：2026-11-21 ｜ 底物：arXiv:2611.16872v1 Table 1 ｜ 判据来源：`embodied-physical-ai/experiments/E2-offline-code-closed-loop/design.md`
> 脚本：`embodied-physical-ai/analyses/acecap0_stratified_recompute.py` ｜ 机器读数：`embodied-physical-ai/evidence/acecap0-stratified-recompute.json`

## 结论（先给）

design 卡问的是「92.1% 是否为少数场景的高均值，长尾是否稳定」。**答：不是，且在 n=30/场景的功效下长尾不显著偏离。** 四条预注册判据 C1–C4 全过，场景间差异（sd=5.02pp）几乎完全由二项抽样噪声解释（观测方差/噪声方差=1.04，χ²(7)=7.259, p=0.402）。92.1% 是 8 个场景大致齐平的结果，不是被某一两个高分场景抬起来的。

这是一份**对论文已报告聚合数字的分层算术复算**，不是真机复现，也不是 GR00T2/WAM 实验。design 卡的阻塞注记写的「GR00T2 权重未放」与它自己的判据不是同一件事——判据所需的 Table 1 逐场景数字是公开的，零底物即可复算。

## 1. 判据逐字与判决

design 卡判据：「92.1% 是否为少数场景的高均值，长尾是否稳定」

| 判据 | 定义 | 读数 | 结果 |
|---|---|---|---|
| C1 聚合一致性 | Σk/Σn == 221/240，与论文 92.1% 一致 | 221/240=0.9208 | PASS |
| C2 均衡设计 | 各场景 n 相同 → 加权均值==未加权均值 | 8 场景各 n=30；两均值均 0.9208 | PASS |
| C3 留一稳健 | 去掉任一场景后整体成功率极差 ≤ 3pp | 极差 2.38pp | PASS |
| C4 长尾稳定 | 最低场景 Wilson 95%CI 覆盖整体 92.1% | Bread Packing 83.3% [66.4%, 92.7%] 覆盖 92.1% | PASS |

`selftest` 四条反证注入（B1 聚合 220/240、B2 某场景 n≠30、B3 单场景拉动使 LOO 极差 6.19pp、B4 最低场景降到 50%）全部让对应判据翻红；B5 Wilson(25,30)=(0.6644,0.9266) 对表吻合。装置不是装饰。

## 2. Table 1 逐场景（底物）

| 场景 | 成功/30 | 成功率 | mean time (min) | output token (M) |
|---|---|---|---|---|
| Charger Insertion | 30/30 | 100.0% | 1.65 | 1.09 |
| Bread Packing | 25/30 | 83.3% | 1.93 | 2.14 |
| Bottle Uncapping | 27/30 | 90.0% | 2.23 | 1.17 |
| Cup Nesting | 28/30 | 93.3% | 1.58 | 0.95 |
| Flower Insertion | 27/30 | 90.0% | 1.37 | 0.92 |
| Chicken Plating | 29/30 | 96.7% | 1.12 | 0.75 |
| Parcel Reorientation | 28/30 | 93.3% | 0.97 | 1.07 |
| Shoe Packing | 27/30 | 90.0% | 2.27 | 1.87 |
| **Overall** | **221/240** | **92.1%** | — | — |

来源：`.tmp/fulltext/2611.16872.txt`，curl 2026-11-21 HTTP 200/179193B。全文逐字：「Each frozen program is then evaluated in 30 trials without further updates.」coding agent = Claude Opus 5.5；每任务最多 10 次人工辅助 scene reset（demo 收集的 reset 不计入）。

## 3. 为什么「不是少数场景拉动」

- **结构层**：8 场景各 30 trials，完全均衡（C2）。加权均值（按 trial 数）与未加权均值（按场景）相等，都是 0.9208——不存在「样本量大的场景权重高」这种拉动机制。
- **稳健层**：留一法把每个场景逐个拿掉，剩下 7 个场景的整体成功率落在 [90.95%, 93.33%]，极差仅 2.38pp（C3）。即使拿掉满分场景 Charger Insertion（30/30），整体也只从 92.08% 掉到 90.95%，仍在高位。没有任何单一场景是「顶梁柱」。
- **分布层**：场景成功率 sd=5.02pp，range=16.7pp（83.3%→100%），看起来有跨度；但在 n=30、p≈0.92 下，纯二项噪声的 sd 就是 √(0.92·0.08/30)=4.93pp。观测方差 0.002520 / 噪声方差 0.002430 = **1.04**——场景间的离散几乎全部是抽样噪声，没有额外而异质性。χ² 异质性检验 p=0.402 同向（不拒绝「8 场景同成功率」原假设）。

## 4. 为什么「长尾稳定」要加引号

最低场景 Bread Packing 83.3%（25/30），Wilson 95%CI [66.4%, 92.7%]——区间很宽，宽到把整体 92.1% 包了进去（C4 据此判「不显著偏离」）。但这是**低功效下的「不显著」，不是「证明稳定」**：

- n=30 的 Wilson 区间半宽约 ±13pp，即使真实成功率低到 66%，这个样本量也未必能把它与 92.1% 区分开。
- 论文全文没有报告逐 trial 序列、variance 或失败聚集，所以**场景内**的 trial 级波动（例如失败是否集中在前几次 reset、是否有学习效应）无法复算。本报告只能复算**场景间**方差。
- 正确表述：在本样本量下，没有证据表明存在显著拖后腿的长尾场景；不等于证明了长尾稳定。

## 5. 与 GR00T2 错配的澄清

design 卡的「依赖与阻塞」写的是「真机不可得；先做论文原始数据的分层复算」——这条路径零底物、本报告已完成。而 manifest E2 的 verdict 与 synthesis 阻塞表写的是「GR00T2 权重未放」，指向另一个更宏大的闭环实验（用 GR00T2/WAM 做离线代码生成 + 真机验证）。两者不是同一件事：

- ACE-CaP-0（arXiv:2611.16872）：已有 92.1% 真机结果，Table 1 公开逐场景数字，可复算分布问题。
- GR00T2/WAM：GitHub NVIDIA/Isaac-GR00T 最新 release 仍是 n1.7-release（2026-04-18），README grep GR00T2/N2/WAM 零命中，官方「12 月开放」截至 2026-11-21 未兑现。

本复算回答的是 design 卡自己的判据（92.1% 的分布问题），不需要 GR00T2 权重。GR00T2 闭环作为独立实验仍阻塞，不应与 E2 判据混为一谈。

## 6. 诚实边界（与 JSON 一致）

1. 只用 Table 1 报告的**聚合逐场景成功数**（k/30），没有逐 trial 序列 → 可复算场景间方差，无法复算场景内 trial 级方差 / 失败聚集 / 学习效应。
2. 每场景 n=30，Wilson CI ≈ ±13–14pp；「长尾稳定」是低功效下不显著，非证明稳定。
3. 这是论文自身数字的**算术一致性复算**，不是独立真机复现（无机器人、无仿真、无 GR00T2 权重）。
4. design 卡的 GR00T2 阻塞是另一实验；本复算不改变那个实验的阻塞状态。

## 7. 复现命令

```bash
python3 embodied-physical-ai/analyses/acecap0_stratified_recompute.py --selftest
python3 embodied-physical-ai/analyses/acecap0_stratified_recompute.py --run --out embodied-physical-ai/evidence/acecap0-stratified-recompute.json
```
