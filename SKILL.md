---
name: talking-head-short
description: Edit a raw talking-head recording into a finished, ready-to-post 9:16 short (Instagram Reel, TikTok, YouTube Short) entirely in code. It covers syncing camera and clean audio, transcribing with word timestamps, picking the last good take of every line and cutting retakes, pauses and false starts with a J-cut voice track, and an eye-contact check. Each run gets one of three layouts (full cam, split with the head popping out of a camera card, full-frame "luxury tech" HyperFrames graphic with a moving world camera and motion blur). It plans the edit as a storyboard and beat table and waits for the user's approval before rendering anything. It burns in two caption styles (small pill captions, and big hero words in the speaker's clothing colour for the hook and key lines), adds a cover title and a CTA comment card, synthesizes SFX, a riser and a music bed in numpy, mixes to -14 LUFS, and writes a report. Use it whenever someone hands you raw footage (a .MP4/.MOV of themselves talking) and wants a short, reel, TikTok, YouTube Short or "edit like a creator", wants retakes removed, captions, B-roll graphics or a vertical cut, or says "edit my video" — even if they don't name the steps.
---

# Talking-head → finished 9:16 short

The pipeline takes one raw recording (plus an optional clean-audio file) to `edit/final.mp4` (1080×1920, 60 fps, H.264 + AAC 48 kHz). It also writes four full-length stems and a report. Everything happens in code, installed locally inside the project: ffmpeg, Python, Node and HyperFrames. No system-wide installs and no editor apps.

- **The standard:** `references/brief.md` is the full house brief, with every number for levels, geometry, timing, type and colour. When this file and the brief disagree on a number, the brief wins.
- **Read before starting:** `references/lessons.md` covers the traps that cost hours on the first run.
- **Sound profile:** `references/sound-profile.md` has the creator's sound-effect style and levels, measured from their own edit.
- **Motion library:** `references/motion-library.md` holds the user's curated motion references, the house look the graphics follow.
- **Examples:** `references/examples/` holds the graphics from the first short (r1–r9 plus cta). `references/example-report.md` is a finished report.

Work autonomously apart from one deliberate stop: the storyboard approval in step 7. The brief tells the user not to be asked anything: make each judgement call (take choice, layout, factual disagreement, unreachable UI), keep going, and log it for the report. The storyboard approval is the only point where you wait for the user. Only stop if the input files are missing or unreadable.

## Layout of a project

```
<project>/RAW.MP4 (+ clean audio if any)
<project>/edit/
  project.json        # every per-video decision lives here (takes, runs, captions, cover…)
  tools/              # bin/ffmpeg, bin/ffprobe, venv/, node_modules/ (setup.sh)
  work/               # all intermediates (gfx/ is the HyperFrames project)
  stems/  final.mp4  final_master.wav  REPORT.md
```

All scripts run **from `edit/`** with `export PATH="$PWD/tools/bin:$PATH"` and `PY=tools/venv/bin/python`. `$S` below is this skill's `scripts/` folder.

## Steps

### 0. Setup and probe
`bash $S/setup.sh <project>`. Then `ffprobe -show_streams` the camera file and note:
- the size and the **rotation** (portrait sources often arrive as landscape with a −90° flag);
- the fps;
- the audio layout.

Decode once into an oriented intermediate. Don't re-decode 4K for every step:
`ffmpeg -i RAW.MP4 -an -vf scale=1080:-2 -c:v libx264 -crf 13 -g 15 work/cam1080.mp4`
Use `scale=-2:1080` for a landscape source. Run long commands in the background: about 6 min per 90 s of 4K on an 8 GB Mac.

### 1. Sync and transcribe
1. `$PY $S/analyze_audio.py <camera> [clean_audio]` cross-correlates at 16 kHz and reports the offset and peak ratio. It writes the voice source on the camera timeline, the 10 ms RMS envelope, the clipped-sample count and the noise floor. With no clean file, it uses the camera track and you must say so in the report.
2. `$PY $S/transcribe.py medium.en "Product names, people, @handles"` lists every word with gaps over 250 ms flagged.
3. Re-run `analyze_audio.py` so the quiet-stretch listing shows the neighbouring words.
4. Group the words into **takes per line**. For each line, keep the **last complete take**. Use an earlier one only if the last has an audible defect (stutter, clipped or wrong word, restart). Drop restarts, self-corrections, "okay", stray syllables and muttering after takes, plus dead air at both ends.

### 2. The cut
Write `project.json → "lines": [[label, src_start, src_end], …]` with rough edges around each kept take, in delivery order. Contiguous lines can share one range. Then:
1. `$PY $S/cut.py` handles onsets/true ends (−35 dB / −32 dB-for-150 ms), pauses over 250 ms → 120 ms, a 40 ms lead-in, a 50 ms audio J-cut lead, tails that fade within the gap, frame-quantized picture cuts and END.
2. `$PY $S/check_joins.py`: any join with a quiet stretch over 150 ms gets a negative `"gap_overrides": {"<segment>": -0.0333}`. Re-run `cut.py`. Never add silence.

### 3. Eye contact
Make a small proxy (`scale=-2:540`), then `$PY $S/eyesheet.py work/proxy.mp4` and **look at** `work/eye/*.jpg`. Add 100 ms steps around any head turn. The camera shows only while the speaker is on-lens. If they look away mid-line, split at the word boundary before the turn and make the rest a full visual.

### 4. Plan the runs (before any graphic)
`$PY $S/plan.py` prints the picture-cut times. Write `"runs": [[start_ms, end_ms, layout, "R1 hook"], …]` tiling [0, END] (use `"END"` for the last end), then re-run it. It validates the rules:
- the hook is a split and the outro (CTA onwards) is full cam;
- no run is over about 8 s and neighbours never share a layout;
- all three layouts are used.

Choose layouts by content:
- direct-to-camera opinions and stories → **cam**;
- one screenshot, card, logo row or short list → **split**;
- screen recordings, news pages, product UI that needs zooming → **visual**.

Put boundaries on picture cuts. `plan.py` then prints each run's words with run-relative times; time the graphics to those.

### 5. Research and captures
For every named product and every claim (release, quote, number), find the real source and check figures against **two or more** reputable sources. Note any disagreement for the report.
- Capture real pages with `node $S/shot.mjs <url> <out.png> 1280 1400 0`, run from `edit/`. It finds HyperFrames' chrome-headless-shell itself. Respect each site's robots.txt and terms: capture the pages you cite, don't crawl.
- Repos often ship a UI GIF or screenshots in `docs/`; rebuild the UI from those.
- A login-walled UI is rebuilt from public screenshots or docs and noted in the report.
- "Claude Code" means the Claude desktop app UI unless the speaker is talking about the terminal.

### 6. Captions and cover (planned now, because the storyboard shows them)
`$PY $S/captions.py work/cam1080.mp4` (the camera video is for the hero colour). Without `"captions.chunks"` it prints an auto draft (pill everywhere, one hero drafted in the hook). Edit it and paste it back. There are two styles:
- **pill** `[a, b, "pill"]`: 1–3 words, small Poppins Bold on a translucent dark rounded box. Use it whenever the speaker talks over visuals or B-roll.
- **hero** `[a, b, "hero", [big word indices]]`: 2–5 words with 1–2 HUGE solid words (Archivo Black) between small words above and below, which are pills in the same style as the pill captions. The big word's colour matches the speaker's clothes: `captions.py work/cam1080.mp4` samples the torso in the first hero frame and prints the colour it picked. It has a deep same-hue outline so it reads over those clothes. Override with `"hero_color": "#RRGGBB"` if the pick is off (busy prints, a jacket over a shirt). Use it in the hook and on important lines where only the speaker is on screen (full cam, or the card in a split), never over a graphic and never two in a row. Pick words that carry the meaning (the claim, number or benefit), never function words.

Set `"cover": [line1, line2]` (write it from the hook if the user gave none, about 14 characters per line at 110 px). Set the pill centre per layout in `"y"` and the hero block centre in `"hero_y"`.
- Captions must never sit on the face, the card edge or a visual.
- With a portrait source the split gap is the face, so put pills at about y 1660 on the torso, and check the outro on a real frame.
- `assemble.py` composites both styles.

### 7. Storyboard and beat table: STOP for approval
Nothing gets rendered until the user has seen and approved the plan.
1. Pick motion references for each graphic beat from `references/motion-library.md` (the user's curated house look). `references/motion-prompts.md` holds the full prompt texts (credited to their creators); read the block for each cited id. Never scrape third-party galleries. The library entries were added by the user, and some sites, e.g. prompt-motion.com, block AI crawlers.
2. Choose the video's **accent colour** from what's being taught: the main product's brand colour (logo, primary button), else a colour that suits the subject. Write `"accent": {"color": "#RRGGBB", "why": "..."}` and run `$PY $S/accent.py`. It writes `work/gfx/assets/accent.css` (accent fill, a 4.5:1 text shade and a light band tint), which every composition picks up through `base.css`. Never hard-code accent hex values in compositions: use `var(--clay)`, `var(--clayText)` and `var(--band)`. The hero-caption colour is separate (it comes from the clothes).
3. Write `"beats"` in project.json, one or more per run: `{"run": "R1", "t": 0.0, "visual": "...", "camera": "...", "sfx": "...", "refs": ["id"], "source": "real capture / rebuilt UI / logo"}`. Optionally add `"storyboard_notes": {"R1": "why this layout"}`.
4. `$PY $S/storyboard.py work/cam1080.mp4` writes `work/storyboard.html`: a 9:16 sketch per run (layout zones, the speaker's frame, the graphic, caption style and position) and the beat table (time, run, layout, exact words, on-screen action, camera move, SFX, caption style with every hero moment, motion refs, source).
5. Show it to the user (the page shows the accent swatch and why it was chosen): publish it as an artifact, or send the file, and give one line on what to look at. Then **end your turn and wait**. Apply their changes to project.json, regenerate, and show it again. Continue only on a clear approval.

### 8. Graphics (HyperFrames)
1. Copy `assets/engine.js`, `assets/base.css`, `assets/accent.css`, `assets/fonts/` and `assets/motion/` into `work/gfx/assets/` (then re-run `accent.py` so the per-video accent replaces the default), plus `hyperframes.json` from `hyperframes init`.
2. Write one `work/gfx/compositions/<run key lowercase>.html` per split/visual run. Its `data-duration` must equal the run exactly.
3. Build exactly what the approved storyboard shows, matching each beat's motion references. Start from the closest example in `references/examples/`:
   - `r1`, `r3`, `r5`, `r7`: split worlds with steps and pushes;
   - `r2`: logo lockup, then a whip to a real capture in the fixed frame on its washed clone;
   - `r4`, `r6`, `r9`: product windows where only the inner camera moves;
   - `cta`: the transparent comment card (CTA style A); `cta_pill.html`: the comment pill (CTA style B);
   - `motion/*.html`: one demo per motion component (cursor, glass, morph, flood + iris, maskrise, kinetic, wall, whip; explain-flow, explain-callout, explain-status, explain-loop); see "Motion components" and "Explainer components" below.

How the engine works and the rules that matter:
- `E.run(id, dur, render)` registers one paused timeline. `render(t)` must be a pure function of t.
- `E.path` gives the world-camera keyframes. `E.camera` applies them and blurs the viewport along screen velocity (σ = 0.29·v·0.75/60, ≤ 40 px, zero at rest and at t = 0).
- `E.track` and `E.land` animate per-object props (opacity, x, y, scale, blur). Depth of field: neighbours up to 14 px blur and 70% opacity; the old hero 9 px and 40%.
- Camera moves:
  - glide: sine.inOut, scale change ≤ 0.04;
  - step: 0.5 s power3.inOut, starting 0.25 s before the word that names the next item;
  - push: 1.2–2 s power2.inOut, up to about 1.6×;
  - pull back: 1–2 s;
  - whip: at most one per run, 0.45 s out power3.in, 0.6 s in power3.out.
- Frame 0 is the landing state, sharp, with the camera at rest.
- While a product window is the subject, only the camera *inside* the window moves (1.15–1.4×, 0.4–0.7 s power2.inOut).
- Content zones:
  - splits keep content in y 40–900, and the world fades out from y 900;
  - visuals keep content above y 1230;
  - on frame 0 the intro graphic stays below y 620 (the cover sits above it).
- Visual style:
  - one sparse subject per scene;
  - Poppins and nothing under 30 px;
  - near-white radial ground and the three-layer shadow;
  - nothing dark, no grid;
  - animate the action, never label it.
- Every visible sound-worthy event goes in the composition's `<script type="application/json" id="events">` (pop / click / chime / thud for icons landing / flash for white flashes / whoosh at the whip midpoint / keys / ticks, run-relative). The audio step reads these, so SFX always land on their visuals.
- `bash $S/render_gfx.sh draft r1 r2 …` then **look at every contact sheet**. When they're right, run `bash $S/render_gfx.sh final …` (240 fps → `tmix=frames=3,fps=60`) and `bash $S/render_gfx.sh cta`. Render one at a time on 8 GB machines.

#### Motion components (`assets/motion/`)
Reusable techniques from the motion library, built on the engine and pure functions of t like it. Copy `assets/motion/` next to `engine.js`, then load `motion/core.js` (springs, expo easing, `E.rect`, `E.accent`) followed by the files you need. Each one has a working demo in `references/examples/motion/<name>.html` (1080×1920, house style); start from the demo.

| Component | File | Use it for | Library refs |
|---|---|---|---|
| `E.cursorEl` / `E.cursorAt(t, keys, {hover, press})` / `E.cursorApply`: macOS arrow, expo.out glides, leans toward its heading, 1.5× on hover, −15% on press | `cursor.js` | a cursor driving clicks in rebuilt UI (put a `click` event on each press) | product-sting-frame-exact, product-showreel-throughline |
| `E.glassBox(root, {source})` → `g.mirror()`, `g.render(g.springOut(t, t0, point, rect))`: frosted panel (blurred, lightened clone of the scene behind) with a bright top rim, springing out of a point | `glass.js` | a prompt box, toolbar or panel over a coloured scene | launch-film-one-take-glass, product-sting-frame-exact |
| `E.morphShape(parent, states)` → `m.render(t)`: one shape morphing chip → bubble → card → pill (size, radius, position and colour spring; text swaps inside its own mask, never overlapping) | `morph.js` | a status that changes (found → 62% → drafted → sent ✓) as one object instead of cuts | launch-film-one-take-glass, showreel-everything-transforms |
| `E.floodAt(t, {from, t0, t1, to})` + `E.rect`: an element floods past all four corners in 0.3 s, then contracts into the next element; `E.irisEl` / `E.irisAt` / `E.irisRender`: six blades close on a hexagonal aperture and snap open | `flood.js` | a scene change *inside* a graphic run (swap the scene while covered) | launch-film-one-take-glass |
| `E.maskLines(el, lines)` + `E.maskRiseAt(spans, t, {tin, tout})`: lines rise out of a mask line; outgoing and incoming blocks get separate timing | `text.js` | a headline or claim set in type | showreel-everything-transforms, launch-film-one-take-glass |
| `E.kineticNumber(el, t, {t0, to, suffix, origin})`: a number counts (expo.out) while it grows out of a point on a spring | `text.js` | a figure the speaker says ("62%") | showreel-everything-transforms |
| `E.cardWall(root, {cols, rows, card})` → `w.render(t, {cam: E.filmCam(t, shot), wave})`: cards on a gently curved CSS 3D wall, an accent wave tilting each card as it passes, one named film-camera move (`crane`, `dolly`, `orbit`, `push`) | `wall.js` | a hook or payoff full visual showing "many" (leads, customers, results) | gallery-3d-film-camera |
| `E.whip({t0, from, to})` → `{segs, mid}`: the house whip as `E.path` segments (0.45 s power3.in out, 0.6 s power3.out in) with matched velocity at the turnover; `E.camera` adds the directional blur | `whip.js` | the one whip per run; put the `whoosh` event at `mid` | house-luxury-tech, product-sting-frame-exact |

Rules that come with them:
- The house rules still win: near-white ground, nothing dark, nothing under 30 px, one whip per run, frame 0 at rest. Fills default to the video's accent (`var(--clay)` / `E.accent()`), so never hard-code Clay.
- Springs are closed-form (`E.spring`, `E.sp` sums one spring per change), so seeking to any t gives the same frame. Keep the overshoot small (the defaults).
- `glassBox` freezes the source's computed styles onto its clone and needs `g.mirror()` after the scene renders each frame. Keep words the viewer reads on the glass's content layer, sharp, never in the blurred clone.
- Flood, contract and iris are transitions inside one run. Layout changes stay hard cuts.

#### Explainer components (`assets/motion/explain.js` + `explain.css`)
Pictures instead of text, taken from the creator's reference edit: product logos and icons popping in, arrows and callouts. Load `motion/core.js`, then `explain.js`, and link `explain.css`. Demos: `references/examples/motion/explain-*.html`.

| Component | Use it for |
|---|---|
| `E.iconTile(parent, icon, label, {hero, svg})` + `E.iconPop(el, t, t0, {rot})`: a tile arrives tilted and small and springs upright (scale 0.8→1, −14°→0, small overshoot). Put the product's official logo in `svg` for the hero tile | a pipeline told as logos: research → Claude → cold email (`pop` event on each tile) |
| `E.arrowEl(parent, len, 'right'/'down')` + `E.arrowDraw(el, t, t0)`: an accent arrow that draws in the direction of flow | joining tiles, steps or cards |
| `E.callout(box, label, t, t0)` with `.xp-callout-box` / `.xp-callout-label`: an accent outline wipes onto one line of a real capture, then a label arrow slides in ("← WHAT YOU SELL") | pointing at the exact line or field the speaker means |
| `.xp-chip` (`.step` for numbered "01 · FIND LEADS", `.accent` for a highlighted tag) + `E.chipPop(el, t, t0)` | numbered steps next to the rows they mark; tag chips under a product title ("Open source", "MIT license", "$0 · free") |
| `.xp-card` (+ `.accent`) with `E.icon(...)`, landed with `E.land` | stacked status cards ("Reply received", "Sales pipeline"), and an accent goal card ("Meeting booked") with a `chime` |
| `E.stageTimeline(parent, labels)` + `E.stageAt(el, t, [[t, stage], ...])`: stage dots on a line, a progress dot springing stage to stage | a pipeline advancing (outreach → won) |
| `E.loopDiagram(parent, labels, r)` + `E.loopAt(el, t, t0, lap)`: labels round a dashed ring with a device in the middle and a dot travelling the loop | anything that repeats ("every 15 minutes", "24/7") |
| `E.ctaPill(parent, keyword, chipHtml)` + `E.ctaPillAt(el, t, t0, typeAt)`: CTA style B, see below | the outro CTA |

#### CTA style (one per video, alternate between videos)
Set `"cta_style": "box"` or `"pill"` in project.json and say which one in the storyboard.
- `box` (style A): `references/examples/cta.html`, a comment box with an avatar, the keyword typed with a caret, and a Post press.
- `pill` (style B): copy `references/examples/cta_pill.html` to `work/gfx/compositions/cta.html`. A big accent pill with a comment icon, `Comment “KEYWORD”` typed in capitals, then a white chip saying where to get it (e.g. GitHub icon + "Free on GitHub · owner/repo"). Set the timings from the CTA line's words in `plan.py`.

### 9. Camera track and mattes
1. `$PY $S/camtrack.py work/cam1080.mp4` writes the frame-exact 60 fps cut (cover-fit full cam, plus `camwide.mp4` for 16:9 split footage) and prints a check that every join shows the new take from its first frame.
2. `$PY $S/matte.py` handles background removal per split run, unique source frames only, keyed by source frame. The head and card therefore come from the same frame even after retiming. For a portrait source the split geometry is derived. The default `"split": {"mode": "fit"}` puts the footage at 0.72 scale with the head clear of y 900, and makes the camera card exactly as wide as the footage (it bleeds off the bottom only), so the card is always real footage edge to edge. `"mode": "cover"` puts full-width footage behind a card that bleeds off both sides like the 16:9 layout. The head is then bigger (top near y 760), so split graphics must keep their content above about y 720. `assemble.py` refuses to render if any part of the card isn't covered by footage. Never fill the card with blurred or stretched copies. Tune `"scale"`/`"y"` if the framing differs, and check that the head clears the graphics.

### 10. Audio
1. `$PY $S/audio.py` writes:
   - voice normalized to −14 LUFS;
   - SFX in the creator's measured style (`references/sound-profile.md`, `"sfx_profile": "creator"`, the default). These are the composition events plus an automatic swoosh peaking on every cut into a graphic and a sub boom on every cut back to the speaker. Peaks relative to the voice peak: ticks −21, pops −22, thuds −19, clicks −21, chimes −13, swooshes and whip whooshes −14, sub booms −8, keys/ticks −24 dB. `"sfx_profile": "house"` restores the original quieter, cut-free palette;
   - a 2.6 s riser whose audible end lands exactly on the hook join (−14 dB);
   - music per `"music": {"mode": ...}`: `"file"` is the creator's own copyright-free track (ask for it; it's looped or trimmed to END, one flat level at `"lufs"`, default −24, 800 ms fade); `"none"` means no bed, as in the creator's AI Iceberg edit; `"synth"` is the code-composed 110 BPM warm bed (default when nothing is given).
2. `$PY $S/master.py` sums the stems, applies a look-ahead true-peak limiter only where needed (≤ −1 dBTP), and measures every stem and the master.

### 11. Assemble and QA (look at real frames; don't assume)
1. Spot-check first with `$PY $S/assemble.py 0,240,1300,…`, looking at `work/qa/*.png` for the cover, head and card alignment, and caption positions. Then run the full `$PY $S/assemble.py`, which writes `final.mp4` and runs about 15 min.
2. QA list:
   - frames on both sides of every join;
   - head present on the first frame of every split and aligned on fast moves;
   - a contact sheet of the whole video (`fps=2,tile=12x9`): captions clear of face and visuals, heroes only where the speaker is alone (never two in a row), hero colour matching the clothes and readable, zones, nothing dark, frame 0 a clean cover;
   - `ffprobe` shows 1080×1920 / 60 / 3,226-ish frames, AAC 48 k stereo;
   - `ebur128` on the final;
   - riser end, whip-whoosh and transition-swoosh peaks, sub booms on the cuts back to the speaker, and join gaps from the stems.
3. Fix, re-export, and repeat until everything passes.

### 12. Report
Write `edit/REPORT.md` with the structure of `references/example-report.md`:
1. END in ms;
2. the runs table;
3. take choices: single-take lines, swaps, and what the other takes said;
4. what each graphic shows and why;
5. facts checked and against what;
6. the SFX list with times;
7. LUFS and true peak per stem and for the master;
8. everything rebuilt, assumed or worth double-checking, plus inputs that were missing.

Lead with anything that changes how the user should read the result (for example, no clean audio file, or an unverified claim).
