# Next-State Prediction 作为世界模型目标函数：谱系、反证与实验空白

**状态**：scoping 完成；证据截止 2026-11-20。`E1-nsp-three-arm` / `E2-multiview-ablation` 因本机 GPU 被 ollama 占用而 BLOCKED。
**可复算产物**：`evidence/2026-11-19-nsp-census.md`（arXiv API 实测 totalResults=53，取回 50）。

## 摘要
"Next-State Prediction (NSP)"不是某个单点发明，而是一条从 2018 延续至今的演化链。我们核验了这条链上的关键节点，并用 arXiv API 对摘要级文献做了一次普查，得到两个结论：（1）把 NSP 当作"统一目标函数取代 next-token"的强主张，在取回的 50 篇摘要中没有固定 backbone 的三臂对照支持；（2）已有的 mechanistically 研究反而提示状态跟踪是 next-token heads 的分布式副产物，因此该主张应收窄为"动作条件化增益"。这构成一个真实、可检验但需 GPU 的实验空白。

## 1. 谱系（全部经 arXiv abs 页验号）
- Ha & Schmidhuber《World Models》arXiv:1803.10122 (2018)：世界模型范式起点。
- Saanum et al. arXiv:2410.04940 (2024-10)：标题首次显式出现 "next state prediction"。
- Emu3.5 arXiv:2510.26583 (2025-10-30, BAAI)：>10T tokens，DiDA 约 20× 加速；但训练目标仍是统一 next-token，正文无字面 "next-state prediction"。
- Orca arXiv:2606.30534 (2026-06-29)：首次显式 "centered on Next-State-Prediction modeling"；125K 小时视频 + 160M 事件标注。
- CF-WAM arXiv:2609.34414 (2026-09-28)：逐字 "Predicting the next state is a core paradigm of World Models"；动态多投影监督；RoboCasa-GR1 82.50% / LIBERO-Plus 82.65% / 真机 84.00%。代码数据承诺"接收后释放"，截至 2026-11-20 未放出。

## 2. 反证：从"目标替换"到"动作条件化"
arXiv:2505.14892《Scaling Laws for State Dynamics in LLMs》逐字指出："state tracking in LLMs emerges from distributed interactions of next-token heads rather than explicit symbolic computation." 其 GPT-2 XL 在状态复杂度低时约 70% 准确率，状态/盒 >5 或 >10 时降到 <30%；Pythia-1B 在状态>10 且转移<30 的 DFA 上不超 50%；激活补丁定位 GPT-2 XL L22H20、Pythia-1B L10/11/12/14，且 action 信息未可靠路由到最终 token。

这意味着：若 NSP 的增益真来自"显式状态预测目标"，它应在上述困难 DFA 上超越纯 next-token；而现有证据显示状态信息根本没被可靠编码——增益更可能来自动作条件化本身。H1 因此收窄为**动作条件化增益**，而非目标函数替换增益。

## 3. 实验空白
取回的 50 篇摘要中，无固定 backbone 下的 next-token / next-state / 多视图三臂对照先例。E1 三臂设计有真实空白，但最小可行 smoke 需加载 Qwen3-0.6B bf16（约 1.2GB），而本机 RTX 3060 Laptop（6GB）被 ollama llama-server（pid <pid-a>）常驻 4.6GB，仅剩约 1GB → OOM。解锁条件：临时释放 ollama 显存或申请云 GPU。

## 4. 诚实边界
本手稿是证据综述 + 实验设计，不含新训练结果。所有百分数来自上列论文的摘要/正文，均可经 arXiv abs/html 页复算；未放出代码的方法其数值为作者自报，不可独立复现。

## 参考文献（节选，均验号）
Ha & Schmidhuber 1803.10122 · Saanum 2410.04940 · Emu3.5 2510.26583 · Orca 2606.30534 · CF-WAM 2609.34414 · Scaling Laws for State Dynamics 2505.14892 · V-JEPA 2404.08471 · Genie 2402.15391 · Ctrl-World 2510.10125 · WorldArena 2602.08971
