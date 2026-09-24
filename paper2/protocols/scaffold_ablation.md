# Matched-information scaffold ablations

Status: **design and offline sufficiency preflight; no paid ablation collected**. This is separate from the completed 135-run repetition study. The original benchmark and its primary scores remain frozen.

## Questions and conditions

1. Does executable policy code improve rule application relative to semantically equivalent prose?
2. What additional errors and costs arise when a system must recover facts from source documents and operational records?
3. Holding information and authority constant, how do agent handoffs affect the final General review?

The first two questions use a paired 2 × 2 design:

| Condition | Policy available | Evidence available |
|---|---|---|
| A | Executable definitions | Authoritative structured snapshots |
| B | Equivalent prose, including thresholds, priorities and exceptions | Same snapshots |
| C | Same executable definitions | Documents and operational records containing the necessary facts |
| D | Same prose as B | Same documents and records as C |

All cells share the same case, output schema, authority rules, tools, context budget, inference settings, stopping rules, and versioned evidence acceptance criterion. Model access to Python execution must be identical across cells; policy representation is the manipulated variable. Policy prose is checked clause by clause against the executable version before collection. Findings catalogs must not restore executable predicates in prose-only cells.

## Executed preflight and blockers

[The offline counterexample](../../research/2026-09-followup/document_ablation_preflight.json) changes only the selected vendor's due-diligence status. All 26 generated Word documents retain identical paragraph/table text, but the required Procurement disposition changes from GO to REWORK. The distinguishing value is in a CSV and the structured snapshot. Thus a **Word-only** condition is underdetermined on this example. This does not show that documents plus operational records are insufficient.

The frozen scorer also requires finding support to cite REVIEW_FACTS. Removing that source while keeping the strict endpoint would mechanically fail evidence conformity. Before any paid calls:

- Map every policy predicate, exception and approval input to at least one visible source field or span in C/D. Preserve timestamps, units, entity identity, and missing/unknown states. Test counterfactual value changes across every gate, not only fields observed in historical failures.
- Prove that source collection C/D and snapshots A/B determine equivalent facts on the scored cases. If a case is intentionally underdetermined, define justified abstention in every relevant condition before collection; do not score a guessed hidden value as the only correct answer.
- Introduce one common evidence interface: source identifier, observed JSON path or document span, and a verifiable value. Retain access logs. Score access, value fidelity, premise coverage, policy application, and authority separately. Validate conversions against the original frozen records without overwriting their scores.
- Prevent alternate tools, search, document previews, filenames, metadata, or catalogs from leaking hidden snapshots or answers in C/D. Verify all tool surfaces with offline access tests.
- Verify policy equivalence and evidence sufficiency with explicit clause mappings, counterfactual tests, and held-out checks. This establishes internal consistency; independent professional validity remains outside the current study.

These are release criteria, not completed results. Until they pass, launching C/D would confound extraction quality, missing information, and an impossible citation contract.

## Additional offline checks now completed

The [300-case source inventory](../../research/2026-09-followup/source_coverage_audit.md) identifies 76 static case fields, with 72 explicit decoders. It distinguishes matching sources, conflicting sources, and physical/phase/gate availability. Its static counts include inactive branches and output metadata; they are not impossibility rates. Two additional counterexamples show that `it.duplicate_capability` and `compliance.audit_trail` can change a decision while all non-snapshot generated artifacts remain identical.

[Targeted generation extensions](../../research/2026-09-followup/source_record_extensions.py) add CSV records for these two omitted fields to **three new development dossiers**, not a held-out sample. [The source-location prototype](../../research/2026-09-followup/SOURCE_LOCATION_CONTRACT.md) copies values from immutable observed sources using pointers/spans; it is not integrated into a paid experiment or a semantic scorer.

A specific access-path check is required: the frozen `request_evidence` tool returns the gate's full factual snapshot even when a non-snapshot document is requested. Other domain tools expose canonical fields too. C/D must use an audited source-only tool adapter, not simply hide files or remove `read_evidence(REVIEW_FACTS)`. The new prototype does not yet implement that adapter.

## Sampling, comparison, and analysis

Use held-out case seeds, fixed route strata, all three named endpoints, and three trajectories per case-condition. Fix the sample and cost ceiling before collection, without selecting on model success. Historical failures may inform development checks but must not serve as the held-out evaluation. Preserve all paid attempts, error checkpoints, provider identifiers, and costs. Do not select the best repeat.

Report paired changes in decision accuracy, false approvals, missed critical findings, each evidence component, complete-route success, abstention, tool use, and cost. Bootstrap whole cases within route, retaining every condition and repeat together. Report conditional-approval behavior and both initial- and effective-reference agreement. Do not compare a new evidence metric numerically with the old primary endpoint as if only the model had changed.

Include the direct rule engine in A. For C, include an extraction-plus-rule system with the same visible inputs; measure extraction error separately. Cost the document/policy preparation and human checking as well as inference. A deterministic parser must not receive hidden canonical truth at inference time.

## General-gate handoff intervention

Replay the same final gate using (i) its saved agent history and (ii) reference history adjusted to preserve the **same validated upstream conditional approvals**. Keep dossier, prompts, mandate, available evidence, tools, and resource limits otherwise identical. Run paired repeated trajectories. A reference history that removes lawful upstream approvals changes authority as well as error content and is not the intended intervention. A no-history arm is admissible only if missing mandatory evidence has a specified, fair target.

## Cost and authorization

No new model calls are authorized by this protocol. The completed repetitions cost $12.5598870228 for 135 full-route runs; that is a historical observation, not a quote for longer document inputs. Once the offline release criteria pass, freeze the manifest, count the resulting model-case-condition trajectories and gates, estimate tokens from actual prompts and tool payloads with current provider prices, and submit a concrete capped budget. Existing repetition authorization must not be reused for this distinct experiment.

Jeremy Canale · 24 September 2026
