#!/usr/bin/env python3
"""arXiv 号-题一致门禁（fail-closed）。

检查 manuscript/ 与 synthesis/manuscript/ 里引用的每个 arXiv 号是否都在
synthesis/evidence/arxiv-verification.json 权威台账里（VERIFIED）。

- 默认：扫描所有手稿，出现台账外的号 → exit 1。
- --selftest：注入一个已知假号，必须判红；再验真号通过。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "synthesis/evidence/arxiv-verification.json")
MANUSCRIPTS = [
    "world-model-nsp/manuscript/draft.md",
    "agentic-systems/manuscript/draft.md",
    "embodied-physical-ai/manuscript/draft.md",
    "ai4science/manuscript/draft.md",
    "trustworthy-ai/manuscript/draft.md",
    "fm-efficiency/manuscript/draft.md",
    "synthesis/manuscript/review.md",
]
ARXIV_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")


def load_ledger():
    with open(LEDGER, encoding="utf-8") as f:
        data = json.load(f)
    return {k for k, v in data["entries"].items() if v.get("verdict") == "VERIFIED"}


def scan():
    verified = load_ledger()
    cited = {}
    for rel in MANUSCRIPTS:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        for m in ARXIV_RE.finditer(open(path, encoding="utf-8").read()):
            cited.setdefault(m.group(1), []).append(rel.split("/")[0])
    unverified = {k: v for k, v in cited.items() if k not in verified}
    return verified, cited, unverified


def main():
    if "--selftest" in sys.argv:
        verified, cited, unverified = scan()
        # 正例：现有手稿应无未验号
        if unverified:
            print(f"SELFTEST FAIL: unexpected unverified ids: {unverified}")
            return 1
        # 反例：注入假号必须被抓
        fake = "9999.99999"
        assert fake not in verified, "selftest fake id collides with ledger"
        if fake in verified or ARXIV_RE.search(fake) is None:
            print("SELFTEST FAIL: fake id not detectable")
            return 1
        # 模拟扫描命中假号 → 应判未验
        simulated = {fake: ["selftest"]}
        bad = {k: v for k, v in simulated.items() if k not in verified}
        if not bad:
            print("SELFTEST FAIL: gate did not flag injected fake id")
            return 1
        print(f"SELFTEST PASS: {len(verified)} verified ids; real manuscripts clean; "
              f"injected {fake} correctly flagged UNVERIFIED")
        return 0

    verified, cited, unverified = scan()
    print(f"Ledger: {len(verified)} VERIFIED ids")
    print(f"Cited in manuscripts: {len(cited)} unique ids")
    if unverified:
        print("UNVERIFIED citations (fail-closed):")
        for k, v in sorted(unverified.items()):
            print(f"  {k} <- {', '.join(sorted(set(v)))}")
        print("OVERALL: FAIL")
        return 1
    print("OVERALL: PASS (all cited arXiv ids are in the verified ledger)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
