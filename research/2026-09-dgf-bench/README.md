# September 2026 DGF-Bench experiment

Measured AI review outcomes on **300 synthetic projects**, with **899 of 900 model/case runs evaluable**. These results accompany *The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance*, by Jeremy Canale.

[Paper](../../paper/The_Last_Human_Gate.pdf) · [Final results](PAPER_RESULTS.md) · [Analysis in French](ANALYSE_FR.md) · [Complete release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923)

## Results

The paper's experimental section provides a step-by-step account, with an experiment diagram and an actual generated architecture. The generator creates a fictional business scenario (Buy, Integrate, or Build), assigns its facts and constraints, and produces documents and simulated records. The tested model reviews that case; it does not generate its own test project. At each gate it receives the applicable rules, allowed tools and evidence, and a required answer format. It investigates, submits findings/actions/evidence and a decision, then its review is passed to later gates. A deterministic evaluator checks the saved submission and tool events against the reference. Entire-route success requires every gate to pass.

| Model | Exact OpenRouter identifier | Common configuration |
|---|---|---|
| DeepSeek v4.1 Flash | `deepseek/deepseek-v4.1-flash` | Temperature 0; vision auto; 20 turns / 40 tool calls per gate; 8,192 output tokens per turn; agent handoffs. |
| Gemini 3.8 Flash | `google/gemini-3.8-flash` | Same task, tools, policy and resource limits. |
| GPT-5.6 Luna | `openai/gpt-5.6-luna` | Same task, tools, policy and resource limits. |

Two post-hoc explanatory cases make the process concrete. In **Project Falcon**, a draft runbook leads to a retained operational-handover finding and a conditional approval under an executed simulated mandate. In **Project Meridian**, Gemini correctly requests changes for a missing API gateway and excessive latency, but reverses the field order in an evidence excerpt and fails the strict proof check. [Recorded outputs and original paths](worked_examples.json). These are examples from the measured run, not additional trials.

| Model | Cases | Strict gate success | Entire route success | Known cost |
|---|---:|---:|---:|---:|
| Gemini 3.8 Flash | 299 | 94.98% | 76.92% | $71.88 |
| GPT-5.6 Luna | 300 | 83.29% | 42.33% | $5.05 |
| DeepSeek v4.1 Flash | 300 | 74.18% | 24.67% | $10.09 |

One Gemini Integrate run failed at the first gate with a provider error and is excluded. The 299 common cases support the paired comparisons. Policy rules and authoritative structured facts were available to the agents; hidden reference answers were not exposed by their tools. This experiment does not measure production remediation, human equivalence, or FTE savings.

## Every experiment file

The [release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923) contains three archives:

| Asset | Original files | Original bytes | ZIP bytes |
|---|---:|---:|---:|
| `dgf-bench-300-run.zip` | 17,700 | 136,698,306 | 33,438,260 |
| `dgf-bench-300-dataset.zip` | 27,947 | 438,842,920 | 357,635,681 |
| `dgf-bench-300-source.zip` | 1,099 | 11,618,586 | 8,744,121 |

All files in the recorded run and prepared dataset directories are included byte for byte. Each ZIP additionally contains `FILE_MANIFEST.json`, recording the path, byte count, and SHA-256 of each original file. [Release manifest](release_manifest.json) · [Archive checksums](SHA256SUMS.txt).

The run contains final and archived error traces, raw model responses, tool events and environment states, submissions, scores, usage ledgers, run configuration, model catalog snapshots, protocol identity, and exported analyses. The dataset includes every generated document, image, CSV/JSON/YAML record, policy, mandate, and reference answer. Everything is synthetic; evaluator reference files are public for offline auditing and must remain excluded from agent inputs in future evaluations.

**Use `analysis_20260923_final` for final results.** Earlier `paper_outputs` are preserved as historical partial exports. Archived absolute Windows paths are historical metadata; the reproduction script uses the local extraction root instead.

The source archive preserves the benchmark working files used during the experiment, including then-uncommitted fixes. Its protocol fingerprint is checked against the run identity. It is the source of record for reproduction; the default Git branch can differ. Third-party assets retain their included license notices.

## Reproduce without API calls

From the repository root, install the dependencies and download the archives (GitHub CLI, or use the release page):

```bash
python -m pip install -r requirements.txt numpy matplotlib
gh release download dgf-bench-300-20260923 --repo jeremy1392/dgf-agentic-bench --pattern "*.zip" --dir experiments/downloaded_300
python research/2026-09-dgf-bench/reproduce.py --archives experiments/downloaded_300 --output experiments/reproduced_300
```

The script verifies archive hashes, validates every file against the inventory, extracts into `verified_inputs`, checks source and dataset fingerprints, and regenerates the final metrics and paired bootstrap comparisons in `reports`. It also checks all evaluable score counts and the total known cost. It needs no API key and makes no model calls. Allow roughly 1 GB of disk space for downloads, verified inputs, and reports. Installing dependencies requires network access; the analysis itself is offline.

The primary outcomes are computed from saved scores. Reproducing those values checks their aggregation, not independent business correctness. For targeted rescoring, the frozen source contains `score_submission.py`; provide both the archived dataset case and its trusted model/case record directory. The release retains the traces needed for that check.

## Files and methods

- [Overall outcomes](paper_overall.csv), [by-gate outcomes](paper_by_gate.csv), and [JSON metrics](paper_results.json): strict CSR, route success, denominators, component metrics, costs, and 95% intervals.
- [Aggregates](aggregate.json), [diagnostics](diagnostics.json), and [paired comparisons](paired_comparisons.json): exclusions, matched cohort, route counts, failure components, safety findings, and model differences.
- [Dataset diversity audit](dataset_diversity_report.json): decision coverage and relevant fact/finding diversity.
- [Latest resume statistics](benchmark_run_stats.json): describes the last resume, not total elapsed collection time.
- [Overview figure](results_overview.svg): also available as [PNG](results_overview.png) and [PDF](results_overview.pdf).

Gate intervals use 2,000 route-stratified case bootstrap draws; complete-route intervals use Wilson bounds. Pairwise differences use 10,000 paired case bootstrap draws within routes. Seed: 81931. Gates within a dossier are not treated as independent trials. These intervals describe sampling uncertainty within the synthetic design, not bias, human agreement, or run-to-run model variability.

`build_paper_assets.py` rebuilds the manuscript's three benchmark tables and results chart from these summaries, renders the workflow diagram, and copies the architecture specimen from the public README assets. `package_release.py` documents archive construction and credential-pattern checks; it is a maintainer utility requiring the original local directories, not a prerequisite for readers. Neither script makes paid inference calls.

## Author

Jeremy Canale · [Website](https://www.jeremycanale.com) · [Email](mailto:contact@jeremycanale.com) · [LinkedIn](https://www.linkedin.com/in/jcanale13)
