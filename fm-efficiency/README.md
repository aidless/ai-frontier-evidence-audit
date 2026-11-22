# 基础模型与工程效率：可复现的净增益

> 项目 id：`fm-efficiency` ｜ 领域：`ai/foundation-models` ｜ 建立：2026-11-19 ｜ 状态：scoping
> 免训练上下文扩展、冻结模型控制、RSI 与系统协同

## 核心研究问题

基础模型工程效率提升（免训练上下文扩展、冻结模型控制、递归自我改进、系统协同）中，哪些是可复现的净增益，哪些只是 benchmark 自报？

## 假设（待检验，非结论）

- **H1** 免训练上下文扩展对 diffusion LLM 有效，但收益随任务长度与分布外程度衰减（PPL 19.51→3.12 属特定设置）。
- **H2** 冻结 VLM 的表示控制（AROMA）收益集中在 exact-count 类任务，泛化到其他任务与更大模型尚未证实。
- **H3** RSI 在代码/基础设施优化上已有可测增益，但「长期稳定的递归提升」未被证明。

## 已核验证据基线

| 结论 / 事实 | 证据 | 等级 |
|---|---|---|
| LongLLaDA：training-free、NTK-RoPE 外推；AAAI 2026 accepted | arXiv:2506.14429 | 预印本/已接收·已核实 |
| MPPA：LLaDA-8B 在 8192 tokens PPL 19.51→3.12，passkey 100% | arXiv:2611.15029 | 预印本·已核实 |
| RangeSWA：连续 diffusion LM 的 training-free 长度外推（摘要未给数值） | arXiv:2610.42084 | 预印本·已核实 |
| AROMA：冻结 Llama-3.2-11B-Vision；89.82% 敏感度仅占 9.52% 激活能量；MEA 81.25% vs 15.18% | arXiv:2611.15041 (2026-11-11) | 预印本·独立验号 |
| Absolute Zero：零外部数据自博弈，自提 code-reasoning 任务 | arXiv:2505.03335 | 预印本·已核实 |
| Darwin Gödel Machine：SWE-bench 20.0%→50.0%，Polyglot 14.2%→30.7% | arXiv:2505.22954 | 预印本·已核实 |
| AlphaEvolve：4×4 复矩阵乘法降到 48 次标量乘法，56 年来首次超 Strassen | arXiv:2506.13131 | 预印本·已核实 |
| RSIBench-Infra：20 任务、最多 32 加速器；66.2% 任务 >1.10× validated speedup | arXiv:2611.24395 | 预印本·已核实 |
| GUARD：冻结 base model、只编辑 harness，带 non-regression guarantee | arXiv:2611.23476 | 预印本·已核实 |

> 完整核验记录与「未核实/存疑」清单见 [`evidence/2026-11-19-baseline.md`](evidence/2026-11-19-baseline.md)。
> 纪律：arXiv 编号必须 abs 页「号-题-作者」一致才算核实；官方通稿数字只作事件证据，不作性能证据。

## 研究缺口（本项目的切入点）

- RangeSWA 摘要无数值结果，数字层面未核实。
- AROMA 为单作者预印本，场景集中于 exact-count。
- RSI 长期稳定性未证；清华榜单原文亦写「仍待验证」。
- **云端**零可用 GPU（AGENTS.md §17 表内通道），但**本机有 RTX 3060 Laptop 6GB**（2026-11-20 实测 torch CUDA 可用、bf16 19.76 TFLOPS；被 ollama 常驻占用后仅剩 ~1GB）。复现前现测 `nvidia-smi` 与 `ssh -o ConnectTimeout=5`，别照抄"零可用"旧结论。

## 可执行的第一步

1. 在固定模型上复现 MPPA 与 AROMA 的关键数字，记录硬件、超参与随机种子。
2. 建立 RSI 增益回归基线：同任务、同预算下自我改进 vs 单次生成的差值。
3. 先现测云端 GPU 通道（ssh ConnectTimeout=5），再决定复现实验落点。

## 目录约定

`experiments/<id>/` 实验（design.md / log.md / code/ / results/）｜`literature/` 文献与 references.bib｜
`artifacts/<name>/v<N>/` 版本化工件｜`analyses/` 可复用分析脚本｜`figures/` 成稿图表｜
`manuscript/` 论文草稿｜`reviews/<id>/` 评审报告｜`evidence/` 证据核验记录。
`research-manifest.json` 是机器与模型共用的真相源，状态变更走工具或按 schema 追加，不手改结构。
