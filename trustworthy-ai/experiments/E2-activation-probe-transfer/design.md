# E2-activation-probe-transfer: DoM 激活探针跨模型族迁移

> 项目：`trustworthy-ai` ｜ 假设：`H2` ｜ 建卡：2026-11-19 ｜ 状态：completed（真实模型方法学诊断，混合/部分负）

## 设计

原设计（GLM5.2→Qwen/GPT-OSS 跨族迁移）需要论文用的推理模型（Kimi K3/GLM5.2/Qwen3.8Max），本机/云均不可得。改为**可证伪的方法学诊断**：

1. DoM 探针严格取自 arXiv:2609.19101 §3.1 式(1)：v_hack = E_pos(x_t) − E_neg(x_t)，分数 s_t = <v_hack, x_t>，阈值按 1% FPR 在测试 honest 分数上校准
2. 训练只用 test-suite tampering 家族 + 5 个 honest 模板，测试在完全未参与的 validator/scorefile/acquire 家族（=论文"泛化到未预见作弊行为"的类比）
3. 在 Qwen2.5-7B-base 与 14B-base 两个真实模型上各做一次模型内探针

## 判据（预注册，写死在 analyze_dom_probe.py）

- Q1 未见家族泛化：三未见家族 TPR@1%FPR 均值 ≥ 0.8
- Q2 信号超出捷径：真实 unseen AUC − max(置换标签对照 AUC) ≥ 0.2
- Q3 跨模型方向搬运：仅当 hidden_size 相同才可能；不同即 NOT_ANSWERABLE

## 依赖与阻塞

论文级跨族需 GLM5.2/Kimi K3/Qwen3.8Max + DeepSWE 真实 rollout 与 judge 标注，本机/云均不可得——本实验只验证"同族不同规模内的跨条件泛化"，不验证论文跨族主张。

## 日志

### 2026-11-21
- 脚本 `analyses/dom_probe_transfer.py`（math selftest PASS：cos_align_e0=0.9945 / fpr_match_ok / auc_signal=1.0 / auc_null=0.4991 / dim_mismatch_detected；置换标签反证内置）；`analyses/analyze_dom_probe.py`（selftest 4/4 PASS，含 TPR 低/置换接近/维度不同三类反证）
- full 7B（AMD gfx1100，24 条/条件）：train AUC 1.0、unseen AUC 1.0、三未见家族 TPR 1.0/1.0/1.0、置换对照 {0.45,0.60,0.758}、signal−shortcut=0.242 → Q1/Q2 过线（Q2 勉强）
- full 14B（需 free VRAM ≥30GiB，2 次尝试后成功）：train AUC 1.0、unseen AUC 0.95、validator TPR=**0.0**/scorefile 1.0/acquire 1.0、置换对照 {0.5,0.6,0.85}、signal−shortcut=0.10 → Q1/Q2 未过
- 跨模型：hidden 3584 vs 5120，方向不可搬运，Q3=NOT_ANSWERABLE
- logit lens 读出乱码 token（非论文的 cheating/illicit）
- 产物：`evidence/dom-full-7b.json`、`evidence/dom-full-14b.json`、`evidence/dom-analysis.json`、`evidence/2026-11-21-dom-probe-result.md`
- 诚实边界：非论文跨族复现；14B validator 家族迁移失败与 0.85 置换对照揭示捷径成分；honest_invest 模板 FPR 偏高（0.083，含命令词）；合成语料≠真实 rollout；logit lens 语义缺失与论文不一致
