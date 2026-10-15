"""Captions (ASS for libass) from the FINAL voice-track word timings + the frame-0 cover PNG. Run from edit/.
project.json "captions":
  "chunks": [[first_word, last_word, [highlight word indices]], ...]   1-3 words each, contiguous over all words.
            Omit it to get an automatic draft printed (then copy, fix and paste it back).
  "display": {"<word index>": "text"}   per-word display overrides ("" hides a word, e.g. a split ".ai")
  "y": {"split": 1027, "cam": 1401, "visual": 1401, "outro": 1171, "<run key>": y}   caption centre per layout
  "cover": ["Line one", "line two"]
Rules enforced: 1-3 words, a highlight after every 2-3 normal chunks, never two highlights in a row."""
import json, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SK = os.path.dirname(os.path.abspath(__file__))
P = json.load(open('work/plan.json')); Wd = P['words']; END = P['END']; runs = P['runs']
C = json.load(open('project.json')).get('captions', {})
FUNC = set('a an the and or but so to of in on at for from with by as is are was were be it its it\'s i i\'ll you your we they them this that there then just even still'.split())
clean = lambda s: re.sub(r'[^\w\']', '', s.lower())

def auto_chunks():
    out = []; i = 0
    while i < len(Wd):
        n = 1
        while n < 3 and i + n < len(Wd) and not re.search(r'[.,?!]$', Wd[i + n - 1]['t']) and len(' '.join(w['t'] for w in Wd[i:i + n + 1])) <= 18:
            n += 1
        out.append([i, i + n - 1, []]); i += n
    since = 0
    for c in out:
        cand = [j for j in range(c[0], c[1] + 1) if clean(Wd[j]['t']) not in FUNC and len(clean(Wd[j]['t'])) > 3]
        if since >= 2 and cand: c[2] = cand[-1:]; since = 0
        else: since += 1
    return out
chunks = C.get('chunks') or auto_chunks()
if not C.get('chunks'):
    print('AUTO DRAFT (review: highlights should be product names, numbers, benefits, the CTA keyword):')
    print(json.dumps(chunks))
assert chunks[0][0] == 0 and chunks[-1][1] == len(Wd) - 1, 'chunks must cover every word'
for a, b in zip(chunks, chunks[1:]): assert b[0] == a[1] + 1, f'gap/overlap at {a} {b}'
assert all(1 <= c[1] - c[0] + 1 <= 3 for c in chunks), 'chunks are 1-3 words'
hl = [i for i, c in enumerate(chunks) if c[2]]
for a, b in zip(hl, hl[1:]): assert 3 <= b - a <= 4, f'highlight spacing at chunks {a},{b} (want 2-3 normal chunks between)'
DISP = {int(k): v for k, v in C.get('display', {}).items()}
Y = dict(split=1027, cam=1401, visual=1401, outro=1171); Y.update(C.get('y', {}))
def where(t):
    for i, r in enumerate(runs):
        if r[0] / 1000 <= t + 1e-6 < r[1] / 1000: return r, i == len(runs) - 1
    return runs[-1], True
ts = lambda t: (lambda cs: f'{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}')(int(round(t * 100)))
lines = []
for k, (a, b, h) in enumerate(chunks):
    st = max(0.017, Wd[a]['s'])                                  # frame 0 stays clean
    en = min(Wd[chunks[k + 1][0]]['s'], Wd[b]['e'] + 0.6) if k + 1 < len(chunks) else END
    r, last = where(st); key = r[3].split()[0]
    y = Y.get(key, Y['outro'] if last else Y[r[2]])
    parts = []
    for i in range(a, b + 1):
        s = DISP.get(i, Wd[i]['t'])
        if s: parts.append(r'{\fnInstrument Serif\i1\b1\c&H00FFFF&}' + s + r'{\r}' if i in h else s)
    lines.append(f'Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\an5\\pos(540,{y})}}' + ' '.join(parts))
open('work/captions.ass', 'w').write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Poppins,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + '\n'.join(lines) + '\n')
print(len(lines), 'caption chunks,', len(hl), 'highlights -> work/captions.ass')

# cover: Poppins Bold 110, black on a white rounded box centred around y 262-603, frame 0 only
L = C.get('cover', ['Your title', 'goes here'])
F = ImageFont.truetype(f'{SK}/../assets/fonts/Poppins-Bold.ttf', 110)
ws = [ImageDraw.Draw(Image.new('L', (1, 1))).textlength(s, font=F) for s in L]
lh = 124; bw = int(min(1040, max(ws) + 100)); bh = 92 + lh * len(L) + 1; x0 = (1080 - bw) // 2; y0 = 262
im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 24, x0 + bw, y0 + bh + 24], 30, fill=70)
im = Image.composite(Image.new('RGBA', im.size, (24, 24, 32, 255)), im, sh.filter(ImageFilter.GaussianBlur(28)))
d = ImageDraw.Draw(im); d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 30, fill=(255, 255, 255, 255))
ty = y0 + (bh - len(L) * lh) // 2 - 8
for i, s in enumerate(L): d.text(((1080 - ws[i]) / 2, ty + i * lh), s, font=F, fill=(17, 17, 17, 255))
im.save('work/cover.png'); print('cover box', x0, y0, bw, bh, '(widest line must fit: shorten it if bw hit 1040)')
