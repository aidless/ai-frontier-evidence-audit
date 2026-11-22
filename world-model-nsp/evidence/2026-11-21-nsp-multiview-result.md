# E2 多投影监督合成诊断结果（2026-11-21）

> 项目：`world-model-nsp` ｜ 假设：H2 ｜ 实验卡：E2-multiview-ablation
> 性质：**合成数据方法学诊断**，非 CF-WAM（arXiv:2609.34414）数值复现。CF-WAM 代码/权重未公开（全文逐字 `Upon acceptance, we will release the code and data.`）。

## 结论先行

**H2 在合成类比下获支持（h2_supported=true）**：多投影监督相对单投影，(Q1) in-distribution 状态预测误差更低，(Q2) 对单一投影扰动更鲁棒，且跨 3 个 seed 一致。但这是信息互补带来的优势，不是免费午餐——两臂参数量相等（68748），multi 输入维度更大。

## 装置

- 潜状态 s（ds=12）通过 4 个互补投影观测：visual/semantic/geometric/interaction，每个投影只耦合 s 的一个子空间块（block=3），模拟不同传感模态看到状态的不同侧面。
- 任务：给定 K 步视图历史 + action 历史，预测下一潜状态 s_next（MSE）。
- 两臂：single（只用 visual 视图）vs multi（4 视图各自投影后 concat）。backbone 相同（TransformerEncoder dm=64/layers=2/heads=4），参数量相等。
- 跨本体类比：eval 时把 visual 投影矩阵换成扰动版本（幅度扰动 eps=0.3 + 正交旋转），其他投影不变；真 state 轨迹相同。
- 动力学：稳定线性 ρ=0.9，action_scale=1.0，view_noise=0.05。

## full 结果（3 seeds，AMD Radeon Graphics gfx1100，elapsed 18.91s）

| 臂 | in-dist MSE | cross-emb MSE | 退化比 (cross/in-dist) | 参数量 |
|---|---|---|---|---|
| single | 0.009137 | 0.077462 | 8.501 ± 0.434 | 68748 |
| multi | 0.008143 | 0.024613 | 3.029 ± 0.158 | 68748 |

per-seed 退化比：single 8.41 / 9.072 / 8.02；multi 2.815 / 3.192 / 3.079。

判决（`analyze_nsp_multiview.py`，selftest PASS）：
- Q1 multi_better_indist = true，误差比 multi/single = **0.8912**（multi 低约 11%）
- Q2 multi_more_robust = true，退化比差 = **5.472**（single 8.5× vs multi 3.0×）
- Q2 跨 seed 一致 = true（3/3 seed multi_deg < single_deg）
- params_equal = true
- **h2_supported = true**

## 诚实边界

1. **不是 CF-WAM 复现**：CF-WAM 的四投影是视觉/语义/几何/交互的真实机器人观测，这里是线性子空间互补的合成类比。不能把本结果写成"复现了 CF-WAM 的跨本体增益"。
2. **信息互补不免费**：multi 输入维度更大（4×view_dim vs 1×view_dim），虽然参数量相等，但 multi 看到了更多信息。Q1 的优势部分来自信息量而非纯归纳偏置。Q2（鲁棒性）才是更接近"跨本体泛化"的核心类比——multi 因冗余对单一投影失效更稳。
3. **smoke 与 full 的 Q2 不一致**：smoke（1 seed, steps=150）曾出现 q2_multi_more_robust=false（multi 退化比 2.39 > single 1.47），full（3 seeds, steps=800）翻转为 true。说明 smoke 欠训练时 multi 的冗余优势未显现，需充分训练才稳定。已如实记录，不以 full 覆盖 smoke 的矛盾。
4. **单步预测口径**：本实验用 teacher-forcing 单步预测 MSE，不是长程自回归 rollout（那是 E1 的口径）。两者不可直接比较。

## 复现命令

```bash
# 本地 selftest
python3 world-model-nsp/analyses/nsp_multiview.py --selftest
python3 world-model-nsp/analyses/analyze_nsp_multiview.py --selftest
# 云端（AMD gfx1100）
scp -o StrictHostKeyChecking=no -P <ssh-port> world-model-nsp/analyses/nsp_multiview.py root@<cloud-host>:/tmp/
ssh -o StrictHostKeyChecking=no -p <ssh-port> root@<cloud-host> '/opt/venv/bin/python /tmp/nsp_multiview.py --mode full --out /tmp/mv_full.json'
scp -o StrictHostKeyChecking=no -P <ssh-port> root@<cloud-host>:/tmp/mv_full.json world-model-nsp/evidence/nsp-multiview-full-result.json
python3 world-model-nsp/analyses/analyze_nsp_multiview.py --out world-model-nsp/evidence/nsp-multiview-analysis.json
```

产物：`nsp-multiview-full-result.json`（原始）、`nsp-multiview-analysis.json`（判决）。
