#!/usr/bin/env python3
import json, tempfile
from pathlib import Path
from dgf_generator import project_context
from azure_architecture import generate_architecture_profile
from semantic_profiles import apply_overrides
from generate_fake_documents import build_case_pack

COMPUTES=["vm_single","vm_ha","vmss","dedicated_host","aks","container_apps","app_service","functions","mixed"]
def main():
    seen=set()
    for i,c in enumerate(COMPUTES):
        import random
        rng=random.Random(9000+i)
        project=project_context(rng,"new_project")
        p=generate_architecture_profile(10000+i,project,3,.1)
        p=apply_overrides(p,{"compute_profile":c},12000+i,3)
        assert p["semantic_compute"]
        assert p["semantic_edge"]
        assert p["semantic_data"]
        assert p["semantic_network"]
        seen.add(p["compute_profile"])
    assert seen==set(COMPUTES)
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        cdir,docs=build_case_pack(4242,4,"new_project",root,.08,.15,
                                  {"compute_profile":"aks","edge_pattern":"frontdoor_waf_cdn","resilience_profile":"multi_region_active_passive"})
        assert (cdir/"04_security_evidence/05_Compute_Platform_Security_Design.docx").exists()
        assert (cdir/"05_tech_readiness_evidence/08_Platform_Operations_and_Readiness.docx").exists()
        gt=json.loads((cdir/"99_hidden_ground_truth.json").read_text())
        assert gt["architecture_profile"]["compute_profile"]=="aks"
        assert gt["architecture_profile"]["semantic_compute"]["kubernetes_version"]
    print("v4 semantic self-test: PASS")
if __name__=="__main__": main()
