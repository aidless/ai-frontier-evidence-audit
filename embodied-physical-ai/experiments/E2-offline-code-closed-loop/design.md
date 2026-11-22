# E2-offline-code-closed-loop: ACE-CaP-0 离线生成 + 真机验证闭环的跨场景分布

> 项目：`embodied-physical-ai` ｜ 假设：`H1` ｜ 建卡：2026-11-19 ｜ 状态：completed（2026-11-21，分层复算，零底物）

## 设计

1. 冻结生成代码，评测阶段无 agent 在环
2. 报告成功率分布（不做单点平均），按场景分组

## 判据

判据：92.1% 是否为少数场景的高均值，长尾是否稳定

## 依赖与阻塞

真机不可得；先做论文原始数据的分层复算。

## 日志

- 2026-11-21：完成零底物分层复算。ACE-CaP-0（arXiv:2611.16872）Table 1 逐场景数字公开，直接复算 design 卡判据，无需真机/GR00T2 权重。
  - 命令：`python3 embodied-physical-ai/analyses/acecap0_stratified_recompute.py --selftest`（PASS，B1–B5 反证全红）→ `--run --out embodied-physical-ai/evidence/acecap0-stratified-recompute.json`（exit 0）。
  - 判据 C1–C4 全过：聚合 221/240=92.08%；8 场景各 n=30 均衡；留一极差 2.38pp（≤3pp）；最低场景 Bread Packing 83.3% Wilson CI [66.4%,92.7%] 覆盖整体。χ²(7)=7.259, p=0.402，观测方差/噪声方差=1.04。
  - 判决：92.1% 不是被少数场景拉动，长尾在 n=30 功效下不显著偏离（低功效不显著 ≠ 证明稳定）。
  - 产物：`embodied-physical-ai/evidence/2026-11-21-acecap0-stratified-recompute.md`、`embodied-physical-ai/evidence/acecap0-stratified-recompute.json`。
  - 边界：只用表1聚合数字，无逐 trial 序列（场景间方差可复算、场景内 trial 级方差不可）；算术复算非物理复现；manifest 原有的 GR00T2 阻塞指向另一实验，本卡判据不涉及。
