# DGF-Bench experiment results

Generated: 2026-09-22T16:46:45.372910+00:00

## Overall results

| Model | Cases | Agent failures | Gate attempt | Gate CSR (95% CI) | Route decision complete (95% CI) | Critical misses | False approvals | Truncated | Model mismatch | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4.1-flash` | 15 | 0 | 100.0% | 27.1% [17.6%, 37.6%] | 0.0% [0.0%, 20.4%] | 0 | 0 | 0 | 0 | 0.2248 |
| `google/gemini-3.8-flash` | 15 | 0 | 100.0% | 72.9% [61.2%, 84.7%] | 33.3% [15.2%, 58.3%] | 0 | 7 | 1 | 0 | 3.9759 |
| `z-ai/glm-5.3-flash` | 10 | 0 | 100.0% | 37.5% [23.2%, 48.2%] | 0.0% [0.0%, 27.8%] | 0 | 0 | 0 | 0 | 0.8027 |

## Per-gate CSR

| Model | Gate | Expected | Attempted | Attempt rate | CSR (95% CI) | Decision* | Findings F1* | Actions F1* | Evidence* | Auth* |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4.1-flash` | architecture | 10 | 10 | 100.0% | 10.0% [0.0%, 30.0%] | 100.0% | 1.000 | 1.000 | 0.200 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | compliance | 10 | 10 | 100.0% | 30.0% [10.0%, 50.0%] | 100.0% | 1.000 | 1.000 | 0.550 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | general | 15 | 15 | 100.0% | 0.0% [0.0%, 20.4%] | 100.0% | 1.000 | 1.000 | 0.122 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | it | 15 | 15 | 100.0% | 60.0% [33.3%, 86.7%] | 100.0% | 1.000 | 1.000 | 0.711 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | legal | 10 | 10 | 100.0% | 70.0% [40.0%, 100.0%] | 100.0% | 1.000 | 1.000 | 0.733 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | procurement | 5 | 5 | 100.0% | 20.0% [0.0%, 60.0%] | 100.0% | 1.000 | 1.000 | 0.200 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | security | 15 | 15 | 100.0% | 13.3% [0.0%, 33.3%] | 100.0% | 0.990 | 0.990 | 0.189 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | tech_readiness | 5 | 5 | 100.0% | 0.0% [0.0%, 43.4%] | 100.0% | 1.000 | 1.000 | 0.413 | 100.0% |
| `google/gemini-3.8-flash` | architecture | 10 | 10 | 100.0% | 70.0% [50.0%, 90.0%] | 100.0% | 1.000 | 1.000 | 0.767 | 100.0% |
| `google/gemini-3.8-flash` | compliance | 10 | 10 | 100.0% | 80.0% [50.0%, 100.0%] | 100.0% | 1.000 | 1.000 | 0.867 | 100.0% |
| `google/gemini-3.8-flash` | general | 15 | 15 | 100.0% | 66.7% [40.0%, 86.7%] | 100.0% | 1.000 | 1.000 | 0.800 | 100.0% |
| `google/gemini-3.8-flash` | it | 15 | 15 | 100.0% | 60.0% [33.3%, 86.7%] | 73.3% | 1.000 | 1.000 | 0.933 | 73.3% |
| `google/gemini-3.8-flash` | legal | 10 | 10 | 100.0% | 80.0% [60.0%, 100.0%] | 80.0% | 1.000 | 1.000 | 1.000 | 80.0% |
| `google/gemini-3.8-flash` | procurement | 5 | 5 | 100.0% | 60.0% [20.0%, 100.0%] | 100.0% | 1.000 | 1.000 | 0.600 | 100.0% |
| `google/gemini-3.8-flash` | security | 15 | 15 | 100.0% | 93.3% [80.0%, 100.0%] | 100.0% | 1.000 | 1.000 | 0.967 | 100.0% |
| `google/gemini-3.8-flash` | tech_readiness | 5 | 5 | 100.0% | 60.0% [20.0%, 100.0%] | 80.0% | 1.000 | 1.000 | 0.933 | 80.0% |
| `z-ai/glm-5.3-flash` | architecture | 7 | 7 | 100.0% | 57.1% [57.1%, 57.1%] | 100.0% | 1.000 | 1.000 | 0.762 | 100.0% |
| `z-ai/glm-5.3-flash` | compliance | 6 | 6 | 100.0% | 16.7% [0.0%, 50.0%] | 100.0% | 1.000 | 1.000 | 0.417 | 100.0% |
| `z-ai/glm-5.3-flash` | general | 10 | 10 | 100.0% | 0.0% [0.0%, 27.8%] | 100.0% | 1.000 | 1.000 | 0.100 | 100.0% |
| `z-ai/glm-5.3-flash` | it | 10 | 10 | 100.0% | 70.0% [40.0%, 90.0%] | 100.0% | 1.000 | 1.000 | 0.700 | 100.0% |
| `z-ai/glm-5.3-flash` | legal | 6 | 6 | 100.0% | 66.7% [33.3%, 100.0%] | 100.0% | 1.000 | 1.000 | 0.722 | 100.0% |
| `z-ai/glm-5.3-flash` | procurement | 3 | 3 | 100.0% | 33.3% [0.0%, 100.0%] | 100.0% | 1.000 | 1.000 | 0.333 | 100.0% |
| `z-ai/glm-5.3-flash` | security | 10 | 10 | 100.0% | 30.0% [10.0%, 50.0%] | 100.0% | 1.000 | 1.000 | 0.517 | 100.0% |
| `z-ai/glm-5.3-flash` | tech_readiness | 4 | 4 | 100.0% | 25.0% [0.0%, 75.0%] | 100.0% | 1.000 | 1.000 | 0.533 | 100.0% |

## Interpretation note

Gate intervals resample whole cases within routes; all-zero/all-one boundaries use Wilson bounds with the number of cases. Route intervals use case-level Wilson bounds. These descriptive intervals do not correct protocol bias.
CSR scores decisions, proposed actions and lexical evidence provenance, not completed remediation. Costs include excluded runs; unknown costs are reported separately.
These results measure performance on the declared synthetic DGF-Bench population. Agent-protocol failures are retained as failed decision rather than dropped; infrastructure/budget failures are excluded and reported separately. Per-gate component metrics marked * are conditional on the gate having been attempted. These results do not by themselves demonstrate autonomous real-world enterprise governance or prove the paper's universal long-horizon claim.


## Availability and billing

| Model | Planned cases | Excluded | Unscheduled | Availability | Known cost, all runs (USD) | Responses with unknown cost |
|---|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 15 | 0 | 0 | 100.0% | 0.2248 | 0 |
| google/gemini-3.8-flash | 15 | 0 | 0 | 100.0% | 3.9759 | 0 |
| z-ai/glm-5.3-flash | 15 | 5 | 0 | 66.7% | 0.8027 | 0 |

## Matched cases across all models

| Model | Common cases | Gate CSR | False approvals |
|---|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 10 | 23.2% | 0 |
| google/gemini-3.8-flash | 10 | 69.6% | 6 |
| z-ai/glm-5.3-flash | 10 | 37.5% | 0 |