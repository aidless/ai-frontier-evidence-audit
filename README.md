# Evidence, Not Enrollment

**Eight recomputable methodological diagnostics on 2026 AI-frontier claims.**

[![paper](https://img.shields.io/badge/paper-PDF-blue)](synthesis/paper/main.pdf)
[![evidence gate](https://img.shields.io/badge/evidence%20gate-5%2F5%20PASS-green)](#reproduce)
[![arxiv gate](https://img.shields.io/badge/arxiv%20gate-37%2F37%20PASS-green)](#reproduce)

A six-direction survey of the 2026 AI frontier (world models / NSP, agents,
embodied & physical AI, AI for science, trustworthy AI, foundation-model
engineering) turned into an auditable research project and then a methods paper.
The central finding: **none of the six directions is wrong — the error is
placing results of different evidence grades in the same table.**

## The paper

> *Evidence, Not Enrollment: Eight Recomputable Methodological Diagnostics on
> 2026 AI Frontier Claims* — 7 pages, TMLR preprint format, anonymous.

- [Read the PDF](synthesis/paper/main.pdf)
- Source: [`synthesis/paper/main.tex`](synthesis/paper/main.tex) + [`synthesis/paper/sections/`](synthesis/paper/sections/) (modular `\input`), `tmlr.sty` bundled.
- The expanded Chinese synthesis is in [`synthesis/manuscript/review.md`](synthesis/manuscript/review.md); the navigation index is [`synthesis/README.md`](synthesis/README.md).

**Abstract.** The 2026 discussion of AI research fronts often presents six
directions as one synchronous wave of progress. We audit the claims behind each
direction and find that the problem is not correctness but evidentiary grade.
We make the audit operational with eight *recomputable* diagnostics, each built
to a pre-registered criterion and equipped with counter-evidence self-tests that
prove the apparatus can fail and still be caught. Diagnostics deliberately
target "substrate unavailable" cards: when code, weights, or per-trial logs are
not released, we convert "cannot test" into a quantitative statement about what
would make it testable. Four diagnostics return a directly citable verdict;
four turn unavailability itself into a conclusion. Across all eight, the scope
of a conclusion is fixed by the apparatus and reporting caliber, not by model
scale.

## The eight diagnostics

| # | Diagnostic | Verdict |
|---|---|---|
| 1 | NSP three-arm (next-token / next-frame / next-state) | action-conditioned state has lowest **absolute** long-horizon error (0.0024), but the "lowest-slope" criterion fails against a quantization floor → `not_supported` |
| 2 | Multi-view projection | single view degrades 3.03× vs 8.50× under cross-embodiment perturbation → `supported_synthetic` (code/weights of the source method unreleased) |
| 3 | Termination-lag early stopping | success governed by detector false-positive rate; collapses once FPR ≥ 0.01 → `partial_support_synthetic` |
| 4 | Workflow-author detectability | with 145 tasks, main-effect MDE dz = 0.234; 16 repeated evals → 0.059 → `not_answerable_with_public_substrate` |
| 5 | Self-reported 1.9× consistency | headline 1.9× incompatible with the public 5 sub-item average at any assignment of the 3 hidden items → `not_identifiable_with_public_data` |
| 6 | DoM activation probe | 7B signal barely clears shortcut, 14B validator family TPR = 0 → mixed / partially negative |
| 7 | Sensitivity–energy geometry | "high explanation power + low activation energy" is the arithmetic of a low-rank (r ≪ d) subspace → `GEOMETRY_GENERIC` |
| 8 | 92.1% stratified recompute | flat across eight scenarios (leave-one-out spread 2.38 pp, χ²(7) p = 0.40) → `STRATIFIED_RECOMPUTE_PASS` |

The reusable method: **pre-register the criterion → build a contrast apparatus →
run a counter-evidence self-test → write results to disk → state the caliber
boundary.** Every number in the paper is traceable to a file under `*/evidence/`.

## Repository layout

```
world-model-nsp/       agentic-systems/     embodied-physical-ai/
ai4science/            trustworthy-ai/      fm-efficiency/
  analyses/              scripts/ that produce the numbers (standard library / numpy / torch)
  evidence/             落盘 results + baseline claim-verification tables
  experiments/           pre-registered experiment designs (E1/E2)
  manuscript/            per-direction draft + full-text deep dives
  research-manifest.json machine-readable source of truth (schema2)
synthesis/
  README.md              cross-project index + caliber baseline table
  manuscript/review.md   expanded review
  paper/                 the submitted-format methods paper + TMLR style
  evidence/              37-paper arXiv verification ledger
scripts/
  six_projects_evidence_gate.py   fail-closed evidence reproducibility gate
  arxiv_verification_gate.py      fail-closed arXiv id verification gate
```

## Reproduce

Both gates are fail-closed (each runs the analysis scripts' `--selftest` and
checks that a deliberately broken variant turns the gate red). No GPU needed
for the gates.

```bash
python3 scripts/six_projects_evidence_gate.py    # expect 5/5 PASS, exit 0
python3 scripts/arxiv_verification_gate.py       # expect 37/37 PASS, exit 0
```

Individual diagnostics can be re-run; e.g.

```bash
python3 ai4science/analyses/build_evidence_tiers.py --selftest
python3 embodied-physical-ai/analyses/acecap0_stratified_recompute.py --selftest
python3 fm-efficiency/analyses/sensitivity_energy_geometry.py --selftest
```

Some full analyses ran on a cloud GPU (AMD gfx1100 / ROCm) or used released
model weights; environment-specific connection details were redacted from this
public copy. The self-tests and all published-aggregate recomputations are
CPU-only.

## Cite

```bibtex
@misc{evidence_not_enrollment_2026,
  title  = {Evidence, Not Enrollment: Eight Recomputable Methodological
            Diagnostics on 2026 AI Frontier Claims},
  author = {Anonymous Author(s)},
  year   = {2026},
  note   = {Anonymous preprint; author details withheld for double-blind review}
}
```

## License

MIT — see [LICENSE](LICENSE). Paper source and evidence are released for
academic reuse with attribution; the anonymous-author placeholder is retained
in the paper until camera-ready.
