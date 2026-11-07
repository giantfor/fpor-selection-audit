"""Run in a fresh checkout with a fresh venv. Report immutable-input and numeric checks."""
from pathlib import Path
import subprocess, sys, json, hashlib, platform, time
root=Path(__file__).resolve().parents[1]
report_dir=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'reproduction_report'
report_dir.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((root/'SHA256SUMS.json').read_text())
checks={name: (root/name).is_file() and sha(root/name)==digest for name,digest in manifest.items()}
report={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
 'python':sys.version,'platform':platform.platform(),'initial_manifest_files':len(checks),
 'initial_manifest_mismatches':[k for k,v in checks.items() if not v],
 'environment_scope':'new virtual environment and public checkout, same host; not an external independent replication',
 'commands':[]}
if report['initial_manifest_mismatches']:
 (report_dir/'report.json').write_text(json.dumps(report,indent=2));raise SystemExit('Initial checksum mismatch')
before={p.name:sha(p) for p in (root/'results').iterdir() if p.suffix in ('.csv','.json')}
commands=['run_analysis.py','extended_analysis.py','verify_artifacts.py','probabilistic_analysis.py','verify_probabilistic.py','render_probabilistic_results.py','mechanism_analysis.py','paired_effects.py','verify_paired_independent.py']
for name in commands:
 if not (root/'code'/name).exists(): continue
 start=time.monotonic();p=subprocess.run([sys.executable,str(root/'code'/name)],cwd=root,capture_output=True)
 (report_dir/(name+'.log')).write_bytes(p.stdout+p.stderr)
 report['commands'].append({'script':name,'exit_code':p.returncode,'seconds':round(time.monotonic()-start,3)})
 print(name,p.returncode,flush=True)
 if p.returncode:
  (report_dir/'report.json').write_text(json.dumps(report,indent=2));raise SystemExit('Script failed')
report['numeric_sha256_matches']={name:sha(root/'results'/name)==digest for name,digest in before.items()}
report['numeric_mismatches']=[k for k,v in report['numeric_sha256_matches'].items() if not v]
report['pip_freeze']=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines()
report['passed']=not report['numeric_mismatches']
(report_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('REPRODUCTION',report['passed'],len(before),'numeric files',flush=True)
if not report['passed']:raise SystemExit(1)
