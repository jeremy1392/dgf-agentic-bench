"""Post-hoc evidence sensitivity and decision diagnostics; no inference or edits to scores.

The relaxed endpoint retains every original component, citation requirement and
lexical success. Only failed finding excerpts can additionally pass the same-object
JSON subset test used in the historical Gemini audit. This is not semantic scoring.
"""
import argparse
import collections
import csv
import json
from pathlib import Path
import audit_evidence as audit

ROOT=audit.ROOT
RANK={name:i for i,name in enumerate(['GO','GO_WITH_RESERVATIONS','REWORK','SUSPENSION','NO_GO'])}


def inspect(folder,row,dataset):
    oid=row['occurrence_id']; path=next(folder.glob('*_'+oid+'.json'))
    record=json.loads(path.read_text(encoding='utf-8'));pred=record['result']
    route=json.loads((dataset/folder.name/'01_route_manifest.json').read_text(encoding='utf-8'))
    occurrence=next(x for x in route['occurrences'] if x['occurrence_id']==oid)
    reader=audit.PublicEvidenceReader(dataset/folder.name,row['gate'],occurrence['phase'])
    observed={}
    for event in record['tool_trace']:
        result=event.get('result')
        if event['tool'] not in ['read_evidence','request_evidence'] or not isinstance(result,dict) or result.get('status') not in ['OK','RECEIVED']:continue
        eid=result.get('evidence_id')
        if eid=='UPSTREAM_DECISIONS' or (eid and reader.read_evidence(eid).get('content')==result.get('content')):
            observed[eid]=result['content']
    citations=bool(pred.get('evidence_refs')) and all(x in observed for x in pred['evidence_refs'])
    fields=audit.finding_fact_fields();items=[]
    for diagnostic in row['evidence_diagnostics']:
        fid=diagnostic.get('finding_id')
        if fid is None:continue
        required='UPSTREAM_DECISIONS' if fid.startswith('GEN-UPSTREAM-') else audit.facts_id(row['gate'])
        evaluations=[]
        for support in pred.get('evidence_support',[]):
            if support.get('finding_id')!=fid:continue
            eid=support.get('evidence_id');quote=support.get('quote');parsed=audit.parse_fragment(quote)
            eligible=eid==required and eid in observed and eid in pred.get('evidence_refs',[])
            source=observed.get(eid)
            match=audit.locate(parsed,source) if eligible and parsed else None
            relevant=bool(parsed and audit.field_names(parsed)&fields.get(fid,set()))
            same=match is not None and relevant
            flat=audit.flattened_locations(parsed,source) if eligible and parsed and not same else None
            classification=('structured_field_values_match' if same else 'flattened_cross_object_values_present' if flat else
                            'unobserved_or_wrong_reference' if not eligible else 'not_parseable_as_object_fragment' if parsed is None else 'no_matching_observed_object')
            evaluations.append({'evidence_id':eid,'quote':quote,'classification':classification,
                'matched_object_path':match,'flattened_field_paths':flat,'contains_rule_field':relevant,'observed_source':source})
        classification=('structured_field_values_match' if any(x['classification']=='structured_field_values_match' for x in evaluations)
                        else evaluations[0]['classification'] if evaluations else 'missing_support_item')
        items.append({'finding_id':fid,'classification':classification,'support_items':evaluations})
    recovered=bool(citations and items and all(x['classification']=='structured_field_values_match' for x in items))
    category=('citation_defect' if not citations else 'all_failed_items_structurally_supported' if recovered else
        'includes_flattened_cross_object_excerpt' if items and all(x['classification'] in ['structured_field_values_match','flattened_cross_object_values_present'] for x in items) else 'unresolved_structural_or_support_defect')
    return {'case':folder.name,'occurrence_id':oid,'gate':row['gate'],'original_score':row,
            'original_trace':path.relative_to(folder.parents[1]).as_posix(),'classification':category,
            'citations_valid':citations,'evidence_recovered':recovered,'items':items}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-dir',type=Path,default=ROOT/'experiments/run_20260922_214402_941347/results')
    ap.add_argument('--dataset',type=Path,default=audit.DATA);ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent)
    args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    audit.check_adversarial_controls();models={};details={};matrix_rows=[]
    for modeldir in sorted(args.run_dir.iterdir()):
        if not modeldir.is_dir():continue
        scores=[];gates=[];route_rows=[];failed_details=[];proc_rules=collections.defaultdict(collections.Counter)
        for folder in sorted(modeldir.glob('DGF-*')):
            p=folder/'score.json'
            if not p.exists():continue
            score=json.loads(p.read_text(encoding='utf-8'))
            if score.get('status') not in ['OK','AGENT_FAILURE'] or not score.get('occurrences'):continue
            scores.append(score);relaxed=[]
            for row in score['occurrences']:
                recovered=False
                if row['evidence_fidelity']<1:
                    detail=inspect(folder,row,args.dataset);failed_details.append(detail);recovered=detail['evidence_recovered']
                    if row['gate']=='procurement':
                        for item in detail['items']:proc_rules[item['finding_id']][item['classification']]+=1
                other_ok=all(row[k]==1 for k in ['decision','findings_f1','actions_f1','authorization'])
                relaxed.append(bool(row['strict_success'] or (other_ok and recovered)))
                gates.append(dict(row,case=folder.name,relaxed_success=relaxed[-1]))
            route_rows.append({'case':folder.name,'strict':score['route_complete_decision'],'relaxed':all(relaxed)})
        if not scores:continue
        model=scores[0]['model'];n=len(gates);cases=len(scores)
        confusion=collections.Counter((g['reference_disposition'],g['predicted_disposition']) for g in gates)
        for (ref,pred),count in sorted(confusion.items()):matrix_rows.append({'model':model,'reference':ref,'prediction':pred,'count':count})
        wrong=[g for g in gates if g['decision']!=1];proc=[g for g in gates if g['gate']=='procurement']
        evidence_only=lambda g:g['evidence_fidelity']<1 and all(g[k]==1 for k in ['decision','findings_f1','actions_f1','authorization'])
        eligible=[d for d in failed_details if evidence_only(d['original_score'])]
        counts={key:sum(g[key] for g in gates) for key in ['strict_success','relaxed_success']}
        models[model]={'cases':cases,'gates':n,'strict_gates':counts['strict_success'],'posthoc_relaxed_gates':counts['relaxed_success'],
            'strict_gate_rate':counts['strict_success']/n,'posthoc_relaxed_gate_rate':counts['relaxed_success']/n,
            'strict_routes':sum(x['strict'] for x in route_rows),'posthoc_relaxed_routes':sum(x['relaxed'] for x in route_rows),
            'strict_route_rate':sum(x['strict'] for x in route_rows)/cases,'posthoc_relaxed_route_rate':sum(x['relaxed'] for x in route_rows)/cases,
            'evidence_failed_gates':len(failed_details),'evidence_only_failed_gates':len(eligible),
            'all_evidence_gate_categories':dict(collections.Counter(d['classification'] for d in failed_details)),
            'evidence_only_gate_categories':dict(collections.Counter(d['classification'] for d in eligible)),
            'wrong_decisions':len(wrong),
            'more_restrictive_by_policy_rank':sum(RANK.get(g['predicted_disposition'],-1)>RANK[g['reference_disposition']] for g in wrong),
            'less_restrictive_by_policy_rank':sum(RANK.get(g['predicted_disposition'],-1)<RANK[g['reference_disposition']] for g in wrong),
            'false_approvals':sum(s['false_approval_count'] for s in scores),
            'frozen_base_matches':sum(g['predicted_disposition']==g['base_reference_disposition'] for g in gates),
            'effective_reference_matches':sum(g['decision']==1 for g in gates),
            'base_differences_with_local_approval':sum(g['predicted_disposition']!=g['base_reference_disposition'] and g['conditional_approval_used'] for g in gates),
            'base_differences_without_local_approval':sum(g['predicted_disposition']!=g['base_reference_disposition'] and not g['conditional_approval_used'] for g in gates),
            'procurement':{'gates':len(proc),'strict':sum(g['strict_success'] for g in proc),
                'relaxed':sum(g['relaxed_success'] for g in proc),'decision_correct':sum(g['decision']==1 for g in proc),
                'evidence_only_failures':sum(evidence_only(g) for g in proc),
                'component_failures':{k:sum(g[k]<1 for g in proc) for k in ['decision','findings_f1','actions_f1','evidence_fidelity','authorization']},
                'failed_evidence_items_by_rule':{k:dict(v) for k,v in sorted(proc_rules.items())}},
            'decision_confusion':[{ 'reference':r,'prediction':p,'count':c} for (r,p),c in sorted(confusion.items())],
            'route_details':route_rows}
        details[model]=failed_details
        assert counts['relaxed_success']>=counts['strict_success']
    expected={'deepseek/deepseek-v4.1-flash':338,'google/gemini-3.8-flash':85,'openai/gpt-5.6-luna':221}
    assert {m:v['evidence_only_failed_gates'] for m,v in models.items()}==expected
    assert models['google/gemini-3.8-flash']['evidence_only_gate_categories']=={'all_failed_items_structurally_supported':69,'citation_defect':7,'includes_flattened_cross_object_excerpt':9}
    result={'scope':'All original 899 evaluable model-case runs; original model trajectories only.',
        'method':'Post-hoc sensitivity: original strict success OR unchanged non-evidence components plus observed citations and exact field/value subset matches within one observed object for every originally failed finding. Original lexical successes remain accepted. No corrected quotes, invented reads, or cross-object promotion.',
        'limits':'This relaxed endpoint is lexical-or-structural provenance, not independent semantic entailment or full premise coverage. No new model calls. Case and gate scores are paired with the original outcomes; original primary scores remain unchanged.',
        'models':models}
    for name,obj in [('all_models_evidence_summary.json',result),('all_models_evidence_items.json',details)]:
        (args.output_dir/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (args.output_dir/'decision_confusion.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['model','reference','prediction','count']);w.writeheader();w.writerows(matrix_rows)
    for m,v in models.items():print(m,json.dumps({k:x for k,x in v.items() if k not in ['decision_confusion','route_details']}))


if __name__=='__main__':main()
