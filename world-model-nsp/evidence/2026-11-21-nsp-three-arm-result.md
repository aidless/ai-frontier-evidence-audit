# E1 三臂对照：合成数据方法学诊断结果（2026-11-21）

> 项目：`world-model-nsp` ｜ 实验：`E1-nsp-three-arm` ｜ 执行：2026-11-21 AMD Radeon Cloud (gfx1100)
> 定位：**合成线性动力系统上的方法学诊断，不是复现任何论文数值**。回答的只是"监督目标的抽象层级是否影响长时程预测稳定性"。

## 一句话结论

**原判据（state 臂误差累积斜率最低）未通过；但 state 臂的绝对长程误差最低（比 frame 好 4×、比 token 好 15×）。**
token 臂斜率看似最低是量化地板假象，不能当作"next-token 更稳"的证据。这是对原假设的**部分支持 + 判据需修正**，不是干净证实。

## 检验的命题（H1 收窄版）

源自 arXiv:2505.14892 全文反证（state tracking 是 next-token heads 的分布式副产物，action 信息未可靠传到最终 token）。收窄后的可证伪命题：

> 同一 backbone / 数据 / 算力预算下，action-conditioned NSP（预测潜状态 s）相对 next-token / next-frame，长时程自回归 rollout 误差累积斜率更低。

三臂唯一差别 = 输出头/监督目标：
- `token`：frame 每维 16 级离散 id + 交叉熵；rollout 反量化
- `frame`：frame 向量 + MSE；rollout 直接喂回
- `state`：潜状态 s + MSE；rollout 经 C 映射回 frame

公平性控制：三臂共享同一动力学 (A,B,C)、同一训练/评测轨迹、同一 action 未来序列；评测统一在 frame 空间 MSE。

## 装置修复链（三轮 smoke 暴露并修掉的缺陷）

| 轮次 | 暴露的问题 | 修复 | 证据 |
|---|---|---|---|
| smoke v1 | horizon 写死 '1000' 致 KeyError（H=120） | `max_h=max(h for h in KS_GRID if h<=H)` | 报错 `KeyError: '1000'` |
| smoke v2 | **公平性 bug**：eval 用独立 A/B/C，state 臂用训练 C 映射回 frame 时 C 错位 | `make_eval(cfg,A,B,C)` 接收训练动力学 | action 消融比 0.996→144.7 |
| smoke v2 | 量化饱和：MSE 全饱和在 8+（frame 方差才~2） | `sigma_s=sqrt((act_scale²+0.02²)/(1-ρ²))` 归一化 frame std≈1 | MSE 8+→0.001–0.13 |
| smoke v3 | 两点 slope 不稳；ρ=0.75 强稳定系统误差被衰减吃掉无区分度 | 密 horizon 网格 KS_GRID（10 点）+ ρ=0.95 临界稳定 | 曲线见 full 结果 |

脚本：`world-model-nsp/analyses/nsp_three_arm.py`；分析：`world-model-nsp/analyses/analyze_nsp_full.py`（含 `--selftest`，注入假数据验证判定逻辑能红）。

## 正式结果（full，3 seeds，ρ=0.95，H=1000，212s）

聚合（mean±std，跨 3 seeds）：

| 臂 | slope (log10 MSE / log10 h) | mse@1000 | 参数量 |
|---|---|---|---|
| token | **0.1355 ± 0.0062** | 0.036540 ± 0.002365 | 230,112 |
| frame | 0.4039 ± 0.0242 | 0.009659 ± 0.001680 | 160,272 |
| state | 0.1971 ± 0.0560 | **0.002406 ± 0.000770** | 156,780 |

seed 级 slope：token 0.1278/0.1431/0.1357；frame 0.438/0.3892/0.3846；state 0.2727/0.1794/0.1391（state 方差大，1/3 seed 降到低于 token 附近）。
action 消融比（打乱未来 action 后 state 臂远端 MSE 的放大倍数）：mean **101.9**（seed 52.6/120.9/132.1）——模型确实在用 action 信息。

派生分析（`nsp-full-analysis.json`，seed0 稠密曲线）：

| 臂 | mse@step1 | mse@1000 | 相对增长倍数 |
|---|---|---|---|
| token | 0.015016 | 0.034022 | 2.27× |
| frame | 0.000767 | 0.011516 | 15.01× |
| state | 0.000639 | 0.003471 | 5.43× |

state 单步精度是 token 的 1/23（量化损失），state 远端绝对误差是 frame 的 0.249×、token 的 0.066×。

## 判读（诚实边界）

1. **原判据失败**：slope 最低的是 token（0.136），不是 state（0.197）。但这不能解读为"next-token 最稳"——token 起点就撞在量化地板（step1 MSE 0.015，是 state 的 23 倍），它的误差曲线从一开始就在天花板附近，log-log 斜率被压平。这是**地板效应**，不是优势。
2. **绝对误差口径 state 全胜**：无论单步还是 1000 步，state 臂绝对 MSE 都最低。若研究目标是"预测得准"，state 胜出；若严格按预注册判据"累积斜率"，state 未过。
3. **增长倍数是折中口径**：frame 增长最快（15×，起点低但发散快），state 居中（5.4×），token 最慢（2.3×，因地板）。这一口径下 state 也不是最稳。
4. **state 的 slope 方差大**（±0.056），3 个 seed 里 1 个降到 0.139（接近 token）。临界稳定系统的长程斜率对 seed 敏感，3 seeds 只够给方向性结论，不足以宣称统计显著。
5. **装置本身是合成线性系统 + Transformer**，与真实视频/机器人动力学的非线性、部分可观测不可同日而语。它只支持"目标抽象层级影响长程稳定性"的**机制性存在**，不支持任何论文数值复现或 SOTA 比较。

## 对 E1 卡判决的影响

原判据未过 → H1（收窄版）**不被本实验证实**。但发现了一个更有信息量的口径（绝对长程误差 state 显著最低）+ 一个必须记录的陷阱（量化地板伪造低 slope）。
建议判决从 `METHOD_UNBLOCKED_SUBSTRATE_PENDING` 更新为 `COMPLETED_NEGATIVE_ON_PRESPECIFIED_CRITERION`（判据按预注册失败），并保留"绝对误差口径支持 state"作为 secondary finding。

## 复现命令

```bash
# 云端（AMD Radeon Cloud，/opt/venv/bin/python，torch2.9.1+hip）
scp -P <ssh-port> world-model-nsp/analyses/nsp_three_arm.py root@HOST:/tmp/nsp_three_arm.py
ssh -p <ssh-port> root@HOST '/opt/venv/bin/python /tmp/nsp_three_arm.py --mode full --out /tmp/nsp_full.json'
scp root@HOST:/tmp/nsp_full.json world-model-nsp/evidence/nsp-full-result.json
python3 world-model-nsp/analyses/analyze_nsp_full.py --selftest
python3 world-model-nsp/analyses/analyze_nsp_full.py --out world-model-nsp/evidence/nsp-full-analysis.json
```

原始结果：`world-model-nsp/evidence/nsp-full-result.json`（5057B）；派生分析：`world-model-nsp/evidence/nsp-full-analysis.json`。smoke v3 曲线存档于云端 `/tmp/nsp_smoke_v3.json`（临时，未入库）。
