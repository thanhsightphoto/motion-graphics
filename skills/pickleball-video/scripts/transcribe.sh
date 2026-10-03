#!/usr/bin/env bash
# Transcribe a video with whisper.cpp: cue-level SRT (for subtitles) + word-level SRT and a gap list (for trimming).
# usage: bash transcribe.sh <video> <out_dir> [language, default auto]
set -euo pipefail
V="$1"; OUT="$2"; LANG_ARG="${3:-auto}"
HERE="$(cd "$(dirname "$0")" && pwd)"
MODEL="${WHISPER_MODEL:-$HOME/.cache/hyperframes/whisper/models/ggml-large-v3.bin}"
VAD="${WHISPER_VAD:-$HOME/.cache/hyperframes/whisper/models/ggml-silero-v5.1.2.bin}"
command -v whisper-cli >/dev/null || { echo "Missing whisper-cli (macOS: brew install whisper-cpp)"; exit 1; }
[ -f "$MODEL" ] || { echo "Missing Whisper model: $MODEL (set WHISPER_MODEL, or download ggml-large-v3.bin)"; exit 1; }
VADARGS=(); [ -f "$VAD" ] && VADARGS=(--vad -vm "$VAD")
mkdir -p "$OUT"
ffmpeg -v error -y -i "$V" -ar 16000 -ac 1 -c:a pcm_s16le "$OUT/audio.wav"
whisper-cli -m "$MODEL" -f "$OUT/audio.wav" -l "$LANG_ARG" -osrt -of "$OUT/transcript" "${VADARGS[@]}" >/dev/null 2>&1
whisper-cli -m "$MODEL" -f "$OUT/audio.wav" -l "$LANG_ARG" -ml 1 -sow -osrt -of "$OUT/words" "${VADARGS[@]}" >/dev/null 2>&1
python3 "$HERE/gaps.py" "$OUT/words.srt" > "$OUT/gaps.txt"
echo "wrote $OUT/transcript.srt ($(grep -c -- '-->' "$OUT/transcript.srt") cues), $OUT/words.srt, $OUT/gaps.txt"
