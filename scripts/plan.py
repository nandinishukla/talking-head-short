"""Map transcript words onto the final timeline and validate the layout-run plan. Run from edit/.
project.json:
  "word_fixes": {"Clod": "Claude", ...}            exact-token replacements for captions
  "runs": [[start_ms, end_ms, "split|visual|cam", "R1 hook"], ...]   tile [0, END]; use "END" for the last end
Writes work/plan.json; prints each run's words with run-relative times (use them to time graphics)."""
import json, sys
cfg = json.load(open('project.json'))
E = json.load(open('work/edl.json')); W = json.load(open('work/tx/words.json')); END = E['END']
fix = cfg.get('word_fixes', {})
words = []
for k, s in enumerate(E['segs']):
    for w in W:
        mid = (w['start'] + w['end']) / 2
        if s['on'] - 0.12 <= mid <= s['end'] + 0.05:
            st = max(w['start'] + s['delta'], s['out_on']); en = min(w['end'] + s['delta'], s['out_end'])
            words.append(dict(t=fix.get(w['text'], w['text']), s=round(st, 3), e=round(max(en, st + 0.06), 3), seg=k))
print('picture cuts (ms) usable as run boundaries:', [round(s['cut'] * 1000) for s in E['segs']], ' END', round(END * 1000))
runs = cfg.get('runs')
if not runs:
    print('No "runs" in project.json yet; plan them against the cut points above.');
    json.dump(dict(END=END, runs=[], words=words), open('work/plan.json', 'w'), indent=1); sys.exit()
runs = [[a, round(END * 1000) if b == 'END' else b, l, n] for a, b, l, n in runs]
# rules: tile [0,END], <= ~8 s, neighbours differ, all three layouts, hook = split, outro = cam
errs = []
if runs[0][0] != 0 or runs[-1][1] != round(END * 1000): errs.append('runs must tile [0, END]')
for a, b in zip(runs, runs[1:]):
    if a[1] != b[0]: errs.append(f'gap/overlap between {a[3]} and {b[3]}')
    if a[2] == b[2]: errs.append(f'{a[3]} and {b[3]} share layout {a[2]}')
for r in runs:
    if r[1] - r[0] > 8200: errs.append(f'{r[3]} is {(r[1]-r[0])/1000:.2f}s (> ~8 s)')
if {r[2] for r in runs} != {'split', 'visual', 'cam'}: errs.append('all three layouts must be used')
if runs[0][2] != 'split': errs.append('hook run must be split')
if runs[-1][2] != 'cam': errs.append('outro run must be full cam')
json.dump(dict(END=END, runs=runs, words=words), open('work/plan.json', 'w'), indent=1)
for r in runs:
    print(f"{r[3]} [{r[0]}-{r[1]} ms, {r[2]}, {(r[1]-r[0])/1000:.3f}s]:",
          ' '.join(f"{w['t']}@{w['s'] - r[0] / 1000:.2f}" for w in words if r[0] / 1000 <= w['s'] < r[1] / 1000))
print('PLAN OK' if not errs else 'PLAN PROBLEMS:\n  ' + '\n  '.join(errs))
