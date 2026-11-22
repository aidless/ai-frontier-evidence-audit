# 六方向 AI 前沿研究 — 总索引与口径基准

> 建立时间：2026-11-20 ｜ 工作区根：`<repo-root>`（根名含字面反斜杠，**不要 cd**，用默认工作目录）
> 性质：证据驱动技术综述 + 可复算离线分析。所有数字可追溯到落盘证据或一手论文全文。
> 状态：12 张实验卡 12 completed / 0 blocked（2026-11-21 全部按各自判据结项；最后一张 embodied E2 用 ACE-CaP-0 公开 Table 1 做分层复算完成——92.1% 不是少数场景拉动、长尾在 n=30 功效下不显著偏离。此前 blocked 卡均经零/低底物方法学诊断绕开；口径不可比的 fm E1 判 CONFIRMED_NOT_ANSWERABLE 亦属结项）。

## 1. 六项目一览

| 项目 | 核心问题 | 实验卡 | 手稿 | 关键落盘证据 |
|---|---|---|---|---|
| [world-model-nsp](../world-model-nsp/) | NSP 是把监督从 token 抬到 world state，还是换词不改目标？ | E1 三臂（**completed 云 GPU 诊断，判据未过**）/ E2 多投影（**completed 云 GPU 合成诊断，h2_supported=true**） | [draft.md](../world-model-nsp/manuscript/draft.md) · [fulltext-deepdive.md](../world-model-nsp/manuscript/fulltext-deepdive.md) | [nsp-three-arm-result.md](../world-model-nsp/evidence/2026-11-21-nsp-three-arm-result.md) · [nsp-multiview-result.md](../world-model-nsp/evidence/2026-11-21-nsp-multiview-result.md) · [nsp-census.md](../world-model-nsp/evidence/2026-11-19-nsp-census.md)（arXiv 普查 totalResults=53 取回 50） |
| [agentic-systems](../agentic-systems/) | 多智能体协同的收益与失败模式如何量化？ | E1 终止延迟早停（**completed 合成轨迹诊断，FPR 主导命题成立**）/ E2 作者效应可判定性（**completed MDE 审计，非 WF Arena 复现**） | [draft.md](../agentic-systems/manuscript/draft.md) · [fulltext-deepdive.md](../agentic-systems/manuscript/fulltext-deepdive.md) | [termination-lag-intervention.md](../agentic-systems/evidence/2026-11-21-termination-lag-intervention.md)（FPR≥0.01 成功率崩盘） · [workflow-author-detectability.md](../agentic-systems/evidence/2026-11-21-workflow-author-detectability.md)（145 任务 MDE=dz0.234；难度交互 MDE 2×） · [availability.md](../agentic-systems/experiments/E2-workflow-author-effect/availability.md) |
| [embodied-physical-ai](../embodied-physical-ai/) | 离线写代码 + 真机验证能否稳定超越端到端 VLA？sim2real 缺口边界在哪？ | E1 sim2real 重算（**completed**）/ E2 92.1% 分层复算（**completed 零底物，非 GR00T2 闭环**） | [draft.md](../embodied-physical-ai/manuscript/draft.md) · [fulltext-deepdive.md](../embodied-physical-ai/manuscript/fulltext-deepdive.md) | [recompute_sim2real.py](../embodied-physical-ai/analyses/recompute_sim2real.py) → [sim2real-recompute.txt](../embodied-physical-ai/evidence/2026-11-19-sim2real-recompute.txt) · [acecap0_stratified_recompute.py](../embodied-physical-ai/analyses/acecap0_stratified_recompute.py) → [acecap0-stratified-recompute.md](../embodied-physical-ai/evidence/2026-11-21-acecap0-stratified-recompute.md) |
| [ai4science](../ai4science/) | AI4S 成果的证据等级如何分级？1.9× 效率提升能否审计？ | E1 证据分类学（**completed**）/ E2 自报口径审计（**completed 内部一致性诊断，偏离不可识别**） | [draft.md](../ai4science/manuscript/draft.md) | [build_evidence_tiers.py](../ai4science/analyses/build_evidence_tiers.py) → [tier-taxonomy.jsonl](../ai4science/evidence/tier-taxonomy.jsonl)(33 条) + [tier-report.md](../ai4science/evidence/2026-11-19-tier-report.md) · [selfreport-1p9x-consistency.md](../ai4science/evidence/2026-11-21-selfreport-1p9x-consistency.md)（1.9× 与公开 5 分项同口径平均不相容） |
| [trustworthy-ai](../trustworthy-ai/) | 聚合指标掩盖多少局部失败？内部激活能否提前抓 reward hacking？ | E1 掩盖点估计（**completed**）/ E2 激活探针（**completed 云 GPU 真实模型，混合负结果**） | [draft.md](../trustworthy-ai/manuscript/draft.md) · [fulltext-deepdive.md](../trustworthy-ai/manuscript/fulltext-deepdive.md) | [masking-point-estimate.txt](../trustworthy-ai/evidence/2026-11-19-masking-point-estimate.txt) · [dom-probe-result.md](../trustworthy-ai/evidence/2026-11-21-dom-probe-result.md)（7B 泛化过线/14B validator 家族 TPR=0，跨规模不可搬运） · [gpu-smoke.txt](../trustworthy-ai/evidence/2026-11-20-gpu-smoke.txt) |
| [fm-efficiency](../fm-efficiency/) | 免训练扩上下文路线能否同表比较？ | E1 CONFIRMED_NOT_ANSWERABLE / E2 能耗比（**completed 结构几何诊断，非 AROMA 复现**） | [draft.md](../fm-efficiency/manuscript/draft.md) | [comparability_matrix.py](../fm-efficiency/analyses/comparability_matrix.py) → [comparability-matrix.txt](../fm-efficiency/evidence/2026-11-19-comparability-matrix.txt) · [sensitivity-energy-geometry.md](../fm-efficiency/evidence/2026-11-21-sensitivity-energy-geometry.md)（89.82% vs 9.52% 分离是 r≪d 低秩几何常态 GEOMETRY_GENERIC） |

每个项目根有 `research-manifest.json`（schema2，真相源）、`README.md`、`literature/references.bib`、`evidence/2026-11-19-baseline.md`（逐条断言核验基线）。所有项目均已注册 `manuscript-draft` artifact 到 manifest。

## 2. 跨项目综合

- **合成综述**：[review.md](manuscript/review.md) 《从预测词到预测世界：2026 年 AI 研究前沿的证据审视》。核心判断：六方向无一错，错在把证据等级不同的成果并列。三条交叉主线：①监督信号 token→state/trajectory/outcome；②智能 模型在环→离线生成+验证闭环；③评估 聚合→局部失败审计。
- **投稿论文（TMLR/NeurIPS 格式方法学论文）**：[main.pdf](paper/main.pdf) 《Evidence, Not Enrollment: Eight Recomputable Methodological Diagnostics on 2026 AI Frontier Claims》（7 页，匿名双盲版）；源在 [paper/main.tex](paper/main.tex) + [paper/sections/](paper/sections/)（模块化 `\input` 组页），`tmlr.sty` 本地随附。论文把八项诊断收口成统一方法学骨架（预注册判据→对照→selftest 反证→落盘→口径边界），四个直接结论 + 四个「不可得即结论」。`research_audit` PASS（7 页正文、无身份泄露、无未解引用）；全部 arXiv 号经 37 篇验号账本核对。未投稿。
- **arXiv 验号账本**：[arxiv-verification.json](evidence/arxiv-verification.json) — 37 篇唯一号，API `id_list=` 三批解析，号-题一致 37/37，0 missing、0 rate-limit。
- **过程笔记**：[six-projects-execution.md](../notes/2026-11-19-six-projects-execution.md)（六项目执行+GPU 翻案）、[八篇全文级深挖.md](../notes/2026-11-20-八篇全文级深挖.md)、[四论文代码可达性.md](../notes/2026-11-20-四论文代码可达性.md)。

## 3. 两道 fail-closed 机器闸（当前均绿）

| 闸 | 命令 | 作用 | 当前状态 |
|---|---|---|---|
| 可复算证据汇总闸 | `python3 scripts/six_projects_evidence_gate.py` | 逐一重跑 5 份分析脚本并验其 selftest 断言；`--selftest-bad` 注入假脚本必须判红 | **5/5 PASS，exit=0** |
| arXiv 验号闸 | `python3 scripts/arxiv_verification_gate.py` | 手稿引用的每个 arXiv id 必须在验号账本里；`--selftest` / 注入 `9999.99999` 实测能红 | **37/37 PASS，exit=0** |

## 4. 口径基准（引用任何数字前先看这里）

这是本轮一致性审计固化的**强制口径**，散落在多份文档里，引用时必须带对应限定：

| 数字 | 正确口径 | 常见误读 |
|---|---|---|
| RoboBuilder **66%** | sim-pass→real-pass **复现率**（`66% of simulated passes hold across all levels`）。全文另有 Jaccard 0.66、AUC 0.66(p=0.014)、Spearman 0.78/Pearson 0.57，是不同量 | 当成相关系数 / 成功率 / AUC |
| DoM **3.1% / −7.9%** | 匹配 FPR 下相对 LLM monitor：**Kimi K3** 多抓 3.1%、**GLM 5.2** 少抓 7.9%（均 DeepSWE）。分属两个模型 | 合并成"同一模型的权衡区间" |
| OpenAI **1.9×** | 8 类科研活动**自我报告时间比**的均值（1,819 人 / 580,186 条消息 + 251 人调查），非实验测量 | 与 CRESt 的 9.3×（独立可复算成本性能比）同表排序 |
| 覆盖率 **2.69–4.79pp** | 医疗 VLM 单一 finding 全败的**聚合准确率代价**（prevalence-matched 平衡设计 f=1/7、p=1/2、r 取 MedGemma 0.377 / Lingshu 0.671）。修复后 acc 仅到 0.582，仍落后 MedGemma 0.698 | 当成"修复气胸即可追平" |
| GaP **"无模型在环"** | 全文只确认 core=Graph-as-Policy（typed ROS dataflow + 行为树）；"无模型在环"本轮**未核到逐字原句，已撤回**，仅作 H1 假设框架 | 当成 GaP 论文已证事实 |
| GR00T 2 **权重** | 官方承诺 12 月开放；截至 2026-11-20 GitHub `NVIDIA/Isaac-GR00T` 最新 release 仍 n1.7-release(2026-04-18)、tags 仅 n1.x | 以为权重已可下载 |
| 本机 **GPU** | RTX 3060 Laptop 6GB、torch CUDA 可用（2026-11-20 现测）；但 ollama llama-server(pid <pid-a>)常驻 4.6GB，空闲仅约 1GB → 多数模型加载 OOM。"云端通道零 GPU"≠"本机零 GPU" | 笼统写"无可用 GPU" |

## 5. 当前阻塞与解锁条件

| 阻塞类型 | 涉及实验卡 | 解锁条件 |
|---|---|---|
| 算力 + 底物（需 VLM/扩散 LLM，云上无对应权重） | fm E2（worldmodel E1/E2、trustworthy E2 借云 GPU 已于 2026-11-21 完成） | 需 AROMA 用 Llama-3.2-11B-Vision 一类 VLM + 扩散 LLM 权重；云实例仅有 Qwen2.5 base/Instruct，11-23 销毁 |
| ~~底物（代码/权重未公开）~~ | ~~embodied E2（GR00T2 权重）~~ — **已解除**：E2 判据用 ACE-CaP-0 公开 Table 1 分层复算完成，不需 GR00T2 | GR00T2/WAM 闭环是另一个实验（权重仍未放，最新 n1.7-release 2026-04-18），但不阻塞 E2 判据 |
| 口径不可比 | fm E1 | 已判定 CONFIRMED_NOT_ANSWERABLE；出路是固定 base 架构对照（LLaDA 离散 vs ELF 连续扩散） |

> 2026-11-21 底物不可得卡的处置：fm E2、agentic E2、ai4science E2、embodied E2 不再空等，改做**零底物方法学诊断**——fm E2 用零模型证明「高解释力+低能量占比」是 r≪d 的低秩几何常态（GEOMETRY_GENERIC，非 AROMA 方法缺陷）；agentic E2 用 a-priori 功效分析给出「多大的作者效应/多少重复评测才判得开」（MDE 0.234→重复 16 次降到 0.059）；ai4science E2 用公开数字算术自检证明 1.9× 不可复现且偏离方向不可识别；embodied E2 用 ACE-CaP-0 已发表 Table 1 分层复算证明 92.1% 是齐平结果而非少数场景拉动（留一极差 2.38pp、χ²(7) p=0.402、方差比 1.04）。四张卡均转 completed，结论写「geometry_generic / not_answerable / not_identifiable / stratified_recompute_pass」而非伪造正结果。至此 12 卡全部按各自判据结项。

## 6. 使用约定

- 真相源是各项目 `research-manifest.json` 与 `evidence/`；本索引只做导航与口径基准，不替代细节。
- 新增证据或数字变动后，重跑第 3 节两闸，并更新第 4 节口径基准表。
- 工作区纪律：研究性改动**只本地 commit、不 push**；`AGENTS.md` / `scripts/` 门脚本等共享文件不擅自改。
