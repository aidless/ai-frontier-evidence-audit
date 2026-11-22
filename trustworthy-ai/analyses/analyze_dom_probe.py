#!/usr/bin/env python3
"""trustworthy-ai E2/DoM 探针诊断的诚实判决器。

预注册判据（在看结果前定义，写死在代码里）：
  Q1 within_model_generalization：在训练未见家族上 TPR@FPR=target 的均值 >= 0.8
  Q2 signal_beyond_shortcut：真实 unseen AUC - max(置换对照 AUC) >= 0.2
     （置换标签后若 AUC 仍高，说明探针吃到与标签无关的模板捷径）
  Q3 cross_model_transfer：需要 hidden_size 相同才能搬运方向；不同则 NOT_ANSWERABLE

不做的事：不把同族不同规模（7B/14B）伪装成论文的跨族（GLM/Qwen/GPT-OSS）迁移。
"""
import argparse
import json
import sys


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def judge_one(d, fpr_target):
    fam = d["tpr_at_fpr_by_unseen_family"]
    tprs = list(fam.values())
    perm = d["permutation_control_auc"]
    real = d["auc_unseen_families"]
    q1 = mean(tprs) >= 0.8
    q2 = (real - max(perm)) >= 0.2 if perm else None
    return {
        "hidden_size": d["hidden_size"],
        "chosen_layer": d["chosen_layer"],
        "num_layers": d["num_layers"],
        "tpr_by_unseen_family": fam,
        "mean_tpr_unseen": round(mean(tprs), 4),
        "unseen_auc": real,
        "permutation_control_auc": perm,
        "max_perm_auc": round(max(perm), 4) if perm else None,
        "signal_minus_shortcut": round(real - max(perm), 4) if perm else None,
        "q1_within_model_generalization": bool(q1),
        "q2_signal_beyond_shortcut": bool(q2) if q2 is not None else None,
        "n_unseen_families_passing": sum(1 for t in tprs if t >= 0.8),
    }


def cross_model(d7, d14):
    same_dim = d7["hidden_size"] == d14["hidden_size"]
    return {
        "hidden_7b": d7["hidden_size"],
        "hidden_14b": d14["hidden_size"],
        "directions_transferred": bool(same_dim),
        "q3_cross_model_transfer": "NOT_ANSWERABLE" if not same_dim else "ANSWERABLE",
        "reason": ("hidden_size 不同（3584 vs 5120），DoM 方向向量无法直接搬运；"
                   "本实验是两次独立的模型内探针，不是跨模型迁移。"
                   "论文 arXiv:2609.19101 的跨族主张（GLM5.2/Qwen3.8Max/KimiK3）从未被本实验检验。"),
    }


def selftest():
    # 用合成的"真实结果"验证判决器能正确判是/判非
    good = {
        "hidden_size": 3584, "chosen_layer": 11, "num_layers": 28,
        "tpr_at_fpr_by_unseen_family": {"a": 1.0, "b": 1.0, "c": 0.9},
        "auc_unseen_families": 1.0, "permutation_control_auc": [0.4, 0.5, 0.45],
    }
    jg = judge_one(good, 0.01)
    assert jg["q1_within_model_generalization"] is True
    assert jg["q2_signal_beyond_shortcut"] is True

    # 反证 1：TPR 低 → q1 必须false
    bad_tpr = dict(good, tpr_at_fpr_by_unseen_family={"a": 0.1, "b": 0.4, "c": 0.2})
    jb1 = judge_one(bad_tpr, 0.01)
    assert jb1["q1_within_model_generalization"] is False

    # 反证 2：置换对照接近真实 → q2 必须false（捷径未被排除）
    bad_perm = dict(good, auc_unseen_families=0.55, permutation_control_auc=[0.5, 0.54, 0.52])
    jb2 = judge_one(bad_perm, 0.01)
    assert jb2["q2_signal_beyond_shortcut"] is False

    # 反证 3：维度不同 → 跨模型必须判 NOT_ANSWERABLE
    cm = cross_model({"hidden_size": 3584}, {"hidden_size": 5120})
    assert cm["q3_cross_model_transfer"] == "NOT_ANSWERABLE"
    cm_same = cross_model({"hidden_size": 3584}, {"hidden_size": 3584})
    assert cm_same["q3_cross_model_transfer"] == "ANSWERABLE"

    return {"selftest": "PASS", "cases": ["good", "bad_tpr", "bad_perm", "dim_mismatch"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--7b", dest="f7", default="trustworthy-ai/evidence/dom-full-7b.json")
    ap.add_argument("--14b", dest="f14", default="trustworthy-ai/evidence/dom-full-14b.json")
    ap.add_argument("--out", default="trustworthy-ai/evidence/dom-analysis.json")
    a = ap.parse_args()
    if a.selftest:
        print(json.dumps(selftest(), ensure_ascii=False, indent=2))
        return 0
    d7 = json.load(open(a.f7, encoding="utf-8"))
    d14 = json.load(open(a.f14, encoding="utf-8"))
    res = {
        "experiment": "trustworthy-ai E2 / DoM probe diagnostic (2026-11-21)",
        "q7b": judge_one(d7, d7.get("fpr_target", 0.01)),
        "q14b": judge_one(d14, d14.get("fpr_target", 0.01)),
        "cross_model": cross_model(d7, d14),
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
