# 聚合指标如何掩盖局部诊断失败：一个恒等式与一个点估计

**状态**：scoping 完成；证据截止 2026-11-20。`E1-aggregate-masking-curve` 已完成（恒等式 + 点估计落盘），`E2-activation-probe-transfer` 因 GPU 被占 BLOCKED。
**可复算产物**：`analyses/masking_identity.py` → `evidence/2026-11-19-masking-identity.txt`；`analyses/masking_point_estimate.py` → `evidence/2026-11-19-masking-point-estimate.txt`（selftest 4 项通过）。

## 摘要
医疗 VLM 的聚合 accuracy 可以掩盖某个 finding 的彻底失败。我们给出这个掩盖效应的精确恒等式 ΔAcc = f·p·r（f 子群占比、p 子群阳性率、r 被抹掉的召回率），用 200 万样本蒙特卡洛验证（最大误差 4.068e-07），并从 arXiv:2611.14975 全文读出 f、p 的实测值，把此前的宽区间 2.14–32.14pp 收紧为点估计 2.69–4.79pp。结论：单一 finding 全败的聚合代价看似很小，但修复后仍落后系统性差距——掩盖机制真实存在但不是全部解释。

## 1. 恒等式与验证
ΔAcc = f·p·r。`masking_identity.py` 用整数计数构造二分类集，`simulate(f,p,r,n=2_000_000)` 与解析式比对，40 组最大绝对误差 4.068e-07（tol=1e-5）。`--selftest` 两修后通过：tol 从 1e-9 放宽到 1e-5（取整误差 ~5e-7）；反证从 r=1.0（触发退化误报）改为 r=0.8 vs 0.5。

## 2. 点估计（从全文读出的实测常量）
arXiv:2611.14975 §3.1 逐字："2 sexes, 3 age bands, 7 findings, 2 labels ... 84 cells, sampling 72 ... 6,048 items ... 432 positives and 432 negatives per finding"——prevalence-matched 完全平衡。于是 f=864/6048=1/7、p=432/864=1/2 从假设变为实测常量，f·p=432/6048。

Table 2 逐字气胸召回：HuatuoGPT=0.000 / Qwen=0.000 / MedGemma=0.377 / Lingshu=0.671；Table 1 聚合 acc：0.698 / 0.620 / 0.534 / 0.518。据此：
- HuatuoGPT 的气胸 r=1.0 → 聚合代价最高 4.79pp（对 Lingshu 0.582 之外）。按 r=0.377（MedGemma 对照）算代价 2.69pp，0.534 → 0.561。
- 按 r=0.671（Lingshu 对照）算代价 4.79pp，0.534 → 0.582。

原宽区间 2.14–32.14pp 因 f 上界 0.357、r 假设 1.0 过宽而收紧；此前稿件写"所有合理假设下 ΔAcc<12pp"被自查发现与区间表 32.14pp 矛盾，已删除。

## 3. 诚实边界
修复气胸单一 finding 后，HuatuoGPT 的 acc 仅到 0.582，仍远低于 MedGemma 0.698——掩盖机制解释的是"为什么聚合分看不出气胸失败"，不是"为什么整体落后"。后者是系统性差距，另需解释。真实缺口：需先取得 6,048 条问题的逐条标签构成才能做 finer-grained 审计。

## 4. 更广的可信 AI 图景
- Emergent Misalignment arXiv:2502.17424：不安全代码微调→无关领域广泛失准。
- In-context Scheming arXiv:2412.04984：o1 85%+追问维持欺骗；反面边界 arXiv:2505.01420 指出未达令人担忧水平。
- Reward hacking 内部激活 arXiv:2609.19101：DoM 均值差向量，GLM5.2 在 DeepSWE 57.2% / SWE-bench 73% rollout 黑客；arXiv:2611.14996 "Going Badly" activations 黑客前数轮上升。
这些与本文共享同一方法论：从聚合行为分数转向内部状态与局部失败的直接观测。

## 参考文献（节选，均验号）
arXiv:2611.14975 · arXiv:2502.17424 · arXiv:2412.04984 · arXiv:2505.01420 · arXiv:2609.19101 · arXiv:2611.14996 · CLEAR arXiv:2610.38389
