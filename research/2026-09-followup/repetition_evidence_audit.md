# Repetition evidence sensitivity: lexical or same-object structural support

Offline audit of all 135 completed model-case trajectories (765 gates), using the unchanged `inspect` function in `audit_all_models.py`. The original strict outcomes remain the primary results. This post-hoc sensitivity is applied to every completed repetition; no best-of-three selection and no new model calls.

| Model | Strict gates | Lexical-or-structural gates | Strict routes | Lexical-or-structural routes | All three strict routes | All three lexical-or-structural routes |
|---|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 187/255 (73.33%) | 195/255 (76.47%) | 11/45 (24.44%) | 11/45 (24.44%) | 0/15 | 0/15 |
| google/gemini-3.8-flash | 245/255 (96.08%) | 249/255 (97.65%) | 35/45 (77.78%) | 39/45 (86.67%) | 9/15 | 12/15 |
| openai/gpt-5.6-luna | 211/255 (82.75%) | 217/255 (85.10%) | 19/45 (42.22%) | 23/45 (51.11%) | 3/15 | 5/15 |

| Model | Repeat | Strict gates | Lexical-or-structural gates | Strict routes | Lexical-or-structural routes |
|---|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 1 | 63/85 | 66/85 | 3/15 | 3/15 |
| deepseek/deepseek-v4.1-flash | 2 | 64/85 | 66/85 | 4/15 | 4/15 |
| deepseek/deepseek-v4.1-flash | 3 | 60/85 | 63/85 | 4/15 | 4/15 |
| google/gemini-3.8-flash | 1 | 82/85 | 83/85 | 12/15 | 13/15 |
| google/gemini-3.8-flash | 2 | 82/85 | 83/85 | 12/15 | 13/15 |
| google/gemini-3.8-flash | 3 | 81/85 | 83/85 | 11/15 | 13/15 |
| openai/gpt-5.6-luna | 1 | 73/85 | 75/85 | 8/15 | 10/15 |
| openai/gpt-5.6-luna | 2 | 71/85 | 74/85 | 7/15 | 8/15 |
| openai/gpt-5.6-luna | 3 | 67/85 | 68/85 | 4/15 | 5/15 |

| Model | Gates with evidence failure | Evidence-only failures | Same-object support for every failed item | Citation defect | Cross-object excerpt | Unresolved support |
|---|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 59 | 56 | 8 | 25 | 0 | 26 |
| google/gemini-3.8-flash | 10 | 10 | 4 | 3 | 3 | 0 |
| openai/gpt-5.6-luna | 36 | 35 | 6 | 0 | 9 | 21 |

The category columns partition all gates with an evidence failure, including gates that also fail another component. A structurally recovered evidence component raises the relaxed gate score only when every unchanged non-evidence component also passes. Detailed category counts for evidence-only failures and individual finding items are in the summary JSON.

## Method and interpretation

An original strict success remains accepted. Otherwise, every unchanged decision, finding, action and authorization component must pass; cited evidence must have an authentic observed tool result; and every originally failed finding excerpt must parse as an exact field/value subset within a single observed source object, with at least one rule-relevant field. Key order and numeric serialization may differ. Wrong values, invented reads, and joins across different objects are not repaired or promoted.

This is lexical-or-structural provenance sensitivity, not semantic entailment, complete coverage of a rule’s premises, or independent human adjudication. A remaining structural failure need not be semantically wrong. An accepted subset need not establish the entire finding. Original lexical successes are retained without a new semantic audit.

The 15 dossiers were selected for the original repetition plan (five per route) and are reused across the three trajectories. These observations are not a new representative dataset and the 765 gates are not independent samples. All-three case success requires the complete route to pass on each of the three trajectories.

Infrastructure resumes retain the completed prefix of the same trajectory. Two Gemini model-case runs retained seven gates in total; these are included exactly once in their final trajectory, with prefix flags in the detailed JSON. Failed attempts are not extra completed trajectories. This audit neither replays nor rescores those prefixes.

## Reproduce

Run `python research/2026-09-followup/repeat_evidence_audit.py` from the repository root. `--run-dir` accepts an extracted repetition archive; `--dataset` optionally points to its preserved dataset. The original benchmark source expected by `audit_evidence.py` must be installed at its documented frozen-source location.

The script checks all 135 planned combinations, the three equal protocol identities, the published strict gate/route/all-three counts, complete and unique occurrence sets, and read-only score/trace hashes. `repetition_evidence_items.json` contains the failed gates and their original excerpts; `repetition_evidence_summary.json` contains model, repeat and per-case outcomes plus input provenance.
