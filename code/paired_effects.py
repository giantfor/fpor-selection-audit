"""Population-paired exposure differences; no new simulated populations."""
from pathlib import Path
import csv, json
import numpy as np
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
rows = list(csv.DictReader((OUT / 'sensitivity_samples.csv').open()))
pairs = {}
for row in rows:
    key = tuple(row[k] for k in ('n','k','distribution','fraction_requested','replicate'))
    pair = pairs.setdefault(key, {})
    assert row['placement'] not in pair
    pair[row['placement']] = row
groups = {}
for key, pair in pairs.items():
    assert set(pair) == {'high','random'}
    a,b = pair['high'], pair['random']
    assert a['samples'] == b['samples'] == '500'
    assert a['malicious_nodes'] == b['malicious_nodes']
    # Placement does not change the sampled committees: fairness is identical.
    assert a['jain_plugin'] == b['jain_plugin']
    assert a['proportional_tv_plugin'] == b['proportional_tv_plugin']
    groups.setdefault(key[:-1], []).append(float(a['risk'])-float(b['risk']))
output=[]
for key, values in sorted(groups.items()):
    d=np.array(values); m=len(d)
    assert m == 40
    mean=float(d.mean()); sd=float(d.std(ddof=1)); half=float(t.ppf(.975,m-1)*sd/np.sqrt(m))
    output.append(dict(zip(('n','k','distribution','fraction_requested'),key),
        populations=m,mean_difference=mean,sd_difference=sd,se_difference=sd/np.sqrt(m),
        ci_low=mean-half,ci_high=mean+half))
with (OUT/'paired_effects.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=output[0]);w.writeheader();w.writerows(output)
table=[r'\begin{tabular}{llrr}',r'\toprule',r'Scores & Fraction & $\Delta P_B$ & 95\% CI \\',r'\midrule']
for r in output:
    if r['n']=='128' and r['k']=='16':
        table.append(f"{r['distribution'].capitalize()} & {float(r['fraction_requested']):.2f} & {r['mean_difference']:.5f} & [{r['ci_low']:.5f}, {r['ci_high']:.5f}] \\")
        table[-1] += '\\'
table += [r'\bottomrule',r'\end{tabular}']
(OUT/'paired_effects_table.tex').write_text('\n'.join(table)+'\n')
report=dict(pairs=len(pairs),configurations=len(output),populations_per_configuration=40,
    estimand='mean population-paired high-minus-random composition exposure',
    interval='pointwise approximate Student t, df=39; not simultaneous',
    includes='population variability, finite committee sampling and one random adversarial set per population',
    excludes='operational attack success and recovery-policy causal effects')
(OUT/'paired_effects_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
