# DGF-Bench v6 Benchmark Design

## 1. Evaluation target

DGF-Bench measures complete gate execution: evidence acquisition, reconciliation, evaluation, disposition, action production, authorization handling and handoff.

It is not designed as a document-summary benchmark.

## 2. Canonical truth vs evidence

The canonical state is generated once. Every evidence object has:

- evidence ID
- version
- age
- authoritative/non-authoritative status
- gate consumers
- availability by phase
- hidden evidence mode

Non-authoritative evidence may be truthful, stale, partial or conflicting. Authoritative evidence may be temporarily unavailable. This prevents a model from treating every PDF or comment as ground truth.

## 3. Route semantics

Buy, Integrate and Build are distinct transformations. The full lifecycle adds repeated gate occurrences over five project phases. Handoff contracts specify the fields that should flow downstream.

## 4. Deterministic reference evaluator

Reference decisions are functions of canonical facts. A contradiction in a document does not change the correct answer; it changes what the agent must investigate.

## 5. Failure-sensitive metrics

A high aggregate score cannot hide consequential failures. Reports include:

- critical finding misses
- false approvals of NO_GO / SUSPENSION / REWORK cases
- evidence-reference fidelity
- authorization-state errors

## 6. Interaction

The synthetic tool environment exposes authoritative enterprise systems. Phase-aware mode blocks future evidence. Tool calls are written to `tool_trace.jsonl` for later analysis of investigation cost and strategy.

## 7. Research extensions

The current implementation can support future metrics for:

- tool-call count / cost
- time-to-decision
- human residual minutes
- exception routing
- evidence-request efficiency
- cross-gate handoff reuse
- complete substitution rate
- robustness to prompt injection inside non-authoritative evidence
