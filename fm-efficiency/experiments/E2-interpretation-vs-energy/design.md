# E2-interpretation-vs-energy: AROMA 悖论的普适性测试

> 项目：`fm-efficiency` ｜ 假设：`H2` ｜ 建卡：2026-11-19 ｜ 状态：completed（结构几何诊断，非 AROMA 复现）

## 设计

1. 对冻结方向方法批量测「解释力」与「激活能量占比」
2. 2026-11-21 调整：代码可达性探测全负（GitHub repo 搜索 0、全文无 release 声明、ModelScope Llama-3.2-VL `record not found`、Proc-Count 不可得），无法对真实模型批量测。改为**预注册结构几何诊断**：在与 AROMA 无关的零模型下，判断「高解释力 89.82% + 低能量 9.52%」的分离是不是 r≪d 低秩子空间的几何必然，而非某方法缺陷。

## 判据

判据：89.82% vs 9.52% 的分离是否为所有冻结方向方法的通病

## 依赖与阻塞

单作者预印本，方法代码可用性未核；先做代码可达性探测。

2026-11-21 结论：代码可达性探测为负 → 不改做不忠实代理（此前 sensitivity_energy_gap.py 因构造不符已删除），改做零模型几何诊断。结果 GEOMETRY_GENERIC：C1 null 正确（A_null 99th=0.220 对表 AROMA 0.219）、C2 耦合缺席（corr(A,E)=0.011）、C3 低维几何（E≈r/d=3.125%）、C4 通病成立。分离是低秩几何常态，非 AROMA 方法特有缺陷。计数增益 +8.00pp 未重测。见 `fm-efficiency/evidence/2026-11-21-sensitivity-energy-geometry.md`。

## 日志

- 2026-11-21：`python3 fm-efficiency/analyses/sensitivity_energy_geometry.py --selftest` → PASS（B1–B5 五条注入反证）。
- 2026-11-21：`python3 fm-efficiency/analyses/sensitivity_energy_geometry.py --run --reps 4000 --out fm-efficiency/evidence/sensitivity-energy-geometry.json` → exit 0，GEOMETRY_GENERIC，C1–C4 全 true。
- 产物：`fm-efficiency/evidence/sensitivity-energy-geometry.json`、`fm-efficiency/evidence/2026-11-21-sensitivity-energy-geometry.md`。
