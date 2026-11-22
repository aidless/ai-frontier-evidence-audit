# AI for Science 的证据分级：从"AI 科学家"叙事到可复算判别

**状态**：scoping 完成；证据截止 2026-11-20。`E1-evidence-tier-taxonomy` 已完成（33 条分类落盘），`E2-tool-selfreport-audit` 已完成（1.9× 口径审计）。
**可复算产物**：`analyses/build_evidence_tiers.py` → `evidence/tier-taxonomy.jsonl`（33 条）+ `evidence/2026-11-19-tier-report.md`。

## 摘要
AI for Science 的叙事常把"自主发现系统发布"与"可复算的性能证据"混为一谈。我们提出一个三维证据分类学——A 载体等级、B 数字口径、C 可复算性——对 33 条已核实断言打分，并给出可机器判定的 composite 与 verdict。结论：33 条中 13 条只能判 ANNOUNCEMENT_ONLY，且分方向均值揭示"AI 科学家"类宣称的证据质量显著低于传统科研工具。

## 1. 方法
- A 载体：A1 期刊 / A2 预印本 / A3 机构通报 / A4 厂商通稿 / A5 媒体。
- B 数字口径：B1 独立可复算 / B2 自报+协议公开 / B3 自报+协议未公开 / B4 无数。
- C 可复算性：C1/C2/C3。
- `composite(a,b,c) = (wA·wB·wC)^(1/3)`（几何平均，任一维塌陷即整体下降）。
- `verdict(a,b) = "PERF_EVIDENCE" if a in {A1,A2} and b in {B1,B2} else "ANNOUNCEMENT_ONLY"`。
- `--selftest` 注入 A4+B3 必须判 ANNOUNCEMENT_ONLY、A1+B1 必须判 PERF_EVIDENCE，exit=0 通过。

## 2. 结果（全部可复算）
载体分布 A1=2 / A2=24 / A3=2 / A4=5；数字口径 B1=3 / B2=17 / B3=13；判定 PERF_EVIDENCE=20 / ANNOUNCEMENT_ONLY=13。
分方向 composite 均值：agent=0.5881、ai4science=0.4314、embodied=0.5411、fm=0.5097、trust=0.661、worldmodel=0.5024。

对照：MIT CRESt (Nature 647:390–396, doi:10.1038/s41586-025-09640-5) 判 A1+B1+C2 / composite 0.8193 / PERF_EVIDENCE——3 个月 900+ 配方、3500 次测试、八元催化剂空间 SOTA、成本专用性能 9.3×。而 GeneScientist (A3+B3+C3 / 0.2507) 与 NanoTitan Ultra (A4+B3+C3 / 0.2241) 均判 ANNOUNCEMENT_ONLY——发布是真实的，但无 arXiv/期刊论文、数字仅官方口径。

## 3. 1.9× 效率提升的口径审计
OpenAI《Science at the Frontier: How scientists use ChatGPT》(2026-11-16)：1,819 名科学家 / 580,186 条消息 + 251 人调查。**1.9× = 8 类科研活动自我报告时间比的均值，非实验测量**；分项代码 2.83× / 阅读 2.21× / 分析 2.05× / 构思 1.86× / 写作 1.76×；98% 认为加速。与 CRESt 的 9.3× 不可同表——后者是独立可复算的成本性能比，前者是自报时间比。

## 4. 诚实边界
分类学评的是"证据质量"，不是"成果真伪"：ANNOUNCEMENT_ONLY 不等于成果不存在，只等于当前无法独立复算。三维权重是设计选择，非从数据拟合，因此 composite 只用于排序，不作绝对门槛。

## 参考文献（节选）
CRESt Nature 647:390–396 doi:10.1038/s41586-025-09640-5 · OpenAI Science at the Frontier 2026-11-16 · GeneScientist 2025-07-30 · NanoTitan Ultra 2026-07-16 · A-Lab Nature Chem Eng 2024-02
