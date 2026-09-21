from __future__ import annotations
from routes import PHASE_ORDER

BASE=["PROJECT_CHARTER","BUSINESS_CASE","BUDGET_APPROVAL","PORTFOLIO_SNAPSHOT","CMDB_EXPORT","TECH_CATALOG","DATA_INVENTORY","REG_MAPPING"]
ADDITIONS={
    "opportunity":[],
    "framing":["HLD","THREAT_MODEL","RFP","DPIA","AI_IMPACT","LIFECYCLE_REGISTER","CAPACITY_REPORT"],
    "design":["LLD","FLOW_MATRIX","OPENAPI","DATA_MODEL","DATA_LINEAGE","IP_PLAN","ADR_REGISTER","ARCH_DEBT","VENDOR_OFFERS","SCORING_MATRIX","DUE_DILIGENCE","PRICING_TCO","VENDOR_EVIDENCE_REQUEST","MSA","DPA","SLA_ANNEX","CONTRACT_PLAYBOOK","NEGOTIATION_LOG","AZURE_RESOURCE_GRAPH","IAM_EXPORT","CONDITIONAL_ACCESS","NSG_RULES","WAF_POLICY","FIREWALL_POLICY","KEYVAULT_CONFIG","SENTINEL_STATUS","DEFENDER_FINDINGS","VULN_SCAN"],
    "build_acceptance":["PENTEST","BACKUP_JOBS","RESTORE_TEST","FAILOVER_TEST","LOAD_TEST","CI_PIPELINE","RUNBOOK","ROLLBACK_TEST","SLO_SLI","MONITOR_ALERTS","SUPPORT_RACI","LICENSE_POSITION"],
    "deployment_closure":["ITSM_CHANGE","INSURANCE","SIGNING_AUTHORITY","RETENTION","ACCESSIBILITY","CONTROL_MATRIX","EXPORT_CONTROL","BENEFITS_PLAN","COMMITTEE_BRIEFING","ACTION_REGISTER"],
    "governance":[],
}

def phase_visibility(graph):
    known=set(); out={}
    for phase in PHASE_ORDER:
        if phase=="opportunity": known.update(BASE)
        known.update(ADDITIONS.get(phase,[]))
        if phase=="governance": known.update(n["evidence_id"] for n in graph["nodes"])
        # Keep only IDs present in this case graph.
        ids={n["evidence_id"] for n in graph["nodes"]}
        out[phase]=sorted(known & ids)
    return out
