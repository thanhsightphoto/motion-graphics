# motion-graphics

Motion-graphics skills for Claude Code. Each skill does one job. The first one is **`motion-broll`**.

| Skill | What it does |
|---|---|
| `motion-broll` | Give it a video and a transcript and it makes motion-graphic B-roll timed to your words. |
| `pickleball-video` | Give it a raw pickleball drill clip and it makes an Instagram Reel: technique animations, a trim that never cuts mid-rally, English subtitles, a 9:16 cover and a caption. Built on `motion-broll`. |

More skills will be added to this repo.

## motion-broll

**Motion-graphic B-roll for your videos, made by Claude Code.** Give it a video and a transcript and it plans, animates and renders clips timed to your words. Each clip is one continuous shape that keeps morphing (pill → card → terminal → chart) and never cuts, with a cursor driving every change.

<p>
  <img src="docs/demo-panel.gif" width="49%" alt="A transparent panel animating beside a picture-in-picture shot of the speaker">
  <img src="docs/demo-cutaway.gif" width="49%" alt="A full-frame cutaway: build notes turning into a master prompt that is dragged into a session">
</p>

## What you get

You run `/motion-broll`, answer a few questions, approve a plan, and get back:

- **The clips**, named by where they go on your timeline (`04-master-prompt_0m32s40.mp4`). Full-frame cutaways are MP4. Panels that sit in empty space next to you are transparent ProRes 4444 `.mov`.
- **A preview render** of your video with the clips cut in.
- **`compare.html`**: original vs. with motion graphics, synced, as side by side, stacked or wipe.
- **`viewer.html`**: step through the clips one by one.
- **`TIMING.md`**: every clip with its in/out point and the line it covers.

The preview is for review. For your final cut, drop the clips into your own editor.

## Install

```
npx skills add Barty-Bart/motion-graphics
```

That installs the skills from this repo (pick `motion-broll`). It works in Claude Code and other agents that read skills.

Or copy `skills/motion-broll` into your project's `.claude/skills/` (or `~/.claude/skills/` to use it everywhere).

**Requirements:** Node 18+, Python 3, and ffmpeg (with the ProRes encoder, standard in Homebrew builds). On first run the skill installs Playwright and Chromium into a local `motion/` folder.

## Use it

```
/motion-broll
```

Then point it at your video and transcript (an SRT from your editor, Descript or YouTube works). It will:

1. **Inspect the footage.** It reads resolution, frame rate and layout, including picture-in-picture sections and whether the box changes size.
2. **Estimate word timings** from your transcript.
3. **Plan the clips** in a table and wait for your OK. For each clip it chooses a full-frame cutaway, a transparent panel in empty space, or nothing, and tells you why.
4. **Build each clip**, check stills on the key words, and fix what's off.
5. **Render** with motion blur at your video's frame rate, then make the preview and the comparison pages.

It never invents numbers or results. Bars show relative size and text uses skeleton lines until you give it the real figures.

## How it works

- Every frame is a pure function of time. Springs are closed-form step responses, and a value that changes target many times is the sum of one spring per change. There are no CSS transitions or timers, so any frame can be rendered on its own.
- Clips are small HTML files on a shared engine (`skills/motion-broll/engine/motion.js`). Headless Chromium captures 4 sub-frames per frame across a 180° shutter, and ffmpeg blends them into motion blur.
- The worked example in `skills/motion-broll/examples/opus-aoe2/` is the six clips from the demo above.

## pickleball-video

**A pickleball coaching clip in, an Instagram Reel out.** Point it at a drill video and tell it the lesson in your own
words ("no read → block & reset, good read → counter"). It runs seven steps and stops for you at four checkpoints:

1. **Transcribe** the coach (any language; quiet court audio is normalized) and write English subtitle lines.
2. **Plan 5+ graphics** around your lesson: full-frame cutaways, or transparent panels in the sky over the live rally
   when the camera leaves room. *You approve the plan.*
3. **Build and render** them (paddle face, swing path, spin, decision cards), then send a full-length preview.
   *You ask for changes until it's right.*
4. **Trim** to your target length (2:30–3:00). Rallies are found from the sound of paddle hits and every cut lands on
   a dead ball, never mid-rally. *You approve the cuts.*
5. **Burn in English subtitles** on top of everything.
6. **Make a 9:16 Reels cover**: title, a zoomed-out shot with both players, and the rules.
7. **Write the caption.**

```
/pickleball-video 2ndvideo/my drill.mp4
Focus: <the lesson in your words>
```

Each video gets its own folder in `videos/<name>/` (git-ignored: footage and renders stay local). The finished files
land in `videos/<name>/out/`: `preview.mp4` (ready to post), the cover, `subtitles_en.srt`, the individual clips and
`TIMING.md`. The skill's `examples/` holds the animations from the first two videos as starting points.

**Extra requirements:** whisper.cpp (`whisper-cli`) with the large-v3 model, and Python 3 with numpy.

## Licence

MIT. Geist fonts: SIL Open Font License. Icon paths adapted from Lucide (ISC).
