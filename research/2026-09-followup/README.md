# Follow-up controls and evidence audit

This directory adds **executed offline measurements** to the September 2026 experiment. It does not replace the original model results or claim independent expert adjudication.

## Deterministic rules control: completed

| Outcome | Result |
|---|---:|
| Dossiers | 300 |
| Strict gate successes | 1,700 / 1,700 |
| Complete routes | 300 / 300 |
| False approvals / critical misses | 0 / 0 |
| Model API cost | $0 |

The comparator executes the rule functions supplied in the agent-visible gate contracts on the public REVIEW_FACTS snapshots. It implements the public priority/authorization rules, retains the permitted base disposition (no optional risk-acceptance action), quotes complete observed JSON snapshots, and propagates its own prior decisions. It has no model output-token limit; the protocol has no independent quote-length cap. Local compute and implementation work are not priced.

Generation rejects hidden-reference reads and does not import the evaluator or scorer. Predictions and tool observations are saved before a separate scoring process reads evaluator references. **This is a scaffold-sufficiency control:** because the public rules derive from the evaluator's rules, it does not independently validate enterprise policy. It demonstrates that a language model is unnecessary for full success on this scaffolded contract.

[Summary](baseline_summary.json) · [Public input read log and policy hashes](baseline_generation.json) · [All 300 submissions, observation records, and scores](baseline/) · [Script](rules_baseline.py)

## Gemini structural evidence audit: completed

All **85 strict-failure gates** were audited. They contain **84 flagged finding-support items**, because multiple findings can fail at one gate and citation-only failures can contain no flagged finding.

| Gate category | Gates | Interpretation |
|---|---:|---|
| Every flagged excerpt matches an observed JSON object after normalization | 69 | 75 finding items preserve checked field values, ignoring key order and numeric serialization. |
| Flattened cross-object excerpts | 9 | 9 items join values found at different object paths; the combined quoted object was not observed. |
| Missing required evidence-tool read | 7 | UPSTREAM_DECISIONS is cited without a corresponding read event. Prior reviews were also present in the prompt, so this does not establish that the model lacked the information. |

The original strict scores are unchanged. This is structural provenance analysis, **not semantic entailment or two-expert adjudication**. No new global semantic success rate is reported. Tests reject wrong values, numeric-prefix matches, boolean/number confusion, duplicate keys, and cross-object joins as same-object evidence.

[All gate/item classifications, excerpts, observed objects, and trace paths](gemini_evidence_audit.json) · [Audit script](audit_evidence.py)

## All-model audit and document preflight: completed

The audit now includes all **690 evidence-failed gates** across DeepSeek, Gemini, and Luna. The [full report](ALL_MODELS_AUDIT.md) adds a declared lexical-or-structural sensitivity endpoint, Procurement diagnostics, decision confusion matrices, and initial-versus-effective reference agreement. Original primary scores remain unchanged.

The [complete offline-audit archive](https://github.com/jeremy1392/dgf-agentic-bench/releases/download/dgf-bench-300-20260923/dgf-bench-evidence-audit-20260924.zip) includes all artifacts from both counterexample variants, including 52 Word files (26 per variant), alongside the audit records and scripts. [Inventory and scope](evidence_audit_archive_manifest.json) · [SHA-256](evidence-audit-SHA256SUMS.txt).

The [document-only counterexample](document_ablation_preflight.json) produces identical text in 26 Word documents but different required Procurement decisions. The [ablation protocol](../../paper2/protocols/scaffold_ablation.md) specifies matched information and a common evidence contract before further paid calls.

## Repetitions: completed on 24 September 2026

The [fixed plan](repetition_plan.json) samples five dossiers per route without replacement using seed 23092026, then schedules three fresh trajectories for each of three models: **135 model-case runs**. Original selected checkpoint costs imply approximately **$12.72**, not a guaranteed price. The user initially authorized a $20 envelope, then raised the total authorization to **$50** to finish the same repetitions. Prior spending remains included. The user launches from the terminal containing their API key.

The plan's `prepared_not_run` value records its preparation status and is retained as historical metadata. Final counts are published in [repetition_results.json](repetition_results.json); [REPETITION_RESULTS.md](REPETITION_RESULTS.md) adds the audited statistics, case-cluster intervals, and archive links.

From the repository root:

```powershell
python research/2026-09-followup/run_repetitions.py --execute --cap-usd 50
```

The wrapper verifies the frozen benchmark source fingerprint, copies and byte-checks the selected dossiers, and writes separate `repeat_1`, `repeat_2`, and `repeat_3` outputs under `experiments/followup_repetitions_20260923/`. Resume retains compatible checkpoints within each repeat. Recorded expenditure from earlier repeats reduces the remaining common envelope. The runner reserves $2 headroom below the requested cap ($48 operating ceiling for `--cap-usd 50`) because the historical provider client knows billed cost only after a response; an independently limited API key provides a stronger provider-side limit. The default remains $20 unless a higher cap is explicitly supplied. The OpenRouter key limit is separate and must allow further calls. Unknown billing stops further execution. Never publish the API key.

`--execute` is required for any inference. Without it, the command only prepares and verifies the dataset. The key can be provided through OPENROUTER_API_KEY in the process, Windows user environment, or the ignored repository `.env` file. The wrapper never prints it or accepts it in command-line arguments.

The completed run has **135/135 evaluable outcomes**, **765 gates**, and **$12.5598870228** in recorded costs. All dossiers pass on all three trajectories for 9/15 Gemini cases, 3/15 Luna cases, and 0/15 DeepSeek cases. Descriptive counts can be refreshed with:

```powershell
python research/2026-09-followup/summarize_repetitions.py
```

Run `python research/2026-09-followup/analyze_repetitions.py` to regenerate the audited analysis and 10,000-draw stratified case bootstrap. For archive reproduction, pass `--run-dir PATH_TO_EXTRACTED_RUN` and optionally `--output-dir PATH_TO_OUTPUT`. All trajectories and infrastructure failures are reported; there is no best-of-three selection. A returned `not_complete` status must not be described as completed replication. Human baselines and independent semantic adjudication remain unperformed.

## Offline reproduction

Defaults use the already verified extraction of the immutable 300-case release at `experiments/reproduction_check_20260923/verified_inputs/benchmark_source`, plus the original prepared dataset. See the [original archive verification instructions](../2026-09-dgf-bench/README.md). The rules script accepts `--source`, `--dataset`, and `--output` overrides for another extraction location.

```powershell
python research/2026-09-followup/rules_baseline.py generate
python research/2026-09-followup/rules_baseline.py score
python research/2026-09-followup/audit_evidence.py
python research/2026-09-followup/audit_all_models.py
python research/2026-09-followup/check_document_ablation.py
```

Author: [Jeremy Canale](https://www.jeremycanale.com) · contact@jeremycanale.com
