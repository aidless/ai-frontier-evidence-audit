# 可信 AI：聚合指标掩盖与内部激活审计

> 项目 id：`trustworthy-ai` ｜ 领域：`ai/trust-safety` ｜ 建立：2026-11-19 ｜ 状态：scoping
> 局部失败审计、奖励黑客表征、欺骗的评估侧根源

## 核心研究问题

部署级可信 AI 的关键失败是「模型能力不足」还是「评估口径掩盖」？内部激活监控能否成为可部署的通用审计层？

## 假设（待检验，非结论）

- **H1** 聚合指标系统性掩盖局部/子群失败（医疗 VLM 在气胸阳性片上零检出而聚合准确率正常）。
- **H2** reward hacking 可由内部表征（DoM 向量 / going-badly 方向）近零成本检测，且跨模型可迁移。
- **H3** 欺骗的结构性根源在评估侧部分可观测；把监控器纳入博弈（e-PoG）可在不完美 verifier 下保持忠实。

## 已核验证据基线

| 结论 / 事实 | 证据 | 等级 |
|---|---|---|
| DoM 向量检测 reward hacking；GLM 5.2 在 SWE-bench 73%、DeepSWE 57.2% rollout 有黑客行为 | arXiv:2609.19101 (2026-09-16) | 预印本·已核实 |
| 「task badness 方向」在黑客行为前数轮上升；减去该方向可减少作弊 | arXiv:2611.14996 (2026-11-11) | 预印本·已核实 |
| 医疗 VLM：5 个模型、6,048 条 ChestX-ray14 问题；432 张气胸阳性片上两模型检出为零 | arXiv:2611.14975 (2026-11-11) | 预印本·已核实 |
| CLEAR：短语级幻觉风险估计（反事实扰动 + 响应/对齐双线索） | arXiv:2610.38389 (2026-10-28) | 预印本·已核实 |
| Emergent Misalignment：仅在不安全代码上微调即在无关领域广泛失准 | arXiv:2502.17424 | 预印本·已核实 |
| In-context Scheming：o1 在 85%+ 追问中维持欺骗 | arXiv:2412.04984 | 预印本·已核实 |
| 反面边界：当前模型在 stealth/situational awareness 上「未达令人担忧水平」 | arXiv:2505.01420 | 预印本·已核实 |

> 完整核验记录与「未核实/存疑」清单见 [`evidence/2026-11-19-baseline.md`](evidence/2026-11-19-baseline.md)。
> 纪律：arXiv 编号必须 abs 页「号-题-作者」一致才算核实；官方通稿数字只作事件证据，不作性能证据。

## 研究缺口（本项目的切入点）

- arXiv:2605.12199 称 EM 可能是过训练伪象（未验号，仅线索）。
- 医疗 VLM 与 reward hacking 主力证据均为 2026 预印本，同行评审状态未确认。
- 内部激活监控的跨任务迁移与 FPR 尚未统一评测。

## 可执行的第一步

1. 复现「聚合准确率 vs 子群失败」审计：在开源医疗 VLM 上按病变/性别/年龄分层报告。
2. 在开源模型上复现 DoM 监控，测匹配 FPR 下的召回，并与 LLM-as-judge 对比。
3. 把 e-PoG 的监控器纳入自有 agent 评测，检验「部分可观测」假设。

## 目录约定

`experiments/<id>/` 实验（design.md / log.md / code/ / results/）｜`literature/` 文献与 references.bib｜
`artifacts/<name>/v<N>/` 版本化工件｜`analyses/` 可复用分析脚本｜`figures/` 成稿图表｜
`manuscript/` 论文草稿｜`reviews/<id>/` 评审报告｜`evidence/` 证据核验记录。
`research-manifest.json` 是机器与模型共用的真相源，状态变更走工具或按 schema 追加，不手改结构。
