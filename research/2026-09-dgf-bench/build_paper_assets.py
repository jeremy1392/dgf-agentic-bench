"""Render manuscript tables, results chart, workflow, and architecture specimen."""
import json
import shutil
import cairosvg
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
payload = json.loads((HERE/'paper_results.json').read_text(encoding='utf-8'))
details = json.loads((HERE/'diagnostics.json').read_text(encoding='utf-8'))
models = ['deepseek/deepseek-v4.1-flash', 'google/gemini-3.8-flash', 'openai/gpt-5.6-luna']
names = ['DeepSeek', 'Gemini', 'Luna']
rows = {r['model']: r for r in payload['overall']}
out = ROOT/'paper/generated'
lines = []
for m, name in zip(models, names):
    r = rows[m]
    gate = f"{100*r['gate_csr']:.2f}\\% [{100*r['gate_csr_ci95_low']:.2f}, {100*r['gate_csr_ci95_high']:.2f}]"
    route = f"{100*r['route_complete_rate']:.2f}\\% [{100*r['route_complete_ci95_low']:.2f}, {100*r['route_complete_ci95_high']:.2f}]"
    lines.append(f"{name} & {r['cases']} & {gate} & {route} & {r['total_cost_usd']:.2f} " + r'\\')
(out/'table_benchmark_overall.tex').write_text('\n'.join(lines)+'\n', encoding='utf-8')
lines = []
for route in ['buy', 'integrate', 'build']:
    cells = [route.title()]
    for m in models:
        r = details[m]['routes'][route]
        cells.append(f"{100*r['gate_success']/r['gates']:.2f}\\%; {r['route_success']}/{r['cases']}")
    lines.append(' & '.join(cells) + r'\\')
(out/'table_benchmark_routes.tex').write_text('\n'.join(lines)+'\n', encoding='utf-8')
gates = {(r['model'], r['gate']): r for r in payload['gates']}
lines = []
for gate in sorted({r['gate'] for r in payload['gates']}):
    name = 'IT' if gate == 'it' else gate.replace('_', ' ').title()
    lines.append(' & '.join([name]+[f"{100*gates[m,gate]['csr']:.2f}" for m in models]) + r'\\')
(out/'table_benchmark_gates.tex').write_text('\n'.join(lines)+'\n', encoding='utf-8')
order = [1, 2, 0]
colors = ['#286b89', '#42a39a', '#a36c24']
fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.8))
for ax, metric, ci, title in zip(axes, ['gate_csr','route_complete_rate'], ['gate_csr','route_complete'], ['Strict gate success (%)','Entire route success (%)']):
    rr = [rows[models[i]] for i in order]
    values = np.array([100*r[metric] for r in rr])
    low = np.array([100*r[ci+'_ci95_low'] for r in rr]); high = np.array([100*r[ci+'_ci95_high'] for r in rr])
    ax.barh(range(3), values, color=colors, height=.5)
    ax.errorbar(values, range(3), xerr=[values-low,high-values], fmt='none', ecolor='#142c40', capsize=4)
    for y, value in enumerate(values): ax.text(3, y, f'{value:.1f}%', va='center', color='white', weight='bold', fontsize=12)
    ax.set_yticks(range(3), [names[i] for i in order] if ax == axes[0] else ['']*3)
    ax.invert_yaxis(); ax.set_xlim(0,105); ax.set_xticks([0,25,50,75,100]); ax.set_title(title, fontsize=12)
    ax.spines[['top','right','left']].set_visible(False); ax.tick_params(axis='y',length=0)
    ax.grid(axis='x',alpha=.15); ax.set_axisbelow(True)
fig.tight_layout(pad=1.5)
fig.savefig(ROOT/'paper/figures/fig_benchmark_results.pdf')
cairosvg.svg2pdf(url=str(ROOT/'assets/readme/experiment-walkthrough.svg'),
                write_to=str(ROOT/'paper/figures/fig_benchmark_walkthrough.pdf'))
shutil.copyfile(ROOT/'assets/readme/example-architecture.png', ROOT/'paper/figures/fig_benchmark_architecture.png')
print('Rebuilt three manuscript tables, results chart, workflow and architecture specimen.')
