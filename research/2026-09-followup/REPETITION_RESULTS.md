# Completed repetition study: 23–24 September 2026

**135/135 evaluable model-case runs; 765/765 gates attempted; total recorded cost $12.5598870228.**

Fifteen existing dossiers (five per route), three endpoints, and three new trajectories per endpoint/dossier. Selection used sorted case identifiers and `random.Random(23092026)` before the new outcomes. This is a local fixed analysis plan, not an external preregistration. The historical trajectories are not pooled as a fourth repeat.

## Per-repeat observations

Each model has 15 cases and 85 gates per repeat. Counts include every completed trajectory, without best-of-three selection.

| Model | Repeat | Strict gates / 85 | Complete routes / 15 | Correct dispositions / 85 | Evidence failures |
|---|---:|---:|---:|---:|---:|
| google/gemini-3.8-flash | 1 | 82 | 12 | 85 | 3 |
| google/gemini-3.8-flash | 2 | 82 | 12 | 85 | 3 |
| google/gemini-3.8-flash | 3 | 81 | 11 | 85 | 4 |
| openai/gpt-5.6-luna | 1 | 73 | 8 | 85 | 12 |
| openai/gpt-5.6-luna | 2 | 71 | 7 | 82 | 11 |
| openai/gpt-5.6-luna | 3 | 67 | 4 | 79 | 13 |
| deepseek/deepseek-v4.1-flash | 1 | 63 | 3 | 83 | 20 |
| deepseek/deepseek-v4.1-flash | 2 | 64 | 4 | 81 | 17 |
| deepseek/deepseek-v4.1-flash | 3 | 60 | 4 | 81 | 22 |

## Aggregated repeated-run performance

| Model | Strict gates, 95% interval | Complete routes, 95% interval | All three routes pass / 15 | Cost including failed attempts |
|---|---:|---:|---:|---:|
| google/gemini-3.8-flash | 96.08% [93.33, 98.43] | 77.78% [62.22, 91.11] | 9 | $10.3888500750 |
| openai/gpt-5.6-luna | 82.75% [75.29, 89.80] | 42.22% [22.22, 62.22] | 3 | $0.7498588800 |
| deepseek/deepseek-v4.1-flash | 73.33% [66.67, 79.61] | 24.44% [13.33, 37.78] | 0 | $1.4211780678 |

The 95% percentile intervals use 10,000 bootstrap draws, seed 24092026. Each draw resamples five whole dossiers with replacement within each route and retains all three trajectories and all gates. Endpoints use linear interpolation. There are only 15 distinct cases: these are exploratory conditional intervals, not enterprise-level uncertainty. DeepSeek’s zero observed all-three successes does not establish zero population probability; the degenerate empirical bootstrap interval in the machine-readable output is not a useful bound.

## What is stable, and what changes?

- Gemini ranks first in each repetition, Luna second, DeepSeek third. No pairwise significance or universal model-ranking claim is made.
- Gemini has 255/255 correct dispositions. Luna has 246/255, DeepSeek 245/255. None records a scored false approval or critical miss in this small follow-up.
- Only 9 Gemini dossiers, 3 Luna dossiers, and 0 DeepSeek dossiers pass all gates on all three trajectories. Complete-route pass/fail varies on 5, 6, and 8 dossiers, respectively.
- Exact dispositions are identical across all three trajectories on 15 Gemini dossiers, 10 Luna dossiers, and 6 DeepSeek dossiers. Optional authorized approvals can legitimately alter a disposition; disagreement is not itself an error.
- Evidence pass/fail varies on 5/85 distinct Gemini gates, 11/85 Luna gates, and 35/85 DeepSeek gates. The original structural audit of 85 historical Gemini failures has not been applied to these new traces.

## Infrastructure, provider routing, and accounting

All repeats retain identical recorded protocol identities and use the frozen source snapshot. Settings: temperature 0, agent handoff, vision auto, 20 turns, 40 tool calls, 8,192 output tokens, three workers and one per model. No model-resolution mismatch is recorded.

The archive retains **48 error checkpoints: 46 API-key-limit refusals and two provider-finish errors**. Completed prefixes were resumed in two Gemini runs (seven gates). There is one recorded truncated Gemini response. Errors and retries are not counted as extra completed trajectories; paid failed attempts remain in the append-only cost ledgers. Unknown-cost count is zero.

The initial authorization was $20; the user increased the shared ceiling to $50 after a separate OpenRouter key limit interrupted collection. Actual total spending was $12.5598870228, below the initial estimate of approximately $12.72. The ceiling amendment did not change case selection, model endpoints, repeat count, or inference settings.

DeepSeek records Alibaba, DeepInfra, Krea, Novita, Relace, StreamLake, Together, and Wafer. Gemini records Google AI Studio; Luna records OpenAI. Provider routing was not fixed, so these results do not isolate intrinsic model randomness. Resume overwrites top-level manifests and summaries: those files describe the latest invocation; error checkpoints and ledgers retain failed attempts.

## Files and reproduction

- [Audited JSON, case-level variability, score hashes, intervals and costs](repetition_analysis.json)
- [Per-repeat counts as CSV](repetition_by_run.csv)
- [Descriptive complete-run snapshot](repetition_results.json)
- [Analysis script](analyze_repetitions.py) and [archive builder](package_repetitions.py)
- [All 4,020 retained experiment files](https://github.com/jeremy1392/dgf-agentic-bench/releases/download/dgf-bench-300-20260923/dgf-bench-repetitions-20260924.zip), including copied Word dossiers, architectures, traces, scores, configurations, ledgers, and errors. The ZIP adds a per-file SHA-256 inventory.
- [Archive manifest](repetition_archive_manifest.json) and [SHA-256 checksum](repetition-SHA256SUMS.txt). The original 300-case archives and first paper are unchanged.

Extract the ZIP, then run from the repository root:

```powershell
python research/2026-09-followup/analyze_repetitions.py --run-dir PATH_TO_EXTRACTED_RUN --output-dir PATH_TO_ANALYSIS
```

The analysis makes no model calls. Original benchmark execution requires the immutable `dgf-bench-300-source.zip` from the same release. The copied dossier files are byte-verified against the original dataset before packaging.

Author: [Jeremy Canale](https://www.jeremycanale.com) · contact@jeremycanale.com
