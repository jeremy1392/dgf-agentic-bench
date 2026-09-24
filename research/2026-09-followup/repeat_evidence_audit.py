"""Apply the published lexical-or-structural sensitivity to all 135 repetitions.

No inference, new scoring, or edits to checkpoints. The inspect function is
imported unchanged from audit_all_models, so the original and repetition audits
share the same failed-excerpt, observed-citation and same-object tests.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

import audit_all_models as method

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NON_EVIDENCE = ('decision', 'findings_f1', 'actions_f1', 'authorization')
EXPECTED_PRIMARY = {
    'deepseek/deepseek-v4.1-flash': (187, 11, 0),
    'google/gemini-3.8-flash': (245, 35, 9),
    'openai/gpt-5.6-luna': (211, 19, 3),
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_only(row):
    return row['evidence_fidelity'] < 1 and all(row[k] == 1 for k in NON_EVIDENCE)


def summarize(routes, gates, failed):
    eligible = [x for x in failed if evidence_only(x['original_score'])]
    n = len(gates)
    cases = len(routes)
    return {
        'model_case_runs': cases,
        'gates': n,
        'strict_gates': sum(g['strict_success'] for g in gates),
        'posthoc_relaxed_gates': sum(g['posthoc_relaxed_success'] for g in gates),
        'strict_routes': sum(r['strict_success'] for r in routes),
        'posthoc_relaxed_routes': sum(r['posthoc_relaxed_success'] for r in routes),
        'strict_gate_rate': sum(g['strict_success'] for g in gates) / n,
        'posthoc_relaxed_gate_rate': sum(g['posthoc_relaxed_success'] for g in gates) / n,
        'strict_route_rate': sum(r['strict_success'] for r in routes) / cases,
        'posthoc_relaxed_route_rate': sum(r['posthoc_relaxed_success'] for r in routes) / cases,
        'correct_dispositions': sum(g['decision'] == 1 for g in gates),
        'evidence_failed_gates': len(failed),
        'evidence_only_failed_gates': len(eligible),
        'all_evidence_gate_categories': dict(collections.Counter(x['classification'] for x in failed)),
        'evidence_only_gate_categories': dict(collections.Counter(x['classification'] for x in eligible)),
        'failed_finding_item_categories': dict(collections.Counter(
            item['classification'] for x in failed for item in x['items'])),
        'resumed_model_case_runs': sum(r['resumed_gate_count'] > 0 for r in routes),
        'resumed_gates': sum(r['resumed_gate_count'] for r in routes),
        'relaxed_recoveries_in_resumed_prefix': sum(
            g['retained_resumed_prefix'] and not g['strict_success'] and g['posthoc_relaxed_success'] for g in gates),
    }


def render_report(result):
    lines = [
        '# Repetition evidence sensitivity: lexical or same-object structural support',
        '',
        'Offline audit of all 135 completed model-case trajectories (765 gates), using the unchanged `inspect` function in `audit_all_models.py`. The original strict outcomes remain the primary results. This post-hoc sensitivity is applied to every completed repetition; no best-of-three selection and no new model calls.',
        '',
        '| Model | Strict gates | Lexical-or-structural gates | Strict routes | Lexical-or-structural routes | All three strict routes | All three lexical-or-structural routes |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for model, m in result['models'].items():
        p = m['pooled']
        rate = lambda k, d: f"{p[k]}/{d} ({100*p[k]/d:.2f}%)"
        lines.append(f"| {model} | {rate('strict_gates', p['gates'])} | {rate('posthoc_relaxed_gates', p['gates'])} | {rate('strict_routes', p['model_case_runs'])} | {rate('posthoc_relaxed_routes', p['model_case_runs'])} | {m['all_three_strict_cases']}/15 | {m['all_three_posthoc_relaxed_cases']}/15 |")
    lines += [
        '',
        '| Model | Repeat | Strict gates | Lexical-or-structural gates | Strict routes | Lexical-or-structural routes |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for model, m in result['models'].items():
        for r in m['repetitions']:
            lines.append(f"| {model} | {r['repeat']} | {r['strict_gates']}/{r['gates']} | {r['posthoc_relaxed_gates']}/{r['gates']} | {r['strict_routes']}/{r['model_case_runs']} | {r['posthoc_relaxed_routes']}/{r['model_case_runs']} |")
    lines += [
        '',
        '| Model | Gates with evidence failure | Evidence-only failures | Same-object support for every failed item | Citation defect | Cross-object excerpt | Unresolved support |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for model, m in result['models'].items():
        p=m['pooled']; c=p['all_evidence_gate_categories']
        lines.append(f"| {model} | {p['evidence_failed_gates']} | {p['evidence_only_failed_gates']} | {c.get('all_failed_items_structurally_supported', 0)} | {c.get('citation_defect', 0)} | {c.get('includes_flattened_cross_object_excerpt', 0)} | {c.get('unresolved_structural_or_support_defect', 0)} |")
    lines += [
        '',
        'The category columns partition all gates with an evidence failure, including gates that also fail another component. A structurally recovered evidence component raises the relaxed gate score only when every unchanged non-evidence component also passes. Detailed category counts for evidence-only failures and individual finding items are in the summary JSON.',
        '',
        '## Method and interpretation',
        '',
        'An original strict success remains accepted. Otherwise, every unchanged decision, finding, action and authorization component must pass; cited evidence must have an authentic observed tool result; and every originally failed finding excerpt must parse as an exact field/value subset within a single observed source object, with at least one rule-relevant field. Key order and numeric serialization may differ. Wrong values, invented reads, and joins across different objects are not repaired or promoted.',
        '',
        'This is lexical-or-structural provenance sensitivity, not semantic entailment, complete coverage of a rule’s premises, or independent human adjudication. A remaining structural failure need not be semantically wrong. An accepted subset need not establish the entire finding. Original lexical successes are retained without a new semantic audit.',
        '',
        'The 15 dossiers were selected for the original repetition plan (five per route) and are reused across the three trajectories. These observations are not a new representative dataset and the 765 gates are not independent samples. All-three case success requires the complete route to pass on each of the three trajectories.',
        '',
        'Infrastructure resumes retain the completed prefix of the same trajectory. Two Gemini model-case runs retained seven gates in total; these are included exactly once in their final trajectory, with prefix flags in the detailed JSON. Failed attempts are not extra completed trajectories. This audit neither replays nor rescores those prefixes.',
        '',
        '## Reproduce',
        '',
        'Run `python research/2026-09-followup/repeat_evidence_audit.py` from the repository root. `--run-dir` accepts an extracted repetition archive; `--dataset` optionally points to its preserved dataset. The original benchmark source expected by `audit_evidence.py` must be installed at its documented frozen-source location.',
        '',
        'The script checks all 135 planned combinations, the three equal protocol identities, the published strict gate/route/all-three counts, complete and unique occurrence sets, and read-only score/trace hashes. `repetition_evidence_items.json` contains the failed gates and their original excerpts; `repetition_evidence_summary.json` contains model, repeat and per-case outcomes plus input provenance.',
    ]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, default=ROOT/'experiments/followup_repetitions_20260923')
    parser.add_argument('--dataset', type=Path)
    parser.add_argument('--output-dir', type=Path, default=HERE)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    dataset = (args.dataset or run/'dataset').resolve()
    output = args.output_dir.resolve()
    assert not output.is_relative_to(run), 'Write analysis separately from the retained experiment.'
    plan = read_json(HERE/'repetition_plan.json')
    expected = {(r, m, c) for r in range(1, 4) for m in plan['models'] for c in plan['cases']}
    method.audit.check_adversarial_controls()
    identities = [read_json(run/f'repeat_{r}'/'protocol_identity.json') for r in range(1, 4)]
    assert identities[0] == identities[1] == identities[2]
    assert identities[0]['models'] == plan['models']
    from benchmark_protocol import source_fingerprint
    assert source_fingerprint() == identities[0]['sources'], 'Frozen source identity differs.'
    inputs = []
    hashes = {}
    seen = set()
    all_routes = collections.defaultdict(list)
    all_gates = collections.defaultdict(list)
    all_failed = collections.defaultdict(list)
    for r in range(1, 4):
        for path in sorted((run/f'repeat_{r}').glob('*/DGF-*/score.json')):
            score = read_json(path)
            model = score['model']
            case = path.parent.name
            key = (r, model, case)
            assert key in expected and key not in seen, key
            seen.add(key)
            assert score['status'] == 'OK'
            assert score['attempted_gate_count'] == score['expected_gate_count'] == len(score['occurrences'])
            assert not score['model_resolution_mismatch'] and score['resolved_models'] == [model]
            assert len({row['occurrence_id'] for row in score['occurrences']}) == len(score['occurrences'])
            manifest = read_json(dataset/case/'01_route_manifest.json')
            assert [x['occurrence_id'] for x in score['occurrences']] == [x['occurrence_id'] for x in manifest['occurrences']]
            assert score['strict_gate_success_count'] == sum(x['strict_success'] for x in score['occurrences'])
            assert bool(score['route_complete_decision']) == all(x['strict_success'] for x in score['occurrences'])
            hashes[path] = sha256(path)
            inputs.append({'path': path.relative_to(run).as_posix(), 'sha256': hashes[path]})
            relaxed = []
            for i, row in enumerate(score['occurrences']):
                traces = list(path.parent.glob('*_'+row['occurrence_id']+'.json'))
                assert len(traces) == 1, (key, row['occurrence_id'], traces)
                trace = traces[0]
                hashes[trace] = sha256(trace)
                inputs.append({'path': trace.relative_to(run).as_posix(), 'sha256': hashes[trace]})
                recovered = False
                if row['evidence_fidelity'] < 1:
                    detail = method.inspect(path.parent, row, dataset)
                    detail.update(repeat=r, model=model, retained_resumed_prefix=i < score['resumed_gate_count'])
                    detail['original_trace'] = trace.relative_to(run).as_posix()
                    detail['trace_sha256'] = hashes[trace]
                    all_failed[model].append(detail)
                    recovered = detail['evidence_recovered']
                other_ok = all(row[k] == 1 for k in NON_EVIDENCE)
                relaxed.append(bool(row['strict_success'] or (other_ok and recovered)))
                all_gates[model].append(dict(row, repeat=r, case=case,
                    posthoc_relaxed_success=relaxed[-1], retained_resumed_prefix=i < score['resumed_gate_count']))
            all_routes[model].append({'repeat': r, 'case': case, 'strict_success': bool(score['route_complete_decision']),
                'posthoc_relaxed_success': all(relaxed), 'strict_gates': score['strict_gate_success_count'],
                'posthoc_relaxed_gates': sum(relaxed), 'gates': len(relaxed), 'resumed_gate_count': score['resumed_gate_count']})
    assert seen == expected and len(seen) == 135
    assert all(sha256(path) == digest for path, digest in hashes.items()), 'A retained score or trace changed during the audit.'
    models = {}
    for model in plan['models']:
        routes, gates, failed = all_routes[model], all_gates[model], all_failed[model]
        pooled = summarize(routes, gates, failed)
        repeats = [dict(summarize([x for x in routes if x['repeat'] == r],
                                 [x for x in gates if x['repeat'] == r],
                                 [x for x in failed if x['repeat'] == r]), repeat=r) for r in range(1, 4)]
        case_rows = []
        for case in plan['cases']:
            cr = sorted([x for x in routes if x['case'] == case], key=lambda x: x['repeat'])
            assert len(cr) == 3
            case_rows.append({'case': case, 'route': case.split('-')[1],
                'all_three_strict': all(x['strict_success'] for x in cr),
                'all_three_posthoc_relaxed': all(x['posthoc_relaxed_success'] for x in cr),
                'strict_route_outcomes': [x['strict_success'] for x in cr],
                'posthoc_relaxed_route_outcomes': [x['posthoc_relaxed_success'] for x in cr]})
        n_strict = sum(x['all_three_strict'] for x in case_rows)
        n_relaxed = sum(x['all_three_posthoc_relaxed'] for x in case_rows)
        assert (pooled['strict_gates'], pooled['strict_routes'], n_strict) == EXPECTED_PRIMARY[model]
        assert pooled['gates'] == 255 and pooled['model_case_runs'] == 45
        assert pooled['posthoc_relaxed_gates'] >= pooled['strict_gates']
        assert pooled['posthoc_relaxed_routes'] >= pooled['strict_routes'] and n_relaxed >= n_strict
        assert sum(pooled['all_evidence_gate_categories'].values()) == pooled['evidence_failed_gates']
        assert sum(pooled['evidence_only_gate_categories'].values()) == pooled['evidence_only_failed_gates']
        models[model] = {'pooled': pooled, 'repetitions': repeats,
            'unique_cases': len(case_rows), 'all_three_strict_cases': n_strict,
            'all_three_posthoc_relaxed_cases': n_relaxed,
            'strict_variable_route_cases': sum(len(set(x['strict_route_outcomes'])) > 1 for x in case_rows),
            'posthoc_relaxed_variable_route_cases': sum(len(set(x['posthoc_relaxed_route_outcomes'])) > 1 for x in case_rows),
            'cases': case_rows, 'route_details': routes}
    result = {
        'scope': 'All 135 completed repetitions: 15 original dossiers, three models, three trajectories each; 765 gates. Historical 300-case trajectories are not pooled.',
        'method': 'Identical inspect function imported from audit_all_models.py. Original strict success OR unchanged non-evidence components plus observed citations and exact field/value subset matches within one observed object for every originally failed finding. Original lexical successes remain accepted. No corrected quotes, invented reads, or cross-object promotion.',
        'limits': 'Post-hoc lexical-or-structural provenance sensitivity, not independent semantic entailment or complete premise coverage. No inference or rescore; primary outcomes unchanged. All-three case success requires complete routes on all three trajectories; only 15 unique cases per model.',
        'resumes': 'Final trajectories retain completed prefixes: two Gemini runs and seven gates in total. Prefix gates count once in their final repetition. Failed attempts are not additional trajectories; no gate was rerun for this audit.',
        'model_case_runs': len(seen), 'gates': sum(len(x) for x in all_gates.values()),
        'protocol_identity_equal_across_repeats': True, 'protocol_identity': identities[0],
        'shared_method_sha256': sha256(HERE/'audit_all_models.py'),
        'shared_helper_sha256': sha256(HERE/'audit_evidence.py'),
        'score_and_trace_inputs_unchanged': True, 'models': models, 'score_and_trace_inputs': inputs,
    }
    assert result['gates'] == 765
    assert sum(m['pooled']['resumed_model_case_runs'] for m in models.values()) == 2
    assert sum(m['pooled']['resumed_gates'] for m in models.values()) == 7
    output.mkdir(parents=True, exist_ok=True)
    for name, obj in [('repetition_evidence_summary.json', result), ('repetition_evidence_items.json', dict(all_failed))]:
        (output/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (output/'repetition_evidence_audit.md').write_text(render_report(result), encoding='utf-8')
    for model, m in models.items():
        print(model, json.dumps({**m['pooled'], 'all_three_strict_cases': m['all_three_strict_cases'],
                               'all_three_posthoc_relaxed_cases': m['all_three_posthoc_relaxed_cases']}))


if __name__ == '__main__':
    main()
