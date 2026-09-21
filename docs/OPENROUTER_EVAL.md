# DGF-Bench OpenRouter Agent Evaluation

This harness evaluates **tool-using agents** against DGF-Bench through OpenRouter's OpenAI-compatible Chat Completions API.

## 1. Configure your key

```bash
cp .env.example .env
# edit .env
```

The runner reads `OPENROUTER_API_KEY`. The key is never written to result files.

## 2. Discover current models

OpenRouter changes its catalog frequently, so the project does **not** assume a fixed model list.

```bash
python discover_openrouter_models.py --min-context 100000 --limit 50
python discover_openrouter_models.py --provider openai --min-context 100000
python discover_openrouter_models.py --provider anthropic --min-context 100000
python discover_openrouter_models.py --provider z-ai --min-context 100000
python discover_openrouter_models.py --search 'gpt|claude|glm|gemini|deepseek|qwen' --json model_catalog.json
```

By default only models whose OpenRouter catalog advertises the `tools` parameter are shown.

## 3. Smoke-test one model / one case

```bash
python run_openrouter_benchmark.py \
  --dataset /path/to/DGF_Bench_v6_Samples \
  --models z-ai/glm-5.3-flashx \
  --max-cases 1 \
  --max-cost-usd 1.00 \
  --output-dir openrouter_results/smoke
```

## 4. Compare several models

```bash
python run_openrouter_benchmark.py \
  --dataset /path/to/hidden_cases \
  --models MODEL_ID_1 MODEL_ID_2 MODEL_ID_3 \
  --max-cases 100 \
  --max-cost-usd 100 \
  --vision auto \
  --output-dir openrouter_results/experiment_001
```

Then aggregate:

```bash
python aggregate_openrouter_results.py --results openrouter_results/experiment_001
```

## Agent protocol

For every route occurrence, the model receives:
- public project/route context;
- the gate contract;
- a **candidate finding catalog** containing possible finding IDs/actions but not which ones apply;
- upstream agent outputs from the current run;
- user-defined DGF tools;
- `list_evidence` and `read_evidence` tools for the public dossier.

The model must investigate, then return:

```json
{
  "occurrence_id": "...",
  "disposition": "GO|GO_WITH_RESERVATIONS|REWORK|SUSPENSION|NO_GO",
  "finding_ids": [],
  "actions": [],
  "evidence_refs": [],
  "authorization_required": false,
  "rationale": "...",
  "confidence": 0.0
}
```

The hidden ground truth is never exposed through the public evidence reader.

## Vision

`--vision auto` attaches the generated HLD PNG to Architecture/Security-oriented calls when the OpenRouter catalog says the model accepts image input. Models without image input use the SVG textual extraction and authoritative tools.

## Cost and reproducibility

The runner requests OpenRouter usage accounting and records:
- prompt tokens;
- completion tokens;
- reasoning tokens when reported;
- cached prompt tokens when reported;
- `usage.cost`;
- resolved model returned by OpenRouter;
- provider field when returned;
- tool calls and public evidence reads.

`--max-cost-usd` is a hard run budget based on observed response cost. It cannot prevent the request that crosses the threshold, so use a conservative value for smoke tests.

For scientific comparisons:
- use exact model IDs rather than an automatic cross-model router;
- keep temperature, case set, max turns and token limits fixed;
- record the catalog snapshot used for the experiment;
- do not use different fallback model IDs for one benchmark condition;
- run multiple replicates if sampling is non-deterministic.

## Security / privacy

- `.env` is gitignored.
- The key is only sent to OpenRouter.
- No key is stored in traces or summaries.
- `read_evidence` can only access evidence IDs present in the public evidence graph and blocks hidden files.

## Handoff experiments

The harness supports three route conditions:

```bash
--handoff-mode agent   # propagate the tested model's own upstream outputs
--handoff-mode oracle  # provide correct structured upstream handoffs (useful for H2 experiments)
--handoff-mode none    # no upstream handoff context
```

This makes it possible to measure error propagation separately from the value of structured handoffs.

## Generate a balanced hidden-case dataset

```bash
python prepare_openrouter_experiment.py \
  --cases-per-route 50 \
  --seed 12000 \
  --difficulty 4 \
  --output-dir experiments/dataset_150
```

For the expensive full-lifecycle condition, add `--include-full-lifecycle`.

### Interactive key setup (avoids shell history)

```bash
python configure_openrouter.py
```

The script hides key input and writes `.env` with restrictive permissions where supported.

## Paper-facing metrics

The v7 scorer adds strict execution metrics on top of the original weighted score:

- **Gate CSR**: fraction of gate occurrences with exact disposition, exact finding set, exact action set, valid evidence references, and correct authorization requirement.
- **Route complete-execution rate**: fraction of cases where every gate occurrence is a strict success.
- **Critical misses** and **false approvals** remain explicit safety metrics.

These are intentionally strict and can be reported alongside softer F1/accuracy metrics.
