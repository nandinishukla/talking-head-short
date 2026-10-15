"""Captions from the FINAL voice-track word timings, in three styles, plus the frame-0 cover. Run from edit/.

  PILL  small Poppins Bold white text on a translucent dark rounded box. Default small caption for general videos.
  MONO  terminal typewriter: uppercase pixel-mono (VT323) white on a near-black box that grows as the letters type in,
        the keyword on an accent block, an accent block cursor at the end. The small caption for tech / AI-tool /
        developer videos (and any video with terminals or code on screen). One small style per video: "small_style".
  HERO  a stacked moment: small word(s) above as a pill, one or two HUGE solid words in the speaker's clothing colour,
        small word(s) below as a pill. Example: "everybody / WANTED TO / know".
        Use it in the hook and on important lines where only the speaker is on screen (full cam, or the card in a split).
        The colour is sampled once per video from the speaker's clothes (torso area of the hook frame), so every
        video gets its own accent; override with "hero_color": "#RRGGBB".

project.json "captions":
  "small_style": "pill" | "mono"   the small caption for this video (auto draft uses it; hero small words follow it)
  "chunks": [[first_word, last_word, "pill"], [a, b, "mono", [accent word indices]], [a, b, "hero", [big word indices]], ...]
            contiguous over all words. Pill / mono = 1-3 words (mono: 0-1 accent word, a meaningful one). Hero = 2-5 words with 1-2 big words in the middle;
            words before the big ones go on top, words after go below. Omit "chunks" to get a printed auto draft.
  "display": {"<word index>": "text"}   per-word display text ("" hides a word)
  "y":      {"split": 1027, "cam": 1401, "visual": 1401, "outro": 1171, "<run key>": y}   pill centre per layout
  "hero_y": {"cam": 1380, "split": 1640}                                                  hero block centre
  "cover":  ["Line one", "line two"]
  "hero_color": "#RRGGBB"   optional; otherwise picked from the clothes (pass the oriented camera video as argv[1])
Usage: python captions.py [work/cam1080.mp4]
Writes work/captions.json (+ per-chunk PNG layers in work/captions/), work/hero_color.json and work/cover.png.
assemble.py composites the layers."""
import json, os, re, shutil, subprocess, sys, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SK = os.path.dirname(os.path.abspath(__file__)); FD = f'{SK}/../assets/fonts'
P = json.load(open('work/plan.json')); Wd = P['words']; END = P['END']; runs = P['runs']
C = json.load(open('project.json')).get('captions', {})
FUNC = set("a an the and or but so to of in on at for from with by as is are was were be it its it's i i'll you your we they them this that there then just".split())
clean = lambda s: re.sub(r"[^\w']", '', s.lower())

SMALL = C.get('small_style', 'pill')
def auto_chunks():
    """small style everywhere, 1-3 words broken at punctuation; the hook's key phrase drafted as a hero for review"""
    out = []; i = 0
    while i < len(Wd):
        n = 1
        while n < 3 and i + n < len(Wd) and not re.search(r'[.,?!]$', Wd[i + n - 1]['t']) and len(' '.join(w['t'] for w in Wd[i:i + n + 1])) <= 20:
            n += 1
        ch = [i, i + n - 1, SMALL]
        if SMALL == 'mono':   # the keyword on the accent block: the longest meaningful word, if any
            cand = [j for j in range(i, i + n) if clean(Wd[j]['t']) not in FUNC and len(clean(Wd[j]['t'])) > 3]
            ch.append(sorted(cand, key=lambda j: -len(Wd[j]['t']))[:1])
        out.append(ch); i += n
    hook_end = runs[0][1] / 1000
    for c in out:
        if Wd[c[0]]['s'] < hook_end and c[1] > c[0]:
            cand = [j for j in range(c[0], c[1] + 1) if clean(Wd[j]['t']) not in FUNC]
            if cand: c[2:] = ['hero', cand[:1]]; break
    return out
chunks = C.get('chunks') or auto_chunks()
if not C.get('chunks'):
    print('AUTO DRAFT: review, choose hero moments (hook + key lines with only the speaker on screen), paste into project.json:')
    print(json.dumps(chunks))
assert chunks[0][0] == 0 and chunks[-1][1] == len(Wd) - 1, 'chunks must cover every word'
for a, b in zip(chunks, chunks[1:]): assert b[0] == a[1] + 1, f'gap/overlap at {a} {b}'
for c in chunks:
    n = c[1] - c[0] + 1
    if c[2] in ('pill', 'mono'):
        assert 1 <= n <= 3, f'{c[2]} chunk {c} must be 1-3 words'
        if c[2] == 'mono': assert len(c) < 4 or (len(c[3]) <= 1 and all(c[0] <= j <= c[1] for j in c[3])), f'mono chunk {c}: 0-1 accent word inside it'
    else:
        assert c[2] == 'hero' and 1 <= n <= 5 and 1 <= len(c[3]) <= 2 and all(c[0] <= j <= c[1] for j in c[3]), f'bad hero chunk {c}'
for a, b in zip(chunks, chunks[1:]): assert not (a[2] == b[2] == 'hero'), f'two hero moments in a row at {a}'
DISP = {int(k): v for k, v in C.get('display', {}).items()}
Y = dict(split=1027, cam=1401, visual=1401, outro=1171); Y.update(C.get('y', {}))
HY = dict(cam=1380, split=1640); HY.update(C.get('hero_y', {}))
def where(t):
    for i, r in enumerate(runs):
        if r[0] / 1000 <= t + 1e-6 < r[1] / 1000: return r, i == len(runs) - 1
    return runs[-1], True

F_PILL = ImageFont.truetype(f'{FD}/Poppins-Bold.ttf', 64)
def shadow_of(alpha, blur, opacity, dy):
    s = Image.new('L', alpha.size, 0); s.paste(alpha, (0, dy)); s = s.filter(ImageFilter.GaussianBlur(blur))
    return s.point(lambda v: int(v * opacity))

def clothing_colour(video, t_out):
    """Dominant clothing colour from the torso area of one camera frame: k-means on the region below the face,
    ignoring near-black (hair, shadows), near-white (highlights) and skin tones; then tuned for a bold solid word."""
    E = json.load(open('work/edl.json'))
    k = max(j for j, s_ in enumerate(E['segs']) if s_['cut'] <= t_out + 1e-9); src = t_out - E['segs'][k]['delta']
    regs = []
    for dt in (0.0, 0.8, 1.6):          # three frames, so a hand or a hair strand over the torso can't decide the colour
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{src + dt:.3f}', '-i', video, '-frames:v', '1', '-vf', 'scale=270:-2',
                              '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        h = len(raw) // (270 * 3); img = np.frombuffer(raw[:270 * 3 * h], np.uint8).reshape(h, 270, 3).astype(np.float32) / 255
        portrait = h > 270
        y0, y1 = (int(h * .58), int(h * .9)) if portrait else (int(h * .65), h)
        regs.append(img[y0:y1, int(270 * .18):int(270 * .82)].reshape(-1, 3))
    reg = np.concatenate(regs)
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in reg])
    skin = (hsv[:, 0] < 0.11) & (hsv[:, 1] > 0.18) & (hsv[:, 1] < 0.6) & (hsv[:, 2] > 0.35)
    keep = (hsv[:, 2] > 0.22) & (hsv[:, 2] < 0.97) & ~skin
    px = reg[keep] if keep.sum() > 200 else reg
    rng = np.random.default_rng(1); cent = px[rng.choice(len(px), 4, replace=False)]
    for _ in range(15):
        lab = np.argmin(((px[:, None] - cent[None]) ** 2).sum(-1), 1)
        cent = np.array([px[lab == i].mean(0) if (lab == i).any() else cent[i] for i in range(4)])
    share = np.bincount(lab, minlength=4) / len(lab)
    sat = np.array([colorsys.rgb_to_hsv(*c)[1] for c in cent])
    c = cent[np.argmax(share * (0.35 + sat))]                  # big AND colourful wins over big grey
    hh, ss, vv = colorsys.rgb_to_hsv(*c)
    ss = min(1.0, max(ss * 1.25, 0.35)) if ss > 0.08 else ss   # keep greys grey, give colours some punch
    vv = min(0.97, max(vv, 0.78))                              # bright enough to read on a dark room
    r, g, b = colorsys.hsv_to_rgb(hh, ss, vv)
    return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255)), '#%02X%02X%02X' % tuple(round(x * 255) for x in c)

def pill(text):
    """RGBA layer: white bold text with a soft shadow on a 45% dark rounded box"""
    d0 = ImageDraw.Draw(Image.new('L', (1, 1))); l, t, r, b = d0.textbbox((0, 0), text, font=F_PILL)
    pw, ph = 30, 14; W, H = r - l + 2 * pw, b - t + 2 * ph
    im = Image.new('RGBA', (W + 40, H + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, 20 + W, 20 + H], 18, fill=(18, 18, 22, 140))
    txt = Image.new('L', im.size, 0); ImageDraw.Draw(txt).text((20 + pw - l, 20 + ph - t), text, font=F_PILL, fill=255)
    sh = shadow_of(txt, 5, 0.75, 3)
    im = Image.alpha_composite(im, Image.merge('RGBA', [Image.new('L', im.size, 0)] * 3 + [sh]))
    im = Image.alpha_composite(im, Image.merge('RGBA', [Image.new('L', im.size, 255)] * 3 + [txt]))
    return im

F_MONO = ImageFont.truetype(f'{FD}/VT323-Regular.ttf', 84)
ACCENT = '#D97757'
if os.path.exists('work/accent.json'): ACCENT = json.load(open('work/accent.json'))['color']
def mono(words, accent_ids):
    """Typewriter caption. words: [(word, is_accent)]. Returns the text layer (RGBA, no box), the char-count -> x edge
    table, and the box geometry; assemble.py draws the growing box, this layer cropped to the typed chars, the cursor."""
    text = ' '.join(w.upper() for w, _ in words)
    asc, desc = F_MONO.getmetrics(); px, py, gap, cw = 22, 8, 14, 26
    H = asc + desc + 2 * py; W = int(F_MONO.getlength(text)) + 2 * px + gap + cw
    edges = [int(px + F_MONO.getlength(text[:i])) for i in range(len(text) + 1)]
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x = 0
    for w, acc in words:                                   # accent block behind the keyword
        w = w.upper(); i0 = text.find(w, x); i1 = i0 + len(w); x = i1
        if acc: d.rectangle([edges[i0] - 8, py - 2, edges[i1] + 8, H - py + 2], fill=ACCENT)
    d.text((px, py), text, font=F_MONO, fill=(255, 255, 255, 255))
    return lay, edges, dict(w=W, h=H, px=px, py=py, gap=gap, cw=cw, n=len(text))
def mono_full(text):
    """static mono box with the whole text (for hero small words in a mono video)"""
    lay, edges, g = mono([(w, False) for w in text.split()], [])
    im = Image.new('RGBA', (g['w'] - g['gap'] - g['cw'], g['h']), (18, 18, 20, 235)); im.alpha_composite(lay.crop((0, 0, im.width, g['h'])))
    return im

def hero(top, big, bottom):
    """layers: big-word alpha mask + its shadow (filled with the solid hero colour in assemble.py), and the small
    words as pills (RGBA): top pill tucked over the big word's top-left, bottom pill under its bottom-right"""
    W = 1080; big = re.sub(r'[.,!?]+$', '', big.upper()); size = 260
    while True:
        F = ImageFont.truetype(f'{FD}/ArchivoBlack-Regular.ttf', size)
        l, t, r, b = ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((0, 0), big, font=F)
        if r - l <= 1000 or size <= 120: break
        size -= 6
    bw, bh = r - l, b - t
    Hc = bh + 2 * 150; ox = (W - bw) // 2; oy = 150
    mask = Image.new('L', (W, Hc), 0); ImageDraw.Draw(mask).text((ox - l, oy - t), big, font=F, fill=255)
    # outline in a deep shade of the same hue: the word keeps the clothing colour but still reads ON those clothes
    stroke = Image.new('L', (W, Hc), 0)
    ImageDraw.Draw(stroke).text((ox - l, oy - t), big, font=F, fill=255, stroke_width=7, stroke_fill=255)
    sh = shadow_of(stroke, 9, 0.62, 7)
    small = Image.new('RGBA', (W, Hc), (0, 0, 0, 0))
    small_box = mono_full if SMALL == 'mono' else pill
    if top:
        p_ = small_box(top); small.alpha_composite(p_, (max(10, ox - 30), max(0, oy - p_.height + 14)))
    if bottom:
        p_ = small_box(bottom); small.alpha_composite(p_, (min(W - p_.width - 10, ox + bw - p_.width + 30), min(Hc - p_.height, oy + bh - 14)))
    return mask, stroke, sh, small, Hc

shutil.rmtree('work/captions', ignore_errors=True); os.makedirs('work/captions')
HERO_COLOR = C.get('hero_color')
if not HERO_COLOR and any(c[2] == 'hero' for c in chunks):
    if len(sys.argv) > 1:
        first = next(c for c in chunks if c[2] == 'hero')
        HERO_COLOR, sampled = clothing_colour(sys.argv[1], Wd[first[0]]['s'] + 0.2)
        print('hero colour picked from the clothes:', HERO_COLOR, '(sampled', sampled + ')')
    else:
        HERO_COLOR = '#FFFFFF'; print('no camera video given and no "hero_color": hero words fall back to white')
json.dump(dict(hero_color=HERO_COLOR), open('work/hero_color.json', 'w'))
items = []
for k, c in enumerate(chunks):
    a, b, style = c[0], c[1], c[2]
    st = max(0.017, Wd[a]['s'])                                    # frame 0 stays clean
    en = min(Wd[chunks[k + 1][0]]['s'], Wd[b]['e'] + 0.6) if k + 1 < len(chunks) else END
    r, last = where(st); key = r[3].split()[0]
    txt = lambda ids: ' '.join(s for s in (DISP.get(i, Wd[i]['t']) for i in ids) if s)
    if style == 'pill':
        im = pill(txt(range(a, b + 1))); y = Y.get(key, Y['outro'] if last else Y[r[2]])
        im.save(f'work/captions/{k:03d}_pill.png')
        items.append(dict(k=k, style='pill', start=st, end=en, x=(1080 - im.width) // 2, y=y - im.height // 2, text=txt(range(a, b + 1))))
    elif style == 'mono':
        acc = set(c[3]) if len(c) > 3 else set()
        words = [(DISP.get(i, Wd[i]['t']), i in acc) for i in range(a, b + 1)]; words = [(w, f) for w, f in words if w]
        lay, edges, g = mono(words, acc); y = Y.get(key, Y['outro'] if last else Y[r[2]])
        lay.save(f'work/captions/{k:03d}_mono.png')
        items.append(dict(k=k, style='mono', start=st, end=en, x=(1080 - g['w']) // 2, y=y - g['h'] // 2, edges=edges, cps=30, text=txt(range(a, b + 1)), **g))
    else:
        bigs = c[3]; top = txt(range(a, bigs[0])); big = txt(bigs); bottom = txt(range(bigs[-1] + 1, b + 1))
        mask, stroke, sh, small, Hc = hero(top, big, bottom); y = HY.get(key, HY.get(r[2], HY['cam']))
        stroke.save(f'work/captions/{k:03d}_stroke.png'); mask.save(f'work/captions/{k:03d}_mask.png'); sh.save(f'work/captions/{k:03d}_shadow.png'); small.save(f'work/captions/{k:03d}_small.png')
        items.append(dict(k=k, style='hero', start=st, end=en, x=0, y=y - Hc // 2, color=HERO_COLOR, text=f'{top} | {big.upper()} | {bottom}'))
json.dump(items, open('work/captions.json', 'w'), indent=1)
print(len(items), 'caption chunks:', ', '.join(f"{sum(i['style'] == s_ for i in items)} {s_}" for s_ in ('hero', 'pill', 'mono')), '-> work/captions.json')

# cover: Poppins Bold 110, black on a white rounded box centred around y 262-603, frame 0 only
L = C.get('cover', ['Your title', 'goes here'])
F = ImageFont.truetype(f'{FD}/Poppins-Bold.ttf', 110)
ws = [ImageDraw.Draw(Image.new('L', (1, 1))).textlength(s, font=F) for s in L]
lh = 124; bw = int(min(1040, max(ws) + 100)); bh = 92 + lh * len(L) + 1; x0 = (1080 - bw) // 2; y0 = 262
im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 24, x0 + bw, y0 + bh + 24], 30, fill=70)
im = Image.composite(Image.new('RGBA', im.size, (24, 24, 32, 255)), im, sh.filter(ImageFilter.GaussianBlur(28)))
d = ImageDraw.Draw(im); d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 30, fill=(255, 255, 255, 255))
ty = y0 + (bh - len(L) * lh) // 2 - 8
for i, s in enumerate(L): d.text(((1080 - ws[i]) / 2, ty + i * lh), s, font=F, fill=(17, 17, 17, 255))
im.save('work/cover.png'); print('cover box', x0, y0, bw, bh, '(widest line must fit: shorten it if bw hit 1040)')
