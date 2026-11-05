"""Shared config and paths for the job-search scripts.

Config lookup order: $JOBSEARCH_CONFIG, then config.json next to this file
(the deployed job-leads/ folder), then config.json one level up (the repo root).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_config():
    env = os.environ.get('JOBSEARCH_CONFIG')
    if env:
        return env
    for d in (HERE, os.path.dirname(HERE)):
        p = os.path.join(d, 'config.json')
        if os.path.exists(p):
            return p
    raise SystemExit('config.json not found: copy config.example.json to config.json and fill it in')


CFG_PATH = _find_config()
cfg = json.load(open(CFG_PATH, encoding='utf-8'))

# leads_dir holds the dated lists, contacts files and followups/; defaults to the folder this file lives in
LEADS = os.path.abspath(os.path.expanduser(cfg.get('paths', {}).get('leads_dir') or HERE))
FOLLOWUPS = os.path.join(LEADS, 'followups')
OUT = os.path.abspath(os.path.expanduser(cfg.get('paths', {}).get('out_dir') or os.path.join(LEADS, '_out')))
WORK = os.path.join(OUT, 'merge')  # raw per-source search results (zip.json, indeed.json, ...)
for d in (OUT, WORK):
    os.makedirs(d, exist_ok=True)


def read(p):
    return open(p, encoding='utf-8').read()


def write(p, s):
    open(p, 'w', encoding='utf-8').write(s)
