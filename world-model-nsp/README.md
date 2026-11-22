# 世界模型与 Next-State Prediction (NSP)

> 项目 id：`world-model-nsp` ｜ 领域：`ai/world-models` ｜ 建立：2026-11-19 ｜ 状态：scoping
> 从 next-token 到 next-state：表征、监督投影与可交互性上限

## 核心研究问题

以「预测动作/干预后的世界状态」为核心训练目标的世界模型，能否在长时程、跨本体、可交互条件下替代纯符号 next-token 预测，成为具身与规划的统一底座？其能力上限由表征、监督投影还是数据规模决定？

## 假设（待检验，非结论）

- **H1** NSP 相对 next-token 的增益主要来自「动作条件状态转移」监督，而非表征容量；固定参数与数据下，动作条件 NSP 的长时程预测误差累积显著低于 next-frame / next-token 基线。
- **H2** 单一固定 next-state 表征（RGB 或单 latent）是当前瓶颈；动态多投影监督（视觉/语义/几何/交互）能提升跨本体泛化（CF-WAM 方向）。
- **H3** 交互式世界模型可用性受 token 带宽约束（4K@60fps 需 >100K tokens/s、1 小时交互需 >100M token context），给定算力下存在可交互性上限。

## 已核验证据基线

| 结论 / 事实 | 证据 | 等级 |
|---|---|---|
| 世界模型思想源头：压缩时空表征、在「梦境」中训练策略 | arXiv:1803.10122 (2018) | 预印本·已核实 |
| 论文标题中最早显式出现 next state prediction | arXiv:2410.04940 (2024-10) | 预印本·已核实 |
| 首次把 NSP 写成世界基础模型范式；125K 小时视频、160M 事件标注 | arXiv:2606.30534 Orca (2026-06-29) | 预印本·已核实 |
| NSP 为 World Models 核心范式的综述定调；RoboCasa-GR1 82.50% | arXiv:2609.34414 CF-WAM (2026-09-28) | 预印本·独立验号 |
| Genie 3：文本生成可实时导航世界，24fps/720p，一致性数分钟 | DeepMind 官方博客 (2025-08-05) | 官方·已核实 |
| V-JEPA 2：>1M 小时视频；<62h 无标注 Droid 数据零样本控制 Franka | arXiv:2506.09985 | 预印本·已核实 |
| RTFM：单 H100 交互帧率；4K@60fps 需 >100K tokens/s、1h 需 >100M context | worldlabs.ai/blog/rtfm (2025-10-16) | 官方·已核实 |
| Ctrl-World 策略评测与真机 Pearson 0.986（Cosmos-Predict 2.5 为 0.483） | arXiv:2510.10125 | 预印本·已核实 |
| WorldArena：16 指标/6 子维度/14 模型，感知质量与功能效用存在差距 | arXiv:2602.08971 | 预印本·已核实 |

> 完整核验记录与「未核实/存疑」清单见 [`evidence/2026-11-19-baseline.md`](evidence/2026-11-19-baseline.md)。
> 纪律：arXiv 编号必须 abs 页「号-题-作者」一致才算核实；官方通稿数字只作事件证据，不作性能证据。

## 研究缺口（本项目的切入点）

- NSP 无单一「发明人」；Emu3.5 训练目标仍是统一 next-token，正文未出现字面 next-state prediction。
- Genie 4 官方未给 FPS/分辨率，不能外推 Genie 3 指标。
- 可交互性与 token 带宽的定量关系尚无统一 benchmark。

## 可执行的第一步

1. 固定同一 backbone，做 next-token / next-frame / action-conditioned NSP 三臂对照，报告长时程误差累积曲线（horizon 10/100/1000 步）。
2. 用 WorldArena 子集只测「功能效用」而非感知质量，验证感知-效用脱节。
3. 复现 CF-WAM 的动态多投影监督，做单投影 vs 多投影消融。

## 目录约定

`experiments/<id>/` 实验（design.md / log.md / code/ / results/）｜`literature/` 文献与 references.bib｜
`artifacts/<name>/v<N>/` 版本化工件｜`analyses/` 可复用分析脚本｜`figures/` 成稿图表｜
`manuscript/` 论文草稿｜`reviews/<id>/` 评审报告｜`evidence/` 证据核验记录。
`research-manifest.json` 是机器与模型共用的真相源，状态变更走工具或按 schema 追加，不手改结构。
