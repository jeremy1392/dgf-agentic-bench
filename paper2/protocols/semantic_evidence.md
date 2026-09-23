# Proposed independent semantic evidence audit

**Status: independent semantic adjudication remains unperformed.** A separate automated structural audit has now covered all 85 Gemini failed gates: 69 same-object matches, 9 flattened cross-object cases, and 7 missing required tool reads. See `research/2026-09-followup/`; those are not expert labels or semantic pass rates. The strict lexical metric and published rates remain frozen.

## Unit and labels

Unit: one required finding, its submitted factual claim, cited evidence, and the evidence actually observed before submission. Preserve case/model/gate/finding IDs and original trace paths.

For each item record separately:

- Observed source: was the source available and read before submission?
- Citation identity: can the cited passage be located in that source?
- Entailment: does the passage support the factual claim with scope, date, and qualifications preserved?
- Policy support: does that fact support the policy finding under the stated rule?

Each label is `supported`, `unsupported`, or `ambiguous`, with a written reason. Classify representation-only differences, unsupported facts, missing sources, contradictions, and policy ambiguity separately. A hidden answer-key fact cannot repair the agent's missing observation. A reordered JSON excerpt can be semantically faithful while still failing the original lexical rule.

## Sampling and adjudication

Include all strict evidence failures and a probability sample of passing items stratified by model, route, and gate. Record inclusion probabilities and apply design weights to population estimates. A complete-route semantic estimate requires all required evidence items on the sampled routes, not just previously failed excerpts.

Two independent domain-qualified adjudicators label each item; mask model and original pass/fail outcome where feasible. A third resolves disagreements using a frozen rubric. Publish raw agreement, a chance-corrected agreement measure, pre-adjudication labels, resolved labels, and disagreement categories. Develop the rubric on separate examples and evaluate on held-out items. An LLM judge is not an independent validation unless checked against human labels.

## Analysis boundary

This audit is post-hoc because the existing outputs have been examined. Publish lexical and semantic scores side by side and retain the original endpoint. Report how many failures are harmless representation issues, unsupported claims, and ambiguous cases; do not infer the distribution from one example. No semantics-based score should be inserted into the current paper until actual adjudication exists.
