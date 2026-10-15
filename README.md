# talking-head-short

A Claude Code skill that turns a raw talking-head recording into a finished 9:16 short (Reel, TikTok, YouTube Short), entirely in code: ffmpeg, Python, Node and [HyperFrames](https://hyperframes.heygen.com).

What it does:
- syncs and transcribes the recording, keeps the last good take of every line and cuts retakes, pauses and false starts;
- builds a J-cut voice track and checks eye contact;
- rotates through three layouts: full cam, a split with your head popping out of a camera card, and full-frame "luxury tech" graphics with a moving world camera and real motion blur;
- burns in captions with highlighted keywords, adds a cover title and a CTA comment card;
- synthesizes every sound effect, the riser and the music bed in numpy, and mixes to -14 LUFS;
- writes a QA'd report.

## Install

```bash
mkdir -p ~/.claude/skills && cp -R talking-head-short ~/.claude/skills/
```

Then hand Claude a recording ("edit RAW.MP4 into a short"). Start with `SKILL.md`, which is the workflow. `references/brief.md` holds the full standard, and `references/lessons.md` lists the traps from the first real run.

## Contents
- `SKILL.md`: the step-by-step workflow.
- `scripts/`: setup, sync and analysis, transcription, cut, join check, run plan, eye-contact sheets, camera track, mattes, graphics render, audio synthesis, mastering, captions and cover, final assembly.
- `assets/`: the HyperFrames scene engine (`engine.js`), house styles (`base.css`) and fonts.
- `references/`: the brief, lessons, an example report and the example compositions from the first short. The examples refer to capture images (`gh.png`, `claude_logo.svg`) that aren't shipped; recapture your own.

## Requirements
macOS or Linux with Node 18+, Python 3.9+ and about 5 GB free disk. Everything else installs locally into the project via `scripts/setup.sh`.

## Licences
Code: MIT. Fonts in `assets/fonts/` (Poppins, Instrument Serif, EB Garamond, IBM Plex Mono, Inter) are under the SIL Open Font License 1.1.
