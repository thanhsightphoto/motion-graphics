#!/usr/bin/env bash
# Build and render every clip in a project, a few at a time (each render is slower than real time).
# usage: bash render_all.sh <project_dir> [fps=30000/1001] [jobs=3] [clip-name-filter]
# Transparent clips (bg:null) render to out/NN-name.mov (ProRes 4444), the rest to out/NN-name.mp4.
set -euo pipefail
P="$(cd "$1" && pwd)"; FPS="${2:-30000/1001}"; JOBS="${3:-3}"; ONLY="${4:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"; MB="$(cd "$HERE/../../motion-broll" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"; export NODE_PATH="${NODE_PATH:-$ROOT/motion/node_modules}"
cd "$P"; mkdir -p dist out
python3 "$MB/engine/build.py" dist clips/*${ONLY}*.html >/dev/null
for f in clips/*${ONLY}*.html; do
  n="$(basename "$f" .html)"; ext=mp4; grep -q "bg:null" "$f" && ext=mov
  echo "$n $ext"
done | xargs -P "$JOBS" -L 1 sh -c 'node "'"$MB"'/engine/render.js" "dist/$0.html" "out/$0.$1" "'"$FPS"'"'
