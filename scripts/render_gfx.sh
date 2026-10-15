#!/bin/bash
# Render HyperFrames compositions for the short. Run from edit/.
#   bash render_gfx.sh draft r1 r2 ...   -> 30 fps draft + 12-frame contact sheet in work/gfx/renders/ (look at it!)
#   bash render_gfx.sh final r1 r2 ...   -> 240 fps render blended to 60 fps motion blur: work/gfx/final/<r>_60.mp4
#   bash render_gfx.sh cta               -> transparent ProRes 4444 work/gfx/final/cta.mov
# Renders run one at a time: an 8 GB machine swaps hard with two Chrome renders plus a matte job.
set -e
E="$(pwd)"; export PATH="$E/tools/bin:$PATH"; H="$E/tools/node_modules/.bin/hyperframes"
MODE=$1; shift
cd work/gfx; mkdir -p renders final
case $MODE in
  draft) for r in "$@"; do
      $H render . -c compositions/$r.html -o renders/${r}_draft.mp4 -f 30 -q draft --quiet > renders/${r}.log 2>&1 || { tail -20 renders/${r}.log; exit 1; }
      D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/${r}_draft.mp4)
      ffmpeg -v error -y -i renders/${r}_draft.mp4 -vf "fps=12/$D,scale=270:480,tile=6x2" -frames:v 1 renders/${r}_sheet.jpg
      echo "$r: $D s -> work/gfx/renders/${r}_sheet.jpg"; done ;;
  final) for r in "$@"; do
      $H render . -c compositions/$r.html -f 240 -q delivery --crf 12 -o final/${r}_240.mp4 --quiet > final/${r}.log 2>&1 || { echo "FAIL $r"; tail -20 final/${r}.log; exit 1; }
      ffmpeg -v error -y -i final/${r}_240.mp4 -vf "tmix=frames=3,fps=60" -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p final/${r}_60.mp4
      echo "OK $r"; done ;;
  cta) $H render . -c compositions/cta.html -f 60 --format mov -o final/cta.mov --quiet > final/cta.log 2>&1 && echo "OK cta" ;;
esac
