# Harvey short: edit report

**Deliverables**
- `edit/final.mp4`: 1080×1920, 60 fps, H.264 High (CRF 14), AAC 48 kHz stereo 320 kb/s, 3,226 frames.
- `edit/stems/voice.wav`, `sfx.wav`, `riser.wav`, `music.wav`: 48 kHz, 24-bit, each exactly END long.

**END = 53,767 ms** (53.767 s, frame 3,226 at 60 fps). Every layer ends on END: voice, all stems, the picture and the CTA card.

---

## 0. Read this first: inputs and the judgement calls that follow from them

1. **There was no separate clean-audio file.** The folder only had `RAW.MP4`, which is 4K, 29.97 fps, with dual-mono 48 kHz PCM. Its noise floor is about −79 dBFS, so it is clearly a wireless lav recorded into the camera. Because the brief said not to stop, I used that track as the "clean audio".
   - The sync step was trivial: I cross-correlated L against R at 16 kHz and got lag 0, with the peak 20.8× above the next-highest peak.
   - The source has **259 clipped samples** at 0 dBFS, which are baked into the voice.
   - If you do have a separate clean recording, drop it in and I can re-sync and redo the cut.
2. **The camera footage is portrait**, not landscape. It is 3840×2160 with a −90° rotation flag, so it plays as 2160×3840.
   - **Full cam** is the frame scaled to 1080×1920, with no crop or zoom.
   - **The split geometry had to be derived for portrait** (see section 4). At scale 1.0 your head would fill the whole graphic zone. I used scale 0.72: the footage is 778×1382 at x 151, y 538. That puts the top of your head at about y 912, so it is clear of the graphic zone (content ends at y 900), and the chin sits just inside the card.
   - Because 778 px of footage is narrower than the card, the strips at the card's sides are filled with a blurred, 18%-darkened, enlarged copy of the same frame, feathered over 70 px.
   - **Split captions moved.** In this portrait layout the 941–1114 gap is where your face is, so split captions sit on the card over your torso, centred at y 1660.
   - **Outro captions moved too.** Centring them at y 1171 put them on your chin, so they are centred at y 1262. That is still inside the 1037–1306 zone and clears the CTA box, which starts at y 1344.
3. **The cover title was empty**, so I wrote one from the hook: "Free AI agent / gets customers". It is Poppins Bold 110 in a white box at x 50, y 262, 980×341, radius 30, shown on frame 0 only.

## 1. Sync and transcription
- Transcription used faster-whisper medium.en with word timestamps, run in a local venv. `hyperframes transcribe` (whisper.cpp) also ran, but its word timings were interpolated and too coarse to cut on.
- Every word edge was then refined against a 10 ms RMS envelope.
- Fixes to the transcript text:
  - "Clod" → Claude
  - "Mac" → **Max** (Claude Pro or Max)
  - "of it" → "of a fit"
  - "techwithnamdini" → techwithnandini.ai

## 2. The cut: takes and swaps

| Line | Kept (source s) | Other takes / what was removed |
|---|---|---|
| Hook: "Someone just built a Claude Code agent… customers." | 4.20–7.90 | single take; 4.2 s of dead air and pre-roll noise removed |
| "It's called Harvey… Harvey Specter from Suits." | 7.90–11.48 | single take |
| "It's completely free and open source." | 11.65–13.56 | single take |
| "You just have to give it your website… ideal customer." | 13.81–19.88 | single take (two internal pauses of about 270 ms cut to 120 ms) |
| "Then Harvey goes out and finds leads… fit they are." | 20.27–25.54 | single take |
| "After that, Claude writes a personalized cold email **for every prospect using something specific about their business**." | 29.71–35.26 (**take 2, the last**) | Take 1 (26.30–28.68) stopped at "…cold email." and was an incomplete restart, so it was dropped |
| "When people reply, Harvey reads the reply… towards a meeting." | 35.67–43.64 | single take (three pauses of 260–290 ms cut to 120 ms) |
| "It runs in a loop… live dashboard." | 44.45–49.27 | single take; 2.0 s pause after it removed |
| "And the best part? It runs on your Claude Pro or Max subscription… no extra AI bill for you." | 51.26–56.51 | single take |
| "It even keeps an eye on your usage so you still have some room for your own Claude work." | 67.86–71.93 (**take 5, the last**) | Takes 1–4 dropped: "…so you have," / "…on your usage. So you," / "it even keeps an eye on," ×2. All were restarts. |
| CTA: "Comment Harvey and I'll DM you the GitHub repo and don't forget to follow techwithnandini.ai" | 78.42–83.14 (**take 3, the last**) | Take 1 "Comment Harvey and I'll DM you the GitHub," (cut off), then a muttered "comment, comment Harvey and," restart. Both dropped, along with the 6 s tail (Whisper hallucinated "Thank you" in the silence). |

**Swaps (earlier take used instead of the last): none.** Every kept line is the last complete take, and none had an audible defect in the words on the waveform/transcript check.

Cut mechanics:
- 40 ms lead-in before the first word.
- Pauses over 250 ms are cut to 120 ms.
- True ends use the −35 dB / −32 dB-for-150 ms rule on 10 ms RMS windows.
- Audio J-cut: each line's audio starts 50 ms before its picture cut.
- Tails fade within the gap, and never past the next onset.
- Measured quiet at the 13 joins: 120–130 ms. One join, into "Harvey reads", measured 160 ms on the first pass. I fixed it by overlapping two frames more (33 ms), not by adding silence.
- Join check: at every picture cut, the new take's first frame is exactly the expected first source frame, and the old take holds up to its last frame. All 13 were checked on frames.

## 3. Eye contact
I sampled 8 frames per kept segment across all 14 segments. You are on-lens in every kept take, including the head tilts at 47.2 s and 69.6 s. No run had to be forced to a full visual.

## 4. Layout runs (tile [0, END])

| Run | ms | Layout | What it shows |
|---|---|---|---|
| R1 hook | 0–3867 | split | Claude logo lockup large, then a step to the **Claude desktop app (Code tab)** streaming Harvey's own `harvey run` output (41 businesses / 12 scored against your ICP / 12 emails waiting) |
| R2 | 3867–9500 | full visual | Harvey's real logo lockup ("H" mark, *Always Be Closing*), then the run's one **whip** to the **real GitHub repo page** (captured headless) in the fixed frame on its washed clone. The inner camera pushes onto "MIT license", which gets a highlight band. |
| R3 | 9500–15433 | split | URL card typing `yoursite.com`, then a step to Harvey's `harvey.yaml` card filling `product / pricing / icp` (Harvey's real config keys) as each word is said |
| R4 | 15433–20817 | full visual | Harvey dashboard **Companies** (rebuilt): 4 Portland businesses stream in, one expands with researched signals, then 1–10 ICP scores fill |
| R5 | 20817–26483 | split | The **real Outbox email** from Harvey's dashboard capture ("Rose City and the map pack", "Ruben — your site has no schema markup…") being written, with a push and a highlight on the specific detail |
| R6 | 26483–34133 | full visual | Harvey **Conversations**: the reply lands and is read, `intent: objection` is classified, Harvey's response streams, then "Meeting booked · Thu 10:00 AM" ✓ |
| R7 | 34133–39083 | split | README's own `harvey run` loop output, then a step to the live **Today** dashboard (counts tick up, pulsing online dot) |
| R8 | 39083–44450 | full cam | "And the best part…" is an opinion/benefit line |
| R9 | 44450–48633 | full visual | Harvey **Usage** (rebuilt): Claude Max quota meter fills to 62% against the 80% cap; the 20% headroom lights up; `max_daily_claude_percent: 80` |
| R10 outro | 48633–53767 | full cam + CTA | Comment box: default avatar, "Harvey" typed with blinking caret, Post press |

- No run is longer than 7.65 s.
- No two neighbouring runs share a layout, and all three layouts are used.
- The hook is a split and the outro is full cam.
- Each run boundary sits exactly on a picture cut, except R1/R2, which is inside one continuous take.

**Why these graphics:**
- Everything Harvey shows is its real UI, rebuilt from the repo's own `docs/dashboard.gif` capture: the cream #F8F7F6 page, serif headings, mono labels, the H mark and the real company/email copy.
- Rebuilding was needed for crisp text at 30 px or larger: the GIF is only 900×559.
- I chose the GitHub page for "free and open source" because that claim is a fact with a real source.

## 5. Facts checked

| Claim in the video | Sources | Result |
|---|---|---|
| Harvey is a Claude Code agent that finds prospects, writes cold email, handles replies and books meetings | GitHub repo `ethanplusai/harvey` (README and API description); TomeVault listing | ✔ |
| "Completely free and open source" | GitHub API (license **MIT**); README "License: MIT"; TomeVault "Free · MIT" | ✔ |
| "Give it your website and it trains itself on product, pricing, ideal customer" | README `harvey train <url>`, `product: {…pricing…}`, `icp: {…}` | ✔ |
| "Scores how good of a fit" | README: ICP scoring 1–10; the "scout" stage | ✔ |
| "Runs in a loop on your computer or a server" | README: heartbeat loop every 15 min, "runs on your machine"; Dockerfile and docker-compose in the repo (server) | ✔ The server part is inferred from the Docker files |
| "Live dashboard" | README: `harvey dashboard` at localhost:5555 | ✔ |
| "Runs on your Claude Pro or Max subscription, no extra AI bill" | README; repo description; TomeVault | ✔ README also says it can use a ChatGPT/Codex plan instead |
| "Keeps an eye on your usage so you still have room for your own Claude work" | README: "reads the active provider's subscription quota and throttles to leave headroom", `max_daily_claude_percent: 80` | ✔ |
| **"Named after Harvey Specter from Suits"** | **Not confirmed anywhere.** The README never mentions Suits. Its tagline "Always Be Closing" fits the theme, but that is not proof. | ⚠ **Please double-check.** The graphic does not claim it. |

Repo stats as captured (14 Oct 2026): 556 stars, 105 forks, MIT license, v0.3.0.

## 6. SFX (one sound per visible event; times are on the final timeline)

| t (s) | Run | Sound | Visual event |
|---|---|---|---|
| 1.750 | R1 | soft pop | Claude app window lands |
| 1.95–3.60 | R1 | tick stream (30 ticks) | agent output streams |
| **7.617** | R2 | **whoosh v1, loudest exactly at the whip midpoint** | the run's one whip (logo → repo page) |
| 9.80–10.65 | R3 | 12 key presses | `yoursite.com` typed |
| 11.550 | R3 | soft pop | harvey.yaml card lands |
| 12.45 / 13.22 / 14.26 | R3 | tick streams | config lines fill |
| 16.69 / 18.05 / 19.15 | R4 | tick streams | companies, signals, scores stream in |
| 21.61–24.32 | R5 | tick stream (49 ticks) | Claude writes the email |
| 26.983 | R6 | soft pop | reply bubble lands |
| 30.68 / 31.57 | R6 | tick streams | intent tag, response streams |
| 33.753 | R6 | two-note chime | "Meeting booked" confirmation |
| 34.25–36.53 | R7 | tick stream | loop output |
| 37.133 | R7 | soft pop | dashboard card lands |
| 49.05–49.55 | R10 | 6 key presses | "Harvey" typed |
| 49.953 | R10 | soft bubbly click | Post button press |

- Nothing plays on layout cuts, steps, pushes or glides.
- Levels, measured as peak relative to the voice's peak: pops, clicks and chimes −10 dB; whoosh −9 dB; keys and ticks −16 dB (ticks vary from −16 to −19).
- **Riser:** it is audible from 1.306 s and its audible end lands at **3.867 s**, exactly on the hook → R2 join. Its peak is **−14.0 dB** relative to the voice.
- **Music:** original 110 BPM warm minimal bed (Dm9–B♭maj9–Fmaj7–C6 pads, sub bass, soft kick/rim/hats, sparse chord-tone plucks, no lead). Beat 1 is on sample 1, with a 5 ms declick, one flat level throughout and an 800 ms fade ending on END.

## 7. Loudness (ffmpeg ebur128)

| Stem | Integrated | True peak |
|---|---|---|
| voice | **−14.0 LUFS** | +0.3 dBTP |
| sfx | −29.3 LUFS | −10.0 dBTP |
| riser | −25.6 LUFS | −15.0 dBTP |
| music | **−24.0 LUFS** (10.0 LU under the voice) | −11.0 dBTP |
| **master** | **−13.7 LUFS** | **−1.3 dBTP** |

- The master is the plain sum of the four stems, then a look-ahead true-peak limiter. The limiter has a 5 ms look-ahead and 120 ms release, with no make-up gain.
- It was needed because the −14 LUFS voice alone peaks at +0.3 dBTP. It only touches voice peaks: at most −2.2 dB, with no pumping or clipping.

## 8. Motion and render
- Every graphic is a HyperFrames composition, one per run, and each one's duration equals its run.
- Each was rendered at 240 fps, then `tmix=frames=3,fps=60`.
- Camera viewport blur follows screen velocity (σ = 0.29·v·0.75/60, capped at 40 px, axis-separable) and is zero at rest. I checked frame 0 and the rest frames: they are sharp.
- The head matte is HyperFrames `remove-background` (u2net human-seg), taken from the **same cut-track frame** as the card on every frame. Matching is by source-frame index, so the head and card cannot drift apart. The matte is feathered 40 px into the card's top edge.

## 9. Things to double-check or that I couldn't do exactly
- **Clean audio file missing.** I used the camera's lav track (see section 0).
- **Harvey Specter naming** is unverified (see section 5).
- **Rebuilt UIs:**
  - Claude desktop app (R1): rebuilt from memory of the public app UI, because it can't be captured headlessly.
  - Harvey Companies, Conversations, Today and Usage views (R4, R6, R7, R9): rebuilt from the repo's dashboard GIF and README. The Usage page isn't shown in the GIF, so its layout is my reconstruction of the documented behaviour.
  - Example companies, emails and counts come from Harvey's own demo capture and README. The Ruben reply/response and the Usage percentages are illustrative.
- **Instrument Serif** only ships Regular and Italic, so the "bold italic" highlights use libass faux-bold.
- **R6 composition length:** it was rendered 33 ms longer (7.684 s) before I tightened one join. The extra 2 static frames are simply not used, so the run still matches its 7.650 s length.
- **u2net matte at 540×960:** for R3/R5/R7 the matte was computed at that size on the unique source frames, then upscaled. This only affects hair edges, and on fast hand moves the matte can soften fingers slightly.
