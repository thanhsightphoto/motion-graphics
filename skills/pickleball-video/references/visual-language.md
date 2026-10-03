# Pickleball visual language

Clips are motion-broll fragments (read `motion-broll/reference/engine-api.md` first). This file covers what is specific to
pickleball coaching videos: the diagrams that work, their geometry, and mistakes already made once. Every pattern has a
working example in `examples/`: copy the nearest one and change it rather than starting blank.

| Pattern | Use it for | Example |
|---|---|---|
| Side-view court: ball, paddle edge-on, net, swing path | paddle face angle, swing path, ball flight, "forward = net" | `01-heavy-slice.html`, `02-no-spin.html` |
| Toggle between two ball types on the same diagram | contrasting two situations (no spin vs heavy slice) | `02-no-spin.html` |
| Stacked chain + direction arrows + arc | body mechanics (hips → arm → paddle, stand up vs step forward) | `03-hips-arc.html` |
| Front view: net band, ball with spin ring, paddle face-on | sidespin, tilted spin axis, paddle roll | `04-sidespin-face.html` |
| Two columns side by side | the closing summary / "rules" card | `05-read-the-ball.html` |
| Transparent title panel over the opening shot | title overlay | `00-title.html` |
| **Sky panels** (all `examples/reset-counter/`): | | |
| Title that *is* the rule: two rows "No read → Block & reset", "Good read → Counter" | when the opening line states the lesson | `01-title-rule.html` |
| Slots filling on words: Block ✓, Block ✓, Good read → Counter | a "my philosophy" / sequence line | `02-philosophy.html` |
| Side-on court mirrored to the camera, four phases (two failures, two right answers) | cause and effect during silent drilling | `03-blind-vs-read.html` |
| Corner island that expands on each call and counts it | live calls ("good read") during play | `04-read-tracker.html` |
| Two columns + shared tag + bottom line | "X is still Y, same decision" | `05-off-speed.html` |

## Two treatments

- **Full-frame cutaways** (twoey): the frame is all players, so graphics replace it while the coach talks.
- **Transparent panels** (reset & counter): a side-on court shot leaves sky across the top ~40%. Panels sit there
  (`center:[960,~250]`, card height ≤ ~380 so the bottom stays above the players' heads at y ≈ 460–520) while the rally
  plays underneath. They can run 10–30 s. Use `cam:1.0` (world px = screen px), white cards (strong on blue sky), no
  cursor (it distracts over live play), and an exit so the card doesn't vanish on a hard cut:
  `geom:(t,g)=>{const e=M.eio((t-(T-0.6))/0.45); g.sc*=1-0.3*e; g.op*=1-e; return g;}`.
  A corner island (`center:[1400,130]`) works for something that should stay small and persistent.

## Frame and layout (1920x1080 footage)

- For full-frame cutaways, place them while the coach *explains*, never mid-rally (people want to see the actual
  shots). For panels, see "Two treatments" above.
- Subtitles are burned in at the bottom (box ~70px tall, 46px from the bottom). Keep cards clear of them:
  `center:[960,490]` and a card of about 1000x580 at `cam:1.42` puts the card bottom near y=900.
- Card text: title 44–46px, key/value rows 26px grey key + 34px bold value at top-right, chips 24px.
- Colour meaning, kept consistent across clips: **orange = what the player controls** (paddle face strip, face-normal
  arrow, swing path). Black/grey for the ball, net, ground. Red (`#D93A2B`) only for a failure mark (✕ into the net).

## Side-view court geometry (examples 01, 02)

Drawn inside `<g transform="translate(-30 -40) scale(1.1)">`; cursor keys are in world coords, so map diagram points with
`W=(t,x,y)=>[t,x*1.1-30,y*1.1-40]`.

- Ground `y=270`. Net: rect `x=234..246`, top `y=80`. Player on the left, net to the right.
- Ball at contact `(-140,160)`, r=24. Paddle pivot `(-172,160)`: the face strip touches the ball.
- **Paddle angle**: `rotate(θ)` about the pivot. **θ < 0 = open** (top tilts back away from the net, face points up),
  **θ > 0 = closed** (top leans toward the net). Used: heavy slice **−35°**, no spin **+20°**, square 0°.
- Face-normal arrow sits on the upper paddle (`y=-58`) so it never crosses the ball.
- The cursor changes the angle by dragging the paddle's top edge; the angle is read from the cursor (`angOf`).

## The paddle swings through the ball

A static paddle with an arrow next to it read poorly; the paddle should travel along its swing path:

- `closestU(path, PX, PY)` finds where the path passes the pivot; `off(path, uc, u)` gives the paddle's offset.
- `segU([[t0,t1,u0,u1,ease],…])` scripts the travel: wind-up to the path start, accelerate into contact (`x*x`),
  ease out to the end, and return to contact if the cursor needs it again.
- Reveal the orange path *as the paddle travels* (`p = u`), and launch the ball **at contact**, on the spoken word.

## Ball flights must clear (or hit) the net

Check arcs numerically before rendering; one early arc visibly clipped the tape. With the net at x=240, top y=80:

```python
from math import comb
B=lambda p,u:tuple(sum(comb(len(p)-1,i)*(1-u)**(len(p)-1-i)*u**i*p[i][k] for i in range(len(p))) for k in (0,1))
pts=[B([(-140,160),(60,-260),(430,262)],i/1000) for i in range(1001)]
print(min(pts,key=lambda q:abs(q[0]-240))[1])   # must be well under 80 (up = smaller y)
```

Paths used: heavy slice `Q 60 -260 430 262`; no spin `C -20 -100, 170 -120, 430 262`; into the net `Q 60 125 232 150`.

## Timing

- Author clips on the **source** timeline (that is where word times are); `trim.py plan` moves them after trimming.
- Put each change on its word (clip-local time = word time − clip in). Whisper word times drift ±0.3s.
- End every clip with a **2-second hold** on its final state: the user asked for time to read.
- Back-to-back clips: make the first clip's `out` equal the next clip's `in` so the face doesn't flash for 0.1s.
- A clip must *start* inside a kept segment; it may run past a cut.

## Side-on court (examples/reset-counter/03)

Mirror the diagram to the camera: if the user stands on the right, they defend on the right and the ball comes from the
left. Ground `y=150`, net `x=-6..6` with top `y=30`, defender paddle pivot `(190,40)`, contact `(165,40)`, ball r=14;
the whole group is scaled 1.15 so it fills the 1240x400 card. For a player facing **left**, `rotate(+θ)` opens the face
(top tilts away from the net). Checked paths: incoming `Q -100 -20 165 40` from `(-380,0)`; block/reset
`Q 40 -150 -90 140` (drops in their kitchen); counter `Q 40 -70 -300 135` (at their feet); blind counter into the net
`Q 80 70 8 100`; pop-up `Q 80 -260 -150 -30` then a red smash line back.

When a panel steps through phases, every phase change must clear the previous result label (empty key in the sequence),
or the old "✕ Pops up" sits next to the new title. Speed lines belong behind the ball's direction of travel.

## Text that has to fit

Chips over ~13 characters at 28px overflow a 210px pill ("Block / Counter"): widen to 220px and drop to 26px. Leave
~40px between the last line of a card and its bottom edge.

## Title overlay

`bg:null`, `center` over the empty court (left side in a behind-the-baseline shot), pill → card with title, subtitle
and the video's rules, then shrink + fade out via `geom` at ~5s. Render to `.mov`; `render_all.sh` does this
automatically when the fragment contains `bg:null`.
