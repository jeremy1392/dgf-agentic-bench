"""Run only explicitly enabled, prepared General replays under one cost ledger.

Default: validate offline and exit. --execute enables paid calls and requires
OPENROUTER_API_KEY in the local environment. No key is read during a dry run.
The user must authorize a new expense; this program does not infer authorization.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import json
import math
import os
from pathlib import Path
import re
import sys
import uuid

import prepare_general_replay as prep

sys.path.insert(0, str(prep.DEFAULT_SOURCE))
from benchmark_protocol import source_fingerprint
from openrouter_eval.agent_runner import AgentConfig, AgentRunError, run_occurrence
from openrouter_eval.benchmark_runner import BudgetedClient, CostBudget
from openrouter_eval.openrouter_client import OpenRouterClient, Usage, BudgetStopped, BillingUnknown, OpenRouterError
from score_submission import score as frozen_score
from evaluator import evaluate_gate
from approval_policy import validated_conditional_approval

PREPARED = prep.ROOT/'experiments/general_replay_targeted_prepared_20260924'
RESULTS = prep.ROOT/'experiments/general_replay_targeted_results_20260924'


class ReplayStopped(RuntimeError):
    pass


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def append_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False)+'\n')
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def exclusive_run_lock(folder):
    """Native lock is released by the OS even when a process terminates."""
    folder.mkdir(parents=True, exist_ok=True)
    with (folder/'runner.lock').open('a+b') as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ReplayStopped('Another replay runner holds this result directory lock.') from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def ledger_state(folder):
    total, unknown, calls = 0.0, 0, 0
    for path in sorted(folder.glob('jobs/*/attempt_*/usage_ledger.jsonl')):
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                value, missing = row['cost'], row['unknown_cost_calls']
                if type(value) not in [int, float] or not math.isfinite(value) or value < 0:
                    raise ValueError('Invalid cost')
                if type(missing) is not int or missing < 0:
                    raise ValueError('Invalid unknown count')
            except (ValueError, TypeError, KeyError) as exc:
                raise ReplayStopped('Ledger is incomplete or invalid; reconcile billing before resuming.') from exc
            total += value
            unknown += missing
            calls += 1
    inflight = sorted(str(p.relative_to(folder)) for p in folder.glob('jobs/*/attempt_*/inflight.json'))
    return {'cost_usd': total, 'unknown_cost_calls': unknown, 'ledger_responses': calls,
            'unresolved_inflight_markers': inflight}


def validate_prepared(prepared=PREPARED):
    manifest = prep.load(prepared/'manifest.json')
    published = prep.load(prep.HERE/'general_replay_targeted_preflight.json')
    assert published['manifest_hash_scope'] == prep.CANONICAL_JSON_HASH_SCOPE
    assert prep.hash_obj(manifest) == published['manifest_sha256'], 'Manifest changed'
    assert manifest['selection_plan_hash_scope'] == prep.CANONICAL_JSON_HASH_SCOPE
    assert prep.hash_obj(prep.load(prep.HERE/'general_replay_targeted_plan.json')) == manifest['selection_plan_sha256'], 'Selection plan changed'
    assert manifest['schema'] == 'general-targeted-executable-v1'
    assert manifest['source_fingerprint'] == source_fingerprint(), 'Frozen source changed'
    assert len(manifest['jobs']) == 270 and len(manifest['pairs']) == 45
    assert manifest['settings']['http_retries'] == 0 and manifest['settings']['workers'] == 1
    assert len({j['job_id'] for j in manifest['jobs']}) == 270
    cases = sorted({p['case'] for p in manifest['pairs']})
    assert all(re.fullmatch(r'DGF-[A-Za-z0-9_-]+', case) for case in cases)
    assert manifest['dataset_fingerprint_scope'] == prep.PORTABLE_DATASET_HASH_SCOPE
    assert prep.portable_dataset_fingerprint([prep.DEFAULT_DATA/case for case in cases]) == manifest['dataset_fingerprint'], 'Dataset changed'
    contexts = {}
    for pair in manifest['pairs']:
        pair_id = pair['pair_id']
        assert re.fullmatch(r'p[0-9]{3}', pair_id)
        audit = prep.load(prepared/'evaluator_only'/f'{pair_id}.json')
        assert prep.hash_obj(audit) == pair['evaluator_only_sha256']
        records = {}
        for rel, expected in audit['original_checkpoint_hashes'].items():
            path = (prep.ROOT/rel).resolve()
            assert path.is_relative_to((prep.DEFAULT_RUN/'results').resolve())
            assert prep.hash_file(path) == expected, 'Original checkpoint changed'
            record = prep.load(path)
            records[record['result']['occurrence_id']] = record
        reconstructed = prep.reconstruct(prep.DEFAULT_DATA/pair['case'], records, prep.DEFAULT_SOURCE)
        assert reconstructed['common_unapproved_reference'] == audit['common_unapproved_general_reference']
        assert reconstructed['approval_checks'] == audit['validated_fixed_upstream_approvals']
        payloads = {}
        for arm in ['A', 'B']:
            payload = prep.load(prepared/'payloads'/f'{pair_id}-{arm}.json')
            assert prep.hash_obj(payload) == pair['payload_sha256'][arm]
            assert payload['model'] == pair['model']
            assert payload['agent_settings'] == manifest['settings']
            expected_history = prep.normalized_history(reconstructed['agent_full_history' if arm == 'A' else 'reference_full_history'])
            assert payload['tool_upstream'] == expected_history
            assert payload['messages'] == prep.make_messages(prep.DEFAULT_DATA/pair['case'], audit['occurrence'], expected_history)
            payloads[arm] = payload
        assert prep.pair_diff(payloads['A']['tool_upstream'], payloads['B']['tool_upstream']) == audit['history_differences']
        contexts[pair_id] = {'pair': pair, 'audit': audit, 'records': records, 'payloads': payloads}
    for job in manifest['jobs']:
        assert re.fullmatch(r'p[0-9]{3}-r[123]-[AB]', job['job_id'])
        assert job['status'] == 'prepared_not_run'
        context = contexts[job['pair_id']]
        assert job['case'] == context['pair']['case'] and job['model'] == context['pair']['model']
        assert job['payload_sha256'] == context['pair']['payload_sha256'][job['arm_code']]
        assert job['payload'] == f"payloads/{job['pair_id']}-{job['arm_code']}.json"
    return manifest, contexts


class DurableBudgetedClient(BudgetedClient):
    """Use frozen accounting; add request markers and conservative failure closure."""
    def __init__(self, client, budget, job_id, attempt_dir, expected_payload):
        self.attempt_dir = attempt_dir
        self.expected_payload = expected_payload
        self.request_number = 0
        self.attempt_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(client, budget, job_id, attempt_dir/'usage_ledger.jsonl')

    def _account(self, usage):
        super()._account(usage)
        # The frozen wrapper flushes each row; also request OS durability.
        with self.ledger.open('a', encoding='utf-8') as stream:
            stream.flush()
            os.fsync(stream.fileno())

    def chat(self, body):
        self._check_budget()
        expected = self.expected_payload
        if body.get('model') != expected['model'] or body.get('messages', [])[:2] != expected['messages']:
            raise ReplayStopped('Runtime model/prompt differs from the prepared payload; no request sent.')
        if self.request_number == 0 and body.get('tools') != expected['initial_tools']:
            raise ReplayStopped('Runtime initial tools differ from preparation; no request sent.')
        self.request_number += 1
        marker = self.attempt_dir/'inflight.json'
        request_id = uuid.uuid4().hex
        event = {'request_id': request_id, 'request_number': self.request_number,
                 'model': body['model'], 'request_sha256': prep.hash_obj(body)}
        atomic_json(marker, event)
        append_json(self.attempt_dir/'request_events.jsonl', dict(event, event='request_started'))
        try:
            response = super().chat(body)
        except BudgetStopped:
            # With one worker, this can only occur before transmission.
            append_json(self.attempt_dir/'request_events.jsonl', dict(event, event='not_sent_budget_stop'))
            marker.unlink()
            raise
        except BillingUnknown:
            # The frozen wrapper already adds unknown_cost_calls=1.
            append_json(self.attempt_dir/'request_events.jsonl', dict(event, event='billing_unknown'))
            marker.unlink()
            raise
        except OpenRouterError as exc:
            # With zero internal HTTP retries, a transport/API error is one
            # attempted request whose actual charge is conservatively unknown.
            self._account(Usage(unknown_cost_calls=1))
            append_json(self.attempt_dir/'request_events.jsonl', dict(event, event='request_failed_billing_unconfirmed', error_type=type(exc).__name__))
            marker.unlink()
            raise BillingUnknown('Request failed; billing must be reconciled before retry.') from None
        else:
            usage = Usage.from_response(response)
            atomic_json(self.attempt_dir/'responses'/f'{self.request_number:03d}.json', response)
            append_json(self.attempt_dir/'request_events.jsonl', dict(event, event='response_accounted', usage=usage.as_dict()))
            marker.unlink()
            return response
        # KeyboardInterrupt, abrupt exit, or unexpected local errors retain the
        # durable marker. A later invocation refuses to send another request.


def score_fresh_record(context, arm, record):
    case_dir = prep.DEFAULT_DATA/context['pair']['case']
    audit = context['audit']
    oid = audit['occurrence']['occurrence_id']
    records = dict(context['records'])
    records[oid] = record
    route = prep.load(case_dir/'01_route_manifest.json')
    submission = {'gate_results': [records[o['occurrence_id']]['result'] for o in route['occurrences']]}
    scoring = frozen_score(case_dir, submission, records)
    common = next(row for row in scoring['occurrences'] if row['occurrence_id'] == oid)
    truth = prep.load(case_dir/'99_hidden_ground_truth.json')['canonical_truth']
    history_ref = evaluate_gate(truth, 'general', audit['occurrence']['phase'], context['payloads'][arm]['tool_upstream'])
    history_ref['occurrence_id'] = oid
    local_approval = validated_conditional_approval(case_dir, history_ref, record)
    history_disposition = ('GO_WITH_RESERVATIONS' if local_approval and record['result']['disposition'] == 'GO_WITH_RESERVATIONS'
                           else history_ref['disposition'])
    return {'common_target_score': common,
            'common_unapproved_reference': audit['common_unapproved_general_reference'],
            'supplied_history_base_disposition': history_ref['disposition'],
            'supplied_history_effective_disposition': history_disposition,
            'disposition_consistent_with_supplied_history': record['result']['disposition'] == history_disposition,
            'approval_valid_under_supplied_history': bool(local_approval),
            'approval_valid_under_common_target': common['conditional_approval_verified'],
            'note': 'Primary score uses the same approval-adjusted canonical upstream reference in both arms. Environment action eligibility is derived from supplied history and can differ.'}


def known_resume_records(job_dir, job, *, block_nonretryable=True):
    previous = []
    for attempt in job_dir.glob('attempt_*'):
        if (attempt/'usage_ledger.jsonl').exists() and not (attempt/'checkpoint.json').exists() and not (attempt/'raw_record.json').exists():
            raise ReplayStopped('A paid attempt has no finalized raw record; inspect retained responses before any retry.')
    for path in sorted(job_dir.glob('attempt_*/checkpoint.json')):
        checkpoint = prep.load(path)
        if checkpoint.get('job_id') != job['job_id'] or checkpoint.get('payload_sha256') != job['payload_sha256']:
            raise ReplayStopped('Checkpoint identity differs from prepared job.')
        if prep.hash_obj(checkpoint.get('record')) != checkpoint.get('raw_record_sha256'):
            raise ReplayStopped('Checkpoint record integrity differs from its saved raw trajectory.')
        if checkpoint['status'] == 'complete' and checkpoint.get('record', {}).get('result', {}).get('occurrence_id') != job['occurrence_id']:
            raise ReplayStopped('Completed checkpoint has no matching General result.')
        previous.append(checkpoint)
        if block_nonretryable and checkpoint['status'] in ['billing_unknown', 'model_mismatch']:
            raise ReplayStopped('Billing or model identity requires inspection before another invocation.')
    terminal = [x for x in previous if x['status'] in ['complete', 'agent_failure']]
    if len(terminal) > 1:
        raise ReplayStopped('Multiple terminal records for one planned job.')
    return previous, terminal[0] if terminal else None


def finalize_raw_record(job, context, raw):
    if raw.get('job_id') != job['job_id'] or raw.get('payload_sha256') != job['payload_sha256']:
        raise ReplayStopped('Saved raw record identity differs from prepared job.')
    record = raw['record']
    if prep.hash_obj(record) != raw['record_sha256']:
        raise ReplayStopped('Saved raw record integrity check failed.')
    scoring, stop_reason = None, None
    kind = raw.get('error_kind')
    if raw.get('billing_unknown'):
        status, stop_reason = 'billing_unknown', 'An API attempt has unconfirmed billing.'
    elif kind == 'budget':
        status, stop_reason = 'budget_stopped', 'Shared operating budget stopped the trajectory.'
    elif kind in ['agent', 'agent_protocol']:
        status = 'agent_failure'
    elif kind is not None:
        status, stop_reason = 'infrastructure_error', 'Infrastructure failure retained; resume can retry if all costs are known.'
    elif any(m != job['model'] for m in record.get('resolved_models', [])):
        status, stop_reason = 'model_mismatch', 'Provider returned a different model identity.'
    else:
        scoring = score_fresh_record(context, job['arm_code'], record)
        status = 'complete'
    checkpoint = {'job_id': job['job_id'], 'pair_id': job['pair_id'], 'model': job['model'],
                  'case': job['case'], 'arm_code': job['arm_code'], 'repeat': job['repeat'],
                  'selection_stratum': job['selection_stratum'], 'payload_sha256': job['payload_sha256'],
                  'attempt': raw['attempt'], 'status': status, 'record': record, 'scoring': scoring,
                  'http_stats': raw['http_stats'], 'raw_record_sha256': raw['record_sha256']}
    return checkpoint, stop_reason


def execute_prepared(manifest, contexts, result_dir, cap_usd, client_factory, *, runner=run_occurrence, max_new_jobs=None):
    """Injectable client/runner for offline tests; the production factory is private to --execute."""
    if type(cap_usd) not in [int, float] or not math.isfinite(cap_usd) or not 0 < cap_usd <= 10:
        raise ValueError('Total cap must be finite, positive and at most USD 10.')
    identity = {'manifest_sha256': prep.hash_obj(manifest), 'manifest_hash_scope': prep.CANONICAL_JSON_HASH_SCOPE,
                'source_fingerprint': manifest['source_fingerprint']}
    operating_cap = max(0.0, cap_usd - 2.0)
    with exclusive_run_lock(result_dir):
        identity_path = result_dir/'run_identity.json'
        if identity_path.exists() and prep.load(identity_path) != identity:
            raise ReplayStopped('Results belong to a different prepared experiment.')
        atomic_json(identity_path, identity)
        prior = ledger_state(result_dir)
        if prior['unknown_cost_calls'] or prior['unresolved_inflight_markers']:
            raise ReplayStopped('Billing is unknown or a request was interrupted; reconcile before resuming. No call sent.')
        budget = CostBudget(operating_cap, initial_spent=prior['cost_usd'], reserve_per_job=0.5)
        append_json(result_dir/'run_invocations.jsonl', {'cap_usd': cap_usd, 'operating_cap_usd': operating_cap,
                                                       'prior_cost_usd': prior['cost_usd']})
        fresh = resumed = failed = 0
        stop_reason = None
        for job in manifest['jobs']:
            context = contexts[job['pair_id']]
            payload = context['payloads'][job['arm_code']]
            job_dir = result_dir/'jobs'/job['job_id']
            # Finish already-paid inference entirely offline before considering
            # another model request. Never rerun inference because scoring failed.
            for raw_path in sorted(job_dir.glob('attempt_*/raw_record.json')):
                checkpoint_path = raw_path.parent/'checkpoint.json'
                if not checkpoint_path.exists():
                    checkpoint, recovered_stop = finalize_raw_record(job, context, prep.load(raw_path))
                    atomic_json(checkpoint_path, checkpoint)
                    if recovered_stop:
                        stop_reason = recovered_stop
            previous, terminal = known_resume_records(job_dir, job)
            if terminal:
                resumed += 1
                continue
            if max_new_jobs is not None and fresh >= max_new_jobs:
                break
            if len(previous) >= 3:
                stop_reason = 'Three known failed attempts retained for a job; inspect before further retry.'
                break
            if not budget.reserve(job['job_id']):
                stop_reason = 'Shared operating budget does not admit another job.'
                break
            existing_dirs = [int(p.name.split('_')[-1]) for p in job_dir.glob('attempt_[0-9][0-9][0-9]') if p.is_dir()]
            attempt_no = max(existing_dirs, default=0) + 1
            attempt_dir = job_dir/f'attempt_{attempt_no:03d}'
            attempt_dir.mkdir(parents=True, exist_ok=False)
            settings = payload['agent_settings']
            config = AgentConfig(model=job['model'], temperature=settings['temperature'], max_tokens=settings['max_tokens'],
                                 max_turns=settings['max_turns'], max_tool_calls=settings['max_tool_calls'],
                                 reasoning_effort=settings['reasoning_effort'], use_vision=False,
                                 require_parameters=True, state_dir=str(attempt_dir/'environment'))
            client = DurableBudgetedClient(client_factory(), budget, job['job_id'], attempt_dir, payload)
            record, error_kind = None, None
            try:
                record = runner(client, prep.DEFAULT_DATA/job['case'], context['audit']['occurrence'],
                                payload['model_capabilities_snapshot'], config, copy.deepcopy(payload['tool_upstream']))
            except AgentRunError as exc:
                record = exc.record
                error_kind = exc.kind
            except BaseException:
                # Do not serialize arbitrary exception messages or provider bodies:
                # they might expose authentication details. Markers preserve uncertainty.
                raise
            finally:
                budget.release(job['job_id'])
            raw = {'job_id': job['job_id'], 'payload_sha256': job['payload_sha256'],
                   'attempt': attempt_no, 'record': record, 'record_sha256': prep.hash_obj(record),
                   'error_kind': error_kind, 'billing_unknown': bool(budget.unknown_cost_calls),
                   'http_stats': client.stats_snapshot()}
            atomic_json(attempt_dir/'raw_record.json', raw)
            checkpoint, stop_reason = finalize_raw_record(job, context, raw)
            status = checkpoint['status']
            atomic_json(attempt_dir/'checkpoint.json', checkpoint)
            fresh += 1
            failed += status != 'complete'
            print(f"[{fresh} new | {job['job_id']} | {job['model']}] {status} | recorded total ${budget.spent:.4f}", flush=True)
            if stop_reason or budget.hard_stop():
                stop_reason = stop_reason or 'Shared operating budget reached.'
                break
        total = ledger_state(result_dir)
        completed = terminal_failures = 0
        for job in manifest['jobs']:
            _, terminal = known_resume_records(result_dir/'jobs'/job['job_id'], job, block_nonretryable=False)
            if terminal:
                completed += terminal['status'] == 'complete'
                terminal_failures += terminal['status'] == 'agent_failure'
        summary = {'status': 'complete' if completed + terminal_failures == len(manifest['jobs']) else 'stopped_or_incomplete',
                   'planned': len(manifest['jobs']), 'complete': completed, 'terminal_agent_failures': terminal_failures,
                   'new_attempts_this_invocation': fresh, 'resumed_terminal_jobs': resumed,
                   'cap_usd': cap_usd, 'operating_cap_usd': operating_cap, 'stop_reason': stop_reason, **total}
        atomic_json(result_dir/'summary.json', summary)
        return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--execute', action='store_true', help='Explicitly enable paid inference after user authorization.')
    ap.add_argument('--cap-usd', type=float, default=10, help='Total across all attempts/resumes, including prior spending; maximum 10.')
    args = ap.parse_args()
    if not math.isfinite(args.cap_usd) or not 0 < args.cap_usd <= 10:
        ap.error('--cap-usd must be finite, positive and at most USD 10.')
    manifest, contexts = validate_prepared()
    prior = ledger_state(RESULTS)
    overview = {'status': 'validated_offline_no_calls', 'planned_general_executions': len(manifest['jobs']),
                'estimated_total_usd': manifest['estimated_total_usd'], 'cap_usd': args.cap_usd,
                'operating_cap_usd': max(0.0, args.cap_usd - 2), 'prior_ledger': prior,
                'transport': 'zero internal HTTP retries; unknown billing or unresolved request halts all calls'}
    if not args.execute:
        print(json.dumps(overview, indent=2))
        return
    if prior['unknown_cost_calls'] or prior['unresolved_inflight_markers']:
        raise ReplayStopped('Unconfirmed billing prevents execution; no key read or request sent.')
    key = os.environ.get('OPENROUTER_API_KEY', '').strip()
    if not key:
        raise ReplayStopped('Set OPENROUTER_API_KEY in this terminal environment; never pass a key on the command line.')
    factory = lambda: OpenRouterClient(api_key=key, retries=0)
    summary = execute_prepared(manifest, contexts, RESULTS, args.cap_usd, factory)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ReplayStopped, AssertionError) as exc:
        # Only our own fixed validation messages, never API exceptions or keys.
        print(f'Stopped: {exc}', file=sys.stderr)
        raise SystemExit(2)
