"""Package the offline audit and all generated counterexample artifacts; no API calls."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    spec = importlib.util.spec_from_file_location(
        'release_pack', ROOT / 'research/2026-09-dgf-bench/package_release.py')
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)
    artifact_root = ROOT / 'experiments/document_ablation_preflight_20260924'
    files = sorted(p for p in artifact_root.rglob('*') if p.is_file())
    assert len([p for p in files if p.suffix == '.docx']) == 52
    names = ['audit_all_models.py', 'audit_evidence.py', 'check_document_ablation.py',
             'package_evidence_audit.py', 'ALL_MODELS_AUDIT.md',
             'all_models_evidence_summary.json', 'all_models_evidence_items.json',
             'decision_confusion.csv', 'document_ablation_preflight.json']
    files += [HERE / name for name in names]
    files += [ROOT / 'paper2/protocols/scaffold_ablation.md']
    result = pack.build('dgf-bench-evidence-audit-20260924.zip', sorted(files), '')
    manifest = {
        'scope': 'All artifacts of both document counterexample variants, all-model audit records, analysis scripts, and proposed ablation protocol.',
        'model_calls': 0,
        'original_experiment_modified': False,
        'source_dependency': 'Immutable dgf-bench-300-source.zip, SHA-256 0729a91554f81c91b0bc935f12e7246b930d76dd755df168e56f86c1fd23ef95',
        'archive': result,
        'reproduction': 'Extract the original source, dataset and run following research/2026-09-dgf-bench/README.md; run the two audit scripts. DOCX text hashes exclude unstable document-container metadata.',
    }
    (HERE / 'evidence_audit_archive_manifest.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (HERE / 'evidence-audit-SHA256SUMS.txt').write_text(
        f"{result['sha256']}  {result['asset']}\n", encoding='utf-8')


if __name__ == '__main__':
    main()
