"""Post-hoc structural audit of every Gemini strict failure; not human adjudication."""
import collections
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEST=Path(__file__).resolve().parent
SOURCE=ROOT/'experiments/reproduction_check_20260923/verified_inputs/benchmark_source'
DATA=ROOT/'experiments/preflight_balanced_300_20260922/dataset'
RUN=ROOT/'experiments/run_20260922_214402_941347/results/google__gemini-3.8-flash__0bb591b009df'
sys.path.insert(0,str(SOURCE))
from openrouter_eval.public_evidence import PublicEvidenceReader
from benchmark_protocol import finding_fact_fields, facts_id
from evidence_provenance import supports_observed_fields


def no_duplicates(pairs):
    result={}
    for k,v in pairs:
        if k in result: raise ValueError('duplicate key')
        result[k]=v
    return result


def parse_fragment(quote):
    if not isinstance(quote,str):return None
    for candidate in [quote, '{'+quote+'}']:
        try:
            value=json.loads(candidate,object_pairs_hook=no_duplicates)
            if isinstance(value,dict) and value:return value
        except (ValueError,TypeError):pass
    return None


def subset(quote,source):
    if isinstance(quote,dict):
        return isinstance(source,dict) and all(k in source and subset(v,source[k]) for k,v in quote.items())
    if isinstance(quote,list):
        return isinstance(source,list) and len(quote)==len(source) and all(subset(a,b) for a,b in zip(quote,source))
    if isinstance(quote,bool) or isinstance(source,bool):return type(quote)==type(source) and quote==source
    if isinstance(quote,(int,float)) and isinstance(source,(int,float)):return quote==source
    return type(quote)==type(source) and quote==source


def locate(quote,source,path='$'):
    if subset(quote,source):return path
    children=source.items() if isinstance(source,dict) else enumerate(source) if isinstance(source,list) else []
    for key,value in children:
        found=locate(quote,value,path+'/'+str(key))
        if found is not None:return found
    return None


def field_names(obj):
    result=set()
    if isinstance(obj,dict):
        result.update(obj)
        for v in obj.values():result.update(field_names(v))
    if isinstance(obj,list):
        for v in obj:result.update(field_names(v))
    return result


def flattened_locations(quote,source):
    """Diagnostic only: preserve paths, never promote a cross-object join to support."""
    if not isinstance(quote,dict) or any(isinstance(v,(dict,list)) for v in quote.values()):return None
    paths={k:locate({k:v},source) for k,v in quote.items()}
    return paths if all(v is not None for v in paths.values()) else None


def check_adversarial_controls():
    assert locate({'a':True,'b':10},{'b':10,'a':True})=='$'
    assert locate({'n':10},{'n':100}) is None
    assert locate({'n':True},{'n':1}) is None
    assert locate({'a':1,'b':2},[{'a':1},{'b':2}]) is None
    assert locate({'missing':1},{'a':1}) is None
    assert parse_fragment('"a":1,"a":2') is None
    assert locate({'n':30},{'n':30.0})=='$'


def main():
    check_adversarial_controls()
    field_map=finding_fact_fields();gates=[];item_counts=collections.Counter();gate_counts=collections.Counter()
    for folder in sorted(RUN.glob('DGF-*')):
        scorefile=folder/'score.json'
        if not scorefile.exists():continue
        score=json.loads(scorefile.read_text(encoding='utf-8'))
        for row in score.get('occurrences',[]):
            if row['strict_success']:continue
            assert all(row[k]==1 for k in ['decision','findings_f1','actions_f1','authorization'])
            oid=row['occurrence_id'];path=next(folder.glob('*_'+oid+'.json'))
            record=json.loads(path.read_text(encoding='utf-8'));pred=record['result']
            route=json.loads((DATA/folder.name/'01_route_manifest.json').read_text(encoding='utf-8'))
            occurrence=next(x for x in route['occurrences'] if x['occurrence_id']==oid)
            reader=PublicEvidenceReader(DATA/folder.name,row['gate'],occurrence['phase'])
            observed={}
            for event in record['tool_trace']:
                r=event.get('result')
                if event['tool'] not in ['read_evidence','request_evidence'] or not isinstance(r,dict) or r.get('status') not in ['OK','RECEIVED']:continue
                eid=r.get('evidence_id')
                if eid=='UPSTREAM_DECISIONS':observed[eid]=r['content']
                elif eid and reader.read_evidence(eid).get('content')==r.get('content'):
                    observed[eid]=r['content']
            citation_ok=bool(pred.get('evidence_refs')) and all(e in observed for e in pred['evidence_refs'])
            findings=[x['finding_id'] for x in row['evidence_diagnostics'] if 'finding_id' in x]
            items=[]
            for fid in findings:
                required='UPSTREAM_DECISIONS' if fid.startswith('GEN-UPSTREAM-') else facts_id(row['gate'])
                supports=[s for s in pred.get('evidence_support',[]) if s.get('finding_id')==fid]
                evaluations=[]
                for support in supports:
                    eid=support.get('evidence_id');quote=support.get('quote')
                    source=observed.get(eid);parsed=parse_fragment(quote)
                    eligible=eid==required and eid in pred.get('evidence_refs',[]) and eid in observed
                    match=locate(parsed,source) if eligible and parsed else None
                    relevant=bool(parsed and field_names(parsed)&field_map.get(fid,set()))
                    equivalent=bool(match is not None and relevant)
                    flattened=flattened_locations(parsed,source) if eligible and parsed and not equivalent else None
                    status=('structured_field_values_match' if equivalent else
                            'flattened_cross_object_values_present' if flattened else
                            'unobserved_or_wrong_reference' if not eligible else
                            'not_parseable_as_object_fragment' if parsed is None else
                            'no_matching_observed_object')
                    evaluations.append({'evidence_id':eid,'quote':quote,'status':status,'matched_object_path':match,
                                        'contains_rule_field':relevant,'observed_source':source,
                                        'flattened_field_paths':flattened,
                                        'original_lexical_support':supports_observed_fields(source,quote,field_map.get(fid,set())) if eligible else False})
                status='structured_field_values_match' if any(x['status']=='structured_field_values_match' for x in evaluations) else (evaluations[0]['status'] if evaluations else 'missing_support_item')
                item_counts[status]+=1;items.append({'finding_id':fid,'classification':status,'support_items':evaluations})
            gate_status=('citation_defect' if not citation_ok else
                         'all_failed_items_structurally_supported' if items and all(i['classification']=='structured_field_values_match' for i in items) else
                         'includes_flattened_cross_object_excerpt' if items and all(i['classification'] in ['structured_field_values_match','flattened_cross_object_values_present'] for i in items) else
                         'unresolved_structural_or_support_defect')
            gate_counts[gate_status]+=1
            gates.append({'case':folder.name,'occurrence_id':oid,'gate':row['gate'],
                          'original_trace':path.relative_to(ROOT).as_posix(),
                          'original_score':row,'evidence_refs':pred.get('evidence_refs',[]),
                          'observed_ids':list(observed),'citations_valid':citation_ok,
                          'classification':gate_status,'failed_finding_items':items})
    assert len(gates)==85
    result={'scope':'All 85 Gemini strict-failure gates; failed finding excerpts are nested items, not 85 independent excerpts.',
            'method':'Post-hoc exact JSON field/value subset matching within a single observed object, ignoring key order and numeric serialization (30 equals 30.0). Separately record flattened cross-object values and their paths without promoting them to same-object support. No value correction or invented reads.',
            'citation_note':'The seven citation defects concern UPSTREAM_DECISIONS without the required read_evidence event. Prior reviews are also supplied in the gate prompt; these are missing required tool observations, not proof that the model never received the upstream information.',
            'limit':'Structural equivalence is not semantic entailment, complete premise coverage, or independent human adjudication. Original strict scores unchanged. No new global semantic score inferred.',
            'gate_counts':dict(gate_counts),'failed_finding_item_counts':dict(item_counts),'gates':gates}
    (DEST/'gemini_evidence_audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='gates'},indent=2))


if __name__=='__main__':main()
