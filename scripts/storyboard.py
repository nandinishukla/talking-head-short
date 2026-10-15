"""Storyboard + beat table, for the user's approval BEFORE any graphic is rendered. Run from edit/.
  python storyboard.py [oriented_camera.mp4=work/cam1080.mp4]
Reads work/plan.json, work/edl.json, work/captions.json (if captions.py already ran) and project.json:
  "beats": [{"run": "R1", "t": 0.0, "visual": "what is on screen and doing what", "camera": "glide / step / push / whip / inner push",
             "sfx": "pop", "refs": ["motion-library id or url"], "source": "real capture / rebuilt UI / logo"}, ...]
           t is run-relative seconds; a run may have several beats.
  "storyboard_notes": {"R1": "why this layout and graphic", ...}   (optional)
Writes work/storyboard.html: one self-contained page (embedded images) with a 9:16 sketch per run (layout zones,
speaker thumbnail at the run's first frame, caption style and position) and the full beat table.
Show it to the user and STOP until they approve or ask for changes."""
import json, os, sys, base64, subprocess, html, math
CAM = sys.argv[1] if len(sys.argv) > 1 else 'work/cam1080.mp4'
P = json.load(open('work/plan.json')); E = json.load(open('work/edl.json')); CFG = json.load(open('project.json'))
caps = json.load(open('work/captions.json')) if os.path.exists('work/captions.json') else []
beats = CFG.get('beats', []); notes = CFG.get('storyboard_notes', {})
W = P['words']; runs = P['runs']; os.makedirs('work/storyboard', exist_ok=True)
esc = html.escape

def src_time(t):
    """output time -> source time through the cut (for thumbnails)"""
    k = max(j for j, s in enumerate(E['segs']) if s['cut'] <= t + 1e-9); return t - E['segs'][k]['delta']
def thumb(t, name):
    p = f'work/storyboard/{name}.jpg'
    if not os.path.exists(p):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{src_time(t):.3f}', '-i', CAM, '-frames:v', '1', '-vf', 'scale=270:-2', '-q:v', '4', p])
    return 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode() if os.path.exists(p) else ''
def words_between(a, b): return ' '.join(w['t'] for w in W if a <= w['s'] < b)
def cap_at(t):
    for c in caps:
        if c['start'] <= t < c['end']: return c
    return None

def sketch(r):
    """270x480 SVG: layout zones, speaker thumbnail where the camera shows, caption marker"""
    a, b, lay, name = r; key = name.split()[0]; img = thumb(a / 1000 + 0.05, key); s = 0.25
    bs = [x for x in beats if x['run'] == key]; first = esc(bs[0]['visual'][:70]) if bs else ''
    g = ['<svg viewBox="0 0 270 480" width="270" height="480" xmlns="http://www.w3.org/2000/svg">',
         '<defs><clipPath id="c' + key + '"><rect x="-16" y="300" width="302" height="216" rx="50"/></clipPath></defs>']
    if lay == 'cam':
        g.append(f'<image href="{img}" x="0" y="0" width="270" height="480" preserveAspectRatio="xMidYMid slice"/>')
    else:
        g.append('<rect width="270" height="480" fill="#F6F6F3"/>')
        top, bot = (10, 225) if lay == 'split' else (50, 307)
        g.append(f'<rect x="12" y="{top}" width="246" height="{bot - top}" rx="12" fill="#fff" stroke="#D97757" stroke-dasharray="5 4"/>')
        g.append(f'<foreignObject x="20" y="{top + 8}" width="230" height="{bot - top - 16}"><div xmlns="http://www.w3.org/1999/xhtml" '
                 f'style="font:600 11px Helvetica;color:#B25730;line-height:1.3">{first}</div></foreignObject>')
        if lay == 'split':
            g.append(f'<image href="{img}" x="0" y="150" width="270" height="480" preserveAspectRatio="xMidYMin slice" clip-path="url(#c{key})"/>')
            g.append('<rect x="-16" y="300" width="302" height="216" rx="50" fill="none" stroke="#111" stroke-width="1.5"/>')
    for c in [c for c in caps if a / 1000 <= c['start'] < b / 1000][:1]:
        y = (c['y'] + (60 if c['style'] == 'pill' else 200)) * s
        col = '#FFE14D' if c['style'] == 'hero' else '#fff'
        g.append(f'<rect x="20" y="{y - 13}" width="230" height="26" rx="6" fill="rgba(0,0,0,.55)"/>'
                 f'<text x="135" y="{y + 5}" text-anchor="middle" font-family="Helvetica" font-weight="700" font-size="12" fill="{col}">'
                 f'{c["style"].upper()} caption</text>')
    g.append('</svg>'); return ''.join(g)

cards = []
for r in runs:
    a, b, lay, name = r; key = name.split()[0]
    cards.append(f'''<section class="run"><div class="sk">{sketch(r)}</div><div class="meta">
<h3>{esc(name)} <span class="tag {lay}">{lay}</span></h3>
<p class="t">{a/1000:.2f}–{b/1000:.2f} s · {(b-a)/1000:.2f} s</p>
<p class="vo">“{esc(words_between(a/1000, b/1000))}”</p>
<p class="why">{esc(notes.get(key, ''))}</p></div></section>''')

rows = []
order = sorted(beats, key=lambda x: (next(i for i, r in enumerate(runs) if r[3].split()[0] == x['run']), x['t']))
for i, bt in enumerate(order):
    r = next(r for r in runs if r[3].split()[0] == bt['run']); t0 = r[0] / 1000 + bt['t']
    nxt = order[i + 1] if i + 1 < len(order) else None
    t1 = (next(rr for rr in runs if rr[3].split()[0] == nxt['run'])[0] / 1000 + nxt['t']) if nxt else P['END']
    t1 = min(t1, r[1] / 1000) if nxt and nxt['run'] != bt['run'] else t1
    heroes = [c['text'] for c in caps if c['style'] == 'hero' and t0 <= c['start'] < t1]
    capcell = ('HERO: ' + ' / '.join(heroes) + ' + pill') if heroes else ('pill' if caps else '')
    rows.append(f'<tr><td>{t0:.2f}–{t1:.2f}</td><td>{esc(bt["run"])}</td><td>{r[2]}</td><td>“{esc(words_between(t0, t1))}”</td>'
                f'<td>{esc(bt.get("visual", ""))}</td><td>{esc(bt.get("camera", ""))}</td><td>{esc(bt.get("sfx", ""))}</td>'
                f'<td>{esc(capcell)}</td><td>{esc(", ".join(bt.get("refs", [])))}</td><td>{esc(bt.get("source", ""))}</td></tr>')
cuts = ', '.join(f'{s["cut"]:.3f}' for s in E['segs'][1:])
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Storyboard</title><style>
:root{{--bg:#fafaf8;--ink:#111;--mut:#6b6a65;--line:#e6e3de;--clay:#B25730}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#161616;--ink:#eee;--mut:#a5a39c;--line:#333}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,Helvetica,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px}} h1{{margin:0 0 4px}} .sub{{color:var(--mut);margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}}
.run{{border:1px solid var(--line);border-radius:14px;padding:12px;display:flex;flex-direction:column;gap:8px}}
.sk svg{{width:100%;height:auto;border-radius:10px;background:#ddd}} h3{{margin:0;font-size:16px}}
.tag{{font-size:11px;padding:2px 8px;border-radius:99px;border:1px solid var(--line);color:var(--mut);vertical-align:2px}}
.t{{margin:0;color:var(--mut);font-size:13px}} .vo{{margin:0;font-style:italic}} .why{{margin:0;color:var(--mut);font-size:13px}}
.tw{{overflow-x:auto;margin-top:28px}} table{{border-collapse:collapse;width:100%;font-size:13px;min-width:900px}}
th,td{{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}} th{{color:var(--mut);font-weight:600}}
</style></head><body><main>
<h1>Storyboard</h1><p class="sub">END {P["END"]*1000:.0f} ms · {len(runs)} runs · picture cuts at {cuts} s. Nothing has been rendered yet. Approve or ask for changes.</p>
<div class="grid">{''.join(cards)}</div>
<h2>Beat table</h2><div class="tw"><table><thead><tr><th>Time (s)</th><th>Run</th><th>Layout</th><th>Words</th><th>On screen</th><th>Camera</th>
<th>SFX</th><th>Caption</th><th>Motion refs</th><th>Source</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
</main></body></html>'''
open('work/storyboard.html', 'w').write(page)
missing = [r[3] for r in runs if r[2] != 'cam' and not any(b['run'] == r[3].split()[0] for b in beats)]
print('work/storyboard.html written;', len(rows), 'beats', ('; runs with no beats: ' + ', '.join(missing)) if missing else '')
