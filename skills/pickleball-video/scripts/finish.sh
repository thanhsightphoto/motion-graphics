#!/usr/bin/env bash
# Composite the clips onto the (trimmed) video, burn the subtitle track on top, and write viewer/compare pages.
# usage: bash finish.sh <project_dir> [plan=plan.json] [subs=work/subs_en.mov]
#   review before trimming:  bash finish.sh <project> plan.source.json work/subs_src.mov
set -euo pipefail
P="$(cd "$1" && pwd)"; PLAN="${2:-plan.json}"; SUBS="${3:-work/subs_en.mov}"; HERE="$(cd "$(dirname "$0")" && pwd)"; MB="$(cd "$HERE/../../motion-broll" && pwd)"
cd "$P"
python3 "$MB/scripts/composite.py" "$PLAN" work/preview_nosubs.mp4
ffmpeg -loglevel error -y -i work/preview_nosubs.mp4 -i "$SUBS" \
  -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]" \
  -map "[v]" -map '0:a?' -c:v libx264 -crf 18 -c:a copy -movflags +faststart out/preview.mp4
python3 "$MB/scripts/make_pages.py" "$PLAN" out/preview.mp4
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/preview.mp4)
python3 -c "d=$d; print(f'out/preview.mp4: {int(d//60)}:{d%60:04.1f}')"
