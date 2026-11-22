# E2 前置：WorkflowArena 数据与代码可用性探测

> 项目：`agentic-systems` ｜ 假设：`H1`（工作流组织是可量化的性能决定因素）｜ 探测日：2026-11-19
> 判定：**BLOCKED — 底物不可得**（判定依据见下，非"没找到"，是"确实未发布"）

## 探测动作与原始观察

| 探测点 | 结果 |
|---|---|
| `arxiv.org/abs/2611.12856`（abs 页） | HTTP 200；标题/作者/提交日（2026-11-09）与预期一致；**无 Code/Data 外链** |
| `arxiv.org/html/2611.12856v1`（HTML 全文） | HTTP 200，67,479 字符；章节为 1 Introduction … 5 Conclusion + Acknowledgements + References，**无 Data/Code Availability 章节** |
| Acknowledgements 段 | 原文只有一句：`This project is funded and supported by Navers Lab, Einsia.AI.` —— 无仓库、无数据地址 |
| References 段 | 全部为文献引用，无自指仓库链接 |

## 从正文取到的两条自述限制（对 H1 是决定性的）

HTML 全文 Limitations 段落原文（逐字摘录）：

> "Each configuration is evaluated once per task, so differences between closely ranked configurations are reported without variance estimates."

> "Content and 3D deliverables are graded against task rubrics by an LLM judge, and agreement with human graders is not measured in this work."

这两句直接约束 H1 的可检验形式：

1. **无方差估计**：单次评测意味着「配置 A 比配置 B 高几个点」无法与噪声区分。H1 若表述为"工作流组织带来 X 个点的提升"，该 X 在当前底物上**不可判读**。
2. **无人类评分一致性**：rubric 由 LLM judge 打分且未测与人类的一致性，因此分数是"judge 偏好的度量"，不是"交付物质量的度量"。

## 判定与后续

- **BLOCKED（底物不可得）**：无法在本地或云端复跑 WorkflowArena，也无法取得 145 个任务与 9 个模型的原始记录。
- **H1 需改写为可判读形式**：从"工作流组织提升多少分"改为"同一任务重复评测下，不同工作流之间的差异是否超过单次评测的抖动"——这需要作者放出逐任务、多次重复的原始分数，属于外部依赖。
- **可立即做的替代**：用本仓库 `agentic-systems/experiments/E1` 的终止延迟数据（38–82% 首编辑即正确、1–8% 撤销正确 patch）自建一个**可本地复现**的编排对照：同一任务、同一执行者、只换"是否强制在首次正确编辑后终止"。这不需要 WorkflowArena 底物，且判据（成功率是否下降 / 撤销率是否归零）与 WorkflowArena 的关切同源。

## 复现命令

```bash
curl -s https://arxiv.org/abs/2611.12856 | grep -iE 'github|zenodo|huggingface|code|data' | head
curl -s https://arxiv.org/html/2611.12856v1 | grep -c 'Acknowledgements'
```
