# Motion-Graphic

This folder is the user's fork of `motion-graphics` (origin: `thanhsightphoto/motion-graphics`, upstream:
`Barty-Bart/motion-graphics`), used to make a recurring series of **pickleball coaching Reels for Instagram**.

## For a new video

Use the `/pickleball-video` skill (`skills/pickleball-video/SKILL.md`). It builds on `/motion-broll`. Both are linked into
`.claude/skills/`, so they only appear in sessions opened in this folder.

The user's standing rules (details in the skill):
- Never cut mid-rally; trims land on dead balls (`scripts/rallies.py` checks them). Keep the first example rally.
- Instagram cover is vertical 9:16 and zoomed out (both players), not square.
- Their own framing of the lesson drives the graphics, title, cover and caption. Target length 2:30–3:00: ask.

## Layout

| Path | What | In git? |
|---|---|---|
| `skills/motion-broll/` | upstream motion-graphic engine + skill | yes |
| `skills/pickleball-video/` | the pickleball workflow: SKILL.md, scripts, references, examples | yes |
| `.claude/skills/` | links that register both skills | yes |
| `videos/<slug>/` | one project per video: transcript, clips, renders, `out/` deliverables | no (ignored) |
| `1stvideo/`, `2ndvideo/`, … | raw footage the user drops in | no (ignored); add new folders to `.gitignore` |
| `motion/` | Playwright/Chromium install (`node_modules`) + the first video's original working files | no (ignored) |

Done so far: `videos/twoey-dink/` (2026-09-27) and `videos/reset-counter/` (2026-10-03).

## Environment notes

- ffmpeg here has no libass/drawtext: subtitles are drawn by Chromium (`subs_track.js`) and overlaid.
- whisper.cpp (`whisper-cli`) with `~/.cache/hyperframes/whisper/models/ggml-large-v3.bin` (+ silero VAD model).
- Run node scripts with `NODE_PATH=motion/node_modules` from this folder.
- Commit or push only when the user asks; footage and renders must never be committed.
