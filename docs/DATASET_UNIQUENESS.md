# Dataset identity and architecture diversity

DGF-Bench v7.5 enforces case-level uniqueness when a dataset is generated.

## Guaranteed unique within one generated dataset

The generator checks and fails closed if any of the following collide:

- case ID;
- project ID;
- full project name and project code;
- architecture ID and case-specific resource prefix;
- structural architecture signature;
- canonical hidden-truth hash;
- MSA version, HLD version, and LLD version;
- every named person used in the project metadata;
- every synthetic vendor name;
- every private CIDR used by the generated cases.

The report is written to `dataset_uniqueness_report.json` next to `dataset_manifest.json`.

## Structural architecture signature

The architecture signature excludes case-specific names and hashes the material topology/configuration fields: solution family, network topology, edge pattern, compute/data profile, resilience, regions, private/public posture, firewall/hybrid connectivity, platform services, SIEM/backup posture, and replication mode.

The balanced generator uses deterministic rejection sampling. If the next RNG stream would repeat a structural architecture signature already present in the dataset, only the architecture RNG stream is advanced until a new signature is obtained. The project seed and identity are not changed.

## What is intentionally allowed to repeat

Benchmark categories must repeat so models can be compared on the same concepts. Azure product names, route names, gate types, dispositions, booleans, policy states, and other controlled categorical values may therefore recur across cases. What may not recur is an entire case identity or structural architecture configuration.

## HLD visual grammar

The renderer no longer uses one fixed Hub -> Compute Spoke -> Data Spoke layout.

- `hub_spoke`: hub VNet plus workload and data spokes;
- `single_vnet`: one VNet with application, data, and management/platform subnets;
- `virtual_wan`: Azure Virtual WAN transit hub with connected workload/data spokes.

Resilience is rendered separately for single-zone, same-region multi-AZ, backup-only, multi-region active/passive, and multi-region active/active configurations.
