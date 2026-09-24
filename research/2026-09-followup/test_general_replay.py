"""Offline end-to-end replay tests. No HTTP, API key, or production output writes."""
import copy
from contextlib import redirect_stdout
import io
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import run_general_replay as replay


class FakeClient:
    def __init__(self, frames):
        self.frames = iter(frames)
        self.before_attempt = None
        self.calls = []

    def chat(self, body):
        if self.before_attempt:
            self.before_attempt()
        self.calls.append(copy.deepcopy(body))
        frame = next(self.frames)
        if isinstance(frame, BaseException):
            raise frame
        return copy.deepcopy(frame)

    def stats_snapshot(self):
        return {'http_attempts': len(self.calls), 'retries': 0}


def response(model, assistant, cost=0.01, choices=True):
    return {'model': model, 'provider': 'OFFLINE_FAKE_NO_NETWORK',
            'usage': {'cost': cost, 'prompt_tokens': 10, 'completion_tokens': 10, 'total_tokens': 20},
            'choices': [{'finish_reason': 'tool_calls' if assistant.get('tool_calls') else 'stop', 'message': assistant}] if choices else []}


def frames(context, arm, cost=0.01):
    payload = context['payloads'][arm]
    model = payload['model']
    reference = context['audit']['common_unapproved_general_reference']
    case_dir = replay.prep.DEFAULT_DATA/context['pair']['case']
    snapshot = replay.prep.load(case_dir/'gate_evidence/general/review_facts.json')
    answer = {'disposition': reference['disposition'], 'finding_ids': [f['id'] for f in reference['findings']],
              'actions': [a['action'] for a in reference['required_actions']],
              'authorization_required': reference['authorization_required'], 'evidence_refs': ['REVIEW_FACTS_GENERAL', 'UPSTREAM_DECISIONS'],
              'evidence_support': [], 'rationale': 'OFFLINE TEST ONLY', 'confidence': 1.0}
    for finding in reference['findings']:
        upstream = finding['id'].startswith('GEN-UPSTREAM-')
        answer['evidence_support'].append({'finding_id': finding['id'],
            'evidence_id': 'UPSTREAM_DECISIONS' if upstream else 'REVIEW_FACTS_GENERAL',
            'quote': json.dumps(payload['tool_upstream'] if upstream else snapshot, ensure_ascii=False)})
    reads = [{'type': 'function', 'id': f'read-{i}', 'function': {'name': 'read_evidence', 'arguments': json.dumps({'evidence_id': eid})}}
             for i, eid in enumerate(['REVIEW_FACTS_GENERAL', 'UPSTREAM_DECISIONS'])]
    submit = [{'type': 'function', 'id': 'submit', 'function': {'name': 'submit_gate_decision', 'arguments': json.dumps(answer)}}]
    return [response(model, {'role': 'assistant', 'content': None, 'tool_calls': reads}, cost),
            response(model, {'role': 'assistant', 'content': None, 'tool_calls': submit}, cost)]


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.contexts = replay.validate_prepared()

    def mini(self, count=1):
        result = copy.deepcopy(self.manifest)
        result['jobs'] = result['jobs'][:count]
        return result

    def run_silent(self, *args, **kwargs):
        with redirect_stdout(io.StringIO()):
            return replay.execute_prepared(*args, **kwargs)

    def test_prepared_payloads_have_only_allowed_history_difference(self):
        self.assertEqual(len(self.manifest['jobs']), 270)
        self.assertEqual(len(self.contexts), 45)
        for context in self.contexts.values():
            left, right = context['payloads']['A'], context['payloads']['B']
            for field in ['model', 'initial_tools', 'agent_settings', 'model_capabilities_snapshot']:
                self.assertEqual(left[field], right[field])
            self.assertEqual(left['agent_settings']['http_retries'], 0)
            self.assertEqual(set(left['tool_upstream'][0]), replay.prep.IDENTITY_FIELDS | replay.prep.VARIABLE_FIELDS)

    def test_dry_run_does_not_access_key_or_construct_client(self):
        original_get = replay.os.environ.get
        def guarded_get(key, *args):
            if key == 'OPENROUTER_API_KEY':
                raise AssertionError('API key must not be read')
            return original_get(key, *args)
        with mock.patch.object(replay, 'validate_prepared', return_value=(self.manifest, self.contexts)), \
             mock.patch.object(replay.os.environ, 'get', side_effect=guarded_get), \
             mock.patch.object(replay, 'OpenRouterClient', side_effect=AssertionError('No network client')), \
             mock.patch.object(replay.sys, 'argv', ['run_general_replay.py']), redirect_stdout(io.StringIO()) as output:
            replay.main()
        self.assertIn('validated_offline_no_calls', output.getvalue())

    def test_full_frozen_runner_tools_common_target_and_idempotent_resume(self):
        manifest = self.mini(2)
        context = self.contexts[manifest['jobs'][0]['pair_id']]
        self.assertEqual(manifest['jobs'][0]['pair_id'], manifest['jobs'][1]['pair_id'])
        clients = [FakeClient(frames(context, job['arm_code'])) for job in manifest['jobs']]
        iterator = iter(clients)
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            result = self.run_silent(manifest, self.contexts, folder, 10, lambda: next(iterator))
            self.assertEqual(result['complete'], 2)
            self.assertAlmostEqual(result['cost_usd'], .04)
            checks = [replay.prep.load(p) for p in sorted(folder.glob('jobs/*/attempt_*/checkpoint.json'))]
            self.assertEqual(checks[0]['scoring']['common_unapproved_reference'], checks[1]['scoring']['common_unapproved_reference'])
            for check in checks:
                self.assertEqual(check['scoring']['common_target_score']['decision'], 1)
                history = next(e['result']['content'] for e in check['record']['tool_trace'] if e['args'].get('evidence_id') == 'UPSTREAM_DECISIONS')
                self.assertEqual(history, context['payloads'][check['arm_code']]['tool_upstream'])
            second = self.run_silent(manifest, self.contexts, folder, 10, lambda: self.fail('Completed jobs must not call a client'))
            self.assertEqual(second['new_attempts_this_invocation'], 0)
            self.assertEqual(second['resumed_terminal_jobs'], 2)
            self.assertAlmostEqual(second['cost_usd'], .04)
            self.assertEqual(replay.ledger_state(folder)['ledger_responses'], 4)

    def test_budget_charges_each_response_and_resume_counts_prior_spend(self):
        manifest = self.mini()
        job = manifest['jobs'][0]
        client = FakeClient(frames(self.contexts[job['pair_id']], job['arm_code'], cost=.6))
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            result = self.run_silent(manifest, self.contexts, folder, 2.5, lambda: client)
            self.assertEqual(len(client.calls), 1)
            self.assertAlmostEqual(result['cost_usd'], .6)
            self.assertEqual(result['complete'], 0)
            resumed = self.run_silent(manifest, self.contexts, folder, 2.5, lambda: self.fail('No additional admission under exhausted cap'))
            self.assertEqual(resumed['new_attempts_this_invocation'], 0)
            self.assertAlmostEqual(resumed['cost_usd'], .6)

    def test_known_cost_infrastructure_failure_is_retained_and_resume_retries_fresh(self):
        manifest = self.mini()
        job = manifest['jobs'][0]
        context = self.contexts[job['pair_id']]
        failed = FakeClient([response(job['model'], {}, cost=.12, choices=False)])
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            first = self.run_silent(manifest, self.contexts, folder, 10, lambda: failed)
            self.assertEqual(first['complete'], 0)
            self.assertAlmostEqual(first['cost_usd'], .12)
            success = FakeClient(frames(context, job['arm_code']))
            second = self.run_silent(manifest, self.contexts, folder, 10, lambda: success)
            self.assertEqual(second['complete'], 1)
            self.assertAlmostEqual(second['cost_usd'], .14)
            paths = sorted(folder.glob('jobs/*/attempt_*/checkpoint.json'))
            self.assertEqual(len(paths), 2)
            self.assertEqual(replay.prep.load(paths[0])['status'], 'infrastructure_error')
            self.assertEqual(replay.prep.load(paths[1])['status'], 'complete')
            self.assertEqual(len(list(folder.glob('jobs/*/attempt_*/environment'))), 2)

    def test_missing_cost_stops_all_future_requests_and_resume(self):
        manifest = self.mini()
        job = manifest['jobs'][0]
        values = frames(self.contexts[job['pair_id']], job['arm_code'])
        del values[0]['usage']['cost']
        client = FakeClient(values)
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            result = self.run_silent(manifest, self.contexts, folder, 10, lambda: client)
            self.assertEqual(len(client.calls), 1)
            self.assertEqual(result['unknown_cost_calls'], 1)
            self.assertEqual(result['complete'], 0)
            with self.assertRaises(replay.ReplayStopped):
                self.run_silent(manifest, self.contexts, folder, 10, lambda: self.fail('Unknown billing must block'))

    def test_transport_failure_is_accounted_as_unknown_once(self):
        manifest = self.mini()
        for failure in [replay.OpenRouterError('synthetic network error'), replay.BillingUnknown('synthetic invalid response')]:
            with self.subTest(type=type(failure).__name__), tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)
                client = FakeClient([failure])
                result = self.run_silent(manifest, self.contexts, folder, 10, lambda: client)
                self.assertEqual(result['unknown_cost_calls'], 1)
                self.assertEqual(result['ledger_responses'], 1)
                self.assertEqual(result['unresolved_inflight_markers'], [])

    def test_interruption_retains_marker_and_blocks_retry(self):
        manifest = self.mini()
        client = FakeClient([KeyboardInterrupt()])
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with self.assertRaises(KeyboardInterrupt):
                self.run_silent(manifest, self.contexts, folder, 10, lambda: client)
            self.assertEqual(len(replay.ledger_state(folder)['unresolved_inflight_markers']), 1)
            with self.assertRaises(replay.ReplayStopped):
                self.run_silent(manifest, self.contexts, folder, 10, lambda: self.fail('Uncertain interrupted request must not retry'))

    def test_runtime_payload_guard_rejects_unexpected_prompt_before_call(self):
        job = self.manifest['jobs'][0]
        context = self.contexts[job['pair_id']]
        fake = FakeClient([])
        with tempfile.TemporaryDirectory() as temporary:
            client = replay.DurableBudgetedClient(fake, replay.CostBudget(8), job['job_id'], Path(temporary), context['payloads'][job['arm_code']])
            with self.assertRaises(replay.ReplayStopped):
                client.chat({'model': job['model'], 'messages': [{'role': 'user', 'content': 'unexpected'}]})
            self.assertFalse(fake.calls)
            self.assertFalse(list(Path(temporary).glob('inflight.json')))

    def test_invalid_ledger_and_invalid_cap_refuse_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            path = folder/'jobs/test/attempt_001/usage_ledger.jsonl'
            path.parent.mkdir(parents=True)
            path.write_text('{"cost":', encoding='utf-8')
            with self.assertRaises(replay.ReplayStopped):
                replay.ledger_state(folder)
            for cap in [float('nan'), float('inf'), 0, 10.01, 20, True]:
                with self.assertRaises(ValueError):
                    self.run_silent(self.mini(), self.contexts, folder, cap, lambda: self.fail('Invalid budget'))

    def test_scoring_failure_resumes_offline_without_new_inference(self):
        manifest = self.mini()
        job = manifest['jobs'][0]
        client = FakeClient(frames(self.contexts[job['pair_id']], job['arm_code']))
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with mock.patch.object(replay, 'score_fresh_record', side_effect=RuntimeError('Synthetic local scoring crash')):
                with self.assertRaises(RuntimeError):
                    self.run_silent(manifest, self.contexts, folder, 10, lambda: client)
            self.assertEqual(len(client.calls), 2)
            self.assertEqual(len(list(folder.glob('jobs/*/attempt_*/raw_record.json'))), 1)
            self.assertEqual(len(list(folder.glob('jobs/*/attempt_*/checkpoint.json'))), 0)
            result = self.run_silent(manifest, self.contexts, folder, 10, lambda: self.fail('Scoring-only resume must not infer'))
            self.assertEqual(result['complete'], 1)
            self.assertEqual(result['new_attempts_this_invocation'], 0)
            self.assertAlmostEqual(result['cost_usd'], .02)

    def test_orphan_paid_reply_without_raw_record_blocks_automatic_retry(self):
        manifest = self.mini()
        job = manifest['jobs'][0]
        context = self.contexts[job['pair_id']]
        client = FakeClient(frames(context, job['arm_code']))
        def crash_after_response(wrapped, *args):
            body = {'model': job['model'], 'messages': context['payloads'][job['arm_code']]['messages'],
                    'tools': context['payloads'][job['arm_code']]['initial_tools']}
            wrapped.chat(body)
            raise RuntimeError('Synthetic local crash before raw trajectory return')
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with self.assertRaises(RuntimeError):
                self.run_silent(manifest, self.contexts, folder, 10, lambda: client, runner=crash_after_response)
            self.assertEqual(len(list(folder.glob('jobs/*/attempt_*/responses/*.json'))), 1)
            self.assertEqual(replay.ledger_state(folder)['unresolved_inflight_markers'], [])
            with self.assertRaises(replay.ReplayStopped):
                self.run_silent(manifest, self.contexts, folder, 10, lambda: self.fail('Paid orphan must not infer'))

    def test_terminal_protocol_failure_is_not_retried_for_a_better_answer(self):
        manifest = self.mini()
        job = manifest['jobs'][0]
        context = self.contexts[job['pair_id']]
        client = FakeClient(frames(context, job['arm_code']))
        def protocol_failure(wrapped, *args):
            payload = context['payloads'][job['arm_code']]
            wrapped.chat({'model': job['model'], 'messages': payload['messages'], 'tools': payload['initial_tools']})
            raise replay.AgentRunError('Offline protocol failure', kind='agent_protocol',
                                       record={'usage': {'cost': .01}, 'tool_trace': [], 'raw_turns': []})
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            first = self.run_silent(manifest, self.contexts, folder, 10, lambda: client, runner=protocol_failure)
            self.assertEqual(first['terminal_agent_failures'], 1)
            second = self.run_silent(manifest, self.contexts, folder, 10, lambda: self.fail('Terminal protocol failure must remain an outcome'))
            self.assertEqual(second['terminal_agent_failures'], 1)
            self.assertEqual(second['new_attempts_this_invocation'], 0)

    def test_native_run_lock_blocks_concurrent_budget_owners(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with replay.exclusive_run_lock(folder):
                with self.assertRaises(replay.ReplayStopped):
                    with replay.exclusive_run_lock(folder):
                        self.fail('Second runner must not acquire the spending lock')

    def test_prepared_hashes_ignore_generated_json_line_endings(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)/'prepared'
            shutil.copytree(replay.PREPARED, folder)
            for index, path in enumerate(sorted(folder.rglob('*.json'))):
                text = path.read_text(encoding='utf-8')
                path.write_bytes(text.replace('\n', '\r\n' if index % 2 else '\n').encode('utf-8'))
            manifest, contexts = replay.validate_prepared(folder)
            self.assertEqual(manifest, self.manifest)
            self.assertEqual(len(contexts), 45)

    def test_preparation_preserves_identical_existing_file_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'value.json'
            value = {'x': 'é', 'n': 1}
            text = json.dumps(value, indent=2, ensure_ascii=False)+'\n'
            path.write_bytes(text.replace('\n', '\r\n').encode('utf-8'))
            before = path.read_bytes()
            replay.prep.dump(path, value)
            self.assertEqual(path.read_bytes(), before)

    def test_portable_dataset_hash_uses_explicit_posix_sort(self):
        with tempfile.TemporaryDirectory() as temporary:
            case = Path(temporary)/'CASE'
            case.mkdir()
            (case/'a.txt').write_bytes(b'lower')
            (case/'Z.txt').write_bytes(b'upper')
            expected = [['CASE', 'Z.txt', replay.prep.hash_file(case/'Z.txt')],
                        ['CASE', 'a.txt', replay.prep.hash_file(case/'a.txt')]]
            self.assertEqual(replay.prep.portable_dataset_fingerprint([case]), replay.prep.hash_obj(expected))


if __name__ == '__main__':
    unittest.main()
