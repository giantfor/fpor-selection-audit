"""Independent arithmetic checks of all saved state transitions, without MILP."""
from pathlib import Path
import json,csv
root=Path(__file__).resolve().parents[1]
traces=json.loads((root/'results/dynamic_traces.json').read_text())
checked=0
for t in traces:
    if t['status']!='ok': continue
    n=t['n']; k=t['k']; chosen=set(t['committee']); eligible=set(range(n))-set(t['excluded'])
    assert len(chosen)==k and chosen<=eligible
    reference=eligible if t['policy']=='eligible_mean' else set(range(n))
    for coord in ('L','R'):
        before=t[coord+'_before'];after=t[coord+'_after']
        # Cross-multiplied comparison; integer-valued stored scores.
        assert sum(before[i] for i in chosen)*len(reference)>=k*sum(before[i] for i in reference)-1e-6
        for i in range(n):
            expected=before[i]
            if i in chosen: expected += (2**(3 if t['round']<=5 else 2)) if coord=='R' else t['R_after'][i]
            assert after[i]==expected
    checked+=1
rows=list(csv.DictReader((root/'results/extended_static.csv').open()))
for r in rows:
    if r['rho']=='-1' and int(r['k'])%2:
        assert float(r['acceptance'])==0
        if r['policy'].endswith('+F'): assert r['status']=='empty' and not r['risk']
    if r['status']=='ok':
        assert 0<float(r['jain'])<=1+1e-12
        assert 0<=float(r['proportional_tv'])<=1
        assert 0<=float(r['risk'])<=1+1e-12
report={'checked_successful_transitions':checked,'static_rows_checked':len(rows),
        'result':'passed','scope':'Arithmetic validation; no independent proof of general MILP infeasibility.'}
(root/'results/artifact_verification.json').write_text(json.dumps(report,indent=2))
print(report)
