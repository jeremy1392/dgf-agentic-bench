"""Prototype source-record additions for NEW development cases only.

Two narrowly scoped business records expose it.duplicate_capability and
compliance.audit_trail outside REVIEW_FACTS. These remain structured synthetic
records; this is neither a document-only benchmark nor a full coverage repair.
Run this file to create three fresh DEVELOPMENT_NOT_EVALUATION cases and a
read-only before/after integrity audit of the original source, dataset and runs.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FROZEN_SOURCE=ROOT/'experiments/reproduction_check_20260923/verified_inputs/benchmark_source'
ORIGINAL_DATA=ROOT/'experiments/preflight_balanced_300_20260922/dataset'
ORIGINAL_RESULTS=ROOT/'experiments/run_20260922_214402_941347/results'
REPETITIONS=ROOT/'experiments/followup_repetitions_20260923'
DEFAULT_OUTPUT=ROOT/'experiments/scaffold_development_20260924'
VERSION='DGF-source-record-extensions-v0.1-development'
PURPOSE='DEVELOPMENT_NOT_EVALUATION'
ROOT_MARKER='DEVELOPMENT_NOT_EVALUATION.json'
EXTENSION_MANIFEST='07_source_record_extensions.json'
PHASES=('opportunity','framing','design','build_acceptance','deployment_closure','governance')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def sha256(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def tree_inventory(root):
    """Hash complete file content and relative names; includes existing caches."""
    root=root.resolve()
    files={p.relative_to(root).as_posix():sha256(p) for p in sorted(root.rglob('*')) if p.is_file()}
    digest=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'file_count':len(files),'sha256_of_sorted_path_to_file_sha256_json':digest,'files':files}


def assert_new_root_location(root,protected_roots):
    root=root.resolve()
    for protected in protected_roots:
        protected=protected.resolve()
        if root==protected or root.is_relative_to(protected) or protected.is_relative_to(root):
            raise ValueError('New development output overlaps a protected source/data/result tree')


def initialize_development_root(root,protected_roots=(FROZEN_SOURCE,ORIGINAL_DATA,ORIGINAL_RESULTS,REPETITIONS)):
    """Require an absent output directory; never mark an existing dataset as new."""
    root=Path(root).resolve()
    assert_new_root_location(root,protected_roots)
    root.mkdir(parents=True,exist_ok=False)
    dump(root/ROOT_MARKER,{'purpose':PURPOSE,'extension_version':VERSION,
        'held_out':False,'preregistered':False,'model_calls':0,
        'description':'Generation/debugging examples only; already inspected during development.'})
    return root


def build_extension_records(canonical_case):
    """Return two domain records, not a copy of any full gate fact snapshot."""
    project=canonical_case['project']; project_id=project['project_id']
    duplicate=canonical_case['it']['duplicate_capability']
    trail=canonical_case['compliance']['audit_trail']
    if type(duplicate) is not bool:raise ValueError('duplicate_capability must be a boolean')
    if trail not in {'complete','partial','missing'}:raise ValueError('Invalid audit-trail status')
    return [
        {'evidence_id':'PORTFOLIO_ASSESSMENT', 'gate':'it',
         'path':'gate_evidence/it/portfolio_assessment_v1.csv',
         'canonical_fact':'it.duplicate_capability','value_column':'duplicate_capability',
         'rows':[{'schema_version':'portfolio-assessment-v1','source_version':'1',
             'assessment_id':project_id+'-PORTFOLIO-1','project_id':project_id,
             'duplicate_capability':str(duplicate).lower(),
             'assessment_owner':'Enterprise Architecture',
             'assessment_scope':'Existing enterprise capability overlap'}]},
        {'evidence_id':'AUDIT_TRAIL_STATUS', 'gate':'compliance',
         'path':'gate_evidence/compliance/audit_trail_status_v1.csv',
         'canonical_fact':'compliance.audit_trail','value_column':'audit_trail_status',
         'rows':[{'schema_version':'audit-trail-status-v1','source_version':'1',
             'record_id':project_id+'-AUDIT-TRAIL-1','project_id':project_id,
             'audit_trail_status':trail,'record_owner':'Compliance',
             'record_scope':'Evidence traceability for project changes'}]},
    ]


def csv_text(rows):
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return stream.getvalue()


def emit_source_record_extensions(case_dir,canonical_case,*,new_dataset_root):
    """Enrich one just-generated case inside a marked, freshly created root.

    Call after frozen build_case. The supplied canonical case must exactly match
    that new case's truth. Existing extensions and output files are refused.
    Gate scope is IT/compliance respectively; phase visibility starts at
    opportunity because both rules apply from that phase onward.
    """
    root=Path(new_dataset_root).resolve();case_dir=Path(case_dir).resolve()
    if not case_dir.is_relative_to(root) or case_dir==root:
        raise ValueError('Case must be inside the new development dataset root')
    marker=root/ROOT_MARKER
    if not marker.is_file() or read(marker).get('purpose')!=PURPOSE:
        raise ValueError('Refusing to alter a case outside a new development dataset')
    assert_new_root_location(root,[FROZEN_SOURCE,ORIGINAL_DATA,ORIGINAL_RESULTS,REPETITIONS])
    manifest_path=case_dir/EXTENSION_MANIFEST
    if manifest_path.exists():raise FileExistsError('Case already has source-record extensions')
    truth_path=case_dir/'99_hidden_ground_truth.json';truth=read(truth_path)
    if truth['canonical_truth']!=canonical_case:
        raise ValueError('Canonical case does not match the newly generated case')
    graph_path=case_dir/'02_evidence_graph.json';graph=read(graph_path)
    contracts_path=case_dir/'04_gate_contracts.json';contracts=read(contracts_path)
    visibility_path=case_dir/'05_phase_visibility.json';visibility=read(visibility_path)
    records=build_extension_records(canonical_case)
    old_ids={n['evidence_id'] for n in graph['nodes']}
    for record in records:
        target=(case_dir/record['path']).resolve()
        if not target.is_relative_to(case_dir):raise ValueError('Output path escapes new case')
        if target.exists() or record['evidence_id'] in old_ids:
            raise FileExistsError('Refusing to replace an existing evidence record')
    additions=[]
    for record in records:
        target=case_dir/record['path'];target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x',encoding='utf-8',newline='') as stream:stream.write(csv_text(record['rows']))
        node={'evidence_id':record['evidence_id'],'path':record['path'],'consumers':[record['gate']],
            'authoritative':True,'version':1,'age_days':0,'public_status':'AVAILABLE',
            'source_record_schema':record['rows'][0]['schema_version'],'generator_extension':VERSION}
        edge={'from':record['evidence_id'],'to_gate':record['gate'],'relation':'consumed_by'}
        graph['nodes'].append(node);graph['edges'].append(edge)
        truth['evidence_graph']['nodes'].append(dict(node,_hidden_mode='truthful'))
        truth['evidence_graph']['edges'].append(copy.deepcopy(edge))
        contracts[record['gate']]['admissible_inputs'].append(record['evidence_id'])
        for phase in PHASES:
            if phase not in visibility:raise ValueError('Missing phase visibility: '+phase)
            visibility[phase]=sorted(set(visibility[phase])|{record['evidence_id']})
        additions.append({k:record[k] for k in ('evidence_id','gate','path','canonical_fact','value_column')})
        additions[-1].update(sha256=sha256(target),visible_phases=list(PHASES),source_version=1)
    for path,value in [(graph_path,graph),(contracts_path,contracts),(visibility_path,visibility),(truth_path,truth)]:dump(path,value)
    manifest={'extension_version':VERSION,'purpose':PURPOSE,'records':additions,
        'scope':'Two known missing source facts only. Structured source records; no claim of total information sufficiency.',
        'citation_contract_changed':False,'model_calls':0}
    dump(manifest_path,manifest)
    return manifest


def variation_checks(canonical_case,evaluate_gate):
    results=[]
    for gate,key,values,fid,eid,column in [
        ('it','duplicate_capability',[False,True],'IT-RATIONAL-001','PORTFOLIO_ASSESSMENT','duplicate_capability'),
        ('compliance','audit_trail',['complete','missing','partial'],'COMP-AUDIT-001','AUDIT_TRAIL_STATUS','audit_trail_status')]:
        variants=[]
        for value in values:
            case=copy.deepcopy(canonical_case);case[gate][key]=value
            record=next(x for x in build_extension_records(case) if x['evidence_id']==eid)
            content=csv_text(record['rows']);decoded=list(csv.DictReader(io.StringIO(content)))
            expected=str(value).lower() if type(value) is bool else value
            assert decoded[0][column]==expected
            findings={f['id'] for f in evaluate_gate(case,gate,'design')['findings']}
            should_trigger=(value is True if gate=='it' else value=='missing')
            assert (fid in findings)==should_trigger,(gate,value,fid,findings)
            variants.append({'input':value,'source_cell':decoded[0][column],
                'target_finding_present':fid in findings,'csv_sha256':hashlib.sha256(content.encode()).hexdigest()})
        assert len({v['csv_sha256'] for v in variants})==len(values)
        results.append({'canonical_fact':gate+'.'+key,'finding_id':fid,'evidence_id':eid,'variants':variants,'status':'PASS'})
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=FROZEN_SOURCE)
    parser.add_argument('--output-dir',type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument('--report',type=Path,default=Path(__file__).with_name('source_record_extensions_report.json'))
    args=parser.parse_args()
    # Importing frozen source must not create or update bytecode in that tree.
    sys.dont_write_bytecode=True
    protected=[args.source,ORIGINAL_DATA,ORIGINAL_RESULTS,REPETITIONS]
    assert_new_root_location(args.output_dir,protected)
    if args.output_dir.exists():raise FileExistsError('Use a new development output directory; no overwrite permitted')
    before={str(p.resolve()):tree_inventory(p) for p in protected}
    sys.path.insert(0,str(args.source.resolve()))
    from generate_dgfbench_v6 import build_case
    from evaluator import evaluate_gate
    from openrouter_eval.public_evidence import PublicEvidenceReader
    from validate_case import validate_case
    seeds={'buy':924100,'integrate':924200,'build':924300}
    old_seeds={read(p)['seed'] for p in ORIGINAL_DATA.glob('DGF-*/00_project_context.json')}
    assert not set(seeds.values())&old_seeds
    output=initialize_development_root(args.output_dir,protected)
    cases=[];tests=[]
    for route,seed in seeds.items():
        case_dir=build_case(output/'cases',seed,4,route)
        canonical=read(case_dir/'99_hidden_ground_truth.json')['canonical_truth']
        before_new=tree_inventory(case_dir)
        extension=emit_source_record_extensions(case_dir,canonical,new_dataset_root=output)
        errors=validate_case(case_dir)
        assert not errors,(case_dir,errors)
        checks=[]
        for item in extension['records']:
            for phase in PHASES:
                response=PublicEvidenceReader(case_dir,item['gate'],phase).read_evidence(item['evidence_id'])
                assert response['status']=='OK'
                assert response['content'][0][item['value_column']]==str(canonical[item['gate']][item['canonical_fact'].split('.')[1]]).lower()
                other='compliance' if item['gate']=='it' else 'it'
                assert PublicEvidenceReader(case_dir,other,phase).read_evidence(item['evidence_id'])['status']=='NOT_IN_GATE_SCOPE'
                checks.append({'evidence_id':item['evidence_id'],'gate':item['gate'],'phase':phase,'status':'PASS','wrong_gate_rejected':True})
        if not tests:tests=variation_checks(canonical,evaluate_gate)
        after_new=tree_inventory(case_dir)
        changed=[name for name,digest in before_new['files'].items() if after_new['files'].get(name)!=digest]
        assert set(changed)=={'02_evidence_graph.json','04_gate_contracts.json','05_phase_visibility.json','99_hidden_ground_truth.json'}
        original_refs=read(case_dir/'99_hidden_ground_truth.json')['reference_decisions']
        dump(case_dir/ROOT_MARKER,{'purpose':PURPOSE,'held_out':False,'preregistered':False,'seed':seed,'extension_version':VERSION})
        case_readme=case_dir/'README_CASE.md'
        case_readme.write_text('# DEVELOPMENT_NOT_EVALUATION\n\nThese are inspected generation/debugging examples, not held-out evaluation cases.\n\n'+case_readme.read_text(encoding='utf-8'),encoding='utf-8')
        cases.append({'case':case_dir.relative_to(output).as_posix(),'route':route,'seed':seed,
            'case_id':canonical['case_id'],'validation_errors':errors,'public_access_checks':checks,
            'extension_manifest':extension,'extension_changed_existing_new_case_files':changed,
            'reference_decisions_sha256':hashlib.sha256(json.dumps(original_refs,sort_keys=True).encode()).hexdigest(),
            'file_inventory':tree_inventory(case_dir)})
    (output/'README.md').write_text('# DEVELOPMENT_NOT_EVALUATION\n\nThree inspected development cases for the source-record extension prototype. These seeds and cases are not held out, preregistered, or evaluated by a model. Original experiment data remain untouched.\n\nThe added portfolio assessment and audit-trail status CSVs expose exactly two source fields omitted from the old document emitter. They remain structured records and do not establish complete information coverage or validate the rules. The old REVIEW_FACTS-only scoring contract is unchanged.\n',encoding='utf-8')
    integrity=[]
    for protected_root in protected:
        key=str(protected_root.resolve());after=tree_inventory(protected_root)
        assert before[key]==after,'Protected tree changed: '+key
        integrity.append({'path':key,'file_count':after['file_count'],'before_sha256':before[key]['sha256_of_sorted_path_to_file_sha256_json'],
            'after_sha256':after['sha256_of_sorted_path_to_file_sha256_json'],'unchanged':True})
    report={'status':'PASS','purpose':PURPOSE,'extension_version':VERSION,'output_dir':str(output),
        'held_out':False,'preregistered':False,'model_calls':0,'source_version':(args.source/'VERSION').read_text(encoding='utf-8').strip(),
        'extension_script_sha256':sha256(Path(__file__)),'seeds_absent_from_original_300':True,
        'protected_tree_integrity':integrity,'counterfactual_tests':tests,'development_cases':cases,
        'limitations':['Only two known missing fields added; global coverage is a separate audit.',
            'Structured CSV business records do not test natural-language or visual extraction.',
            'Synthetic record authority and values are stipulated by the generator, not independently verified.',
            'The frozen scoring contract still requires REVIEW_FACTS citations; a separate contract revision is required.',
            'The frozen request_evidence tool can return a full factual_snapshot under REVIEW_FACTS_GATE even when another source is requested. A future ablation harness must block these alternate snapshot access paths; the two CSV additions do not do so.',
            'Development cases are publicly inspected and must not become held-out evaluation cases.']}
    dump(args.report,report)
    print(json.dumps({'status':report['status'],'cases':len(cases),'counterfactual_variants':sum(len(t['variants']) for t in tests),
        'protected_trees_unchanged':len(integrity),'report':str(args.report),'output_dir':str(output)},indent=2))


if __name__=='__main__':main()
