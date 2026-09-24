"""Recompute and draw the declared synthetic workforce scenarios (no inference)."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent


def calculate():
    params = json.loads((ROOT.parent / 'paper/anc/parameters.json').read_text(encoding='utf-8'))
    capacity = params['useful_hours_per_fte']
    visits = params['visits_per_population']
    values = []
    for name, regime in params['regimes'].items():
        hours = 0.0
        for pop in params['populations']:
            h0 = capacity * pop['people'] / visits
            hours += visits * (pop['q'] * params['kappa'] * regime['eta'] * h0
                              + (1-pop['q']) * regime['m'] * h0 + regime['hW']) + regime['BA']
        values.append(hours/capacity)
    assert [round(v,2) for v in values] == [43.52,85.32,89.07,168.92]
    baseline = sum(p['people'] for p in params['populations'])
    phi = sum(p['people']*p['q']*params['kappa'] for p in params['populations'])/baseline
    return baseline, values, phi


def main():
    baseline, values, phi = calculate()
    labels = ['Baseline', 'S0\nAssisted\nexceptions', 'S1\nBaseline\nexception effort',
              'S2\nAdded\nrework', 'S3\nHeavy\nassurance']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
    fig, ax = plt.subplots(figsize=(8.0,3.5),layout='constrained')
    bars=ax.bar(range(5),[baseline,*values],color=['#718096','#146b83','#37869b','#61a0b1','#b25a44'],width=.63)
    for bar,value in zip(bars,[baseline,*values]):
        ax.text(bar.get_x()+bar.get_width()/2,value+3,f'{value:.2f}',ha='center',fontweight='bold',fontsize=10)
    ax.axhline(.2*baseline,color='#8f3547',linestyle='--',linewidth=1.2)
    ax.text(4.65,.2*baseline+2,'28 FTE: 80% reduction target',ha='right',fontsize=9,color='#8f3547')
    ax.set_xticks(range(5),labels); ax.set_ylabel('Required human work (FTE)')
    ax.set_ylim(0,192);ax.set_xlim(-.6,4.7)
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.savefig(ROOT/'figures/fig_labor_scenarios.pdf',metadata={'CreationDate':None,'ModDate':None,'Title':'Illustrative human labor requirements; not measured deployment outcomes'})
    plt.close(fig)
    print(json.dumps({'baseline_fte':baseline,'scenario_fte':values,'weighted_phi':phi,'eta_max_for_80_percent_if_other_costs_zero':.2/phi}))


if __name__=='__main__':main()
