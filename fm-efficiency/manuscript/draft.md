# 免训练扩展扩散语言模型上下文：三路线为何不可同表比较

**状态**：scoping 完成；证据截止 2026-11-20。`E1-context-extension-headtohead` 升为 CONFIRMED_NOT_ANSWERABLE，`E2-interpretation-vs-energy` 因 GPU 被占 BLOCKED。
**可复算产物**：`analyses/comparability_matrix.py` → `evidence/2026-11-19-comparability-matrix.txt`。

## 摘要
"无需重训即可扩展扩散 LLM 上下文窗口"是一个吸引人的主张，但 LongLLaDA、MPPA、RangeSWA 三条路线使用不同 base 架构、不同评测集、不同指标。我们逐篇取全文核验，证明三者两两 NOT_COMPARABLE，并给出唯一可推进的对照设计。结论：在当前公开数字下，任何"哪条路线更好"的单表排序都是伪比较。

## 1. 逐篇全文核验
- LongLLaDA arXiv:2506.14429 v3 (AAAI 2026)：方法 NTK-RoPE。**正文无 8192-token PPL 数值**——PPL 只在 Figure 1 曲线中，Table 1/2 是 LongBench/RULER/NIAH，"8k"是训练长度描述而非评测点。Base 未定为 LLaDA-8B 单一配置（文中含 Base/Instruct 及 LLaMA3-8B 对照）。
- MPPA arXiv:2611.15029：LLaDA-8B，8192-token PPL 19.51 → 3.12，passkey 100%（作者自报）。这是三者中唯一给出明确 8192-token PPL 数值的。
- RangeSWA arXiv:2610.42084：用 **ELF-B/M/L**（连续扩散语言模型，**非 LLaDA**）；Table 2 Gen.PPL@8192=153.12 (ELF-B)。

## 2. 可比性判定（机器可复算）
`comparable(a,b)` 当且仅当：同 base + 同评测集 + 共同指标 + 双方有数。三对结果全部 NOT_COMPARABLE：
- LongLLaDA vs MPPA：base 表述不同 + 评测集不同 + 无共同数值指标。
- LongLLaDA vs RangeSWA：base 不同（LLaDA vs ELF）+ 评测集不同。
- MPPA vs RangeSWA：base 不同（离散 vs 连续扩散）+ 指标不同（PPL vs Gen.PPL）。
`--selftest`：同配置判可比、改评测集判不可比，exit=0 通过。

## 3. 出路
唯一可推进的对照是固定 base 的架构对照：**LLaDA（离散扩散）vs ELF（连续扩散）**，在相同 context 下比 Gen.PPL + 重复率。这仍需 GPU（本机 RTX 3060 Laptop 被 ollama 占用）。

## 4. 诚实边界
CONFIRMED_NOT_ANSWERABLE 不是说"三路线无优劣"，而是说"用当前公开数字无法判定"。MPPA 的 19.51→3.12 是作者自报，未经独立复现；把它与 RangeSWA 的 Gen.PPL 并列会犯口径错误。

## 参考文献（均验号）
LongLLaDA 2506.14429 · MPPA 2611.15029 · RangeSWA 2610.42084 · AROMA 2611.15041（解释与能量，另文）
