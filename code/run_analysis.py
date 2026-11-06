"""Exact finite-state selection audit, not a distributed FPoR implementation.
Run: python code/run_analysis.py (from the version directory).
No Monte Carlo estimates, hidden seeds, or measured network performance.
"""
from pathlib import Path
from itertools import combinations
from math import comb, ceil
import json, csv, platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'; FIG=ROOT/'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)

def metrics(n,h,k,policy,bh=4,btotal=4):
    committees=np.array(list(combinations(range(n),k)),dtype=int)
    high=(committees<h).sum(axis=1)
    reputations=np.array([120.]*h+[100.]*(n-h))
    threshold=ceil(k*h/n)
    valid=high>=threshold
    if policy=='uniform': masses=np.ones(len(committees))
    elif policy=='weighted': masses=1.2**high
    elif policy=='filtered': masses=valid.astype(float)
    elif policy=='filtered_weighted': masses=valid*(1.2**high)
    else: raise ValueError(policy)
    probs=masses/masses.sum()
    inclusion=np.bincount(committees.ravel(),weights=np.repeat(probs,k),minlength=n)
    assert abs(inclusion.sum()-k)<1e-10 and abs(probs.sum()-1)<1e-10
    bad=set(range(bh))|set(range(h,h+btotal-bh))
    counts=np.array([sum(int(i) in bad for i in c) for c in committees])
    risk=float(probs[counts>=(k-1)//3+1].sum())
    jain=float(k*k/(n*np.sum(inclusion**2)))
    # Frozen reputations, previous committee distributed by this policy.
    # A next committee must contain at least threshold remaining high nodes.
    next_impossible=(h-high<threshold) | (n-k<k)
    deadlock=float(probs[next_impossible].sum())
    accept=float((1.2**high)[valid].sum()/(1.2**high).sum()) if 'weighted' in policy else float(valid.mean())
    return dict(n=n,h=h,k=k,policy=policy,malicious_high=bh,malicious_total=btotal,
                valid_committees=int(valid.sum()),all_committees=len(committees),
                inclusion_high=float(inclusion[:h].mean()),inclusion_low=float(inclusion[h:].mean()),
                jain=jain,risk=risk,next_infeasible=deadlock,filter_acceptance=accept)

def formation_probability(n,h,k):
    q=ceil(k*h/n)
    counts={r:comb(h,r)*comb(n-h,k-r) for r in range(max(q,k-(n-h)),min(h,k)+1)}
    den=sum(counts.values())
    return sum(v for r,v in counts.items() if n-k<k or h-r<q)/den

def main():
    rows=[metrics(16,4,k,p) for k in (4,6,8) for p in ('uniform','weighted','filtered','filtered_weighted')]
    # Independent combinatorial check of uniform Byzantine tail probability.
    for r in rows:
        if r['policy']=='uniform':
            k=r['k']; analytic=sum(comb(4,b)*comb(12,k-b) for b in range((k-1)//3+1,min(4,k)+1) if 0<=k-b<=12)/comb(16,k)
            assert abs(analytic-r['risk'])<1e-12
        if r['policy']=='filtered':
            assert abs(formation_probability(16,4,r['k'])-r['next_infeasible'])<1e-12
    # Exhaustively verify the concrete admissible transition counterexample.
    previous=set(range(4)); remaining=[i for i in range(16) if i not in previous]
    valid_next=[c for c in combinations(remaining,4) if sum(120 if i<4 else 100 for i in c)>=4*105]
    assert not valid_next
    # Necessary coordinate tests are not jointly sufficient.
    a=np.array([10,10,0,0]); b=np.array([0,0,10,10])
    assert max(a)>=a.mean() and max(b)>=b.mean()
    assert not any(a[i]>=a.mean() and b[i]>=b.mean() for i in range(4))
    riskrows=[metrics(16,4,4,p,bh) for bh in range(5) for p in ('uniform','weighted','filtered','filtered_weighted')]
    for name,data in [('selection_metrics',rows),('adversary_placement',riskrows)]:
        with (OUT/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
    summary={'scope':'Exact frozen-state enumeration; not FPoR implementation or network simulation',
             'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__,
             'checks':'probability normalization; inclusion sum; hypergeometric tail; transition formula; counterexamples',
             'counterexample_valid_next':len(valid_next),'main':rows,'placement':riskrows}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    labels={'uniform':'Uniform','weighted':'Product-weighted','filtered':'Uniform + filter','filtered_weighted':'Product-weighted + filter'}
    colors=['#4c78a8','#f58518','#54a24b','#b279a2']
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(6.9,2.8))
    for p,c in zip(labels,colors):
        rr=[r for r in riskrows if r['policy']==p]
        ax.plot([r['malicious_high'] for r in rr],[r['risk'] for r in rr],'o-',label=labels[p],color=c)
    ax.set(xlabel='Malicious nodes among the four high-reputation nodes',ylabel='Probability of exceeding BFT bound',xticks=range(5),ylim=(0,0.5))
    ax.legend(fontsize=8,ncol=2);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(FIG/'risk_placement.pdf');fig.savefig(FIG/'risk_placement.png',dpi=180);plt.close(fig)
    hs=list(range(1,13));ks=list(range(4,9)); grid=np.array([[formation_probability(16,h,k) for h in hs] for k in ks])
    np.savetxt(OUT/'formation_grid.csv',grid,delimiter=',',header='columns h=1..12; rows k=4..8',comments='# ')
    fig,ax=plt.subplots(figsize=(6.9,2.7));im=ax.imshow(grid,origin='lower',aspect='auto',vmin=0,vmax=1,cmap='YlOrRd')
    ax.set(xticks=range(12),xticklabels=hs,yticks=range(5),yticklabels=ks,xlabel='Number of high-reputation nodes h (n = 16)',ylabel='Committee size k')
    for i in range(5):
        for j in range(12): ax.text(j,i,f'{grid[i,j]:.2f}',ha='center',va='center',fontsize=7,color='white' if grid[i,j]>.65 else 'black')
    fig.colorbar(im,ax=ax,label='Next-round infeasibility probability');fig.tight_layout();fig.savefig(FIG/'formation.pdf');fig.savefig(FIG/'formation.png',dpi=180);plt.close(fig)
    table=['\\begin{tabular}{llrrrr}','\\toprule','$k$ & Policy & $J$ & $P_B$ & $P_{\\emptyset}$ & $A$ \\\\','\\midrule']
    for r in rows:
        table.append(f"{r['k']} & "+{'uniform':'U','weighted':'W','filtered':'U+F','filtered_weighted':'W+F'}[r['policy']]+f" & {r['jain']:.3f} & {r['risk']:.3f} & {r['next_infeasible']:.3f} & {r['filter_acceptance']:.3f} \\\\")
    table+=['\\bottomrule','\\end{tabular}'];(OUT/'metrics_table.tex').write_text('\n'.join(table),encoding='utf-8')
    print(json.dumps(rows,indent=2)); print('All exact checks passed.')
if __name__=='__main__': main()
