import json, sys, os
# usage: board_gen.py <followups.json> <YYYY-MM-DD>  -> writes <out_dir>/followup-board.html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from common import cfg, FOLLOWUPS, OUT, read, write

src = sys.argv[1]; date = sys.argv[2]
rows = json.load(open(src, encoding='utf-8')); rows.sort(key=lambda r: (r['applied'], r['list_date'], int(r['n'])))
st = os.path.join(FOLLOWUPS, 'scan_state.json')
scan = json.load(open(st, encoding='utf-8')).get('last_scan_label', 'not yet') if os.path.exists(st) else 'not yet'
iv_path = os.path.join(FOLLOWUPS, 'interviews.json')  # optional, hand-maintained list of active interviews
iv = json.load(open(iv_path, encoding='utf-8')) if os.path.exists(iv_path) else []
fu = cfg.get('followup', {})
conf = dict(name=cfg.get('name', ''), inbox=cfg.get('gmail', {}).get('inbox', 'your'),
            pitch=fu.get('pitch', ''), due_days=fu.get('due_days', 5),
            scans=cfg.get('gmail', {}).get('scans_per_day', 4), tz=cfg.get('timezone', 'America/New_York'))
j = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
page = read(os.path.join(HERE, 'board_template.html'))
dest = os.path.join(OUT, 'followup-board.html')
write(dest, page.replace('__DATA__', j(rows)).replace('__INTERVIEWS__', j(iv)).replace('__CONFIG__', j(conf))
      .replace('__DATE__', date).replace('__SCAN__', scan))
print(dest, len(rows))
