#!/usr/bin/env bash
# Encode the rendered Motion Canvas frames into the final GIF + poster.
# Runs after the editor's RENDER button has produced PNGs in output/project/.
#
# Two-pass palette (ubitux's high-quality GIF recipe): palettegen with
# stats_mode=diff, then paletteuse with sierra2_4a dithering and diff_mode
# so only changing rectangles cost bytes — keeps the file under budget while
# the flat fills + static background stay crisp.

set -euo pipefail
cd "$(dirname "$0")/.."

FRAMES="output/project/%06d.png"
PAL="/tmp/debt-ops-pal.png"
GIF="debt-ops-concept.gif"
POSTER_FRAME="${POSTER_FRAME:-000130}" # ≈ hero hold (card A just filed). Override via env.

if [[ ! -f "output/project/000000.png" ]]; then
  cat <<EOF >&2
encode.sh: no rendered frames found in output/project/.
First render them in the Motion Canvas editor:
  npm start
  # then open http://localhost:9000 and click the blue RENDER button
EOF
  exit 1
fi

echo "→ palettegen"
ffmpeg -y -framerate 25 -i "$FRAMES" -frames:v 1 -update 1 \
  -vf "scale=960:-1:flags=lanczos,palettegen=max_colors=192:stats_mode=diff" \
  "$PAL" 2>/dev/null

echo "→ paletteuse"
ffmpeg -y -framerate 25 -i "$FRAMES" -i "$PAL" \
  -filter_complex "[0:v]scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
  -loop 0 "$GIF" 2>/dev/null

echo "→ poster (frame $POSTER_FRAME)"
if [[ -f "output/project/${POSTER_FRAME}.png" ]]; then
  ffmpeg -y -i "output/project/${POSTER_FRAME}.png" -vf "scale=960:-1:flags=lanczos" poster.png 2>/dev/null
else
  echo "  (frame $POSTER_FRAME not found — skipping poster regeneration)" >&2
fi

du -h "$GIF" poster.png 2>/dev/null | awk '{printf "%-8s %s\n", $1, $2}'
