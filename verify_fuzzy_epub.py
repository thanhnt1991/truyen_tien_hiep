from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from difflib import SequenceMatcher
import html, re, unicodedata

REPORT = Path('importer/truyen_zalo_epub_duplicate_report_2026-09-27.md')
SRC = Path('/home/thanh/Downloads/reup_epub/truyen_zalo')
OUT = Path('importer/truyen_zalo_fuzzy_verification_2026-09-27.md')

def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace('đ','d')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\b(ban sao|full|dich|ban dich|updated|kosuga|translate|ebookshop vn|ebook|vn)\b', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def text_of(raw):
    s = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', raw, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def meta(path):
    try:
        with ZipFile(path) as z:
            names = z.namelist()
            root = ET.fromstring(z.read('META-INF/container.xml'))
            opf = root.find('.//{*}rootfile').attrib['full-path']
            tree = ET.fromstring(z.read(opf))
            title = next((x.text for x in tree.findall('.//{*}title') if x.text), '')
            author = next((x.text for x in tree.findall('.//{*}creator') if x.text), '')
            manifest = {x.attrib.get('id'): x.attrib.get('href','') for x in tree.findall('.//{*}manifest/{*}item')}
            spine = [x.attrib.get('idref') for x in tree.findall('.//{*}spine/{*}itemref')]
            base = Path(opf).parent
            docs = []
            for sid in spine:
                href = manifest.get(sid)
                if not href: continue
                p = str((base / href).as_posix())
                if p in names:
                    docs.append(text_of(z.read(p).decode('utf-8','ignore')))
            docs = [d for d in docs if len(d) > 40]
            first = docs[0] if docs else ''
            last = docs[-1] if docs else ''
            return {'title': title or path.stem, 'author': author, 'chapters': len(docs),
                    'first': first[:6000], 'last': last[-6000:]}
    except Exception as e:
        return {'title': path.stem, 'author':'', 'chapters':0, 'first':'', 'last':'', 'error':str(e)}

def sim(a,b): return SequenceMatcher(None, norm(a), norm(b)).ratio()
def content_sim(a,b): return (SequenceMatcher(None, a, b).ratio() if a and b else 0)

pairs=[]; in_sec=False
for line in REPORT.read_text(encoding='utf8').splitlines():
    if line.startswith('## Cặp tên gần giống'): in_sec=True; continue
    if in_sec and line.startswith('## '): break
    if not in_sec or not line.startswith('| '): continue
    cells=line.split('|')
    if len(cells)<5: continue
    names=[]
    for cell in cells[2:4]:
        m=re.search(r'`([^`]+)`', cell)
        if m: names.append(m.group(1))
    if len(names)==2: pairs.append((cells[1].strip(), names[0], names[1]))

cache={}
def get(name):
    if name not in cache: cache[name]=meta(SRC/name) if (SRC/name).is_file() else {'title':name,'author':'','chapters':0,'first':'','last':'','missing':True}
    return cache[name]

rows=[]
for score,a,b in pairs:
    x,y=get(a),get(b)
    title_score=sim(x['title'],y['title'])
    author_score=sim(x.get('author',''),y.get('author','')) if x.get('author') and y.get('author') else 0
    first_score=content_sim(x.get('first',''),y.get('first',''))
    last_score=content_sim(x.get('last',''),y.get('last',''))
    ratio=(min(x['chapters'],y['chapters'])/max(x['chapters'],y['chapters'])) if x['chapters'] and y['chapters'] else 0
    if first_score >= .90 or last_score >= .90:
        verdict='XÁC NHẬN TRÙNG'
    elif title_score >= .94 and (author_score >= .80 or ratio >= .85):
        verdict='RẤT CÓ KHẢ NĂNG TRÙNG'
    elif title_score >= .94 and author_score >= .65:
        verdict='NÊN XÁC NHẬN THÊM'
    else:
        verdict='KHÔNG ĐỦ CĂN CỨ / CÓ THỂ KHÁC'
    rows.append((verdict,float(score),a,b,x,y,title_score,author_score,first_score,last_score,ratio))

order={'XÁC NHẬN TRÙNG':0,'RẤT CÓ KHẢ NĂNG TRÙNG':1,'NÊN XÁC NHẬN THÊM':2,'KHÔNG ĐỦ CĂN CỨ / CÓ THỂ KHÁC':3}
rows.sort(key=lambda r:(order[r[0]],-r[1]))
counts={k:sum(r[0]==k for r in rows) for k in order}
out=['# Kiểm tra lại 263 cặp EPUB gần giống','',f'- Tổng cặp trong báo cáo: {len(rows)}',*['- '+k+': '+str(v) for k,v in counts.items()],'','Chỉ các nhóm đầu tiên đủ điều kiện để cân nhắc xóa; chưa xóa file nào.','','| Kết luận | Điểm cũ | File 1 | File 2 | Tên | Tác giả | Chương | First | Last |','|---|---:|---|---|---:|---:|---:|---:|---:|']
for v,s,a,b,x,y,ts,au,fs,ls,ra in rows:
    out.append(f'| {v} | {s:.3f} | `{a}` | `{b}` | {ts:.2f} | {au:.2f} | {x["chapters"]}/{y["chapters"]} | {fs:.2f} | {ls:.2f} |')
OUT.write_text('\n'.join(out)+'\n',encoding='utf8')
print('pairs',len(rows),counts)
print('report',OUT)
