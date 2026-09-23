# September 22 pilot: complete original experiment

**[Browse all original files](../../experiments/run_20260922_180730_063947/)** from `run_20260922_180730_063947`. This historical pilot is separate from the [300-project experiment](../2026-09-dgf-bench/).

All 2,214 files (28,704,405 bytes) are committed directly to this repository, with their original bytes preserved. The [file inventory](FILE_MANIFEST.json) lists the size and SHA-256 checksum of every file.

| Contents | Location |
|---|---|
| All 15 synthetic project dossiers: 1,389 dataset files, including 380 Word documents and 15 architecture diagrams in both PNG and SVG | [dataset](../../experiments/run_20260922_180730_063947/dataset/) |
| Architecture documents and supporting evidence | Each dossier's `gate_evidence/architecture/` directory inside the dataset |
| Agent traces, tool calls, submissions, scores, checkpoints, and recorded failures: 817 files | [results](../../experiments/run_20260922_180730_063947/results/) |
| Original tables and reports: 6 files | [paper_outputs](../../experiments/run_20260922_180730_063947/paper_outputs/) |
| Recorded experiment settings | [experiment_config.json](../../experiments/run_20260922_180730_063947/experiment_config.json) |
| Recorded model catalog | [model_catalog_selected.json](../../experiments/run_20260922_180730_063947/model_catalog_selected.json) |

## Historical results

The recorded models are `deepseek/deepseek-v4.1-flash`, `google/gemini-3.8-flash`, and `z-ai/glm-5.3-flash`. The original report contains 15 evaluable cases for DeepSeek, 15 for Gemini, and 10 for GLM, with 5 GLM cases excluded. The dataset itself contains all 15 dossiers.

[Read the original pilot report](../../experiments/run_20260922_180730_063947/paper_outputs/PAPER_RESULTS.md). Its reported Gate CSR values are 27.1%, 72.9%, and 37.5%, respectively. These historical statistics have not been recomputed for this publication and must not be pooled with the later 300-project experiment.

The original [protocol identity](../../experiments/run_20260922_180730_063947/results/protocol_identity.json) is retained. Its source fingerprint differs from the later experiment; this publication preserves the pilot data and does not claim that the current repository code is its exact historical executable snapshot. Absolute paths in metadata describe the original machine.

Evaluator reference files are included for offline inspection; publication does not mean these references were exposed through the agents' tools. The dossiers describe synthetic projects.

Author: [Jeremy Canale](https://www.jeremycanale.com) · contact@jeremycanale.com
