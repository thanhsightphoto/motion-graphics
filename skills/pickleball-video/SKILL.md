---
name: pickleball-video
description: Turn a raw pickleball coaching/drill clip into a finished Instagram Reel - transcript (any language, e.g. a Vietnamese- or English-speaking coach), 5+ motion-graphic technique clips or panels (paddle face, swing path, spin, when to reset vs counter) timed to the words, a title overlay, a trim to about 2:30-3:00 that never cuts mid-rally, burned-in English subtitles, a vertical 9:16 Instagram cover and a post caption. Use this whenever the user drops a new pickleball (or other racket-sport coaching) video and wants it edited, explained with animations, subtitled, trimmed, or prepared for Instagram, even if they only mention one of those steps, e.g. "make another one like the twoey video", "process this new clip", "do the usual for this drill".
---

# Pickleball coaching video → Instagram Reel

One pipeline, seven steps, with the user in the loop at four checkpoints. Two videos have been made this way; their
projects are in `videos/` and their clips in `examples/`. Together they are the quality bar:

| Example | Footage | Treatment | Look at it for |
|---|---|---|---|
| `examples/twoey-dink/` (Sept 2026) | behind-the-baseline, coach speaks Vietnamese, explains a lot | full-frame cutaways + a title panel | side-view paddle/swing diagrams, front-view sidespin, summary card |
| `examples/reset-counter/` (Oct 2026) | side-on court, coach speaks English, says little; the user is the right-side player | transparent panels in the sky over live play | rule card as title, decision slots, blind-vs-read diagram, live "read" tracker |

This skill builds on **motion-broll** (sibling skill). Read `motion-broll/SKILL.md` and
`motion-broll/reference/engine-api.md` before writing clips, then `references/visual-language.md` here for the pickleball
diagrams, their geometry and the mistakes already made once.

Paths below: `$PV` = this skill's folder, `$MB` = the motion-broll skill folder, `$P` = the video's project folder.
Run node scripts with `NODE_PATH=motion/node_modules` from the repo root (motion-broll's setup installs Playwright there).

## The user's standing rules

- **Never cut mid-rally.** Cuts start and end on dead balls (step 4). They noticed twice.
- **Keep the first example rally** after the explanation: it shows what the drill is.
- **Cover: vertical 9:16, zoomed out**, both players in the shot (step 6). Not square.
- The user's own framing of the lesson drives everything; when the coach says little, it *is* the content.
- Clips end with a ~2 s hold so people can read them; the paddle visibly swings through the ball.
- Target length: just under 3:00 by default; they have also asked for 2:30. Ask.

## 0. Set up the project

```bash
bash $MB/scripts/setup.sh ./motion          # first time on a machine only
P=videos/<short-slug>; mkdir -p $P/{transcript,clips,out,work,inputs}
ln -sfn "<absolute path to the video>" $P/source.mp4    # the raw folder (e.g. 2ndvideo/) is git-ignored: add it to .gitignore if new
python3 $MB/scripts/inspect_video.py $P/source.mp4 $P/work    # resolution, fps; look at work/contact.png
```

Scan the whole video too (one frame every 5 s into a sheet) to see the camera angle, where the players stand, and where
the frame is empty: that decides cutaways vs panels (step 2).

**Interview (checkpoint 1)**, one AskUserQuestion round, skipping anything already said:
- **Which technique or insight to focus on, in their words.** It becomes the clips, title, cover rules and caption.
- **Which player are they / who does what** (attacker, defender, coach), when they appear in the footage.
- Target length and number of graphics (default: 5 plus a title).
- Anything to keep or cut (a favourite rally, a tangent).
Defaults that no longer need asking: English on-screen text and subtitles, the motion-broll default palette.

## 1. Transcript

```bash
bash $PV/scripts/transcribe.sh $P/source.mp4 $P/transcript      # auto-detects language; ~1 min for 5 min of video
```

Writes `transcript.srt` (cues), `words.srt` (word times, for clip beats), `audio.wav` and `gaps.txt` (pauses in the talk).

**Check coverage first.** Court audio is often quiet: if the transcript is suspiciously short, whisper's VAD dropped
speech (Reset & Counter: 3 cues for 3:50). Normalize and re-run without VAD, with `-mc 0` so it can't loop on one
phrase over long rallies (it produced "Yeah, that's a good one" x 60 without it):

```bash
ffmpeg -i $P/transcript/audio.wav -af "highpass=f=120,dynaudnorm=f=150:g=15,loudnorm=I=-16" -ar 16000 -ac 1 $P/transcript/audio_norm.wav
whisper-cli -m <model> -f $P/transcript/audio_norm.wav -l <lang> -mc 0 -ml 1 -sow -osrt -of $P/transcript/words
```

Drop end-of-file hallucinations ("Thanks for watching!").

**Subtitle lines.**
- Coach speaks English (or whisper's cues run long): build subtitle-sized cues from the word timings, then write
  `en.txt` with the corrected lines (fix misheard words: "good beat" → "good read").
  `python3 $PV/scripts/cues_from_words.py $P/transcript/words.srt $P/transcript/transcript.srt`
- Other languages: write `en.txt` with **one natural English line per cue, same order**. Fix pickleball terms whisper
  mishears (Vietnamese "xuyết/xiết" = brush, "điền/đinh" = dink, "băng/bánh" = banh = ball).
- Either way: drop or mark `(unclear)` rather than guess, and list uncertain lines for the user.

```bash
python3 $PV/scripts/translate_srt.py $P/transcript/transcript.srt $P/transcript/en.txt $P/transcript/en.srt $P/work/cues_en.json
```

## 2. Plan the clips (checkpoint 2)

Find where the coach **explains** and map it to the user's focus. Pick the treatment from the frame:
- **Transparent panels** (`bg:null`, `center` in the empty area) when one wide shot leaves open sky or wall above the
  players (side-on court camera). The rally keeps playing underneath, panels can run long, and the title can be the
  first panel. Check the empty region on a gridded full-resolution frame; keep panels above the players' heads.
- **Full-frame cutaways** when the frame has no empty region (behind-the-baseline). Only while the coach talks, never
  mid-rally.
- When the coach says little, put the user's framing in panels during silent drilling, and drive beats from the calls
  that are there ("good read", "nice").

Show the motion-broll plan table (# · in–out · the line in English · what the shape does on which words · treatment ·
why) with at least 5 graphics plus a title, times on the **source** timeline. Wait for approval.

## 3. Build, check, render, review (checkpoint 3: loop until the user is happy)

- Write fragments in `$P/clips/NN-name.html`, starting from the closest example clip.
- Stills on the key words for every clip: `node $MB/engine/beats.js $P/dist/NN-name.html $P/work/NN.png t1 t2 …`. Look
  at every sheet; fix cramped, clipped, overflowing or stale states (a label from the previous phase still showing)
  before rendering. Check ball arcs clear the net numerically (snippet in `references/visual-language.md`).
- Render all: `bash $PV/scripts/render_all.sh $P` (parallel; `.mov` for `bg:null` clips). Filter one clip with
  the 4th argument when iterating: `bash $PV/scripts/render_all.sh $P 30000/1001 2 02-no-spin`.
- Write `$P/plan.source.json` (motion-broll plan schema plus `"video":"source.mp4"`, `"trimmed_video":"work/trimmed.mp4"`,
  files named `out/NN-name.ext`). For a review preview on the full-length video:
  ```bash
  NODE_PATH=motion/node_modules node $PV/scripts/subs_track.js $P/work/cues_en.json $P/work/subs_src.mov
  bash $PV/scripts/finish.sh $P plan.source.json work/subs_src.mov
  ```
- Check frames of every panel over the real footage, send `out/preview.mp4`, and ask what to change. Expect concrete
  feedback ("heavy spin paddle open and vertical", "remove #6"), and **ask a clarifying question with previews when a
  request can be read two ways** before re-rendering. Re-render only changed clips; a dropped clip leaves the plan and
  its render moves to `out/unused/`.

## 4. Trim to length (checkpoint 4)

**Never cut mid-rally.** Silence in the talk is not a dead ball, so find the rallies from the paddle-hit sounds:

```bash
python3 $PV/scripts/rallies.py $P/transcript/audio.wav            # rallies + dead-ball windows (safe cut zones)
```

- Start and end every kept segment in a dead-ball window; remove **whole points**, not pieces of the drill. The closing
  examples are usually the first thing to go.
- Keep the first example after the explanation, and every clip's explanation, intact.
- Quick re-feeds merge several points into one long "rally". A 1–2 s pause inside it *may* be a dead ball: confirm with
  frames (players walking back, picking up balls). In Reset & Counter, "sorry, sorry" turned out to be mid-point; a
  partner picking up balls after "Woo!" was a real dead ball.
- Reactions mark point ends: keep the reaction ("Woo!") and cut just after it, before the next feed.

Propose the cuts as a table (source range · what it is · seconds) with the resulting length. After approval write
`$P/keep.json` (segments to **keep**), check it, then trim:

```bash
python3 $PV/scripts/rallies.py $P/transcript/audio.wav --check $P/keep.json   # MID-RALLY fails; VERIFY = look at frames
python3 $PV/scripts/trim.py cut  $P/keep.json $P/source.mp4 $P/work/trimmed.mp4
python3 $PV/scripts/trim.py cues $P/keep.json $P/work/cues_en.json $P/work/cues_en_trim.json $P/out/subtitles_en.srt
python3 $PV/scripts/trim.py plan $P/keep.json $P/plan.source.json $P/plan.json   # re-stamps clip files with new in-points
```

A clip may not start inside a cut (the script stops and says which). Don't trim before the clips are approved: word
times live on the source timeline. Re-trimming is safe: `trim.py plan` finds renders that carry an older stamp.

## 5. Burn English subtitles, final preview

```bash
NODE_PATH=motion/node_modules node $PV/scripts/subs_track.js $P/work/cues_en_trim.json $P/work/subs_en.mov
bash $PV/scripts/finish.sh $P
```

This ffmpeg has no libass/drawtext; the subtitle track is drawn by Chromium and overlaid, so subtitles sit on top of the
clips too. Grab frames around each cut and in each clip to check, then remove stale `*_preview.mp4` files in `out/`.

## 6. Instagram cover (9:16 Reels cover, 1080x1920)

Vertical 9:16, **zoomed out** so both players and the net are in the shot. Don't fill the tall frame by cropping into
one player (that upscales and zooms in, and was rejected). Use the stacked layout: title card, the sharp wide shot in a
rounded box, the rules, over a blurred full-height crop of the same moment:

```bash
ffmpeg -ss <t> -i $P/source.mp4 -frames:v 1 -vf "crop=<w≈1380>:1080:<x>:0" $P/inputs/cover_frame_wide.png        # both players
ffmpeg -ss <t> -i $P/source.mp4 -frames:v 1 -vf "crop=608:1080:<x>:0,scale=1080:1920" $P/inputs/cover_frame_vertical.png  # blurred bg
NODE_PATH=motion/node_modules node $PV/scripts/cover.js $P/cover_vertical.json
```

`cover_vertical.json` (example in `examples/reset-counter/`): `{"frame":"inputs/cover_frame_wide.png",
"bg":"inputs/cover_frame_vertical.png","out":"out/cover_instagram_1080x1920.png","width":1080,"height":1920,
"layout":"stack","photoAspect":"<crop w/h>","cardTop":300, chip/title/subtitle/rules as on the title}`. Pick a sharp
moment with the ball near a paddle (take the time from the **source**, not a trimmed timeline that may change). The
script reports where the rules end: keep it under y=1680, because the profile grid shows only the middle 3:4. Tell the
user to pick it via "Add from camera roll" when uploading the Reel. A square 1080x1080 cover (no `layout`) only if asked.

## 7. Caption

Write it in chat following `references/caption.md` (structure, rules, both examples), built on the same rules as the
cover. Flag any technique cue in it that comes from you rather than the video. Offer a Vietnamese or one-line version.

## Deliver

In `$P/out/`: the clips named by in-point on the trimmed timeline, `preview.mp4` (trimmed, clips + subtitles),
`subtitles_en.srt`, `cover_instagram_1080x1920.png`, `TIMING.md`, `viewer.html`, `compare.html`; the caption in chat. Say
plainly: the preview is ready to post; for a final edit, drop the clips into an editor at the times in their names;
diagram angles and paths are schematic; list any `(unclear)` subtitle lines and the cut list.
