# fm-efficiency E2：AROMA「解释力 89.82% vs 能量 9.52%」分离的几何普适性诊断

> 卡：`E2-interpretation-vs-energy`（假设 H2）｜ 日期：2026-11-21 ｜ 性质：**结构几何诊断，不是 AROMA 复现**
> 判据（预注册于 design.md）：「89.82% vs 9.52% 的分离是否为所有冻结方向方法的通病」

## 结论

**GEOMETRY_GENERIC（几何通病，而非 AROMA 的方法缺陷）。**

在一个与 AROMA 无关的零模型下——灵敏度梯度 g_i 与激活 h 都是各向同性高斯，维度 d=128、秩 r=4（取 AROMA 的 L18H13 actuator 头维度）——"用 top-r 灵敏度子空间解释第二矩"与"该子空间只承载极小激活能量"这两件事**结构性必然同时发生**，且两者之间没有耦合：

| 量 | 零模型（无结构随机） | AROMA 报告值 | 判读 |
|---|---|---|---|
| 解释力 A（top-4 灵敏度第二矩占比） | mean 0.209，99th **0.220** | 0.8982 | AROMA 远高于随机，但随机本身也有 0.22 的底 |
| 能量占比 E（ρ² 中位数） | **0.027**（理论 Beta 中位 0.0263） | 0.0952 | 两者同量级；E 低不是 AROMA 独有 |
| r/d | **0.03125** | — | E≈r/d 的上限解释：4 维塞进 128 维 |
| corr(A, E) | **0.0107**（独立） | — | 高解释力与低能量之间没有任何权衡关系 |

关键点是：**E 低是维度的算术后果，A 高是灵敏度方向集中的后果，二者互不约束**。任何冻结方向方法只要在两处成立——(a) 灵敏度集中在少数方向，(b) 激活能量均匀铺在 d 维——就会同时得到"A 很高、E 很低"。所以 89.82% vs 9.52% 这个"悖论"不是某个方法的病灶，是 r≪d 时的几何常态。AROMA 自己的 isotropic null（99th≈0.219）只排除了"A 是随机产生"，**没有排除"E 低是所有低秩方法共有"**——后者才是本卡要问的"通病"。

## 装置

- 脚本：`fm-efficiency/analyses/sensitivity_energy_geometry.py`（`--selftest` / `--run --reps N --out path`）
- 零模型：`S = (1/N) Σ g_i g_iᵀ`，`U_r` = S 的 top-r 特征向量，`A = Σ_{j≤r} λ_j / Σ_j λ_j`，`E = ‖P_U h‖² / ‖h‖²`，P_U = U_r U_rᵀ
- **E 的分布是解析的**：h/‖h‖ 在球面上均匀，P_U 是秩 r 正交投影 ⇒ ρ² ~ Beta(r/2, (d−r)/2)，与 U 的选取无关（故与 g 独立 ⇒ corr(A,E)=0 结构性成立）。`run_null` 直接抽 Beta，不做逐样本 eigh。
- A 的 null 99th **强烈依赖灵敏度估计样本数 N**（见下表）——AROMA 报的 0.219 对应 N≈40，故取 `n_grad=40`。

  | N（灵敏度样本数） | 16 | 20 | 24 | 32 | **40** | 48 | 64 | 96 | 128 |
  |---|---|---|---|---|---|---|---|---|---|
  | null 99th | 0.3985 | 0.3414 | 0.3038 | 0.2528 | **0.2199** | 0.1976 | 0.1676 | 0.1359 | 0.1179 |

- full：`python3 fm-efficiency/analyses/sensitivity_energy_geometry.py --run --reps 4000 --out fm-efficiency/evidence/sensitivity-energy-geometry.json`（本机 CPU，约 10 s，exit 0）

## 验证（门必须能失败）

`--selftest` 5 条注入反证，全部按预期翻转：B1 满秩 r=d ⇒ C3/C4 false；B2 E=0.95 ⇒ C3 false；B3 r=d/2 ⇒ r/d 与理论中位同步跟随；B4 正常参数 ⇒ C1–C4 全 true；B5 A/E 独立 ⇒ |corr|≈0（实测 −0.00011）。结果 PASS。

## 诚实边界

1. **不是 AROMA 复现**。代码可达性全负：GitHub repo 搜索 0 命中、全文无 release/data-availability 声明、ModelScope `meta-llama/Llama-3.2-11B-Vision-Instruct` 返回 `record not found`、Proc-Count 数据不可得。本诊断不调用任何 AROMA 代码或数据。
2. **h 各向同性是假设**。AROMA 的 E=9.52% > r/d=3.125%，说明真实 h 能量比各向同性更集中。但 C3 的结论（低秩子空间承载小能量份额）对各向异性同样成立——E<0.5 是低维几何事实，不因方法而异；各向异性只会抬高 E，不会推翻"A-E 分离是常态"。
3. **测的是耦合几何，不是计数准确率**。AROMA 的 +8.00pp held-out 增益是独立声称，本诊断不重测、不背书。
4. **C1 借用了 AROMA 自己的 null 值**（0.219）做对表；MC 在有偏的 N=40 下独立恢复同阶 0.22046（差 0.0015）。若两者差 >0.05 则 C1 判红。

## 复现

```bash
python3 fm-efficiency/analyses/sensitivity_energy_geometry.py --selftest
python3 fm-efficiency/analyses/sensitivity_energy_geometry.py --run --reps 4000 \
  --out fm-efficiency/evidence/sensitivity-energy-geometry.json
```
