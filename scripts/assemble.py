"""Build the picture frame by frame from work/plan.json, burn captions, mux the master. Run from edit/.
  python assemble.py               -> final.mp4
  python assemble.py 0,240,1300    -> only write those frames as PNGs to work/qa/ (fast checks; stops at the max)
Inputs: work/camtrack.mp4 (+_map.json), work/camwide.mp4 for landscape sources, work/gfx/final/<run>_60.mp4 per
graphic run, work/matte/<RUN>.mov/.json per split run, work/gfx/final/cta.mov, work/cover.png, work/captions.ass,
final_master.wav. Optional project.json "split": {"scale": 0.72, "y": 538} for PORTRAIT sources."""
import json, subprocess, sys, os, numpy as np, cv2
SK = os.path.dirname(os.path.abspath(__file__)); FPS = 60
P = json.load(open('work/plan.json')); END = P['END']; N = int(round(END * FPS)); runs = P['runs']
CFG = json.load(open('project.json')) if os.path.exists('project.json') else {}
ONLY = None if len(sys.argv) < 2 else [int(x) for x in sys.argv[1].split(',')]
FM = json.load(open('work/camtrack_map.json'))
WIDE = os.path.exists('work/camwide.mp4')

def reader(path, w, h, fmt='rgb24', vf=None):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path] + (['-vf', vf] if vf else []) + ['-f', 'rawvideo', '-pix_fmt', fmt, '-'],
                         stdout=subprocess.PIPE, bufsize=10 ** 8)
    ch = {'rgb24': 3, 'gray': 1, 'rgba': 4}[fmt]
    def nxt():
        b = p.stdout.read(w * h * ch)
        if len(b) < w * h * ch: return None
        a = np.frombuffer(b, np.uint8); return a.reshape(h, w, ch) if ch > 1 else a.reshape(h, w)
    return nxt

# ---------- split geometry ----------
CX, CY, CW, CH, CR = -65, 1200, 1210, 864, 200            # camera card, squircle radius 200, bleeds L/R/bottom
if WIDE:   # 16:9 source: footage 1890x1063 at (-405, 1008), as specified
    SW, SH, SX, SY = 1890, 1063, -405, 1008; FEED = (1890, 1063)
else:      # portrait source: derived so the head clears the graphic zone (content ends y 900) and the card is covered
    sc = CFG.get('split', {}).get('scale', 0.72); SW, SH = round(1080 * sc), round(1920 * sc)
    SX = (1080 - SW) // 2; SY = CFG.get('split', {}).get('y', 1920 - SH); FEED = (1080, 1920)
yy, xx = np.mgrid[0:1920, 0:1080].astype(np.float32)
def squircle():
    R = CR * 1.25; n = 5.0; lx, rx, ty, by = CX, CX + CW, CY, CY + CH
    m = ((xx >= lx) & (xx < rx) & (yy >= ty) & (yy < by)).astype(np.float32)
    for cx_, cy_ in ((lx + R, ty + R), (rx - R, ty + R), (lx + R, by - R), (rx - R, by - R)):
        inq = ((xx < lx + R) if cx_ < 540 else (xx > rx - R)) & ((yy < ty + R) if cy_ < ty + CH / 2 else (yy > by - R))
        val = np.clip((1 - ((np.abs(xx - cx_) / R) ** n + (np.abs(yy - cy_) / R) ** n)) * R / n + 0.5, 0, 1)
        m = np.where(inq, np.minimum(m, val), m)
    return m * np.clip(yy - ty + 0.5, 0, 1)
M = squircle()[..., None]
sh = np.zeros((1920, 1080), np.float32)                     # the three-layer card shadow on the graphic
for oy, blur, a in ((60, 120, .16), (24, 48, .10), (4, 10, .06)):
    s_ = np.roll(M[..., 0], oy, axis=0); s_[:oy] = 0
    sh = 1 - (1 - sh) * (1 - a * cv2.GaussianBlur(s_, (0, 0), blur / 2))
SHA = (sh * (1 - M[..., 0]))[..., None]; SHC = np.array([24, 24, 32], np.float32)
RAMP = np.clip((CY + 40 - yy) / 40.0, 0, 1)[..., None]      # head shows above the card edge, feathered 40 px into it
INSIDE = ((xx >= SX) & (xx < SX + SW) & (yy >= SY) & (yy < SY + SH))
FX = (np.clip(np.minimum(xx - SX, SX + SW - xx) / 70.0, 0, 1) * INSIDE)[..., None]

def place(img, interp=cv2.INTER_AREA):
    """scale img to (SW,SH) and paste at (SX,SY) on a 1080x1920 canvas (clipped)"""
    s = cv2.resize(img, (SW, SH), interpolation=interp).astype(np.float32)
    out = np.zeros((1920, 1080) + s.shape[2:], np.float32)
    x0, y0 = max(0, SX), max(0, SY); x1, y1 = min(1080, SX + SW), min(1920, SY + SH)
    out[y0:y1, x0:x1] = s[y0 - SY:y1 - SY, x0 - SX:x1 - SX]; return out

def split_frame(G, F, A):
    """G graphic, F split footage frame, A matte of the SAME source frame (any size)"""
    G = G.astype(np.float32); S = place(F)
    if WIDE: card = S
    else:    # portrait: fill the card's side strips with a blurred, darkened, enlarged copy of the same frame
        big = cv2.GaussianBlur(cv2.resize(F, (round(1080 * 1.15), round(1920 * 1.15)), interpolation=cv2.INTER_AREA), (0, 0), 30).astype(np.float32) * 0.82
        B = np.zeros_like(G); oy = SY - (big.shape[0] - SH) // 2; ox = (big.shape[1] - 1080) // 2
        y0, y1 = max(0, oy), min(1920, oy + big.shape[0]); B[y0:y1] = big[y0 - oy:y1 - oy, ox:ox + 1080]
        card = B * (1 - FX) + S * FX
    out = G * (1 - SHA) + SHC * SHA
    out = out * (1 - M) + card * M
    Ah = place(cv2.resize(A, FEED, interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0, cv2.INTER_LINEAR)[..., None] * RAMP
    out = out * (1 - Ah) + S * Ah
    return np.clip(out, 0, 255).astype(np.uint8)

cam = reader('work/camtrack.mp4', 1080, 1920)
wide = reader('work/camwide.mp4', 1890, 1063) if WIDE else None
cover = cv2.cvtColor(cv2.imread('work/cover.png', cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32)

def open_run(r):
    key = r[3].split()[0]; d = dict(name=key, layout=r[2])
    if r[2] in ('split', 'visual'): d['g'] = reader(f'work/gfx/final/{key.lower()}_60.mp4', 1080, 1920)
    if r[2] == 'split':
        meta = json.load(open(f'work/matte/{key}.json'))
        mw, mh = (960, 540) if WIDE else (540, 960)
        rd = reader(f'work/matte/{key}.mov', mw, mh, 'gray', 'alphaextract')
        d['bysrc'] = {s: rd() for s in meta['src']}
    if r is runs[-1] and os.path.exists('work/gfx/final/cta.mov'): d['cta'] = reader('work/gfx/final/cta.mov', 1080, 1920, 'rgba')
    return d

if ONLY is None:
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(FPS), '-i', '-',
        '-i', 'final_master.wav', '-vf', f"subtitles=work/captions.ass:fontsdir={SK}/../assets/fonts", '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', 'final.mp4'], stdin=subprocess.PIPE)
else: os.makedirs('work/qa', exist_ok=True)
ri = -1; d = None
for i in range(N):
    while ri + 1 < len(runs) and i >= round(runs[ri + 1][0] / 1000 * FPS):   # frame-index boundaries, never float times
        ri += 1; d = open_run(runs[ri])
    F = cam(); WF = wide() if wide else None
    if d['layout'] == 'cam': out = F
    else:
        G = d['g']()
        if G is None: sys.exit(f'graphic for {d["name"]} is shorter than its run (frame {i}): its duration must equal the run')
        out = G if d['layout'] == 'visual' else split_frame(G, WF if WIDE else F, d['bysrc'][FM[i][2]])
    if 'cta' in d:
        c = d['cta']()
        if c is not None: a = c[..., 3:4].astype(np.float32) / 255; out = (out * (1 - a) + c[..., :3] * a).astype(np.uint8)
    if i == 0: a = cover[..., 3:4] / 255; out = (out * (1 - a) + cover[..., :3] * a).astype(np.uint8)
    if ONLY is None: enc.stdin.write(np.ascontiguousarray(out).tobytes())
    elif i in ONLY: cv2.imwrite(f'work/qa/f{i:05d}.png', cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    if ONLY is not None and i >= max(ONLY): break
if ONLY is None: enc.stdin.close(); enc.wait()
print('frames', i + 1, 'of', N)
