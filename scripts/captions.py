"""Captions from the FINAL voice-track word timings, in two styles, plus the frame-0 cover. Run from edit/.

  PILL  small Poppins Bold white text on a translucent dark rounded box. The default: talking over visuals/B-roll.
  HERO  a stacked moment: small white script word(s) above, one or two HUGE see-through words (the footage shows
        through the letters, brightened and washed), small script word(s) below. Example: "everybody / WANTED TO / know".
        Use it in the hook and on important lines where only the speaker is on screen (full cam, or the card in a split).

project.json "captions":
  "chunks": [[first_word, last_word, "pill"], [first_word, last_word, "hero", [big word indices]], ...]
            contiguous over all words. Pill = 1-3 words. Hero = 2-5 words with 1-2 big words in the middle;
            words before the big ones go on top, words after go below. Omit "chunks" to get a printed auto draft.
  "display": {"<word index>": "text"}   per-word display text ("" hides a word)
  "y":      {"split": 1027, "cam": 1401, "visual": 1401, "outro": 1171, "<run key>": y}   pill centre per layout
  "hero_y": {"cam": 1380, "split": 1640}                                                  hero block centre
  "cover":  ["Line one", "line two"]
Writes work/captions.json (+ per-chunk PNG layers in work/captions/) and work/cover.png.
assemble.py composites them; hero fills are taken from each frame, so the footage really shows through."""
import json, os, re, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SK = os.path.dirname(os.path.abspath(__file__)); FD = f'{SK}/../assets/fonts'
P = json.load(open('work/plan.json')); Wd = P['words']; END = P['END']; runs = P['runs']
C = json.load(open('project.json')).get('captions', {})
FUNC = set("a an the and or but so to of in on at for from with by as is are was were be it its it's i i'll you your we they them this that there then just".split())
clean = lambda s: re.sub(r"[^\w']", '', s.lower())

def auto_chunks():
    """pill everywhere, 1-3 words broken at punctuation; the hook's key phrase drafted as a hero for review"""
    out = []; i = 0
    while i < len(Wd):
        n = 1
        while n < 3 and i + n < len(Wd) and not re.search(r'[.,?!]$', Wd[i + n - 1]['t']) and len(' '.join(w['t'] for w in Wd[i:i + n + 1])) <= 20:
            n += 1
        out.append([i, i + n - 1, 'pill']); i += n
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
    if c[2] == 'pill': assert 1 <= n <= 3, f'pill chunk {c} must be 1-3 words'
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
F_SCRIPT = ImageFont.truetype(f'{FD}/Pacifico-Regular.ttf', 104)
def shadow_of(alpha, blur, opacity, dy):
    s = Image.new('L', alpha.size, 0); s.paste(alpha, (0, dy)); s = s.filter(ImageFilter.GaussianBlur(blur))
    return s.point(lambda v: int(v * opacity))

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

def hero(top, big, bottom):
    """layers: big-word alpha mask (filled per frame with the footage), its shadow, and the script words (RGBA)"""
    W = 1080; big = re.sub(r'[.,!?]+$', '', big.upper()); size = 260
    while True:
        F = ImageFont.truetype(f'{FD}/ArchivoBlack-Regular.ttf', size)
        l, t, r, b = ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((0, 0), big, font=F)
        if r - l <= 1000 or size <= 120: break
        size -= 6
    bw, bh = r - l, b - t
    Hc = bh + 2 * 150; ox = (W - bw) // 2; oy = 150
    mask = Image.new('L', (W, Hc), 0); ImageDraw.Draw(mask).text((ox - l, oy - t), big, font=F, fill=255)
    sh = shadow_of(mask, 9, 0.62, 7)
    sc = Image.new('L', (W, Hc), 0); ds = ImageDraw.Draw(sc)
    if top:
        tl, tt, tr, tb = ds.textbbox((0, 0), top, font=F_SCRIPT)
        ds.text((max(30, ox - 10) - tl, oy - (tb - tt) * 0.78 - tt), top, font=F_SCRIPT, fill=255)
    if bottom:
        bl, bt, br, bb = ds.textbbox((0, 0), bottom, font=F_SCRIPT)
        ds.text((min(W - 30, ox + bw + 10) - (br - bl) - bl, oy + bh - (bb - bt) * 0.18 - bt), bottom, font=F_SCRIPT, fill=255)
    scs = shadow_of(sc, 6, 0.7, 4)
    script = Image.alpha_composite(Image.merge('RGBA', [Image.new('L', sc.size, 0)] * 3 + [scs]),
                                   Image.merge('RGBA', [Image.new('L', sc.size, 255)] * 3 + [sc]))
    return mask, sh, script, Hc

shutil.rmtree('work/captions', ignore_errors=True); os.makedirs('work/captions')
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
    else:
        bigs = c[3]; top = txt(range(a, bigs[0])); big = txt(bigs); bottom = txt(range(bigs[-1] + 1, b + 1))
        mask, sh, script, Hc = hero(top, big, bottom); y = HY.get(key, HY.get(r[2], HY['cam']))
        mask.save(f'work/captions/{k:03d}_mask.png'); sh.save(f'work/captions/{k:03d}_shadow.png'); script.save(f'work/captions/{k:03d}_script.png')
        items.append(dict(k=k, style='hero', start=st, end=en, x=0, y=y - Hc // 2, text=f'{top} | {big.upper()} | {bottom}'))
json.dump(items, open('work/captions.json', 'w'), indent=1)
print(len(items), 'caption chunks:', sum(i['style'] == 'hero' for i in items), 'hero,', sum(i['style'] == 'pill' for i in items), 'pill -> work/captions.json')

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
