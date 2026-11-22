# 具身智能与物理 AI：离线 agent + Real2Sim + 真机验证

> 项目 id：`embodied-physical-ai` ｜ 领域：`ai/embodied` ｜ 建立：2026-11-19 ｜ 状态：scoping
> agentic robotics 能否稳定超越端到端 VLA，sim-to-real 保真度的可测边界

## 核心研究问题

「离线 agent 写程序 + Real2Sim + 真机验证」的 agentic robotics 范式，能否在非结构化、高变异任务上稳定超越端到端 VLA？其 sim-to-real 保真度的可测边界在哪里？

## 假设（待检验，非结论）

- **H1** 真机阶段代码冻结、agent 离线的 agentic 路线，在长程/高变异任务上优于端到端策略（ACE-CaP-0 是"冻结代码、评测无 agent 在环"的直接证据；GaP 全文确认 core=Graph-as-Policy，但"无模型在环"未逐字核实，仅作假设框架不作既成事实）。
- **H2** Real2Sim 保真度（视觉 + 物理参数）是 sim-to-real 成功率的主要瓶颈；「仿真通过但真机失败」的比例可量化（RoboBuilder 66% sim-pass→real-pass 复现率为反证）。
- **H3** 世界-动作联合模型（WAM，如 GR00T 2）的零样本与少样本收益来自视频-动作联合预训练，而非单纯数据量。

## 已核验证据基线

| 结论 / 事实 | 证据 | 等级 |
|---|---|---|
| GaP：多 coding agent 写/验/递归改进技能图，导出 ROS2；CoRL 2026 Spotlight | arXiv:2607.05369 | 同行评审·已核实 |
| RoboSimStudio：短视频→物理仿真 Real2Sim；「about an hour」出处 | arXiv:2610.18835 | 预印本·已核实 |
| Flip Anything：24 种工具、36 个版本，成功率 24.7%→95.0% | arXiv:2611.11941 (2026-11-09) | 预印本·已核实 |
| 擦金属杆墨水案例牵头人 Ken Goldberg/AUTOLab；「不到一小时」仅指 Real2Sim | Berkeley News (2026-11-09) | 媒体·已核实 |
| GR00T 2：World-Action Model；402,730h 人类视频；零样本 40%，5 演示+30 分钟微调→95%；Turbo 124ms | NVIDIA GEAR 官方 (2026-11-09) | 官方·已核实 |
| Anthropic 无机器人模型；Project Fetch 有 Claude 组耗时约一半；Embody 低层控制 0–5.5% | Anthropic 官方 (2025-11/2026-07) | 官方·已核实 |
| MHS 硬件接口标准（与 HHMI Janelia），设备集成从数周压到小时/分钟级 | Anthropic (2026-08-27) | 官方·已核实 |
| RoboBuilder：16,427 次仿真、135 台真机；仿真通过的设计仅 66% 真机复现（66% = sim-pass→real-pass 复现率，非相关系数/AUC） | arXiv:2611.23855 全文（2026-11-20 核） | 预印本·已核实 |
| ACE-CaP-0：冻结代码、评测时 agent 不在环；221/240=92.1% 真机成功率 | arXiv:2611.16872 | 预印本·已核实 |

> 完整核验记录与「未核实/存疑」清单见 [`evidence/2026-11-19-baseline.md`](evidence/2026-11-19-baseline.md)。
> 纪律：arXiv 编号必须 abs 页「号-题-作者」一致才算核实；官方通稿数字只作事件证据，不作性能证据。

## 研究缺口（本项目的切入点）

- 「多智能体」只在 GaP 代码生成阶段成立；Real2Sim 实际是单 agent。
- 「不到一小时」是 Real2Sim 子环节耗时，端到端远超一小时。
- GR00T 2 权重/代码官方写 12 月开放，截至 2026-11-19 未放出；「开源全栈」说法超前。
- Anthropic 不产机器人基础模型/VLA，引用时不得写成「Anthropic 发布机器人模型」。

## 可执行的第一步

1. 复现 Real2Sim→GaP→真机的最小闭环，记录各阶段墙钟与失败回灌次数。
2. 建立「仿真通过率 vs 真机通过率」对照表，量化 sim-to-real gap。
3. 在同一任务上对比 agentic（冻结代码）与端到端 VLA 的成功率与步数。

## 目录约定

`experiments/<id>/` 实验（design.md / log.md / code/ / results/）｜`literature/` 文献与 references.bib｜
`artifacts/<name>/v<N>/` 版本化工件｜`analyses/` 可复用分析脚本｜`figures/` 成稿图表｜
`manuscript/` 论文草稿｜`reviews/<id>/` 评审报告｜`evidence/` 证据核验记录。
`research-manifest.json` 是机器与模型共用的真相源，状态变更走工具或按 schema 追加，不手改结构。
