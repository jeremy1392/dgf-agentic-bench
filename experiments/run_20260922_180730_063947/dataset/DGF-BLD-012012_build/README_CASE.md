# DGF-Bench v8 review case

Case: d3d68264-320d-50e7-bcd1-79409c4b2f8d
Project: Project Titan — Payments API Hub [C2052]
Route: W3 — Build
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
