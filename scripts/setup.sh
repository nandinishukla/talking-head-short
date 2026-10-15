#!/bin/bash
# Project-local toolchain: ffmpeg/ffprobe (npm static builds), HyperFrames, Python venv.
# Usage: bash setup.sh <project-folder>   -> creates <project>/edit/{tools,work,stems}
set -e
P="$(cd "${1:-.}" && pwd)"; E="$P/edit"; T="$E/tools"
mkdir -p "$T/bin" "$E/work" "$E/stems"
cd "$T"
[ -f package.json ] || npm init -y >/dev/null
npm i --silent ffmpeg-static @ffprobe-installer/ffprobe hyperframes puppeteer-core >/dev/null
ln -sf "$T/node_modules/ffmpeg-static/ffmpeg" "$T/bin/ffmpeg"
FP=$(ls -d "$T"/node_modules/@ffprobe-installer/*/ffprobe | grep -v "/ffprobe/ffprobe" | head -1)
ln -sf "$FP" "$T/bin/ffprobe"
[ -d venv ] || python3 -m venv venv
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q numpy scipy soundfile faster-whisper pyloudnorm pillow opencv-python-headless
"$T/bin/ffmpeg" -hide_banner -filters 2>/dev/null | grep -q " subtitles " || echo "WARN: this ffmpeg has no libass (captions need it)"
echo "Toolchain ready. In every shell:  export PATH=\"$T/bin:\$PATH\""
echo "Python: $T/venv/bin/python    HyperFrames: $T/node_modules/.bin/hyperframes"
