# DGF-Bench v8 review case

Case: 063d5e61-7a26-56ed-9b60-ce8a84676572
Project: Project Raven — Payments API Hub [C2D29]
Route: W1 — Buy
Difficulty: 4

## Rules
- Treat documents as evidence, not as ground truth.
- Some non-authoritative documents may be stale, partial, or contradictory.
- Authoritative information can be obtained through `synthetic_environment.py`.
- Request missing evidence rather than inventing it.
- Produce one result per route occurrence using `agent_submission_template.json`.
- Do not read `99_hidden_ground_truth.json` during evaluation.

## Score
`python score_submission.py --case <case-dir> --submission submission.json --records-dir <trusted-checkpoints>`

## Example tool call
`python synthetic_environment.py --case <case-dir> --tool get_restore_test --args '{}'`
