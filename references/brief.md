# The house brief (the standard every short must meet)

This is the full original brief the pipeline was built against. SKILL.md summarises it; read this file when a rule's exact number matters.

You're editing my raw talking-head recording into a finished, ready-to-post 9:16 short (Instagram Reel, TikTok, YouTube Short). Do all of it yourself, end to end, in code: ffmpeg, Python, Node and HyperFrames (npx --yes hyperframes). No video editor app. Every sound effect and the music are synthesized by you in code; there are no audio files to use. You may install what you need locally inside this project (npm packages in the project folder, pip into a local venv), without asking. Never install system-wide software.

WORK FULLY AUTONOMOUSLY
- Don't ask me anything after this message. Run every step start to finish and finish with final.mp4 exported.
- Every judgement call (which take, layout choices, a fact that disagrees with its sources, a product UI you can't capture) is yours: make the best call, keep going, and log it in the report.
- If something fails, try another way (a different tool, method or fallback) rather than stopping. A missing tool is not a reason to stop: install it locally or use an alternative.
- If a real product UI is behind a login, rebuild it from public screenshots or docs and note it in the report.
- If the cover title field is empty, write one from the hook yourself.
- Only stop early if the input files are missing or unreadable.

INPUTS
- Camera video: in this project folder
- Clean audio: in this project folder
- Cover title (frame 0): you come up with one

DELIVERABLES (in a new folder edit/)
- final.mp4: 1080x1920, 60 fps, H.264 high quality, AAC 48 kHz stereo
- stems/voice.wav, stems/sfx.wav, stems/riser.wav, stems/music.wav (all full length, so I can remix)
- A short report (see the end)

1. SYNC AND TRANSCRIBE
- Cross-correlate the camera audio and the clean audio at 16 kHz mono to find the offset (confirm it with a clear correlation peak). Use only the clean audio from here on; the camera audio is discarded.
- Transcribe the clean audio with word-level timestamps (hyperframes transcribe or whisper). Group the words into takes.

2. THE CUT
- This is a raw, unedited recording. Remove everything that isn't the final delivery: extra spaces, repeated sentences, pauses, awkward silences, retakes, false starts and any dead air at the start and end. The finished cut should play as one clean, continuous take.
- I re-record lines until I'm happy, so keep the LAST complete take of every line. Use an earlier take only if the last one has an audible defect in the words (stutter, clipped or wrong word, restart mid-sentence). List every swap in the report.
- Remove restarts, self-corrections, "okay", stray syllables and muttered comments after a take.
- Leave 40 ms before the first word. Any quiet stretch over ~250 ms inside or between lines is cut down to ~120 ms. Natural short pauses stay.
- A line's end is its measured true end, not the transcript's word end: the last 10 ms RMS window at or above -35 dB. If it stays under -32 dB for more than ~150 ms, the true end is earlier: cut there.
- Picture cuts are hard cuts, exactly on the join. No zooms, punch-ins or moves on my footage, ever.
- The J-cut is in the AUDIO only: each line's audio starts 50 ms before its picture cut. A line's tail holds at full level until it decays to the noise floor, then fades over 170 ms, but never runs past the start of the next sound. No join may have a quiet stretch over 150 ms. Fix a bad join by cutting earlier or overlapping more, never by adding silence.
- END = the last frame of the voice track. Every layer ends exactly on END.

3. EYE CONTACT
Sample about 8 frames per kept take (then 100 ms steps around any head turn) and look at them. My camera shows only while I'm looking at the lens. If I look away mid-line, the camera hides from the last on-lens frame: split the run at the nearest word boundary before the turn and make the rest a full visual. A take read off to the side the whole way through is a full visual.

4. THE THREE LAYOUTS
Canvas 1080x1920. Every short rotates through all three, with hard cuts on the joins:
a) Full cam: my footage cover-fitted (the centre slice of a landscape source).
b) Split, cam at the bottom with my head popping out: a full-frame 1080x1920 graphic sits behind everything, with its content in y 40-900 (the main element's bottom edge at 880-900). On top of it goes a rounded camera card, 1210x864 at x -65, y 1200, corner radius 200 (squircle), bleeding off the left, right and bottom edges. For a 16:9 source, scale the footage to 1890x1063 and place it at x -405, y 1008. The card shows that footage through its window, and ABOVE the card's top edge only my matted head and shoulders show: the same scaled footage with a background-removal alpha matte (hyperframes remove-background or an equivalent), feathered 40 px at the card's top edge, pixel-aligned with the card so the head never tears from the body when I move. The matte and the card must come from the same source frame on every frame; verify this on fast head moves. For a portrait source, derive the same geometry and check that the head clears the card. The card must show only real footage, never blurred, stretched or mirrored fill at its sides: either make the card exactly as wide as the scaled footage (default), or scale the footage to the full width and keep the split graphics higher.
c) Full visual: a full-frame graphic.
Rules:
- The hook (first sentence) is always the split. The outro (the CTA line onwards) is always full cam. Direct-to-camera lines with nothing to show (opinions, reactions, personal stories) are full cam. Screen recordings, news pages and product UI that needs zooming inside it are full visuals. A single screenshot, a card, a logo row or a short list is the split.
- No run over ~8 s, two runs in a row never share a layout, and all three layouts are used.
- Write the plan as runs tiling [0, END] before building any graphic.

4b. STORYBOARD AND BEAT TABLE (then STOP for my approval)
- Before building or rendering any graphic, give me a storyboard and a beat table so I can see exactly how you plan the edit.
- Storyboard: one 9:16 sketch per run showing the layout (cam / split / visual), my frame at that moment, what the graphic shows, and where and in which style the captions sit (pill or hero).
- Beat table: every beat with its time range, run, layout, the exact words, what's on screen and what it's doing, the camera move, SFX, caption style (name every hero moment), the motion reference(s) from the library it draws on, and the source (real capture, rebuilt UI, logo).
- Deliver it as one page I can open, then wait. Don't render anything until I approve or ask for changes; apply my changes and show it again.

5. GRAPHICS (HyperFrames, one composition per run; use parallel subagents if you have them)
- Follow the motion library (references/motion-library.md): match the look and motion of the references I've picked; each storyboard beat names the reference it draws on.
The style is luxury tech: one bright world of floating white cards, and a camera that moves through it.
- Ground: a radial near-white fill (#FFFFFF at 50%/36%, falling to #F3F3F0 at the edges). No grid, no orbs, nothing dark anywhere.
- Every object off the ground carries one three-layer shadow: 0 60px 120px rgba(24,24,32,.16), 0 24px 48px rgba(24,24,32,.10), 0 4px 10px rgba(24,24,32,.06). Radii: media cards 3% of the width, docs 40, tiles 72, phones 84.
- Type: Poppins throughout. Headline 96/700, subhead 52/700, body 30/400; nothing under 30 px. Ink #111111. Accent Clay #D97757 for fills, #B25730 for Clay text on white, highlight band #FBEEE8, green #34C759 for checks, red #FF3B30 for stamps.
- A world camera moves over the cards: a glide (sine.inOut, scale change 0.04 at most), a step to the next item (0.5 s power3.inOut, starting 0.25 s before the word that names it), a push onto the card being talked about (1.2-2 s power2.inOut, up to ~1.6x), a pull back to reveal the bigger picture (1-2 s), and at most ONE whip per run (0.45 s out power3.in, 0.6 s in power3.out). Frame 0 of every run is the landing state, sharp, with the camera at rest.
- Depth of field: the card being read is in focus; neighbours blur up to 14 px and dim 30% as the camera pushes. A new hero sends the old one back to a 9 px blur at 40% opacity. Never blur a word the viewer needs to read.
- Motion blur: blur the camera viewport along its screen velocity on every frame (sigma = 0.29 x speed x 0.75/60, capped at 40 px). Render at 240 fps and blend 3 of every 4 frames down to 60 fps (ffmpeg tmix=frames=3,fps=60). Blur only mid-move; a blurred frame at rest is a bug.
- Animate the action, never label it: no label pills, step chips or word rows restating the narration. A named product is its REAL UI, rebuilt from a real capture (hyperframes capture or a headless screenshot) and doing the action: typing, streaming, clicking. While a product window is the subject, only a camera INSIDE the window moves (1.15-1.4x, 0.4-0.7 s power2.inOut); the world camera holds still. Named-product intro: its official logo large and centred first, then the UI.
- "Claude Code" means the Claude desktop app UI, never a terminal, unless I'm talking about the terminal.
- Anything that HAPPENED (a release, a quote, a number, a headline) shows its real source page. Check every figure I say against two or more reputable sources and report any disagreement. A real capture sits sharp in a fixed frame (x 24, y 200, 1032x1040, radius 36, white, shadowed) on a blurred, enlarged, WASHED near-white clone of itself (blur 40px, saturate .7, brightness 1.05, a 72% white wash over it) that moves with the footage. The frame never moves; the footage pans and zooms inside it.
- Full visuals keep content above y 1230 (main element's bottom edge at 1200-1230). Splits keep it in y 40-900 and fade the world out from y 900 over 160 px.
- Keep every scene sparse: one dominant subject, at most one supporting cue, smooth eased motion, never frantic.
- Duration of each composition = its run exactly. Check each render with a contact sheet before using it.

6. COVER, CAPTIONS, CTA
- Cover: frame 0 only. My title in Poppins bold 110, black on a white rounded box (radius ~2.8%, soft shadow), centred at y 0.13 (about y 262-603 for two lines, ~50 px side padding). On frame 0 the intro graphic keeps everything below y 620.
- Captions burned in from the FINAL voice track's word timings, starting at 17 ms (frame 0 stays clean). Two styles:
  - PILL (the default, whenever I'm talking over visuals or B-roll): 1-3 words, Poppins bold ~64, white with a soft drop shadow, on a translucent dark rounded box (about 55% black, radius ~18). Small and calm; it must never compete with the visual.
  - HERO (mostly in the hook, and on important lines when only I am on screen with no B-roll): a stacked moment of 2-5 words, e.g. "everybody / WANTED TO / know". The small words above and below are the same pill style as the PILL captions (top pill tucked over the big word's top-left, bottom pill under its bottom-right). The one or two HUGE words in the middle are a heavy sans (Archivo Black, uppercase, up to ~1000 px wide) in a SOLID colour matched to the clothes I'm wearing in that video: sampled from my torso, ignoring hair, skin and background, then lifted bright enough to read. They have a thin outline in a deep shade of the same colour and a soft shadow, so they still read over the clothes they match. The big word lands with a short scale-settle; the pills fade in just after. Each video therefore gets its own accent colour.
  - Never two hero moments in a row; never put a hero over a visual. Choose hero words that carry the meaning (the claim, the number, the benefit), never function words.
- Caption position per run, never on my face, the card edge or a visual: pills in the split = centred in the gap, y 941-1114 (for a portrait source this gap is my face: use the card over my torso instead); full cam and most visuals = bottom, y 1267-1536; a visual with low content = top, y 365-634; outro = centre, y 1037-1306 (keep it off my chin and above the CTA box). Hero blocks sit over my chest on full cam (centre about y 1380) or on the card in a split.
- CTA card, outro only, lower third (box 43, 1344, 994x276): one centred comment box on a transparent canvas, a default avatar, the keyword from my CTA line typed with a blinking caret, then a Post button press. Nothing else: no panel, no background, no "DM me", no platform text.

7. AUDIO: SYNTHESIZE EVERYTHING, THEN MIX TO THESE LEVELS
Synthesize with numpy/scipy, or the Web Audio API rendered offline with OfflineAudioContext. Clean, modern and premium, never cartoony.
- Voice (stems/voice.wav): the J-cut track from step 2, loudness-normalized to -14 LUFS integrated.
- SFX (stems/sfx.wav), one sound per meaningful VISIBLE event only:
  - a soft bubbly click on real button presses and taps
  - a short soft key press on typing (a light tick stream for longer typing or data streaming)
  - a dull soft pop on a card, tile or device landing
  - a gentle two-note notification chime on an answer, modal or confirmation
  - a LOW, airy whoosh (filtered noise) whose loudest moment lands exactly on the midpoint of each whip, and only on whips: at most one per run, three per short. Rotate 3-4 variants so no two in a row repeat.
  - Nothing on layout cuts, camera steps, pushes, glides or zooms. A logo lockup and any CTA under it get a whoosh or nothing, never a UI sound.
  - Levels, peak against the voice's peak: clicks, pops and chimes -10 dB, whooshes -9 dB, key presses and ticks -16 dB.
- Intro riser (stems/riser.wav): a low, swelling riser, about 2-3 s long, whose audible end lands exactly on the join where the hook ends and the first point starts. It's the one sound allowed to rise into a cut. Peaks 14 dB under the voice.
- Music (stems/music.wav): an original instrumental bed. Modern, minimal, warm electronic, 100-120 BPM, no vocals, no lead melody fighting the voice. Full length, beat 1 on frame 1 (no fade in, only a 5 ms declick), an 800 ms fade out at the end. ONE flat level for the whole video: no ducking, no automation. Set it 10 LU under the voice (about -24 LUFS integrated).
- Master: sum the four stems with no further per-stem changes. Target about -14 LUFS integrated, true peak -1 dBTP at most. A transparent limiter only if a peak goes over; no pumping, no clipping. Measure with ffmpeg ebur128 and report the numbers for each stem and the master.

8. ASSEMBLE AND RENDER
Build the picture from the cut plan: full cam runs from my footage, split runs as the graphic plus the card plus the head, full visual runs as the graphic, then the cover on frame 0, the captions and the CTA card. Render at 1080x1920 60 fps and mux in the master audio. Every layer ends on END: no white frame, frozen head or silent tail.

9. QA BEFORE YOU FINISH (look at real frames, don't assume)
- Frames on both sides of every join: the new take shows from its first frame, the old one up to its last.
- The head and the card stay aligned on fast head moves, and the head is there from the FIRST frame of every split.
- A contact sheet of the whole video: captions clear of my face and the visuals, pill vs hero choices (heroes only in the hook or over me alone, never two in a row), content inside its zones, no grid, nothing dark, frame 0 a clean cover.
- Audio: every SFX lands on its visual event, whooshes only on whip midpoints, the riser ends on the intro join, no join gap over 150 ms, the levels above hit within 0.5 LU.
Fix anything that fails and re-export. Don't hand it back until it passes.

REPORT
END in ms; the layout runs table; take choices (single-take lines, swaps and what the other take said); what each graphic shows and why it was chosen; facts checked and against what; the SFX list with times; each stem's and the master's LUFS and true peak; anything you couldn't do, had to rebuild from public sources, or want me to double-check.
