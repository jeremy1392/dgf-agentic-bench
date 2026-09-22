# DGF-Bench v6 synthetic case

Case: 90534c60-1b6b-5ed2-8680-3b8688f20bc9
Project: Gaia Acquisition Integration — Cloud Landing Zone Extension [AB974]
Route: W2 — Integrate
Difficulty: 3

## Rules
- Treat documents as evidence, not as ground truth.
- Some non-authoritative documents may be stale, partial, or contradictory.
- Authoritative information can be obtained through `synthetic_environment.py`.
- Request missing evidence rather than inventing it.
- Produce one result per route occurrence using `agent_submission_template.json`.
- Do not read `99_hidden_ground_truth.json` during evaluation.

## Score
`python score_submission.py --case <case-dir> --submission submission.json`

## Example tool call
`python synthetic_environment.py --case <case-dir> --tool get_restore_test --args '{}'`
