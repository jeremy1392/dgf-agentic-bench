"""Trace-based Procurement excerpt diagnostics; no model calls or score changes.

Do not equate a failed JSON parser with false evidence. This separately checks
literal provenance, complete scalar field/value occurrence, and the frozen
REVIEW_FACTS-only source requirement. Scalar matches are not semantic entailment.
"""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

import audit_evidence as audit

ROOT = audit.ROOT
SCALAR = r'"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"|true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?'
PAIR = re.compile(r'("(?:[^"\\]|\\.)*")\s*:\s*(' + SCALAR + r')(?=\s*(?:[,}\];]|\.\.\.|$))')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def scalar_pairs(quote):
    """Extract only syntactically complete JSON scalar pairs, retaining duplicates."""
    pairs = []
    for match in PAIR.finditer(quote or ''):
        try:
            pairs.append({'field': json.loads(match[1]), 'value': json.loads(match[2]),
                          'quote_span': [match.start(), match.end()]})
        except ValueError:
            pass
    return pairs


def locations(field, value, source, path='$'):
    found = []
    if isinstance(source, dict):
        if field in source and audit.subset(value, source[field]):
            found.append(path + '/' + field)
        for key, child in source.items():
            found.extend(locations(field, value, child, path + '/' + str(key)))
    elif isinstance(source, list):
        for index, child in enumerate(source):
            found.extend(locations(field, value, child, path + '/' + str(index)))
    return found


def value_locations(value, source, path='$'):
    """Diagnostic for unparsed prose: string occurrence alone proves no relation."""
    found = [path] if audit.subset(value, source) else []
    children = source.items() if isinstance(source, dict) else enumerate(source) if isinstance(source, list) else []
    for key, child in children:
        found.extend(value_locations(value, child, path + '/' + str(key)))
    return found


def inspect_source(quote, pairs, result):
    content = result['content']
    paths = [locations(p['field'], p['value'], content) for p in pairs]
    return {'path': result.get('path'), 'authoritative': result.get('authoritative'),
            'exact_quote_substring': bool(quote) and quote in source_text(content),
            'all_scalar_pairs_present': bool(pairs) and all(paths),
            'scalar_pair_paths': paths}


def controls():
    assert scalar_pairs('"a": 10 ... "b": false; selected offer: "vendor": "A"') == [
        {'field': 'a', 'value': 10, 'quote_span': [0, 7]},
        {'field': 'b', 'value': False, 'quote_span': [12, 22]},
        {'field': 'vendor', 'value': 'A', 'quote_span': [40, 53]}]
    assert locations('n', 10, {'n': 100}) == []
    assert locations('n', True, {'n': 1}) == []
    assert locations('n', 10, {'n': '10'}) == []
    assert locations('n', 10, {'n': 10.0}) == ['$/n']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', type=Path, default=ROOT/'experiments/run_20260922_214402_941347/results')
    ap.add_argument('--dataset', type=Path, default=audit.DATA)
    ap.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()
    controls()
    details = []
    model_counts = {}
    for modeldir in sorted(args.run_dir.iterdir()):
        if not modeldir.is_dir():
            continue
        counts = collections.Counter()
        classifications = collections.Counter()
        references = collections.Counter()
        original_classes = collections.Counter()
        model = None
        for folder in sorted(modeldir.glob('DGF-*')):
            score_path = folder/'score.json'
            if not score_path.exists():
                continue
            score = json.loads(score_path.read_text(encoding='utf-8'))
            if score.get('status') not in ['OK', 'AGENT_FAILURE'] or not score.get('occurrences'):
                continue
            model = score['model']
            for row in score['occurrences']:
                if row['gate'] != 'procurement':
                    continue
                counts['all_procurement_gates'] += 1
                if row['evidence_fidelity'] == 1:
                    continue
                counts['evidence_failed_gates'] += 1
                oid = row['occurrence_id']
                record_path = next(folder.glob('*_' + oid + '.json'))
                record = json.loads(record_path.read_text(encoding='utf-8'))
                pred = record['result']
                route = json.loads((args.dataset/folder.name/'01_route_manifest.json').read_text(encoding='utf-8'))
                occurrence = next(o for o in route['occurrences'] if o['occurrence_id'] == oid)
                reader = audit.PublicEvidenceReader(args.dataset/folder.name, 'procurement', occurrence['phase'])
                available = {}
                for eid in reader.nodes:
                    value = reader.read_evidence(eid)
                    if value.get('status') == 'OK':
                        available[eid] = value
                observed = {}
                invalid_events = []
                for index, event in enumerate(record.get('tool_trace', [])):
                    result = event.get('result')
                    if event.get('tool') not in ['read_evidence', 'request_evidence'] or not isinstance(result, dict):
                        continue
                    if result.get('status') not in ['OK', 'RECEIVED']:
                        continue
                    eid = result.get('evidence_id')
                    if eid == 'UPSTREAM_DECISIONS':
                        continue  # Dynamic handoff is not a Procurement source artifact.
                    if eid in available and result.get('content') == available[eid]['content']:
                        observed[eid] = dict(available[eid], tool_trace_index=index)
                    else:
                        invalid_events.append({'tool_trace_index': index, 'evidence_id': eid})
                failed_fids = [d['finding_id'] for d in row['evidence_diagnostics'] if 'finding_id' in d]
                items = []
                counts['failed_findings'] += len(failed_fids)
                gate_has_exact_csv = False
                for fid in failed_fids:
                    supports = [s for s in pred.get('evidence_support', []) if s.get('finding_id') == fid]
                    if not supports:
                        counts['missing_support_findings'] += 1
                    finding_has_exact_csv = False
                    finding_has_exact_cited_csv = False
                    finding_values = []
                    for support_index, support in enumerate(supports):
                        counts['submitted_support_entries'] += 1
                        eid = support.get('evidence_id')
                        quote = support.get('quote', '')
                        pairs = scalar_pairs(quote)
                        observed_checks = {key: inspect_source(quote, pairs, value) for key, value in observed.items()}
                        unread_checks = {key: inspect_source(quote, pairs, value) for key, value in available.items() if key not in observed}
                        exact = [key for key, value in observed_checks.items() if value['exact_quote_substring']]
                        values = [key for key, value in observed_checks.items() if value['all_scalar_pairs_present']]
                        unread_exact = [key for key, value in unread_checks.items() if value['exact_quote_substring']]
                        unread_values = [key for key, value in unread_checks.items() if value['all_scalar_pairs_present']]
                        exact_documents = [key for key in exact if Path(observed[key]['path']).suffix.lower() in ['.csv', '.docx']]
                        category = ('exact_quote_in_observed_source' if exact else
                                    'all_extracted_scalar_pairs_in_observed_source_not_literal_quote' if values else
                                    'matching_available_source_not_observed' if unread_exact or unread_values else
                                    'no_literal_or_complete_scalar_pair_match')
                        if eid not in reader.nodes:
                            reference = 'unknown_source_identifier'
                        elif eid not in observed:
                            reference = 'known_source_not_observed'
                        elif eid not in pred.get('evidence_refs', []):
                            reference = 'observed_source_omitted_from_evidence_refs'
                        elif eid != 'REVIEW_FACTS_PROCUREMENT':
                            reference = 'observed_cited_source_excluded_by_snapshot_only_contract'
                        else:
                            reference = 'observed_cited_required_snapshot'
                        classifications[category] += 1
                        references[reference] += 1
                        if exact_documents:
                            counts['entries_exact_in_observed_csv_or_docx'] += 1
                            finding_has_exact_csv = True
                        if eid in exact_documents and eid in pred.get('evidence_refs', []):
                            counts['entries_exact_in_own_observed_cited_csv_or_docx'] += 1
                            finding_has_exact_cited_csv = True
                            parsed = audit.parse_fragment(quote)
                            procurement = observed.get('REVIEW_FACTS_PROCUREMENT', {}).get('content', {}).get('procurement', {})
                            if parsed and parsed.get('vendor') == procurement.get('selected_vendor'):
                                counts['exact_csv_entries_identifying_observed_selected_vendor'] += 1
                        if eid in exact:
                            counts['entries_exact_in_own_observed_cited_source'] += 1
                        if eid in values:
                            counts['entries_all_extracted_scalar_pairs_in_own_observed_source'] += 1
                        if audit.parse_fragment(quote) is None:
                            original_classes['not_parseable_as_object_fragment'] += 1
                            original_classes['nonparseable_' + category] += 1
                        else:
                            original_classes['parseable_object_fragment'] += 1
                        item = {'finding_id': fid, 'support_index': support_index, 'evidence_id': eid,
                                'quote': quote, 'classification': category, 'reference_status': reference,
                                'parseable_as_object_fragment': audit.parse_fragment(quote) is not None,
                                'scalar_pairs': pairs, 'exact_observed_sources': exact,
                                'all_scalar_pairs_observed_sources': values,
                                'exact_observed_csv_or_docx_sources': exact_documents,
                                'unread_exact_sources': unread_exact, 'unread_scalar_pair_sources': unread_values,
                                'observed_source_checks': observed_checks,
                                'unread_matching_source_checks': {key: unread_checks[key] for key in sorted(set(unread_exact + unread_values))}}
                        if not pairs:
                            quoted = re.findall(r'"((?:[^"\\]|\\.)*)"', quote)
                            item['unparsed_prose_quoted_string_locations'] = [
                                {'string': value, 'sources': {key: value_locations(value, src['content']) for key, src in observed.items() if value_locations(value, src['content'])}}
                                for value in quoted]
                        finding_values.append(item)
                    if finding_has_exact_csv:
                        counts['failed_findings_with_exact_observed_csv_or_docx_alternative'] += 1
                        gate_has_exact_csv = True
                    if finding_has_exact_cited_csv:
                        counts['failed_findings_with_exact_own_observed_cited_csv_or_docx'] += 1
                    items.append({'finding_id': fid, 'support_items': finding_values})
                if gate_has_exact_csv:
                    counts['gates_with_exact_observed_csv_or_docx_alternative'] += 1
                assert not invalid_events, (folder, invalid_events)
                details.append({'model': model, 'case': folder.name, 'occurrence_id': oid,
                                'trace': record_path.relative_to(ROOT).as_posix(),
                                'trace_sha256': digest(record_path), 'score_sha256': digest(score_path),
                                'original_evidence_score': row['evidence_fidelity'],
                                'evidence_refs': pred.get('evidence_refs', []),
                                'observed_sources': {key: {k: value[k] for k in ['path', 'authoritative', 'tool_trace_index']} for key, value in observed.items()},
                                'selected_vendor_from_observed_snapshot': observed.get('REVIEW_FACTS_PROCUREMENT', {}).get('content', {}).get('procurement', {}).get('selected_vendor'),
                                'failed_findings': items})
        if model:
            for key in ['missing_support_findings', 'entries_exact_in_observed_csv_or_docx',
                        'entries_exact_in_own_observed_cited_csv_or_docx',
                        'failed_findings_with_exact_observed_csv_or_docx_alternative',
                        'failed_findings_with_exact_own_observed_cited_csv_or_docx',
                        'gates_with_exact_observed_csv_or_docx_alternative',
                        'exact_csv_entries_identifying_observed_selected_vendor',
                        'entries_exact_in_own_observed_cited_source',
                        'entries_all_extracted_scalar_pairs_in_own_observed_source']:
                counts.setdefault(key, 0)
            for key in ['exact_quote_in_observed_source',
                        'all_extracted_scalar_pairs_in_observed_source_not_literal_quote',
                        'matching_available_source_not_observed',
                        'no_literal_or_complete_scalar_pair_match']:
                classifications.setdefault(key, 0)
            model_counts[model] = {'counts': dict(counts), 'support_classifications': dict(classifications),
                                   'source_reference_status': dict(references), 'parser_crosscheck': dict(original_classes)}
    summary = {
        'scope': 'Every originally evidence-failed Procurement occurrence in all 899 evaluable original model-case runs; failed finding diagnostics only. Includes all support alternatives, not only the first support.',
        'observation_method': 'Only read_evidence/request_evidence OK/RECEIVED results in the saved final checkpoint whose contents equal immutable PublicEvidenceReader outputs. Dynamic UPSTREAM_DECISIONS is excluded from this Procurement artifact audit. The frozen agent_runner returns at final submission before executing other tool calls in the same batch, so saved trace results precede final submission. Available but unread sources are recorded separately.',
        'matching_method': 'Literal quote substring in actual returned content serialized exactly as agent_runner JSON dumps (or extracted document text). Separately extract complete JSON scalar field/value pairs even from excerpts with ellipses/prose; locate every pair with strict type/value matching (numeric 30 equals 30.0; boolean is not numeric; CSV string 30 is not number 30). Retain all paths and duplicates; no source reads invented.',
        'limits': 'Pair occurrence is not full quote fidelity, correct association of fields across objects, full rule premise coverage, semantic entailment, or independent adjudication. A quote can have individually real values but misleading relationships. A valid observed CSV quote can still violate the original instructed snapshot-only support contract. No primary or post-hoc relaxed scores changed.',
        'models': model_counts,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'procurement_source_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (args.output_dir/'procurement_source_items.json').write_text(json.dumps(details, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
