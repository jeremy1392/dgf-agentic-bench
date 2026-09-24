"""Prepare the fixed targeted replay's payloads and evaluator records, offline."""
import copy
import random
import sys

import prepare_general_replay as prep

OUT = prep.ROOT/'experiments/general_replay_targeted_prepared_20260924'


def main():
    sys.path.insert(0, str(prep.DEFAULT_SOURCE))
    from benchmark_protocol import source_fingerprint
    from score_submission import score
    from openrouter_eval.agent_tools import ALL_TOOLS
    from openrouter_eval.prompts import SUBMIT_DECISION_TOOL
    plan_path = prep.HERE/'general_replay_targeted_plan.json'
    plan = prep.load(plan_path)
    identity = prep.load(prep.DEFAULT_RUN/'results/protocol_identity.json')
    assert source_fingerprint() == identity['sources']
    assert plan['status'] == 'proposed_not_authorized_not_run'
    caps = prep.load(prep.DEFAULT_RUN/'model_catalog_selected.json')
    settings = {'temperature': 0.0, 'max_tokens': 8192, 'max_turns': 20, 'max_tool_calls': 40,
                'reasoning_effort': None, 'use_vision': False, 'require_parameters': True,
                'http_retries': 0, 'workers': 1, 'default_cap_usd': 10, 'maximum_cap_usd': 10,
                'operating_headroom_usd': 2, 'reserve_per_job_usd': 0.5,
                'transport_note': 'No internal HTTP retry: stop on uncertain billing. New transport protocol, identical in both arms.'}
    pairs, jobs = [], []
    for index, selection in enumerate(plan['selected_model_cases'], 1):
        pair_id = f'p{index:03d}'
        model, case = selection['model'], selection['case']
        case_dir = prep.DEFAULT_DATA/case
        general_path = prep.ROOT/selection['original_general_checkpoint']
        assert prep.hash_file(general_path) == selection['general_checkpoint_sha256']
        records, paths = {}, {}
        for path in sorted(general_path.parent.glob('[0-9][0-9]_*.json')):
            if '_ERROR' in path.stem:
                continue
            record = prep.load(path)
            if isinstance(record.get('result'), dict):
                oid = record['result']['occurrence_id']
                assert oid not in records
                records[oid], paths[oid] = record, path
        reconstructed = prep.reconstruct(case_dir, records, prep.DEFAULT_SOURCE)
        occurrence = reconstructed['occurrence']
        route = prep.load(case_dir/'01_route_manifest.json')
        assert score(case_dir, {'gate_results': [records[o['occurrence_id']]['result'] for o in route['occurrences']]}, records)['occurrences'] == prep.load(general_path.parent/'score.json')['occurrences']
        histories = {'A': prep.normalized_history(reconstructed['agent_full_history']),
                     'B': prep.normalized_history(reconstructed['reference_full_history'])}
        differences = prep.pair_diff(histories['A'], histories['B'])
        assert bool(differences) == selection['history_differs']
        common_inputs = prep.public_state_fingerprint(case_dir, occurrence)
        payload_hashes, invariant = {}, None
        for arm, history in histories.items():
            messages = prep.make_messages(case_dir, occurrence, history)
            history_text = prep.json.dumps(history, ensure_ascii=False, indent=2)
            assert messages[1]['content'].count(history_text) == 1
            tools = copy.deepcopy(ALL_TOOLS + [SUBMIT_DECISION_TOOL])
            parameters = set(caps[model].get('supported_parameters', []))
            if 'structured_outputs' in parameters or 'response_format' in parameters:
                tools[-1]['function']['strict'] = True
            payload = {'model': model, 'messages': messages, 'initial_tools': tools,
                       'tool_upstream': history, 'agent_settings': settings,
                       'model_capabilities_snapshot': caps[model]}
            masked = copy.deepcopy(payload)
            masked['messages'][1]['content'] = masked['messages'][1]['content'].replace(history_text, '<MATCHED_HISTORY>')
            masked['tool_upstream'] = '<MATCHED_HISTORY>'
            current = prep.hash_obj(masked)
            assert invariant is None or invariant == current
            invariant = current
            payload_hashes[arm] = prep.hash_obj(payload)
            prep.dump(OUT/'payloads'/f'{pair_id}-{arm}.json', payload)
        audit = {'pair_id': pair_id, 'model': model, 'case': case, 'occurrence': occurrence,
                 'historical_agent_full_history': reconstructed['agent_full_history'],
                 'reference_full_history': reconstructed['reference_full_history'],
                 'common_unapproved_general_reference': reconstructed['common_unapproved_reference'],
                 'validated_fixed_upstream_approvals': reconstructed['approval_checks'],
                 'original_checkpoint_hashes': {prep.relative(path): prep.hash_file(path) for path in paths.values()},
                 'common_public_inputs': common_inputs, 'history_differences': differences,
                 'scorer_reproduction_exact': True}
        prep.dump(OUT/'evaluator_only'/f'{pair_id}.json', audit)
        pair = dict(selection, pair_id=pair_id, payload_sha256=payload_hashes,
                    evaluator_only_sha256=prep.hash_obj(audit), common_inputs_sha256=prep.hash_obj(common_inputs),
                    nonhistory_payload_sha256=invariant)
        pairs.append(pair)
    # Round-robin model queues; randomize order only within each matched arm pair.
    queues = {model: [p for p in pairs if p['model'] == model] for model in plan['models']}
    rng = random.Random(24092026)
    for repeat in range(1, 4):
        for pair_index in range(max(map(len, queues.values()))):
            for model in queues:
                if pair_index >= len(queues[model]):
                    continue
                pair = queues[model][pair_index]
                arms = ['A', 'B']
                rng.shuffle(arms)
                for arm in arms:
                    pair_id = pair['pair_id']
                    jobs.append({'job_id': f'{pair_id}-r{repeat}-{arm}', 'pair_id': pair_id,
                                 'repeat': repeat, 'arm_code': arm, 'case': pair['case'], 'model': model,
                                 'occurrence_id': pair['occurrence_id'], 'selection_stratum': pair['selection_stratum'],
                                 'payload': f'payloads/{pair_id}-{arm}.json', 'payload_sha256': pair['payload_sha256'][arm],
                                 'status': 'prepared_not_run'})
    assert len(pairs) == 45 and len(jobs) == 270
    dataset_cases = [prep.DEFAULT_DATA/case for case in sorted({p['case'] for p in pairs})]
    manifest = {'schema': 'general-targeted-executable-v1', 'status': 'prepared_not_authorized_not_run',
                'paid_calls_made': 0, 'selection_plan_sha256': prep.hash_obj(plan),
                'selection_plan_hash_scope': prep.CANONICAL_JSON_HASH_SCOPE,
                'source_fingerprint': identity['sources'], 'dataset_fingerprint': prep.portable_dataset_fingerprint(dataset_cases),
                'dataset_fingerprint_scope': prep.PORTABLE_DATASET_HASH_SCOPE,
                'settings': settings, 'estimated_total_usd': plan['estimated_total_usd'],
                'pairs': pairs, 'jobs': jobs, 'planned_general_executions': 270,
                'preflight': {'passed': True, 'historical_scores_reproduced': 45,
                              'same_fixed_upstream_approvals': True, 'identical_nonhistory_payloads': True,
                              'history_difference_fields': sorted(prep.VARIABLE_FIELDS),
                              'separate_evaluator_only_targets': True}}
    prep.dump(OUT/'manifest.json', manifest)
    prep.dump(prep.HERE/'general_replay_targeted_preflight.json',
              {k: v for k, v in manifest.items() if k not in ['pairs', 'jobs']} |
              {'manifest_path': prep.relative(OUT/'manifest.json'), 'manifest_sha256': prep.hash_obj(manifest),
               'manifest_hash_scope': prep.CANONICAL_JSON_HASH_SCOPE})
    print(prep.canonical({'status': manifest['status'], 'jobs': len(jobs), 'payloads': len(pairs)*2,
                          'estimated_total_usd': plan['estimated_total_usd'], 'paid_calls_made': 0}))


if __name__ == '__main__':
    main()
