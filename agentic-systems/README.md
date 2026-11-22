# 智能体系统：协同、协议与可审计失败

> 项目 id：`agentic-systems` ｜ 领域：`ai/agents` ｜ 建立：2026-11-19 ｜ 状态：scoping
> 多智能体的性能上限由模型能力还是工作流组织决定

## 核心研究问题

多智能体系统的性能上限由「模型能力」还是「工作流组织 / 协议 / 验证」决定？在什么条件下多 agent 优于单 agent，其失败模式如何被结构性审计与量化？

## 假设（待检验，非结论）

- **H1** 固定执行模型时，工作流组织（谁编写流程、如何委派、委派粒度）是可量化的性能决定因素（WorkflowArena 方向）。
- **H2** 多 agent 失败主要来自系统设计与 agent 间失配，而非单模型能力（MAST 14 类失败模式）。
- **H3** 评估侧「部分可观测」是智能体欺骗的结构性根源；把监控器纳入博弈（e-PoG）可在不完美 verifier 下保持忠实。
- **H4** RL 训练的能力遗忘可通过被丢弃 checkpoint 的 on-policy 蒸馏恢复（Agentic-OPD）。

## 已核验证据基线

| 结论 / 事实 | 证据 | 等级 |
|---|---|---|
| WorkflowArena：145 个长程任务/8 域/9 模型；无全域最优配置，工作流组织可量化影响性能 | arXiv:2611.12856 (2026-11-09) | 预印本·已核实 |
| Agentic-OPD：GRPO 丢弃 checkpoint 造成遗忘；HCN+LAD；最高 +7.4 分 | arXiv:2611.12799 | 预印本·已核实 |
| Termination Lag：成功运行 38–82% 在首次源码编辑即得正确解；1–8% 继续活动撤销正确 patch | arXiv:2611.14960 (2026-11-11) | 预印本·已核实 |
| e-PoG：评估侧部分可观测博弈；欺骗缓解 +26.0%、成功率最高 +39.8%（自报） | arXiv:2611.12835 (2026-11-09) | 预印本·已核实 |
| MAST：1600+ 标注轨迹、7 框架、κ=0.88、14 种失败模式 3 大类 | arXiv:2503.13657 | 预印本·已核实 |
| MCP 捐给 Linux Foundation 旗下 AAIF；月 SDK 下载 >9700 万、活跃 server 1 万 | MCP 官方博客 (2025-12-09) | 官方·已核实 |
| A2A v1.0 生产稳定版；2026-08 加入 AAIF，>150 组织 | a2a-protocol.org (2026-03-12) | 官方·已核实 |

> 完整核验记录与「未核实/存疑」清单见 [`evidence/2026-11-19-baseline.md`](evidence/2026-11-19-baseline.md)。
> 纪律：arXiv 编号必须 abs 页「号-题-作者」一致才算核实；官方通稿数字只作事件证据，不作性能证据。

## 研究缺口（本项目的切入点）

- 26.0%/39.8% 为论文自报，未独立复现。
- WorkflowArena 机构归属仅搜索摘要来源。
- MCP 首发日（2024-11）未在公告页核实；A2A 首发方与日期待核实。

## 可执行的第一步

1. 在 WorkflowArena 上做「单 agent vs 多 agent vs 固定工作流」三臂对照，固定同一执行模型。
2. 把 Termination Lag 作为效率指标纳入自有评测，统计「首次编辑即正确」比例与撤销率。
3. 复现 MAST 标注流程，用自有轨迹验证 14 类失败模式的分布。

## 目录约定

`experiments/<id>/` 实验（design.md / log.md / code/ / results/）｜`literature/` 文献与 references.bib｜
`artifacts/<name>/v<N>/` 版本化工件｜`analyses/` 可复用分析脚本｜`figures/` 成稿图表｜
`manuscript/` 论文草稿｜`reviews/<id>/` 评审报告｜`evidence/` 证据核验记录。
`research-manifest.json` 是机器与模型共用的真相源，状态变更走工具或按 schema 追加，不手改结构。
