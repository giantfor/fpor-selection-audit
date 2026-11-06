"""Replay saved stochastic paths and verify failure labels independently."""
from pathlib import Path
import json,csv
import numpy as np
from extended_analysis import solve
root=Path(__file__).resolve().parents[1];out=root/'results'
runs=json.loads((out/'probabilistic_traces.json').read_text());checked=0;failures=0
for run in runs:
    n=run['n'];k=int(np.log2(n));L=np.full(n,100.);R=L.copy();previous=[];proposer=[]
    if run['initial']=='three_level': L[:n//4]=120;L[n//4:n//2]=110;R=L.copy()
    for t,event in enumerate(run['events'],1):
        C=event['committee'];excluded=previous if run['policy']=='full' else proposer
        assert len(set(C))==k and not set(C)&set(excluded)
        assert L[C].sum()>=k*L.mean()-1e-8 and R[C].sum()>=k*R.mean()-1e-8
        assert event['proposer'] in C
        R[C]+=2**(3 if t<=5 else 2);L[C]+=R[C]
        previous=C;proposer=[event['proposer']];checked+=1
    assert len(run['events'])==run['completed']
    if run['status']=='horizon': assert run['completed']==20
    elif run['status']=='infeasible':
        excluded=previous if run['policy']=='full' else proposer
        eligible=np.setdiff1d(np.arange(n),excluded)
        scalar=len(eligible)<k or any(np.sort(v[eligible])[-k:].sum()<k*v.mean()-1e-8 for v in (L,R))
        assert scalar or solve(L,R,k,excluded)[1]=='infeasible'
        failures+=1
    else: assert run['status']=='sampling_censored'
rows=list(csv.DictReader((out/'probabilistic_trajectories.csv').open()))
for row in rows:
    r=[x for x in runs if x['n']==int(row['n']) and x['initial']==row['initial'] and x['policy']==row['policy']]
    assert len(r)==int(row['runs']) and sum(x['status']=='infeasible' for x in r)==int(row['failed'])
report=dict(replayed_trajectories=len(runs),checked_transitions=checked,checked_failures=failures,result='passed')
(out/'probabilistic_replay_verification.json').write_text(json.dumps(report,indent=2));print(report)
