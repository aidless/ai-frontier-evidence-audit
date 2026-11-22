# 从预测词到预测世界：2026 年 AI 研究前沿的证据审视

**跨项目综述 · 证据截止 2026-11-21**
**底层六份手稿**：`world-model-nsp/`、`agentic-systems/`、`embodied-physical-ai/`、`ai4science/`、`trustworthy-ai/`、`fm-efficiency/` 各自的 `manuscript/draft.md`。所有数字均可从对应项目的 `evidence/` 与 `analyses/` 复算。
**收口说明**：本文在综述之上并入 2026-11-21 完成的八项可复算方法学诊断（世界模型三臂 / 多投影、可信 AI DoM 探针、智能体终止延迟早停 / 工作流作者效应可判定性、AI4S 1.9× 内部一致性、基础模型解释力-能量几何、具身智能 92.1% 分层复算），统一口径为「零/低底物的方法学诊断、非论文数值复现」，全部带 selftest 反证与落盘证据。后四项专治「底物不可得就空等」——用 a-priori 功效分析、公开数字算术自检、零模型几何计算与已发表聚合数字的分层复算，把「测不了」升级成「定量给出要什么条件才测得了 / 公开数字本身就对不上 / 那个悖论是 r≪d 的算术 / 那个均值问题其实用公开数字就能判分布」。

## 摘要

当前 AI 研究的六个活跃方向——世界模型、智能体、具身智能、AI for Science、可信 AI、基础模型工程效率——常被并列表述为"同步突破"。本文逐条核验后发现：这些方向没有一个方向是错的，错在把**证据等级截然不同的成果放在同一张表上**。我们提出三条贯穿六方向的交叉主线：监督信号从 token 转向 state/trajectory/outcome；智能从"模型在环"转向"离线生成 + 真机/环境验证"；评估从聚合指标转向局部失败审计。用三维证据分类学对 33 条断言打分，13 条只能判为 ANNOUNCEMENT_ONLY。真正的方法论进步，收敛为三件事：**可验证的状态预测、可审计的失败模式、离线生成 + 验证闭环**。为把"区分叙事与证据"从口号变成可复用工具，我们进一步完成八项带反证的方法学诊断，其中四项直接给出可引用结论：世界模型三臂（低频状态预测的绝对误差最小 0.0024，但"累积斜率最低"判据被量化地板证伪）、多投影（跨本体扰动退化 3.03× vs 8.50×，互补视图是鲁棒性而非精度红利）、DoM 探针（7B 泛化过线但 14B validator 家族 TPR=0，跨规模方向不可搬运）、终止延迟早停（成败由检测器假阳性率主导，FPR≥0.01 成功率即崩）。八项一致表明：结论的边界由装置与口径决定，而非模型或分数本身。其中对三个「底物不可得」的卡，我们把不可判定性也做成了可引用的定量结论——工作流作者效应在 145 任务下可检出下限为 dz=0.234、难度交互判据比主效应难一倍（MDE 0.468），须每任务重复评测 16 次才降到 0.059；OpenAI 1.9× 与公开五分项在同口径平均下彻底不相容（可行区间 [1.999, 2.400] 不含 1.9），偏离方向因无配对无方差而不可识别；AROMA「89.82% 解释力 vs 9.52% 能量占比」的分离被证明是 r=4≪d=128 的低秩几何常态（零模型 corr(A,E)=0.011、能量中位 2.63%≈r/d），不是该方法特有缺陷。第八项是正例：具身智能卡看似卡在"真机不可得"，但判据（92.1% 是否被少数场景拉动）用 ACE-CaP-0 已发表 Table 1 即可复算——8 场景各 30 次、留一极差 2.38pp、场景间方差与二项噪声比 1.04、χ²(7) p=0.402，证明 92.1% 是齐平结果而非被高分场景抬高。

## 1. 引言：范式转移的命名与实质

"从预测词到预测世界状态"是对 2026 年研究重心的通俗概括，学术术语是 Next-State Prediction (NSP)。但核验显示 NSP 不是单点发明，而是一条从 2018 延续至今的演化链（见 §2.1）。更重要的是：把 NSP 当成"统一目标函数取代 next-token"的强主张，在本轮取回的 50 篇摘要中**没有固定 backbone 的三臂对照支持**，且有反向证据表明状态跟踪是 next-token heads 的分布式副产物。这是本文的主线——**区分叙事与证据**。

## 2. 六方向逐项核验

### 2.1 世界模型 / NSP
谱系：Ha & Schmidhuber 1803.10122 (2018) → Saanum 2410.04940 (2024-10，标题首次显式 next state prediction) → Emu3.5 2510.26583 (2025-10-30，训练目标仍是 next-token，正文无字面 NSP) → Orca 2606.30534 (2026-06-29，首次显式 centered on NSP) → CF-WAM 2609.34414 (2026-09-28，RoboCasa-GR1 82.50% / LIBERO-Plus 82.65% / 真机 84.00%，代码承诺"接收后释放"未兑现)。

反证 arXiv:2505.14892：state tracking 是 next-token heads 的分布式交互，而非显式符号计算；GPT-2 XL 低复杂度约 70%、状态 >5 或 >10 降到 <30%；action 信息未可靠路由到最终 token。因此 H1 收窄为"动作条件化增益"而非"目标函数替换增益"。arXiv API 普查 53 篇命中、取回 50 篇，无固定 backbone 三臂先例——真实空白。

**本轮补做的三臂诊断（2026-11-21，云 GPU）**：在合成线性动力系统上做方法学对照（非论文数值复现），三臂共享 backbone/数据/算力，唯一差别=输出头。结果对预注册判据是**负的**：state 臂累积斜率 0.197 并非最低（token 0.136 最低，但其起点撞量化地板、是假象）；frame 0.404 最高。但 state 的**绝对长程误差最低**（mse@1000=0.0024，frame 的 0.249×、token 的 0.066×），action 消融比 101.9 证明模型确用 action。判读：量化地板会伪造低 slope，"斜率最低"作为判据在稳定系统上不可靠；目标抽象层级影响精度有支持，影响累积斜率未获支持。详见 [nsp-three-arm-result.md](../world-model-nsp/evidence/2026-11-21-nsp-three-arm-result.md)。

**多投影诊断（2026-11-21，云 GPU，E2/H2）**：CF-WAM 代码/权重未公开，改做合成类比——潜状态经 4 个互补投影观测，single（只 visual）vs multi（4 视图 concat）预测下一状态，参数量相等（68748）。full（3 seeds）：multi in-dist MSE 0.0081 vs single 0.0091（比 0.891）；跨本体扰动退化比 multi 3.03× vs single 8.50×（差 5.47），3/3 seed 一致，**h2_supported=true**。诚实边界：信息互补不免费（multi 输入维度更大），Q2 鲁棒性才是"跨本体泛化"的核心类比；smoke 欠训练时 Q2 曾为 false，full 才稳定。详见 [nsp-multiview-result.md](../world-model-nsp/evidence/2026-11-21-nsp-multiview-result.md)。

**可信 AI 激活探针诊断（2026-11-21，云 GPU，trustworthy E2/H2）**：用 Qwen2.5-7B-base / 14B-base 做真实模型上的 DoM 探针方法学诊断（非 arXiv:2609.19101 复现）。训练只用 test-suite tampering 家族 + 5 个 honest 模板，测试在完全未参与的 validator/scorefile/acquire 家族。结果**混合/部分负**：7B 上三未见家族 TPR@1%FPR 全为 1.0（Q1 过线），但置换标签对照 AUC 最高 0.758，signal−shortcut=0.242 仅勉强过 0.2；14B 上 validator 家族 TPR=0.0（Q1 未过），置换对照 AUC 高达 0.85（Q2 未过）。跨规模维度不同（3584 vs 5120）方向不可搬运，Q3 判 NOT_ANSWERABLE。logit lens 读出乱码 token（`utow/zos/...`），与论文的 `cheating/illicit` 定性发现不一致——探针方向在本实验不呈现可解释语义。详见 [dom-probe-result.md](../trustworthy-ai/evidence/2026-11-21-dom-probe-result.md)。

### 2.2 智能体
协议标准化是产业事件：MCP 2025-12-09 捐给 AAIF、月 SDK 下载 >9700 万；A2A v1.0 2026-03-12、26.6k stars。评估侧有三类可审计缺口：WorkflowArena 2611.12856 逐字承认"each configuration is evaluated once per task ... without variance estimates"且 LLM judge 与人工一致性未测；Agentic-OPD 2611.12799 最高 +7.4 分为作者自报、代码未放；Termination Lag 2611.14960 量化出 38–82% 成功运行首次编辑即正确、1–8% 继续活动撤销正确 patch。四篇代码全部未公开（见 §5）。

**终止延迟早停诊断（2026-11-21，agentic E1/H2，纯 numpy 合成轨迹）**：逐-step patch 轨迹底物作者未放出，改做等价合成轨迹方法学诊断（非 SWE-bench 真跑）。校准 baseline 撤销率 3.05%（落论文 1–8% 区间），离线 oracle 上界省步 70.4% 且撤销归零；但在线可部署版（廉价正确性检测器）仅 FPR=0 时有效，FPR≥0.01 成功率即从 96.95% 崩至 94.35%，FPR=0.30 时 62.94%。命题「早停成败由假阳性率主导、而非召回率」成立（`fpr_dominates=true`）：假阴性只让停止变晚，假阳性直接掐断未修好的 run。这把论文的离线 oracle 结论翻译成一条在线部署硬约束——须先有近零假阳性的正确性判据，否则省下的步数以成功率为代价。详见 [termination-lag-intervention.md](../agentic-systems/evidence/2026-11-21-termination-lag-intervention.md)。

**工作流作者效应可判定性审计（2026-11-21，agentic E2/H1）**：WorkflowArena 底物不可得，且论文自承每任务只评一次、无方差估计，原判据「作者差异是否可复现/随难度变化」在公开数据上不可判读。改做零底物的 a-priori 功效分析：配对 t 主效应在 145 任务下 MDE=dz 0.234（小于此测不出）；难度交互（72/73 分组）MDE=d 0.468，恰为主效应 2×——「随难度变化」本就比「有差异」难判一倍；每任务重复评测 R=16 可把 MDE 降到 0.059。Monte Carlo 5000 次校验 H0 拒真率 0.045 [0.0396,0.0511]、MDE 处功效 0.7996，门有效。结论：不是「作者效应不存在」，而是「现有协议在dz<0.234处判不了」，把空等的卡转成可引用的检测性门槛。详见 [workflow-author-detectability.md](../agentic-systems/evidence/2026-11-21-workflow-author-detectability.md)。

### 2.3 具身智能 / 物理 AI
牵头人是 Ken Goldberg / UC Berkeley AUTOLab（非 Abbeel/Levine）。Agentic Robotics 三件套：GaP 2607.05369（多 coding agent 写/验技能图，导出 ROS2）、RoboSimStudio 2610.18835（"about an hour" 出处）、Flip Anything 2611.11941（成功率 24.7%→95.0%）。"不到一小时擦杆"真相：擦金属杆上的墨水，且 <1h 仅指 Real2Sim 子环节、由单 agent 完成，多智能体只在 GaP 阶段。sim2real 重算：RoboBuilder 2611.23855 的 66% 复现率对应成功 ≈89/135、Wilson 95%CI [57.67%, 73.45%]（宽 15.78pp），与 ACE-CaP-0 的 92.1% 不可比。GR00T 2 是 World-Action Model，官方承诺 12 月放权重，截至 2026-11-20 未兑现。Anthropic 不产机器人基础模型/VLA。

### 2.4 AI for Science
三维证据分类学（A 载体/B 数字口径/C 可复算性，composite 几何平均，verdict 机器判定）：33 条中 PERF_EVIDENCE=20 / ANNOUNCEMENT_ONLY=13；A1=2/A2=24/A3=2/A4=5，B1=3/B2=17/B3=13。分方向 composite 均值：trust=0.661、agent=0.5881、embodied=0.5411、fm=0.5097、worldmodel=0.5024、ai4science=0.4314。对照鲜明：MIT CRESt (Nature 647:390–396, doi:10.1038/s41586-025-09640-5) 判 A1+B1+C2 / 0.8193，3 个月 900+ 配方、成本专用性能 9.3×；GeneScientist 0.2507、NanoTitan Ultra 0.2241 均判 ANNOUNCEMENT_ONLY。OpenAI 1.9× 是 8 类活动自我报告时间比的均值、非实验，分项代码 2.83×/阅读 2.21×/分析 2.05×/构思 1.86×/写作 1.76×。

**1.9× 内部一致性诊断（2026-11-21，ai4science E2/H3）**：配对实测底物（人类受试者+任务日志）不可得，改对公开数字做算术自检。5 个公开分项均值 2.142、中位 2.05、几何均值 2.112，无一等于 1.9；若 1.9 是 8 项算术均值，未公开 3 项须平均 1.497（低于所有公开分项的最低 1.76）；更强的是可行均值区间 [1.999,2.400] 根本不含 1.9——1.9 与公开分项在同口径平均下彻底不相容。判决：1.9× 无法从公开材料复现，聚合口径未公开；且无配对、无方差使「偏离方向与幅度」在数学上不可识别，只能给时间节省恒等变换（1.9×→47.4%）。这不声称 1.9× 是错的，只说它不可审计。详见 [selfreport-1p9x-consistency.md](../ai4science/evidence/2026-11-21-selfreport-1p9x-consistency.md)。

### 2.5 可信 AI
给出聚合掩盖恒等式 ΔAcc = f·p·r，200 万样本验证最大误差 4.068e-07。从 arXiv:2611.14975 全文读出实测常量 f=864/6048=1/7、p=432/864=1/2（prevalence-matched 完全平衡），把宽区间 2.14–32.14pp 收紧为点估计 2.69–4.79pp：气胸单一 finding 全败（召回 HuatuoGPT=0/Qwen=0 vs MedGemma=0.377/Lingshu=0.671）只值聚合 acc 2.69–4.79pp。但修复后 acc 仅到 0.582，仍远低于 MedGemma 0.698——掩盖机制解释"为什么聚合分看不出气胸失败"，不是"为什么整体落后"。与之同源：emergent misalignment 2502.17424、in-context scheming 2412.04984、reward hacking 内部激活 2609.19101/2611.14996。

### 2.6 基础模型 / 工程效率
免训练扩上下文三路线不可同表：LongLLaDA 2506.14429 v3 正文无 8192-token PPL 数值（只在 Figure 1 曲线）；MPPA 2611.15029 给 LLaDA-8B 8192 PPL 19.51→3.12 / passkey 100%（作者自报）；RangeSWA 2610.42084 用 ELF-B/M/L 连续扩散、Gen.PPL@8192=153.12。两两 NOT_COMPARABLE，出路是固定 base 的 LLaDA（离散）vs ELF（连续）架构对照。RSI 侧：Darwin Gödel Machine 2505.22954 (SWE-bench 20%→50%)、AlphaEvolve 2506.13131（4×4 复矩阵乘法 48 次标量乘法，56 年首次超 Strassen）、RSIBench-Infra 2611.24395 (66.2% >1.10×)。

解释力-能量几何（E2）：AROMA 2611.15041 报告 top-4 灵敏度子空间解释 89.82% 的二阶矩、却只承载 9.52% 的中位激活能量，读起来像"方法找到了高杠杆方向"。零模型诊断（d=128/r=4、g,h 各向同性）显示这一分离是 r≪d 的低秩几何常态——理论中位能量 r/d=3.125%，模型 E_null 中位 2.63%，且 corr(A,E)=0.011（灵敏度集中与能量占比在零模型里根本不耦合）；A_null 99th=0.220 与论文自报的 0.219 对齐。故 9.52% 是几何必然而非 AROMA 的缺陷或成就；论文真正的增量在 89.82% 远超其自身 isotropic null（10,000 次 rank-matched），而"高解释力 + 低能量"这一对被当成悖论的部分不携带方法学信息。此处仅测 A-E 耦合几何，非复现其计数增益（+8.00pp 未重测）。

## 3. 三条交叉主线

**主线一：监督信号从 token 转向 state / trajectory / outcome。** NSP 试图把监督从词元抬到世界状态；具身智能用 ROS2 技能图与真机结果代替模仿轨迹；可信 AI 用内部激活（DoM、"Going Badly"）代替行为分数；AI4S 用实验成败 outcome 代替文本相似度。共同点是把监督信号锚定在可验证的物理/实验量上。

**主线二：智能从"模型在环"转向"离线生成 + 验证闭环"。** GaP 让 agent 离线写控制程序、导出 ROS2（core=Graph-as-Policy；「真机无模型在环」本轮全文未核到逐字原句，此处作为范式特征而非 GaP 已证断言）；RoboSimStudio 从视频建仿真再生成程序；ACE-CaP-0 是"冻结代码、评测无 agent 在环"的极端形态（92.1% 真机，此点论文明确）。这条主线的价值在于把执行与验证解耦，让失败可回放、可回灌。

**主线三：评估从聚合指标转向局部失败审计。** Termination Lag 的"撤销正确 patch"、医疗 VLM 的"气胸召回为零"、WorkflowArena 的"无方差"、Agentic-OPD 的"遗忘被 best-checkpoint 掩盖"——都是聚合分数看不到的局部失败。共同出路是把评估拆到具体失败模式、给出方差或区间、审计掩盖机制。

## 4. 核心判断

六个方向无一方向错，错在把证据等级不同的成果并列。真正的方法论进步不是某个新模型或新分数，而是三个可复用的工程原则：**可验证的状态预测**（监督信号锚定物理/实验量）、**可审计的失败模式**（评估拆到局部、带方差/区间）、**离线生成 + 验证闭环**（执行与验证解耦）。掌握这三条，就能在叙事噪音中识别哪些成果是真正的进展。

## 5. 全文级深挖：四方向新证据（2026-11-20）

四方向各选两篇争议核心论文，从摘要级推进到全文级（HTML 下载 + 剥标签逐句核验），产物见各项目 `manuscript/fulltext-deepdive.md`。新增四个可复算结论：

**世界模型 / NSP（2505.14892 + 2606.30534）**：反证从"相关"加固到"机制"——`state tracking ... limited to pattern matching (without attention across state-action history) ... emerge from weak interaction of several next token heads`，且 `action information is also not moved`，被点名的 GPT-XL L22H20 / Pythia-1B L6H12 本身就是 next-token heads。Orca 的 Table 5 消融是对**自建三项损失** λ_obs/λ_evt/λ_vqa 的组合（全用 Text51.8/Image59.8/Action32.4/Avg48.0），**不是 next-token vs NSP 固定 backbone 对照**——"修辞三分"判断全文级坐实。

**智能体（2611.14960 + 2611.12799）**：翻案点——Termination Lag 的 oracle 是**离线重算**（逐 step 记录 patch 后用官方测试离线判对错，`evaluate each distinct patch offline`），因此"早停干预"不需要重跑 agent，E1 卡从"需 API+GPU"翻案为"卡在逐-step patch 轨迹底物"。Agentic-OPD 机制全解：HCN（Gain matrix/Scored pool/Scheduling）选教师、LAD 三层（problem/rollout/turn）定信任，Qwen3-4B base 25.7→GRPO 50.4→Agentic-OPD 55.6，最高 +7.4 分为作者自报。

**具身智能（2611.23855 + 2607.05369）**：口径纠错——RoboBuilder 的 66% 是 **sim-pass→real-pass 复现率**（`66% of simulated passes hold across all levels`），全文另有三个不同的 0.66 必须区分（Parts Jaccard 0.66 / AUC 0.66 p=0.014 / 穿越时间 Spearman 0.78 Pearson 0.57）。GaP 全文确认是 Graph-as-Policy（typed ROS dataflow + 行为树，可静态类型检查 + 显式失败恢复），不是单个 VLA。

**可信 AI（2609.19101 + 2611.14996）**：主体纠错——DoM 向量 `catching 3.1% more hacks in Kimi K3 but 7.9% fewer hacks in GLM 5.2`（**分属两个模型，不可合并成区间**）；GLM 5.2 在 DeepSWE 57.2% / SWE-bench 73% rollout 黑客。Going Badly 用 `1,774 narratives ... containing no hacking examples` 提取 v_bad 方向，`rises over the turns leading up to a hack`（run 内上升趋势而非固定阈值），因果 steering 适度减法减作弊、**过量减法反使 agent 看不见自身失败**。

### 5.1 八项可复算方法学诊断的统一判决表（收口）

八项诊断跨越五方向，但共享同一方法学骨架：**预注册判据 → 三臂/对照/解析计算 → selftest 反证注入（门必须能红）→ 落盘可复算证据 → 诚实标注边界**。统一列示如下，避免把不同口径的结论误并列：

| 诊断（项目/卡） | 装置 | 预注册判据 | 主结果 | 判决 | 口径边界 |
|---|---|---|---|---|---|
| NSP 三臂（worldmodel E1） | 合成线性动力，共享 backbone，头不同 | state 臂累积斜率最低 | state 斜率 0.197 非最低；绝对 mse@1000=0.0024 最低 | 判据**未过**，保留 secondary finding | 量化地板伪造低 slope；非论文复现 |
| 多投影（worldmodel E2） | 4 互补投影，参数量相等 68748 | multi 跨本体退化小于 single | 退化 3.03× vs 8.50×，3/3 seed | **h2_supported=true** | 单步预测，非 E1 长程口径；CF-WAM 代码未放 |
| DoM 探针（trustworthy E2） | Qwen2.5-7B/14B 真实权重，未见家族迁移 | Q1 未见 TPR≥0.8 + Q2 signal−shortcut≥0.2 | 7B Q1/Q2 勉强过；14B validator TPR=0、Q2=0.10 未过 | **混合/部分负** | 跨规模 hidden 3584 vs 5120 不可搬运；非论文跨族复现 |
| 终止延迟早停（agentic E1） | 纯 numpy 合成 patch 轨迹，三臂 | 撤销率归零且成功率不降，主导因子为 FPR | 校准撤销 3.05%，FPR=0 有效、FPR≥0.01 成功率崩 | **命题成立**（fpr_dominates=true） | 合成参数非实测；FPR/FNR 为扫描网格 |
| 工作流可判定性（agentic E2） | a-priori 非中心 t 功效 + 5000 次 MC | SESOI 不可得→报 MDE；难度交互应比主效应难 | 主效应 MDE=dz0.234、交互 d0.468(2×)、R=16→0.059 | **判不了即结论**（not_answerable_with_public_substrate） | MDE 非效应存在性；dz 无量纲、σ 未公开无法换分数点 |
| 1.9× 一致性（ai4science E2） | 公开数字算术自检 + 可识别性诊断 | headline 应可由公开分项同口径复现 | 均值2.142/中位2.05/几何2.112 均≠1.9；可行区间[1.999,2.400]不含1.9 | **not_identifiable_with_public_data** | 不声称 1.9 错，只说不可复现；偏离方向无配对不可识别 |
| 解释力-能量几何（fm E2） | 各向同性零模型 d=128/r=4 + Beta 解析 | 89.82% vs 9.52% 分离是否为低秩几何通病 | E≈r/d=3.125%（理论中位2.63%）、corr(A,E)=0.011、A_null99th=0.220 对表AROMA0.219 | **GEOMETRY_GENERIC**（C1–C4 全真） | 非 AROMA 复现（代码/数据不可得）；h 各向同性为假设，结论对各向异性亦成立；+8.00pp 计数增益未重测 |
| 92.1% 分层复算（embodied E2） | ACE-CaP-0 Table 1 逐场景聚合数字，8 场景各 n=30 | 92.1% 是否为少数场景高均值、长尾是否稳定 | 均衡设计（加权==未加权 0.9208）、留一极差 2.38pp、最低场景 83.3% Wilson CI[66.4%,92.7%] 覆盖整体、χ²(7)=7.259 p=0.402、方差比 1.04 | **STRATIFIED_RECOMPUTE_PASS**（C1–C4 全真） | 非真机/物理复现，只用表1聚合数字、无逐trial序列（场景间方差可算、场景内不可）；n=30 长尾「不显著」≠「证明稳定」；GR00T2 是另一实验 |

八者共同的可推广教训：**判据必须自带反证**（否则量化地板、C 错位、模板捷径、撤销假象、功效函数 nan、判据方向反转、慢跑对不上表都会制造假绿）；结论的适用范围由装置口径而非模型规模决定。特别是后几项证明：**「底物不可得」不必等于「无结论」**——功效分析能把「测不了」定量成「要什么条件才测得了」，算术自检能把「不可审计」定量成「公开数字本身就对不上」，几何诊断能把「方法悖论」还原成「r≪d 的低维算术」，分层复算能把一个「真机实验」的均值问题拆成公开数字就能判的分布问题（92.1% 不是被少数场景拉动）。这与 §4 核心判断一致——三条工程原则（可验证的状态预测、可审计的失败模式、离线生成 + 验证闭环）正是从这些诊断里长出来的。

## 6. 局限与引用纪律

- **代码/数据/权重可得性**：CF-WAM、AROMA、Termination Lag、Agentic-OPD 四篇全文均已核验，无一公开代码数据（CF-WAM 承诺接收后释放）。因此涉及这些方法的数值都是作者自报，不可独立复现。
- **算力约束**：本机 RTX 3060 Laptop（6GB）CUDA 可用，但被 ollama llama-server 常驻 4.6GB，不腾显存不可行。本轮新增结果分三类：①借用云 AMD Radeon Cloud（gfx1100，48GiB 共享）跑的合成三臂诊断 + 多投影诊断（§2.1）+ 可信 AI 激活探针诊断（Qwen2.5-7B/14B-base，§2.1）；②终止延迟早停诊断（§2.2）用纯 numpy 合成轨迹、无需 GPU；③工作流作者效应可判定性（§2.2）、1.9× 一致性（§2.4）、解释力-能量几何（§2.6）与 ACE-CaP-0 92.1% 分层复算（§5.1，纯标准库）纯解析计算+本机、无需云。八者均为方法学诊断而非论文数值复现；原定需 VLM 的 fm E2 已由零模型几何诊断绕开（不拉 Llama-3.2-11B-Vision、不做不忠实代理），不再阻塞。embodied E2 的判据（92.1% 的分布/长尾）已用 ACE-CaP-0 公开 Table 1 分层复算完成——design 卡自写的「GR00T2 权重未放」指向的是另一个更宏大的闭环实验（用 GR00T2/WAM 做离线生成+真机验证），与本卡判据不是同一件事；那个闭环实验仍等论文方释放 artifact，但不阻塞本卡结项。至此 12 张实验卡按各自判据全部结项。
- **证据分级不是真伪判断**：ANNOUNCEMENT_ONLY 只表示当前无法独立复算，不等于成果不存在。
- **引用纪律**：所有 arXiv 编号均经 abs 页"号-题一致"验号（37 篇全部在 `synthesis/evidence/arxiv-verification.json` 判 VERIFIED）；所有百分数可从对应 `evidence/` 文件重算；厂商口径（MCP 下载量、1.9×、GeneScientist/NanoTitan 数字）明确标注为自报。全文级深挖新增的引用（2505.14892/2606.30534/2611.14960/2611.12799/2611.23855/2607.05369/2609.19101/2611.14996）均已在该清单内。
- **口径纠错（本轮）**：RoboBuilder 的 66% 是复现率、不是相关系数；2609.19101 的 3.1%/−7.9% 分属 Kimi K3 与 GLM 5.2 两个模型；任何 0.66 引用必须带尺名（复现率 vs Jaccard vs AUC vs 相关系数）。
- **不建议的读法**：把 9.3×（独立可复算成本性能比）与 1.9×（自报时间比）并列排序；把 66% sim2real 与 92.1% 真机成功率同表；把 LongLLaDA/MPPA/RangeSWA 的 PPL 数值直接比较。

## 参考文献（节选，均验号）

世界模型：1803.10122 · 2410.04940 · 2510.26583 · 2606.30534 · 2609.34414 · 2505.14892
智能体：2611.12856 · 2611.12799 · 2611.14960 · 2611.12835 · 2503.13657
具身：2607.05369 · 2610.18835 · 2611.11941 · 2611.23855 · 2611.16872
AI4S：Nature 647:390–396 (doi:10.1038/s41586-025-09640-5) · OpenAI Science at the Frontier 2026-11-16
可信：2611.14975 · 2502.17424 · 2412.04984 · 2609.19101 · 2611.14996
基础模型：2506.14429 · 2611.15029 · 2610.42084 · 2505.22954 · 2506.13131 · 2611.24395
