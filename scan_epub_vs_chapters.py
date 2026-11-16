from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import unicodedata, re, html

SRC=Path('/home/thanh/Downloads/reup_epub/truyen_zalo')
CH=Path('/home/thanh/Documents/tool_code/code_tool_thread/web/importer/chapters')
OUT=Path('/home/thanh/Documents/tool_code/code_tool_thread/web/importer/epub_vs_chapters_duplicate_candidates_2026-09-28.md')

def norm(s):
    s=unicodedata.normalize('NFKD',s or '')
    s=''.join(c for c in s if not unicodedata.combining(c)).lower().replace('đ','d')
    s=re.sub(r'\[[^]]*\]|\([^)]*(?:dich|full|ban dich|convert)[^)]*\)', ' ', s)
    s=re.sub(r'\b(ban sao|dich|full|ban dich|converted|translated|kosuga|ebook|zalo|online)\b',' ',s)
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def info_file(p):
    d={}
    for line in p.read_text(encoding='utf8',errors='ignore').splitlines():
        if '=' in line:
            k,v=line.split('=',1); d[k.strip()]=v.strip()
    return d

books=[]
for p in CH.glob('*/book_info.txt'):
    d=info_file(p); title=d.get('title')
    if title: books.append((p.parent.name,d))
by_title={norm(d.get('title','')): (folder,d) for folder,d in books if norm(d.get('title',''))}

def epub_info(p):
    try:
        with ZipFile(p) as z:
            root=ET.fromstring(z.read('META-INF/container.xml'))
            opf=root.find('.//{*}rootfile').attrib['full-path']
            tree=ET.fromstring(z.read(opf))
            title=next((x.text for x in tree.findall('.//{*}title') if x.text),'')
            author=next((x.text for x in tree.findall('.//{*}creator') if x.text),'')
            return title or p.stem, author or ''
    except Exception:
        return p.stem,''

matches=[]
for p in sorted(SRC.glob('*.epub')):
    title,author=epub_info(p); key=norm(title)
    if key in by_title:
        folder,d=by_title[key]
        matches.append((p,title,author,folder,d.get('title',''),d.get('author','')))

out=['# EPUB trùng truyện đã convert trong chapters','',f'- EPUB đã quét: {len(list(SRC.glob("*.epub")))}',f'- Book info đã quét: {len(books)}',f'- Khớp tiêu đề chuẩn hóa: {len(matches)}','', '| EPUB | EPUB title | EPUB author | Converted folder | book_info title | book_info author |','|---|---|---|---|---|---|']
for p,t,a,f,bt,ba in matches: out.append(f'| `{p.name}` | {t} | {a} | `{f}` | {bt} | {ba} |')
OUT.write_text('\n'.join(out)+'\n',encoding='utf8')
print(f'epub={len(list(SRC.glob("*.epub")))} book_info={len(books)} matches={len(matches)} report={OUT}')
