# E1-termination-lag-intervention: 首次正确 patch 后强制退出的 scaffold 干预

> 项目：`agentic-systems` ｜ 假设：`H2` ｜ 建卡：2026-11-19 ｜ 状态：completed（2026-11-21，合成轨迹方法学诊断，非 SWE-bench 真跑）

## 设计

1. 复现 Termination Lag 的 baseline：5 模型 / 2 框架 / 3 个 SWE-bench
2. 干预组：检测首次源码编辑即正确 → 强制终止

## 判据

判据：1–8% 的「撤销正确 patch」率是否归零，且成功率不下降

## 依赖与阻塞

需要可运行的 coding-agent 环境与 SWE-bench 数据；本地只允许亚分钟级 smoke，全量实验上云。

## 日志

- 2026-11-21：逐-step patch 轨迹底物作者仍未放出，改用**等价合成轨迹方法学诊断**（非论文数值复现、非 GPU 需求）。
  - 脚本 `analyses/termination_lag_intervention.py`；`--selftest` PASS（三类反证：恒报/恒不报判 false、完美检测器判 true）。
  - `--out evidence/termination-lag-full.json`：n=20000，校准 baseline 撤销率 3.05%（落论文 1–8% 区间）、oracle 上界省步 70.4% 且撤销归零；在线 detector 仅 FPR=0 有效，FPR≥0.01 成功率 96.95%→94.35%→62.94% 崩盘，`fpr_dominates=true`。
  - 装置修正：撤销时刻按 undo/refix 逐帧重建，去掉「t≥k 恒真」假象。
  - 报告 `evidence/2026-11-21-termination-lag-intervention.md`；verdict：命题成立（有效性由 FPR 主导而非召回率），H2 更新为 partial_support_synthetic。
  - 边界：合成轨迹参数非实测、FPR/FNR 为扫描网格而非真实检测器标定。
