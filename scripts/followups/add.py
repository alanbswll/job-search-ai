import sys, json, re, os, subprocess, datetime
# usage: add.py <list.md> N [N...]  -> adds applied jobs to the Follow-up Board and rebuilds it
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from common import FOLLOWUPS

os.makedirs(FOLLOWUPS, exist_ok=True)
M = os.path.join(FOLLOWUPS, 'followups.json')
src = sys.argv[1]; N = {x for x in sys.argv[2:]}
date = re.search(r'(\d{8})', os.path.basename(src)).group(1); short = f'{int(date[4:6])}/{date[6:]}'
cf = os.path.join(os.path.dirname(src), f'{date}_contacts.json')
con = json.load(open(cf, encoding='utf-8')) if os.path.exists(cf) else {}
rows = json.load(open(M, encoding='utf-8')) if os.path.exists(M) else []
have = {r['id'] for r in rows}
for line in open(src, encoding='utf-8'):
    if not re.match(r'^\| \d+ \|', line): continue
    x = [s.strip() for s in line.strip().strip('|').split(' | ')]
    if x[0] not in N or f'{short} #{x[0]}' in have: continue
    c = con.get(x[0], {})
    m = re.search(r'Applied (\d{4}-\d{2}-\d{2})', x[10] if len(x) > 10 else '')
    rows.append(dict(id=f'{short} #{x[0]}', list_date=date, n=x[0], source=x[1], company=x[2], title=x[3], location=x[4],
        applied=m.group(1) if m else f'{date[:4]}-{date[4:6]}-{date[6:]}', email_status='not checked', email_date='', email_subject='', email_url='',
        contact_name=c.get('name', ''), contact_title=c.get('title', ''), contact_email=c.get('email', ''), contact_link=c.get('url', ''),
        found_via=c.get('source', ''), contact_level=c.get('level', 'none'),
        job_url=(re.search(r'\((https?://[^)]+)\)', x[9]) or [None, ''])[1]))
    print('added', rows[-1]['id'], x[2])
json.dump(rows, open(M, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
subprocess.run([sys.executable, os.path.join(HERE, 'board_gen.py'), M, datetime.date.today().isoformat()])
