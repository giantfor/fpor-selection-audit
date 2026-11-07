"""Separate estimator implementation using Python's standard library.

Reconstruct from integer counts with rational arithmetic; obtain the Student
quantile by integration and bisection, not SciPy. This same-assistant cross-check
is NOT an independent-person review or independent regeneration of committees.
"""
from pathlib import Path
from fractions import Fraction
import csv, json, math, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
def critical_t(steps):
    df=39
    norm=math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    def cdf(x):
        h=x/steps
        def f(i):return norm*(1+(i*h)**2/df)**(-(df+1)/2)
        return .5+h/3*(f(0)+f(steps)+4*sum(f(i) for i in range(1,steps,2))+2*sum(f(i) for i in range(2,steps,2)))
    lo,hi=0.,5.
    for _ in range(48):
        mid=(lo+hi)/2
        if cdf(mid)<.975:lo=mid
        else:hi=mid
    return (lo+hi)/2
def main():
    critical=critical_t(2048);refined=critical_t(4096)
    assert abs(critical-refined)<1e-10
    pairs={}
    data=list(csv.DictReader((OUT/'sensitivity_samples.csv').open()))
    for row in data:
        key=tuple(row[k] for k in ['n','k','distribution','fraction_requested','replicate'])
        group=pairs.setdefault(key,{})
        assert row['placement'] not in group
        x,m=int(row['risky']),int(row['samples'])
        assert 0<=x<=m and m==500
        assert abs(float(Fraction(x,m))-float(row['risk']))<1e-14
        group[row['placement']]=Fraction(x,m)
    grouped={}
    for key,pair in pairs.items():
        assert set(pair)=={'high','random'}
        grouped.setdefault(key[:-1],{})[int(key[-1])]=pair['high']-pair['random']
    reported={tuple(row[k] for k in ['n','k','distribution','fraction_requested']):row
              for row in csv.DictReader((OUT/'paired_effects.csv').open())}
    assert set(reported)==set(grouped)
    audit=[];max_error=0.
    table=(OUT/'paired_effects_table.tex').read_text()
    for key,reps in sorted(grouped.items()):
        assert set(reps)==set(range(40))
        ds=list(reps.values());mean=sum(ds,Fraction(0))/40
        variance=sum(((d-mean)**2 for d in ds),Fraction(0))/39
        sd=math.sqrt(float(variance));se=sd/math.sqrt(40)
        expected={'mean_difference':float(mean),'sd_difference':sd,'se_difference':se,
                  'ci_low':float(mean)-critical*se,'ci_high':float(mean)+critical*se}
        errors={name:abs(value-float(reported[key][name])) for name,value in expected.items()}
        assert max(errors.values())<1e-10,(key,errors)
        max_error=max(max_error,max(errors.values()))
        row=dict(zip(['n','k','distribution','fraction_requested'],key),**expected,
                 exact_mean=str(mean),ci_includes_zero=expected['ci_low']<=0<=expected['ci_high'])
        if key[:2]==('128','16'):
            expected_line=f"{key[2].capitalize()} & {float(key[3]):.2f} & {float(mean):.5f} & [{expected['ci_low']:.5f}, {expected['ci_high']:.5f}]"
            assert expected_line in table,expected_line
        audit.append(row)
    report={'status':'passed','input_sha256':hashlib.sha256((OUT/'sensitivity_samples.csv').read_bytes()).hexdigest(),
            'population_evaluation_rows':len(data),'population_pairs':len(pairs),'configurations':len(grouped),
            'table7_rows_verified':9,'replicate_ids_per_configuration':'0..39',
            'critical_t_df39':critical,'integration_refinement_difference':abs(critical-refined),
            'maximum_numeric_difference':max_error,'comparison_tolerance':1e-10,
            'independent_implementation':True,'independent_external_reviewer':False,
            'scope':'Recomputes estimator/interval/table from saved integer counts; does not independently regenerate committees.',
            'focal_rows':[row for row in audit if row['n']=='128' and row['k']=='16']}
    (OUT/'paired_independent_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
