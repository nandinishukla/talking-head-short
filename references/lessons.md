# Lessons from the first real run (read before you start)

These are the things that actually went wrong or cost time on the first short. Each is cheap to avoid.

## Inputs
- **The "clean audio" file may not exist.** Phone and mirrorless rigs often record the lav straight into the camera. Check the camera track: a noise floor around -75 to -80 dBFS and identical L/R mean it's already the lav. Use it, still run the L/R cross-correlation so the sync step has a number, and say so prominently in the report. Count clipped samples (`analyze_audio.py` does).
- **Check rotation before anything else.** `ffprobe -show_streams` showing `rotation=-90` / `TAG:rotate=90` on a 3840x2160 stream means the picture is really **portrait 2160x3840**. ffmpeg auto-rotates on decode, so a forced `scale=960:540` squashes it. Always scale with `-2` or to the oriented size.
- 4K HEVC/H.264 decode is slow on an 8 GB laptop, about 6 min per pass for 90 s. Decode the camera file **once** into a 1080-wide oriented intermediate (CRF 13, `-g 15`) and use that everywhere.

## Transcript
- `hyperframes transcribe` (whisper.cpp) gives chunk-interpolated word times: fine for reading, useless for cutting. Use `faster-whisper` (`transcribe.py`) with `word_timestamps=True` and an `initial_prompt` naming the product and people.
- Whisper still mishears product names ("Clod", "Mac" for Max, handles). Put fixes in `word_fixes`, and double-check numbers and names against the sources.
- It hallucinates words ("Thank you.") in long trailing silence. Trust the energy envelope, not the transcript, for where speech ends.

## Cut
- Join gaps are measured on the **raw** voice track at -35 dB. A soft breathy onset can make one join read 160 ms even when the gap is 120 ms. Fix it with a negative `gap_overrides` entry for that segment index (one or two frames, e.g. -0.0333), never by adding silence. Every later timestamp shifts by that amount, so update `runs` boundaries after it. `plan.py` prints the new cut points.
- Put run boundaries on picture cuts where you can: a layout change then lands on a real edit. The hook→first-point boundary may sit inside one continuous take; that's fine.

## Portrait split layout
- The brief's split numbers (1890x1063 at -405, 1008) assume 16:9. For a portrait source at scale 1.0 the head is about 460 px tall and covers the graphic zone. Scale about 0.72 (778x1382, centred, bottom on the canvas bottom) puts the head top near y 912 and the chin at the card edge. The card's side strips then need a blurred, darkened, enlarged copy of the same frame, feathered 70 px.
- In that geometry the brief's split caption gap (941-1114) **is the face**. Put split captions on the card over the torso (about y 1660). Also check the outro: at y 1171 captions sat on the chin, so about y 1262 (bottom of the outro zone) cleared it. Always look at a real frame with captions burned in.

## Mattes
- `hyperframes remove-background` runs at about 0.5 s/frame alone but 2-5 s/frame when Chrome renders are running at the same time. **Matte only unique source frames** (a 29.97 source at 60 fps duplicates every frame) at 540 px; u2net is 320 px internally anyway.
- CoreML can die mid-run with "Unable to compute the prediction" under memory pressure. `matte.py` retries on `--device cpu`.
- Key mattes by **source frame index**, not output frame. Then retiming the cut (gap overrides) never misaligns head and card.

## Graphics (HyperFrames)
- Drive every scene from one pure function `render(t)` via a single GSAP tween's `onUpdate` (see `assets/engine.js`). The renderer seeks the timeline, `onUpdate` fires on seek, and the camera velocity for motion blur is computed analytically from `cam(t±1/240)`.
- First run of the headless Chrome can time out ("Chrome cannot start"). Run it once by hand; the second attempt works.
- `-c compositions/x.html` renders a standalone composition file. Asset paths are relative (`../assets/...`).
- **Product windows fill up**: a 1032x1040 window with 30 px UI text looked empty at first. Scale type up (titles 92, rows 40) so the lower third isn't blank.
- **Inner camera pushes crop text.** At 1.3x the visible width is about 794 px; check that the line being talked about stays fully in frame (pad the page or push less).
- A whip whose total travel is much wider than the viewport shows **empty ground at the midpoint**. Keep out-distance about 700 px and size the in-distance so the velocities match at the midpoint (power3.in end speed = 3·d1/0.45; power3.out start speed = 3·d2/0.6). With that, both cards are streaking through the midpoint frame.
- Render drafts at 30 fps and **look at the contact sheet** before the 240 fps render (about 6-10 min per run on 8 GB).
- If you retime the cut after rendering, a graphic can end up a few frames longer than its run. The assembler drops the extra frames, but re-render if the run got shorter by more than a held frame or two.

## Assembly
- Switch runs on **frame indices** (`round(ms/1000*60)`), never `t >= start` in floats: 3.867 s × 60 = 232.02 made the first graphic "run short" by one frame.
- `ffmpeg ... Broken pipe` at the end of assembly is harmless (unused tail frames of a source).
- When polling a background job, `pgrep -f "assemble.py"` matches the polling shell's own command line, so the wait loop never ends. Poll for the output file or the PID instead.

## Captions
- Captions are composited in Python (`assemble.py`), not libass, because the hero style's letters must be filled with the live frame behind them. Pills are pre-rendered PNG layers; the hero big word is a mask filled per frame with the footage enlarged 12%, desaturated 30%, contrast up and washed 62% toward white, over a soft dark shadow. A weaker wash (45%) read grey and muddy over a dark room.
- A translucent pill box nearly disappears over a dark background; that's acceptable (the text keeps its shadow), but check pills over light graphics.
- Strip trailing punctuation from hero big words ("CUSTOMERS." looks wrong at 230 px).

## Storyboard
- Plan captions (pill vs hero) before the storyboard: the sketches show caption style and position, and the beat table lists every hero moment.
- Generate thumbnails from the oriented intermediate through the EDL (out time → source time), not from the camera track: the storyboard comes before the track is built.

## Audio
- A -14 LUFS talking voice peaks around +0.3 dBTP, so the master always needs the true-peak limiter. That's expected; report the max reduction (about 2 dB).
- Put the whoosh by its **measured** loudest sample, not the envelope centre: band-pass filtering shifted the peak 40 ms early.
- Never overwrite `final_master.wav` while an assembly is reading it. Remux afterwards instead: `ffmpeg -i final.mp4 -i final_master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k`.
