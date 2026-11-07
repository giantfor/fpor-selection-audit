"""Conditional-uniform sampling, trajectory uncertainty, and score sensitivity.
No solver-selected committee is substituted for a random sample.
"""
from pathlib import Path
from math import ceil,log2,sqrt,comb
import csv,json
import numpy as np
from scipy.stats import t as student_t
from extended_analysis import solve,writecsv

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
CONFIG={'trajectory_replicates':200,'horizon':20,'proposal_cap':4096,
        'sensitivity_populations':40,'sensitivity_samples':500,
        'n':[16,32,64,128,256],'master_seed':20261106}
COUNTERS={'exact_group_fallbacks':0}

def grouped_fallback(L,R,k,eligible,rng):
    pairs,inverse=np.unique(np.column_stack([L[eligible],R[eligible]]),axis=0,return_inverse=True)
    g=len(pairs)
    if comb(k+g-1,g-1)>100000: return None,'not_attempted'
    groups=[eligible[inverse==i] for i in range(g)];sizes=[len(v) for v in groups]
    candidates=[];masses=[]
    def visit(index,left,counts,mass):
        if index==g:
            if left: return
            if np.all(np.array(counts)@pairs>=k*np.array([L.mean(),R.mean()])-1e-8):
                candidates.append(counts);masses.append(mass)
            return
        for take in range(max(0,left-sum(sizes[index+1:])),min(left,sizes[index])+1):
            visit(index+1,left-take,counts+[take],mass*comb(sizes[index],take))
    visit(0,k,[],1)
    if not masses: return None,'infeasible'
    probs=np.array(masses,dtype=float);probs/=probs.sum()
    counts=candidates[int(rng.choice(len(candidates),p=probs))]
    C=np.concatenate([rng.choice(ids,c,replace=False) for ids,c in zip(groups,counts)]).astype(int)
    COUNTERS['exact_group_fallbacks']+=1
    return C,'ok'

def wilson(x,n,z=1.959963984540054):
    p=x/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den
    half=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,mid-half),min(1,mid+half)

def sample_batch(L,R,k,eligible,rng,batch):
    # iid continuous priorities -> uniform k-subsets of eligible identities.
    if len(eligible)<k: return np.empty((0,k),dtype=int),np.empty(0,dtype=bool)
    keys=rng.random((batch,len(eligible)))
    C=eligible[np.argpartition(keys,k-1,axis=1)[:,:k]]
    valid=(L[C].sum(axis=1)>=k*L.mean()-1e-8)&(R[C].sum(axis=1)>=k*R.mean()-1e-8)
    return C,valid

def sample_one(L,R,k,excluded,rng):
    eligible=np.setdiff1d(np.arange(len(L)),excluded)
    # Exact scalar necessary conditions provide a simple infeasibility certificate.
    if len(eligible)<k: return None,'infeasible',0
    if any(np.sort(v[eligible])[-k:].sum()<k*v.mean()-1e-8 for v in (L,R)):
        return None,'infeasible',0
    proposed=0
    while proposed<CONFIG['proposal_cap']:
        batch=min(16,CONFIG['proposal_cap']-proposed)
        C,valid=sample_batch(L,R,k,eligible,rng,batch)
        if valid.any():
            j=int(np.flatnonzero(valid)[0]); return C[j],'ok',proposed+j+1
        proposed+=batch
    # Exact grouped fallback preserves the same conditional-uniform law.
    C,status=grouped_fallback(L,R,k,eligible,rng)
    if status in ('ok','infeasible'): return C,status,proposed
    # A failed sampling budget is not proof that the feasible family is empty.
    _,status=solve(L,R,k,excluded)
    return None,'infeasible' if status=='infeasible' else 'sampling_censored',proposed

def trajectory(n,initial,policy,replicate):
    code=0 if initial=='equal' else 1; mode=0 if policy=='full' else 1
    seed=[CONFIG['master_seed'],n,code,mode,replicate]
    rng=np.random.default_rng(np.random.SeedSequence(seed));k=int(log2(n))
    L=np.full(n,100.);R=L.copy()
    if initial=='three_level': L[:n//4]=120;L[n//4:n//2]=110;R=L.copy()
    previous=[];proposer=[];events=[]
    status='horizon';proposals=0
    for round_ in range(1,CONFIG['horizon']+1):
        excluded=previous if policy=='full' else proposer
        C,state,num=sample_one(L,R,k,excluded,rng);proposals+=num
        if state!='ok': status=state;break
        assert not set(C)&set(excluded)
        assert L[C].sum()>=k*L.mean()-1e-8 and R[C].sum()>=k*R.mean()-1e-8
        leader=int(rng.choice(C));events.append({'committee':sorted(C.tolist()),'proposer':leader})
        R[C]+=2**(3 if round_<=5 else 2);L[C]+=R[C]
        previous=C;proposer=[leader]
    return dict(n=n,initial=initial,policy=policy,replicate=replicate,seed=seed,
                completed=len(events),status=status,proposals=proposals,events=events)

def score_population(n,k,distribution,replicate):
    idx={'continuous':0,'lognormal':1,'evolved':2}[distribution]
    rng=np.random.default_rng(np.random.SeedSequence([73219,n,k,idx,replicate]))
    if distribution=='continuous': L=rng.uniform(50,150,n);R=rng.uniform(50,150,n)
    elif distribution=='lognormal':
        L=rng.lognormal(0,1,n);R=rng.lognormal(0,1,n);L*=100/L.mean();R*=100/R.mean()
    else:
        L=np.full(n,100.);R=L.copy();bad=set(rng.choice(n,n//4,replace=False))
        for t in range(200):
            C=rng.choice(n,k,replace=False)
            for i in C:
                if i in bad and t>=50 and rng.random()<.25 and rng.random()<.8:
                    L[i]/=2;R[i]=0
                else:
                    R[i]+=2**(3 if t<5 else 2);L[i]+=R[i]
    return L,R,rng

def sensitivity(n,k,distribution,replicate):
    L,R,rng=score_population(n,k,distribution,replicate)
    samples=[];proposed=0;valid_count=0
    # Fixed batch stream stopped when enough acceptances; first 500 retained.
    while len(samples)<CONFIG['sensitivity_samples'] and proposed<65536:
        C,valid=sample_batch(L,R,k,np.arange(n),rng,256)
        proposed+=len(C);valid_count+=int(valid.sum());samples.extend(C[valid].tolist())
    if len(samples)<CONFIG['sensitivity_samples']:
        _,s=solve(L,R,k,[])
        return [],dict(n=n,k=k,distribution=distribution,replicate=replicate,
                        status='infeasible' if s=='infeasible' else 'sampling_censored')
    C=np.array(samples[:CONFIG['sensitivity_samples']]);m=len(C)
    # Independent fixed proposal batch for acceptance: no optional-stop bias.
    _,valid=sample_batch(L,R,k,np.arange(n),rng,2048)
    inc=np.bincount(C.ravel(),minlength=n)/m;w=.6*L+.4*R
    rows=[]
    for frac in (.10,.25,.40):
        b=int(np.floor(n*frac))
        for placement in ('high','random'):
            bad=np.argsort(-w)[:b] if placement=='high' else rng.choice(n,b,replace=False)
            count=np.isin(C,bad).sum(axis=1);x=int((count>(k-1)//3).sum())
            lo,hi=wilson(x,m)
            rows.append(dict(n=n,k=k,distribution=distribution,replicate=replicate,
                fraction_requested=frac,malicious_nodes=b,placement=placement,
                samples=m,risky=x,risk=x/m,wilson_low=lo,wilson_high=hi,
                acceptance=float(valid.mean()),jain_plugin=k*k/(n*np.sum(inc**2)),
                proportional_tv_plugin=float(.5*np.sum(abs(inc/k-w/w.sum())))))
    state=dict(n=n,k=k,distribution=distribution,replicate=replicate,status='ok',L=L.tolist(),R=R.tolist())
    return rows,state

def oracle_check():
    from itertools import combinations
    n=8;k=3;L=np.array([100,120,130,90,80,110,140,70.]);R=L[::-1].copy()
    rng=np.random.default_rng(1872)
    C,_=sample_batch(L,R,k,np.arange(n),rng,56000)
    ids={tuple(c):0 for c in combinations(range(n),k)}
    for c in C: ids[tuple(sorted(c))]+=1
    # Distributional smoke check: 56 cells each expectation 1000, 7-sigma bound.
    assert all(abs(v-1000)<7*sqrt(1000*(1-1/56)) for v in ids.values())
    assert abs(wilson(0,200)[1]-.018845326377266575)<1e-10
    assert wilson(200,200)[1]==1
    L=np.array([100.]*4+[120.]*4);R=L.copy();eligible=np.arange(8)
    counts=np.zeros(8)
    for _ in range(5000):
        c,status=grouped_fallback(L,R,3,eligible,rng);assert status=='ok';counts[c]+=1
    valid=[c for c in combinations(range(8),3) if L[list(c)].sum()>=3*L.mean()]
    exact=np.zeros(8)
    for c in valid: exact[list(c)]+=1/len(valid)
    assert np.max(abs(counts/5000-exact))<.04
    COUNTERS['exact_group_fallbacks']=0

def main():
    oracle_check();traces=[];rows=[]
    for n in CONFIG['n']:
        for initial in ('equal','three_level'):
            for policy in ('full','proposer'):
                runs=[trajectory(n,initial,policy,r) for r in range(CONFIG['trajectory_replicates'])]
                traces.extend(runs);N=len(runs)
                failed=sum(r['status']=='infeasible' for r in runs)
                censored=sum(r['status']=='sampling_censored' for r in runs)
                lo,_=wilson(failed,N);_,hi=wilson(failed+censored,N)
                rows.append(dict(n=n,initial=initial,policy=policy,runs=N,failed=failed,
                    sampling_censored=censored,failure_frequency=failed/N,
                    wilson_or_envelope_low=lo,wilson_or_envelope_high=hi))
        print('Monte Carlo complete n=',n,flush=True)
    writecsv('probabilistic_trajectories.csv',rows)
    (OUT/'probabilistic_traces.json').write_text(json.dumps(traces))
    sens=[];states=[]
    for n in (64,128,256):
        for k in (int(log2(n)),n//8,n//4):
            for dist in ('continuous','lognormal','evolved'):
                for rep in range(CONFIG['sensitivity_populations']):
                    rr,state=sensitivity(n,k,dist,rep);sens.extend(rr);states.append(state)
        print('Sensitivity complete n=',n,flush=True)
    writecsv('sensitivity_samples.csv',sens)
    (OUT/'sensitivity_populations.json').write_text(json.dumps(states))
    agg=[]
    for n in (64,128,256):
        for k in (int(log2(n)),n//8,n//4):
            for dist in ('continuous','lognormal','evolved'):
                for frac in (.10,.25,.40):
                    for placement in ('high','random'):
                        rr=[r for r in sens if (r['n'],r['k'],r['distribution'],r['fraction_requested'],r['placement'])==(n,k,dist,frac,placement)]
                        x=np.array([r['risk'] for r in rr]);m=len(x)
                        if not m: continue
                        half=student_t.ppf(.975,m-1)*x.std(ddof=1)/sqrt(m) if m>1 else float('nan')
                        agg.append(dict(n=n,k=k,distribution=dist,fraction_requested=frac,placement=placement,
                            populations=m,mean_risk=float(x.mean()),population_t_low=max(0,float(x.mean()-half)),population_t_high=min(1,float(x.mean()+half))))
    writecsv('sensitivity_summary.csv',agg)
    table=['\\begin{tabular}{rlrrl}','\\toprule','$n$ & Policy & Fail/N & Cens. & 95\\% interval \\\\','\\midrule']
    for r in rows:
        if r['initial']=='three_level':
            label='Full' if r['policy']=='full' else 'Proposer'
            table.append(f"{r['n']} & {label} & {r['failed']}/{r['runs']} & {r['sampling_censored']} & [{r['wilson_or_envelope_low']:.3f},{r['wilson_or_envelope_high']:.3f}] \\\\")
    table+=['\\bottomrule','\\end{tabular}'];(OUT/'probabilistic_table.tex').write_text('\n'.join(table))
    report=dict(config=CONFIG,trajectories=len(traces),sensitivity_populations=len(states),
        sensitivity_rows=len(sens),sensitivity_unresolved=sum(s['status']!='ok' for s in states),
        trajectory_sampling_censored=sum(r['sampling_censored'] for r in rows),
        checks='sampler oracle and transition inequalities passed',counters=COUNTERS,
        scope='Conditional uniform audit sampler; not calibrated to FPoR implementation')
    (OUT/'probabilistic_verification.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':main()
