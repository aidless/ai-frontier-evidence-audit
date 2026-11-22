#!/usr/bin/env python3
"""六项目可复算证据的汇总门禁（fail-closed）。

每个子脚本必须 --selftest 通过；任一失败 → 整闸 exit 1。
配套反证：--selftest-bad 故意注入一个必失败的假子脚本，验证闸会变红。
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (项目, 相对路径) —— 五个可复算脚本，覆盖六项目中三个 completed 卡 + fm + trust 双证据
CHECKS = [
    ("ai4science", "analyses/build_evidence_tiers.py"),
    ("trustworthy-ai", "analyses/masking_identity.py"),
    ("trustworthy-ai", "analyses/masking_point_estimate.py"),
    ("embodied-physical-ai", "analyses/recompute_sim2real.py"),
    ("fm-efficiency", "analyses/comparability_matrix.py"),
]


def run_one(project, rel):
    path = os.path.join(ROOT, project, rel)
    if not os.path.isfile(path):
        return False, f"MISSING: {project}/{rel}"
    try:
        r = subprocess.run(
            [sys.executable, path, "--selftest"],
            cwd=os.path.join(ROOT, project),
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT: {project}/{rel}"
    ok = r.returncode == 0
    tail = (r.stdout or r.stderr).strip().split("\n")[-1][:120]
    return ok, f"{'PASS' if ok else 'FAIL'}: {project}/{rel} :: {tail}"


def main():
    bad_mode = "--selftest-bad" in sys.argv
    if bad_mode:
        # 反证：给 CHECKS 拼一个不存在的脚本，闸必须判红
        checks = CHECKS + [("__nonexistent__", "analyses/fake.py")]
        expect_fail = True
    else:
        checks = CHECKS
        expect_fail = False

    results = [run_one(p, r) for p, r in checks]
    all_ok = all(ok for ok, _ in results)
    for ok, line in results:
        print(("  [OK] " if ok else "  [XX] ") + line)

    if expect_fail:
        # 反证模式：期望 all_ok == False，否则说明闸是装饰（空性失败）
        verdict = "GATE_CAN_FAIL (correct)" if not all_ok else "GATE_IS_DECORATIVE (wrong)"
        print(f"\nSELFTEST-BAD verdict: {verdict}")
        return 0 if not all_ok else 1

    print(f"\nSUMMARY: {sum(1 for ok, _ in results if ok)}/{len(results)} subgate(s) passed")
    if all_ok:
        print("OVERALL: PASS (all evidence scripts reproducible)")
        return 0
    print("OVERALL: FAIL (fail-closed: at least one evidence script not reproducible)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
