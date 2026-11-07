"""Exact first-transition mechanism and ablations for three-level scores."""
from pathlib import Path
from math import comb,log2
from fractions import Fraction
import csv,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def experiment(n,k,spread=20,reward='full'):
    levels=[100,100+spread//2,100+spread];sizes=[n//2,n//4,n//4]
    total=sum(a*b for a,b in zip(levels,sizes));weights=[];bad=[];means=[]
    for high in range(min(sizes[2],k)+1):
        for mid in range(min(sizes[1],k-high)+1):
            low=k-high-mid
            if low>sizes[0]:continue
            counts=[low,mid,high];score=sum(a*b for a,b in zip(counts,levels))
            if n*score<k*total:continue
            cumulative=total+(score+8*k if reward=='full' else 0)
            current=total+(8*k if reward!='none' else 0)
            remaining=[a-b for a,b in zip(sizes,counts)];left=k;top=0
            for lev,size in reversed(list(zip(levels,remaining))):
                take=min(left,size);top+=lev*take;left-=take
            empty=left>0 or n*top<k*max(cumulative,current)
            mult=comb(sizes[0],low)*comb(sizes[1],mid)*comb(sizes[2],high)
            weights.append(mult);bad.append(mult*empty);means.append(cumulative/n)
    return dict(n=n,k=k,ratio=k/n,spread=spread,reward=reward,valid_first=sum(weights),
        failed_next_count=sum(bad),exact_failure_probability=float(Fraction(sum(bad),sum(weights))),
        next_mean_L_min=min(means),next_mean_L_max=max(means),max_unrewarded=levels[-1])
def main():
    rows=[experiment(n,k,s,r) for n in (16,32,64,128,256)
          for k in sorted(set([int(log2(n)),n//8,n//4])) if k>=int(log2(n))
          for s in (20,40,80) for r in ('none','current_only','full')]
    with (OUT/'mechanism_ablations.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    base=[r for r in rows if r['k']==int(log2(r['n'])) and r['spread']==20 and r['reward']=='full']
    assert [r['exact_failure_probability'] for r in base]==[1,1,0,0,0]
    # Brute-force cross-check n=16 first committees and residual top-k test.
    from itertools import combinations
    values=[100]*8+[110]*4+[120]*4;v=0;b=0
    for c in combinations(range(16),4):
        score=sum(values[i] for i in c)
        if score*16<4*sum(values):continue
        v+=1;left=sorted([values[i] for i in range(16) if i not in c],reverse=True)
        b+=sum(left[:4])*16<4*(sum(values)+score+32)
    assert (v,b)==(base[0]['valid_first'],base[0]['failed_next_count'])
    table=['\\begin{tabular}{rrrrr}','\\toprule','$n$ & $k$ & Min. $\\bar L^\\prime$ & Max. $\\bar L^\\prime$ & $P_{\\emptyset}^{(2)}$ \\\\','\\midrule']
    for r in base:table.append(f"{r['n']} & {r['k']} & {r['next_mean_L_min']:.3f} & {r['next_mean_L_max']:.3f} & {r['exact_failure_probability']:.0f} \\\\")
    table+=['\\bottomrule','\\end{tabular}'];(OUT/'mechanism_table.tex').write_text('\n'.join(table))
    report={'configurations':len(rows),'baseline':base,'checks':'exact group count versus individual enumeration passed',
            'scope':'first transition only; later-horizon frequencies are separate empirical results'}
    (OUT/'mechanism_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
