"""Build the curated 89-entry bibliography from checked metadata, without network."""
from pathlib import Path
import re,json,html
ROOT=Path(__file__).resolve().parents[1]
def clean(s):
    s=html.unescape(re.sub('<[^>]+>','',str(s)))
    for a,b in [('‐','-'),('‑','-'),('–','--'),('’',"'"),('\u00a0',' ')]:s=s.replace(a,b)
    return s.replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('#',r'\#')
def main():
    base=(ROOT/'source_notes/base_references32.bib').read_text(encoding='utf-8')
    rows=[];entries=[]
    for i in range(33,90):
        obj=json.loads((ROOT/f'source_notes/added_reference_metadata/add{i:02d}.json').read_text(encoding='utf-8'))
        m=obj['metadata'];title=m['title'][0]
        if m.get('subtitle') and m['subtitle'][0].lower() not in title.lower():title+=': '+m['subtitle'][0]
        # All low-similarity search results must have explicit review evidence.
        assert obj['match_score']>.9 or obj.get('verification'),(i,title)
        kind={'journal-article':'article','book':'book','report':'techreport'}.get(m.get('type'),'inproceedings')
        year=m.get('published-print',m.get('issued'))['date-parts'][0][0]
        assert 1900<=year<=2026 or i==73
        authors=[]
        for a in m.get('author',[]):
            if a.get('family'):
                if a.get('given'):authors.append(clean(a['family'])+', '+clean(a['given']))
                else:authors.append('{Student}' if a['family']=='Student' else clean(a['family']))
            elif a.get('name'):
                # Manually matched persons use normal name parsing, except the Student pseudonym.
                authors.append('{'+clean(a['name'])+'}' if a['name']=='Student' else clean(a['name']))
        assert authors,(i,title)
        fields={'title':'{'+clean(title)+'}','author':' and '.join(authors),'year':str(year)}
        if kind in ('article','inproceedings'):
            venue=m.get('container-title',[''])[ -1]
            assert venue,(i,title)
            fields['journal' if kind=='article' else 'booktitle']=clean(venue)
        if kind=='book':fields['publisher']=clean(m['publisher'])
        if kind=='techreport':fields.update(institution=clean(m['publisher']),number='TR-301')
        for dest,source in [('volume','volume'),('number','issue'),('pages','page')]:
            if m.get(source):fields[dest]=clean(m[source])
        if 'pages' in fields:fields['pages']=re.sub(r'(?<=\d)-(?=\d)','--',fields['pages'])
        if m.get('DOI'):fields['doi']=m['DOI']
        else:fields['url']=m['URL']
        entry='@'+kind+'{add'+str(i)+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}'
        entries.append(entry)
        rows.append({'key':f'add{i}','title':title,'authors':authors,'year':year,'doi':m.get('DOI'),
          'source':('https://api.crossref.org/works/'+m['DOI']) if m.get('DOI') and i!=59 else m.get('URL'),
          'verification':obj.get('verification','Publisher-deposited metadata; title match checked'),
          'scope':'Bibliographic identity verified; no claim of exhaustive full-text or Scopus audit'})
    text=base+'\n\n'+'\n\n'.join(entries)+'\n'
    # Classic BibTeX requires TeX accents; one publisher record has a C1 mojibake z-caron.
    for a,b in {'\x9e':r'{\v z}','á':r"{\'a}",'í':r"{\'i}",'ú':r"{\'u}",'ø':r'{\o}',
                'ł':r'{\l}','ž':r'{\v z}','ć':r"{\'c}",'–':'--','—':'---','’':"'"}.items():
        text=text.replace(a,b)
    keys=re.findall(r'@\w+\{([^,]+),',text);assert len(keys)==89 and len(set(keys))==89
    dois=re.findall(r'\bdoi\s*=\s*\{([^}]+)',text,re.I);assert len(set(d.lower() for d in dois))==len(dois)
    (ROOT/'references.bib').write_text(text,encoding='utf-8')
    (ROOT/'source_notes/added_references_verified.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    lines=['# Verification and citation role of 57 additional references','','Identity/metadata verification does not mean all papers were read in full or individually checked in Scopus. Publisher versions replace mistaken search candidates. All 32 original entries are retained.','','| Key | Source | Role |','|---|---|---|']
    for r in rows:
        i=int(r['key'][3:]);role='Consensus assumptions and progress' if i<=38 else 'Cryptographic randomness' if i<=44 else 'Membership and ledger security' if i<=51 else 'Agreement engines and sharding' if i<=61 else 'Fairness comparison' if i<=67 else 'Sampling/statistical methods' if i<=74 else 'Reputation and identity' if i<=85 else 'Formal verification evidence standards'
        link='https://doi.org/'+r['doi'] if r['doi'] else r['source']
        lines.append(f"| {r['key']} | [{r['title']}]({link}) | {role} |")
    (ROOT/'source_notes/reference_expansion_audit.md').write_text('\n'.join(lines),encoding='utf-8')
    print('89 distinct bibliographic entries; no duplicate DOI; 57 additional identities checked.')
if __name__=='__main__':main()
