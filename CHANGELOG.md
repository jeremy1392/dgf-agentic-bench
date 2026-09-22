# Changelog

## 7.7.0

- Add true concurrent execution across independent `(model × DGF case)` jobs with `--workers` (default 6).
- Keep every gate within a single DGF route sequential when `handoff_mode=agent`, preserving handoff causality.
- Add automatic per-model concurrency limits (`--max-workers-per-model`, default auto).
- Add a thread-safe global cost ledger with per-job budget reservations so parallel workers cannot all start from the same apparent remaining budget.
- Record HTTP retries, rate-limit responses, transient provider errors, and network errors per case.
- Add gate-level checkpoint resume: interrupted cases reuse a contiguous prefix of successful gates instead of paying to rerun the entire route.
- Count previous partial/failed OpenRouter calls in resumed experiment cost accounting.
- Preserve every failed occurrence trace across repeated resumes instead of overwriting the previous error attempt.
- Retry `INFRA_ERROR` and `BUDGET_STOP` cases on resume while preserving their previous paid trace cost; completed `OK` and `AGENT_FAILURE` cases remain final.
- Add an offline concurrency regression test proving four simultaneous jobs across three models while respecting a per-model cap of two.
- Preserve v7.6 typed finalization, multi-model identity auditing, 8192-token default, and v7.5 topology/uniqueness guarantees.

## 7.6.0

- Run multi-model experiments in balanced `round_robin` order by default instead of completing every case for model 1 before model 2 starts.
- Add typed `submit_gate_decision` tool finalization and force it on the last investigation turn.
- Add JSON-Schema structured-output fallback when a model does not finalize through the tool.
- Preserve failed-agent traces, usage, resolved model IDs, providers, finish reasons, and validation errors.
- Count model protocol failures as failed execution instead of dropping those cases from paper metrics.
- Keep infrastructure/budget failures separate from model-quality results.
- Fix incomplete-submission scoring so unattempted gates receive zero credit rather than accidental boolean/evidence credit.
- Record and report gate attempt rate, agent failure count, and requested-vs-resolved model mismatches.
- Add a model-balanced scheduler test and typed-finalization offline test.
- Restore a bundled three-case smoke dataset matching the current uniqueness/topology generator.


## 7.5.0

- Replace the fixed Azure HLD renderer with topology-aware layouts for `hub_spoke`, `single_vnet`, and `virtual_wan`.
- Make resilience geometry visibly different for single-zone, multi-AZ, backup-only, active/passive, and active/active designs.
- Add solution-aware architecture content for web, API, back-office, data, agentic-AI, and integration platforms.
- Enforce unique project IDs, project names, project codes, named people, vendors, private CIDRs, contract/HLD/LLD versions, resource prefixes, and canonical case hashes across generated datasets.
- Enforce a unique structural architecture signature for every generated DGF case via deterministic rejection sampling.
- Write `dataset_uniqueness_report.json` and fail dataset generation if a uniqueness invariant is violated.
- Give every rendered Azure resource a case-specific instance identifier to prevent visual cross-case shortcuts.
- Regenerate the bundled smoke dataset with the new diversity rules.
- Use 8192 output tokens by default throughout the OpenRouter harness and record `finish_reason` / truncation counts in raw traces and scores.

## 7.3.0

- Stream subprocess output live in the one-command runner (fixes the apparent Windows freeze caused by `capture_output=True`).
- Use the bundled 3-case dataset automatically for `--preset smoke`.
- Add `--regenerate-smoke` to explicitly rebuild smoke cases.
- Show 5 top-level experiment stages.
- Show live progress per model, case, and gate, including disposition, turns, tool calls, and response cost.
- Force unbuffered child Python output with `-u` / `PYTHONUNBUFFERED=1`.


## v7.0 - 2026-09-21

- Consolidated DGF-Bench into a GitHub-ready research repository.
- Added the arXiv-ready research paper source and compiled PDF.
- Added facts-first latent-state case generation.
- Added Buy, Integrate, Build, and full-lifecycle route models.
- Added multi-phase gate occurrences and route-aware evidence visibility.
- Added five governance dispositions: GO, GO_WITH_RESERVATIONS, REWORK, SUSPENSION, NO_GO.
- Added shared evidence graph and authoritative synthetic enterprise tools.
- Added deterministic reference evaluator and strict gate/route scoring.
- Added detailed Azure HLD generation with official Azure architecture icons, API Gateway, network/security zones, and resilience patterns.
- Added OpenRouter multi-model tool-using agent evaluation harness.
- Added model discovery, vision support, cost/token tracking, result aggregation, and handoff experiments.
- Added GitHub CI, citation metadata, preflight checks, third-party notices, and paper build tooling.
