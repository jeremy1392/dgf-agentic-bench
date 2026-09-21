#!/usr/bin/env python3
"""
DGF Synthetic Information Generator
-----------------------------------
Generates coherent synthetic project dossiers for the 8 governance gates
visible in the provided "Guide Complet des Gates de Gouvernance" screenshot.

No external dependencies: Python 3.10+ standard library only.

Main goals:
- produce random but internally coherent enterprise project information;
- generate one dossier per gate and per subject;
- preserve GREEN / YELLOW / RED gate decisions;
- expose hidden ground truth for DGF-Bench-style evaluation;
- inject missing, conflicting and risky evidence in a controlled way;
- support deterministic reproduction with --seed.

IMPORTANT SOURCE NOTE
---------------------
The screenshot visibly provides detailed criteria for:
  1) Gate Général,
  2) Gate IT,
  3) Gate Architecture.
It exposes the macro categories / names for:
  4) Gate Sécurité Architecture,
  5) Gate Tech Readiness,
  6) Gate Procurement,
  7) Gate Légale,
  8) Gate Compliance.

For gates 4-8 the generator uses conservative, domain-standard subtopics
consistent with those macro gate names. They are tagged "inferred_extension"
in gate_catalog.json so they can be replaced with the exact source wording
when the complete 34-page document is available.
"""

from __future__ import annotations
import argparse
import json
import random
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

STATUSES = ["PASS", "WARN", "FAIL", "MISSING", "NA"]
DECISIONS = {"PASS": "GREEN", "WARN": "YELLOW", "FAIL": "RED"}

FIRST_NAMES = ["Nadia","Jeremy","Sofia","Omar","Leila","Thomas","Marc","Elena","David","Amira","Lucas","Maya"]
LAST_NAMES = ["Martin","Canale","Ivanov","Moreau","Benali","Rossi","Smith","Petrescu","Dubois","Khan","Garcia","Nguyen"]

BUSINESS_UNITS = ["Finance","Retail","Corporate Banking","HR","Operations","Sales","Risk","Procurement","Customer Service","Technology"]
REGIONS = ["EU","UAE","UK","US","APAC","Multi-region"]
CLOUDS = ["Azure","AWS","GCP","Private Cloud","Hybrid","On-premises"]
CLASSIFICATIONS = ["Public","Internal","Confidential","Restricted"]
CRITICALITIES = ["Low","Medium","High","Critical"]
PROJECT_TYPES = ["new_platform","ma_integration","new_project"]
PROJECT_NAMES = [
    "Customer 360 CRM","Digital Treasury Hub","Claims Modernization","Secure Vendor Portal",
    "AI Service Desk","M&A Integration Wave","Data Governance Platform","Payments API Hub",
    "HR Experience Platform","Enterprise Observability Program","Cloud Landing Zone Upgrade",
    "Regulatory Reporting Modernization"
]

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def weighted_choice(rng, pairs):
    vals, weights = zip(*pairs)
    return rng.choices(vals, weights=weights, k=1)[0]

def person(rng):
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"

def evidence_ref(rng, prefix):
    return f"{prefix}-{rng.randint(1000,9999)}-v{rng.randint(1,5)}"

def subject(topic, value, status, evidence=None, notes=None, critical=False, origin="source_detail"):
    return {
        "topic": topic,
        "value": value,
        "status": status,
        "critical": critical,
        "evidence": evidence or [],
        "notes": notes or "",
        "topic_origin": origin,
    }

def issue_status(rng, difficulty=3, critical=False, allow_na=False):
    """Difficulty 1..5; higher => more missing/warn/fail."""
    if allow_na and rng.random() < 0.08:
        return "NA"
    d = clamp(difficulty, 1, 5)
    fail = 0.02 + 0.035*(d-1) + (0.05 if critical else 0)
    missing = 0.03 + 0.025*(d-1)
    warn = 0.10 + 0.04*(d-1)
    x = rng.random()
    if x < fail:
        return "FAIL"
    if x < fail + missing:
        return "MISSING"
    if x < fail + missing + warn:
        return "WARN"
    return "PASS"

def gate_decision(subjects):
    critical_fail = any(s["critical"] and s["status"] in ("FAIL","MISSING") for s in subjects)
    nfail = sum(s["status"] == "FAIL" for s in subjects)
    nmissing = sum(s["status"] == "MISSING" for s in subjects)
    nwarn = sum(s["status"] == "WARN" for s in subjects)
    if critical_fail or nfail >= 2:
        return "RED"
    if nfail or nmissing or nwarn:
        return "YELLOW"
    return "GREEN"

def project_context(rng, project_type=None):
    ptype = project_type or rng.choice(PROJECT_TYPES)
    start = date.today() + timedelta(days=rng.randint(-30,120))
    users = rng.choice([50,120,250,500,1000,2000,5000,12000])
    budget = rng.choice([150_000,300_000,500_000,750_000,1_200_000,2_500_000,5_000_000,10_000_000])
    classification = weighted_choice(rng, [("Public",1),("Internal",3),("Confidential",5),("Restricted",2)])
    criticality = weighted_choice(rng, [("Low",1),("Medium",4),("High",4),("Critical",2)])
    cloud = rng.choice(CLOUDS)
    region = rng.choice(REGIONS)
    if ptype == "ma_integration":
        name = "M&A Integration Wave"
        users = rng.choice([150,400,900,2500,7000])
        cloud = rng.choice(["Hybrid","On-premises","Azure","AWS"])
        criticality = weighted_choice(rng, [("Medium",2),("High",5),("Critical",3)])
    elif ptype == "new_platform":
        name = rng.choice(["Customer 360 CRM","HR Experience Platform","Secure Vendor Portal","Regulatory Reporting Modernization"])
    else:
        name = rng.choice([p for p in PROJECT_NAMES if p != "M&A Integration Wave"])
    return {
        "project_id": f"PRJ-{rng.randint(10000,99999)}",
        "project_name": name,
        "project_type": ptype,
        "business_unit": rng.choice(BUSINESS_UNITS),
        "sponsor": person(rng),
        "project_manager": person(rng),
        "target_start": start.isoformat(),
        "target_go_live": (start + timedelta(days=rng.randint(90,540))).isoformat(),
        "users_impacted": users,
        "budget_eur": budget,
        "data_classification": classification,
        "business_criticality": criticality,
        "hosting_model": cloud,
        "primary_region": region,
        "vendor_name": rng.choice(["Contoso","Fabrikam","Northwind","Litware","Adventure Works","In-house"]),
        "architecture_pattern": rng.choice(["SaaS","3-tier web","Microservices","Event-driven","Data platform","Agentic AI","Batch integration"]),
    }

def gen_general(rng, ctx, difficulty):
    origin="source_detail"
    roi = round(rng.uniform(-0.05,0.55),3)
    payback = rng.randint(8,60)
    budget_gap = rng.choice([0,0,0,0.05,0.10,0.20])
    strategy = rng.choice(["Directly aligned","Aligned","Partially aligned","Weak alignment"])
    capacity_gap = rng.randint(0,5)
    risk_count = rng.randint(1,10)
    benefits_kpi = rng.choice(["cost-to-serve","processing time","NPS","incident rate","conversion rate","availability"])
    subjects = [
        subject("Alignement stratégique", {"assessment":strategy,"portfolio_priority":rng.choice(["P0","P1","P2","P3"])}, issue_status(rng,difficulty), [evidence_ref(rng,"STRAT")], origin=origin),
        subject("Business case", {"roi":roi,"payback_months":payback,"npv_eur":int(ctx["budget_eur"]*rng.uniform(-0.1,1.2))}, "WARN" if roi < 0.08 else issue_status(rng,difficulty), [evidence_ref(rng,"BC")], critical=True, origin=origin),
        subject("Budget", {"requested_eur":ctx["budget_eur"],"funding_gap_pct":budget_gap,"contingency_pct":rng.choice([5,10,15,20])}, "FAIL" if budget_gap>=0.2 else ("WARN" if budget_gap else issue_status(rng,difficulty)), [evidence_ref(rng,"BUD")], critical=True, origin=origin),
        subject("Planning", {"critical_path_weeks":rng.randint(8,72),"schedule_slip_weeks":rng.choice([0,0,1,2,4,8]),"dependencies":rng.randint(1,8)}, issue_status(rng,difficulty), [evidence_ref(rng,"PLAN")], origin=origin),
        subject("Capacité à faire", {"skill_gaps":capacity_gap,"fte_needed":round(rng.uniform(2,35),1),"fte_available":round(rng.uniform(1,30),1)}, "WARN" if capacity_gap>=3 else issue_status(rng,difficulty), [evidence_ref(rng,"CAP")], origin=origin),
        subject("Risques", {"open_major_risks":risk_count,"highest_risk_score":rng.choice([4,6,8,9,12,16]),"residual_risk_owner":person(rng)}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"RISK")], critical=True, origin=origin),
        subject("Conduite du changement", {"impacted_users":ctx["users_impacted"],"training_plan":rng.choice(["Complete","Partial","Draft","Missing"]),"adoption_target_pct":rng.randint(60,98)}, issue_status(rng,difficulty), [evidence_ref(rng,"OCM")], origin=origin),
        subject("Réalisation des bénéfices", {"kpi":benefits_kpi,"baseline":round(rng.uniform(10,100),1),"target_improvement_pct":rng.randint(5,45),"measurement_owner":person(rng)}, issue_status(rng,difficulty), [evidence_ref(rng,"BEN")], origin=origin),
    ]
    return subjects

def gen_it(rng, ctx, difficulty):
    origin="source_detail"
    lifecycle = rng.choice(["Strategic","Tolerate","Invest","Migrate","Eliminate"])
    capacity_util = rng.randint(35,98)
    subjects = [
        subject("Conformité au catalogue", {"technology":rng.choice(["Java 21",".NET 8","Python 3.12","SAP","Salesforce","Node.js","Kubernetes"]),"catalog_status":rng.choice(["Standard","Approved exception","Non-standard"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"CAT")], critical=True, origin=origin),
        subject("Rationalisation applicative", {"duplicate_capability":rng.choice([True,False,False]),"existing_alternative":rng.choice(["None","Legacy app","Shared service","SaaS already licensed"])}, issue_status(rng,difficulty), [evidence_ref(rng,"APP")], origin=origin),
        subject("Licences", {"license_model":rng.choice(["Subscription","Per-user","Consumption","Enterprise agreement","Open-source"]),"license_compliant":rng.choice([True,True,True,False]),"annual_cost_eur":rng.randint(20_000,800_000)}, issue_status(rng,difficulty), [evidence_ref(rng,"LIC")], origin=origin),
        subject("Exploitabilité (Run)", {"run_owner":person(rng),"support_tier":rng.choice(["L1-L2-L3","L2-L3","Vendor-only","DevOps product team"]),"runbook_status":rng.choice(["Approved","Draft","Missing"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"RUN")], critical=True, origin=origin),
        subject("Support & Maintenabilité", {"vendor_support":rng.choice(["24x7","Business hours","Community","Internal"]),"patch_sla_days":rng.choice([7,14,30,90]),"skills_available":rng.choice([True,True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"SUP")], origin=origin),
        subject("Capacité & Hébergement", {"hosting":ctx["hosting_model"],"capacity_utilization_pct":capacity_util,"headroom_pct":100-capacity_util}, "WARN" if capacity_util>85 else issue_status(rng,difficulty), [evidence_ref(rng,"CAPIT")], origin=origin),
        subject("Cycle de vie & Obsolescence", {"lifecycle":lifecycle,"eol_months":rng.choice([6,12,18,36,60,120]),"technical_debt":rng.choice(["Low","Medium","High"])}, issue_status(rng,difficulty), [evidence_ref(rng,"EOL")], origin=origin),
        subject("Continuité de service", {"rto_hours":rng.choice([1,2,4,8,24,48]),"rpo_minutes":rng.choice([0,15,60,240,1440]),"dr_tested":rng.choice([True,True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"BCP")], critical=True, origin=origin),
        subject("Intégration ITSM", {"cmdb_record":rng.choice([True,True,False]),"incident_queue":rng.choice(["ServiceNow","Jira Service Management","Other"]),"change_process":rng.choice(["Standard","Normal","Emergency","Undefined"])}, issue_status(rng,difficulty), [evidence_ref(rng,"ITSM")], origin=origin),
        subject("Poste de travail & Mobilité", {"client_type":rng.choice(["Browser","Managed desktop","Mobile","VDI","None"]),"mdm_required":rng.choice([True,False]),"offline_mode":rng.choice([True,False])}, issue_status(rng,difficulty,allow_na=True), [evidence_ref(rng,"EUC")], origin=origin),
    ]
    return subjects

def gen_architecture(rng, ctx, difficulty):
    origin="source_detail"
    latency = rng.choice([10,20,50,100,200,500])
    availability = rng.choice([99.0,99.5,99.9,99.95,99.99])
    subjects = [
        subject("Urbanisation & API", {"integration_style":rng.choice(["REST","Event-driven","Batch","GraphQL","File transfer"]),"api_gateway":rng.choice([True,False]),"domain_alignment":rng.choice(["Strong","Partial","Weak"])}, issue_status(rng,difficulty), [evidence_ref(rng,"API")], origin=origin),
        subject("Architecture applicative", {"pattern":ctx["architecture_pattern"],"coupling":rng.choice(["Low","Medium","High"]),"reference_pattern_compliant":rng.choice([True,True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"APPARCH")], critical=True, origin=origin),
        subject("Architecture de données", {"model":rng.choice(["Relational","Lakehouse","Document","Event stream","Mixed"]),"master_data_owner":person(rng),"data_lineage":rng.choice(["Complete","Partial","Missing"])}, issue_status(rng,difficulty), [evidence_ref(rng,"DATA")], origin=origin),
        subject("Bande passante & Latence", {"bandwidth_mbps":rng.choice([50,100,500,1000,10000]),"target_latency_ms":latency,"cross_region":ctx["primary_region"]=="Multi-region"}, issue_status(rng,difficulty), [evidence_ref(rng,"NET")], origin=origin),
        subject("Adressage IP & Routage", {"private_cidrs":rng.randint(1,8),"ip_overlap":rng.choice([False,False,False,True]),"dns_zone":f"{ctx['project_id'].lower()}.corp.example"}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"IP")], critical=True, origin=origin),
        subject("Connectivité Cloud & Inter-sites", {"connectivity":rng.choice(["Private Link","VPN","ExpressRoute","Internet","SD-WAN"]),"sites":rng.randint(1,12),"segmented":rng.choice([True,True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"CONN")], origin=origin),
        subject("Disponibilité & Répartition", {"sla_pct":availability,"zones":rng.choice([1,2,3]),"load_balanced":rng.choice([True,True,False]),"failover_tested":rng.choice([True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"HA")], critical=True, origin=origin),
        subject("Performance & Scalabilité", {"peak_rps":rng.randint(50,10000),"autoscaling":rng.choice([True,False]),"load_test_pct_of_peak":rng.choice([50,75,100,125,150])}, issue_status(rng,difficulty), [evidence_ref(rng,"PERF")], origin=origin),
        subject("Réversibilité & Portabilité", {"exit_plan":rng.choice(["Tested","Documented","Draft","Missing"]),"proprietary_services":rng.randint(0,12),"data_export_supported":rng.choice([True,True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"EXIT")], origin=origin),
        subject("Éco-conception", {"estimated_kwh_month":rng.randint(500,100000),"right_sizing":rng.choice([True,False]),"idle_shutdown":rng.choice([True,False]),"region_carbon_reviewed":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"ECO")], origin=origin),
    ]
    return subjects

def gen_security(rng, ctx, difficulty):
    origin="source_macro"
    subjects = [
        subject("Conformité aux politiques de sécurité", {"policy_exceptions":rng.randint(0,5),"security_baseline":rng.choice(["Compliant","Partial","Non-compliant"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"SEC-POL")], critical=True, origin=origin),
        subject("Analyse de risques", {"threat_scenarios":rng.randint(3,18),"highest_score":rng.choice([4,6,8,9,12,16]),"risk_owner":person(rng)}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"SEC-RISK")], critical=True, origin=origin),
        subject("Surface d'exposition & segmentation", {"internet_exposed":rng.choice([True,False]),"segments":rng.randint(1,8),"dmz_or_private_zone":rng.choice([True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"SEG")], critical=True, origin=origin),
        subject("IAM & privilèges", {"sso":rng.choice([True,True,False]),"mfa":rng.choice(["Mandatory","Optional","Missing"]),"privileged_roles":rng.randint(1,15),"service_identity":rng.choice(["Managed identity","Service principal","Shared account","Human account"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"IAM")], critical=True, origin=origin),
        subject("Chiffrement", {"in_transit":rng.choice([True,True,False]),"at_rest":rng.choice([True,True,False]),"customer_managed_keys":rng.choice([True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"CRYPT")], critical=True, origin=origin),
        subject("Logs, monitoring & détection", {"logs_to_siem":rng.choice([True,True,False]),"retention_days":rng.choice([30,90,180,365,730]),"alerting":rng.choice(["Operational","Partial","Missing"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"LOG")], critical=True, origin=origin),
        subject("Vulnérabilités & tests", {"last_pentest_days":rng.choice([30,90,180,365,None]),"critical_vulns_open":rng.randint(0,4),"sast_dast":rng.choice(["Both","SAST only","DAST only","None"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"VULN")], critical=True, origin=origin),
        subject("Sauvegarde, reprise & résilience", {"backup":rng.choice([True,True,False]),"restore_tested":rng.choice([True,False]),"ransomware_isolation":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"RES")], origin=origin),
        subject("Sécurité fournisseur", {"security_clauses":rng.choice(["Complete","Partial","Missing"]),"certifications":rng.sample(["ISO27001","SOC2","PCI-DSS","CSA STAR","None"],k=1),"subprocessors_known":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"TPRM")], origin=origin),
        subject("Réversibilité sécurité", {"credential_revocation_plan":rng.choice([True,False]),"key_exit_plan":rng.choice([True,False]),"log_export_on_exit":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"SECEXIT")], origin=origin),
    ]
    return subjects

def gen_readiness(rng, ctx, difficulty):
    origin="source_macro"
    subjects = [
        subject("Environnements & tests", {"envs":["DEV","TEST","PROD"] if rng.random()>0.2 else ["DEV","PROD"],"test_completion_pct":rng.randint(60,100)}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"TEST")], critical=True, origin=origin),
        subject("Pilote / POC", {"pilot_completed":rng.choice([True,True,False]),"pilot_users":rng.randint(10,500),"success_criteria_met_pct":rng.randint(50,100)}, issue_status(rng,difficulty), [evidence_ref(rng,"POC")], origin=origin),
        subject("Performance & charge", {"load_tested":rng.choice([True,False]),"peak_test_pct":rng.choice([50,75,100,125,150]),"p95_ms":rng.randint(20,2000)}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"LOAD")], critical=True, origin=origin),
        subject("Qualité de code / build", {"unit_test_coverage_pct":rng.randint(30,95),"critical_static_findings":rng.randint(0,5),"build_reproducible":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"CODE")], origin=origin),
        subject("Observabilité", {"metrics":rng.choice([True,False]),"logs":rng.choice([True,False]),"traces":rng.choice([True,False]),"dashboard":rng.choice(["Ready","Partial","Missing"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"OBS")], critical=True, origin=origin),
        subject("Sauvegarde & restauration", {"backup_enabled":rng.choice([True,True,False]),"restore_tested":rng.choice([True,False]),"last_restore_days":rng.choice([7,30,90,180,None])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"RESTORE")], critical=True, origin=origin),
        subject("Runbooks & exploitation", {"runbooks":rng.choice(["Approved","Draft","Missing"]),"on_call":rng.choice([True,False]),"handover_signed":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"OPS")], origin=origin),
        subject("Support & incidents", {"support_model":rng.choice(["24x7","Business hours","Vendor","Product team"]),"sev1_response_min":rng.choice([15,30,60,120]),"known_errors":rng.randint(0,12)}, issue_status(rng,difficulty), [evidence_ref(rng,"INC")], origin=origin),
        subject("Déploiement & rollback", {"deployment_automated":rng.choice([True,False]),"rollback_tested":rng.choice([True,False]),"change_type":rng.choice(["Standard","Normal","Emergency"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"DEPLOY")], critical=True, origin=origin),
        subject("Aptitude à la production", {"open_blockers":rng.randint(0,4),"open_major_actions":rng.randint(0,10),"go_live_owner":person(rng)}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"PRODREADY")], critical=True, origin=origin),
    ]
    return subjects

def gen_procurement(rng, ctx, difficulty):
    origin="inferred_extension"
    subjects = [
        subject("Stratégie d'achat", {"route":rng.choice(["RFI/RFP","Direct award","Framework","Existing contract","Build vs Buy"]),"competition":rng.choice(["Open","Restricted","Single source"])}, issue_status(rng,difficulty), [evidence_ref(rng,"BUY")], origin=origin),
        subject("RFI / RFP", {"requirements_count":rng.randint(20,250),"responses_received":rng.randint(1,8),"mandatory_criteria_failed":rng.randint(0,4)}, issue_status(rng,difficulty), [evidence_ref(rng,"RFP")], origin=origin),
        subject("Sélection fournisseur", {"vendor":ctx["vendor_name"],"score":rng.randint(45,98),"references_checked":rng.choice([True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"VENDOR")], critical=True, origin=origin),
        subject("Conditions commerciales", {"discount_pct":rng.randint(0,35),"commitment_months":rng.choice([12,24,36,60]),"renewal":rng.choice(["Auto","Manual","None"])}, issue_status(rng,difficulty), [evidence_ref(rng,"COMM")], origin=origin),
        subject("Prix / TCO", {"year1_eur":rng.randint(25_000,1_500_000),"three_year_tco_eur":rng.randint(100_000,4_500_000),"price_indexation_pct":rng.choice([0,2,3,5,8])}, issue_status(rng,difficulty), [evidence_ref(rng,"TCO")], origin=origin),
        subject("SLA / pénalités", {"availability_sla":rng.choice([99,99.5,99.9,99.95]),"support_sla_hours":rng.choice([1,2,4,8,24]),"service_credits":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"SLA")], origin=origin),
        subject("Due diligence fournisseur", {"financial_health":rng.choice(["Good","Watch","Weak"]),"security_review":rng.choice(["Complete","Partial","Pending"]),"sanctions_check":rng.choice(["Clear","Hit","Pending"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"DD")], critical=True, origin=origin),
        subject("Sous-traitants", {"count":rng.randint(0,20),"approved_list":rng.choice([True,False]),"change_notification_days":rng.choice([0,15,30,60])}, issue_status(rng,difficulty), [evidence_ref(rng,"SUB")], origin=origin),
        subject("Réversibilité fournisseur", {"data_export":rng.choice([True,False]),"exit_assistance_days":rng.choice([0,30,60,90,180]),"deletion_certificate":rng.choice([True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"EXITBUY")], critical=True, origin=origin),
        subject("Commande / contractualisation", {"po_ready":rng.choice([True,False]),"contract_status":rng.choice(["Draft","Negotiation","Approved","Signed"]),"signature_authority":person(rng)}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"PO")], critical=True, origin=origin),
    ]
    return subjects

def gen_legal(rng, ctx, difficulty):
    origin="inferred_extension"
    subjects = [
        subject("Contrat principal", {"status":rng.choice(["Draft","Negotiation","Approved","Signed"]),"governing_law":rng.choice(["France","England & Wales","UAE","New York","Ireland"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"CONTRACT")], critical=True, origin=origin),
        subject("DPA / protection des données", {"dpa":rng.choice(["Signed","Draft","Missing","N/A"]),"controller_processor_roles":rng.choice(["Clear","Ambiguous"])}, issue_status(rng,difficulty,critical=True,allow_na=True), [evidence_ref(rng,"DPA")], critical=True, origin=origin),
        subject("Propriété intellectuelle", {"ownership":rng.choice(["Customer","Vendor","Shared","Ambiguous"]),"third_party_ip":rng.choice([True,False]),"open_source_obligations":rng.choice(["Reviewed","Pending","None"])}, issue_status(rng,difficulty), [evidence_ref(rng,"IPR")], origin=origin),
        subject("Responsabilité & plafonds", {"liability_cap_multiplier":rng.choice([0.5,1,2,5,"unlimited"]), "security_carveout":rng.choice([True,False]),"indemnity":rng.choice(["Broad","Limited","None"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"LIAB")], critical=True, origin=origin),
        subject("Confidentialité", {"nda":rng.choice(["Signed","Missing","Embedded in MSA"]),"survival_years":rng.choice([2,3,5,10])}, issue_status(rng,difficulty), [evidence_ref(rng,"NDA")], origin=origin),
        subject("Droits d'audit", {"audit_right":rng.choice(["Full","Limited","Reports only","None"]),"notice_days":rng.choice([5,10,30,60])}, issue_status(rng,difficulty), [evidence_ref(rng,"AUDIT")], origin=origin),
        subject("Résiliation", {"termination_for_convenience":rng.choice([True,False]),"notice_days":rng.choice([30,60,90,180]),"termination_assistance":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"TERM")], origin=origin),
        subject("Localisation / transfert", {"data_regions":[ctx["primary_region"]],"cross_border_transfer":rng.choice([True,False]),"transfer_mechanism":rng.choice(["SCC","Adequacy","Contractual","N/A"])}, issue_status(rng,difficulty), [evidence_ref(rng,"XFER")], origin=origin),
        subject("Assurance / garanties", {"cyber_insurance_m":rng.choice([0,1,2,5,10,20]),"professional_indemnity_m":rng.choice([1,2,5,10]),"certificate_valid":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"INS")], origin=origin),
        subject("Engagements réglementaires", {"mandatory_clauses":rng.choice(["Complete","Partial","Missing"]),"regulatory_change_clause":rng.choice([True,False])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"REGCLAUSE")], critical=True, origin=origin),
    ]
    return subjects

def gen_compliance(rng, ctx, difficulty):
    origin="inferred_extension"
    subjects = [
        subject("RGPD / Privacy", {"personal_data":rng.choice([True,True,False]),"dpia_required":rng.choice([True,False]),"dpia_status":rng.choice(["Complete","Draft","Missing","N/A"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"GDPR")], critical=True, origin=origin),
        subject("NIS2 / DORA / réglementation sectorielle", {"applicable":rng.choice(["NIS2","DORA","PCI DSS","SOX","None","Multiple"]),"control_mapping":rng.choice(["Complete","Partial","Missing"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"REG")], critical=True, origin=origin),
        subject("Résidence des données", {"required_region":rng.choice(["EU","UAE","UK","US","No restriction"]),"actual_region":ctx["primary_region"],"compliant":rng.choice([True,True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"RESID")], origin=origin),
        subject("Éthique / principes internes", {"ethics_review":rng.choice(["Passed","Conditional","Not required","Missing"]),"high_impact_use":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"ETH")], origin=origin),
        subject("Politiques internes", {"policies_checked":rng.randint(5,40),"exceptions":rng.randint(0,5),"exception_approvals_valid":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"GRC")], origin=origin),
        subject("Conservation & archivage", {"retention_years":rng.choice([1,3,5,7,10]),"legal_hold_supported":rng.choice([True,False]),"deletion_enforced":rng.choice([True,False])}, issue_status(rng,difficulty), [evidence_ref(rng,"RET")], origin=origin),
        subject("Traçabilité / audit", {"audit_trail":rng.choice(["Complete","Partial","Missing"]),"evidence_immutable":rng.choice([True,False]),"audit_frequency":rng.choice(["Continuous","Quarterly","Annual","Ad hoc"])}, issue_status(rng,difficulty,critical=True), [evidence_ref(rng,"TRACE")], critical=True, origin=origin),
        subject("Tiers & chaîne de sous-traitance", {"tier_count":rng.randint(0,4),"third_party_monitoring":rng.choice(["Continuous","Annual","Onboarding only","None"])}, issue_status(rng,difficulty), [evidence_ref(rng,"TP")], origin=origin),
        subject("Reporting réglementaire", {"reporting_required":rng.choice([True,False]),"owner":person(rng),"deadline_days":rng.choice([1,3,7,30,90])}, issue_status(rng,difficulty), [evidence_ref(rng,"REPORT")], origin=origin),
        subject("Sanctions / conformité export", {"screening":rng.choice(["Clear","Pending","Hit","N/A"]),"export_control_review":rng.choice(["Clear","Pending","Restricted","N/A"])}, issue_status(rng,difficulty,critical=True,allow_na=True), [evidence_ref(rng,"SAN")], critical=True, origin=origin),
    ]
    return subjects

GENERATORS = {
    "general": ("Gate Général", gen_general),
    "it": ("Gate IT", gen_it),
    "architecture": ("Gate Architecture", gen_architecture),
    "security": ("Gate Sécurité Architecture", gen_security),
    "tech_readiness": ("Gate Tech Readiness", gen_readiness),
    "procurement": ("Gate Procurement", gen_procurement),
    "legal": ("Gate Légale", gen_legal),
    "compliance": ("Gate Compliance", gen_compliance),
}

OWNERS = {
    "general": ["Sponsor","COMEX/CODIR","PMO","Finance","Risk"],
    "it": ["DSI","Operations IT","Cloud/Platform","DBA","FinOps","ITSM"],
    "architecture": ["Chief Architect","Solution Architect","Data Architect","Integration Architect","Network Architect"],
    "security": ["CISO/RSSI","Security Architect","Cyber Risk","IAM","SOC/CERT","Network Security"],
    "tech_readiness": ["CTO","QA/Test","SRE/DevOps","Release Manager","Production","Operations"],
    "procurement": ["Procurement Director","Category Manager","Vendor Manager","Buyer"],
    "legal": ["Legal Director","Contract Counsel","DPO/Privacy Counsel","IP Counsel"],
    "compliance": ["Chief Compliance Officer","DPO","GRC","Internal Audit","Regulatory Affairs"],
}

def build_gate(key, ctx, rng, difficulty):
    name, fn = GENERATORS[key]
    subjects = fn(rng, ctx, difficulty)
    return {
        "gate_key": key,
        "gate_name": name,
        "population_owner": rng.choice(OWNERS[key]),
        "reviewer": person(rng),
        "subjects": subjects,
        "decision": gate_decision(subjects),
        "summary": {
            "pass": sum(s["status"]=="PASS" for s in subjects),
            "warn": sum(s["status"]=="WARN" for s in subjects),
            "fail": sum(s["status"]=="FAIL" for s in subjects),
            "missing": sum(s["status"]=="MISSING" for s in subjects),
            "na": sum(s["status"]=="NA" for s in subjects),
        }
    }

def inject_conflict(rng, gates, conflict_rate):
    """Mark random evidence as conflicting without changing the hidden source value."""
    conflicts=[]
    for gate in gates.values():
        for s in gate["subjects"]:
            if rng.random() < conflict_rate and s["status"] not in ("NA",):
                conflicts.append({
                    "gate": gate["gate_key"],
                    "topic": s["topic"],
                    "claim_a": "Document A indicates compliant / complete",
                    "claim_b": "Authoritative system indicates non-compliant / incomplete",
                    "authoritative_source": rng.choice(["CMDB","Cloud API","IAM API","Contract repository","SIEM","Policy registry"]),
                })
    return conflicts

def generate_case(seed, difficulty=3, project_type=None, gates=None, conflict_rate=0.05):
    rng = random.Random(seed)
    ctx = project_context(rng, project_type)
    keys = gates or list(GENERATORS.keys())
    gate_data = {k: build_gate(k, ctx, rng, difficulty) for k in keys}
    conflicts = inject_conflict(rng, gate_data, conflict_rate)
    decisions = {k:v["decision"] for k,v in gate_data.items()}
    overall = "RED" if "RED" in decisions.values() else ("YELLOW" if "YELLOW" in decisions.values() else "GREEN")
    return {
        "schema_version": "1.0",
        "seed": seed,
        "difficulty": difficulty,
        "case_id": str(uuid.UUID(int=rng.getrandbits(128))),
        "project": ctx,
        "gates": gate_data,
        "cross_gate_conflicts": conflicts,
        "overall_decision": overall,
        "hidden_ground_truth": {
            "note": "For benchmark evaluation. Do not expose to the evaluated agent.",
            "expected_gate_decisions": decisions,
            "expected_overall_decision": overall,
            "conflicts": conflicts,
        }
    }

def main():
    p=argparse.ArgumentParser(description="Generate synthetic DGF gate dossiers.")
    p.add_argument("--count",type=int,default=1)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--difficulty",type=int,choices=range(1,6),default=3)
    p.add_argument("--project-type",choices=PROJECT_TYPES,default=None)
    p.add_argument("--gate",choices=list(GENERATORS.keys())+["all"],default="all")
    p.add_argument("--conflict-rate",type=float,default=0.05)
    p.add_argument("--format",choices=["json","jsonl"],default="json")
    p.add_argument("--output",type=str,default="-")
    args=p.parse_args()

    gates=None if args.gate=="all" else [args.gate]
    cases=[generate_case(args.seed+i,args.difficulty,args.project_type,gates,args.conflict_rate) for i in range(args.count)]
    if args.format=="jsonl":
        out="\n".join(json.dumps(x,ensure_ascii=False) for x in cases)
    else:
        out=json.dumps(cases[0] if args.count==1 else cases,ensure_ascii=False,indent=2)
    if args.output=="-":
        print(out)
    else:
        Path(args.output).write_text(out,encoding="utf-8")

if __name__=="__main__":
    main()
