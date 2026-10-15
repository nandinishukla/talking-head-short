# Sound profile: measured from the creator's own edit

Source: the creator's "AI Iceberg" short (17.7 s, edited in DaVinci Resolve). The full mix was separated into vocals / drums / bass / other with Demucs (htdemucs), then each effect was detected (spectral flux on the non-vocal stems), classified by duration, low/high-band energy and tonality, and matched to the frame on screen at that moment. `scripts/audio.py` uses these levels by default (`"sfx_profile": "creator"`).

## Music
- **A quiet music bed runs under the whole clip**, about **20 LU below the voice**. I measured it on the stereo image: the voice is mono, but the side channel carries steady content 21.5 dB below the mid (−34.4 LUFS on its own), and the quietest 20 ms windows between words never fall below about −36 dBFS. The noise floor of a dry recording is near −79 dBFS.
- My first pass said "no bed". That was wrong: Demucs folded the soft bed into the vocal stem, so the music stems looked empty. Corrected after a second measurement; the creator confirmed there is music.
- The track itself can't be identified from the clip (no name, voice on top). When the creator supplies it, use `"music": {"mode": "file", "file": "...", "lufs": -34}`. Until then, the code-composed bed (`"mode": "synth"`) at the same quiet level is the stand-in.
- Level rule from this edit: music about **20 LU under the voice (about −34 LUFS)**, much quieter than the original brief's 10 LU, so it sits as texture under dense effects.

## Effects: what plays on what (peak level relative to the voice peak)
| Visual event | Sound | Measured | Level |
|---|---|---|---|
| White / warm flash, hard visual switch | bright tick | ~0.08 s, centroid ~7 kHz | −21 dB |
| Card or graphic lands | pop / tap | ~0.05–0.1 s, centroid 1.3–2.8 kHz | −22 dB |
| Icon / logo pops in (one per icon, e.g. ChatGPT, Claude, Gemini) | soft low thud | ~0.2 s, centroid ~200 Hz | −19 dB |
| Text / state change inside a screen recording | click | ~0.1 s, centroid 5–8 kHz | −21 dB |
| Cut from the speaker into a screen recording / graphic | swoosh with body (rises, peaks on the cut) | 0.6–0.9 s, centroid ~500–800 Hz | −12 to −17 dB |
| Cut back to the speaker / zoom into the main graphic | deep sub boom | 0.3–0.8 s, centroid ~55 Hz | −7 dB |
| A number or stat appears ("90%") | bright chime / shimmer | 0.25–0.35 s, tonal | −12 to −14 dB |

Density: **25 effects in 17.7 s (about 1.4 per second)**. There's a sound on almost every visual change, **including layout cuts**, which the original house brief had banned.

## Event log (creator's clip)
| t (s) | Sound | On screen |
|---|---|---|
| 0.71 | bright tick | white flash after the warm-flash hook frame |
| 1.06 | pop | iceberg graphic card lands |
| 1.90 | thud | element on the iceberg appears |
| 3.85 | click | chatbot icons start popping in |
| 4.82 / 5.04 / 5.42 | pop + thuds | ChatGPT / Claude / Gemini icons land one by one |
| 6.2–7.2 | swoosh (with body) | cut to the white screen-recording layout |
| 8.35 / 9.32 | click / pop | screen-recording text changes |
| 9.58 / 9.91 | thuds | recording content swaps |
| 10.25 | chime | "ya video" (the last recording) |
| 10.85 | sub boom | back to the speaker with the iceberg card |
| 11.50 | click | icon row updates |
| 14.64 + 14.88 | click + chime | "90%" appears |
| 16.0–16.9 | swoosh / boom | full-frame cream flash transition |
| 17.58 | thud | final hit |
