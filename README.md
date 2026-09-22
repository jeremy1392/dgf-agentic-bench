# DGF-Bench

**DGF-Bench** is a synthetic, facts-first benchmark and agent evaluation environment for enterprise **Digital Governance Frameworks (DGF)**. It is designed to test whether an AI agent can execute the work of enterprise governance gates end to end: inspect evidence, request missing information, identify findings, produce a defensible disposition, propose required actions, respect authorization boundaries, and hand structured information to downstream gates.

The repository also contains the accompanying research paper:

> **Every Gate Becomes Software: Agentic Automation of Enterprise Governance and the Contraction of Its Workforce**  
> Jeremy Canale, September 2026

- Compiled paper: [`paper/Every_Gate_Becomes_Software.pdf`](paper/Every_Gate_Becomes_Software.pdf)
- LaTeX source and reproducibility material: [`paper/`](paper/)
- Detailed explanation of the relationship between the paper and benchmark: [`docs/PAPER_AND_BENCHMARK.md`](docs/PAPER_AND_BENCHMARK.md)

## Why this benchmark exists

The paper argues that a governance gate is better understood as an **information-transforming contract** than as a profession. A gate receives a dossier and other evidence, investigates what is missing or contradictory, applies policies and decision rules, produces findings and a disposition, may trigger authorized actions, and hands a structured result to the next part of the governance process.

DGF-Bench turns that theoretical unit of analysis into an executable benchmark. Instead of asking a model to write a plausible governance report, it asks whether an agent can actually satisfy a gate contract under controlled conditions.

A typical benchmark episode looks like this:

```text
synthetic enterprise state
        ↓
shared evidence graph
        ↓
DGF gate occurrence
        ↓
agent investigates with tools
        ↓
findings + disposition + actions
        ↓
authorization checks
        ↓
structured handoff
        ↓
scoring against hidden ground truth
```

The benchmark is intended to answer questions such as:

- Which governance gates can current agents execute reliably?
- Which gates produce the highest critical-miss or false-approval rates?
- Can an agent distinguish missing evidence from negative evidence?
- Can it prefer authoritative system state over stale or contradictory documents?
- Does structured handoff from one gate improve downstream performance?
- How does gate-level reliability compound across complete Buy, Integrate, or Build routes?
- What is the quality/cost tradeoff between different models and providers?
- How close is a model to **complete gate execution**, rather than mere drafting assistance?

DGF-Bench is therefore the **experimental companion** to the paper. It operationalizes the paper's definitions and hypotheses so they can be tested longitudinally as model capabilities improve.

## What DGF-Bench does not claim

DGF-Bench is a synthetic controlled environment. A strong score does **not** by itself prove that every real-world enterprise governance process can be automated, nor does it prove the paper's universal long-horizon claim.

Results establish performance only on the declared benchmark population and experimental protocol. Real organizations have additional institutional, legal, political, operational, and data-quality constraints that may not be represented in a synthetic case.

This distinction is intentional: the paper states the theory and its falsifiable claims; DGF-Bench provides a reproducible way to test concrete execution capability.

## What is in this repository

- **Facts-first case generation**: canonical enterprise facts are generated first; documents, evidence, omissions, stale versions, and contradictions are derived from that latent state.
- **Dataset uniqueness enforcement**: project identities, named people, vendors, CIDRs, contract/HLD/LLD versions, canonical case hashes, and structural architecture signatures are unique within each generated dataset; `dataset_uniqueness_report.json` records the checks.
- **Topology-aware HLD rendering**: `hub_spoke`, `single_vnet`, and `virtual_wan` are drawn as genuinely different network topologies, with distinct resilience layouts and case-specific resource instance names.
  A generated 15-case visual preview is available at `docs/architecture_diversity_preview.png`.
- **Eight governance gate families**: General, IT, Architecture, Security Architecture, Tech Readiness, Procurement, Legal, and Compliance.
- **Route-aware execution**: Buy, Integrate, Build, and full-lifecycle cases.
- **Multi-phase governance**: the same gate can reappear with a different contract at Opportunity, Framing, Design, Build/Acceptance, and Closure.
- **Five dispositions**: `GO`, `GO_WITH_RESERVATIONS`, `REWORK`, `SUSPENSION`, `NO_GO`.
- **Shared evidence graph**: the same HLD, contract, data inventory, test result, or supplier evidence can feed several gates.
- **Interactive agent tools**: agents query authoritative evidence instead of receiving every document upfront.
- **Azure HLD generation**: detailed SVG/PNG diagrams with official Azure architecture icons, API Gateway, network/security zones, multi-AZ and multi-region resilience.
- **OpenRouter agent evaluation**: discover compatible models, run tool-using agents, record cost/tokens, and compare gate/route performance.
- **Research paper source**: arXiv-ready LaTeX source plus a compiled PDF and reproducibility artifacts.

## The eight gate families

DGF-Bench models eight reusable gate types. Enterprises may merge, split, rename, reorder, or omit gates in practice; the benchmark treats them as configurable contracts rather than a universal mandatory sequence.

| Gate | Benchmark focus |
|---|---|
| **General** | Strategic alignment, business case, budget, residual risk, reservations, benefits, and final governance arbitration |
| **IT** | Technology catalog, duplication, licences, hosting, capacity, lifecycle, support, ITSM, and run readiness |
| **Architecture** | HLD/LLD, APIs, flows, data ownership, addressing, routing, connectivity, availability, performance, and reversibility |
| **Security Architecture** | Exposure, segmentation, IAM, encryption, hardening, logging, vulnerability evidence, pentest evidence, and residual cyber risk |
| **Tech Readiness** | Production maturity, tests, resilience, backups, restoration, failover, observability, rollback, runbooks, and operational handover |
| **Procurement** | Make/buy, RFP, supplier comparison, TCO, due diligence, SLA, subcontractors, and sourcing decisions |
| **Legal** | Contract clauses, liability, SLA/penalties, IP, data terms, audit rights, termination, insurance, and signing authority |
| **Compliance** | Regulatory applicability, privacy, data residence, retention, control mapping, auditability, ethics, accessibility, and recurring obligations |

## Facts-first benchmark design

The correct answer is **derived from the latent enterprise state**; it is not independently randomized after the documents are generated.

```text
canonical facts
     ↓
deterministic reference evaluator
     ↓
expected findings / actions / disposition

canonical facts
     ↓
document & evidence factory
     ↓
truthful / stale / partial / contradictory observations
     ↓
agent-visible case
```

This design allows the benchmark to include realistic ambiguity without making the ground truth arbitrary. A document can say that a SQL service is private while an authoritative Azure resource export shows public network access. The agent is expected to investigate and resolve the contradiction using the available evidence hierarchy.

## Route-aware execution

The benchmark includes several example route compositions:

```text
BUY
Business need → Procurement → Legal → Compliance → Security → IT → General

INTEGRATE
Existing system → IT → Architecture → Security → Legal → Compliance → General

BUILD
New project → IT → Architecture → Security → Tech Readiness → General
```

`full_lifecycle` cases can also exercise the same gate at multiple project phases. This supports experiments on route composition, rework, evidence requests, reservations, and downstream handoff quality.

## Repository layout

```text
DGF-Bench/
├── README.md
├── LICENSE
├── LICENSE-MIT
├── LICENSE-APACHE
├── NOTICE
├── CITATION.cff
├── Makefile
├── requirements.txt
├── .env.example
├── paper/                         # LaTeX source + compiled paper
├── docs/                          # Benchmark design and evaluation docs
├── openrouter_eval/               # Model/tool loop, prompts, catalog, aggregation
├── openrouter_smoke_dataset/      # Public smoke-test dataset only
├── example_diagrams/              # Generated Azure HLD examples
├── assets/                        # Azure icon pack + Microsoft usage terms
├── generate_dgfbench_v6.py        # Facts-first case generator
├── facts_engine.py                # Canonical latent state
├── evidence_graph.py              # Shared evidence graph
├── evaluator.py                   # Deterministic reference evaluator
├── synthetic_environment.py       # Interactive synthetic enterprise environment
├── score_submission.py            # Gate/route scoring
├── run_openrouter_benchmark.py    # Multi-model OpenRouter runner
├── discover_openrouter_models.py  # Live model capability discovery
└── prepare_openrouter_experiment.py
```

## Quick start

### 1. Create a Python environment

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\\Scripts\\activate     # Windows
pip install -r requirements.txt
```

### 2. Run the offline tests

```bash
make test
```

or directly:

```bash
python self_test_v6.py
python smoke_test_openrouter_harness.py
```

### 3. Generate synthetic cases

```bash
python generate_dgfbench_v6.py \
  --count 10 \
  --seed 1000 \
  --difficulty 4 \
  --route build \
  --output-dir generated_cases
```

Supported route modes:

```text
buy
integrate
build
full_lifecycle
```

### 4. Create a balanced experiment dataset

```bash
python prepare_openrouter_experiment.py \
  --cases-per-route 50 \
  --seed 12000 \
  --difficulty 4 \
  --output-dir experiments/dataset_150
```

## One-command OpenRouter experiment

If you only want to provide an OpenRouter key and model IDs and receive paper-ready results, use:

```bash
python run_full_experiment.py \
  --api-key YOUR_OPENROUTER_KEY \
  --models z-ai/glm-5.3 z-ai/glm-5.3-flashx
```

The safe default is the `pilot` preset (5 cases per Buy/Integrate/Build route). For the frozen main experiment used in a paper:

```bash
python run_full_experiment.py \
  --models MODEL_A MODEL_B MODEL_C \
  --preset paper \
  --workers 6 \
  --max-cost-usd 150
```

If `--api-key` is omitted, the script prompts for the key without echoing it, which avoids placing the key in shell history. The key is never written to the experiment files.

The script automatically:

1. validates the exact model IDs against the live OpenRouter catalog and requires tool support;
2. creates a balanced Buy/Integrate/Build dataset unless `--dataset` is supplied;
3. runs every selected model under the same protocol;
4. scores all gate and route executions;
5. aggregates OpenRouter token/cost usage;
6. calculates Wilson 95% confidence intervals for strict gate CSR and route-complete execution;
7. writes paper-ready JSON, CSV, Markdown, and LaTeX results.

Main outputs appear under `experiments/run_<timestamp>/paper_outputs/`:

```text
PAPER_RESULTS.md
paper_overall.csv
paper_by_gate.csv
paper_results.json
paper_table_overall.tex
aggregate.json
```

Presets:

```text
smoke  = 1 case per route  (3 cases total)
pilot  = 5 cases per route (15 cases total)
paper  = 50 cases per route (150 cases total)
```

## OpenRouter evaluation

### Concurrent multi-model execution (v7.7)

DGF-Bench now runs independent **model × DGF case** jobs concurrently. The default is `--workers 6`. For three models, the automatic per-model limit is two simultaneous cases per model. Gates inside one route are **not** parallelized in `handoff_mode=agent`: IT → Architecture → Security → Readiness → General (or the equivalent route) remains sequential so downstream gates receive the tested model's actual upstream handoff.

Example:

```bash
python run_full_experiment.py \
  --models MODEL_A MODEL_B MODEL_C \
  --preset pilot \
  --workers 6 \
  --max-cost-usd 25
```

Useful controls:

```text
--workers 6                    total concurrent model×DGF jobs
--max-workers-per-model 0      0 = auto ceil(workers / models)
--job-budget-reserve-usd 0.50  reserve before each concurrent job is launched
```

The cost cap is enforced with a thread-safe observed-cost ledger plus reservations for in-flight jobs. Because provider cost is known only after a response completes, already-running requests can still cross the nominal cap; the harness prevents new jobs from being launched once the cap/reservation guard binds. OpenRouter 429/5xx/network retries are recorded in each case score.

Interrupted runs also resume at the **gate level**: a contiguous prefix of completed gates is reused, preserving route handoffs and avoiding unnecessary paid reruns. Previous failed attempts are retained for complete cost accounting.

On Windows, `run_parallel_pilot.ps1` launches the default three-model pilot with the project `.venv` and six workers.

### Multi-model fairness and typed finalization (v7.6)

`round_robin` is now the default schedule. Models are interleaved across cases rather than running all 15/150 cases for model A before model B starts. This makes progress visibly multi-model and prevents an interrupted or global-budget-limited run from systematically favoring the first model. Use `--schedule model_major` only to reproduce the legacy order.

Each gate now exposes a typed `submit_gate_decision` tool. The model investigates with the normal evidence tools and then submits the final contract through that tool. The last investigation turn is forced to finalize, and a JSON-schema structured-output fallback is used if necessary. This reduces incidental `Agent did not produce valid JSON` failures without relaxing the semantic scoring contract. Any remaining model protocol failure is retained as failed execution rather than silently removed from aggregate results. Infrastructure failures remain separately labeled and excluded from model-quality estimates.

Every successful API response records the requested model and OpenRouter's resolved `model` field. A mismatch counter is surfaced in paper outputs so model identity can be audited.


### One-command runner progress on Windows

The v7.6 one-command runner streams child-process output live and uses a balanced round-robin multi-model schedule by default. You should see explicit stages such as:

```text
[1/5] Validating OpenRouter models...
[2/5] Using bundled smoke dataset...
[3/5] Running agent benchmark through OpenRouter...
[benchmark] schedule=round_robin | models=3 | cases=15 | jobs=45 | pending=45 | workers=6 | per_model=2
[job 1/45 | MODEL_A | DGF-...] START (case 1/15, model 1/3)
[job 1/45 | MODEL_A | DGF-...] gate 1/6 procurement (...) ...
[job 1/45 | MODEL_A | DGF-...] gate 1/6 -> REWORK | turns=... | tools=... | resolved=MODEL_A | cost=$...
[job 2/45 | MODEL_B | DGF-...] START (case 1/15, model 2/3)
[4/5] Aggregating benchmark results...
[5/5] Creating paper-ready outputs...
```

For `--preset smoke`, the bundled three-case smoke dataset is used by default, so the connectivity test does not regenerate DOCX/HLD artifacts. Add `--regenerate-smoke` only when you specifically want to rebuild those three cases.


Do not commit API keys. Copy the environment template:

```bash
cp .env.example .env
```

Then set:

```text
OPENROUTER_API_KEY=your_key_here
```

You can also use the interactive helper:

```bash
python configure_openrouter.py
```

Discover currently available OpenRouter models and their capabilities:

```bash
python discover_openrouter_models.py \
  --search 'gpt|claude|gemini|glm|deepseek|qwen' \
  --min-context 100000
```

Run a one-case smoke test:

```bash
python run_openrouter_benchmark.py \
  --dataset openrouter_smoke_dataset \
  --models z-ai/glm-5.3-flashx \
  --max-cases 1 \
  --max-cost-usd 1 \
  --output-dir openrouter_results/smoke
```

Run several models under identical conditions:

```bash
python run_openrouter_benchmark.py \
  --dataset experiments/dataset_150 \
  --models MODEL_A MODEL_B MODEL_C \
  --temperature 0 \
  --vision auto \
  --max-cost-usd 100 \
  --output-dir openrouter_results/experiment_001
```

Aggregate results:

```bash
python aggregate_openrouter_results.py \
  --results openrouter_results/experiment_001
```

See [docs/OPENROUTER_EVAL.md](docs/OPENROUTER_EVAL.md) for the full evaluation protocol.

## Interactive agent environment

The agent is not simply handed all evidence. It can investigate with tools such as:

```text
list_evidence()
read_evidence()
get_azure_resource()
get_cmdb_record()
get_iam_assignments()
get_contract_version()
get_backup_job()
get_restore_test()
get_failover_test()
get_siem_connector_status()
get_vulnerability_findings()
get_regulatory_applicability()
request_vendor_evidence()
request_evidence()
create_risk_card()
return_to_design()
approve_with_conditions()
```

This makes DGF-Bench an **agentic execution benchmark**, not just a document-question-answering benchmark.

## Benchmark outputs and metrics

Each gate occurrence has hidden reference outcomes derived from canonical facts. The evaluator can score:

- disposition accuracy;
- critical finding recall;
- finding/action precision and recall;
- evidence fidelity;
- authorization correctness;
- false approval rate;
- critical miss rate;
- strict gate Complete Substitution Rate (CSR);
- route complete-execution rate;
- tool calls, turns, tokens, and model cost.

`99_hidden_ground_truth.json` is benchmark-only data and must never be exposed to the evaluated agent.

### Strict gate CSR

A gate counts as a strict complete success only when the agent gets the required decision, critical findings, actions, evidence grounding, and authorization behavior correct under the benchmark contract.

This is deliberately stricter than normal answer accuracy because the paper's concept of **complete execution** includes more than producing plausible prose.

## Handoff experiments

The OpenRouter runner supports different handoff conditions so the benchmark can measure whether structured upstream evidence improves downstream execution:

```text
none    - no upstream handoff
agent   - prior agent outputs are passed downstream
oracle  - correct structured handoffs are supplied
```

This supports controlled experiments on information structure, coordination, and route-level reliability.

## Paper

The accompanying paper is included so the theoretical claims, benchmark unit of analysis, and experimental design remain together in one reproducible repository.

### Paper role

**Every Gate Becomes Software** develops the theoretical argument, formal definitions, labor model, route composition, handoff hypotheses, objections, and long-horizon falsifiable claim. It distinguishes the governance function from its current human implementation and defines what complete gate execution would require.

### Benchmark role

**DGF-Bench** turns those definitions into testable artifacts. It creates bounded synthetic gate contracts, hidden ground truth, evidence hierarchies, interactive tools, authorization state, and route-level scoring so current and future agents can be evaluated under repeatable conditions.

### How to use both together

If an experiment shows that a model achieves high CSR on Security or Tech Readiness, that is evidence about capability **within DGF-Bench**, not direct proof of universal automation. If performance improves across model generations, the benchmark provides a reproducible trajectory measurement that can support, challenge, or refine the paper's predictions.

The paper source is in [`paper/`](paper/). A compiled copy is included as:

[`paper/Every_Gate_Becomes_Software.pdf`](paper/Every_Gate_Becomes_Software.pdf)

Build it locally with:

```bash
make paper
```

## Documentation

- [Benchmark design](docs/BENCHMARK_DESIGN.md)
- [Gate coverage](docs/GATE_COVERAGE.md)
- [OpenRouter evaluation guide](docs/OPENROUTER_EVAL.md)
- [Paper/benchmark relationship](docs/PAPER_AND_BENCHMARK.md)
- [GitHub publication guide](docs/GITHUB_PUBLISH.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## Azure architecture icons

This repository contains Microsoft Azure architecture icons for the permitted purpose of rendering architecture diagrams, documentation, and training/evaluation material. Microsoft usage terms and FAQ are retained alongside the assets under `assets/azure-icons/Azure_Public_Service_Icons/`.

The DGF-Bench **MIT OR Apache-2.0** license does not replace or override Microsoft's terms for those assets. Do not use Microsoft product icons to represent DGF-Bench itself or another product.

## Reproducibility

Random generation is seed-driven. For experiments, record at minimum:

- repository commit hash;
- model ID returned by OpenRouter;
- seed and difficulty;
- route and handoff mode;
- temperature and tool settings;
- model/provider metadata;
- benchmark version;
- token usage and cost.

## Secrets and public release

The `.gitignore` excludes `.env`, keys, local result directories, caches, and LaTeX build artifacts. Before pushing, run:

```bash
make preflight
```

The included `openrouter_smoke_dataset` is public test material and should not be used as a hidden leaderboard set. Generate fresh private test cases for real evaluations.

## Citation

See [`CITATION.cff`](CITATION.cff). If you use the theoretical framework, cite the paper. If you use the benchmark, generated datasets, or model evaluations, cite DGF-Bench and record the exact repository commit and benchmark configuration.

## License

The original DGF-Bench source code and original benchmark documentation are **dual-licensed under MIT OR Apache-2.0, at your option**.

- [`LICENSE`](LICENSE) — scope and dual-license notice
- [`LICENSE-MIT`](LICENSE-MIT) — MIT License
- [`LICENSE-APACHE`](LICENSE-APACHE) — Apache License 2.0
- [`NOTICE`](NOTICE) — notices associated with the Apache-2.0 option
- [`LICENSE-NOTICE.md`](LICENSE-NOTICE.md) — human-readable licensing summary

The software license does not automatically cover the research paper or third-party assets. The manuscript under `paper/` remains separately copyrighted unless a separate paper license is added, and Microsoft Azure icons remain under Microsoft's own terms. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
