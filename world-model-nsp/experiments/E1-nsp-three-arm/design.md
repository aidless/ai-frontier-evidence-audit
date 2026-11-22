# E1-nsp-three-arm: 三臂对照：next-token / next-frame / action-conditioned NSP

> 项目：`world-model-nsp` ｜ 假设：`H1` ｜ 建卡：2026-11-19 ｜ 状态：completed（判据未过，见日志）
> 执行：2026-11-21 AMD Radeon Cloud (gfx1100)，合成数据方法学诊断

## 设计

1. 同一 backbone、同一数据切分、同一算力预算
2. 固定评测：长时程预测误差累积（horizon 10/100/1000）

## 判据

判据：action-conditioned NSP 的误差累积斜率显著低于两个基线

## 依赖与阻塞

本机 GPU 存在（RTX 3060 Laptop 6GB，2026-11-20 实测 CUDA 可用、bf16 19.76 TFLOPS），但被 ollama 常驻占用后仅剩 ~1GB，三臂对比需多 checkpoint 常驻不可行；云端 ecs-hz 无 GPU、hpccube 无 GPU。需先停 ollama 腾显存（须确认无其他会话依赖）或申请云 GPU。

## 日志

- 2026-11-21：在 AMD Radeon Cloud (gfx1100, torch2.9.1+hip) 跑通 full（3 seeds, ρ=0.95, H=1000, 212s）。
  - 命令：`/opt/venv/bin/python /tmp/nsp_three_arm.py --mode full --out /tmp/nsp_full.json`
  - 退出码 0；原始结果 `world-model-nsp/evidence/nsp-full-result.json`，分析 `world-model-nsp/evidence/nsp-full-analysis.json`，报告 `world-model-nsp/evidence/2026-11-21-nsp-three-arm-result.md`。
  - 判决：**原判据（state slope 最低）未过**——token slope 0.136 最低（量化地板假象），state 0.197、frame 0.404。但 state 绝对长程误差最低（mse@1000=0.0024，frame 的 0.249×、token 的 0.066×）。action 消融比 101.9 证明模型确用 action。
  - 装置修复链与诚实边界见报告。H1 不获证实；保留 secondary finding。
