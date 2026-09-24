"""Offline scan and conditionally selected General replay proposal, never inference."""
import argparse
import collections
from decimal import Decimal
import random
import sys

import prepare_general_replay as prep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=prep.Path, default=prep.DEFAULT_SOURCE)
    ap.add_argument('--dataset', type=prep.Path, default=prep.DEFAULT_DATA)
    ap.add_argument('--run', type=prep.Path, default=prep.DEFAULT_RUN)
    args = ap.parse_args()
    sys.path.insert(0, str(args.source.resolve()))
    from benchmark_protocol import source_fingerprint
    from evaluator import evaluate_gate
    assert source_fingerprint() == prep.load(args.run/'results/protocol_identity.json')['sources']
    models = prep.load(prep.HERE/'repetition_plan.json')['models']
    folders, cases_by_model = {}, {}
    for modeldir in sorted((args.run/'results').iterdir()):
        if not modeldir.is_dir():
            continue
        first = next(modeldir.glob('DGF-*/score.json'), None)
        if first is None:
            continue
        model = prep.load(first)['model']
        if model not in models:
            continue
        folders[model] = modeldir
        cases_by_model[model] = {}
        for score_path in sorted(modeldir.glob('DGF-*/score.json')):
            score = prep.load(score_path)
            general = [r for r in score.get('occurrences', []) if r['gate'] == 'general' and r['attempted']]
            if score.get('status') in ['OK', 'AGENT_FAILURE'] and len(general) == 1:
                cases_by_model[model][score_path.parent.name] = score
    common = sorted(set.intersection(*(set(cases_by_model[m]) for m in models)))
    assert len(common) == 299
    rows, summaries = [], {}
    selected = []
    seed = 24092026
    total_cost = Decimal('0')
    for model in models:
        field_counts, mutation_counts = collections.Counter(), collections.Counter()
        current_rows = []
        for case in common:
            folder = folders[model]/case
            records, paths = {}, {}
            for path in sorted(folder.glob('[0-9][0-9]_*.json')):
                if '_ERROR' in path.stem:
                    continue
                record = prep.load(path)
                if isinstance(record.get('result'), dict):
                    oid = record['result']['occurrence_id']
                    assert oid not in records
                    records[oid], paths[oid] = record, path
            value = prep.reconstruct(args.dataset/case, records, args.source)
            agent = prep.normalized_history(value['agent_full_history'])
            reference = prep.normalized_history(value['reference_full_history'])
            differences = prep.pair_diff(agent, reference)
            old = {r['occurrence_id']: r for r in cases_by_model[model][case]['occurrences']}
            for approval in value['approval_checks']:
                assert approval['validated'] == old[approval['occurrence_id']]['conditional_approval_verified']
                assert approval['used'] == old[approval['occurrence_id']]['conditional_approval_used']
                assert approval['effective_disposition'] == old[approval['occurrence_id']]['reference_disposition']
            fields = sorted({f for d in differences for f in d['fields']})
            field_counts.update(fields)
            for difference in differences:
                mutation_counts.update(difference['fields'])
            general_oid = value['occurrence']['occurrence_id']
            usage = records[general_oid]['usage']
            assert not usage.get('unknown_cost_calls')
            cost = Decimal(str(usage['cost']))
            assert cost.is_finite() and cost >= 0
            canonical_case = prep.load(args.dataset/case/'99_hidden_ground_truth.json')['canonical_truth']
            agent_environment_reference = evaluate_gate(canonical_case, 'general', value['occurrence']['phase'], agent)
            common_target = value['common_unapproved_reference']
            row = {'model': model, 'case': case, 'occurrence_id': general_oid,
                   'history_differs': bool(differences), 'changed_fields': fields,
                   'history_differences': differences,
                   'original_general_checkpoint': prep.relative(paths[general_oid]),
                   'general_checkpoint_sha256': prep.hash_file(paths[general_oid]),
                   'historical_general_cost_usd': str(cost),
                   'validated_upstream_approvals': sum(x['validated'] for x in value['approval_checks']),
                   'used_upstream_approvals': sum(x['used'] for x in value['approval_checks']),
                   'agent_history_environment_base_disposition': agent_environment_reference['disposition'],
                   'common_reference_base_disposition': common_target['disposition'],
                   'general_base_disposition_changes_under_history': agent_environment_reference['disposition'] != common_target['disposition'],
                   'general_reference_finding_ids_change_under_history':
                       sorted(f['id'] for f in agent_environment_reference['findings']) != sorted(f['id'] for f in common_target['findings'])}
            current_rows.append(row)
        changed = [r for r in current_rows if r['history_differs']]
        unchanged = [r for r in current_rows if not r['history_differs']]
        rng = random.Random(str(seed) + ':' + model)
        difference_sample = rng.sample(changed, min(15, len(changed)))
        control_sample = rng.sample(unchanged, min(5, len(unchanged)))
        current_cost = sum((Decimal(r['historical_general_cost_usd']) * 6 for r in difference_sample + control_sample), Decimal('0'))
        total_cost += current_cost
        for row in difference_sample + control_sample:
            selected.append(dict(row, selection_stratum='changed_history' if row['history_differs'] else 'identical_history_control'))
        summaries[model] = {'common_cases': len(common), 'different_histories': len(changed),
                            'identical_history_controls_available': len(unchanged),
                            'cases_by_changed_field': dict(field_counts),
                            'upstream_occurrences_by_changed_field': dict(mutation_counts),
                            'general_base_disposition_changes_under_history': sum(r['general_base_disposition_changes_under_history'] for r in current_rows),
                            'general_reference_finding_ids_change_under_history': sum(r['general_reference_finding_ids_change_under_history'] for r in current_rows),
                            'proposed_difference_cases': len(difference_sample), 'proposed_control_cases': len(control_sample),
                            'proposed_fresh_general_executions': 6 * (len(difference_sample) + len(control_sample)),
                            'estimated_general_cost_usd': str(current_cost)}
        rows.extend(current_rows)
    scan = {'schema': 'general-normalized-history-population-scan-v1', 'status': 'offline_analysis_complete_no_inference',
            'paid_calls_made': 0, 'source_fingerprint': source_fingerprint(), 'common_cases': common,
            'model_case_pairs_scanned': len(rows),
            'scope': '299 original cases evaluable in all three models; normalized upstream decision fields only; upstream approvals revalidated with frozen policy.',
            'models': summaries, 'pairs': rows}
    prep.dump(prep.HERE/'general_replay_population_scan.json', scan)
    proposal = {'schema': 'general-normalized-history-targeted-proposal-v1', 'status': 'proposed_not_authorized_not_run',
                'paid_calls_made': 0, 'sampling_seed': seed,
                'sampling': 'For each model separately, sample without replacement from lexicographically sorted 299 common case IDs using random.Random(str(seed)+":"+model). Select up to 15 cases with changed normalized upstream history, plus 5 identical-history controls. No selection by future outcomes or checkpoint cost. The difference stratum is deliberately selected on historical model/reference disagreement.',
                'estimand': 'Effect of replacing historical normalized decision content by approval-adjusted reference content conditional on historical disagreement; not a population-average effect. Identical-history controls estimate fresh-run variation and order effects, not correction benefits.',
                'arms': {'A': 'Normalized actual historical upstream decisions', 'B': 'Normalized approval-adjusted reference upstream decisions'},
                'fresh_trajectories_per_model_case_per_arm': 3, 'planned_general_executions': 6 * len(selected),
                'models': summaries, 'selected_model_cases': selected,
                'estimated_total_usd': str(total_cost), 'proposed_total_envelope_usd': 10,
                'cost_basis': 'Six times usage.cost in each selected original final General checkpoint; excludes historical failed attempts. Pricing/routing/caching, normalized prompt length, tool choices and retries can change realized cost; estimate is not a hard bound.',
                'authorization': 'New targeted proposal only. No API key read, no paid calls, and no execution launcher included. Prior repetition authorization is not reused.',
                'analysis': 'Report each arm and repeat; paired differences by model within disagreement and control strata; uncertainty clustered by case. Keep every trace/error/cost and all fresh trajectories; do not pick best-of-three. Distinguish common approval-adjusted target accuracy from consistency with the supplied history. Do not pool the two strata into an unweighted population rate.',
                'population_scan_sha256': prep.hash_obj(scan),
                'population_scan_hash_scope': prep.CANONICAL_JSON_HASH_SCOPE}
    prep.dump(prep.HERE/'general_replay_targeted_plan.json', proposal)
    print(prep.canonical({'model_case_pairs_scanned': len(rows), 'models': summaries,
                          'targeted_general_executions': proposal['planned_general_executions'],
                          'estimated_total_usd': str(total_cost), 'status': proposal['status']}))


if __name__ == '__main__':
    main()
