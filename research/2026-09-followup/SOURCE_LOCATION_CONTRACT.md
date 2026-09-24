# Source-location evidence contract: offline prototype

Version: `DGF-evidence-location-v1-dev`. Status: **implemented and unit-tested as a prototype; not integrated into a paid benchmark run**. Historical traces and scores are unchanged.

The agent designates the source observation and a location. The harness copies the value; the agent does not retype it. This removes field-order and number-format reconstruction from the citation task and permits a CSV, document, or JSON source actually read through an authorized tool.

1. The trusted harness registers a successful public tool response in `ObservationStore`, retaining an immutable copy and a content hash. Registration is never a model-callable tool; arbitrary model text must never be registered as an observation.
2. The response includes an observation identifier. A later revision of the same source receives another identifier, preserving which version was read.
3. For JSON and CSV-as-rows, the model supplies an RFC 6901 JSON pointer, such as `/1/due_diligence`. For extracted document text, it supplies a half-open `[start, end)` span in Unicode code points, relative to the actual observed text. A future UI may expose stable block/line identifiers to make selection easier; those are not silently inferred here.
4. The resolver returns the source ID, observation digest, location, and copied value/quote. It rejects unobserved IDs, missing paths, invalid spans, injected quote fields, and oversized selections. Values retain their observed types, including CSV strings.
5. Separate scoring must check whether these values concern the selected entity, cover the required premises, and support the claimed finding. `provenance_verified` does **not** mean `semantic_support`; the latter is explicitly `NOT_EVALUATED`.

The prototype accepts sources without privileging `REVIEW_FACTS`. It grants no additional source access and does not treat a stale or non-authoritative source as correct merely because its quote is faithful. Availability, freshness, conflicts, policy judgment, and authorization remain separate checks.

```powershell
python -m unittest discover -s research/2026-09-followup -p test_source_location_contract.py
```

The tests cover CSV citations, source revisions, immutability, unseen sources, Unicode spans, pointer escaping, types, nonexistent paths, and quote-size limits. The new contract still needs integration with prompts, tool schemas, access logs, and a versioned finding-support evaluator before any factorial comparison. No old score is recalculated with this contract.
