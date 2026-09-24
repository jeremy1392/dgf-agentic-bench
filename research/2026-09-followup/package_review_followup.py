"""Package offline review follow-ups, development dossiers and unrun preparations.

No model calls or data generation. Uses the original release secret scanner and
ZIP builder, including uncompressed DOCX XML scanning, CRC verification and a
per-file SHA-256 inventory. Human-review materials are explicitly excluded.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET='dgf-bench-review-followup-20260924.zip'
OUTPUT=ROOT/'experiments/publication_20260923'
PATTERNS=(
    'conditional_approval*','procurement_source*','repeat_evidence*','repetition_evidence*',
    'source_coverage*','source_location*','source_record_extensions*','general_replay*.json',
    'test_general_replay*.py',
)
REQUIRED=(
    'SOURCE_LOCATION_CONTRACT.md','test_source_location_contract.py',
    'GENERAL_REPLAY_PREPARATION.md','prepare_general_replay.py','scan_general_replay.py',
    'prepare_targeted_general_replay.py','run_general_replay.py','package_review_followup.py',
    # Local imports and frozen analysis inputs needed by the packaged scripts.
    'audit_all_models.py','audit_evidence.py','rules_baseline.py','repetition_plan.json',
    'repetition_results.json','repetition_analysis.json',
)
ARTIFACT_ROOTS=(
    ROOT/'experiments/scaffold_development_20260924',
    ROOT/'experiments/general_replay_prepared_20260924',
    ROOT/'experiments/general_replay_targeted_prepared_20260924',
)
DISALLOWED_PARTS={'__pycache__','.pytest_cache','qa','logs','test_results','test-output','test_output'}
DISALLOWED_SUFFIXES={'.pyc','.pyo','.log','.tmp','.key','.pem','.p12','.pfx'}


def allowed(path):
    relative=path.relative_to(ROOT)
    lower_parts=[part.lower() for part in relative.parts]
    if any('human_review' in part or 'human-review' in part for part in lower_parts):return False
    if any(part in DISALLOWED_PARTS for part in lower_parts):return False
    if path.suffix.lower()!='.py' and any(tag in path.stem.lower() for tag in ('_qa','qa_','test_log','test_result')):return False
    if path.suffix.lower() in DISALLOWED_SUFFIXES:return False
    if path.name.lower()=='.env' or path.name.lower().startswith('.env.'):return False
    return True


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def select_files():
    files={ROOT/'research/2026-09-dgf-bench/package_release.py'}
    for pattern in PATTERNS:
        matched=[p for p in HERE.glob(pattern) if p.is_file()]
        if pattern!='test_general_replay*.py' and not matched:
            raise FileNotFoundError('Expected follow-up pattern is empty: '+pattern)
        files.update(matched)
    for name in REQUIRED:
        path=HERE/name
        if not path.is_file():raise FileNotFoundError(path)
        files.add(path)
    # Explicitly require executable runner tests before calling this a ready archive.
    if not list(HERE.glob('test_general_replay*.py')):
        raise FileNotFoundError('Wait for the General runner test sources before packaging')
    counts={}
    for directory in ARTIFACT_ROOTS:
        if not directory.is_dir():raise FileNotFoundError(directory)
        included=[p for p in directory.rglob('*') if p.is_file() and allowed(p)]
        if not included:raise ValueError('Empty prepared artifact directory: '+str(directory))
        files.update(included)
        counts[directory.relative_to(ROOT).as_posix()]=len(included)
    return sorted(p for p in files if allowed(p)),counts


def validate_status():
    extension=load(HERE/'source_record_extensions_report.json')
    assert extension['purpose']=='DEVELOPMENT_NOT_EVALUATION'
    assert extension['model_calls']==0 and extension['held_out'] is False
    original=load(HERE/'general_replay_preflight.json')
    targeted=load(HERE/'general_replay_targeted_preflight.json')
    assert original['status']=='prepared_not_run' and original['paid_calls_made']==0
    assert targeted['status']=='prepared_not_authorized_not_run' and targeted['paid_calls_made']==0
    assert original['preflight']['passed'] and targeted['preflight']['passed']
    return extension,original,targeted


def main():
    extension,original,targeted=validate_status()
    files,artifact_counts=select_files()
    spec=importlib.util.spec_from_file_location('release_pack',ROOT/'research/2026-09-dgf-bench/package_release.py')
    pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
    pack.OUT=OUTPUT;OUTPUT.mkdir(parents=True,exist_ok=True)
    archive=pack.build(ASSET,files,'')
    with zipfile.ZipFile(OUTPUT/ASSET) as bundle:
        inventory=json.loads(bundle.read('FILE_MANIFEST.json'))
        assert len(inventory)==len(files)
        assert len({row['path'] for row in inventory})==len(files)
        assert all('human_review' not in name.lower() and 'human-review' not in name.lower() for name in bundle.namelist())
        assert not any('general_replay_targeted_results_' in name for name in bundle.namelist())
        assert bundle.testzip() is None
    manifest={
        'release_tag':'dgf-bench-300-20260923',
        'scope':'Offline conditional-approval, Procurement-source, repetition-evidence and source-coverage audits; source-location citation prototype and tests; two-field source-record extension prototype with every file of three new development dossiers; both General replay preparations, evaluator-only targets, executable runner and offline tests.',
        'archive':archive,'per_file_inventory':'FILE_MANIFEST.json inside the ZIP: SHA-256 and byte count for each archived source/artifact file',
        'artifact_directory_file_counts':artifact_counts,
        'offline_analyses':'Post-hoc analyses of existing original/repetition traces, not newly sampled model responses.',
        'development_examples':{'count':len(extension['development_cases']),'purpose':'DEVELOPMENT_NOT_EVALUATION','held_out':False,
            'scope':'Two targeted CSV additions only; not a certified complete ablation dataset.'},
        'general_preparations':[
            {'directory':'experiments/general_replay_prepared_20260924','status':original['status'],
             'planned_executions':original['planned_general_executions'],'paid_calls_made':0},
            {'directory':'experiments/general_replay_targeted_prepared_20260924','status':targeted['status'],
             'planned_executions':targeted['planned_general_executions'],'paid_calls_made':0}],
        'human_review_materials_included':False,'new_model_calls_made':0,'original_experiment_modified':False,
        'source_dependency':'Immutable dgf-bench-300-source.zip, SHA-256 0729a91554f81c91b0bc935f12e7246b930d76dd755df168e56f86c1fd23ef95',
        'other_dependencies':['Original dgf-bench-300 dataset/run archives and completed dgf-bench-repetitions-20260924.zip are separate release assets.',
            'Some scripts retain historical default absolute/relative extraction paths; use their explicit CLI path options where supported.'],
        'security_checks':['Release secret scanner applied to every included file and every XML part within DOCX files.',
            'No .env, private-key files, caches, QA logs, human-review materials or General paid-result directories included.',
            'ZIP CRC verification passed.'],
        'notes':['Evaluator-only prepared targets and development hidden truth are published for inspection but must never be supplied as model evidence.',
            'Prepared manifests and payloads are not model outcomes; no causal General result is reported.',
            'A future paid run requires explicit authorization and execution; packaging does not execute the runner.'],
    }
    (HERE/'review_followup_archive_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (HERE/'review-followup-SHA256SUMS.txt').write_text(f"{archive['sha256']}  {archive['asset']}\n",encoding='utf-8')
    print(json.dumps({'status':'PACKAGED','archive':archive,'artifact_directory_file_counts':artifact_counts},indent=2))


if __name__=='__main__':main()
