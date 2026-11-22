# 智能体：两篇核心全文的深度核验 + 一个可离线复算的翻案（2026-11-20）

**范围**：arXiv:2611.14960（Termination Lag）与 arXiv:2611.12799（Agentic-OPD），均为全文级，已验号（VERIFIED）。全文 HTML 存 `.tmp/fulltext/<id>.html`。

## 1. Termination Lag：论文自带 oracle = 可离线复算的干预（翻案点）

### 1.1 三个已核数字（全文逐字）
- `38–82% of successful runs achieve a correct solution on their initial source-code edit`（首次源码编辑即正确）
- `post-solution steps accounting for a median of 35–37% for Qwen3-Coder and 54–60% for Laguna-XS.2`（多余步骤占比中位数）
- `1–8% ... agents to undo their earlier correct patch`（继续活动撤销正确 patch 的比例）

### 1.2 关键新发现：oracle 是离线重算，不需真跑 Agent
论文自带一个 oracle 段（逐字）：

> `we consider an oracle that stops each run at its first correct patch ... this would eliminate a median of 35% and 37% ... for Qwen3-Coder ... 60% and 54% for Laguna-XS.2, and 54% for Haiku on Verified, while preserving every originally solved task`

且测量协议（逐字）：

> `We record the repository patch after every agent step and evaluate each distinct patch offline against the official benchmark tests`

**这两句合起来的含义**：作者已经把每个 agent step 的 patch 离线重放、用官方 benchmark test 判对错。所谓"oracle 早停"就是用每步 patch 的离线判定结果去找第一个正确 patch——这本身就是一次**离线重算**，不需要重新驱动 agent、不需要 API 配额、不需要 GPU。

### 1.3 对 E1-termination-lag-intervention 卡判决的翻案
此前该卡被判 BLOCKED（理由：需对同一批 SWE-bench 跑配对 Agent 运行，无 API 配额）。全文级证据表明：

- 论文的 oracle 干预指标（"消除 35–60% 多余步骤且保留所有已解任务"）可以在**已有的逐-step patch 序列 + 官方测试**上离线复算。
- **但**：作者并未放出数据/代码（外链仅 ALCF Aurora 文档 / NIST），逐-step patch 轨迹这个底物本身不在盘上。所以解封条件是二选一：①拿到作者的 patch 轨迹数据；②用本地可跑的 agent（需 GPU/API）自己生成一份 patch 序列再离线重算。
- 结论：E1 从"必须真跑 Agent"翻案为"**方法上可离线复算，卡在逐-step patch 轨迹底物**"。这是一个比原来更窄、更明确的 blocker。

## 2. Agentic-OPD：能力遗忘的机制与恢复（全文逐字）

- 问题定义：`standard practice keeps only the best-validation checkpoint and discards the rest. We show that this is lossy`
- 核心观察：`the union of problems solved across checkpoints far exceeds any single one. The discarded checkpoints thus form a teacher pool obtained at no additional training cost`
- 两个组件：
  - **HCN（Which Teacher to Distill From）**：Gain matrix / Scored pool / Scheduling teacher。
  - **LAD（Locality-Aware Distillation, Where to Trust）**：problem / rollout / turn 三层，`confines transfer to failed student rollouts on problems where the teacher performs better`。
- 量化：`across five agentic task domains and 24 benchmarks and task subsets, Agentic-OPD improves over its initialization checkpoint by up to 7.4 points`；DeepSearch 上 3 个 backbone 增益 2.6–7.4 分。
- Qwen3-4B-Instruct-2507 表格行（全文逐字）：Base 25.7 → GRPO 50.4 → OPSD 30.4 → **Agentic-OPD 55.6**（Avg 列）。
- 对照 SOTA（DeepSeek-V4.1 Avg 42.7 / GPT-5.6 Avg 25.4 等）只是表中参照行，**不是 Agentic-OPD 超越它们的结论**——4B 学生模型在 DeepSearch 子集超过更大模型属论文自述语境，需谨慎表述。

**方法论价值**：把"RL 之后"独立成一个阶段——post-RL capability recovery，与 RL 算法本身正交。 discarded checkpoints 变成免费教师池，这是一个可迁移到任何 RL 训练流程的通用思路。

## 3. 对本方向实验卡判决的影响

- `E1-termination-lag-intervention`：从 BLOCKED 翻案为 **BLOCKED（底物更窄）**——需要 patch 轨迹数据，方法已明确可离线复算；写报告时突出 oracle 离线协议。
- `E2-workflow-author-effect`：维持 BLOCKED（WorkflowArena 无 Code/Data，两条 Limitations 逐字存档）。

## 4. 诚实边界

- 两篇均无代码/数据放出，所有数字为作者自报，不可独立复现。
- oracle "保留所有已解任务"是作者在其轨迹上的结论；离线复算需要拿到同样的逐-step patch 判定序列才能验证。
- 全文 HTML 存临时目录 `.tmp/`，不入库；关键句已在本文逐字引用。
