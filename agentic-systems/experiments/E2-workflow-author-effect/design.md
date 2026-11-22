# E2-workflow-author-effect: 固定执行者，只换工作流编写者

> 项目：`agentic-systems` ｜ 假设：`H1` ｜ 建卡：2026-11-19 ｜ 状态：completed（可判定性审计，非数值复现）

## 设计

1. WorkflowArena 子集：选 2–3 个专业域
2. 固定弱执行者，分别用 Opus 5.5 与普通模型编写工作流

## 判据

判据：工作流编写者造成的性能差异是否可复现、是否随任务难度变化

## 依赖与阻塞

需要 WorkflowArena 数据与 API 额度；机构署名仅摘要级，数据可用性待核。
**2026-11-21 结论**：底物不可得 + 论文自承每配置每任务只评一次、无方差估计 → 原判据「差异是否可复现/随难度变化」在公开数据上不可判读。改做 a-priori MDE 检测性审计（非复现）：145 任务下主效应 MDE=dz 0.234、难度交互 MDE=d 0.468（主效应 2×），Monte Carlo Type I=0.045 与 α=0.05 相容。结论=需每任务重复评测或扩到 ≥199 任务才判得开。见 evidence/2026-11-21-workflow-author-detectability.md。

## 日志

- 2026-11-21：可判定性审计完成。命令 `python3 agentic-systems/analyses/workflow_author_detectability.py --selftest`（PASS，4 反证捕获）与 `--mode full`（exit 0）。产物 `agentic-systems/evidence/workflow-author-detectability.json` + `agentic-systems/evidence/2026-11-21-workflow-author-detectability.md`。selftest 修 `_two_sided_power` 的 scipy nct nan 边界（sf 替 1−cdf、下尾 nan 置 0）。
