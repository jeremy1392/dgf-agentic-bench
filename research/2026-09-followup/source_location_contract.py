"""Prototype evidence contract for a new experiment, never a rescorer of old runs.

The trusted harness registers successful public tool observations. A model supplies
an observation id and a JSON pointer or text span; the harness copies the value.
Provenance acceptance alone does not establish relevance or semantic entailment.
"""
import copy
import hashlib
import json
import re

VERSION = 'DGF-evidence-location-v1-dev'


class CitationError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      allow_nan=False)


def pointer_value(content, pointer):
    if not isinstance(pointer, str) or not pointer.startswith('/'):
        raise CitationError('Supply a non-root RFC 6901 JSON pointer.')
    value = content
    for raw in pointer[1:].split('/'):
        if re.search(r'~(?![01])', raw):
            raise CitationError('Invalid JSON pointer escape.')
        key = raw.replace('~1', '/').replace('~0', '~')
        if isinstance(value, dict):
            if key not in value:
                raise CitationError('Missing object key.')
            value = value[key]
        elif isinstance(value, list):
            if not re.fullmatch(r'0|[1-9][0-9]*', key):
                raise CitationError('Invalid array index.')
            upper = str(len(value) - 1)
            if not value or len(key) > len(upper) or (len(key) == len(upper) and key > upper):
                raise CitationError('Array index outside observation.')
            index = int(key)
            if index >= len(value):
                raise CitationError('Array index outside observation.')
            value = value[index]
        else:
            raise CitationError('Pointer traverses a scalar.')
    return copy.deepcopy(value)


class ObservationStore:
    def __init__(self, max_value_chars=2048):
        if type(max_value_chars) is not int or max_value_chars < 1:
            raise ValueError('Positive integer length required.')
        self.max_value_chars = max_value_chars
        self._observations = {}

    def register_public_tool_result(self, result):
        """Harness-only: result must come from its access-controlled public reader.

        This method must never be exposed as a model-callable tool. It does not
        authenticate arbitrary model-supplied dictionaries or grant file access.
        """
        if (not isinstance(result, dict) or result.get('status') not in {'OK', 'RECEIVED'}
                or not isinstance(result.get('evidence_id'), str)
                or not result['evidence_id'] or 'content' not in result):
            raise CitationError('Successful public observation required.')
        stored = copy.deepcopy({key: result[key] for key in
                               ('evidence_id', 'content', 'version', 'path', 'authoritative',
                                'age_days', 'gate', 'phase') if key in result})
        digest = hashlib.sha256(canonical(stored).encode('utf-8')).hexdigest()
        observation_id = f'obs-{len(self._observations) + 1:06d}-{digest[:16]}'
        self._observations[observation_id] = (stored, digest)
        return {'observation_id': observation_id, 'evidence_id': stored['evidence_id'],
                'observation_sha256': digest, 'contract_version': VERSION}

    def resolve(self, observation_id, selector):
        if not isinstance(observation_id, str) or observation_id not in self._observations:
            raise CitationError('Source was not observed in this store.')
        if not isinstance(selector, dict):
            raise CitationError('Selector must be an object.')
        stored, digest = self._observations[observation_id]
        content = stored['content']
        if isinstance(content, (dict, list)):
            if set(selector) != {'json_pointer'}:
                raise CitationError('JSON/CSV observations require only json_pointer.')
            value = pointer_value(content, selector['json_pointer'])
            quote = canonical(value)
        elif isinstance(content, str):
            if set(selector) != {'start', 'end'}:
                raise CitationError('Text observations require start and end offsets.')
            start, end = selector['start'], selector['end']
            if (type(start) is not int or type(end) is not int
                    or not 0 <= start < end <= len(content)):
                raise CitationError('Invalid Unicode-code-point span.')
            value = quote = content[start:end]
        else:
            raise CitationError('This content representation is unsupported.')
        if len(quote) > self.max_value_chars:
            raise CitationError('Select a smaller value or span.')
        return {'contract_version': VERSION, 'observation_id': observation_id,
                'evidence_id': stored['evidence_id'], 'observation_sha256': digest,
                'selector': copy.deepcopy(selector), 'value': value, 'quote': quote,
                'provenance_verified': True,
                'semantic_support': 'NOT_EVALUATED'}
