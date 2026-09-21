#!/usr/bin/env python3
from __future__ import annotations
import collections, json, random, sys
from pathlib import Path
from dgf_generator import project_context
from azure_architecture import generate_architecture_profile

EXPECTED = {
 'edge_pattern': {'frontdoor_waf_cdn','cdn_then_waf','waf_then_cdn','waf_only','frontdoor_only','private_only'},
 'compute_profile': {'vm_single','vm_ha','vmss','dedicated_host','aks','container_apps','app_service','functions','mixed'},
 'data_profile': {'transactional','enterprise_sql','postgres','event_driven','analytics','ai'},
 'network_profile': {'hub_spoke','single_vnet','virtual_wan'},
 'resilience_profile': {'single_region_single_az','single_region_multi_az','multi_region_active_passive','multi_region_active_active','backup_only'},
}

def main(n=1000):
    counts={k:collections.Counter() for k in EXPECTED}
    defect_count=0; inconsistency_count=0; multi_az=0; multi_region=0
    for i in range(n):
        rng=random.Random(100000+i)
        project=project_context(rng)
        p=generate_architecture_profile(200000+i,project,difficulty=(i%5)+1,inconsistency_rate=.20)
        for k in EXPECTED: counts[k][p[k]] += 1
        defect_count += len(p['defects']); inconsistency_count += len(p['inconsistencies'])
        multi_az += int(p['multi_az']); multi_region += int(p['multi_region'])
    missing={k:sorted(EXPECTED[k]-set(counts[k])) for k in EXPECTED}
    assert not any(missing.values()), f'Missing categories: {missing}'
    report={
      'profiles_tested':n,
      'distributions':{k:dict(v) for k,v in counts.items()},
      'avg_hidden_defects_per_case':round(defect_count/n,3),
      'avg_cross_document_inconsistencies_per_case':round(inconsistency_count/n,3),
      'multi_az_share':round(multi_az/n,3),
      'multi_region_share':round(multi_region/n,3),
      'status':'PASS'
    }
    Path('randomness_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
