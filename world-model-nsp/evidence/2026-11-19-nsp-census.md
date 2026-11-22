# E1 前置：NSP 三臂对照的文献普查（arXiv API 实测）

> 项目：`world-model-nsp` ｜ 假设：`H1`（同等参数/数据下，动作条件 NSP 的长时程误差累积低于 next-token / next-frame）
> 普查日：2026-11-19 ｜ 通道：`https://export.arxiv.org/api/query?search_query=abs:"next-state+prediction"`

## 普查口径

- API 返回 `totalResults=53`，取回 `max_results=50` 条（**3 条未取，不声称全覆盖**）。
- 筛查器：摘要同时命中 `next-token|token-level|autoregressive` 与 `next-state|next-frame|state prediction|frame prediction`，且含 `compar|outperform|baseline|ablation|versus|rather than`。
- 命中 3 条 → 逐条读摘要（见下）。其余 47 条摘要不同时含两类词，不构成"三臂对照"的候选。
- 年份分布（取回的 50 条）：2026=26、2025=11、2024=6、2023=1、2022=2、2021=2、2020=2。

## 三条命中：逐条判定

### 1. Orca (arXiv:2606.30534) — **修辞上的三分，不是受控消融**

摘要原文：

> "Rather than optimizing isolated next-token, next-frame, or next-action prediction, we are centered on Next-State-Prediction modeling..."

摘要同时说：

> "Orca outperforms similar-sized specialized baselines."

**判定**：明确把 next-token / next-frame / next-action 与 NSP 对立，但**对照对象是"相近规模的专用基线"，不是同一 backbone 下只改训练目标的三臂**。因此不能用来分离 NSP 的净增益。

### 2. Scaling Laws for State Dynamics in LLMs (arXiv:2505.14892) — **对 H1 的反向证据**

摘要原文（关键句）：

> "Our results suggest that state tracking in LLMs emerges from distributed interactions of next-token heads rather than explicit symbolic computation."

具体数字：GPT-2 XL 在低复杂度设置约 70% next-state 准确率，状态/盒子数超过 5 或 10 时降到 30% 以下；Pythia-1B 在状态 >10 且转移 <30 的 DFA 任务上不能超过 50%。激活补丁定位到 GPT-2 XL Layer 22 Head 20、Pythia-1B Layer 10/11/12/14。

**判定**：这篇是**已知唯一直接量化"next-token 模型内部如何做 next-state"的论文**。它表明状态跟踪是由 next-token heads 的分布交互实现的，且 action 信息**未被可靠路由到最终 token**——后者支持 H1 的"动作条件化是瓶颈"，前者削弱"NSP 必须替换 next-token"的强表述。**H1 应改写为"动作条件化增益"而非"目标函数替换增益"。**

### 3. Tabular Foundation Models as Training-Free World Models (arXiv:2611.11921) — **不同轴的比较**

摘要报告：TabFM 在同量级转移数据上几乎全面优于从零训练的 LSTM/MLP；但在完整数据上训练的模型多数系统仍显著更好；自回归 rollout 时短上下文迅速退化到平凡基线、长上下文显著改善且在一个 locomotion 任务上超过训练过的 LSTM；推理比 LSTM 慢约三个数量级。

**判定**：比较的是**预测器架构/上下文长度**，不是训练目标（token/frame/state）。对 H3（token 带宽约束）有直接价值：短上下文 rollout 退化的实测证据；对 H1 无直接判据。

## 结论

1. **H1 的原始形式在取回的 50 篇摘要中无直接先例**：没有一篇报告"固定 backbone、固定数据、只换 next-token / next-frame / 动作条件 NSP 三个目标"的长时程误差累积曲线。这是真正的空白，本项目 E1 有价值。
2. **H1 的表述必须收窄**：`2505.14892` 说明 next-token heads 本身就能实现状态跟踪，所以"替换目标函数"不是唯一路径；待测的是**动作条件化**是否带来独立增益。
3. **E1 仍受算力阻塞**：普查只完成了"空白是否存在"的证明；实际三臂实验需要 GPU，当前通道全部无卡（见交付总说明）。

## 复现命令

```bash
mkdir -p .tmp
curl -sS 'https://export.arxiv.org/api/query?search_query=abs:%22next-state+prediction%22&start=0&max_results=50' -o .tmp/nsp2.xml
grep -o '<opensearch:totalResults>[0-9]*' .tmp/nsp2.xml
```
