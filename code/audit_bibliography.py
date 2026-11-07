"""Select the manuscript's cited entries from the preserved 89-source catalog."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
catalog=(ROOT/'source_notes/references_catalog89.bib').read_text(encoding='utf-8')
entries={}
for match in re.finditer(r'@\w+\{([^,]+),',catalog):
    start=match.start(); pos=catalog.index('{',start); depth=0
    for end in range(pos,len(catalog)):
        if catalog[end]=='{' and (end==0 or catalog[end-1]!='\\'):depth+=1
        if catalog[end]=='}' and (end==0 or catalog[end-1]!='\\'):
            depth-=1
            if depth==0:break
    entries[match[1]]=catalog[start:end+1]
seen=set(); files=set()
def visit(path):
    if path in files:return
    files.add(path);s=path.read_text(encoding='utf-8')
    for group in re.findall(r'\\cite\w*\{([^}]+)\}',s):seen.update(k.strip() for k in group.split(','))
    for name in re.findall(r'\\input\{([^}]+)\}',s):
        p=ROOT/name
        if not p.suffix:p=p.with_suffix('.tex')
        visit(p)

if (ROOT/'paper.tex').exists():
    visit(ROOT/'paper.tex')
else:
    prior=json.loads((ROOT/'source_notes/bibliography_audit_v5.json').read_text())
    seen=set(entries)-set(prior['removed_from_manuscript'])
assert len(entries)==89 and not(seen-set(entries))
issues=[];dois=[]
for key in sorted(seen):
    e=entries[key]
    for field in ['title','author','year']:
        if not re.search(r'\b'+field+r'\s*=',e,re.I):issues.append([key,'missing '+field])
    doi=re.search(r'\bdoi\s*=\s*\{([^}]+)',e,re.I)
    if doi:dois.append(doi[1].lower())
    elif not re.search(r'\burl\s*=',e,re.I):issues.append([key,'missing DOI and URL'])
assert len(dois)==len(set(dois))
(ROOT/'references.bib').write_text('\n\n'.join(e for k,e in entries.items() if k in seen)+'\n',encoding='utf-8')
report={'catalog_entries':89,'retained':len(seen),'removed_from_manuscript':sorted(set(entries)-seen),
 'structural_metadata_issues':issues,'duplicate_dois':0,
 'scope':'Structural completeness and prior curated metadata; not a fresh full-text or indexing audit.',
 'selection_rationale':'Retain selection, reputation, fairness, explicit assumptions, numerical methods, and close comparisons; remove broad agreement-engine/randomness surveys without a direct analytical role.'}
(ROOT/'source_notes/bibliography_audit_v5.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
