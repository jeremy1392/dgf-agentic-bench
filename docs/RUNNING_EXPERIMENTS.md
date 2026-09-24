# Running and reproducing DGF-Bench

[Back to the project](../README.md) · [Published results and offline reproduction](../research/2026-09-dgf-bench/README.md)

Use the frozen release to reproduce the published study. The commands below also explain how to run a new experiment with your checkout; new inference is paid and is a separate evaluation.

## Get started

### 1. Install

Python 3.10 or later is required. Create an environment, activate it for your shell, and install dependencies:

```text
python -m venv .venv
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

```text
python -m pip install -r requirements.txt
```

### 2. Run an experiment

Choose exact model identifiers from the OpenRouter catalog. `MODEL_ID` below is a placeholder:

```text
python discover_openrouter_models.py --min-context 100000 --limit 20
python run_full_experiment.py --models MODEL_ID --preset smoke --regenerate-smoke --workers 1 --max-cost-usd 5
```

Set `OPENROUTER_API_KEY` in your terminal's environment before launching, or enter it at the launcher's hidden prompt. The smoke command makes paid API calls; offline checks do not. OpenRouter's account balance and API-key spending limit are separate from the script's budget cap.

To reproduce the published results, use the [exact benchmark source snapshot](https://github.com/jeremy1392/dgf-agentic-bench/releases/download/dgf-bench-300-20260923/dgf-bench-300-source.zip) and [offline reproduction instructions](../research/2026-09-dgf-bench/README.md). That frozen protocol includes collection-time changes; the default-branch checkout is not a substitute for it. Reproducing the released measurements requires no new model calls.

| Preset | Cases per route | Total cases |
|---|---:|---:|
| `smoke` | 1 | 3 |
| `pilot` | 5 | 15 |
| `paper` | 50 | 150 |

Use `--cases-per-route 100` for 300 newly generated cases across the three main routes. Equal route counts do not imply balanced decisions or findings. For a prepared dataset, its manifest determines the cases used:

```text
python run_full_experiment.py --dataset PATH_TO_DATASET --models MODEL_A MODEL_B MODEL_C --preset paper --workers 6 --max-cost-usd 65
```

The budget shown is an example spending ceiling, not a cost estimate or a guarantee of completion. With 300 cases and three models, the experiment schedules 900 model/case runs. With six workers and three models, the automatic limit is two concurrent cases per model. Gates within a case remain sequential in `agent` handoff mode.

Useful controls include `--temperature`, `--vision`, `--handoff-mode`, `--max-turns`, `--max-tool-calls`, and `--max-output-tokens`; inspect `python run_full_experiment.py --help` for the options in your checkout. Handoff modes are `agent` (model outputs), `oracle` (reference outputs), and `none`.

## Read the results

Each new one-command experiment writes to `experiments/run_<timestamp>/`:

| Location | Contents |
|---|---|
| `experiment_config.json` | Models, dataset path, generation and execution settings |
| `results/` | Per-model, per-case traces, submissions, scores, and usage records |
| `paper_outputs/PAPER_RESULTS.md` | Human-readable results |
| `paper_outputs/` | Aggregate JSON, CSV tables, and a LaTeX summary table |

Start with `PAPER_RESULTS.md`, then check how many cases each model actually completed. A high score on a small, incomplete subset is not a result for the whole dataset. Check the separate Buy, Integrate, and Build results, and keep provider errors visible. Reviews from the same project share information, so uncertainty should be assessed at the project level.

<details>
<summary><strong>Resume an interrupted experiment</strong></summary>

For a compatible interrupted run, use `run_openrouter_benchmark.py` with the **original dataset, models, results directory, and execution settings**. This lower-level runner supports resumption; avoid `--no-resume`. Retain the original code and data, and follow any compatibility checks implemented by that protocol version. A new `run_full_experiment.py` invocation creates a new experiment rather than continuing the previous one.

After a lower-level resume, regenerate aggregates:

```text
python aggregate_openrouter_results.py --results PATH_TO_EXISTING_RESULTS
```

This updates the aggregate JSON in the results directory. It does not refresh the one-command launcher's separate `paper_outputs` tables. Existing exports must be regenerated before publication.

</details>

## For researchers: make the comparison reproducible

<details>
<summary><strong>Protocol, sampling, and statistical details</strong></summary>

- Freeze the dataset, prompts, model settings, and scoring protocol before evaluation. Keep development cases separate from the final test set.
- Record the repository commit and local changes, model/provider identity, seed, difficulty, routes, sampling policy, exclusions, and costs.
- State whether sampling follows the generator distribution or conditions cases on target decisions. Coverage balancing is not an estimate of real enterprise prevalence.
- Keep hidden reference files, including `99_hidden_ground_truth.json`, outside agent-visible evidence.
- Interpret reference-evaluator checks as internal consistency; professional validity of the business rules is outside this experiment.
- Report uncertainty at the case level and distinguish decision correctness from evidence-format compliance. Do not treat partial runs as completed studies.

Historical datasets and generators remain in the repository for reproducibility; they are not automatically compatible with newer scoring protocols or suitable as held-out evaluation data.

</details>

## Offline checks and paper build

The paper's arithmetic checks and figure regeneration also require NumPy and Matplotlib:

```text
python -m pip install "numpy>=1.24" "matplotlib>=3.7"
```

The following checks do not call paid model APIs:

```text
python self_test_v6.py
python smoke_test_openrouter_harness.py
python self_test_multimodel_protocol.py
python self_test_uniqueness.py
python paper/anc/test_reproduce.py
```

With LaTeX, `latexmk`, and Make installed:

```text
make paper
```

This builds `paper/The_Last_Human_Gate.pdf`. The [paper README](../paper/README.md) documents the direct LaTeX build; the [reproduction package](../paper/anc/README.md) explains the numerical assumptions and generated tables.

For the second paper, follow the [self-contained LaTeX build and verification instructions](../paper2/README.md#sources-and-reproduction).
