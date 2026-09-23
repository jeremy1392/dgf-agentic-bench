<p align="center">
  <a href="paper/The_Last_Human_Gate.pdf">
    <img src="assets/readme/last-human-gate-fde-hero.png" alt="The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance — research paper by Jeremy Canale" width="1200" />
  </a>
</p>

<h1 align="center">DGF-Bench</h1>

<p align="center">
  Research and project by <strong>Jeremy Canale</strong><br />
  <a href="mailto:contact@jeremycanale.com">contact@jeremycanale.com</a> &nbsp; · &nbsp;
  <a href="https://www.linkedin.com/in/jcanale13">LinkedIn</a>
</p>

<p align="center">
  <strong>The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance</strong><br />
  DGF-Bench tests whether AI agents can review projects, spot problems, and make justified decisions.
</p>

<p align="center">
  <code>8 types of review</code> &nbsp; <code>3 project paths</code> &nbsp; <code>5 possible decisions</code>
</p>

<p align="center">
  <a href="paper/The_Last_Human_Gate.pdf"><strong>Read the paper ↗</strong></a> &nbsp; · &nbsp;
  <a href="#what-we-want-to-measure">What we measure</a> &nbsp; · &nbsp;
  <a href="#the-papers-timeline">Timeline</a> &nbsp; · &nbsp;
  <a href="#get-started">Get started</a> &nbsp; · &nbsp;
  <a href="CITATION.cff">Cite this work</a>
</p>

---

## The idea in plain language

Before a company buys software, connects two systems, or launches a new application, people review the project. They check its security, contracts, budget, technical design, and readiness for use. They decide whether it can proceed and what needs to change.

**We want to measure how reliably an AI can perform these reviews when it has documents, clear rules, and tools to investigate.** Can it find the important problems, justify its decision with evidence, respect its authority, and pass useful information to the next reviewer?

A **gate** is one review checkpoint, such as Security or Legal. A **Digital Governance Framework (DGF)** is the way a company organizes these checkpoints. A **route** is the sequence of checkpoints followed by a project. A **dossier**, or case, is the project's collection of facts and documents.

### The bigger question: how much human work will DGF still need?

**Jeremy Canale's hypothesis: by 2033, the DGF ecosystem will require 80% fewer full-time equivalents (FTE) than in 2026, for comparable project volume, quality, and service.** In the paper's illustrative baseline, that means **140 FTE today and at most 28 FTE in 2033**, including human supervision and support.

**FTE means full-time equivalent, or ETP in French.** It measures an amount of work. Two people each spending half their working time on DGF contribute one FTE together. It does not mean one individual employee. The paper converts human work into FTE using a stated convention of 120 useful hours per month.

The scope spans architecture, security, operations, technical readiness, compliance, project support, and related procurement, legal, and finance work. Exceptions, rework, maintenance, and supplier support stay in the account. Moving work to a contractor does not eliminate it.

DGF-Bench tests an early part of the argument: whether AI performs reviews reliably. The FTE reduction is a research hypothesis; confirming it requires measuring human work in organizations. Individual headcount, staffing choices, and employment effects are separate outcomes.

### Why Forward Deployed Engineering?

Forward Deployed Engineers work with customer teams to turn technology into operational systems. The paper already examines their role: connect the evidence sources, implement the review rules and permissions, evaluate the agents, and make the handoffs work across the whole DGF. This deployment perspective is now explicit in the title. [Read the paper's FDE section](paper/sections/s17_fde.tex).

Their work is part of the accounting. Initial implementation is a transition investment; recurring adaptation, evaluation, maintenance, and support remain in the required FTE. The 2033 hypothesis cannot be met by moving work from governance teams to uncounted engineers. The current benchmark does not measure FDE productivity or establish these savings.

### A concrete example

Imagine a company wants to buy a cloud application. The supplier looks suitable, but some customer references have not been checked and a contract clause needs attention.

The AI must read the relevant evidence, identify which rules apply, explain the problems, and propose the required next steps. It may need to ask for information or check whether someone has authorized acceptance of a particular risk. Then it must choose the decision allowed by the rules.

**An approval is not automatically a success.** If the correct response is to request changes, wait, or reject the project, that is what a successful AI should do.

## What we want to measure

| In everyday terms | What we check |
|---|---|
| **Does it make the right decision?** | Does its decision match the rules for this particular case? |
| **Does it find the problems and suggest the right fixes?** | Which required problems and actions did it identify, miss, or invent? |
| **Can it show why?** | Did it actually read the relevant evidence and provide valid supporting excerpts? |
| **Does it stay within its authority?** | Does it respect approval conditions and permissions? Does it approve something that should be blocked? |
| **Can it get the whole project review right?** | Does every required checkpoint succeed, including those that receive information from earlier reviews? |
| **What does it cost, and does it finish?** | How many calls and tokens are used, what is the recorded cost, and how many cases complete or fail technically? |

### How to read a score

The strict **gate success rate**, called **Gate CSR** in the reports, is the percentage of review checkpoints that meet *all* the scoring requirements: decision, identified problems, proposed actions, evidence, and authorization.

**Complete-route success** is stricter: every checkpoint in the project's route must pass. For example, if an AI gets four of a five-checkpoint project's reviews completely right, its gate success rate on that project is 80%, but that project's route is not complete. This is an illustration, not an experimental result.

The reports also show the individual components. This matters because an AI can reach the correct decision yet fail the evidence requirement. For example, an excerpt that rearranges source text can fail the exact-quotation rule. We distinguish those errors from an incorrect decision.

A **critical miss** means the AI failed to identify a problem classified as critical by the benchmark. A **false approval** means it allowed a project to proceed when the applicable rules and validated permissions required changes, a pause, or rejection.

## How we test it

We generate **fictional company projects** with known facts. Documents, technical diagrams, and expected review outcomes are derived from those facts. The model receives the allowed evidence and rules, but not the answer key.

Each model works through the same cases using tools to inspect evidence, ask questions, and submit decisions. The evaluator then compares its work with the expected outcome and the recorded actions. The files preserve what the model read, what it submitted, and what the provider charged.

## How project reviews work

### Where reviews happen during a project

<p align="center">
  <a href="assets/readme/dgf-lifecycle-matrix.svg"><img src="assets/readme/dgf-lifecycle-matrix.svg" alt="A project moves from an initial idea to planning, design, testing, and closure. The grid shows which review teams are involved at each stage. A General review brings their conclusions together at every stage." width="1200" /></a>
</p>

**Figure 1 — A project can be reviewed more than once.** Read this grid from left to right as the project progresses. A blue dot means that type of specialist review is used at that stage. An amber diamond is the General review, which brings the other conclusions together. This full-lifecycle example contains 26 reviews; it is separate from the shorter Buy, Integrate, and Build routes below. Companies can organize these reviews differently. [Source: route definitions](routes.py).

### What happens inside one review

<p align="center">
  <a href="assets/readme/gate-contract.svg"><img src="assets/readme/gate-contract.svg" alt="A project team supplies facts and documents. A reviewer checks them against the rules and records problems, evidence, proposed fixes, and a decision. Approval authority is checked separately. A request for changes sends the dossier back for revision." width="1200" /></a>
</p>

**Figure 2 — Read, investigate, explain, decide.** Having an opinion that a risk is acceptable does not automatically give the reviewer permission to accept it. The authorization checks establish what is allowed. The return arrow shows what requesting changes means; it does not claim that the benchmark carries out those changes in a real company. [Source: the paper's gate example](paper/sections/s_appF_contract.tex).

| Decision in the report | Plain-language meaning |
|---|---|
| `GO` | Proceed. |
| `GO_WITH_RESERVATIONS` | Proceed with stated conditions, under the applicable authorization rules. |
| `REWORK` | Make the required changes and bring the dossier back for review. |
| `SUSPENSION` | Wait for a prerequisite, information, funding, or arbitration. |
| `NO_GO` | Do not proceed with the proposal as submitted. |

### Three kinds of project

<p align="center">
  <a href="assets/readme/dgf-main-routes.svg"><img src="assets/readme/dgf-main-routes.svg" alt="Buy means purchasing a solution, Integrate means connecting systems, and Build means developing a new solution. Each project follows a different sequence of specialist reviews, ending with a General review." width="1200" /></a>
</p>

**Figure 3 — Different projects follow different paths.** Buy and Integrate use six checkpoints; Build uses five. In the normal `agent` setting, the next checkpoint receives the AI's earlier review outputs. The `oracle` setting supplies reference outputs instead, and `none` omits those messages. Comparing these settings can help study whether the information passed between reviews affects performance. [Source: route definitions](routes.py).

## How we compare models

<p align="center">
  <a href="assets/readme/research-design.svg"><img src="assets/readme/research-design.svg" alt="Example study: three models each review the same 300 fictional projects. There are 100 Buy, 100 Integrate, and 100 Build cases, giving 900 model-case runs and 5,100 review checkpoints in total. These are planned counts, not results." width="1200" /></a>
</p>

**Figure 4 — The comparison plan.** The illustrated setup uses 300 different projects, each reviewed by three models. That means 900 runs, not 900 different projects. The 5,100 checkpoints include repeated reviews of the same projects across models. These numbers describe the study design; they do not say how much of an experiment has finished.

We compare models on cases they have all completed. A provider outage or an exhausted API-key budget is recorded separately from a wrong answer. If a run stops early, the remaining cases are missing observations, not evidence that the AI passed or failed their reviews.

The [figure sources and regeneration command](assets/readme/README.md) are included, with SVG and high-resolution PNG downloads.

## What this study can tell us

It can show **how reliably the tested models review these fictional cases under the stated rules**, where they make mistakes, how errors affect later reviews, and what the evaluation costs.

It cannot, on its own, show that an AI can run every real company's governance process, fix the problems it identifies, save a measured number of working hours, or replace employees. Those questions need additional studies in real organizations.

The test cases are generated, so their variety and rules matter. Balancing the dataset to include different decisions helps test more situations; it does not tell us how common those situations are in business. The answer key also needs independent checking: agreement with the program that generated it is not proof that every business rule is sound.

### How this relates to the paper

**[The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance](paper/The_Last_Human_Gate.pdf)**, by Jeremy Canale (September 2026), sets out the broader argument and its research hypotheses. Its numerical examples about human work are calculations based on stated assumptions, not measured deployments.

**DGF-Bench tests a narrower part of that argument:** can AI models perform the specified review tasks reliably? Model results, synthetic workforce calculations, and claims about real-world automation must remain clearly distinguished. [Paper sources](paper/main.tex) · [Reproduction package](paper/anc/).

## The paper's FTE model

The two charts below come directly from the paper's reproduction code and parameters. **They are synthetic calculations, not measured staffing reductions.**

<p align="center">
  <a href="assets/readme/fig_trajectory.svg"><img src="assets/readme/fig_trajectory.svg" alt="Paper configurations: 140, 60.56, 16.35, 5, and 0 required FTE, split across Buy, Integrate, Build, and support. A dotted line marks the 2033 hypothesis of at most 28 FTE, 80 percent below the illustrative baseline. The configurations have no assigned dates." width="1100" /></a>
</p>

**From 140 FTE to different levels of remaining work.** The bars reuse the paper's configurations. The **28-FTE line** is the 2033 hypothesis applied to this example; the bars are not a year-by-year forecast.

| Configuration from the paper | Required FTE, support included | Reading |
|---|---:|---|
| Manual baseline | **140.00** | The illustrative starting workload. |
| Uneven substitution | **60.56** | Progress differs across routes; this remains above 28 FTE. |
| All routes advanced | **16.35** | This configuration falls below the 28-FTE threshold. |
| Full gate execution | **5.00** | Direct execution is automated, but human support remains. |
| Closed-support endpoint | **0.00** | Complete closure is assumed in this stronger, undated configuration. |

**Support is inside the target.** If 5 FTE of support remain, at most 23 other FTE can remain to meet the 28-FTE threshold. The 140-FTE pool illustrates an enterprise's governance work; it is not a census of the ecosystem. A real study must include supplier work consistently at baseline and follow-up. [Paper configuration appendix](paper/sections/s_appE_trajectory.tex).

<p align="center">
  <a href="assets/readme/fig_components.svg"><img src="assets/readme/fig_components.svg" alt="Four paper scenarios at the same task coverage and volume require 43.52, 85.32, 89.07, or 168.92 FTE. Bars include exceptions, review, rework, and human upkeep. The manual baseline is 140 FTE." width="1100" /></a>
</p>

**The same automation coverage can save work or create more of it.** These four operating scenarios hold case volume and coverage fixed. Their costs in exceptions, review, rework, and support differ. In the most burdensome scenario, the requirement rises to **168.92 FTE**, above the 140-FTE baseline. This is why we measure the whole human-work account. [Paper workload example](paper/sections/06_example.tex).

## The paper's timeline

**2033 hypothesis: 80% fewer required FTE than in 2026, at comparable governed output, quality, and service.** This means 20 FTE remaining per 100 baseline FTE, or 28 per 140. It does not predict an identical percentage decline in individual employees.

| When | What we measure | What it means |
|---|---|---|
| **2026: establish the baseline** | Human hours, converted into FTE under a fixed convention, including execution and support. | Baseline records cover the year ending on 20 September 2026. No enterprise cohort has yet been enrolled. |
| **2027 to 2032: follow adoption** | Review capability, remaining human effort, exceptions, new support work, quality, and authority. | The existing capability scenarios explore possible progress; they do not establish the FTE prediction. |
| **September 2032 to September 2033: observe the final year** | Average monthly FTE, with both actual workload and a comparison standardized to baseline project volume and case mix. | Include periodic maintenance and shared support. Fewer projects alone cannot establish an efficiency gain. |
| **20 September 2033: test the threshold** | Required FTE at comparable output must be **20% or less of baseline**, with quality, service, and authority requirements met. | Above 20%, the prediction fails for that population. Missing data or uncertainty around the threshold can leave the result inconclusive. |
| **Longer term: investigate complete automation** | Test whether every necessary execution and support task can be automated. | The zero-FTE configuration remains a stronger conjecture without a fixed date. |

The paper's task-length and reliability scenarios retain their explicit assumptions. Qualification of an individual work package is different from reducing total required FTE. Broad inference to the DGF ecosystem requires representative coverage, and attributing a reduction to AI requires a comparative study.

Sources: [FTE mechanism and hypothesis](paper/sections/s11_workforce.tex) · [study protocol](paper/anc/cohort_protocol.md) · [figure parameters and reproduction code](paper/anc/) · [SVG/PNG downloads](assets/readme/README.md).

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
- Validate a sample independently. Reusing the reference evaluator to check public observations establishes internal consistency, not independent business validity.
- Report uncertainty at the case level and distinguish decision correctness from evidence-format compliance. Do not treat partial runs as completed studies.

Historical datasets and generators remain in the repository for reproducibility; they are not automatically compatible with newer scoring protocols or suitable as held-out evaluation data.

</details>

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

## Author and contact

**Jeremy Canale** is the author of *The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance* and the creator of DGF-Bench.

For research questions, feedback, or collaboration:

- **Email:** [contact@jeremycanale.com](mailto:contact@jeremycanale.com)
- **LinkedIn:** [Jeremy Canale](https://www.linkedin.com/in/jcanale13)

Please credit Jeremy Canale when citing or building on this research, and retain the attribution required by the applicable licenses.

## Citation and license

Use [CITATION.cff](CITATION.cff) to cite the paper. For benchmark experiments, also cite DGF-Bench and identify the repository commit, protocol, and dataset configuration.

Original benchmark code and documentation are dual-licensed under **MIT OR Apache-2.0**; see [LICENSE](LICENSE). The [paper has separate copyright terms](paper/LICENSE-NOTICE.md). Microsoft Azure icons and other third-party assets retain their own terms, documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

<p align="center">
  <a href="paper/The_Last_Human_Gate.pdf"><strong>The Last Human Gate</strong></a><br />
  <sub>Forward Deployed Engineering and the Automation of Enterprise Governance</sub>
</p>
