# README visuals

These assets explain the research; they do not report model performance. They include explanatory diagrams, synthetic FTE calculations, and one unchanged generated evidence specimen. The four numbered research figures use a restrained light background, numbered panels, descriptive captions, and source references. SVG sources remain editable; explanatory PNG exports are 2,100 pixels wide.

## Experiment walkthrough

| Visual | Downloads | Grounding |
|---|---|---|
| From a fictional project to a scored review | [SVG](experiment-walkthrough.svg) / [PNG](experiment-walkthrough.png) | Six conceptual stages of the active generator and agent pipeline, with the reference restricted to the evaluator |
| Backup and restore review | [SVG](experiment-restore-example.svg) / [PNG](experiment-restore-example.png) | Illustrative application of `TR-RESTORE-001` in [evaluator.py](../../evaluator.py), assuming all other checks pass; not a model trace or a finding about the architecture specimen |
| Generated architecture specimen | [SVG](example-architecture.svg) / [PNG](example-architecture.png) | Byte-for-byte copy of public synthetic evidence from case `DGF-BLD-035200_build`, dataset `preflight_balanced_300_20260922`; original PNG dimensions: 1,980 × 1,320 |

Rebuild the two explanatory diagrams:

```text
python assets/readme/build_experiment_figures.py --render-png
```

The [builder](build_experiment_figures.py) reuses the research figures' visual primitives and makes no network or model calls. Its diagram text explains the implemented pipeline; it is not computed from model scores.

The architecture specimen comes from `gate_evidence/architecture/Architecture_Diagram_Detailed.svg` and its paired PNG. [Context and provenance](example-project-context.json) preserve an excerpt of the public project facts, seed, and architecture signature. It is evidence to review, not an independently validated design. Its labels can require cross-checking against other case evidence. The diagram builder does not regenerate this specimen, and its hidden answer key is not included here. Azure icon attribution and terms are documented in [third-party notices](../../THIRD_PARTY_NOTICES.md).

## Verification diagrams

| Visual | English | Français |
|---|---|---|
| When the agent is checked | [SVG](verification-timing.svg) / [PNG](verification-timing.png) | [SVG](verification-timing-fr.svg) / [PNG](verification-timing-fr.png) |
| How a gate passes | [SVG](verification-criteria.svg) / [PNG](verification-criteria.png) | [SVG](verification-criteria-fr.svg) / [PNG](verification-criteria-fr.png) |

These diagrams explain the original strict scoring protocol. They were checked against the frozen benchmark source extracted under `experiments/reproduction_check_20260923/verified_inputs/benchmark_source`: `synthetic_environment.py` validates conditional-approval tool requests during a gate; `openrouter_eval/benchmark_runner.py` preserves actual agent handoffs and calls the scorer after the route; `score_submission.py` checks the five components and replays conditional approvals. The frozen source archive is available in the [experiment release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923).

The diagrams distinguish review correctness from executing physical remediation. They describe the original strict evidence requirements, not the later structural-matching sensitivity analysis. No new experiment or performance measurement is represented.

Rebuild all four language variants:

```text
python assets/readme/build_verification_figures.py --render-png
```

The [builder](build_verification_figures.py) uses the existing vector drawing primitives and CairoSVG for PNG export. It makes no network or model calls.

## Research figures

| Figure | SVG / PNG | Grounding |
|---|---|---|
| 1. DGF lifecycle | [SVG](dgf-lifecycle-matrix.svg) · [PNG](dgf-lifecycle-matrix.png) | Gate/phase activity generated from `ROUTES['full_lifecycle']` in [routes.py](../../routes.py): 26 occurrences over five phases |
| 2. Gate contract | [SVG](gate-contract.svg) · [PNG](gate-contract.png) | Conceptual synthesis of the [framework definition](../../paper/sections/s02_dgf.tex) and [gate-contract appendix](../../paper/sections/s_appF_contract.tex); simulated actions and conceptual rework are identified as such |
| 3. Main routes | [SVG](dgf-main-routes.svg) · [PNG](dgf-main-routes.png) | Gate order and phase for Buy, Integrate, and Build generated directly from [routes.py](../../routes.py) |
| 4. Experimental design | [SVG](research-design.svg) · [PNG](research-design.png) | An example configuration of 100 cases per main route and three models; 900 model/case runs and 5,100 gates are design counts, not completion or performance measurements |

Rebuild the figures from the repository root:

```text
python assets/readme/build_research_figures.py --render-png
```

SVG generation uses Python's standard library. PNG rendering uses CairoSVG, already declared in the project dependencies. The script makes no network or model calls. It does not read experiment results or change the benchmark's Python sources. Source: [build_research_figures.py](build_research_figures.py).

For a paper or slide, use the SVG when possible; all labels remain vector text. The main comparison and full-lifecycle example are distinct configurations and must not be combined into a single case count. The research questions in the README are proposed evaluation questions, not established findings.

## FTE charts reused from the paper

| Chart | Downloads | Meaning |
|---|---|---|
| Substitution configurations | [SVG](fig_trajectory.svg) / [PNG](fig_trajectory.png) / [paper PDF figure](../../paper/figures/fig_trajectory.pdf) | Original 140, 60.56, 16.35, 5, and 0 FTE configurations; dotted 28-FTE threshold for the 2033 hypothesis |
| Operating burdens | [SVG](fig_components.svg) / [PNG](fig_components.png) / [paper PDF figure](../../paper/figures/fig_components.pdf) | Original S0-S3 decomposition into exceptions, review, rework, and upkeep at fixed coverage |

These charts are rendered by the paper's [reproduction script](../../paper/anc/reproduce.py) from its [parameters](../../paper/anc/parameters.json). They are synthetic calculations, not empirical results or a fitted calendar trajectory. The paper uses 120 useful hours/month per FTE. All support is included in the displayed totals; the illustrative enterprise pool is not an ecosystem census.

To regenerate the paper's outputs and the matching README SVG/PNG charts, run from the repository root:

```text
python paper/anc/reproduce.py
```

## Editorial assets

| Asset | Purpose | Production |
|---|---|---|
| `last-human-gate-fde-hero.png` | Current paper banner with the Forward Deployed Engineering subtitle | Built-in ImageGen edit of the original banner; [edit prompt](banner-fde-prompt.txt) |
| `last-human-gate-hero.png` | Archived original banner used as the edit source | Built-in ImageGen; retained for provenance |
| `benchmark-flow.svg` | Supplemental overview of facts, public evidence, agent review, and evaluator-only reference flow | Hand-authored SVG with accessible title and description |
| `governance-routes.svg` | Earlier compact overview of Buy, Integrate, and Build, retained as a supplemental asset | Hand-authored SVG with accessible title and description |

The diagrams use the same navy, cyan, and amber palette as the banner. They contain no model performance numbers. The banner is conceptual art, not a representation of an enterprise deployment.

## Original banner prompt (archived)

Generated with the built-in ImageGen tool, not the CLI/API fallback. Final prompt:

```text
Use case: stylized-concept.
Create a premium editorial hero banner for a GitHub research repository about "The Last Human Gate", a paper on AI and enterprise governance. Extra-wide horizontal composition, approximately 3:1 aspect ratio, suitable for a README at 1200px wide.
Design a quiet, architectural scene: a sequence of four monumental rectangular portal frames on a dark midnight navy plane receding in perspective. The nearest portal on the right has a thin warm amber edge; the others have restrained icy cyan edges. A tiny solitary human silhouette stands beside the nearest threshold, providing scale. A fine, precise network of luminous lines travels through the portals, subtly suggesting information moving through governance reviews. Physically plausible materials, frosted glass, charcoal anodized metal, soft volumetric light, subtle paper-like grain. Sophisticated scientific editorial art, restrained and spacious, not cyberpunk.
The left 48 percent is a calm nearly solid midnight navy field with impeccably typeset editorial text, exactly:
"THE LAST"
"HUMAN GATE"
and beneath, smaller:
"Can AI Automate Enterprise Governance?"
At the top left in small tracked lettering:
"DGF-BENCH / RESEARCH"
Title off-white in a bold elegant modern sans-serif, amber dot accent optional. Title must be clearly readable, large and spelled exactly. Keep all text comfortably inside a generous 80px safe margin. No tiny unreadable decorative text, no brands, no watermarks, no performance numbers, no claims of scientific results. Composition must feel like a high-end research publication cover rather than a software dashboard.
```
