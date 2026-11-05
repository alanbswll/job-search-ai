import sys, os, subprocess, time, datetime
# usage: mark.py <list.md> applied|nofit|expired N [N...]
# Writes the status into the list, rebuilds the tracker, and (for applied) adds the jobs to the Follow-up Board.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from common import FOLLOWUPS, read, write

f, kind = sys.argv[1], sys.argv[2]
today = datetime.date.today().isoformat()
lab = {'applied': f'✅ Applied {today}', 'nofit': f'✖️ Not a fit (by me, {today})',
       'expired': f'⌛ Expired (posting closed, {today})'}[kind]
N = {int(x) for x in sys.argv[3:]}
L = read(f).split('\n')
for i, l in enumerate(L):
    p = l.split('|')
    if len(p) > 3 and p[1].strip().isdigit() and int(p[1]) in N and lab.split()[1] not in l:
        L[i] = (l[:-4] + f'| {lab} |') if l.endswith('|  |') else l[:-2] + f' · {lab} |'
        print(p[1].strip(), '|', p[3].strip(), '|', p[4].strip())
write(f, '\n'.join(L))
time.sleep(8)  # synced project folders can lag; read back to confirm the write stuck
txt = read(f)
print('verified', all(any(l.startswith(f'| {n} |') and lab in l for l in txt.split('\n')) for n in N))
subprocess.run([sys.executable, os.path.join(HERE, 'gen.py'), f])
if kind == 'applied':
    subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), 'followups', 'add.py'), f] + sys.argv[3:])
