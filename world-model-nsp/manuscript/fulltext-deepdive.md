# 世界模型 / NSP：两篇核心全文的深度核验（2026-11-20）

**范围**：本轮从摘要级推进到全文级，核验 arXiv:2505.14892（反证）与 arXiv:2606.30534（Orca）两篇。两篇均已在 `synthesis/evidence/arxiv-verification.json` 验号（VERIFIED）。全文 HTML 存 `.tmp/fulltext/<id>.html`（临时目录，不入库），关键句逐字摘录如下，可复算。

## 1. 2505.14892：反证从"相关"加固到"机制"

此前只有摘要级一句 "state tracking ... emerges from distributed interactions of next-token heads"。全文给出三条更硬的机制证据：

1. **机制判定（逐字）**：`evidence of state tracking is most-likely limited to pattern matching (without attention across state-action history) in the DFA domain; the behavior seems to emerge from weak interaction of several next token heads.`
   → 不是"显式状态机"，是"弱交互的 next-token heads 的 pattern matching"，且明确 `without attention across state-action history`。
2. **具体 head 定位（逐字）**：`GPT-XL Layer 22 Head 20 and Pythia-1B Layer 6 Head 12 are both next-token heads.`
   → 被当作"状态跟踪证据"的 head，本身就是 next-token head。（旧笔记另记 Pythia-1B L10/11/12/14 为激活补丁定位；本次全文核到 L6H12 这一明确表述，两者不冲突：补丁可涉及多层，此处点名的是典型 head。）
3. **动作信息未传播（逐字）**：`the relevant modified state information is not reliably propagated to the final token ... action information is also not moved—indicating that joint state-action reasoning is not preserved.`
   → 最关键一条：连动作信息都没被送到最终 token，"联合 state-action 推理"没有在残差流里被 preserved。

**规模递降数据（摘要级已核，全文复用）**：GPT-2 XL 低复杂度约 70%、状态/盒 >5 或 >10 时降到 <30%；Pythia-1B 在状态>10 且转移<30 的 DFA 上不超 50%。

**对 H1 的判决**：全文把反证推到机制层面——如果 NSP 的收益真来自显式状态预测目标，它应当在这类需要跨历史 attention 的困难 DFA 上超过纯 next-token；但现有机制证据显示状态/动作信息根本没被可靠编码进最终 token。因此 H1 必须收窄为**动作条件化增益**（action conditioning gain），而非**目标函数替换增益**（objective replacement gain）。这一收窄现在有全文级支撑，不再只靠摘要。

## 2. 2606.30534 Orca："修辞三分"的全文级确认

**逐字立场句**：`Rather than optimizing isolated next-token, next-frame, or next-action prediction, we are centered on Next-State-Prediction modeling...`
**规模**：125K 小时视频 + 160M 事件标注。
**自报性能**：`Orca outperforms similar-sized specialized baselines`（作者自报，无独立复现）。

**关键核验（Table 5 消融）**：全文消融是对**自建目标函数的三种损失项**做组合——λ_obs（观测）、λ_evt（事件）、λ_vqa（VQA）：

- 三项全用：Text 51.8 / Image 59.8 / Action 32.4 / Avg 48.0
- 去掉 λ_evt：Image 列记为 `-`

这意味着：Orca 的 "next-token / next-frame / next-action vs next-state" 是**目标函数的修辞对照**（作者用语言把旧目标并列出来强调自己不同），**不是固定 backbone 下的 A/B 消融**。Table 5 真正测的是"三类辅助损失的贡献"，与"目标函数替换增益"是两个不同的问题。→ 此前"修辞三分"的判断获得全文级确认。

## 3. 对本方向实验卡判决的影响

- `E1-nsp-three-arm`：仍 BLOCKED（需 GPU）。但全文级证据进一步**提高了这张卡的科学价值**：50 篇摘要 + 2 篇全文都找不到"固定 backbone、next-token vs next-state 三臂"的先例，且反证已有机制层面支撑。这是真空白，不是没查到。
- `E2-multiview-ablation`：仍 BLOCKED（CF-WAM 代码承诺"接收后释放"，截至 2026-11-20 未放出）。

## 4. 诚实边界

- 两篇的负面结论是"现有证据不支持强主张"，不是"已证明强主张为假"——三臂对照本身还没被跑过。
- 全文 HTML 存临时目录 `.tmp/`，不入库；关键句已在本文逐字引用，可独立复核。
- 所有量化数字来自论文正文，非本工作复算的实验值。
