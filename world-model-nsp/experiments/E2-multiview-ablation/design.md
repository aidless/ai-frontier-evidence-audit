# E2-multiview-ablation: CF-WAM 动态多投影监督的单投影 vs 多投影消融

> 项目：`world-model-nsp` ｜ 假设：`H2` ｜ 建卡：2026-11-19 ｜ 状态：completed（合成诊断）

## 设计

原设计（CF-WAM 数值复现）因代码/权重未公开而阻塞；改为**合成数据方法学诊断**：

1. 潜状态 s 通过 4 个互补投影观测（visual/semantic/geometric/interaction），每投影只耦合一个子空间块
2. single（只用 visual）vs multi（4 视图 concat）预测下一潜状态，backbone/参数量相等
3. 跨本体类比：eval 时扰动 visual 投影矩阵（幅度+旋转），其他投影不变

## 判据

原判据（跨本体成功率增益）需 CF-WAM 底物，不可达。合成诊断改判两个可证伪子问题：
- Q1：multi 的 in-dist 状态预测误差是否更低
- Q2：multi 对单一投影扰动是否更鲁棒（退化比更小），且跨 seed 一致

## 依赖与阻塞

CF-WAM 权重与代码未公开（全文逐字 `Upon acceptance, we will release the code and data.`）。合成诊断不依赖该底物，已在云 GPU（AMD gfx1100）跑通。

## 日志

### 2026-11-21
- 脚本 `world-model-nsp/analyses/nsp_multiview.py`（selftest PASS，perturb_rel_fro=0.2558）
- smoke（1 seed, steps=150）：q1=true, q2=false（multi 退化比 2.39 > single 1.47，欠训练）
- full（3 seeds, steps=800, AMD Radeon Graphics, elapsed 18.91s）：single in-dist 0.009137/cross 0.077462/退化 8.501±0.434；multi 0.008143/0.024613/3.029±0.158；参数量均 68748
- 分析 `analyze_nsp_multiview.py`（selftest PASS）：q1_ratio=0.8912, q2_gap=5.472, 跨seed一致=true, **h2_supported=true**
- 产物：`evidence/nsp-multiview-full-result.json`、`evidence/nsp-multiview-analysis.json`、`evidence/2026-11-21-nsp-multiview-result.md`
- 诚实边界：非 CF-WAM 复现；信息互补不免费（multi 输入维度更大）；smoke/full Q2 不一致已如实记录；单步预测口径与 E1 长程 rollout 不可比
