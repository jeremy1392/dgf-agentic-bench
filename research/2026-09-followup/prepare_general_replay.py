"""Prepare a paired General-only handoff intervention; never call a model API.

Two fresh arms share all inputs except normalized upstream decision content.
The reference arm is adjusted to exactly the approvals validated in the original
trajectory, using the frozen scorer's reconstruction. No oracle label is sent.
"""
from __future__ import annotations

import argparse
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT/'experiments/reproduction_check_20260923/verified_inputs/benchmark_source'
DEFAULT_DATA = ROOT/'experiments/preflight_balanced_300_20260922/dataset'
DEFAULT_RUN = ROOT/'experiments/run_20260922_214402_941347'
DEFAULT_OUT = ROOT/'experiments/general_replay_prepared_20260924'
VERSION = 'general-normalized-history-replay-v1-prepared'
CANONICAL_JSON_HASH_SCOPE = 'sha256-canonical-json-v1: UTF-8; sorted keys; compact separators; ensure_ascii=False; allow_nan=False'
PORTABLE_DATASET_HASH_SCOPE = 'sha256 of canonical JSON rows [case, POSIX-relative-path, file-byte-sha256], sorted by case and POSIX path; excludes tool_trace.jsonl/environment_state.json'
VARIABLE_FIELDS = {'disposition', 'finding_ids', 'actions', 'authorization_required'}
IDENTITY_FIELDS = {'case_id', 'source_version', 'occurrence_id', 'gate', 'phase'}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def hash_obj(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def portable_dataset_fingerprint(cases):
    rows = []
    for case in cases:
        for path in Path(case).rglob('*'):
            if path.is_file() and path.name not in {'tool_trace.jsonl', 'environment_state.json'}:
                rows.append([Path(case).name, path.relative_to(case).as_posix(), hash_file(path)])
    rows.sort(key=lambda row: (row[0], row[1]))
    return hash_obj(rows)


def relative(path):
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n'
    if path.exists():
        if path.read_text(encoding='utf-8') != text:
            raise RuntimeError(f'Prepared artifact differs; choose a new output directory: {path}')
        return  # Do not change existing bytes merely because OS newline defaults differ.
    path.write_text(text, encoding='utf-8', newline='\n')


def normalized_history(history):
    """Drop explanations/quotes in both arms; sort arrays without deduplication."""
    output = []
    for row in history:
        value = {k: copy.deepcopy(row[k]) for k in sorted(IDENTITY_FIELDS | VARIABLE_FIELDS)}
        value['finding_ids'] = sorted(value['finding_ids'])
        value['actions'] = sorted(value['actions'])
        output.append(value)
    return output


def reconstruct(case_dir, records, source):
    """Reproduce score_submission's effective reference, approval use included."""
    from approval_policy import validated_conditional_approval
    from benchmark_protocol import make_handoff, select_upstream, PROTOCOL_VERSION
    from evaluator import evaluate_gate
    truth = load(case_dir/'99_hidden_ground_truth.json')
    route = load(case_dir/'01_route_manifest.json')
    case_public = load(case_dir/'00_project_context.json')
    by_oid = {x['occurrence_id']: x for x in route['occurrences']}
    effective_history, reference_handoffs, agent_handoffs, approval_checks = [], [], [], []
    general_target = None
    for base_ref in truth['reference_decisions']:
        ref = copy.deepcopy(base_ref)
        oid = ref['occurrence_id']
        occurrence = by_oid[oid]
        if ref['gate'] == 'general':
            ref.update(evaluate_gate(truth['canonical_truth'], ref['gate'], ref['phase'],
                                    select_upstream(effective_history, ref['phase'])))
            if general_target is not None:
                raise ValueError('This plan requires exactly one General per route.')
            general_target = {'occurrence': occurrence, 'common_unapproved_reference': copy.deepcopy(ref),
                              'agent_full_history': select_upstream(agent_handoffs, ref['phase']),
                              'reference_full_history': select_upstream(reference_handoffs, ref['phase'])}
            break  # The fresh General's own approval must not inherit its historical action.
        record = records[oid]
        approval = validated_conditional_approval(case_dir, ref, record)
        used = bool(approval and record['result'].get('disposition') == 'GO_WITH_RESERVATIONS')
        if used:
            ref['disposition'] = 'GO_WITH_RESERVATIONS'
            ref['authorization_required'] = True
        approval_checks.append({'occurrence_id': oid, 'validated': bool(approval), 'used': used,
                                'approval': approval, 'effective_disposition': ref['disposition']})
        effective_history.append(ref)
        reference_payload = dict(ref, finding_ids=[f['id'] for f in ref['findings']],
                                 actions=[a['action'] for a in ref['required_actions']])
        reference_handoffs.append(make_handoff(case_public['case_id'], occurrence, reference_payload, PROTOCOL_VERSION))
        agent_handoffs.append(make_handoff(case_public['case_id'], occurrence, record['result'], PROTOCOL_VERSION))
    if general_target is None:
        raise ValueError('General occurrence missing.')
    general_target['approval_checks'] = approval_checks
    return general_target


def pair_diff(first, second):
    if len(first) != len(second):
        raise AssertionError('Handoff size differs between arms.')
    changes = []
    for left, right in zip(first, second):
        assert set(left) == set(right) == IDENTITY_FIELDS | VARIABLE_FIELDS
        assert all(left[key] == right[key] for key in IDENTITY_FIELDS)
        fields = [key for key in sorted(VARIABLE_FIELDS) if left[key] != right[key]]
        if fields:
            changes.append({'occurrence_id': left['occurrence_id'], 'fields': fields})
    return changes


def make_messages(case_dir, occurrence, upstream):
    from benchmark_protocol import public_policy
    from openrouter_eval.finding_catalog import build_catalog
    from openrouter_eval.prompts import SYSTEM_PROMPT, occurrence_prompt
    import evaluator
    project = load(case_dir/'00_project_context.json')
    route = load(case_dir/'01_route_manifest.json')
    contract = copy.deepcopy(load(case_dir/'04_gate_contracts.json')['general'])
    contract.setdefault('decision_policy', public_policy('general'))
    catalog = build_catalog(Path(evaluator.__file__))['general']
    return [{'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': occurrence_prompt(project['project'], route['route'], occurrence,
                                                        contract, catalog, upstream)}]


def public_state_fingerprint(case_dir, occurrence):
    from openrouter_eval.agent_tools import ToolExecutor
    # No state_dir: no state files are written; only read-only calls are made.
    executor = ToolExecutor(case_dir, 'general', occurrence['phase'], occurrence['occurrence_id'], [])
    sources = {}
    for row in executor.public.list_evidence()['evidence']:
        value = executor.public.read_evidence(row['evidence_id'])
        sources[row['evidence_id']] = hash_obj(value)
    return {'public_sources': sources,
            'authorization_mandates': executor.env.get_authorization_mandates(),
            'source_contract': hash_file(case_dir/'04_gate_contracts.json'),
            'phase_visibility': hash_file(case_dir/'05_phase_visibility.json')}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    ap.add_argument('--dataset', type=Path, default=DEFAULT_DATA)
    ap.add_argument('--run', type=Path, default=DEFAULT_RUN)
    ap.add_argument('--output-dir', type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    sys.path.insert(0, str(args.source.resolve()))
    from benchmark_protocol import source_fingerprint, dataset_fingerprint
    from score_submission import score as frozen_score
    from openrouter_eval.agent_tools import ALL_TOOLS
    from openrouter_eval.prompts import SUBMIT_DECISION_TOOL
    plan = load(HERE/'repetition_plan.json')
    identity = load(args.run/'results/protocol_identity.json')
    assert source_fingerprint() == identity['sources'], 'Frozen source fingerprint mismatch'
    assert len(plan['cases']) == len(set(plan['cases'])) == 15 and len(plan['models']) == 3
    model_caps = load(args.run/'model_catalog_selected.json')
    result_dirs = {}
    for folder in sorted((args.run/'results').iterdir()):
        if folder.is_dir():
            score_path = next(folder.glob('DGF-*/score.json'), None)
            if score_path:
                result_dirs[load(score_path)['model']] = folder
    settings = {'temperature': 0.0, 'max_tokens': 8192, 'max_turns': 20, 'max_tool_calls': 40,
                'reasoning_effort': None, 'use_vision': False, 'require_parameters': True,
                'http_retries': 8, 'fresh_environment_each_job': True,
                'proposed_total_envelope_usd': 20, 'operating_headroom_usd': 2,
                'workers': 1, 'reserve_per_job_usd': 0.5}
    pairs, jobs, rows, by_model_cost = [], [], [], {}
    seed = 24092026
    schedule_rng = random.Random(seed)
    for model_index, model in enumerate(plan['models']):
        by_model_cost[model] = Decimal('0')
        for case_index, name in enumerate(plan['cases']):
            pair_id = f'm{model_index+1:02d}-c{case_index+1:02d}'
            case_dir = args.dataset/name
            folder = result_dirs[model]/name
            original_score = load(folder/'score.json')
            records, checkpoint_paths = {}, {}
            for path in sorted(folder.glob('[0-9][0-9]_*.json')):
                if '_ERROR' in path.stem:
                    continue
                record = load(path)
                if isinstance(record.get('result'), dict):
                    oid = record['result']['occurrence_id']
                    assert oid not in records
                    records[oid], checkpoint_paths[oid] = record, path
            route = load(case_dir/'01_route_manifest.json')
            assert len([o for o in route['occurrences'] if o['gate'] == 'general']) == 1
            assert set(records) == {o['occurrence_id'] for o in route['occurrences']}
            reconstructed = reconstruct(case_dir, records, args.source)
            occurrence = reconstructed['occurrence']
            oid = occurrence['occurrence_id']
            # Validate complete scorer equivalence, including authorized upstream history.
            scored = frozen_score(case_dir, {'gate_results': [records[o['occurrence_id']]['result'] for o in route['occurrences']]}, records)
            assert scored['occurrences'] == original_score['occurrences'], (model, name, 'Scorer replay mismatch')
            original_by_oid = {r['occurrence_id']: r for r in original_score['occurrences']}
            for approval in reconstructed['approval_checks']:
                old = original_by_oid[approval['occurrence_id']]
                assert approval['validated'] == old['conditional_approval_verified']
                assert approval['used'] == old['conditional_approval_used']
                assert approval['effective_disposition'] == old['reference_disposition']
            agent = normalized_history(reconstructed['agent_full_history'])
            reference = normalized_history(reconstructed['reference_full_history'])
            differences = pair_diff(agent, reference)
            common_inputs = public_state_fingerprint(case_dir, occurrence)
            histories = {'A': agent, 'B': reference}
            payload_hashes = {}
            stripped_hash = None
            for arm, history in histories.items():
                messages = make_messages(case_dir, occurrence, history)
                serialized_history = json.dumps(history, ensure_ascii=False, indent=2)
                assert messages[1]['content'].count(serialized_history) == 1
                masked = copy.deepcopy(messages)
                masked[1]['content'] = masked[1]['content'].replace(serialized_history, '<MATCHED_HISTORY>')
                current_stripped_hash = hash_obj(masked)
                assert stripped_hash in [None, current_stripped_hash]
                stripped_hash = current_stripped_hash
                assert all(set(row) == IDENTITY_FIELDS | VARIABLE_FIELDS for row in history)
                tools = copy.deepcopy(ALL_TOOLS + [SUBMIT_DECISION_TOOL])
                params = set(model_caps[model].get('supported_parameters', []))
                if 'structured_outputs' in params or 'response_format' in params:
                    tools[-1]['function']['strict'] = True
                payload = {'model': model, 'messages': messages, 'initial_tools': tools,
                           'tool_upstream': history, 'agent_settings': settings,
                           'model_capabilities_snapshot': model_caps[model]}
                masked_payload = copy.deepcopy(payload)
                masked_payload['messages'] = masked
                masked_payload['tool_upstream'] = '<MATCHED_HISTORY>'
                if arm == 'A':
                    invariant_payload_hash = hash_obj(masked_payload)
                else:
                    assert hash_obj(masked_payload) == invariant_payload_hash
                payload_hashes[arm] = hash_obj(payload)
                dump(args.output_dir/'payloads'/f'{pair_id}-{arm}.json', payload)
            usage = records[oid]['usage']
            assert not usage.get('unknown_cost_calls'), (model, name, 'Unknown historical cost')
            cost = Decimal(str(usage['cost']))
            assert cost.is_finite() and cost >= 0
            by_model_cost[model] += cost
            checkpoint = checkpoint_paths[oid]
            rows.append({'pair_id': pair_id, 'model': model, 'case': name,
                         'general_checkpoint': relative(checkpoint), 'checkpoint_sha256': hash_file(checkpoint),
                         'historical_usage_cost_usd': str(cost), 'six_fresh_executions_estimate_usd': str(cost * 6)})
            source_hashes = {relative(path): hash_file(path) for path in checkpoint_paths.values()}
            frozen = {'pair_id': pair_id, 'case': name, 'model': model, 'occurrence': occurrence,
                      'historical_agent_full_history': reconstructed['agent_full_history'],
                      'reference_full_history': reconstructed['reference_full_history'],
                      'normalized_agent_history': agent, 'normalized_reference_history': reference,
                      'common_unapproved_general_reference': reconstructed['common_unapproved_reference'],
                      'validated_fixed_upstream_approvals': reconstructed['approval_checks'],
                      'original_checkpoint_hashes': source_hashes, 'score_sha256': hash_file(folder/'score.json'),
                      'common_public_inputs': common_inputs, 'history_differences': differences,
                      'scorer_reproduction_exact': True}
            dump(args.output_dir/'evaluator_only'/f'{pair_id}.json', frozen)
            pairs.append({'pair_id': pair_id, 'model': model, 'case': name, 'occurrence_id': oid,
                          'identical_normalized_history_negative_control': not differences,
                          'history_differences': differences, 'common_inputs_sha256': hash_obj(common_inputs),
                          'prompt_without_history_sha256': stripped_hash,
                          'payload_sha256': payload_hashes,
                          'evaluator_only_sha256': hash_obj(frozen)})
            for repeat in range(1, 4):
                arms = ['A', 'B']
                schedule_rng.shuffle(arms)
                for arm in arms:
                    job_id = f'{pair_id}-r{repeat}-{arm}'
                    jobs.append({'job_id': job_id, 'pair_id': pair_id, 'repeat': repeat, 'arm_code': arm,
                                 'model': model, 'case': name, 'occurrence_id': oid,
                                 'payload': f'payloads/{pair_id}-{arm}.json', 'payload_sha256': payload_hashes[arm],
                                 'status': 'prepared_not_run', 'fresh_independent_trajectory_required': True})
    total_cost = sum(by_model_cost.values(), Decimal('0'))
    assert len(pairs) == 45 and len(jobs) == 270
    controls = {m: sum(p['model'] == m and p['identical_normalized_history_negative_control'] for p in pairs) for m in plan['models']}
    manifest = {'schema': VERSION, 'status': 'prepared_not_run', 'paid_calls_made': 0,
                'source_fingerprint': identity['sources'],
                'selected_dataset_fingerprint': dataset_fingerprint([args.dataset/name for name in plan['cases']]),
                'selection_source': relative(HERE/'repetition_plan.json'), 'selection_sha256': hash_file(HERE/'repetition_plan.json'),
                'models': plan['models'], 'cases': plan['cases'], 'model_case_pairs': 45,
                'fresh_trajectories_per_pair_per_arm': 3, 'planned_general_executions': 270,
                'arms': {'A': 'Historical actual upstream decisions, normalized',
                         'B': 'Reference upstream decisions with the same revalidated historical approvals, normalized'},
                'normalization': 'Keep only identity and decision/findings/actions/authorization fields; sort findings/actions lists without deduplication. Drop rationale, evidence refs/support and verification-status labels in both arms. Historical full handoffs are retained evaluator-only. This is a new normalized-content intervention, not an identical replay of historical prompts.',
                'comparison': 'Both arms are fresh executions. Historical General outcomes supply cost context only, not a treatment arm. Repeat index pairs execution order, not identical random seeds.',
                'settings': settings, 'schedule_seed': seed,
                'negative_control_pairs_by_model': controls,
                'cost_estimate': {'basis': 'Six times actual usage.cost from each of the 45 historical General final checkpoints; no route extrapolation.',
                                  'historical_45_general_total_usd': str(total_cost),
                                  'estimated_270_general_usd': str(total_cost * 6),
                                  'by_model_usd': {m: str(v * 6) for m, v in by_model_cost.items()},
                                  'uncertainty': 'Not a bound: normalized shorter prompts, new routing/pricing/caching, tools, generated tokens and retries can alter cost. Historical failed-attempt costs are not included. Proposed USD 20 envelope has not been spent or newly authorized here.'},
                'preflight': {'passed': True, 'exact_historical_score_reproductions': 45,
                              'fixed_approvals_revalidated': True, 'only_allowed_history_fields_differ': True,
                              'identical_nonhistory_messages_tools_settings_sources_mandates': True,
                              'no_oracle_label_or_evaluator_target_in_model_content': True,
                              'model_visible_history_fields': sorted(IDENTITY_FIELDS | VARIABLE_FIELDS)},
                'pairs': pairs, 'historical_cost_records': rows, 'jobs': jobs}
    dump(args.output_dir/'manifest.json', manifest)
    # Compact tracked record; payloads and evaluator targets remain in distinct folders.
    compact = {k: v for k, v in manifest.items() if k not in {'pairs', 'jobs', 'historical_cost_records'}}
    compact['prepared_directory'] = relative(args.output_dir)
    compact['manifest_sha256'] = hash_file(args.output_dir/'manifest.json')
    compact['manifest_path'] = relative(args.output_dir/'manifest.json')
    compact['historical_cost_records'] = rows
    dump(HERE/'general_replay_preflight.json', compact)
    print(json.dumps({k: compact[k] for k in ['status', 'paid_calls_made', 'planned_general_executions',
                                            'negative_control_pairs_by_model', 'cost_estimate', 'preflight']}, indent=2))


if __name__ == '__main__':
    main()
