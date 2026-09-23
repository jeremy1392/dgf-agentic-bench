"""Build the README's explanatory research figures from repository definitions.

Run: python assets/readme/build_research_figures.py [--render-png]
SVG generation uses the standard library. Optional PNG exports use CairoSVG.
No model calls or experimental results are involved.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html import escape
import importlib.util
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
spec = importlib.util.spec_from_file_location("figure_routes", ROOT / "routes.py")
routes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routes)

INK = "#142c40"
MUTED = "#506678"
BLUE = "#286b89"
GOLD = "#a36c24"
LINE = "#d5dfe6"
PALE = "#eef4f7"


class Figure:
    def __init__(self, height, title, description, label):
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{height}" viewBox="0 0 1400 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M1 1 L7 4.5 L1 8" fill="none" stroke="#627f90" stroke-width="1.5"/></marker></defs>',
            '<rect x="1" y="1" width="1398" height="'+str(height-2)+'" rx="12" fill="#fcfdfd" stroke="#d5dfe6"/>',
            '<g font-family="Arial, Helvetica, sans-serif">',
        ]
        self.text(48, 43, label, 13, BLUE, weight="700", spacing="2")
        self.text(48, 89, title, 32, INK, weight="700")

    def text(self, x, y, text, size=18, color=INK, weight="400", anchor="start", spacing="0"):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}">{escape(text)}</text>')

    def lines(self, x, y, values, size=18, color=MUTED, step=27, anchor="start"):
        for i, text in enumerate(values):
            self.text(x, y+i*step, text, size, color, anchor=anchor)

    def rect(self, x, y, w, h, fill=PALE, stroke=LINE, radius=9):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')

    def path(self, d, color=LINE, width=1.5, arrow=False, dash=False):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="6 5"' if dash else '')+'/>')

    def footer(self, text):
        self.path(f'M48 {self.height-57} H1352')
        self.text(48, self.height-28, text, 15, MUTED)

    def save(self, name):
        path = OUT / (name+'.svg')
        path.write_text('\n'.join(self.parts+['</g></svg>'])+'\n', encoding='utf-8')
        return path


def lifecycle():
    f=Figure(816, 'A Digital Governance Framework across the project lifecycle',
             'An activity matrix generated from the full_lifecycle route. Rows are eight gate families; columns are five project phases. Filled circles indicate specialist reviews; diamonds indicate General gate arbitration. Each phase can invoke a gate with a different contract.',
             'FIGURE 01 / FRAMEWORK STRUCTURE')
    f.text(48, 125, 'One configurable example: a gate can recur in different phases with a different review contract.', 19, MUTED)
    phases=['opportunity','framing','design','build_acceptance','deployment_closure']
    labels=[['Opportunity'],['Framing &','feasibility'],['Design'],['Build &','acceptance'],['Deployment &','closure']]
    gates=['it','architecture','security','tech_readiness','procurement','legal','compliance','general']
    names=['IT','Architecture','Security','Tech Readiness','Procurement','Legal','Compliance','General']
    active=set(routes.ROUTES['full_lifecycle']['occurrences'])
    xs=[400,610,820,1030,1240]
    for i,(phase,lines,x) in enumerate(zip(phases,labels,xs)):
        f.rect(x-91,158,182,77, '#edf4f7', '#c7d8e1')
        f.text(x-72,181,f'0{i+1}',12,BLUE,weight='700')
        f.lines(x,201 if len(lines)>1 else 212,lines,17,INK,21,'middle')
        if i<4:f.path(f'M{x+93} 197 H{xs[i+1]-97}', '#627f90', arrow=True)
    for i,(gate,name) in enumerate(zip(gates,names)):
        y=277+i*52
        f.rect(48,y-22,1304,46,'#f1f4f6' if i%2==0 else '#fcfdfd','none',3)
        f.text(68,y+6,name,19,INK,weight='700' if gate=='general' else '400')
        for phase,x in zip(phases,xs):
            if (gate,phase) in active:
                if gate=='general':
                    f.parts.append(f'<path d="M{x} {y-12} l12 12 -12 12 -12 -12 Z" fill="{GOLD}"/>')
                else:f.parts.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{BLUE}"/>')
            else:f.path(f'M{x-6} {y} H{x+6}', '#aab8c2',1.5)
    count=Counter(p for g,p in active)
    f.text(68,699,'Reviews / phase',15,MUTED)
    for phase,x in zip(phases,xs):f.text(x,699,str(count[phase]),17,INK,weight='700',anchor='middle')
    f.parts.append(f'<circle cx="61" cy="731" r="7" fill="{BLUE}"/>')
    f.text(79,737,'Specialist review',15,MUTED)
    f.parts.append(f'<path d="M286 722 l9 9 -9 9 -9 -9 Z" fill="{GOLD}"/>')
    f.text(305,737,'General gate arbitration',15,MUTED)
    f.text(1346,737,f'{len(active)} gate occurrences in this full-lifecycle example',15,MUTED,anchor='end')
    f.footer('Source: routes.py · full_lifecycle. Illustrative composition, not a mandatory enterprise standard.')
    return f.save('dgf-lifecycle-matrix')


def contract():
    f=Figure(750,'The gate as an evidence and authorization contract',
             'An owner prepares a dossier. An agent or reviewing expert investigates evidence under a gate and phase policy, then produces findings, a disposition, proposed actions, citations and an authorization state. A scoped mandate separately governs permitted actions. REWORK can request a revised dossier. In the benchmark this is a simulated review, not proof of production execution.',
             'FIGURE 02 / UNIT OF ANALYSIS')
    f.text(48,125,'Each occurrence has inputs, decision rules, evidence obligations, permitted actions, and a traceable output.',19,MUTED)
    f.rect(445,162,907,86,'#fbf3e7','#d8bb90')
    f.text(468,192,'AUTHORITY / VALIDATED MANDATE',13,GOLD,weight='700',spacing='1')
    f.text(468,224,'Gate + phase + finding scope + conditions',21,INK)
    f.text(1330,224,'Permission is checked separately.',16,MUTED,anchor='end')
    f.rect(48,287,340,259)
    f.rect(445,287,410,259,'#eaf3f7','#93b4c5')
    f.rect(912,287,440,259)
    for x,label,title in [(72,'INPUT / DOSSIER OWNER','Versioned evidence'),(469,'REVIEW / AGENT OR EXPERT','Investigate and assess'),(936,'OUTPUT / RECORDED REVIEW','A structured decision')]:
        f.text(x,320,label,13,BLUE,weight='700',spacing='1')
        f.text(x,358,title,23,INK,weight='700')
    f.lines(72,398,['Project facts + documents','Applicable policy + gate phase','Available upstream decisions','Evidence provenance'],18,step=34)
    f.lines(469,398,['Read and cross-check evidence','Request missing information','Identify findings + required actions','Check permitted governance actions'],18,step=34)
    f.lines(936,398,['Findings + evidence references','Disposition + proposed actions','Authorization state + rationale','Trace for scoring and handoff'],18,step=34)
    f.path('M390 418 H437','#627f90',arrow=True)
    f.path('M857 418 H904','#627f90',arrow=True)
    f.path('M650 248 V279',GOLD,arrow=True,dash=True)
    f.path('M1132 248 V279',GOLD,arrow=True,dash=True)
    f.path('M1132 546 V592 H216 V554','#627f90',arrow=True,dash=True)
    f.rect(430,575,500,33,'#fcfdfd','none',4)
    f.text(680,597,'REWORK → revise evidence and return for review',16,MUTED,anchor='middle')
    labels=['GO','GO_WITH_RESERVATIONS','REWORK','SUSPENSION','NO_GO']
    widths=[116,340,180,210,146]
    x=145
    for label,w in zip(labels,widths):
        f.rect(x,633,w,37,'#eef3f5','#d5dfe6',6)
        f.text(x+w/2,657,label,15,INK,anchor='middle')
        x+=w+16
    f.footer('Concept: paper §2 and gate-contract appendix. Benchmark actions are simulated; real remediation is not assessed.')
    return f.save('gate-contract')


def main_routes():
    f=Figure(617,'Three routes through the governance framework',
             'Exact gate sequences and phases from routes.py for Buy, Integrate and Build. The General gate concludes each main route. These short routes are distinct from the full_lifecycle example in Figure 1.',
             'FIGURE 03 / ROUTE COMPOSITION')
    f.text(48,125,'Each node names a gate family and its review phase. Arrows show the evaluation order.',19,MUTED)
    names={'it':'IT','architecture':'Architecture','security':'Security','tech_readiness':'Tech Readiness',
           'procurement':'Procurement','legal':'Legal','compliance':'Compliance','general':'General'}
    phases={'design':'Design','build_acceptance':'Build / acceptance','opportunity':'Opportunity',
            'framing':'Framing','governance':'Governance'}
    for i,key in enumerate(['buy','integrate','build']):
        y=169+i*126
        f.text(48,y+39,key.upper(),18,BLUE,weight='700')
        sequence=routes.ROUTES[key]['occurrences']
        f.text(48,y+67,f'{len(sequence)} reviews',15,MUTED)
        xs=[190+194*j for j in range(len(sequence)-1)]+[1160]
        for j,((gate,phase),x) in enumerate(zip(sequence,xs)):
            f.rect(x,y,166,88,'#fbf3e7' if gate=='general' else PALE,'#d8bb90' if gate=='general' else LINE)
            f.text(x+83,y+35,names[gate],18,INK,weight='700',anchor='middle')
            f.text(x+83,y+66,phases[phase],14,MUTED,anchor='middle')
            if j<len(xs)-1:f.path(f'M{x+169} {y+44} H{xs[j+1]-8}','#627f90',arrow=True)
    f.text(48,547,'Handoff conditions: agent outputs · reference outputs (oracle) · no upstream handoff',17,MUTED)
    f.footer('Source: routes.py. Phase labels identify benchmark occurrences; these are example routes, not a universal sequence.')
    return f.save('dgf-main-routes')


def design():
    keys=['buy','integrate','build'];n=100;k=3
    gates=sum(len(routes.ROUTES[r]['occurrences'])*n for r in keys)
    f=Figure(768,'A controlled comparison on shared dossiers',
             'An example design uses 100 Buy, 100 Integrate and 100 Build dossiers, evaluated by three models on the same case set. It schedules 900 model-case runs and 5100 gate occurrences. Counts describe the design, not completed results. Reference outcomes are evaluator-only; model availability and technical exclusions must be reported. Statistical comparisons retain the dossier as the sampling unit.',
             'FIGURE 04 / EXPERIMENTAL DESIGN')
    f.text(48,125,'Example configuration: 300 cases × 3 models. These are design counts, not completed results.',19,MUTED)
    f.rect(48,166,355,267)
    f.text(72,198,'SHARED CASE SET',13,BLUE,weight='700',spacing='1')
    f.text(72,238,'300 synthetic dossiers',25,INK,weight='700')
    for i,route in enumerate(keys):
        y=279+i*47
        f.text(72,y,f'{n} {route.capitalize()}',19,INK)
        f.text(379,y,f'{len(routes.ROUTES[route]["occurrences"])} gates / case',16,MUTED,anchor='end')
    f.text(72,411,'Same cases for every model',16,BLUE,weight='700')
    f.rect(462,166,377,267,'#eaf3f7','#93b4c5')
    f.text(486,198,'MATCHED MODEL COMPARISON',13,BLUE,weight='700',spacing='1')
    for i,label in enumerate(['Model A','Model B','Model C']):
        y=216+i*63
        f.rect(486,y,329,49,'#fcfdfd','#bdd1dd',7)
        f.text(504,y+31,label,19,INK,weight='700')
        f.text(797,y+31,'300 cases',16,MUTED,anchor='end')
    f.text(486,411,'Fixed prompts, tools, and scoring',16,BLUE,weight='700')
    f.rect(898,166,454,267)
    f.text(922,198,'TRACEABLE EVALUATION',13,BLUE,weight='700',spacing='1')
    f.text(922,238,f'{300*k:,} model / case runs',25,INK,weight='700')
    f.text(922,276,f'{gates*k:,} scheduled gate occurrences',20,INK)
    f.lines(922,321,['Decisions, findings, evidence, authority','Strict gate success + route success','Cost, availability, and exclusions'],18,step=34)
    f.path('M405 299 H454','#627f90',arrow=True)
    f.path('M841 299 H890','#627f90',arrow=True)
    cards=[(48,355,'01 / FREEZE','Before evaluation',['Dataset + sampling policy','Prompts + model settings','Versioned scoring contract']),
           (462,377,'02 / COMPARE','Within shared cases',['Report scores on common cases','Separate technical exclusions','Preserve within-case dependence']),
           (898,454,'03 / INTERPRET','Within the study boundary',['Report uncertainty at case level','Validate business rules independently','Synthetic coverage ≠ real prevalence'])]
    for x,w,label,title,lines in cards:
        f.rect(x,478,w,199,'#fcfdfd','#d5dfe6')
        f.text(x+24,508,label,13,BLUE,weight='700',spacing='1')
        f.text(x+24,542,title,22,INK,weight='700')
        f.lines(x+24,580,lines,17,step=32)
    f.footer('Counts derived from routes.py for 100 cases per main route. 900 model/case runs are not 900 independent dossiers.')
    return f.save('research-design')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-png',action='store_true')
    args=parser.parse_args()
    paths=[lifecycle(),contract(),main_routes(),design()]
    for path in paths:
        if args.render_png:
            import cairosvg
            cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')),output_width=2100)
        print(path.relative_to(ROOT))


if __name__=='__main__':
    main()
