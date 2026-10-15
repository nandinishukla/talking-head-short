"""The cut: kept takes -> segments -> J-cut voice track. Run from edit/.
Reads project.json "lines": [[label, src_start_s, src_end_s], ...]  (rough edges around each KEPT take,
in delivery order) and optional "gap_overrides": {"<segment index>": seconds_to_add_to_120ms_gap}.
Writes work/edl.json and work/voice_raw.wav (48 kHz stereo float), prints the segment table."""
import numpy as np, json, soundfile as sf
cfg = json.load(open('project.json'))
r = np.load('work/rms10.npy')
FPS = 60
GAP, PRE, FADE = 0.12, 0.07, 0.17       # compressed pause, audio pre-roll before onset, tail fade
GAPX = {int(k): v for k, v in cfg.get('gap_overrides', {}).items()}
idx = lambda t: int(round(t * 100))

def segs_in(a, b):
    """split [a,b] at quiet runs (< -35 dB) longer than 250 ms -> (onset, true end) pairs"""
    i0, i1 = idx(a), idx(b)
    li = np.where(r[i0:i1] >= -35)[0]
    out = []; s = p = li[0]
    for k in li[1:]:
        if k - p > 25: out.append((s, p)); s = k
        p = k
    out.append((s, p)); res = []
    for s, e in out:
        s += i0; e += i0
        on = s
        while on > s - 8 and r[on - 1] >= -48: on -= 1          # soft attack, up to 80 ms back
        end = e; j = end
        while j > on and r[j] < -32: j -= 1                      # tail under -32 dB for >150 ms -> real end earlier
        if end - j > 15: end = j
        res.append((on / 100, (end + 1) / 100))
    return res

segs = [dict(line=n, on=on, end=en) for n, a, b in cfg['lines'] for on, en in segs_in(a, b)]
floor = float(np.percentile(r[idx(0.5):], 3))
for k, s in enumerate(segs):
    s['out_on'] = 0.040 if k == 0 else segs[k - 1]['out_end'] + GAP + GAPX.get(k, 0.0)
    s['delta'] = s['out_on'] - s['on']                          # out_time = src_time + delta
    s['out_end'] = s['end'] + s['delta']
    s['cut'] = 0.0 if k == 0 else round((s['out_on'] - PRE + 0.05) * FPS) / FPS   # picture cut on a frame
    s['a_start'] = 0.0 if k == 0 else s['cut'] - 0.05                            # audio leads picture by 50 ms
for k, s in enumerate(segs):
    j = idx(s['end'])
    while j < len(r) - 1 and r[j] > floor + 6 and (j / 100 - s['end']) < 0.6: j += 1
    decay = j / 100 + s['delta']
    limit = segs[k + 1]['out_on'] if k + 1 < len(segs) else 1e9          # never past the next sound
    s['fade_end'] = min(decay + FADE, limit)
    s['fade_start'] = max(s['out_end'], s['fade_end'] - FADE)
END = float(np.ceil(segs[-1]['fade_end'] * FPS) / FPS)
segs[-1]['fade_end'] = END; segs[-1]['fade_start'] = min(segs[-1]['fade_start'], END - FADE)
json.dump(dict(END=END, floor=floor, segs=segs), open('work/edl.json', 'w'), indent=1)
for k, s in enumerate(segs):
    print(f"{k:2d} {s['line'][:24]:24s} src {s['on']:6.2f}-{s['end']:6.2f}  out {s['out_on']:6.3f}-{s['out_end']:6.3f}  cut {s['cut']:6.3f}")
print('END', END)

x, sr = sf.read('work/voice_src48.wav'); m = x.mean(1) if x.ndim > 1 else x
v = np.zeros(int(round(END * sr)))
for s in segs:
    o0 = int(round(s['a_start'] * sr)); o1 = int(round(s['fade_end'] * sr))
    src0 = int(round((s['a_start'] - s['delta']) * sr))
    seg = m[src0:src0 + (o1 - o0)].copy(); g = np.ones(len(seg))
    fi = int(0.005 * sr); g[:fi] = np.linspace(0, 1, fi)
    fs = int(round((s['fade_start'] - s['a_start']) * sr)); fl = len(seg) - fs
    if fl > 0: g[fs:] = np.cos(np.linspace(0, np.pi / 2, fl)) ** 2
    v[o0:o0 + len(seg)] += seg * g
sf.write('work/voice_raw.wav', np.stack([v, v], 1), sr, subtype='FLOAT')
