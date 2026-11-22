# E2 工作流作者效应：单次评测协议下的可判定性审计

> 项目：`agentic-systems` ｜ 卡：E2-workflow-author-effect ｜ 日期：2026-11-21
> 性质：**可判定性 / 检测性（MDE）审计，不是 WorkflowArena 数值复现，也不是新实验观测**

## 结论先行

WorkflowArena 底物不可得，且论文自承「每个配置每任务只评测一次、不给方差」，因此原判据「作者差异是否可复现、是否随难度变化」在公开数据上**不可判读**。本审计不伪造观测，改用预注册的功效分析回答一个可判的问题：**在单次评测协议下，多大的真实效应才判得开（MDE）**。结果：

- 主效应（配对 t，145 任务，α=0.05 双侧，power=0.80）：**MDE = dz 0.234**。小于此的作者效应，即便存在也测不出来。
- 难度交互（把 145 任务分 72/73 两半，独立两样本 t）：**MDE = d 0.468，恰为主效应的 2.0 倍**——「随难度变化」比「有差异」难判一倍，原卡把它并列要求是不现实的。
- Monte Carlo 校验：H0 拒真率 0.045（Wilson 95%CI [0.0396, 0.0511]，与 α=0.05 相容）；在 MDE 处实测功效 0.7996（解析 0.800），门本身有效。
- 灵敏度：dz=0.10 需 787 任务、dz=0.20 需 199、dz=0.30 需 90、dz=0.50 需 34。用现有 145 任务只能可靠检出 dz≥0.234。

**判决**：底物不可得 + 方差缺失 → 原判据不可判读；MDE 审计给出「要多大的效应、多少任务/重复次数才判得开」的定量门槛，作为该卡可执行结论。若未来拿到底物，需每任务重复评测（R=4 使 MDE 降到 0.117，R=16 降到 0.059）或扩到 ≥199 任务，才有意义地检验作者效应。

## 依据（逐字，已落盘）

`agentic-systems/experiments/E2-workflow-author-effect/availability.md`：
1. "Each configuration is evaluated once per task, so differences between closely ranked configurations are reported without variance estimates."
2. "Content and 3D deliverables are graded against task rubrics by an LLM judge, and agreement with human graders is not measured in this work."

论文规模：145 任务 / 9 模型（availability.md:30）。

## 装置与口径

- 分析单元 = **任务**（不是单次评测）。配对差 `d_i = score_A(task_i) − score_B(task_i)`。
- 主效应：配对 t 检验 H0 `E[d]=0`；难度交互：easy/hard 两组独立两样本 t。
- `δ` = 真实作者效应（分数点），`σ` = 单次评测 judge 抖动，`dz = δ/σ`。
- **SESOI 状态 = NOT_AVAILABLE_FROM_SUBSTRATE**：论文既不报方差也不测 human-judge 一致性，无法给出可辩护的分数点最小重要效应。按 statistical-power 纪律，不发明效应量、不做 post-hoc observed power，改为报 **MDE + 灵敏度曲线**。
- 数值全部由 `scipy.stats.nct` 非中心 t 精确计算；selftest 注入 4 类反证（Type I 失控 / MDE 不随 n 降 / 交互不比主效应难 / 重复评测不降 MDE）全部被捕获。

## 结果表

| 量 | 值 | 口径 |
|---|---|---|
| 主效应 MDE（145 任务，配对） | dz = 0.2342 | σ 为单次评测抖动 |
| 任务数灵敏度 | 48→0.4129 / 72→0.3347 / 100→0.2829 / 145→0.2342 | 越多越低 |
| 难度交互 MDE（72/73） | d = 0.4685（主效应的 2.0×） | 独立两样本 |
| 重复评测 R | 1→0.234 / 4→0.117 / 16→0.0586 / 64→0.0293 | 按 1/√R 缩放（以单次 σ 计） |
| H0 拒真率（MC 5000） | 0.045 [0.0396, 0.0511] | α=0.05 相容 |
| MDE 处功效（MC / 解析） | 0.7996 / 0.8000 | 一致 |

## 诚实边界

1. 这是**检测性审计**，不产出任何「作者效应真实存在/多大」的观测结论——底物根本不可得。
2. `dz = δ/σ` 是无量纲量；因 σ 未公开，无法换算成 WorkflowArena 的分数点门槛。给的是相对抖动的可判定性，不是绝对分数。
3. 难度交互按 50/50 近半分组；难度标签本身需外部标注，本审计假设分组已给定。
4. R 次重复的 1/√R 缩放假设评测抖动独立同分布；若 judge 偏差系统性（同一配置总被高估），重复不消除系统偏差——这正是 availability.md 第二条限制指出的风险，MDE 审计**无法**修复它。

## 复现

```bash
python3 agentic-systems/analyses/workflow_author_detectability.py --selftest
python3 agentic-systems/analyses/workflow_author_detectability.py --mode full \
  --out agentic-systems/evidence/workflow-author-detectability.json
```
