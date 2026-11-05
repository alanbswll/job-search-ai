import json, glob, re, os, sys, datetime
# usage: merge.py [YYYYMMDD]
# Reads <out_dir>/merge/{zip,indeed,dice,upwork}.json (lists of jobs saved by the search step), filters, dedupes
# against every earlier list in leads_dir, ranks, and writes <leads_dir>/YYYYMMDD_Job_Leads_Top100.md.
# Each job: {source, company, title, loc, pay, posted, url, score (1-10), why, cat: "F" (fractional/contract) | "T" (full-time), easy_apply}
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import cfg, LEADS, WORK, write

DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().strftime('%Y%m%d')
OUT = os.path.join(LEADS, f'{DATE}_Job_Leads_Top100.md')
F = cfg.get('filters', {})
LOC = cfg.get('location', {})


def norm(s):
    return re.sub(r'[^a-z0-9 ]', ' ', (s or '').lower()).split()

SUFFIX = {'inc', 'llc', 'ltd', 'corp', 'corporation', 'co', 'company', 'group', 'plc', 'lp'}

def company(s):
    return ' '.join(w for w in norm(s) if w not in SUFFIX)

def key(j):
    return company(j['company']) + '|' + ' '.join(norm(j['title']))

# prior lists: a job is "seen" if company and title words all appear on one line
prior = []
for f in glob.glob(os.path.join(LEADS, '*.md')):
    if DATE in os.path.basename(f):
        continue
    for line in open(f, encoding='utf-8'):
        if line.startswith('|') or line.startswith('-') or line.startswith('*'):
            prior.append(' '.join(norm(line)))

def seen(j):
    # loose match: first company word (suffixes dropped) plus the core title words, so reposts with
    # "(Remote)" or "Inc" variations are still caught
    cw = company(j['company']).split()
    core = re.split(r'[(/]', j['title'])[0]
    tw = [w for w in norm(core) if w not in ('remote', 'the')]
    return bool(cw) and bool(tw) and any(cw[0] in l.split() and all(w in l.split() for w in tw) for l in prior)

# keep remote jobs (if allowed) and on-site/hybrid jobs in the home metro; drop on-site/hybrid elsewhere
METRO = tuple(a.lower() for a in LOC.get('metro_keywords', []))

def loc_ok(j):
    if LOC.get('allow_onsite_anywhere'):
        return True
    l = (j.get('loc') or '').lower()
    if any(a in l for a in METRO):
        return True
    if LOC.get('allow_remote', True) and 'remote' in l and not re.search(r'title says .remote. but|tagged on-site', l):
        return True
    return False

EXCL_TITLE = [w.lower() for w in F.get('exclude_title_keywords', [])]
EXCL_CO = {company(c) for c in F.get('exclude_companies', [])}

def excluded(j):
    t = j['title'].lower()
    return any(w in t for w in EXCL_TITLE) or company(j['company']) in EXCL_CO

# reposts with reworded titles that the loose match misses, as "company|title words" keys (see key())
SKIP = set(F.get('skip_keys', []))
jobs, by = [], {}
for f in ['zip.json', 'indeed.json', 'dice.json', 'upwork.json']:
    p = os.path.join(WORK, f)
    if not os.path.exists(p):
        continue
    for j in json.load(open(p, encoding='utf-8')):
        if not j.get('company') or not j.get('title') or seen(j) or excluded(j) or not loc_ok(j):
            continue
        k = key(j)
        if k in SKIP:
            continue
        if k in by:
            if j.get('score', 0) > by[k].get('score', 0):
                by[k].update({x: j[x] for x in ('score', 'why') if j.get(x)})
            if j.get('easy_apply'): by[k]['easy_apply'] = True
            if j['source'] not in by[k]['source']:
                by[k]['source'] += ' / ' + j['source']
            continue
        k2 = ' '.join(norm(j['title'])) + '|' + str(j.get('pay'))
        if j.get('pay') and k2 in by:  # same posting under a parent/brand name
            continue
        by[k] = by[k2] = j
        jobs.append(j)

def cell(s):
    return str(s or '').replace('|', '/').replace('\n', ' ').strip()

def table(rows, start):
    out = ['| # | Source | Company | Title | Location/remote | Pay | Posted | Score | Why it fits | Apply | Status |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for i, j in enumerate(rows):
        url = j.get('url') or ''
        link = f'[Apply]({url})' if url else ''
        out.append(f"| {start+i} | {cell(j['source'])} | {cell(j['company'])} | {cell(j['title'])} | {cell(j.get('loc'))} | {cell(j.get('pay'))} | {cell(j.get('posted'))} | {j.get('score','')} | {('⚡ Easy apply. ' if j.get('easy_apply') else '')+cell(j.get('why'))} | {link} |  |")
    return out

MIN = F.get('min_score', 6)
CAP = F.get('max_per_category', 50)
res = {}
for c in 'FT':
    res[c] = sorted([j for j in jobs if j['cat'] == c and j.get('score', 0) >= MIN], key=lambda j: -j['score'])[:CAP]

nice = f'{DATE[:4]}-{DATE[4:6]}-{DATE[6:]}'
md = [f'# Job leads, {nice}: top fractional/contract and full-time matches', '',
      f'Sources: ZipRecruiter, Indeed, Dice, Upwork (whichever were connected). Merged, deduped by company + title, and excluding jobs from earlier lists. Ranked by fit to the resume (score 1-10; only {MIN}+ kept).',
      '', '_These listings were found with AI-assisted search. Verify details with the employer before applying._', '',
      f'## Fractional / contract ({len(res["F"])})', ''] + table(res['F'], 1) + \
     ['', f'## Full-time ({len(res["T"])})', ''] + table(res['T'], 51) + ['']
write(OUT, '\n'.join(md))
json.dump(res, open(os.path.join(WORK, 'ranked.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(OUT, len(jobs), {c: len(res[c]) for c in res})
for c, st in (('F', 1), ('T', 51)):
    for i, j in enumerate(res[c][:6]):
        print(st+i, j['source'], '|', j['company'], '|', j['title'], '|', j.get('loc'), '|', j.get('pay'), '|', j['score'])
