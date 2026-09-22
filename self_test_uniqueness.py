#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from azure_architecture import architecture_signature, render_architecture
from facts_engine import generate_canonical_case


def main() -> None:
    used=set(); names=set(); ids=set(); people=set(); vendors=set(); cidrs=set()
    attempts=[]; cases=[]; counter=0
    for route in ["buy","integrate","build"]:
        for _ in range(50):
            seed=12000+counter; counter+=1; attempt=0
            while True:
                case=generate_canonical_case(seed,route,4,architecture_attempt=attempt)
                sig=architecture_signature(case["architecture_profile"])
                if sig not in used:
                    break
                attempt+=1
                if attempt>10000: raise AssertionError("unique architecture search exhausted")
            used.add(sig); attempts.append(attempt); cases.append(case)
            p=case["project"]
            assert p["project_id"] not in ids; ids.add(p["project_id"])
            assert p["project_name"] not in names; names.add(p["project_name"])
            for x in [p["sponsor"],p["project_manager"],p["business_owner"],p["service_owner"],p["risk_owner"],case["general"]["benefits_owner"]]:
                assert x not in people; people.add(x)
            for o in case["procurement"]["offers"]:
                assert o["vendor"] not in vendors; vendors.add(o["vendor"])
            for c in case["architecture"]["private_cidrs"]:
                assert c not in cidrs; cidrs.add(c)

    assert len(used)==150
    assert len(names)==150 and len(ids)==150
    assert len(people)==900 and len(vendors)==600 and len(cidrs)==450

    # Render one example of every network grammar and ensure its topology label
    # appears in the SVG. This catches regressions back to one fixed layout.
    expected={
        "hub_spoke":"Hub VNet / Shared Services",
        "single_vnet":"Single Application VNet",
        "virtual_wan":"Azure Virtual WAN Hub",
    }
    with tempfile.TemporaryDirectory() as td:
        t=Path(td)
        found={}
        for case in cases:
            net=case["architecture_profile"]["network_profile"]
            if net in found: continue
            svg=t/f"{net}.svg"; png=t/f"{net}.png"
            render_architecture(case["architecture_profile"],case["project"],svg,png)
            txt=svg.read_text(encoding="utf-8")
            assert expected[net] in txt
            found[net]=True
            if len(found)==3: break
        assert set(found)==set(expected)

    print(json.dumps({
        "status":"PASS",
        "cases":150,
        "unique_project_names":len(names),
        "unique_architecture_signatures":len(used),
        "unique_people":len(people),
        "unique_vendors":len(vendors),
        "unique_private_cidrs":len(cidrs),
        "network_layouts_verified":sorted(expected),
        "max_architecture_retry":max(attempts),
    },indent=2))


if __name__=="__main__":
    main()
