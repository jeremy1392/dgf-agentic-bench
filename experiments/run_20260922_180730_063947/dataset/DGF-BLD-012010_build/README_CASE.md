# DGF-Bench v8 review case

Case: d879a593-18bc-5aaf-a8b6-c65ea6e0a91f
Project: Project Falcon — Observability Platform [83985]
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
