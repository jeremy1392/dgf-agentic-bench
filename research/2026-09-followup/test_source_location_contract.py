"""Offline contract tests: access, immutable observations and exact copied values."""
import unittest
from source_location_contract import CitationError, ObservationStore


class ContractTests(unittest.TestCase):
    def test_csv_source_is_accepted_without_snapshot(self):
        store = ObservationStore()
        ref = store.register_public_tool_result({'status': 'OK', 'evidence_id': 'DUE_DILIGENCE',
              'content': [{'vendor': 'A', 'due_diligence': 'pending'},
                          {'vendor': 'B', 'due_diligence': 'complete'}]})
        citation = store.resolve(ref['observation_id'], {'json_pointer': '/1/due_diligence'})
        self.assertEqual(citation['value'], 'complete')
        self.assertEqual(citation['evidence_id'], 'DUE_DILIGENCE')
        self.assertEqual(citation['semantic_support'], 'NOT_EVALUATED')

    def test_observation_and_return_value_cannot_be_mutated(self):
        store = ObservationStore()
        result = {'status': 'OK', 'evidence_id': 'X', 'content': {'nested': {'value': 3}}}
        oid = store.register_public_tool_result(result)['observation_id']
        result['content']['nested']['value'] = 9
        first = store.resolve(oid, {'json_pointer': '/nested'})
        first['value']['value'] = 8
        self.assertEqual(store.resolve(oid, {'json_pointer': '/nested/value'})['value'], 3)

    def test_source_revision_keeps_old_observation(self):
        store = ObservationStore()
        ids = [store.register_public_tool_result({'status': 'OK', 'evidence_id': 'X',
                 'version': v, 'content': {'status': state}})['observation_id']
               for v, state in [(1, 'pending'), (2, 'complete')]]
        self.assertNotEqual(*ids)
        self.assertEqual(store.resolve(ids[0], {'json_pointer': '/status'})['value'], 'pending')

    def test_refuses_unread_and_failed_sources(self):
        store = ObservationStore()
        with self.assertRaises(CitationError):
            store.resolve('invented', {'json_pointer': '/x'})
        for invalid_id in [[], {}, None, 1]:
            with self.assertRaises(CitationError):
                store.resolve(invalid_id, {'json_pointer': '/x'})
        with self.assertRaises(CitationError):
            store.register_public_tool_result({'status': 'MISSING', 'evidence_id': 'X', 'content': {}})

    def test_exact_unicode_text_span_and_no_quote_argument(self):
        store = ObservationStore()
        oid = store.register_public_tool_result({'status': 'OK', 'evidence_id': 'DOC',
                                                'content': 'Aé🙂 état signé'})['observation_id']
        self.assertEqual(store.resolve(oid, {'start': 1, 'end': 3})['quote'], 'é🙂')
        for selector in [{'start': -1, 'end': 2}, {'start': True, 'end': 2},
                         {'start': 3, 'end': 2}, {'start': 0, 'end': 2, 'quote': 'fake'}]:
            with self.assertRaises(CitationError):
                store.resolve(oid, selector)

    def test_pointer_escaping_types_and_invalid_paths(self):
        store = ObservationStore()
        oid = store.register_public_tool_result({'status': 'OK', 'evidence_id': 'JSON',
              'content': {'a/b': {'~': [False, 0, 1.0, None]}}})['observation_id']
        self.assertIs(store.resolve(oid, {'json_pointer': '/a~1b/~0/0'})['value'], False)
        self.assertEqual(type(store.resolve(oid, {'json_pointer': '/a~1b/~0/1'})['value']), int)
        for pointer in ['', '/a~2b', '/a~1b/~0/-1', '/a~1b/~0/01', '/a~1b/~0/4', '/absent']:
            with self.assertRaises(CitationError):
                store.resolve(oid, {'json_pointer': pointer})
        with self.assertRaises(CitationError):
            store.resolve(oid, {'json_pointer': '/a~1b/~0/' + '9' * 5000})

    def test_prevents_unbounded_entire_source_quote(self):
        store = ObservationStore(max_value_chars=12)
        oid = store.register_public_tool_result({'status': 'OK', 'evidence_id': 'X',
                    'content': {'large': 'x' * 100}})['observation_id']
        with self.assertRaises(CitationError):
            store.resolve(oid, {'json_pointer': '/large'})


if __name__ == '__main__':
    unittest.main()
