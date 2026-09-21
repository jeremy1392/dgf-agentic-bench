#!/usr/bin/env python3
from __future__ import annotations

import json, random
from pathlib import Path
from typing import Any, Dict, List
import cairosvg
from azure_icon_registry import AzureIconRegistry

AZURE_REGIONS = [
    "UAE North","UAE Central","West Europe","North Europe","UK South",
    "France Central","Germany West Central","East US","East US 2",
    "West US 2","Southeast Asia","Australia East"
]

EDGE_PATTERNS = {
    "frontdoor_waf_cdn": ["Azure Front Door Premium", "WAF + CDN"],
    "cdn_then_waf": ["Azure CDN", "Application Gateway WAF"],
    "waf_then_cdn": ["Application Gateway WAF", "Azure CDN"],
    "waf_only": ["Application Gateway WAF"],
    "frontdoor_only": ["Azure Front Door"],
    "private_only": ["Private Access Only"],
}

COMPUTE_PROFILES = {
    "vm_single": ["Azure VM"],
    "vm_ha": ["Azure VM AZ1","Azure VM AZ2"],
    "vmss": ["VM Scale Set AZ1","VM Scale Set AZ2","VM Scale Set AZ3"],
    "dedicated_host": ["Azure Dedicated Host","VM Group A","VM Group B"],
    "aks": ["AKS System Pool","AKS App Pool","Ingress Controller","Worker Pods"],
    "container_apps": ["Azure Container Apps Environment","Frontend Container","API Container","Worker Container"],
    "app_service": ["Azure App Service","Deployment Slot"],
    "functions": ["Azure Functions","Function App Workers"],
    "mixed": ["Azure App Service","AKS App Pool","Azure Functions","Batch VM"],
}

DATA_PROFILES = {
    "transactional": ["Azure SQL Database","Azure Storage Account","Azure Cache for Redis"],
    "enterprise_sql": ["Azure SQL Managed Instance","Azure Storage Account","Azure Key Vault"],
    "postgres": ["Azure Database for PostgreSQL","Azure Storage Account","Azure Cache for Redis"],
    "event_driven": ["Azure Cosmos DB","Azure Service Bus","Azure Event Hubs","Azure Storage Account"],
    "analytics": ["Azure Data Lake Storage","Azure Synapse / Fabric Endpoint","Azure SQL Database"],
    "ai": ["Azure AI Search","Azure Storage Account","Azure Cosmos DB","Azure Key Vault"],
}

RESILIENCE_PROFILES = [
    "single_region_single_az",
    "single_region_multi_az",
    "multi_region_active_passive",
    "multi_region_active_active",
    "backup_only",
]

def weighted(rng, items):
    vals, weights = zip(*items)
    return rng.choices(vals, weights=weights, k=1)[0]

def b(rng, p=.5):
    return rng.random() < p

def generate_architecture_profile(seed:int, project:Dict[str,Any], difficulty:int=3,
                                  inconsistency_rate:float=.12) -> Dict[str,Any]:
    rng=random.Random(seed)
    solution_type=weighted(rng, [
        ("web_platform",3),("api_platform",3),("enterprise_backoffice",2),
        ("data_platform",2),("agentic_ai",2),("integration_platform",2)
    ])
    edge=weighted(rng, [
        ("frontdoor_waf_cdn",5),("cdn_then_waf",2),("waf_then_cdn",1),
        ("waf_only",2),("frontdoor_only",2),("private_only",1)
    ])
    compute=weighted(rng, [
        ("vm_single",1),("vm_ha",2),("vmss",3),("dedicated_host",1),
        ("aks",4),("container_apps",4),("app_service",3),("functions",2),("mixed",3)
    ])
    data=weighted(rng, [
        ("transactional",4),("enterprise_sql",2),("postgres",2),
        ("event_driven",3),("analytics",2),("ai",2)
    ])
    net=weighted(rng, [("hub_spoke",6),("single_vnet",2),("virtual_wan",2)])
    resilience=weighted(rng, [
        ("single_region_single_az",1+difficulty),
        ("single_region_multi_az",5),
        ("multi_region_active_passive",4),
        ("multi_region_active_active",2),
        ("backup_only",1+difficulty//2),
    ])
    primary=project.get("primary_region")
    if primary not in AZURE_REGIONS:
        primary=rng.choice(AZURE_REGIONS)
    secondary=rng.choice([x for x in AZURE_REGIONS if x!=primary])
    multi_region=resilience.startswith("multi_region")
    multi_az=resilience in ("single_region_multi_az","multi_region_active_passive","multi_region_active_active")
    dr_mode={
        "single_region_single_az":"No dedicated DR",
        "single_region_multi_az":"Zone-resilient / same-region",
        "multi_region_active_passive":"Warm standby",
        "multi_region_active_active":"Active-active",
        "backup_only":"Backup restore only",
    }[resilience]
    internet_facing=edge!="private_only"
    private_endpoints=b(rng,.75 if difficulty<=3 else .55)
    firewall=b(rng,.78); bastion=b(rng,.65); ddos=b(rng,.55 if internet_facing else .25)
    expressroute=b(rng,.45); vpn=b(rng,.40); nat=b(rng,.35)
    apim=solution_type in ("api_platform","integration_platform","agentic_ai") or b(rng,.35)
    messaging=solution_type in ("api_platform","integration_platform","agentic_ai") or b(rng,.45)
    managed_identity=b(rng,.80); pim=b(rng,.60); ca=b(rng,.78)
    sentinel=b(rng,.80); defender=b(rng,.78); appinsights=b(rng,.75); logs_to_siem=sentinel and b(rng,.88)
    backup_enabled=b(rng,.90); restore_tested=b(rng,.70); dr_tested=multi_region and b(rng,.62)
    asr=compute in ("vm_single","vm_ha","vmss","dedicated_host","mixed") and multi_region and b(rng,.75)
    if multi_region:
        data_replication=rng.choice(["Geo-replication","GRS/RA-GRS","Cross-region replica","Active geo-replication"])
    elif multi_az:
        data_replication=rng.choice(["Zone redundant","ZRS","Synchronous zone replica"])
    else:
        data_replication=rng.choice(["LRS only","Single-zone replica","None"])
    rto=rng.choice([.25,.5,1,2,4,8,24]); rpo=rng.choice([0,5,15,30,60,240,1440])
    if resilience in ("single_region_single_az","backup_only"):
        rto=max(rto,rng.choice([4,8,24])); rpo=max(rpo,rng.choice([60,240,1440]))

    defects=[]
    candidates=[
        ("public_database","Data service exposes a public endpoint despite private-network design."),
        ("shared_service_principal","A shared service principal is used across environments."),
        ("no_waf","Internet-facing application has no effective WAF policy."),
        ("single_point_compute","Only one compute instance exists in production."),
        ("backup_not_restored","Backups exist but no successful restore test is available."),
        ("no_siem_export","Application logs are retained locally and not exported to SIEM."),
        ("dr_not_tested","Secondary-region failover has not been tested."),
        ("region_mismatch","HLD names a DR region that differs from the recovery plan."),
        ("overprivileged_identity","Workload identity has broader Graph / Azure permissions than required."),
        ("missing_private_endpoint","A data service expected to be private is reachable through a public endpoint."),
        ("stale_diagram","Architecture diagram version is older than the security review package."),
    ]
    p=min(.08+.05*difficulty,.45)
    seen=set()
    def add_defect(k,desc,severity=None):
        if k not in seen:
            defects.append({"id":k,"description":desc,"severity":severity or rng.choice(["medium","high","critical"])})
            seen.add(k)
    for k,desc in candidates:
        if rng.random()<p: add_defect(k,desc)
    if internet_facing and edge in ("frontdoor_only",):
        add_defect("edge_control_gap","Internet entry path has incomplete WAF protection.","high")
    if compute=="vm_single": add_defect("single_point_compute","Single VM is a production compute single point of failure.","high")
    if backup_enabled and not restore_tested: add_defect("backup_not_restored","Backup policy exists but restore evidence is missing.","high")
    if multi_region and not dr_tested: add_defect("dr_not_tested","Cross-region DR architecture exists but failover test evidence is absent.","high")

    inconsistencies=[]
    for d in defects:
        if rng.random()<inconsistency_rate:
            inconsistencies.append({
                "type":"cross_document_conflict","fact":d["id"],
                "diagram_claim":"appears compliant / present",
                "authoritative_truth":"non-compliant / incomplete",
                "source_of_truth":rng.choice(["Azure Resource Graph","SIEM","IAM export","Backup report","Recovery test report"])
            })

    return {
        "seed":seed,"solution_type":solution_type,"edge_pattern":edge,"edge_services":EDGE_PATTERNS[edge],
        "compute_profile":compute,"compute_services":COMPUTE_PROFILES[compute],
        "data_profile":data,"data_services":DATA_PROFILES[data],"network_profile":net,
        "resilience_profile":resilience,"primary_region":primary,
        "secondary_region":secondary if multi_region else None,"multi_region":multi_region,"multi_az":multi_az,
        "availability_zones":[1,2,3] if multi_az else [1],"dr_mode":dr_mode,
        "rto_hours":rto,"rpo_minutes":rpo,"internet_facing":internet_facing,
        "private_endpoints":private_endpoints,"azure_firewall":firewall,"bastion":bastion,
        "ddos_protection":ddos,"expressroute":expressroute,"vpn":vpn,"nat_gateway":nat,
        "api_management":apim,"messaging":messaging,"entra_id":True,"managed_identity":managed_identity,
        "pim":pim,"conditional_access":ca,"key_vault":True,"sentinel":sentinel,
        "defender_for_cloud":defender,"application_insights":appinsights,"logs_to_siem":logs_to_siem,
        "backup_enabled":backup_enabled,"restore_tested":restore_tested,"dr_tested":dr_tested,
        "azure_site_recovery":asr,"data_replication":data_replication,"defects":defects,
        "inconsistencies":inconsistencies,"version":f"{rng.randint(1,4)}.{rng.randint(0,9)}",
        "diagram_age_days":rng.randint(0,120),
    }

def architecture_flows(profile:Dict[str,Any]) -> List[Dict[str,Any]]:
    flows=[]
    def add(src,dst,proto,purpose,trust="internal"):
        flows.append({"source":src,"destination":dst,"protocol":proto,"purpose":purpose,"trust":trust})
    if profile["internet_facing"]:
        add("Users",profile["edge_services"][0],"HTTPS 443","User / API traffic","external")
        for a,c in zip(profile["edge_services"],profile["edge_services"][1:]): add(a,c,"HTTPS 443","Edge forwarding","external")
        last=profile["edge_services"][-1]
    else: last="Corporate Network"
    if profile["api_management"]:
        add(last,"Azure API Management","HTTPS 443","API gateway / policy enforcement"); last="Azure API Management"
    add(last,profile["compute_services"][0],"HTTPS 443","Application request")
    for c in profile["compute_services"][1:]: add(profile["compute_services"][0],c,"Internal TCP/HTTPS","Workload communication")
    for d in profile["data_services"]: add(profile["compute_services"][0],d,"Private Link / TLS" if profile["private_endpoints"] else "TLS / public service endpoint","Application data")
    if profile["messaging"]:
        add(profile["compute_services"][0],"Azure Service Bus","AMQP/TLS","Commands / async work")
        add(profile["compute_services"][0],"Azure Event Hubs","AMQP/TLS","Events / telemetry")
    add(profile["compute_services"][0],"Azure Key Vault","HTTPS 443","Secrets / keys")
    if profile["sentinel"]: add(profile["compute_services"][0],"Log Analytics / Sentinel","HTTPS 443","Logs and detections")
    if profile["expressroute"] or profile["vpn"]: add("Corporate Network","Hub VNet","ExpressRoute/VPN","Private hybrid connectivity")
    if profile["multi_region"]: add("Primary Region","Secondary Region","Replication","DR replication / failover")
    return flows

_ICON_REGISTRY = None
_ICON_HITS = 0
_ICON_MISSES = 0

COLORS={"edge":"#E9F3FF","compute":"#E9F8F1","data":"#FFF0F3","security":"#EEF3FF","network":"#E7FAFA","dr":"#F5EDFF","external":"#F4F4F4","identity":"#F2ECFF","azure":"#0078D4","text":"#17365D"}
def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def rect(x,y,w,h,fill,stroke="#7FA9D8",rx=10,sw=2): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def text(x,y,s,size=16,weight="normal",anchor="start",fill="#17365D"): return f'<text x="{x}" y="{y}" font-family="Arial,Segoe UI,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{esc(s)}</text>'
def badge(x,y,n,color="#2F5597"):
    return f'<circle cx="{x}" cy="{y}" r="12" fill="#FFFFFF" stroke="{color}" stroke-width="3"/><text x="{x}" y="{y+4}" font-family="Arial,Segoe UI,sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="{color}">{n}</text>'
def service(x,y,w,h,name,category="compute",subtitle=None):
    global _ICON_HITS, _ICON_MISSES
    out=rect(x,y,w,h,COLORS.get(category,"#FFF"))
    uri=_ICON_REGISTRY.data_uri(name) if _ICON_REGISTRY and _ICON_REGISTRY.available else None
    if uri:
        _ICON_HITS += 1
        size=min(34,h-12)
        out+=f'<image x="{x+10}" y="{y+(h-size)/2}" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet" href="{uri}"/>'
    else:
        _ICON_MISSES += 1
        out+=f'<circle cx="{x+24}" cy="{y+22}" r="12" fill="#0078D4"/>'
        out+=text(x+24,y+27,"Az",9,"bold","middle","white")
    label=name if len(name)<=28 else name[:27]+"…"
    # leave icon column free; center label slightly right
    out+=text(x+w/2+10,y+27,label,12,"bold","middle")
    if subtitle: out+=text(x+w/2+10,y+h-9,subtitle,9,"normal","middle","#51677F")
    return out
def arrow(x1,y1,x2,y2,label="",color="#2F5597",dash=False,label_dx=0,label_dy=0):
    ds=' stroke-dasharray="8 6"' if dash else ''
    out=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3" stroke-linecap="round"{ds} marker-end="url(#arrow)"/>'
    if label:
        lx=(x1+x2)/2+label_dx; ly=(y1+y2)/2-8+label_dy
        out += f'<rect x="{lx-46}" y="{ly-13}" width="92" height="18" rx="7" fill="white" opacity="0.92"/>'
        out += text(lx,ly,label,10,"bold","middle",color)
    return out

def orth_arrow(points,label="",color="#2F5597",dash=False,label_pos=0.5):
    ds=' stroke-dasharray="8 6"' if dash else ''
    pts=' '.join(f"{x},{y}" for x,y in points)
    out=f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"{ds} marker-end="url(#arrow)"/>'
    if label:
        # estimate label point along polyline
        import math
        segs=[]; total=0
        for (x1,y1),(x2,y2) in zip(points[:-1],points[1:]):
            d=((x2-x1)**2+(y2-y1)**2)**0.5; segs.append((x1,y1,x2,y2,d)); total+=d
        target=total*label_pos; cur=0; lx,ly=points[0]
        for x1,y1,x2,y2,d in segs:
            if cur+d>=target and d>0:
                r=(target-cur)/d; lx=x1+(x2-x1)*r; ly=y1+(y2-y1)*r; break
            cur+=d
        out += f'<rect x="{lx-54}" y="{ly-14}" width="108" height="18" rx="7" fill="white" opacity="0.94"/>'
        out += text(lx,ly-1,label,10,"bold","middle",color)
    return out

def render_architecture(profile:Dict[str,Any], project:Dict[str,Any], out_svg:Path, out_png:Path, icon_root:Path|None=None):
    global _ICON_REGISTRY, _ICON_HITS, _ICON_MISSES
    _ICON_REGISTRY=AzureIconRegistry(icon_root)
    _ICON_HITS=0; _ICON_MISSES=0
    W,H=1980,1320
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#2F5597"/></marker></defs>',
       '<rect width="100%" height="100%" fill="#FBFDFF"/>']
    s += [rect(22,22,1935,92,'#FFFFFF','#C9D8EA',12,1),
          text(30,46,f"Azure HLD - {project['project_name']}",30,'bold'),
          text(30,72,f"Project {project['project_id']} | {profile['solution_type']} | Diagram v{profile['version']}",15),
          text(30,96,f"Primary: {profile['primary_region']} | Resilience: {profile['resilience_profile']} | Compute: {profile['compute_profile']}",14)]

    # Frames
    s += [rect(25,160,225,395,COLORS['external']), text(40,190,'Clients / Identity / On-Prem',18,'bold')]
    s += [rect(275,160,245,395,COLORS['edge']), text(290,190,'Ingress / Edge',18,'bold')]
    s += [rect(545,135,980,875,'#F6FBFF','#3C9CE0',14,3), text(565,165,f"Primary Azure Region - {profile['primary_region']}",21,'bold')]
    s.append(text(1500,165,'Multi-AZ' if profile['multi_az'] else 'Single AZ / no AZ guarantee',13,'bold','end','#2E75B6' if profile['multi_az'] else '#C65911'))

    # External nodes
    ext_nodes=[(45,215,'Users','external','Web / API consumers'), (45,320,'Microsoft Entra ID','identity','SSO / MFA / Conditional Access')]
    if profile['expressroute'] or profile['vpn']:
        ext_nodes.append((45,425,'Corporate Network','external','Hybrid source'))
    for x,y,name,cat,sub in ext_nodes:
        s.append(service(x,y,185,72,name,cat,sub))

    # Edge stack
    edge_y=215
    edge_positions=[]
    for svc in profile['edge_services']:
        s.append(service(300,edge_y,195,72,svc,'edge'))
        edge_positions.append((svc,300,edge_y,195,72))
        edge_y += 100
    if profile['ddos_protection']:
        s.append(service(300,edge_y,195,62,'DDoS Protection','security'))
        edge_positions.append(('DDoS Protection',300,edge_y,195,62))
        edge_y += 84

    # Hub/shared services
    hub_x, hub_y = 570, 200
    hub_w, hub_h = 230, 760
    s += [rect(hub_x,hub_y,hub_w,hub_h,COLORS['network']), text(hub_x+15,hub_y+28,'Shared Services / Hub',17,'bold')]
    hy=250; hub_cards=[]
    for cond,name,sub in [
        (profile['azure_firewall'],'Azure Firewall','Network filtering / egress control'),
        (profile['bastion'],'Azure Bastion','Privileged administration'),
        (True,'Private DNS','Name resolution'),
        (profile['nat_gateway'],'NAT Gateway','Controlled outbound access'),
        (profile['expressroute'] or profile['vpn'],'ER / VPN Gateway','Hybrid connectivity'),
    ]:
        if cond:
            s.append(service(hub_x+20,hy,190,64,name,'network',sub))
            hub_cards.append((name,hub_x+20,hy,190,64))
            hy += 82

    # Application / compute spoke
    app_x, app_y = 825, 200
    app_w, app_h = 325, 620
    s += [rect(app_x,app_y,app_w,app_h,COLORS['compute']), text(app_x+15,app_y+28,'Application / Compute Spoke',17,'bold')]
    cy=248; compute_cards=[]
    if profile['api_management']:
        s.append(service(app_x+22,cy,280,64,'API Gateway (Azure API Management)','edge','Policy / auth / throttling'))
        compute_cards.append(('API Gateway (Azure API Management)',app_x+22,cy,280,64))
        cy += 84
    for svc in profile['compute_services'][:5]:
        subtitle='Primary app path' if len(compute_cards)==0 else 'Workload component'
        s.append(service(app_x+22,cy,280,60,svc,'compute',subtitle))
        compute_cards.append((svc,app_x+22,cy,280,60))
        cy += 80
        if cy > app_y + app_h - 72:
            break

    # Data spoke
    data_x, data_y = 1178, 200
    data_w, data_h = 330, 620
    s += [rect(data_x,data_y,data_w,data_h,COLORS['data']), text(data_x+15,data_y+28,'Data Services Spoke',17,'bold')]
    dy=248; data_cards=[]
    for svc in profile['data_services'][:6]:
        sub='Private Endpoint' if profile['private_endpoints'] else 'Public / Service Endpoint'
        s.append(service(data_x+24,dy,282,60,svc,'data',sub))
        data_cards.append((svc,data_x+24,dy,282,60))
        dy += 80
        if dy > data_y + data_h - 72:
            break

    # Security / monitoring
    sec_x, sec_y = 825, 848
    sec_w, sec_h = 683, 152
    s += [rect(sec_x,sec_y,sec_w,sec_h,COLORS['security']), text(sec_x+15,sec_y+28,'Security, Monitoring, Backup & Recovery',17,'bold')]
    ops=[]
    if profile['application_insights']:
        ops.append('Application Insights')
    ops += ['Azure Monitor','Log Analytics']
    if profile['sentinel']:
        ops.append('Microsoft Sentinel')
    if profile['defender_for_cloud']:
        ops.append('Defender for Cloud')
    if profile['backup_enabled']:
        ops.append('Azure Backup / RSV')
    sec_cards=[]
    for i,svc in enumerate(ops[:6]):
        x=sec_x+18+(i%3)*214; y=sec_y+42+(i//3)*74
        s.append(service(x,y,188,58,svc,'security'))
        sec_cards.append((svc,x,y,188,58))

    # DR / resilience
    if profile['multi_region']:
        s += [rect(1550,135,345,865,COLORS['dr'],'#9673C5',14,3), text(1568,165,'Secondary Region / DR',19,'bold'), text(1568,190,profile['secondary_region'],14)]
        dr_cards=[]
        dr_specs=[('DR Compute',profile['dr_mode']), ('Replicated Data',profile['data_replication'])]
        if profile['azure_site_recovery']:
            dr_specs.append(('Azure Site Recovery','Orchestration'))
        if profile['backup_enabled']:
            dr_specs.append(('Recovery Vault','Backup / restore'))
        dr_specs.append(('DR Health / Failover','Tested' if profile['dr_tested'] else 'NOT TESTED'))
        y=230
        for name,sub in dr_specs:
            s.append(service(1570,y,280,72,name,'dr',sub))
            dr_cards.append((name,1570,y,280,72))
            y += 96
    else:
        s += [rect(1550,135,345,445,'#FFF8E7','#D6A64A',14,3), text(1568,165,'Resilience Boundary',19,'bold')]
        dr_cards=[]
        for name,sub,y in [(profile['dr_mode'],'Current resilience mode',220), ('Backup Strategy','Restore tested' if profile['restore_tested'] else 'Restore NOT tested',320)]:
            s.append(service(1570,y,280,78,name,'dr',sub))
            dr_cards.append((name,1570,y,280,78))

    # Connections - fewer labels, placed in empty corridors
    first_edge=edge_positions[0]
    s.append(orth_arrow([(230,251),(270,251),(270,251),(300,251)],'',label_pos=.55))
    for (_,x,y,w,h),(_,nx,ny,nw,nh) in zip(edge_positions[:-1],edge_positions[1:]):
        s.append(orth_arrow([(x+w,y+h/2),(x+w+18,y+h/2),(x+w+18,ny+nh/2),(nx,ny+nh/2)],'',label_pos=.55))

    target_y = compute_cards[0][2] + compute_cards[0][4]/2 if compute_cards else 260
    s.append(orth_arrow([(230,356),(520,356),(520,target_y),(app_x+22,target_y)],'',color='#7A4FB0',label_pos=.42))
    if profile['expressroute'] or profile['vpn']:
        s.append(orth_arrow([(230,461),(570,461)],'',color='#0E7490',label_pos=.55))

    last_edge=edge_positions[-1]
    edge_exit_y=last_edge[2]+last_edge[4]/2
    first_app=compute_cards[0]
    first_app_entry=(first_app[1], first_app[2]+first_app[4]/2)
    s.append(orth_arrow([(last_edge[1]+last_edge[3],edge_exit_y),(760,edge_exit_y),(760,first_app_entry[1]),first_app_entry],'',label_pos=.45))

    # unlabeled internal compute chain
    for (_,x,y,w,h),(_,nx,ny,nw,nh) in zip(compute_cards[:-1],compute_cards[1:]):
        s.append(orth_arrow([(x+w/2,y+h),(x+w/2,ny-10),(nx+nw/2,ny-10),(nx+nw/2,ny)],'',color='#4F6D8A',label_pos=.6))

    # one labeled trunk for data access, then unlabeled branches
    source=compute_cards[min(1,len(compute_cards)-1)]
    trunk_y=source[2]+source[4]/2
    trunk_x_start=source[1]+source[3]
    trunk_x_mid=1148
    s.append(orth_arrow([(trunk_x_start,trunk_y),(trunk_x_mid,trunk_y)],'',color='#B03A5B',label_pos=.5))
    for dc in data_cards[:4]:
        dy_mid=dc[2]+dc[4]/2
        s.append(orth_arrow([(trunk_x_mid,trunk_y),(trunk_x_mid,dy_mid),(dc[1],dy_mid)],'',color='#B03A5B',label_pos=.72))

    # telemetry trunk
    sec_target=sec_cards[0]
    sec_mid=sec_target[2]+sec_target[4]/2
    s.append(orth_arrow([(source[1]+source[3]/2, source[2]+source[4]),(source[1]+source[3]/2,835),(sec_target[1]+40,835),(sec_target[1]+40,sec_mid)],'',color='#2F855A',label_pos=.48))

    if profile['multi_region']:
        s.append(orth_arrow([(1500,330),(1570,330)],'',color='#7030A0',dash=True,label_pos=.6))
        s.append(orth_arrow([(1500,880),(1570,880)],'',color='#7030A0',dash=True,label_pos=.6))
    else:
        s.append(orth_arrow([(1500,340),(1570,340)],'',color='#A16207',dash=True,label_pos=.6))

    # Numbered flow markers (kept off the service cards)
    s += [badge(258,238,1,'#2F5597'), badge(535,340,2,'#7A4FB0')]
    if profile['expressroute'] or profile['vpn']:
        s.append(badge(392,446,3,'#0E7490'))
    s += [badge(775,edge_exit_y-16,4,'#2F5597'), badge(1162,trunk_y-16,5,'#B03A5B'), badge(source[1]+source[3]/2+18,836,6,'#2F855A')]
    if profile['multi_region']:
        s += [badge(1534,316,7,'#7030A0'), badge(1534,866,8,'#7030A0')]
    else:
        s += [badge(1534,326,7,'#A16207')]

    # Summary and legend
    s.append(rect(25,1030,1890,260,'#F7F9FC','#B8C6D8',8,1))
    s.append(text(45,1060,'Summary',16,'bold'))
    facts=[
        f"Edge path: {' -> '.join(profile['edge_services'])}",
        f"API gateway: {'enabled' if profile['api_management'] else 'not present'} | Compute: {profile['compute_profile']}",
        f"Network: {profile['network_profile']} | Private endpoints: {profile['private_endpoints']} | Firewall: {profile['azure_firewall']}",
        f"Resilience: {profile['resilience_profile']} | Multi-AZ: {profile['multi_az']} | Multi-region: {profile['multi_region']}",
        f"RTO/RPO: {profile['rto_hours']}h / {profile['rpo_minutes']}min | DR tested: {profile['dr_tested']} | Restore tested: {profile['restore_tested']}",
        f"Benchmark defects in hidden ground truth: {len(profile['defects'])}"
    ]
    for i,f in enumerate(facts):
        s.append(text(45,1088+i*24,f,13))
    lx=1110; ly=1060
    s += [text(lx,ly,'Flow legend',15,'bold')]
    legend_items=[
        (1,'HTTPS / API entry from users','#2F5597'),
        (2,'Identity and token flow','#7A4FB0'),
        (3,'Private / hybrid network access','#0E7490') if (profile['expressroute'] or profile['vpn']) else None,
        (4,'Request path into API / app tier','#2F5597'),
        (5,'Application to data services','#B03A5B'),
        (6,'Telemetry / monitoring / SIEM','#2F855A'),
        (7,'DR orchestration or backup path','#7030A0' if profile['multi_region'] else '#A16207'),
        (8,'Replication / failover path','#7030A0') if profile['multi_region'] else None,
    ]
    row=0
    for item in legend_items:
        if not item: continue
        num,desc,color=item
        col=0 if row<4 else 1
        yy=ly+30+(row%4)*26; xx=lx+col*360
        s.append(badge(xx,yy-4,num,color))
        s.append(text(xx+20,yy,desc,12))
        row += 1
    icon_mode = 'Official Azure Architecture Icons' if (_ICON_REGISTRY and _ICON_REGISTRY.available) else 'Fallback icons (official pack not installed)'
    s.append(text(1910,1288,f"Icon mode: {icon_mode} | mapped {_ICON_HITS} | fallback {_ICON_MISSES}",10,'normal','end','#66788A'))
    s.append('</svg>')
    out_svg.write_text('\n'.join(s),encoding='utf-8')
    cairosvg.svg2png(bytestring=out_svg.read_bytes(),write_to=str(out_png),output_width=W,output_height=H)
    return out_svg,out_png

def write_profile(profile,project,out_json:Path):
    out_json.write_text(json.dumps({"project":project,"architecture_profile":profile,"flows":architecture_flows(profile)},ensure_ascii=False,indent=2),encoding='utf-8')
    return out_json