"""Build the picture frame by frame from work/plan.json, burn captions, mux the master. Run from edit/.
  python assemble.py               -> final.mp4
  python assemble.py 0,240,1300    -> only write those frames as PNGs to work/qa/ (fast checks; stops at the max)
Inputs: work/camtrack.mp4 (+_map.json), work/camwide.mp4 for landscape sources, work/gfx/final/<run>_60.mp4 per
graphic run, work/matte/<RUN>.mov/.json per split run, work/gfx/final/cta.mov, work/cover.png, work/captions.json
(+ work/captions/ layers from captions.py), final_master.wav.
PORTRAIT sources, optional project.json "split": {"mode": "fit" | "cover", "scale": .., "y": ..}
  fit   (default) footage at 0.72 (778x1382), and the camera card is exactly as wide as the footage (bleeds off
        the bottom only), so no part of the card ever needs filling: no blurred side bands
  cover footage at full width (1080x1920) behind a card that bleeds off left/right/bottom like the 16:9 layout;
        the head is bigger and reaches ~y 760, so split graphics must keep their content above ~y 720"""
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
SPL = CFG.get('split', {}); MODE = 'wide' if WIDE else SPL.get('mode', 'fit')
if MODE == 'wide':    # 16:9 source: footage 1890x1063 at (-405, 1008), as specified
    SW, SH, SX, SY = 1890, 1063, -405, 1008; FEED = (1890, 1063)
elif MODE == 'cover': # portrait at full width: covers the bleeding card; head chin lands near the card edge
    sc = SPL.get('scale', 1.0); SW, SH = round(1080 * sc), round(1920 * sc)
    SX = (1080 - SW) // 2; SY = SPL.get('y', 240); FEED = (1080, 1920)
else:                 # portrait 'fit': head clears the graphic zone; the card shrinks to the footage width
    sc = SPL.get('scale', 0.72); SW, SH = round(1080 * sc), round(1920 * sc)
    SX = (1080 - SW) // 2; SY = SPL.get('y', 1920 - SH); FEED = (1080, 1920)
    CX, CW = SX, SW                                          # card = footage width, so it is always fully covered
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
# the card must be fully covered by real footage: never fill it with blur or stretched pixels
_vis = (M[..., 0] > 0.01) & (yy < 1920)
_cov = (xx >= SX) & (xx < SX + SW) & (yy >= SY) & (yy < SY + SH)
assert not (_vis & ~_cov).any(), 'split card is not fully covered by the footage: adjust "split" scale/y/mode'

def place(img, interp=cv2.INTER_AREA):
    """scale img to (SW,SH) and paste at (SX,SY) on a 1080x1920 canvas (clipped)"""
    s = cv2.resize(img, (SW, SH), interpolation=interp).astype(np.float32)
    out = np.zeros((1920, 1080) + s.shape[2:], np.float32)
    x0, y0 = max(0, SX), max(0, SY); x1, y1 = min(1080, SX + SW), min(1920, SY + SH)
    out[y0:y1, x0:x1] = s[y0 - SY:y1 - SY, x0 - SX:x1 - SX]; return out

def split_frame(G, F, A):
    """G graphic, F split footage frame, A matte of the SAME source frame (any size)"""
    G = G.astype(np.float32); S = place(F)
    out = G * (1 - SHA) + SHC * SHA
    out = out * (1 - M) + S * M                              # the card shows only real footage
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

# ---------- captions: pill layers are pre-rendered; hero letters are filled from each frame ----------
CAPS = json.load(open('work/captions.json')); _cache = {}
def layer(k, name, flag=cv2.IMREAD_UNCHANGED):
    if (k, name) not in _cache:
        im = cv2.imread(f'work/captions/{k:03d}_{name}.png', flag)
        if im.ndim == 3: im = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
        _cache[(k, name)] = im.astype(np.float32) / 255.0
    return _cache[(k, name)]
def ease_out(u): u = min(1.0, max(0.0, u)); return 1 - (1 - u) ** 3
def blit(out, rgba, x, y, op=1.0):
    h, w = rgba.shape[:2]; x0, y0 = max(0, x), max(0, y); x1, y1 = min(1080, x + w), min(1920, y + h)
    if x1 <= x0 or y1 <= y0: return
    src = rgba[y0 - y:y1 - y, x0 - x:x1 - x]; a = src[..., 3:4] * op
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + src[..., :3] * 255 * a
def scaled(img, s):
    if abs(s - 1) < 1e-3: return img
    h, w = img.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, s)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR)
def draw_captions(out, t):
    out = out.astype(np.float32)
    for c in CAPS:
        if not (c['start'] <= t < c['end']): continue
        u = t - c['start']
        if c['style'] == 'pill':                                     # quick 80 ms fade + 4% settle
            blit(out, scaled(layer(c['k'], 'pill'), 0.96 + 0.04 * ease_out(u / 0.12)), c['x'], c['y'], ease_out(u / 0.08))
        else:                                                         # hero: big solid word lands, pills fade in
            s = 1.08 - 0.08 * ease_out(u / 0.22); op = ease_out(u / 0.10)
            mask = scaled(layer(c['k'], 'mask', cv2.IMREAD_GRAYSCALE), s)[..., None] * op
            sh = scaled(layer(c['k'], 'shadow', cv2.IMREAD_GRAYSCALE), s)[..., None] * op
            st = scaled(layer(c['k'], 'stroke', cv2.IMREAD_GRAYSCALE), s)[..., None] * op
            y0 = c['y']; h = mask.shape[0]; y1 = min(1920, y0 + h); ys = max(0, y0)
            reg = out[ys:y1]; m = mask[ys - y0:y1 - y0]; shd = sh[ys - y0:y1 - y0]; stk = st[ys - y0:y1 - y0]
            col = np.array([int(c['color'][i:i + 2], 16) for i in (1, 3, 5)], np.float32)   # solid clothing colour
            deep = col * 0.32                                         # same hue, deep: the outline
            reg[:] = reg * (1 - shd)                                  # soft shadow under everything
            reg[:] = reg * (1 - stk) + deep * stk
            reg[:] = reg * (1 - m) + col * m
            blit(out, layer(c['k'], 'small'), c['x'], y0, ease_out((u - 0.04) / 0.12))
    return np.clip(out, 0, 255).astype(np.uint8)

if ONLY is None:
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(FPS), '-i', '-',
        '-i', 'final_master.wav', '-map', '0:v', '-map', '1:a',
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
    else: out = draw_captions(out, i / FPS)
    if ONLY is None: enc.stdin.write(np.ascontiguousarray(out).tobytes())
    elif i in ONLY: cv2.imwrite(f'work/qa/f{i:05d}.png', cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    if ONLY is not None and i >= max(ONLY): break
if ONLY is None: enc.stdin.close(); enc.wait()
print('frames', i + 1, 'of', N)
