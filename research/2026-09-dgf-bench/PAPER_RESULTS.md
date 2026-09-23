# DGF-Bench experiment results

Generated: 2026-09-23T12:12:28.802006+00:00

Scoring: DGF-decision-v8.2-authorized-review

## Overall results

| Model | Cases | Agent failures | Gate attempt | Gate CSR (95% CI) | Route decision complete (95% CI) | Critical misses | False approvals | Truncated | Model mismatch | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4.1-flash` | 300 | 0 | 100.0% | 74.2% [71.9%, 76.5%] | 24.7% [20.1%, 29.8%] | 1 | 1 | 2 | 0 | 10.0938 |
| `google/gemini-3.8-flash` | 299 | 0 | 100.0% | 95.0% [93.9%, 96.0%] | 76.9% [71.8%, 81.3%] | 0 | 0 | 14 | 0 | 71.8755 |
| `openai/gpt-5.6-luna` | 300 | 0 | 100.0% | 83.3% [81.3%, 85.2%] | 42.3% [36.9%, 48.0%] | 3 | 1 | 0 | 0 | 5.0465 |

## Per-gate CSR

| Model | Gate | Expected | Attempted | Attempt rate | CSR (95% CI) | Decision* | Findings F1* | Actions F1* | Evidence* | Auth* |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4.1-flash` | architecture | 200 | 200 | 100.0% | 75.0% [68.5%, 81.0%] | 99.5% | 0.991 | 0.991 | 0.832 | 99.0% |
| `deepseek/deepseek-v4.1-flash` | compliance | 200 | 200 | 100.0% | 88.0% [83.0%, 92.5%] | 98.0% | 0.982 | 0.982 | 0.925 | 99.5% |
| `deepseek/deepseek-v4.1-flash` | general | 300 | 300 | 100.0% | 68.7% [63.7%, 73.7%] | 92.3% | 0.923 | 0.923 | 0.803 | 97.7% |
| `deepseek/deepseek-v4.1-flash` | it | 300 | 300 | 100.0% | 87.0% [83.7%, 90.3%] | 94.3% | 0.958 | 0.958 | 0.928 | 96.3% |
| `deepseek/deepseek-v4.1-flash` | legal | 200 | 200 | 100.0% | 68.5% [62.0%, 75.0%] | 95.5% | 0.990 | 0.990 | 0.836 | 97.0% |
| `deepseek/deepseek-v4.1-flash` | procurement | 100 | 100 | 100.0% | 43.0% [34.0%, 53.0%] | 97.0% | 0.980 | 0.980 | 0.474 | 98.0% |
| `deepseek/deepseek-v4.1-flash` | security | 300 | 300 | 100.0% | 72.3% [67.7%, 77.3%] | 93.0% | 0.962 | 0.962 | 0.832 | 98.7% |
| `deepseek/deepseek-v4.1-flash` | tech_readiness | 100 | 100 | 100.0% | 71.0% [62.0%, 80.0%] | 97.0% | 0.998 | 0.998 | 0.773 | 99.0% |
| `google/gemini-3.8-flash` | architecture | 199 | 199 | 100.0% | 85.4% [80.4%, 89.9%] | 100.0% | 1.000 | 1.000 | 0.902 | 100.0% |
| `google/gemini-3.8-flash` | compliance | 199 | 199 | 100.0% | 100.0% [98.1%, 100.0%] | 100.0% | 1.000 | 1.000 | 1.000 | 100.0% |
| `google/gemini-3.8-flash` | general | 299 | 299 | 100.0% | 88.0% [84.3%, 91.3%] | 100.0% | 1.000 | 1.000 | 0.925 | 100.0% |
| `google/gemini-3.8-flash` | it | 299 | 299 | 100.0% | 100.0% [98.7%, 100.0%] | 100.0% | 1.000 | 1.000 | 1.000 | 100.0% |
| `google/gemini-3.8-flash` | legal | 199 | 199 | 100.0% | 99.5% [98.5%, 100.0%] | 100.0% | 1.000 | 1.000 | 0.995 | 100.0% |
| `google/gemini-3.8-flash` | procurement | 100 | 100 | 100.0% | 96.0% [92.0%, 99.0%] | 100.0% | 1.000 | 1.000 | 0.968 | 100.0% |
| `google/gemini-3.8-flash` | security | 299 | 299 | 100.0% | 98.7% [97.3%, 99.7%] | 100.0% | 1.000 | 1.000 | 0.989 | 100.0% |
| `google/gemini-3.8-flash` | tech_readiness | 100 | 100 | 100.0% | 89.0% [83.0%, 95.0%] | 100.0% | 1.000 | 1.000 | 0.967 | 100.0% |
| `openai/gpt-5.6-luna` | architecture | 200 | 200 | 100.0% | 89.5% [85.0%, 93.5%] | 99.5% | 0.995 | 0.995 | 0.966 | 98.5% |
| `openai/gpt-5.6-luna` | compliance | 200 | 200 | 100.0% | 96.0% [93.0%, 98.5%] | 99.5% | 0.992 | 0.992 | 0.978 | 99.0% |
| `openai/gpt-5.6-luna` | general | 300 | 300 | 100.0% | 61.7% [56.0%, 67.0%] | 95.3% | 0.980 | 0.980 | 0.741 | 96.7% |
| `openai/gpt-5.6-luna` | it | 300 | 300 | 100.0% | 97.7% [96.0%, 99.3%] | 99.3% | 0.995 | 0.995 | 0.997 | 98.7% |
| `openai/gpt-5.6-luna` | legal | 200 | 200 | 100.0% | 80.5% [75.0%, 86.0%] | 96.5% | 0.983 | 0.983 | 0.895 | 97.0% |
| `openai/gpt-5.6-luna` | procurement | 100 | 100 | 100.0% | 33.0% [24.0%, 43.0%] | 96.0% | 0.997 | 0.997 | 0.341 | 96.0% |
| `openai/gpt-5.6-luna` | security | 300 | 300 | 100.0% | 92.0% [89.0%, 95.0%] | 99.7% | 0.992 | 0.992 | 0.967 | 99.0% |
| `openai/gpt-5.6-luna` | tech_readiness | 100 | 100 | 100.0% | 97.0% [93.0%, 100.0%] | 98.0% | 0.989 | 0.989 | 0.998 | 98.0% |

## Interpretation note

Gate intervals resample whole cases within routes; boundary or degenerate intervals use a descriptive Wilson fallback with the number of cases. Route intervals use case-level Wilson bounds. These descriptive intervals do not correct protocol bias.
CSR scores decisions, proposed actions and lexical evidence provenance, not completed remediation. Costs include excluded runs; unknown costs are reported separately.
These results measure performance on the declared synthetic DGF-Bench population. Agent-protocol failures are retained as failed decision rather than dropped; infrastructure/budget failures are excluded and reported separately. Per-gate component metrics marked * are conditional on the gate having been attempted. These results do not by themselves demonstrate autonomous real-world enterprise governance or prove the paper's universal long-horizon claim.


## Availability and billing

| Model | Planned cases | Excluded | Unscheduled | Availability | Known cost, all runs (USD) | Responses with unknown cost |
|---|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 300 | 0 | 0 | 100.0% | 10.0938 | 0 |
| google/gemini-3.8-flash | 300 | 1 | 0 | 99.7% | 71.8755 | 0 |
| openai/gpt-5.6-luna | 300 | 0 | 0 | 100.0% | 5.0465 | 0 |

## Matched cases across all models

| Model | Common cases | Gate CSR | False approvals |
|---|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 299 | 74.1% | 1 |
| google/gemini-3.8-flash | 299 | 95.0% | 0 |
| openai/gpt-5.6-luna | 299 | 83.2% | 1 |