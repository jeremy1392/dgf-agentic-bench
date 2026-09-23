<p align="center">
  <a href="paper/The_Last_Human_Gate.pdf">
    <img src="assets/readme/last-human-gate-hero.png" alt="The Last Human Gate: Can AI Automate Enterprise Governance? — research paper by Jeremy Canale" width="1200" />
  </a>
</p>

<h1 align="center">DGF-Bench</h1>

<p align="center">
  <strong>Research artifacts for evidence-grounded governance decisions.</strong><br />
  A synthetic enterprise governance benchmark and research companion to <em>The Last Human Gate</em>.
</p>

<p align="center">
  <code>8 gate families</code> &nbsp; <code>3 core routes</code> &nbsp; <code>5 dispositions</code>
</p>

<p align="center">
  <a href="paper/The_Last_Human_Gate.pdf"><strong>Read the paper ↗</strong></a> &nbsp; · &nbsp;
  <a href="#research-framework">Research framework</a> &nbsp; · &nbsp;
  <a href="#get-started">Get started</a> &nbsp; · &nbsp;
  <a href="CITATION.cff">Cite this work</a>
</p>

---

DGF-Bench evaluates tool-using AI agents on governance review tasks: inspect evidence, identify findings, choose a disposition, propose actions, respect authorization rules, and pass structured results to the next gate. Reference outcomes are derived from generated enterprise facts.

| 01 / RESEARCH | 02 / BENCHMARK | 03 / REPRODUCIBILITY |
|---|---|---|
| **The Last Human Gate** | **Governance as a testable task** | **Inspect the assumptions** |
| A theoretical framework for governance automation and residual human work. | Synthetic dossiers, evidence tools, authorization rules, and route-level evaluation. | LaTeX sources, numerical parameters, generated tables, and model traces. |
| [Read the manuscript](paper/The_Last_Human_Gate.pdf) | [Explore the protocol](#research-framework) | [Open the research package](paper/anc/) |

*Jeremy Canale · September 2026. The paper's workforce calculations are synthetic scenarios, not measured deployments. Model evaluations are separate empirical results.*

## Research framework

A **Digital Governance Framework (DGF)** organizes the reviews through which an enterprise change is assessed and authorized. Specialist gates issue findings and opinions; a General gate consolidates them and arbitrates commitments. Gate families, ordering, and tasks can vary across organizations.

### 1. Position gates across the lifecycle

<p align="center">
  <a href="assets/readme/dgf-lifecycle-matrix.svg"><img src="assets/readme/dgf-lifecycle-matrix.svg" alt="DGF activity matrix: eight gate families across Opportunity, Framing, Design, Build and Acceptance, and Deployment and Closure. General arbitration occurs in each phase. The full-lifecycle example contains 26 gate occurrences." width="1200" /></a>
</p>

**Figure 1 — A configurable DGF lifecycle.** Generated from the `full_lifecycle` definition in [routes.py](routes.py). Filled circles identify specialist reviews; diamonds identify General arbitration. The same gate family can return under a different phase contract. This example is separate from the three shorter routes used in the main comparison. See the [paper's framework definition](paper/sections/s02_dgf.tex).

### 2. Define an explicit review contract

<p align="center">
  <a href="assets/readme/gate-contract.svg"><img src="assets/readme/gate-contract.svg" alt="Gate contract: a dossier owner provides versioned evidence; an agent or expert investigates it; the review yields findings, a disposition, proposed actions, citations, and authorization state. A separately validated mandate controls permitted actions. Rework can return the dossier for revision." width="1200" /></a>
</p>

**Figure 2 — Inputs, obligations, authority, and outputs.** The unit of analysis is a gate occurrence, not a job title. A favorable assessment and permission to commit are distinct. The dashed return illustrates the governance meaning of `REWORK`; it does not claim that the fixed-route benchmark completes a real remediation cycle. See the [gate-contract appendix](paper/sections/s_appF_contract.tex).

### 3. Compose and evaluate routes

<p align="center">
  <a href="assets/readme/dgf-main-routes.svg"><img src="assets/readme/dgf-main-routes.svg" alt="Buy has six reviews: Procurement, Legal, Compliance, Security, IT, General. Integrate has six: IT, Architecture, Security, Legal, Compliance, General. Build has five: IT, Architecture, Security, Tech Readiness, General. Each node also identifies its review phase." width="1200" /></a>
</p>

**Figure 3 — Main benchmark routes and phases.** Sequences and phase labels are generated directly from [routes.py](routes.py). Within a route, gates run sequentially. In `agent` handoff mode, downstream gates receive the model's upstream outputs; `oracle` and `none` provide comparison conditions.

## Experimental design

<p align="center">
  <a href="assets/readme/research-design.svg"><img src="assets/readme/research-design.svg" alt="Example experimental design: 100 Buy, 100 Integrate, and 100 Build dossiers evaluated by three models on the same cases. This schedules 900 model-case runs and 5,100 gate occurrences. These are planned counts, not reported completion or performance results." width="1200" /></a>
</p>

**Figure 4 — A matched comparison on shared dossiers.** The illustrated configuration uses 300 cases and three models. Its counts describe the design, not experiment completion. Gate counts are derived from the route definitions. Model comparisons retain the dossier as the sampling unit and report technical exclusions separately.

| Research question | Observable quantities |
|---|---|
| **RQ1. Can an agent produce a correct gate review?** | Disposition accuracy, finding/action precision and recall, evidence support |
| **RQ2. Does it respect authorization boundaries?** | Authorization correctness, false approvals, critical misses |
| **RQ3. How does reliability change across a route?** | Strict gate success, complete-route success, handoff-condition comparisons |
| **RQ4. What resources does the evaluation require?** | Calls, tokens, cost, availability, and unfinished or excluded cases |

The five dispositions are `GO`, `GO_WITH_RESERVATIONS`, `REWORK`, `SUSPENSION`, and `NO_GO`; applicability depends on the gate and phase. A valid refusal can be the correct answer. Report the scoring version and sampling policy alongside every result.

> **Study boundary**
>
> The benchmark measures review decisions, proposed actions, and simulated authorization. It does not establish completed enterprise remediation, production deployment, hours saved, or workforce replacement. A high score on this synthetic population does not by itself establish the paper's broader automation thesis.

The figures are available as editable SVGs and high-resolution PNGs. Their [sources, definitions, and regeneration command](assets/readme/README.md) are included in the repository.

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

The launcher reads `OPENROUTER_API_KEY` from the environment or local `.env`, or prompts for it with hidden input. The smoke command makes paid API calls; offline checks do not. OpenRouter's account balance and API-key spending limit are separate from the script's budget cap.

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

Inspect evaluated, excluded, and unfinished case counts before interpreting scores. Infrastructure failures are not evidence of incorrect model decisions. Compare models on common completed cases and report coverage by route. Gates from the same case are dependent observations; 1,700 gates from 300 dossiers are not 1,700 independent dossiers.

<details>
<summary><strong>Resume an interrupted experiment</strong></summary>

For a compatible interrupted run, use `run_openrouter_benchmark.py` with the **original dataset, models, results directory, and execution settings**. This lower-level runner supports resumption; avoid `--no-resume`. Retain the original code and data, and follow any compatibility checks implemented by that protocol version. A new `run_full_experiment.py` invocation creates a new experiment rather than continuing the previous one.

After a lower-level resume, regenerate aggregates:

```text
python aggregate_openrouter_results.py --results PATH_TO_EXISTING_RESULTS
```

This updates the aggregate JSON in the results directory. It does not refresh the one-command launcher's separate `paper_outputs` tables. Existing exports must be regenerated before publication.

</details>

## Research use and reproducibility

- Freeze the dataset, prompts, model settings, and scoring protocol before evaluation. Keep development cases separate from the final test set.
- Record the repository commit and local changes, model/provider identity, seed, difficulty, routes, sampling policy, exclusions, and costs.
- State whether sampling follows the generator distribution or conditions cases on target decisions. Coverage balancing is not an estimate of real enterprise prevalence.
- Keep hidden reference files, including `99_hidden_ground_truth.json`, outside agent-visible evidence.
- Validate a sample independently. Reusing the reference evaluator to check public observations establishes internal consistency, not independent business validity.
- Report uncertainty at the case level and distinguish decision correctness from evidence-format compliance. Do not treat partial runs as completed studies.

Historical datasets and generators remain in the repository for reproducibility; they are not automatically compatible with newer scoring protocols or suitable as held-out evaluation data.

## Offline checks and paper build

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

This builds `paper/The_Last_Human_Gate.pdf`. The [paper README](paper/README.md) documents the direct LaTeX build; the [reproduction package](paper/anc/README.md) explains the numerical assumptions and generated tables.

<details>
<summary><strong>Repository map and further reading</strong></summary>

| Path | Role |
|---|---|
| `paper/` | Manuscript, compiled PDF, and synthetic calculations |
| `facts_engine.py`, `evaluator.py` | Case facts and reference rules |
| `generate_dgfbench_v6.py`, `prepare_openrouter_experiment.py` | Case and dataset generation; filenames retain historical version names |
| `openrouter_eval/` | Agent loop, tools, provider client, runner, and aggregation |
| `score_submission.py` | Scoring against reference outcomes |
| `synthetic_environment.py` | Simulated evidence queries and governance actions |
| `docs/` | Design, gate coverage, and protocol documentation |

See [the paper/benchmark relationship](docs/PAPER_AND_BENCHMARK.md) for the boundary between theoretical claims and empirical evaluation. Release history belongs in [CHANGELOG.md](CHANGELOG.md).

</details>

## Citation and license

Use [CITATION.cff](CITATION.cff) to cite the paper. For benchmark experiments, also cite DGF-Bench and identify the repository commit, protocol, and dataset configuration.

Original benchmark code and documentation are dual-licensed under **MIT OR Apache-2.0**; see [LICENSE](LICENSE). The [paper has separate copyright terms](paper/LICENSE-NOTICE.md). Microsoft Azure icons and other third-party assets retain their own terms, documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

<p align="center">
  <a href="paper/The_Last_Human_Gate.pdf"><strong>The Last Human Gate</strong></a><br />
  <sub>Can AI Automate Enterprise Governance?</sub>
</p>
