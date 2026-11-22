# AI4S / 六方向成果证据等级分布（E1 输出）

> 生成：`python3 analyses/build_evidence_tiers.py` ｜ 记录数：33 ｜ 全部分数是脚本由三维权重算出的，非手写

## 总量

| 维度 | 分布 |
|---|---|
| 载体等级 A | A1=2 / A2=24 / A3=2 / A4=5 |
| 数字口径 B | B1=3 / B2=17 / B3=13 |
| 引用判定 | ANNOUNCEMENT_ONLY=13 / PERF_EVIDENCE=20 |

## 分方向

| 方向 | 记录数 | 平均 composite | 可作性能证据 |
|---|---|---|---|
| agent | 5 | 0.5881 | 3/5 |
| ai4science | 6 | 0.4314 | 2/6 |
| embodied | 5 | 0.5411 | 3/5 |
| fm | 6 | 0.5097 | 4/6 |
| trust | 3 | 0.661 | 3/3 |
| worldmodel | 8 | 0.5024 | 5/8 |

## 逐条

| id | 成果 | A | B | C | composite | 引用判定 |
|---|---|---|---|---|---|---|
| `crest2025` | MIT CRESt 自主催化剂发现 | A1 | B1 | C2 | 0.8193 | PERF_EVIDENCE |
| `alab2024` | 自驱动催化实验 Pareto 前沿 | A1 | B1 | C2 | 0.8193 | PERF_EVIDENCE |
| `genescientist2025` | GeneScientist 生物育种自主发现 | A3 | B3 | C3 | 0.2507 | ANNOUNCEMENT_ONLY |
| `nanotitan2026` | NanoTitan Ultra 新材料模拟器 | A4 | B3 | C3 | 0.2241 | ANNOUNCEMENT_ONLY |
| `openai2026science` | OpenAI《Science at the Frontier》 | A3 | B3 | C3 | 0.2507 | ANNOUNCEMENT_ONLY |
| `kosmos2025` | FutureHouse Kosmos | A4 | B3 | C3 | 0.2241 | ANNOUNCEMENT_ONLY |
| `cfwam2026` | CF-WAM 动态多投影 NSP | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `orca2026` | Orca 世界基础模型 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `emu35_2025` | Emu3.5 原生多模态世界学习者 | A2 | B3 | C2 | 0.4983 | ANNOUNCEMENT_ONLY |
| `vjepa2_2025` | V-JEPA 2 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `ctrlworld2025` | Ctrl-World 策略评测器 | A2 | B2 | C3 | 0.4286 | PERF_EVIDENCE |
| `worldarena2026` | WorldArena 世界模型基准 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `rtfm2025` | World Labs RTFM | A4 | B3 | C3 | 0.2241 | ANNOUNCEMENT_ONLY |
| `genie3_2025` | Genie 3 | A4 | B3 | C3 | 0.2241 | ANNOUNCEMENT_ONLY |
| `terminationlag2026` | Termination Lag | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `epog2026` | e-PoG 评估侧部分可观测博弈 | A2 | B3 | C2 | 0.4983 | ANNOUNCEMENT_ONLY |
| `opd2026` | Agentic-OPD 遗忘修复 | A2 | B3 | C1 | 0.6082 | ANNOUNCEMENT_ONLY |
| `workflowarena2026` | WorkflowArena 工作流编排基准 | A2 | B2 | C3 | 0.4286 | PERF_EVIDENCE |
| `mast2025` | MAST 多智能体失败分类学 | A2 | B1 | C2 | 0.7444 | PERF_EVIDENCE |
| `gap2026` | GaP 技能图程序合成 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `groot2_2026` | GR00T 2 World-Action Model | A4 | B3 | C3 | 0.2241 | ANNOUNCEMENT_ONLY |
| `flipanything2026` | Flip Anything | A2 | B3 | C2 | 0.4983 | ANNOUNCEMENT_ONLY |
| `acecap2026` | ACE-CaP-0 离线代码闭环 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `robobuilder2026` | RoboBuilder sim2real 复现 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `dom2026` | DoM 奖励黑客激活探针 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `medvlm2026` | 医疗 VLM 隐藏失败审计 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `em2025` | Emergent Misalignment | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `aroma2026` | AROMA 冻结方向多模态控制 | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `mppa2026` | MPPA 扩散 LLM 免训练扩上下文 | A2 | B3 | C3 | 0.3232 | ANNOUNCEMENT_ONLY |
| `longllada2025` | LongLLaDA | A2 | B3 | C3 | 0.3232 | ANNOUNCEMENT_ONLY |
| `dgm2025` | Darwin Gödel Machine | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |
| `alphaevolve2025` | AlphaEvolve | A2 | B2 | C3 | 0.4286 | PERF_EVIDENCE |
| `rsibench2026` | RSIBench-Infra | A2 | B2 | C2 | 0.661 | PERF_EVIDENCE |

## 结论

- 13/33 条只能写成「宣布/声称」，不得写成「证明/达到」——这批是引用风险最高的。
- 7 条载体为机构通报或厂商通稿，其中 7 条同时无性能数字口径（B3），即「发布事件可信、性能不可引」。
- 载体等级 A 与数字口径 B 的联合分布解释了原综述的并列失真：Nature 正刊(B1) 与厂商通稿(B3) 出现在同一段落时，读者会默认它们等权。
