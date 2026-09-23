"""Verify the release archives and reproduce final metrics offline (no API key).

python research/2026-09-dgf-bench/reproduce.py --archives downloads --output experiments/reproduced_300
Requires the benchmark dependencies and NumPy. Archive contents are hash-verified before use.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile


def unpack(archives, workspace):
    manifest = json.loads(Path(__file__).with_name('release_manifest.json').read_text(encoding='utf-8'))
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    for item in manifest['archives']:
        archive = archives / item['asset']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == item['sha256'], archive
        with zipfile.ZipFile(archive) as z:
            inventory = json.loads(z.read('FILE_MANIFEST.json'))
            assert len(inventory) == item['file_count']
            assert len(z.infolist()) == len(inventory)+1
            for entry in inventory:
                dest = (workspace / entry['path']).resolve()
                assert dest.is_relative_to(workspace), entry['path']
                data = z.read(entry['path'])
                assert len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256']
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists() or dest.read_bytes() != data:
                    dest.write_bytes(data)
        print('Verified and extracted:', item['asset'], flush=True)
    return manifest


def calculate(workspace, output, identity):
    import numpy as np
    sys.path.insert(0, str(workspace/'benchmark_source'))
    from benchmark_protocol import source_fingerprint, dataset_fingerprint
    from openrouter_eval.benchmark_runner import iter_cases
    from openrouter_eval.aggregate import aggregate
    from run_full_experiment import collect_paper_metrics, write_paper_outputs
    dataset = workspace/'experiments/preflight_balanced_300_20260922/dataset'
    results = workspace/'experiments/run_20260922_214402_941347/results'
    assert source_fingerprint() == identity['sources'], 'Source fingerprint mismatch'
    assert dataset_fingerprint(iter_cases(dataset)) == identity['dataset'], 'Dataset fingerprint mismatch'
    payload = aggregate(results)
    overall, gates = collect_paper_metrics(results, payload)
    output.mkdir(parents=True, exist_ok=True)
    write_paper_outputs(output, overall, gates, {'scoring_version': payload['scoring_version'], 'source': 'Verified release archives; offline reproduction'})
    (output/'aggregate.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    records = {}
    for p in sorted(results.glob('*/*/score.json')):
        s = json.loads(p.read_text(encoding='utf-8'))
        if s['status'] == 'OK':
            n = 5 if p.parent.name.endswith('_build') else 6
            assert len(s['occurrences']) == s['attempted_gate_count'] == s['expected_gate_count'] == n
            assert s['strict_gate_success_count'] == sum(o['strict_success'] for o in s['occurrences'])
            assert s['route_complete_decision'] == all(o['strict_success'] for o in s['occurrences'])
            records.setdefault(s['model'], {})[p.parent.name] = s
    models = sorted(records)
    common = sorted(set.intersection(*(set(records[m]) for m in models)))
    count = np.array([[records[m][c]['strict_gate_success_count'] for c in common] for m in models])
    route_count = np.array([[records[m][c]['route_complete_decision'] for c in common] for m in models], dtype=int)
    total = sum(records[models[0]][c]['expected_gate_count'] for c in common)
    rng = np.random.default_rng(81931)
    sampled = []
    for route in ['buy', 'integrate', 'build']:
        ix = np.array([i for i, c in enumerate(common) if c.endswith('_'+route)])
        sampled.append(rng.choice(ix, size=(10000, len(ix)), replace=True))
    ix = np.concatenate(sampled, axis=1)
    pairs = []
    for a, b in [(1, 0), (1, 2), (2, 0)]:
        delta = count[a]-count[b]
        routes = route_count[a]-route_count[b]
        pairs.append({'model_a': models[a], 'model_b': models[b], 'gate_diff_pp': 100*delta.sum()/total,
                      'gate_ci95_pp': (100*np.quantile(delta[ix].sum(axis=1)/total, [.025,.975])).tolist(),
                      'route_diff_pp': 100*routes.mean(),
                      'route_ci95_pp': (100*np.quantile(routes[ix].mean(axis=1), [.025,.975])).tolist()})
    (output/'paired_comparisons.json').write_text(json.dumps({'cases': len(common), 'comparisons': pairs}, indent=2), encoding='utf-8')
    expected = {models[0]: (300, 1261, 74), models[1]: (299, 1609, 230), models[2]: (300, 1416, 127)}
    for m, rr in records.items():
        actual = (len(rr), sum(s['strict_gate_success_count'] for s in rr.values()), sum(s['route_complete_decision'] for s in rr.values()))
        assert actual == expected[m], (m, actual)
        print(m, 'cases / strict gates / strict routes:', actual)
    assert abs(sum(r['total_cost_usd'] for r in overall)-87.015829172) < 1e-8
    print('Verified: 899 evaluable cases; 299 matched cases; total cost USD 87.015829172.')
    print('Reproduced reports:', output)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archives', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    output = args.output.resolve()
    workspace = output/'verified_inputs'
    manifest = unpack(args.archives.resolve(), workspace)
    calculate(workspace, output/'reports', manifest['protocol_identity'])
