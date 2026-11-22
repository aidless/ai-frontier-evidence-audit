# 具身智能：两篇核心全文的深度核验 + 66% 口径辨析（2026-11-20）

**范围**：arXiv:2611.23855（RoboBuilder）与 arXiv:2607.05369（GaP），均为全文级，已验号（VERIFIED）。全文 HTML 存 `.tmp/fulltext/<id>.html`。

## 1. RoboBuilder：66% 到底是什么（口径纠错）

### 1.1 三个规模数字（全文逐字，已核）
> `16,427 simulations of 12,774 distinct robots and 135 physical robots built in an estimated 240 hours`

即：16,427 次仿真 / 12,774 个不同机器人设计 / 135 台实体机器人 / 约 240 小时建造。此前 `recompute_sim2real.py` 用的 N_sim=16427、N_real=135 与全文一致。

### 1.2 66% 的精确定义（关键纠错，全文逐字）
> `in the real world, where 66% of simulated passes hold across all levels`

以及方法段：
> `on the benchmark designs, never used for fitting, 66% of its passes cross the real course (Sec. 4)`

**判定**：66% 是"**学习到的仿真器判为通过的设计里，有多少比例在真机赛道上也通过**"——即 **sim-pass → real-pass 的复现率（replication/transfer rate）**，不是相关系数，不是成功率，不是 AUC。此前手稿与 `recompute_sim2real.py` 把它当复现率去做 Wilson 区间，口径正确。

### 1.3 必须区分的三个不同 "0.66"（避免张冠李戴）
全文里出现至少三处 0.66/66%，含义完全不同：

| 数值 | 出处 | 含义 |
|---|---|---|
| 66% | 摘要 + Sec.4 | sim-pass → real-pass 复现率（本方向核心量）|
| 0.66 | Figure 11 表 | Parts (Jaccard) 距离值（设计相似度指标）|
| AUC 0.66 (p=0.014) | real success 打分段 | 用分值预测真机成功的 AUC |

另有两个相关但不同的相关系数：sim 与 real 穿越时间的 Spearman 0.78 / Pearson 0.57（48 个设计）。→ **写任何数字时必须带尺名**，`recompute_sim2real.py` 中 `p=0.66` 明确指复现率，不能在正文里与 Jaccard/AUC 混用。

### 1.4 其余硬结论（全文逐字）
- `under public part data, none of 15 initial passing designs crossed the real course`：公开零件数据下，15 个初始通过设计真机全败 → 必须让 agent 从实测/视频里学仿真器。
- learned simulator `predicts 35 of the 38 labelled runs, including 9 of the 10 validation ones (Tab.25)`：仿真器验证预测 35/38、9/10。
- 闭环 `removes 72% of level-1 and level-2 failures`：给失败视频后 agent 重设计，消除 72% 的一二级失败。
- 边界：`Agents redesign after seeing the failure on the same course, so this measures recovery, not transfer of new designs` —— 测的是恢复，不是迁移。

### 1.5 对 E1-sim2real-replication 的影响
该卡已 completed：Wilson 95% CI [57.67%, 73.45%]（宽 15.78pp），不含 75% 也不含 50%。全文核准 66% 定义后，**结论更稳**：这就是 sim→real 复现率的点估计，区间宽到不能与 ACE-CaP-0 的 92.1% 相比（分母、任务、判据全不同）。全文数据反而支持"66% 只是粗点估计"的判断。

## 2. GaP：多智能体写码闭环的真实结构（此前只有摘要级）

### 2.1 身份与定位
- 标题（逐字）：`GaP: A Graph-as-Policy Multi-Agent Self-Learning Harness For Variational Automation (VA) Tasks`
- 作者机构：UC Berkeley + NVIDIA（Guanzhi Wang / Adithyavairavan Murali / Balakumar Sundaralingam 属 NVIDIA；S. Shankar Sastry 等属 UC Berkeley）。
- 定位：不是"一个 VLA 模型"，而是一个**多智能体编码 harness**——让多个 coding agent 协作编写/验证/递归改进机器人控制程序。

### 2.2 核心机制（全文逐字）
> `GaP combines the typed dataflow topology of the ROS computation graph with the reactive task logic and failure recovery of BTs, enabling (a) static type checking and verification, (b) explicit failure recovery loops`

两个支柱：
- **Modular Open Robot Skill Library (MORSL)**：模块化机器人技能库。
- **Self-Learning through Internal Simulation Rehearsal**：通过内部仿真彩排自学习。

**方法论意义**：Graph-as-Policy 把策略表示为**有类型的 ROS 计算图 + 行为树（BT）**，因此能①静态类型检查与验证、②显式失败恢复循环。这是"离线 agent 写可验证程序"主线的代表——智能不在模型权重里，在可检查的计算图里。

### 2.3 Benchmark（全文目录逐字）
- Benchmark I/II：Fulfill Grocery Orders / Pack Grocery Items（仿真 + 真机）。
- Benchmark III：Make Popcorn in sim and real。
- Benchmark IV：Insert USB-C Cables (Real)。

### 2.4 诚实边界
- 全文未核到"无模型在环"的逐字断言（此前摘要级笔记如此说，但本轮 HTML 中未定位到明确原句），此处不重复该主张，标为**未逐字核实**。
- 无公开代码/数据链接的核验证据（与四论文可达性探测一致）。
- 所有数字为作者自报。

## 3. 对本方向实验卡判决的影响

- `E1-sim2real-replication`：维持 completed，66% 定义全文核准，口径更稳。
- `E2-offline-code-closed-loop`：维持 BLOCKED——GR00T 2 权重截至 2026-11-20 未放出（releases 最新 n1.7-release 2026-04-18）。但 GaP 全文证明"离线 agent 写可验证程序"这条路本身成立， substrates 一旦放出即可推进。

## 4. 诚实边界

- 三个 "0.66" 的区分是本轮最重要的纠错；引用任何一个都必须带尺名。
- GaP 的"无模型在环"表述本轮未逐字核实，已从结论中移除，避免编造。
- 全文 HTML 存临时目录 `.tmp/`，不入库；关键句已在本文逐字引用。
