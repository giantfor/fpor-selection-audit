"""Version 2: exact grouped enumeration and explicit state-transition audit.
Not an implementation of the authors' FPoR prototype or a network benchmark.
"""
from pathlib import Path
from itertools import combinations
from math import comb, ceil, log2
import csv, json, platform
import numpy as np
import scipy
from scipy.optimize import milp, Bounds, LinearConstraint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results'; FIG = ROOT/'figures'
TYPES = np.array([[0,0],[1,0],[0,1],[1,1]])

def compositions(sizes, k):
    for a in range(min(sizes[0], k)+1):
        for b in range(min(sizes[1], k-a)+1):
            for c in range(min(sizes[2], k-a-b)+1):
                d=k-a-b-c
                if 0 <= d <= sizes[3]:
                    yield np.array([a,b,c,d])

def feasible(sizes, k, ql, qr):
    if sum(sizes)<k: return False
    for d in range(min(sizes[3], k)+1):
        b=max(0,ql-d); c=max(0,qr-d)
        if b<=sizes[1] and c<=sizes[2] and d+b+c<=k and k-d<=sum(sizes[:3]):
            return True
    return False

def hypergeom(pop,bad,draw):
    out=np.zeros(draw+1)
    for j in range(draw+1):
        if j<=bad and draw-j<=pop-bad:
            out[j]=comb(bad,j)*comb(pop-bad,draw-j)/comb(pop,draw)
    return out

def grouped(n,rho,policy):
    k=int(log2(n))
    sizes=np.array({-1:[0,n//2,n//2,0],0:[n//4]*4,1:[n//2,0,0,n//2]}[rho])
    weights=100+20*(TYPES@np.array([.6,.4]))
    q=ceil(k/2)
    # Worst-score placement with a fixed tie order: 11, 10, 01, 00.
    bad=np.zeros(4,dtype=int); remaining=n//4
    for t in np.argsort(-weights):
        bad[t]=min(remaining,sizes[t]); remaining-=bad[t]
    entries=[]; total=0.; accepted=0.
    for counts in compositions(sizes,k):
        mult=np.prod([comb(int(m),int(c)) for m,c in zip(sizes,counts)],dtype=object)
        mass=float(mult)*float(np.prod((weights/100)**counts) if policy.startswith('W') else 1)
        total+=mass
        valid=bool(np.all(counts@TYPES>=q))
        if valid: accepted+=mass
        if policy.endswith('+F') and not valid: continue
        dist=np.array([1.])
        for m,b,c in zip(sizes,bad,counts):
            dist=np.convolve(dist,hypergeom(int(m),int(b),int(c)))
        risk=float(dist[(k-1)//3+1:].sum())
        empty=not feasible(sizes-counts,k,q,q)
        entries.append((mass,counts,risk,empty))
    base=dict(n=n,k=k,rho=rho,policy=policy,acceptance=accepted/total)
    if not entries:
        return dict(**base,status='empty',jain=None,proportional_tv=None,risk=None,next_empty=None)
    z=sum(e[0] for e in entries)
    expected=sum(e[0]*e[1] for e in entries)/z
    pi=np.divide(expected,sizes,out=np.zeros(4),where=sizes>0)
    target=weights/(sizes@weights)
    tv=.5*float(np.sum(sizes*np.abs(pi/k-target)))
    assert abs(sizes@pi-k)<1e-9
    return dict(**base,status='ok',jain=k*k/(n*float(sizes@(pi*pi))),proportional_tv=tv,
                risk=sum(e[0]*e[2] for e in entries)/z,next_empty=sum(e[0]*e[3] for e in entries)/z)

def solve(L,R,k,excluded,eligible_mean=False,objective=None):
    n=len(L); eligible=np.ones(n,dtype=bool); eligible[list(excluded)]=False
    if eligible.sum()<k: return None,'infeasible'
    meanL=L[eligible].mean() if eligible_mean else L.mean()
    meanR=R[eligible].mean() if eligible_mean else R.mean()
    A=np.vstack([np.ones(n),L,R])
    result=milp(np.zeros(n) if objective is None else objective,
        integrality=np.ones(n),bounds=Bounds(np.zeros(n),eligible.astype(float)),
        constraints=LinearConstraint(A,[k,k*meanL,k*meanR],[k,np.inf,np.inf]),
        options={'time_limit':10,'mip_rel_gap':0})
    if result.status==2: return None,'infeasible'
    if result.status!=0: return None,'unresolved'
    C=np.flatnonzero(result.x>.5)
    assert len(C)==k and eligible[C].all()
    assert L[C].sum()>=k*meanL-1e-6 and R[C].sum()>=k*meanR-1e-6
    return C,'ok'

def dynamic(n,policy,seed,initial='equal',rounds=20):
    rng=np.random.default_rng(seed); k=int(log2(n))
    R=np.full(n,100.); L=R.copy()
    if initial=='three_level':
        R[:n//4]=120; R[n//4:n//2]=110; L=R.copy()
    previous=[]; proposer=[]; trace=[]
    for t in range(1,rounds+1):
        excluded=previous if policy in ('full','eligible_mean') else proposer if policy=='proposer' else []
        C,status=solve(L,R,k,excluded,policy=='eligible_mean',rng.normal(size=n))
        record=dict(n=n,k=k,policy=policy,seed=seed,initial=initial,round=t,status=status,
                    L_before=L.tolist(),R_before=R.tolist(),excluded=list(map(int,excluded)))
        if status!='ok': trace.append(record); break
        record['committee']=C.tolist(); record['proposer']=int(C[0])
        # Section 3.5.1: update current first, then cumulative; selected honest nodes only.
        gamma=3 if t<=5 else 2
        R[C]+=2**gamma
        L[C]+=R[C]
        record['L_after']=L.tolist(); record['R_after']=R.tolist()
        trace.append(record); previous=C; proposer=[int(C[0])]
    return trace

def independent_checks():
    # Exhaustive individual-subset oracle for genuinely distinct coordinates.
    for sizes in ([2,2,2,2],[0,4,4,0],[4,0,0,4]):
        types=np.repeat(TYPES,sizes,axis=0)
        for k in range(1,6):
            for excluded in ([],[0],[0,1,2]):
                eligible=[i for i in range(8) if i not in excluded]
                q=np.ceil(k*types.mean(axis=0)).astype(int)
                brute=any(np.all(types[list(c)].sum(axis=0)>=q) for c in combinations(eligible,k))
                left=np.array(sizes)-np.bincount(np.repeat(np.arange(4),sizes)[excluded],minlength=4)
                assert feasible(left,k,*q)==brute
                _,status=solve(100+20*types[:,0],100+20*types[:,1],k,excluded)
                assert (status=='ok')==brute and status!='unresolved'
    # Grouped probability agrees with direct enumeration at n=16, rho=0.
    types=np.repeat(TYPES,4,axis=0); w=100+20*(types@np.array([.6,.4])); k=4
    bad=set(np.argsort(-w,kind='stable')[:4])
    for policy in ('U','W','U+F','W+F'):
        incl=np.zeros(16); z=0.; risky=0.
        for c in combinations(range(16),k):
            if policy.endswith('+F') and np.any(types[list(c)].sum(axis=0)<2): continue
            m=float(np.prod(w[list(c)]/100)) if policy.startswith('W') else 1.
            z+=m; incl[list(c)]+=m; risky+=m*(len(set(c)&bad)>1)
        row=grouped(16,0,policy); incl/=z
        assert abs(row['risk']-risky/z)<1e-10
        assert abs(row['jain']-k*k/(16*np.sum(incl**2)))<1e-10
    # Reachable equal-start obstruction after any selected committee.
    for n in (16,32,64,128,256):
        k=int(log2(n)); L=np.full(n,100.);R=L.copy();C=np.arange(k)
        R[C]+=8;L[C]+=R[C]
        assert solve(L,R,k,C)[1]=='infeasible'
        assert solve(L,R,k,[0])[1]=='ok'

def quorum_witness():
    # Authenticated certificate abstraction, NOT a PBFT execution trace.
    a={0,1,2}; b={0,1,3}; malicious={0,1}; quorum=3
    assert len(a)>=quorum and len(b)>=quorum and a&b<=malicious
    assert 4-len(malicious)<quorum
    for x in combinations(range(4),3):
        for y in combinations(range(4),3): assert len(set(x)&set(y))>=2
    return dict(model='single-height quorum certificates, no PBFT view changes',
                k=4,quorum=3,malicious=[0,1],value_A_signers=sorted(a),value_B_signers=sorted(b),
                honest_equivocations=0,withholding_available_votes=2,
                within_bound_note='With <=1 faulty replica every pair of 3-vote certificates shares an honest signer.')

def writecsv(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)

def main():
    independent_checks()
    rows=[grouped(n,r,p) for n in (16,32,64,128,256) for r in (-1,0,1) for p in ('U','W','U+F','W+F')]
    writecsv('extended_static.csv',rows)
    traces=[]; summary=[]
    for n in (16,32,64,128,256):
        for initial in ('equal','three_level'):
            for policy in ('full','proposer','none','eligible_mean'):
                for seed in range(5):
                    tr=dynamic(n,policy,seed,initial);traces.extend(tr)
                    summary.append(dict(n=n,initial=initial,policy=policy,seed=seed,
                        completed=sum(t['status']=='ok' for t in tr),last_status=tr[-1]['status']))
        print('Completed dynamic n =',n,flush=True)
    (OUT/'dynamic_traces.json').write_text(json.dumps(traces),encoding='utf-8')
    writecsv('dynamic_summary.csv',summary)
    (OUT/'quorum_witness.json').write_text(json.dumps(quorum_witness(),indent=2),encoding='utf-8')
    assert all(r['completed']==1 for r in summary if r['initial']=='equal' and r['policy']=='full')
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(7,2.6))
    for rho in (-1,0,1):
        rr=[r for r in rows if r['policy']=='U+F' and r['rho']==rho]
        axes[0].plot([r['n'] for r in rr],[r['acceptance'] for r in rr],'o-',label=f'rho={rho}')
        axes[1].plot([r['n'] for r in rr],[np.nan if r['risk'] is None else r['risk'] for r in rr],'o-',label=f'rho={rho}')
    for ax in axes:
        ax.set_xscale('log',base=2);ax.set_xticks([16,32,64,128,256],[16,32,64,128,256]);ax.set_xlabel('Candidate population n');ax.set_ylim(-.03,1.03);ax.grid(alpha=.2)
    axes[0].set_ylabel('Filter acceptance');axes[1].set_ylabel('Byzantine-bound exceedance');axes[0].legend(fontsize=8)
    fig.tight_layout();fig.savefig(FIG/'extended_static.pdf');plt.close(fig)
    table=['\\begin{tabular}{llrrr}','\\toprule','Init. & Policy & Min. & Max. & Empty \\\\','\\midrule']
    for initial in ('equal','three_level'):
        for policy in ('full','proposer','none','eligible_mean'):
            s=[r for r in summary if r['initial']==initial and r['policy']==policy]
            label={'full':'Full','proposer':'Proposer','none':'None','eligible_mean':'Eligible mean'}[policy]
            table.append(f"{'Equal' if initial=='equal' else 'Three-level'} & {label} & {min(r['completed'] for r in s)} & {max(r['completed'] for r in s)} & {sum(r['last_status']=='infeasible' for r in s)}/25 \\\\")
    table+=['\\bottomrule','\\end{tabular}'];(OUT/'dynamic_table.tex').write_text('\n'.join(table))
    report=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
        static_configs=len(rows),dynamic_runs=len(summary),max_rounds=20,seeds=list(range(5)),
        unresolved=sum(r['last_status']=='unresolved' for r in summary),checks='all passed',
        sampler='MILP with seeded normal random objective: stress witnesses, not uniform sampling')
    (OUT/'extended_verification.json').write_text(json.dumps(report,indent=2))
    print(report)
if __name__=='__main__': main()
