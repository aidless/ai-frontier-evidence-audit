# E1 终止延迟早停干预：合成轨迹方法学诊断结果

日期：2026-11-21
性质：**合成轨迹方法学诊断**，非 Termination Lag (arXiv:2611.14960) 数值复现，非 SWE-bench 真跑。
脚本：`agentic-systems/analyses/termination_lag_intervention.py`（`--selftest` / `--out`）
原始数据：`agentic-systems/evidence/termination-lag-full.json`

## 结论先行

早停干预（首次判「patch 已正确」即强制退出）**不是免费午餐**：它的成败由一个廉价正确性检测器的**假阳性率（FPR）**决定，而非召回率。在合成装置中，只有 FPR=0 的检测器同时做到「撤销率归零 + 成功率不降」；FPR 一旦到 1%，成功率从 96.95% 掉到 94.35%，到 30% 时掉到 62.94%——**省下的步数越多，成功率塌得越狠**。这把论文的离线 oracle 结论（「首正确 patch 处停，消除中位 35–60% 步骤且保留所有原本解决任务」）转化为一个在线部署的硬约束：你必须有近乎零假阳性的正确性判据，否则早停会把还没修好的 run 提前掐死。

## 可证伪命题（预注册）

> 在线早停干预的有效性取决于检测器 FPR，而非召回率（1−FNR）。

三臂对照（同一合成轨迹、同 backbone 无关）：
- **baseline**：跑到终点。
- **oracle**：在 ground-truth 首个正确 patch 处停（离线预知，上界）。
- **detector**：检测器首次报 correct 时停（在线可部署，FPR/FNR 可调）。

## 装置与校准

- 20,000 条合成 patch 轨迹，步数 8–40；首次正确位置以 q=0.6 落在首步（对齐论文「38–82% 成功 run 首次源码编辑即正确」），否则均匀。
- 首正确后每步以 p_undo=0.012 被改坏，坏后以 p_refix=0.30 修回。
- **校准锚点**：baseline 撤销率 3.05%，落在论文观察的 1–8% 区间——装置量级对齐，非结论。
- 撤销时刻真实状态用 undo/refix 标志逐帧重建（修正了初版「t≥k 恒真」的结构假象；修正后撤销率随 FNR 上升而上升，符合预期）。

## 结果（mean，n=20,000）

| 臂 | 成功率 | 撤销率 | 平均步数 | 省步 |
|---|---|---|---|---|
| baseline | 0.9695 | 0.0305 | 23.89 | — |
| oracle（上界） | 1.0000 | 0.0000 | 7.08 | 70.4% |
| detector, FPR=0, FNR=0 | 1.0000 | 0.0000 | 7.08 | 70.4% |
| detector, FPR=0.01, FNR=0 | 0.9435 | 0.0000 | 6.47 | 73.0% |
| detector, FPR=0.05, FNR=0 | 0.7996 | 0.0000 | 4.74 | 80.2% |
| detector, FPR=0.30, FNR=0 | 0.6294 | 0.0000 | 1.86 | 92.2% |

判据（预注册）：撤销率较 baseline 降 ≥3pp 且 ≤2%，且成功率不降 >1pp。
- 有效点全部且仅在 **FPR=0**（FNR ∈ {0, 0.10, 0.30}）；FNR=0.60 时撤销 0.0009 略超阈值失效（漏报→晚停→遇 undo）。
- FPR ≥0.01 全部失效——撤销率虽降到 0，但成功率崩盘。
- `fpr_dominates = True`：有效点 FPR 全为 0，失效点 FPR ∈ {0, 0.01, 0.05, 0.1, 0.3}。

反证（selftest PASS）：① detector 恒报 correct（FPR=1,FNR=0）→ 判 false；② 恒不报（FPR=0,FNR=1）→ 判 false；③ 完美（FPR=0,FNR=0）→ 判 true。

## 机制解读

假阳性提前掐断未修好的 run → 成功率直接受损；假阴性只让停止变晚 → 多走几步、撤销率略升，但不伤成功率。所以「正确性检测器」的设计焦点应是**宁可漏报不可误报**（高阈值、要求强证据），这与异常检测里 FPR 优先的常识一致。论文的 oracle 之所以能「保留所有原本解决任务」，正因为它是离线精确重算、没有假阳性——在线把这个 oracle 逼近成检测器，全部代价集中在 FPR 上。

## 诚实边界

1. **合成轨迹，不是 SWE-bench 真跑**；q_first / p_undo / p_refix 是校准参数，不是实测。
2. 未构建真实的「廉价正确性检测器」；FPR/FNR 是扫的参数网格，不是某个具体 judge 的实测可靠性。要落地，须先测一个真实检测器（如测试子集执行、LLM judge）的 FPR 曲线。
3. 撤销率归零在 FPR>0 时也发生，但那是「提前停在没有 undo 机会的早期」造成的，伴随成功率崩盘——不能当作干预成功。
4. 与已完成的 E1 oracle 离线诊断（逐-step patch 离线重算）口径不同：此处是在线检测器视角，回答「能不能部署」，不是「离线 oracle 有多强」。

## 复现

```bash
python3 agentic-systems/analyses/termination_lag_intervention.py --selftest
python3 agentic-systems/analyses/termination_lag_intervention.py \
  --out agentic-systems/evidence/termination-lag-full.json
```
