# General-only handoff replay: prepared, not executed

No model API was called and no new budget authorization was assumed. Two offline preparations are retained: the originally proposed 15-case plan and a more informative targeted proposal after inspecting whether its treatment actually changes the inputs.

## Original 15-case plan: 270 fresh General executions

The cases are exactly the 15 previously selected in `repetition_plan.json`: five per route, three models, three fresh trajectories per arm. Each fresh trajectory runs **only the final General occurrence**, not the full route. Both arms are newly sampled; a historical General response is not reused as a control outcome.

- Arm A: the original upstream agents' decisions, findings, actions, and authorization flags.
- Arm B: the corresponding rule-reference outputs, adjusted to exactly the same recorded upstream conditional approvals that the frozen approval validator accepts.

Both histories use the same normalization: preserve case/occurrence/gate/phase/source-version identifiers; sort finding/action arrays without removing duplicates; omit rationale, evidence references/quotes, and verification-status labels from both arms. **This is a new intervention on normalized decision content, not a verbatim reproduction of historical prompts.** The full historical handoffs remain in evaluator-only audit files. No `oracle` label, treatment label, or General target is included in the model-facing history.

The preparer reconstructs references with the frozen scorer's logic, replays every upstream conditional approval, and verifies that all 45 selected historical case scores reproduce exactly. It validates that only `disposition`, `finding_ids`, `actions`, and `authorization_required` can differ within each matched history. The two arms have identical non-history messages, tool schemas, model capability settings, public evidence, active General mandate, turn/tool/token limits, and proposed budget envelope. The prompt and `UPSTREAM_DECISIONS` tool receive the same assigned history; no mixed-arm prompt/tool state is allowed.

The prepared directory contains 90 payloads, 45 evaluator-only audit records, and a manifest assigning three fresh trajectories to each payload. All 270 job entries remain `prepared_not_run`. All output content is hash-identified and preparation reruns must reproduce it rather than overwrite divergent artifacts.

### Preflight revealed weak treatment variation

| Model | Selected pairs | Changed normalized histories | Identical-history controls |
|---|---:|---:|---:|
| DeepSeek | 15 | 6 | 9 |
| Gemini | 15 | 0 | 15 |
| GPT-5.6-Luna | 15 | 0 | 15 |

Thus 39 of the 45 pairs have identical inputs across arms. Those pairs measure fresh-run variation or order/provider effects; they cannot show a benefit from correcting an upstream history because nothing was corrected. In this sample the substantive intervention applies only to six DeepSeek cases. **The plan is retained as an inspectable preflight, with no default launcher.**

The 45 actual historical General checkpoints cost **$0.9427226474**. Multiplying each recorded `usage.cost` by six gives a provisional total of **$5.6563358844**: DeepSeek $0.4820, Gemini $4.9010, Luna $0.2733. This is not a full-route extrapolation or a spending guarantee; shortened histories, routing, caching, response length, tools, retries, and future pricing can change cost. Historical failed attempts are excluded from this estimate.

## Offline scan of the 299 common original cases

`scan_general_replay.py` applies the same normalization and frozen approval reconstruction to all **897 model-case pairs** whose General result is available across the three models. It does not generate model responses or modify original checkpoints.

| Model | Histories differing from adjusted reference | Identical histories | Cases differing in disposition | Findings | Actions | Authorization |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek | 63 | 236 | 51 | 43 | 43 | 25 |
| Gemini | 0 | 299 | 0 | 0 | 0 | 0 |
| GPT-5.6-Luna | 33 | 266 | 17 | 19 | 19 | 21 |

Changed-field columns overlap and count cases, not independent errors. Under the frozen General rule, supplying the changed rather than reference history changes the General base disposition in 22 DeepSeek cases and three Luna cases. Other upstream differences may leave General's ultimate disposition unchanged, for example when another blocking finding remains. These are offline rule counterfactuals, not new model performance measurements.

## Targeted exploratory proposal: 270 General executions, estimated $3.06

`general_replay_targeted_plan.json` fixes a new sample before any new model calls. For each model, sample without replacement from the sorted common-case lists using `random.Random("24092026:" + model)`:

- DeepSeek: 15 changed-history cases and five identical-history controls.
- Luna: 15 changed-history cases and five identical-history controls.
- Gemini: five identical-history controls; no changed-history cases exist in this dataset under this normalization.

At three fresh trajectories per arm, this is 120 DeepSeek + 120 Luna + 30 Gemini = **270 General executions**. The selected original General checkpoint costs × six total **$3.061466976**: DeepSeek $0.7834, Gemini $1.8884, Luna $0.3897. The proposed total spending envelope is **$10**, including all attempts and resumptions, with $2 operating headroom. Both the command line and execution function reject a cap above $10. **The targeted proposal is not authorized and has not run.** Its sample is deliberately enriched for historical disagreement; its effect is conditional on that disagreement and must not be reported as a population-average gain. The initial 15-case results would not be pooled with this targeted sample.

## Targets, environment, and analysis boundaries

1. **Common target in both arms.** Reconstruct the canonical General reference after the same validated upstream approvals. Keep those upstream predictions and their genuine original action records fixed for scoring both arms. Fresh General approvals, if any, must be revalidated against that common target. Never import the original General's own approval into a fresh trajectory.
2. **Separate historical approval from mere eligibility.** `validated_conditional_approval` reruns the recorded action under its occurrence-scoped mandate. The effective upstream disposition changes only when that validated action was used by a submitted `GO_WITH_RESERVATIONS`, exactly as in `score_submission`.
3. **General tool feedback is history-dependent.** Frozen `ToolExecutor` derives its General action eligibility/reference from the supplied history. Changing that history can therefore change responses to conditional approval or return-to-design requests even though tool schemas, mandates, facts, and starting state are identical. This is a consequence of the intervention, not a second independently assigned treatment. Preserve these action traces and report when environment-authorized actions differ from validation against the common target.
4. **Report two distinct outcomes.** Primary: agreement and strict protocol success against the common approval-adjusted world reference. Diagnostic: consistency with the supplied history and failures caused by defective handoff content. Do not silently retarget the truth label to each model's own mistaken upstream history; that would hide propagation. Conversely, a General agent that follows a defective input faithfully can fail the common target without making a new local reasoning error.
5. **Fresh independent state.** Every model-case-arm-repeat has a new session and isolated environment directory. No risk cards, requests, General approvals, model conversation, or saved response from another arm/repeat may carry over. Upstream approval records are evaluator inputs, not fresh General state mutations.
6. **Analysis.** Report every arm and trajectory, paired differences by model within the changed-history and control strata, and uncertainty clustered by case. A matching repeat index is not a matching random seed. Do not select the best of three; retain all failures, interrupted attempts, costs, resolved model IDs, and providers. Identical-history controls should show no systematic treatment gain. The small targeted strata do not identify a population-wide effect or a causal difference between model families.

## Tested execution wrapper; explicit approval still required

`prepare_targeted_general_replay.py` creates the targeted plan's own **90 payloads and 45 evaluator-only records**, separate from the initial 15-case preflight. `run_general_replay.py` reuses the frozen `run_occurrence`, `BudgetedClient`, `Usage`, and `CostBudget`. Before executing, it verifies source/dataset fingerprints, every payload, historical checkpoints, reconstructed approvals and common targets. Runtime checks require the prepared model, prompt and initial tools. Reference answers and audit files are never passed to the model.

Generated JSON manifests, selection plans and payloads use canonical JSON hashes with explicit hash scopes, so CRLF versus LF does not change experiment identity. New dataset verification explicitly sorts POSIX-relative paths, avoiding Windows/Linux filename-order differences; each underlying source file and historical checkpoint still has a byte-level SHA-256. Recreating an identical preparation preserves existing file bytes. These changes concern the new replay's portability and leave historical benchmark identities intact.

The default command is a dry run: no network client and no API-key lookup. Only `--execute` reads `OPENROUTER_API_KEY` from the local environment; there is no key argument, and authentication is never included in the saved model payloads. **Publishing the runner does not authorize expenditure.**

Transport is explicitly changed for this new experiment: **zero internal HTTP retries**, identically in both arms. The historical wrapper's hidden transport retries could repeat an uncertain request; the new wrapper records each request attempt, its response and its known usage, and stops after unconfirmed billing. These transport settings must not be described as identical to the old benchmark.

Each response cost is durably appended, including responses associated with failed trajectories. Every previous attempt counts against the same envelope on resume. A native directory lock prevents concurrent runners from spending the same budget. Model mismatch, missing cost, an unresolved in-flight marker, or a paid response with no complete raw trajectory record blocks further requests. Responses remain available for inspection. A raw completed trajectory is persisted **before scoring**; if local scoring fails, a resumed invocation performs scoring offline and does not purchase another response. Valid completed jobs and terminal agent protocol failures are not retried to obtain better answers. A known-cost infrastructure failure can be retried on a later invocation in a fresh environment, retaining every earlier attempt; three such attempts require inspection.

The maximum is $10 across all attempts, with an $8 operating boundary. Because costs become known after a response, this is an admission/accounting limit rather than a provider-enforced hard cap; the $2 margin is retained for in-flight billing. A provider-side key spending limit can additionally constrain charges, but no account setting is modified by the runner.

Validation uses a fake client with the **real frozen agent loop, evidence tools, and scorer**, plus tests for matched common targets, immutable prompts, cost accounting, unknown billing, interruption, paid orphan detection, idempotent completion, and offline scoring recovery. The tests make no external requests and write only temporary test directories.

## Reproduce offline

```powershell
.venv/Scripts/python.exe research/2026-09-followup/prepare_general_replay.py
.venv/Scripts/python.exe research/2026-09-followup/scan_general_replay.py
.venv/Scripts/python.exe research/2026-09-followup/prepare_targeted_general_replay.py
.venv/Scripts/python.exe research/2026-09-followup/run_general_replay.py --cap-usd 10
.venv/Scripts/python.exe -m unittest discover -s research/2026-09-followup -p test_general_replay.py -v
```

The first command writes `experiments/general_replay_prepared_20260924/manifest.json`, `payloads/`, and `evaluator_only/`, plus tracked `general_replay_preflight.json`. The second writes tracked `general_replay_population_scan.json` and `general_replay_targeted_plan.json`. Targeted executable payloads are stored in `experiments/general_replay_targeted_prepared_20260924`; real execution results, if later authorized, go to `experiments/general_replay_targeted_results_20260924`. All commands require the frozen source and original released dataset/checkpoints at the documented paths. Preparation records and reference targets are never supplied as model tools or public evidence.

**Only after the user authorizes the new $10 envelope**, with the key configured locally in the same terminal:

```powershell
.venv/Scripts/python.exe research/2026-09-followup/run_general_replay.py --execute --cap-usd 10
```

Rerunning that command resumes the same experiment and includes all prior ledger costs. It stops instead of silently retrying if an earlier request's billing or completion is uncertain.
