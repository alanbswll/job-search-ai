import re, json, sys, os
# usage: gen.py <YYYYMMDD_Job_Leads_Top100.md>  -> writes <out_dir>/job-leads.html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import cfg, OUT, read, write

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
DEST = os.path.join(OUT, 'job-leads.html')
date = re.search(r'(\d{8})', os.path.basename(SRC)).group(1)
nice = f"{date[:4]}-{date[4:6]}-{date[6:]}"
CF = os.path.join(os.path.dirname(SRC), f'{date}_contacts.json')
CON = json.load(open(CF, encoding='utf-8')) if os.path.exists(CF) else {}
rows = []
for line in open(SRC, encoding='utf-8'):
    m = re.match(r'^\| (\d+) \|', line)
    if not m:
        continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    n, src, co, title, loc, pay, posted, score, why, apply_, status = (c + [''] * 11)[:11]
    url = (re.search(r'\((https?://[^)]+)\)', apply_) or [None, ''])[1]
    docs = 'Resume' in status
    st = re.sub(r'📄 \[Resume\]\([^)]*\), \[Cover letter\]\([^)]*\)( · )?', '', status).strip()
    if 'Not a fit' in st or 'Duplicate' in st or 'Expired' in st: state = 'skip'
    elif 'applied' in st.lower(): state = 'done'
    elif 'broken' in st: state = 'warn'
    else: state = 'open'
    rows.append(dict(n=int(n), src=src, co=co, title=title, loc=loc, pay=pay, posted=posted,
                     score=score, why=why, url=url, docs=docs, status=st, state=state, contact=CON.get(n, {})))
data = json.dumps(rows, ensure_ascii=False).replace('</', '<\\/')
title = cfg.get('tracker_title') or f"{cfg.get('name', 'My')}'s Job Leads"
page = read(os.path.join(HERE, 'template.html'))
write(DEST, page.replace('__DATA__', data).replace('__DATE__', nice).replace('__TITLE__', title))
print(DEST, len(rows), sum(r['state'] == 'done' for r in rows))
