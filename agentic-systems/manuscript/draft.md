# 多智能体工作流：协议标准化、能力修复与终止效率的可审计性

**状态**：scoping 完成；证据截止 2026-11-20。`E1-termination-lag-intervention` / `E2-workflow-author-effect` 因代码不可得 + GPU 被占而 BLOCKED。
**可复算产物**：`experiments/E2-workflow-author-effect/availability.md`（WorkflowArena 无 Code/Data；两条 Limitations 逐字存档）。

## 摘要
智能体研究从单点工具走向复杂协同，MCP/A2A 等通信协议的标准化提供了通用"语言"。但评估侧存在三类可审计性问题：工作流基准无方差估计、能力修复的增益为作者自报、编码智能体的"终止延迟"刚被量化。我们核验了这些断言的一手来源，并指出每条从"已报道"到"可复现"之间缺什么。

## 1. 协议标准化（事件已核实）
- MCP：Anthropic 开源，2025-12-09 捐给 Linux Foundation 旗下 AAIF；官方称月 SDK 下载 >9700 万、活跃 server 1 万；规范 current 2026-07-28。
- A2A：v1.0 2026-03-12 生产稳定版；2026-08 加入 AAIF，>150 组织，GitHub 26.6k stars，Apache-2.0，6 SDK。
这两条是产业事件，数字为官方口径，无独立审计。

## 2. 工作流评估的可审计缺口
WorkflowArena arXiv:2611.12856 (2026-11-09)：145 任务 / 8 域 / 9 模型 / 共享预算 14400s；结论"无全域最优"，Claude Opus 5.5 写工作流显著提升弱执行者。但全文 HTML（67,479 字符）**无 Code/Data 章节与外链**，Acknowledgements 逐字 "This project is funded and supported by Navers Lab, Einsia.AI."。两条 Limitations 逐字：
1. "Each configuration is evaluated once per task, so differences between closely ranked configurations are reported without variance estimates."
2. "Content and 3D deliverables are graded against task rubrics by an LLM judge, and agreement with human graders is not measured in this work."

因此 H1 必须从"写工作流提升多少分"改写为"差异是否超过单次评测抖动"——在方差缺失下，前者不可判。

## 3. 能力修复与终止效率
- Agentic-OPD arXiv:2611.12799 (v1 2026-11-09/v2 11-13)：GRPO 只留 best-validation checkpoint 造成遗忘；丢弃 checkpoint 当教师池；HCN 按覆盖率选教师 + LAD 只在学生失败且教师更优处迁移；5 任务域 / 24 benchmark，最高 +7.4 分。代码未放出，"4B 学生 deep search 超 GPT-5.6/DeepSeek-V4.1"为论文自述。
- Termination Lag arXiv:2611.14960 (2026-11-11, Musa Cim 等)：5 模型 / 2 框架 / 3 SWE-bench；成功运行 38–82% 在首次源码编辑即正确；多余步骤中位 Qwen3-Coder 35–37%、Laguna-XS.2 54–60%；1–8% 继续活动撤销正确 patch。无代码链接。
- e-PoG arXiv:2611.12835：评估侧部分可观测是欺骗的根源；SPOE 解；自报欺骗缓解 +26.0%、成功率最高 +39.8%。
- MAST arXiv:2503.13657：1600+ 轨迹 / 7 框架 / κ=0.88 / 14 失败模式 3 类。

## 4. 交叉主线
智能体的可信问题与"评估侧部分可观测"同源：欺骗（e-PoG）、终止延迟（Termination Lag）、工作流无方差（WorkflowArena）都是"聚合指标掩盖局部失败"的不同 manifestations。共同出路是把评估从聚合分数转向局部失败审计。

## 参考文献（节选，均验号）
WorkflowArena 2611.12856 · Agentic-OPD 2611.12799 · Termination Lag 2611.14960 · e-PoG 2611.12835 · MAST 2503.13657 · MultiAgentBench 2503.01935 · 协议综述 2504.16736
