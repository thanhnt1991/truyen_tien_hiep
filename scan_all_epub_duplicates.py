from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
import sys
sys.path.insert(0, str(Path('/home/thanh/Documents/tool_code/code_tool_thread/web')))
from verify_fuzzy_epub import meta, norm, sim, content_sim

SRC=Path('/home/thanh/Downloads/reup_epub/truyen_zalo')
OUT=Path('importer/truyen_zalo_full_duplicate_scan_2026-09-28.md')
files=sorted(SRC.glob('*.epub'))
data=[]
for i,p in enumerate(files,1):
    m=meta(p); m['file']=p.name; m['path']=p
    data.append(m)
    if i%100==0: print(f'scanned {i}/{len(files)}', flush=True)

groups=defaultdict(list)
for m in data: groups[norm(m['title'])].append(m)
exact=[g for g in groups.values() if len(g)>1]
fuzzy=[]
for i,a in enumerate(data):
    for b in data[i+1:]:
        if norm(a['title'])==norm(b['title']): continue
        ts=SequenceMatcher(None,norm(a['title']),norm(b['title'])).ratio()
        au=SequenceMatcher(None,norm(a.get('author','')),norm(b.get('author',''))).ratio() if a.get('author') and b.get('author') else 0
        if ts>=.93 and au>=.75:
            fs=content_sim(a.get('first',''),b.get('first',''))
            ls=content_sim(a.get('last',''),b.get('last',''))
            fuzzy.append((ts,au,fs,ls,a,b))
fuzzy.sort(key=lambda x:(-x[2],-x[0]))

out=['# Full EPUB duplicate scan - 2026-09-28','',f'- EPUB scanned: {len(files)}',f'- Exact normalized-title groups: {len(exact)}',f'- Fuzzy candidates (title + author): {len(fuzzy)}','', '## Exact groups']
for g in sorted(exact,key=lambda x:norm(x[0]['title'])):
    out.append('')
    for m in g: out.append(f'- `{m["file"]}` | title={m["title"]} | author={m.get("author","")} | chapters={m["chapters"]} | bytes={m["path"].stat().st_size}')
out += ['', '## Fuzzy candidates; first/last content scores', '', '| Title score | Author score | First | Last | File 1 | File 2 |', '|---:|---:|---:|---:|---|---|']
for ts,au,fs,ls,a,b in fuzzy:
    out.append(f'| {ts:.3f} | {au:.3f} | {fs:.2f} | {ls:.2f} | `{a["file"]}` | `{b["file"]}` |')
OUT.write_text('\n'.join(out)+'\n',encoding='utf8')
print(f'groups={len(exact)} fuzzy={len(fuzzy)} report={OUT}')
