"""Synthesize SFX, riser and music; normalize the voice; write the four full-length stems. Run from edit/.
SFX come from each composition's <script type="application/json" id="events"> block (run-relative times):
  pop | click | chime | whoosh (t = whip midpoint) | keys (t,t1,n) | ticks (t,t1) | thud | boom | flash | swoosh (t = peak)
Compositions are work/gfx/compositions/<run key lowercased>.html (R1 -> r1.html) plus cta.html for the last run.
project.json "sfx_profile": "creator" (default: levels and transition sounds measured from the creator's own edits,
  see references/sound-profile.md) or "house" (the original brief's quieter, cut-free palette).
  creator profile also adds a transition sound on every layout change: a swoosh peaking on the cut when the picture
  goes to a graphic or a screen, a sub boom when it comes back to the speaker (skipped where a whip whoosh already sits).
project.json "music": {"mode": "synth" | "file" | "none", "file": "path/to/track.mp3", "start": 0.0, "lufs": -24,
  "bpm": 110, "chords": [[midi...], ...]}
  synth = the original code-composed bed; file = the creator's own copyright-free track (looped if short, trimmed to END,
  5 ms declick, 800 ms fade, one flat level); none = no bed. Default level: -34 LUFS with the creator profile (their edits
  run the bed ~20 LU under the voice), -24 LUFS with the house profile."""
import json, re, glob, os
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, sosfiltfilt

SR = 48000
W = 'work'
P = json.load(open(f'{W}/plan.json'))
CFG = json.load(open('project.json')) if os.path.exists('project.json') else {}
END = P['END']; N = int(round(END * SR))
rng = np.random.default_rng(7)
meter = pyln.Meter(SR)

def db(x): return 20 * np.log10(max(x, 1e-12))
def peak(x): return np.max(np.abs(x))
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def tt(n): return np.arange(n) / SR

# ---------------- voice ----------------
v, _ = sf.read(f'{W}/voice_raw.wav'); v = v[:N] if len(v) >= N else np.pad(v, ((0, N - len(v)), (0, 0)))
gain = -14.0 - meter.integrated_loudness(v)
voice = v * 10 ** (gain / 20)
VP = peak(voice)  # reference peak for every relative level

# ---------------- SFX palette ----------------
def s_pop():
    n = int(0.16 * SR); t = tt(n)
    f = 150 * np.exp(-t / 0.05) + 70
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.035)
    tap = lp(rng.standard_normal(n), 900) * env_exp(n, 0.006) * 0.5
    x = body + tap; x[:48] *= np.linspace(0, 1, 48); return x
def s_click():
    n = int(0.09 * SR); t = tt(n)
    f = 1500 * np.exp(-t / 0.012) + 650
    blip = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.012)
    bub = np.sin(2 * np.pi * 2300 * t) * env_exp(n, 0.004) * 0.35
    x = blip + bub; x[:24] *= np.linspace(0, 1, 24); return x
def s_key():
    n = int(0.05 * SR)
    x = bp(rng.standard_normal(n), 1800, 5200) * env_exp(n, 0.004) + np.sin(2 * np.pi * 180 * tt(n)) * env_exp(n, 0.008) * 0.6
    x[:12] *= np.linspace(0, 1, 12); return x
def s_tick():
    n = int(0.025 * SR)
    x = bp(rng.standard_normal(n), 2500, 7000) * env_exp(n, 0.0025)
    x[:8] *= np.linspace(0, 1, 8); return x
def s_chime():
    n = int(1.1 * SR); out = np.zeros(n)
    for k, (f, d) in enumerate([(1046.5, 0.0), (1568.0, 0.11)]):   # C6 then G6
        o = int(d * SR); m = n - o; t = tt(m)
        tone = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * env_exp(m, 0.08)) * env_exp(m, 0.32)
        tone[:96] *= np.linspace(0, 1, 96); out[o:] += tone * (1.0 if k else 0.85)
    return out
def s_thud():
    """soft low thud: an icon or element landing (measured ~200 Hz centroid, ~0.2 s)"""
    n = int(0.22 * SR); t = tt(n); f = 110 * np.exp(-t / 0.04) + 55
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.06) + lp(rng.standard_normal(n), 400) * env_exp(n, 0.01) * 0.3
    x[:48] *= np.linspace(0, 1, 48); return x
def s_boom():
    """deep sub boom: the cut back to the speaker / a big reveal (measured ~55 Hz, ~0.3-0.8 s)"""
    n = int(0.9 * SR); t = tt(n); f = 70 * np.exp(-t / 0.12) + 38
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.28) + lp(rng.standard_normal(n), 220) * env_exp(n, 0.05) * 0.25
    x = np.tanh(1.4 * x); x[:96] *= np.linspace(0, 1, 96); return x
def s_flash():
    """bright tick: a white flash / hard visual switch (measured ~7 kHz centroid, ~0.08 s)"""
    n = int(0.08 * SR); x = bp(rng.standard_normal(n), 3500, 11000) * env_exp(n, 0.012)
    x += np.sin(2 * np.pi * 5200 * tt(n)) * env_exp(n, 0.008) * 0.3; x[:12] *= np.linspace(0, 1, 12); return x
def s_swoosh():
    """transition swoosh with body (measured ~0.6-0.9 s, centroid ~500-800 Hz); returns (signal, peak index)"""
    L = 0.8; n = int(L * SR); t = tt(n); noise = rng.standard_normal(n); out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        u = (i + blk / 2) / n; fc = 250 + 1100 * u ** 1.6
        y = bp(noise[max(0, i - 2048):i + blk], fc * 0.55, fc * 1.7)[-min(blk, n - i):]; out[i:i + len(y)] = y
    e = np.where(t < 0.62 * L, (t / (0.62 * L)) ** 2.2, np.exp(-(t - 0.62 * L) / 0.07))
    x = out * e + np.sin(2 * np.pi * np.cumsum(90 + 60 * t / L) / SR) * e * 0.35
    return x, int(np.argmax(np.abs(x)))
def s_whoosh(var):
    """low airy whoosh; loudest point at its centre (returned with centre index)"""
    L = [0.95, 1.1, 0.85, 1.0][var]; n = int(L * SR); t = tt(n); c = n // 2
    noise = rng.standard_normal(n)
    lo, hi = [(180, 700), (140, 600), (220, 900), (160, 800)][var]
    # sweep a band through blocks
    out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        u = (i + blk / 2) / n; fc = lo + (hi - lo) * np.sin(np.pi * u)
        seg = noise[max(0, i - 2048):i + blk]
        y = bp(seg, fc * 0.6, fc * 1.6)[-min(blk, n - i):]
        out[i:i + len(y)] = y
    e = np.exp(-((t - L / 2) / (L * [0.2, 0.22, 0.18, 0.21][var])) ** 2)
    x = lp(out * e, 1400); return x, c

def place(buf, x, t, level_db_rel_voice):
    x = x / peak(x) * VP * 10 ** (level_db_rel_voice / 20)
    i = int(round(t * SR))
    if i < 0: x = x[-i:]; i = 0
    m = min(len(x), len(buf) - i)
    if m > 0: buf[i:i + m] += x[:m]

# ---------------- gather events from compositions ----------------
runs = {r[3].split()[0]: r for r in P['runs']}
comp_run = {r[3].split()[0].lower(): r[3].split()[0] for r in P['runs']}
comp_run['cta'] = P['runs'][-1][3].split()[0]
events = []
for comp, rn in comp_run.items():
    f = f'{W}/gfx/compositions/{comp}.html'
    if not os.path.exists(f): continue
    html = open(f).read()
    if 'id="events"' not in html: continue
    ev = json.loads(re.search(r'<script type="application/json" id="events">(.*?)</script>', html, re.S).group(1))
    off = runs[rn][0] / 1000
    for e in ev:
        e = dict(e); e['t'] += off
        if 't1' in e: e['t1'] += off
        e['run'] = rn; events.append(e)
events.sort(key=lambda e: e['t'])

# peak levels relative to the voice peak (dB)
PROFILE = CFG.get('sfx_profile', 'creator')
LV = (dict(pop=-22, click=-21, chime=-13, whoosh=-14, keys=-24, ticks=-25, thud=-19, boom=-8, flash=-21, swoosh=-14)
      if PROFILE == 'creator' else
      dict(pop=-10, click=-10, chime=-10, whoosh=-9, keys=-16, ticks=-16, thud=-12, boom=-10, flash=-12, swoosh=-9))
if PROFILE == 'creator':   # transition sounds on layout changes, as in the creator's own edits
    whips = [e['t'] for e in events if e['type'] == 'whoosh']
    for a, b in zip(P['runs'], P['runs'][1:]):
        tc = b[0] / 1000
        if tc < P['runs'][0][1] / 1000 + 0.01 or any(abs(w - tc) < 0.35 for w in whips): continue   # riser owns the hook join
        if b[2] == 'cam' and a[2] != 'cam': events.append(dict(t=tc, type='boom', run=b[3].split()[0], auto=True))
        elif b[2] != 'cam': events.append(dict(t=tc, type='swoosh', run=b[3].split()[0], auto=True))
    events.sort(key=lambda e: e['t'])
sfx = np.zeros(N); log = []
wv = 0
for e in events:
    ty = e['type']
    if ty == 'pop': place(sfx, s_pop(), e['t'], LV['pop']); log.append((e['t'], 'pop (card lands)', e['run']))
    elif ty == 'click': place(sfx, s_click(), e['t'], LV['click']); log.append((e['t'], 'click (button press)', e['run']))
    elif ty == 'chime': place(sfx, s_chime(), e['t'], LV['chime']); log.append((e['t'], 'chime (confirmation / stat reveal)', e['run']))
    elif ty == 'thud': place(sfx, s_thud(), e['t'], LV['thud']); log.append((e['t'], 'thud (icon / element lands)', e['run']))
    elif ty == 'flash': place(sfx, s_flash(), e['t'], LV['flash']); log.append((e['t'], 'flash tick (white flash / hard switch)', e['run']))
    elif ty == 'boom': place(sfx, s_boom(), e['t'], LV['boom']); log.append((e['t'], 'sub boom (back to the speaker)' if e.get('auto') else 'sub boom', e['run']))
    elif ty == 'swoosh':
        x, c = s_swoosh(); place(sfx, x, e['t'] - c / SR, LV['swoosh'])
        log.append((e['t'], 'swoosh (layout change, peak on the cut)' if e.get('auto') else 'swoosh', e['run']))
    elif ty == 'whoosh':
        x, c = s_whoosh(wv % 4)
        c = int(np.argmax(np.convolve(np.abs(x), np.ones(480) / 480, 'same')))   # measured loudest point
        place(sfx, x, e['t'] - c / SR, LV['whoosh']); log.append((e['t'], f'whoosh v{wv % 4 + 1} (whip midpoint)', e['run'])); wv += 1
    elif ty == 'keys':
        n = e.get('n', 8); ts = np.linspace(e['t'], e['t1'], n)
        for k, t0 in enumerate(ts): place(sfx, s_key() * (0.85 + 0.15 * rng.random()), t0 + 0.004 * rng.standard_normal(), LV['keys'])
        log.append((e['t'], f'key presses x{n} until {e["t1"]:.2f}', e['run']))
    elif ty == 'ticks':
        t0 = e['t']; k = 0
        while t0 < e['t1']:
            place(sfx, s_tick(), t0, LV['ticks'] - 3 * rng.random()); t0 += 0.045 + 0.02 * rng.random(); k += 1
        log.append((e['t'], f'tick stream x{k} until {e["t1"]:.2f}', e['run']))

# ---------------- riser: ends exactly on the hook join ----------------
JOIN = P['runs'][0][1] / 1000
L = 2.6; n = int(L * SR); t = tt(n); u = t / L
f = 55 + 70 * u ** 2
tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR)
air = np.zeros(n); noise = rng.standard_normal(n); blk = 2048
for i in range(0, n, blk):
    fc = 200 + 1400 * ((i + blk / 2) / n) ** 2
    y = bp(noise[max(0, i - 4096):i + blk], fc * 0.7, fc * 1.4)[-min(blk, n - i):]; air[i:i + len(y)] = y
r = (lp(tone, 400) * 0.8 + air * 0.6) * u ** 2.2
r[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))
riser = np.zeros(N); place(riser, r, JOIN - L, -14)
log.append((JOIN - L, f'riser start (ends {JOIN:.3f} on hook join)', 'R1'))

# ---------------- music ----------------
MUS = CFG.get('music', {}); MODE = MUS.get('mode', 'synth')
def file_bed(path):
    """the creator's own track: decoded to 48 kHz stereo, looped if short, trimmed to END"""
    import subprocess
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(MUS.get('start', 0)), '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    reps = int(np.ceil(N / len(a))); return np.tile(a, (reps, 1))[:N]
BPM = MUS.get('bpm', 110); beat = 60 / BPM
def note(m): return 440 * 2 ** ((m - 69) / 12)
chords = CFG.get('music', {}).get('chords', [[50, 57, 60, 64, 65], [46, 53, 57, 60, 62], [41, 48, 52, 57, 60], [48, 55, 57, 60, 64]])  # Dm9 Bbmaj9 Fmaj7 C6
mus = np.zeros((N + SR, 2))
bar = 4 * beat
nb = int(np.ceil(END / bar)) + 1
def add(buf, x, t0, pan=0.0):
    i = int(round(t0 * SR)); m = min(len(x), len(buf) - i)
    if m <= 0: return
    buf[i:i + m, 0] += x[:m] * (1 - pan) ; buf[i:i + m, 1] += x[:m] * (1 + pan)
for b in range(nb):
    ch = chords[(b // 2) % len(chords)]; t0 = b * bar
    if b % 2 == 0:   # pad: 2 bars, detuned saws, lowpassed
        n = int(2 * bar * SR) + int(0.5 * SR); t = tt(n); pad = np.zeros(n)
        for m in ch[1:]:
            for d in (-0.07, 0.0, 0.07):
                ph = (note(m + d) * t) % 1.0; pad += (2 * ph - 1)
        pad = lp(pad, 1100, 2) * np.minimum(1, t / 0.25) * np.minimum(1, np.maximum(0, (2 * bar + 0.45 - t) / 0.45))
        add(mus, pad * 0.035, t0, 0)
    for q in range(4):  # kick on 1 and 3, soft
        tb = t0 + q * beat
        if q in (0, 2):
            n = int(0.35 * SR); t = tt(n); fk = 45 + 75 * np.exp(-t / 0.03)
            k = np.sin(2 * np.pi * np.cumsum(fk) / SR) * env_exp(n, 0.11); add(mus, k * 0.55, tb)
        if q in (1, 3):  # soft rim / snap
            n = int(0.12 * SR); s = bp(rng.standard_normal(n), 900, 3500) * env_exp(n, 0.03); add(mus, s * 0.10, tb, 0.15)
        for h in range(2):  # hats on 8ths
            n = int(0.05 * SR); hh = hp(rng.standard_normal(n), 7000) * env_exp(n, 0.012)
            add(mus, hh * (0.05 if h else 0.03), tb + h * beat / 2, -0.25)
        # sub bass: root on 1 and the "and" of 2
    for tb, dur in ((t0, 1.4 * beat), (t0 + 1.5 * beat, 0.9 * beat), (t0 + 2.5 * beat, 1.3 * beat)):
        n = int(dur * SR); t = tt(n); fr = note(ch[0] - 12)
        bs = np.tanh(1.6 * np.sin(2 * np.pi * fr * t)) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.05)
        add(mus, lp(bs, 300) * 0.22, tb)
    for s16 in (3, 7, 11, 14):  # sparse soft pluck texture (chord tones, no melody line)
        m = ch[1 + (s16 + b) % 4] + 12; n = int(0.4 * SR); t = tt(n)
        pl = (np.sin(2 * np.pi * note(m) * t) + 0.3 * np.sin(4 * np.pi * note(m) * t)) * env_exp(n, 0.09)
        add(mus, lp(pl, 2500) * 0.035, t0 + s16 * beat / 4, 0.3 if s16 % 2 else -0.3)
mus = mus[:N]
if MODE == 'file': mus = file_bed(MUS['file'])
if MODE == 'none': mus = np.zeros((N, 2))
else:
    mus[:int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))[:, None]
    fo = int(0.8 * SR); mus[-fo:] *= np.linspace(1, 0, fo)[:, None]
    MUS_LUFS = MUS.get('lufs', -34.0 if PROFILE == 'creator' else -24.0)              # creator edits: bed ~20 LU under the voice
    mus *= 10 ** ((MUS_LUFS - meter.integrated_loudness(mus)) / 20)   # one flat level, no ducking

st = lambda x: np.stack([x, x], 1) if x.ndim == 1 else x
stems = {'voice': voice, 'sfx': st(sfx), 'riser': st(riser), 'music': mus}
os.makedirs('stems', exist_ok=True)
for k, x in stems.items(): sf.write(f'stems/{k}.wav', x, SR, subtype='PCM_24')
json.dump(dict(events=log, voice_peak_dbfs=db(VP)), open(f'{W}/sfx_log.json', 'w'), indent=1)
for e in log: print(f'{e[0]:7.3f}  {e[2]:4s} {e[1]}')
print('voice peak dBFS', db(VP))
