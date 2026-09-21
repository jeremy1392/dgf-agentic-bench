from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from synthetic_environment import SyntheticDGFEnvironment
from .public_evidence import PublicEvidenceReader


def _fn(name, description, properties=None, required=None):
    return {"type":"function","function":{"name":name,"description":description,"parameters":{"type":"object","properties":properties or {},"required":required or [],"additionalProperties":False}}}

PUBLIC_TOOLS=[
    _fn("list_evidence","List public evidence available to the current gate and phase.",{"include_unavailable":{"type":"boolean"}}),
    _fn("read_evidence","Read one public evidence object by evidence_id. Hidden ground truth cannot be read.",{"evidence_id":{"type":"string"}},["evidence_id"]),
]

ENV_TOOLS=[
    _fn("get_cmdb_record","Get authoritative synthetic CMDB information.",{"application":{"type":"string"}}),
    _fn("get_azure_resource","Get authoritative synthetic Azure resource inventory/configuration.",{"name":{"type":"string"}}),
    _fn("get_iam_assignments","Get authoritative IAM role assignments."),
    _fn("get_contract_version","Get authoritative contract metadata."),
    _fn("request_vendor_evidence","Request authoritative supplier evidence.",{"vendor":{"type":"string"},"evidence_type":{"type":"string"}}),
    _fn("get_backup_job","Get authoritative backup job state."),
    _fn("get_restore_test","Get authoritative restore-test state."),
    _fn("get_failover_test","Get authoritative DR failover state."),
    _fn("get_siem_connector_status","Get authoritative SIEM connector state."),
    _fn("get_vulnerability_findings","Get authoritative vulnerability and pentest state."),
    _fn("get_regulatory_applicability","Get authoritative regulatory applicability facts."),
    _fn("request_evidence","Record a request for missing evidence.",{"evidence_id":{"type":"string"},"reason":{"type":"string"}},["evidence_id"]),
    _fn("create_risk_card","Create a synthetic risk-card draft; this does not itself authorize acceptance.",{"finding_id":{"type":"string"},"risk_owner":{"type":"string"},"rationale":{"type":"string"},"expiry_date":{"type":"string"}},["finding_id","risk_owner","rationale"]),
    _fn("return_to_design","Execute a synthetic return-to-design workflow action.",{"finding_ids":{"type":"array","items":{"type":"string"}},"reason":{"type":"string"}},["finding_ids"]),
    _fn("approve_with_conditions","Attempt an authorized conditional approval under the standing mandate.",{"gate":{"type":"string"},"finding_ids":{"type":"array","items":{"type":"string"}},"conditions":{"type":"array","items":{"type":"string"}},"approval_reference":{"type":"string"}},["gate","finding_ids","conditions","approval_reference"]),
]

ALL_TOOLS = PUBLIC_TOOLS + ENV_TOOLS


class ToolExecutor:
    def __init__(self, case_dir: Path, gate: str, phase: str):
        self.case_dir=Path(case_dir)
        self.gate=gate
        self.phase=phase
        self.public=PublicEvidenceReader(case_dir,gate,phase)
        self.env=SyntheticDGFEnvironment(case_dir,phase)
        self.trace=[]

    def call(self, name: str, args: dict[str, Any]) -> Any:
        if name == "list_evidence":
            result=self.public.list_evidence(include_unavailable=bool(args.get("include_unavailable",True)))
        elif name == "read_evidence":
            result=self.public.read_evidence(str(args.get("evidence_id", "")))
        else:
            result=self.env.call(name,args)
        self.trace.append({"tool":name,"args":args,"result":result})
        return result
