"""Render tables/figures from the stored stochastic experiment outputs."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
rows=list(csv.DictReader((OUT/'sensitivity_summary.csv').open()))
plt.rcParams.update({'font.size':9,'pdf.fonttype':42})
fig,axes=plt.subplots(1,3,figsize=(7.2,2.5),sharey=True)
for ax,dist in zip(axes,('continuous','lognormal','evolved')):
    for placement in ('high','random'):
        r=[x for x in rows if x['n']=='128' and x['k']=='16' and x['distribution']==dist and x['placement']==placement]
        r.sort(key=lambda x:float(x['fraction_requested']))
        x=[float(s['fraction_requested']) for s in r];y=np.array([float(s['mean_risk']) for s in r])
        lo=np.array([float(s['population_t_low']) for s in r]);hi=np.array([float(s['population_t_high']) for s in r])
        ax.errorbar(x,y,yerr=np.array([y-lo,hi-y]),marker='o',capsize=3,label=placement)
    ax.set(title=dist,xlabel='Adversarial fraction',ylim=(-.03,1.03),xticks=[.1,.25,.4]);ax.grid(alpha=.2)
axes[0].set_ylabel('Byzantine-bound exceedance');axes[0].legend(fontsize=8)
fig.tight_layout();fig.savefig(ROOT/'figures/sensitivity.pdf');plt.close(fig)
summary=json.loads((OUT/'probabilistic_verification.json').read_text())
assert summary['trajectory_sampling_censored']==0
(OUT/'probabilistic_findings.tex').write_text(
    'Table~\\ref{tab:probabilistic} reports the three-level results. Full exclusion terminates in all 200 runs at each of $n=16,32$, while no empty-family termination is observed at $n=64,128,256$. All proposer-only runs reach the horizon. For equal initialization, full exclusion fails after one successful round in every run, as proved analytically; proposer-only runs reach the horizon. The exact grouped fallback is used 149 times, leaving no sampling-censored runs. A zero observed rate has a Wilson upper endpoint of 0.01885 at $N=200$, rather than proving zero risk. The solver-witness count 10/25 is deliberately not pooled with these data.\n')
parts=[]
for dist in ('continuous','lognormal','evolved'):
    pair={r['placement']:r for r in rows if r['n']=='128' and r['k']=='16' and r['distribution']==dist and r['fraction_requested']=='0.25'}
    parts.append(f"{dist} scores yield mean exposure {float(pair['high']['mean_risk']):.3f} under high-weight placement and {float(pair['random']['mean_risk']):.3f} under random placement")
(OUT/'sensitivity_findings.tex').write_text('At $n=128$, $k=16$, and requested adversarial fraction 0.25, '+ '; '.join(parts)+'. Fig.~\\ref{fig:sensitivity} shows the corresponding sensitivity curves and population-level uncertainty.\n')
print('Generated probabilistic findings and sensitivity figure.')
