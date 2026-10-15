# talking-head-short

A Claude Code skill that turns a raw talking-head recording into a finished 9:16 short (Reel, TikTok, YouTube Short), entirely in code: ffmpeg, Python, Node and [HyperFrames](https://hyperframes.heygen.com).

What it does:
- syncs and transcribes the recording, keeps the last good take of every line and cuts retakes, pauses and false starts;
- builds a J-cut voice track and checks eye contact;
- rotates through three layouts: full cam, a split with your head popping out of a camera card, and full-frame "luxury tech" graphics with a moving world camera and real motion blur;
- plans the whole edit as a storyboard and beat table and waits for your approval before rendering;
- burns in two caption styles: small pill captions over visuals, and big see-through hero words for the hook and key lines; adds a cover title and a CTA comment card;
- synthesizes every sound effect, the riser and the music bed in numpy, and mixes to -14 LUFS;
- writes a QA'd report.

## Install

```bash
mkdir -p ~/.claude/skills && cp -R talking-head-short ~/.claude/skills/
```

Add the motion references you like to `references/motion-library.md`. Then hand Claude a recording ("edit RAW.MP4 into a short"). Start with `SKILL.md`, which is the workflow. `references/brief.md` holds the full standard, and `references/lessons.md` lists the traps from the first real run.

## Contents
- `SKILL.md`: the step-by-step workflow.
- `scripts/`: setup, sync and analysis, transcription, cut, join check, run plan, eye-contact sheets, camera track, mattes, graphics render, audio synthesis, mastering, captions and cover, final assembly.
- `assets/`: the HyperFrames scene engine (`engine.js`), house styles (`base.css`) and fonts.
- `references/`: the brief, lessons, an example report and the example compositions from the first short. The examples refer to capture images (`gh.png`, `claude_logo.svg`) that aren't shipped; recapture your own.

## Requirements
macOS or Linux with Node 18+, Python 3.9+ and about 5 GB free disk. Everything else installs locally into the project via `scripts/setup.sh`.

## Credits
The motion references in `references/motion-prompts.md` come from [prompt-motion.com](https://prompt-motion.com/) (curated by @p4nthera_). Prompts by
[@wozu-co](https://prompt-motion.com/customize/wozu-co-242285),
[@elliot-garreffa](https://prompt-motion.com/customize/elliot-garreffa-f334bc),
[@bizibeast](https://prompt-motion.com/customize/bizibeast-10f264),
[@adamdesgns](https://prompt-motion.com/customize/adamdesgns-478d6d),
[@devius-maximus](https://prompt-motion.com/customize/devius-maximus-beab45),
[@fractadev](https://prompt-motion.com/customize/fractadev-149adc),
[@miskinho](https://prompt-motion.com/customize/miskinho-443898) and
[@gautam-mer1](https://prompt-motion.com/customize/gautam-mer1-2ae354).
The prompts belong to their creators.

## Licences
Code: MIT. Fonts in `assets/fonts/` (Poppins, Pacifico, Archivo Black, EB Garamond, IBM Plex Mono, Inter) are under the SIL Open Font License 1.1.
