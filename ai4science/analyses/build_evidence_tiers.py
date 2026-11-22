#!/usr/bin/env python3
"""
ai4science/E1 — AI4S 成果证据等级分类学（三维标注 + 可失败门）

三维：
  A 载体等级   A1 同行评审期刊/顶会 | A2 预印本(方法+数字) | A3 机构通报(无论文) | A4 厂商通稿 | A5 媒体二手
  B 数字口径   B1 独立可复算 | B2 作者自报+协议公开 | B3 作者自报+协议未公开 | B4 无性能数字
  C 可复算性   C1 数据与代码公开 | C2 部分公开 | C3 未公开

引用门（fail-closed）：
  只有 (A1|A2) 且 B1|B2 的记录，才允许在稿件中作为**性能证据**引用；
  其余一律只能写成"宣布/声称"，写"证明/达到"即为违规。

用法：
  python3 build_evidence_tiers.py            # 生成 jsonl + 报告
  python3 build_evidence_tiers.py --selftest # 注入违规样本，必须 exit 1
"""
import json, os, sys, argparse
from collections import Counter

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "evidence")

# ---------------------------------------------------------------- 记录
# 仅收录本工作区已验号/已取一手载体的条目；不含任何凭记忆补的项。
RECORDS = [
    # id, 成果, 方向, A, B, C, 载体, 关键数字, 备注
    ("crest2025", "MIT CRESt 自主催化剂发现", "ai4science", "A1", "B1", "C2",
     "Nature 647:390-396, doi:10.1038/s41586-025-09640-5", "3个月900+配方/3500次测试；成本专用性能9.3×",
     "本项目证据等级最高的一条"),
    ("alab2024", "自驱动催化实验 Pareto 前沿", "ai4science", "A1", "B1", "C2",
     "Nature Chemical Engineering (2024-02)", "Pareto 前沿推进", "自驱动实验室前序证据"),
    ("genescientist2025", "GeneScientist 生物育种自主发现", "ai4science", "A3", "B3", "C3",
     "机构通报 2025-07-30", "30万条假设-实验-结论链；官方称数十个新基因", "无 arXiv/期刊"),
    ("nanotitan2026", "NanoTitan Ultra 新材料模拟器", "ai4science", "A4", "B3", "C3",
     "厂商通稿 2026-07-16", "成本降超90%", "无论文、无独立 benchmark"),
    ("openai2026science", "OpenAI《Science at the Frontier》", "ai4science", "A3", "B3", "C3",
     "OpenAI 报告 2026-11-16", "1819 名科学家/580,186 条消息；1.9× 自我报告均值", "非实验测量；分项 2.83×~1.76×"),
    ("kosmos2025", "FutureHouse Kosmos", "ai4science", "A4", "B3", "C3",
     "厂商口径 2025-11", "未核数字", "仅记存在"),
    ("cfwam2026", "CF-WAM 动态多投影 NSP", "worldmodel", "A2", "B2", "C2",
     "arXiv:2609.34414 (2026-09-28)", "RoboCasa-GR1 82.50%/LIBERO-Plus 82.65%/真实84.00%",
     "主会话独立验号"),
    ("orca2026", "Orca 世界基础模型", "worldmodel", "A2", "B2", "C2",
     "arXiv:2606.30534 (2026-06-29)", "125K 小时视频+160M 事件标注", ""),
    ("emu35_2025", "Emu3.5 原生多模态世界学习者", "worldmodel", "A2", "B3", "C2",
     "arXiv:2510.26583 (2025-10-30)", ">10T token；DiDA 约20× 加速", "训练目标仍是统一 next-token"),
    ("vjepa2_2025", "V-JEPA 2", "worldmodel", "A2", "B2", "C2",
     "arXiv:2506.09985", ">1M 小时视频；<62h Droid 零样本控 Franka", ""),
    ("ctrlworld2025", "Ctrl-World 策略评测器", "worldmodel", "A2", "B2", "C3",
     "arXiv:2510.10125", "与真机 Pearson 0.986（对照 Cosmos 0.483）", ""),
    ("worldarena2026", "WorldArena 世界模型基准", "worldmodel", "A2", "B2", "C2",
     "arXiv:2602.08971", "16指标/6子维度/14模型", "感知-效用差距"),
    ("rtfm2025", "World Labs RTFM", "worldmodel", "A4", "B3", "C3",
     "官方博客 2025-10-16", "4K@60fps 需 >100K tokens/s；1h 需 >100M context", "厂商推导，非测量"),
    ("genie3_2025", "Genie 3", "worldmodel", "A4", "B3", "C3",
     "DeepMind 官方博客 2025-08-05", "24fps/720p，一致性数分钟", "无同行评审"),
    ("terminationlag2026", "Termination Lag", "agent", "A2", "B2", "C2",
     "arXiv:2611.14960 (2026-11-11)", "38–82% 首编辑即正确；多余步骤中位 35–60%；1–8% 撤销正确 patch", ""),
    ("epog2026", "e-PoG 评估侧部分可观测博弈", "agent", "A2", "B3", "C2",
     "arXiv:2611.12835 (2026-11-09)", "欺骗缓解+26.0%；成功率最高+39.8%", "两项均为自报，未独立复现"),
    ("opd2026", "Agentic-OPD 遗忘修复", "agent", "A2", "B3", "C1",
     "arXiv:2611.12799", "最高+7.4分；4B 学生超过 GPT-5.6 为自述", "无朴素集成配对对照"),
    ("workflowarena2026", "WorkflowArena 工作流编排基准", "agent", "A2", "B2", "C3",
     "arXiv:2611.12856 (2026-11-09)", "145任务/8域/9模型/14400s 预算", "机构署名仅摘要级"),
    ("mast2025", "MAST 多智能体失败分类学", "agent", "A2", "B1", "C2",
     "arXiv:2503.13657", "1600+轨迹/7框架/κ=0.88/14失败模式", ""),
    ("gap2026", "GaP 技能图程序合成", "embodied", "A2", "B2", "C2",
     "arXiv:2607.05369 (CoRL 2026 Spotlight)", "真机无模型在环", ""),
    ("groot2_2026", "GR00T 2 World-Action Model", "embodied", "A4", "B3", "C3",
     "NVIDIA 官方 2026-11-09", "零样本40%；5演示+30min微调→95%", "权重未放出，协议未公开"),
    ("flipanything2026", "Flip Anything", "embodied", "A2", "B3", "C2",
     "arXiv:2611.11941", "24.7%→95.0%", "论文自选任务"),
    ("acecap2026", "ACE-CaP-0 离线代码闭环", "embodied", "A2", "B2", "C2",
     "arXiv:2611.16872", "221/240=92.1% 真机", "冻结代码、无 agent 在环"),
    ("robobuilder2026", "RoboBuilder sim2real 复现", "embodied", "A2", "B2", "C2",
     "arXiv:2611.23855", "16427仿真/135真机；66% 真机复现", "sim2real 反证"),
    ("dom2026", "DoM 奖励黑客激活探针", "trust", "A2", "B2", "C2",
     "arXiv:2609.19101 (2026-09-16)", "SWE-bench 73% rollout 黑客；多抓3.1%/少抓7.9%", ""),
    ("medvlm2026", "医疗 VLM 隐藏失败审计", "trust", "A2", "B2", "C2",
     "arXiv:2611.14975 (2026-11-11)", "5模型/6048问题；432 张气胸阳性片零检出", ""),
    ("em2025", "Emergent Misalignment", "trust", "A2", "B2", "C2",
     "arXiv:2502.17424", "不安全代码微调→无关领域广泛失准", "机制存争议"),
    ("aroma2026", "AROMA 冻结方向多模态控制", "fm", "A2", "B2", "C2",
     "arXiv:2611.15041 (2026-11-11)", "解释89.82% cardinality sensitivity/占9.52%激活能量；MEA 81.25%", "单作者"),
    ("mppa2026", "MPPA 扩散 LLM 免训练扩上下文", "fm", "A2", "B3", "C3",
     "arXiv:2611.15029", "8192 token PPL 19.51→3.12；passkey 100%", ""),
    ("longllada2025", "LongLLaDA", "fm", "A2", "B3", "C3",
     "arXiv:2506.14429 (AAAI 2026)", "NTK-RoPE 外推", "摘要无数值"),
    ("dgm2025", "Darwin Gödel Machine", "fm", "A2", "B2", "C2",
     "arXiv:2505.22954", "SWE-bench 20.0%→50.0%；Polyglot 14.2%→30.7%", "限定场景"),
    ("alphaevolve2025", "AlphaEvolve", "fm", "A2", "B2", "C3",
     "arXiv:2506.13131", "4×4 复矩阵乘法 48 次标量乘法（56年首次超 Strassen）", "可验证目标"),
    ("rsibench2026", "RSIBench-Infra", "fm", "A2", "B2", "C2",
     "arXiv:2611.24395", "20任务/最多32加速器；66.2% 任务>1.10×", ""),
]

WEIGHTS = {
    "A": {"A1": 1.0, "A2": 0.75, "A3": 0.35, "A4": 0.25, "A5": 0.10},
    "B": {"B1": 1.0, "B2": 0.70, "B3": 0.30, "B4": 0.00},
    "C": {"C1": 1.0, "C2": 0.55, "C3": 0.15},
}
CITE_OK = {"A1", "A2"}


def composite(a, b, c):
    """几何平均：三维任一维塌陷都会把总分压下来（避免'大'盖住'对'）。"""
    w = (WEIGHTS["A"][a], WEIGHTS["B"][b], WEIGHTS["C"][c])
    return round((w[0] * w[1] * w[2]) ** (1 / 3), 4)


def verdict(a, b):
    return "PERF_EVIDENCE" if a in CITE_OK and b in ("B1", "B2") else "ANNOUNCEMENT_ONLY"


ASSERTIVE = ("证明", "达到", "实现", "证实", "表明", "优于", "带来", "提升", "降低", "取代", "突破")


def lint(text, rows):
    """稿件核查：ANNOUNCEMENT_ONLY 记录不得以断言语气被引用为性能证据。

    判据：同一行出现该记录 id 或 title，且出现断言词 → 违规。
    PERF_EVIDENCE 记录不报（它们本就可以当性能证据引用）。
    """
    viol = []
    for r in rows:
        if r["citation_verdict"] != "ANNOUNCEMENT_ONLY":
            continue
        keys = (r["id"], r["title"])
        for ln, line in enumerate(text.splitlines(), 1):
            if any(k in line for k in keys) and any(w in line for w in ASSERTIVE):
                viol.append((ln, r["id"], line.strip()))
                break
    return viol


def build(records):
    out = []
    for rid, title, dom, a, b, c, carrier, nums, note in records:
        assert a in WEIGHTS["A"] and b in WEIGHTS["B"] and c in WEIGHTS["C"], rid
        out.append({
            "id": rid, "title": title, "direction": dom,
            "carrier_tier": a, "number_tier": b, "reproducibility_tier": c,
            "carrier": carrier, "key_numbers": nums, "note": note,
            "composite": composite(a, b, c),
            "citation_verdict": verdict(a, b),
        })
    return out


def report(rows):
    n = len(rows)
    by_dom = Counter(r["direction"] for r in rows)
    by_a = Counter(r["carrier_tier"] for r in rows)
    by_b = Counter(r["number_tier"] for r in rows)
    by_v = Counter(r["citation_verdict"] for r in rows)
    lines = [
        "# AI4S / 六方向成果证据等级分布（E1 输出）",
        "",
        "> 生成：`python3 analyses/build_evidence_tiers.py` ｜ 记录数：%d ｜ 全部分数是脚本由三维权重算出的，非手写" % n,
        "",
        "## 总量",
        "",
        "| 维度 | 分布 |",
        "|---|---|",
        "| 载体等级 A | " + " / ".join(f"{k}={v}" for k, v in sorted(by_a.items())) + " |",
        "| 数字口径 B | " + " / ".join(f"{k}={v}" for k, v in sorted(by_b.items())) + " |",
        "| 引用判定 | " + " / ".join(f"{k}={v}" for k, v in sorted(by_v.items())) + " |",
        "",
        "## 分方向",
        "",
        "| 方向 | 记录数 | 平均 composite | 可作性能证据 |",
        "|---|---|---|---|",
    ]
    for d in sorted(by_dom):
        sub = [r for r in rows if r["direction"] == d]
        avg = round(sum(r["composite"] for r in sub) / len(sub), 4)
        ok = sum(1 for r in sub if r["citation_verdict"] == "PERF_EVIDENCE")
        lines.append(f"| {d} | {len(sub)} | {avg} | {ok}/{len(sub)} |")
    lines += ["", "## 逐条", "",
              "| id | 成果 | A | B | C | composite | 引用判定 |",
              "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| `{r['id']}` | {r['title']} | {r['carrier_tier']} | {r['number_tier']} | "
                     f"{r['reproducibility_tier']} | {r['composite']} | {r['citation_verdict']} |")
    lines += ["", "## 结论", ""]
    only = [r for r in rows if r["citation_verdict"] == "ANNOUNCEMENT_ONLY"]
    lines.append(f"- %d/%d 条只能写成「宣布/声称」，不得写成「证明/达到」——这批是引用风险最高的。" % (len(only), n))
    a3a4 = [r for r in rows if r["carrier_tier"] in ("A3", "A4")]
    lines.append(f"- %d 条载体为机构通报或厂商通稿，其中 %d 条同时无性能数字口径（B3），"
                 "即「发布事件可信、性能不可引」。" % (len(a3a4), sum(1 for r in a3a4 if r["number_tier"] == "B3")))
    lines.append("- 载体等级 A 与数字口径 B 的联合分布解释了原综述的并列失真："
                 "Nature 正刊(B1) 与厂商通稿(B3) 出现在同一段落时，读者会默认它们等权。")
    return "\n".join(lines) + "\n"


def selftest(records):
    """注入违规样本：A4+B3 却标 PERF_EVIDENCE，必须被门抓住。"""
    bad = list(records) + [("__inject__", "注入违规样本", "ai4science", "A4", "B3", "C3",
                            "厂商通稿", "无", "自检")]
    rows = build(bad)
    inj = [r for r in rows if r["id"] == "__inject__"][0]
    print("inject verdict:", inj["citation_verdict"])
    if inj["citation_verdict"] != "ANNOUNCEMENT_ONLY":
        print("FAIL: gate did not catch A4+B3 as performance evidence")
        return 1
    print("PASS: A4+B3 → ANNOUNCEMENT_ONLY")
    # 反证二：把 A1+B1 误判为 ANNOUNCEMENT_ONLY 也要能红
    rows2 = build(records)
    good = [r for r in rows2 if r["id"] == "crest2025"][0]
    assert good["citation_verdict"] == "PERF_EVIDENCE", "A1+B1 must be PERF_EVIDENCE"
    print("PASS: A1+B1 → PERF_EVIDENCE")
    # 反证三：ANNOUNCEMENT_ONLY 记录被写成断言语气，门必须红
    good = "nanotitan2026 官方宣布成本降超90%（A4+B3，只能写'宣布'）。"
    bad = "nanotitan2026 实现成本降超90%，证明已达到 SOTA。"
    assert not lint(good, rows2), f"合规文本误报: {lint(good, rows2)}"
    assert lint(bad, rows2), "注入违规文本未被门抓住"
    print("PASS: 断言式引用 ANNOUNCEMENT_ONLY → 门红")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--lint", metavar="TEXTFILE", help="核查稿件文本里的引用语气（fail-closed）")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest(RECORDS))
    if args.lint:
        rows = build(RECORDS)
        text = open(args.lint, encoding="utf-8").read()
        viol = lint(text, rows)
        for ln, rid, line in viol:
            print(f"L{ln} {rid}: {line}")
        print(f"[lint] {len(viol)} violation(s)")
        sys.exit(1 if viol else 0)
    os.makedirs(os.path.abspath(OUT_DIR), exist_ok=True)
    rows = build(RECORDS)
    jl = os.path.join(OUT_DIR, "tier-taxonomy.jsonl")
    with open(jl, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rp = os.path.join(OUT_DIR, "2026-11-19-tier-report.md")
    with open(rp, "w", encoding="utf-8") as f:
        f.write(report(rows))
    print(f"wrote {jl} ({len(rows)} records)")
    print(f"wrote {rp}")


if __name__ == "__main__":
    main()
