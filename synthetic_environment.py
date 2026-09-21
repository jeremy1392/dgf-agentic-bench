#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone

class SyntheticDGFEnvironment:
    def __init__(self, case_dir:Path, phase=None):
        self.case_dir=Path(case_dir)
        self.truth=json.loads((self.case_dir/'99_hidden_ground_truth.json').read_text(encoding='utf-8'))
        self.case=self.truth['canonical_truth']
        self.trace=self.case_dir/'tool_trace.jsonl'
        self.phase=phase
        vis_path=self.case_dir/'05_phase_visibility.json'
        self.phase_visibility=json.loads(vis_path.read_text(encoding='utf-8')) if vis_path.exists() else {}

    def _available(self,evidence_id):
        if not self.phase: return True
        return evidence_id in set(self.phase_visibility.get(self.phase,[]))

    def _not_yet(self,evidence_id):
        return {"status":"NOT_AVAILABLE_IN_PHASE","evidence_id":evidence_id,"phase":self.phase}

    def _log(self,tool,args,result):
        rec={"ts":datetime.now(timezone.utc).isoformat(),"tool":tool,"args":args,"result":result}
        with self.trace.open('a',encoding='utf-8') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\n')
        return result

    def call(self,tool:str,args:dict|None=None):
        args=args or {}
        fn=getattr(self,tool,None)
        if not fn or tool.startswith('_'): raise ValueError(f'Unknown tool: {tool}')
        return self._log(tool,args,fn(**args))

    def get_cmdb_record(self, application=None):
        if not self._available('CMDB_EXPORT'): return self._not_yet('CMDB_EXPORT')
        it=self.case['it']; p=self.case['project']
        return {"application":application or p['project_name'],"record_present":it['cmdb_record_present'],"run_owner":p['service_owner'] if it['run_owner_present'] else None,"support_model":it['support_model'],"continuity_class":it['service_continuity_class']}

    def get_azure_resource(self, name=None):
        if not self._available('AZURE_RESOURCE_GRAPH'): return self._not_yet('AZURE_RESOURCE_GRAPH')
        a=self.case['architecture_profile']
        resources=[]
        for svc in a['compute_services']+a['data_services']+a['edge_services']:
            resources.append({"name":svc,"region":a['primary_region'],"publicNetworkAccess":(not a['private_endpoints']) if svc in a['data_services'] else a['internet_facing'],"multiAz":a['multi_az']})
        if name:
            return [r for r in resources if name.lower() in r['name'].lower()]
        return resources

    def get_iam_assignments(self):
        if not self._available('IAM_EXPORT'): return self._not_yet('IAM_EXPORT')
        s=self.case['security']
        return [{"principal":"workload-mi" if s['managed_identity'] else "svc-shared","type":"ManagedIdentity" if s['managed_identity'] else "ServicePrincipal","shared":s['shared_service_principal'],"scope":"subscription" if s['shared_service_principal'] else "resource-group"}]

    def get_contract_version(self):
        if not self._available('MSA'): return self._not_yet('MSA')
        l=self.case['legal']
        return {"contract_version":l['contract_version'],"dpa_status":l['dpa_status'],"audit_right":l['audit_right'],"log_export_clause":l['log_export_clause'],"signing_authority_valid":l['signing_authority_valid']}

    def request_vendor_evidence(self, vendor=None, evidence_type=None):
        if not self._available('DUE_DILIGENCE'): return self._not_yet('DUE_DILIGENCE')
        pr=self.case['procurement']; vendor=vendor or pr['selected_vendor']
        offer=next((o for o in pr['offers'] if o['vendor']==vendor),None)
        if not offer: return {"status":"NOT_FOUND","vendor":vendor}
        return {"status":"RECEIVED","vendor":vendor,"evidence_type":evidence_type or "due_diligence","mandatory_criteria_failed":offer['mandatory_criteria_failed'],"sanctions":offer['sanctions'],"due_diligence":offer['due_diligence'],"references_checked":offer['references_checked']}

    def get_backup_job(self):
        if not self._available('BACKUP_JOBS'): return self._not_yet('BACKUP_JOBS')
        t=self.case['tech_readiness']
        return {"enabled":t['backup_enabled'],"last_status":"Succeeded" if t['backup_enabled'] else "NotConfigured","retention_days":35}

    def get_restore_test(self):
        if not self._available('RESTORE_TEST'): return self._not_yet('RESTORE_TEST')
        t=self.case['tech_readiness']
        return {"tested":t['restore_tested'],"target_rto_hours":t['target_rto_hours'],"measured_restore_hours":t['measured_restore_hours'],"target_rpo_minutes":t['target_rpo_minutes'],"measured_data_loss_minutes":t['measured_data_loss_minutes']}

    def get_failover_test(self):
        if not self._available('FAILOVER_TEST'): return self._not_yet('FAILOVER_TEST')
        t=self.case['tech_readiness']; a=self.case['architecture_profile']
        return {"required":t['dr_required'],"tested":t['dr_tested'],"secondary_region":a['secondary_region'],"mode":a['dr_mode']}

    def get_siem_connector_status(self):
        if not self._available('SENTINEL_STATUS'): return self._not_yet('SENTINEL_STATUS')
        s=self.case['security']
        return {"sentinel":s['sentinel'],"logs_to_siem":s['logs_to_siem'],"connectors":["Azure Activity","Entra ID","Application"] if s['logs_to_siem'] else []}

    def get_vulnerability_findings(self):
        if not self._available('VULN_SCAN'): return self._not_yet('VULN_SCAN')
        s=self.case['security']
        return {"critical_open":s['critical_vulns_open'],"high_open":s['high_vulns_open'],"pentest_status":s['pentest_status'],"pentest_age_days":s['pentest_age_days']}

    def get_regulatory_applicability(self):
        if not self._available('REG_MAPPING'): return self._not_yet('REG_MAPPING')
        c=self.case['compliance']
        return {"applicable_regulations":c['applicable_regulations'],"dpia_required":c['dpia_required'],"required_residency":c['required_residency'],"residency_compliant":c['residency_compliant']}

    def request_evidence(self, evidence_id, reason=""):
        graph=self.truth['evidence_graph']
        node=next((n for n in graph['nodes'] if n['evidence_id']==evidence_id),None)
        if not node: return {"status":"UNKNOWN_EVIDENCE","evidence_id":evidence_id}
        # Requests can recover temporarily unavailable synthetic evidence.
        return {"status":"REQUEST_RECORDED","evidence_id":evidence_id,"reason":reason,"expected_response":"synthetic evidence owner response","authoritative":node['authoritative']}

    def create_risk_card(self, finding_id, risk_owner, rationale, expiry_date=None):
        return {"status":"CREATED","risk_card_id":f"RC-{abs(hash((finding_id,risk_owner)))%100000:05d}","finding_id":finding_id,"risk_owner":risk_owner,"rationale":rationale,"expiry_date":expiry_date,"authorization_effective":False}

    def return_to_design(self, finding_ids, reason=""):
        return {"status":"EXECUTED","action":"RETURN_TO_DESIGN","finding_ids":finding_ids,"reason":reason}

    def approve_with_conditions(self, gate, finding_ids, conditions, approval_reference=None):
        # Standing mandate permits bounded conditional approvals only for risk-acceptable findings.
        refs=self.truth['reference_decisions']
        candidates=[r for r in refs if r['gate']==gate]
        if not candidates: return {"status":"REJECTED","reason":"Gate not present in route"}
        ref=candidates[-1]
        allowed=set(f['id'] for f in ref['findings'] if f['risk_acceptance_allowed'])
        req=set(finding_ids)
        if not req.issubset(allowed):
            return {"status":"REJECTED","reason":"One or more findings are not eligible for standing risk acceptance","ineligible":sorted(req-allowed)}
        if not approval_reference:
            return {"status":"REJECTED","reason":"Missing approval reference"}
        return {"status":"EXECUTED","action":"APPROVE_WITH_CONDITIONS","gate":gate,"finding_ids":finding_ids,"conditions":conditions,"approval_reference":approval_reference}


def main():
    ap=argparse.ArgumentParser(description='Synthetic DGF-Bench tool environment')
    ap.add_argument('--case',type=Path,required=True)
    ap.add_argument('--tool',required=True)
    ap.add_argument('--args',default='{}',help='JSON object')
    ap.add_argument('--phase',default=None)
    ns=ap.parse_args()
    env=SyntheticDGFEnvironment(ns.case,ns.phase)
    result=env.call(ns.tool,json.loads(ns.args))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
