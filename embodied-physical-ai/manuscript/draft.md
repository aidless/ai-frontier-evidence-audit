# 离线代码生成 + 真机验证：具身智能的范式转移与 sim2real 反证

**状态**：scoping 完成；证据截止 2026-11-20。`E1-sim2real-replication` 已完成（数字落盘），`E2-offline-code-closed-loop` 因 GR00T2 权重未放出 BLOCKED。
**可复算产物**：`analyses/recompute_sim2real.py` → `evidence/2026-11-19-sim2real-recompute.txt`；`evidence/2026-11-20-gr00t2-availability.txt`。

## 摘要
具身智能的核心方法论进步，是从"模型在环"转向"离线让 agent 写代码、真机验证"。我们核验了 Berkeley AUTOLab 的 Agentic Robotics 三件套，重算了 RoboBuilder 的 sim2real 复现率，并复核了 GR00T 2 的权重开放状态。结论：范式在收敛，但 sim2real 缺口与代码可得性是两道真实门槛。

## 1. Agentic Robotics 三件套（牵头人 Ken Goldberg / UC Berkeley AUTOLab，非 Abbeel/Levine）
- GaP arXiv:2607.05369 (CoRL 2026 Spotlight top 3.4%)：多 coding agent 写/验/递归改进技能图，导出 ROS2，core=Graph-as-Policy（typed ROS dataflow + 行为树，可静态类型检查 + 显式失败恢复）；作者含 Goldberg/Yuke Zhu/Linxi Fan/Sastry。"真机无模型在环"本轮全文未核到逐字原句，已撤回（见 fulltext-deepdive.md）。
- RoboSimStudio arXiv:2610.18835 (Apache-2.0，20 作者，NVIDIA Coumans/Macklin/Heiden)："about an hour" 出处。
- Flip Anything arXiv:2611.11941：24 工具 / 36 版本，成功率 24.7% → 95.0%。

"不到一小时擦杆"的真相：擦的是**金属杆上的墨水**；执行者 Eric Kaiyuan Chen、Shuangyu Xie，用 OpenAI Astra；**不到一小时仅指 Real2Sim 子环节**（含海绵形变）；中途机器人误判杆质量推倒杆，失败视频回灌修正。多智能体只在 GaP 阶段，Real2Sim 是单 agent——用户原综述把这两阶段混为一谈。

## 2. sim2real 反证（重算，可复算）
RoboBuilder arXiv:2611.23855 报 N_sim=16427、N_real=135、p=0.66（p 为 sim-pass→real-pass 复现率，非相关系数/AUC/Jaccard；详见 fulltext-deepdive.md 口径辨析）。重算：真机复现成功 ≈89 条、未复现 ≈46 条；筛选率 135/16427=0.822%；Wilson 95% 区间 [57.67%, 73.45%]（宽 15.78pp），**不含 75% 也不含 50%**。因此 66% 只能作点估计 ±7.9pp。与 ACE-CaP-0 的 92.1% 不可比（分母/任务来源/成功判据均不同）。ACE-CaP-0 arXiv:2611.16872 本身是"冻结代码、评测无 agent 在环"的设置，221/240=92.1% 真机。

## 3. GR00T 2 状态（复核，结论未变）
NVIDIA 2026-11-09 CoRL 发布；World-Action Model (WAM)；402,730h 第一人称视频 + 10,184h UMI + 23,500h 真机遥操作；零样本 50 任务 40%，5 演示+RTX5090 微调 30min → 95%。但截至 2026-11-20，GitHub NVIDIA/Isaac-GR00T 最新 release 仍 n1.7-release (2026-04-18)、tags 仅 n1.x，README 头条 N1.7 GA；官方承诺的 12 月权重开放未兑现 → E2 BLOCKED。上轮"grep 零命中"口径不精确：宽正则 N2 会匹配 Cosmos-Reason2-2B 的 "Reason2"，精确正则带 \b 后确实零命中。

## 4. Anthropic 澄清
Anthropic **无机器人基础模型/VLA**。Project Fetch (2025-11-12)、Claude plays robotics (2026-07-09，Embody 基准低层直接控制 0–5.5%)、MHS (2026-08-27) 都是 Claude 作为组件的研究，不是发布机器人模型。

## 参考文献（节选，均验号）
GaP 2607.05369 · RoboSimStudio 2610.18835 · Flip Anything 2611.11941 · RoboBuilder 2611.23855 · ACE-CaP-0 2611.16872 · GR00T 2 (NVIDIA CoRL 2026) · Gemini Robotics 1.5 2510.03342
