# E2-tool-selfreport-audit: 自我报告效率 vs 配对实测的差距设计

> 项目：`ai4science` ｜ 假设：`H3` ｜ 建卡：2026-11-19 ｜ 状态：completed（内部一致性诊断；非配对实测）

## 设计

1. 定义同任务、同课题组、有/无工具的配对方案
2. 指标：完成时间、返工率、结果质量（非自我报告）

## 判据

判据：自我报告 1.9× 与配对实测的偏离方向与幅度

## 依赖与阻塞

需要人类受试者与工具访问；本阶段只完成 pre-registration。
**2026-11-21 结论**：配对实测底物不可用；改对已公开的 1.9× 与 5 个分项做算术自检。结果=1.9 与公开分项在同口径平均下彻底不相容（5 项均值 2.142、中位数 2.05、几何均值 2.112 均≠1.9；隐含未公开 3 项均值 1.497<最低分项 1.76；可行均值区间 [1.999,2.400] 不含 1.9）。偏离方向/幅度因无配对无方差在数学上不可识别。见 evidence/2026-11-21-selfreport-1p9x-consistency.md。

## 日志

- 2026-11-21：内部一致性诊断完成。命令 `python3 ai4science/analyses/selfreport_1p9x_consistency.py --selftest`（PASS，注入反证验证门能红）与 `--mode full`（exit 0）。产物 `ai4science/evidence/selfreport-1p9x-consistency.json` + `ai4science/evidence/2026-11-21-selfreport-1p9x-consistency.md`。selftest 修 C3 判据方向（headline 落在可行区间外才是「不相容」的正证据）。
