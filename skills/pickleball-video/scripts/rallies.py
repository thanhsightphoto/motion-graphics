"""Find rallies from the sound of paddle hits, so trims land between points and never mid-rally.
usage: python3 rallies.py audio.wav [max_gap_in_rally=1.8] [--check keep.json]

Paddle contact is a short broadband pop: we take the energy above 1.5 kHz in 5 ms frames, keep peaks 22 dB over the
local background that rise and fall within tens of ms, and chain hits less than max_gap apart into a rally. Output: one line per rally and the dead-ball
windows between them (safe cut zones). With --check, every cut boundary in keep.json is tested: a boundary inside a
rally (or within 0.4 s of a hit) is reported as MID-RALLY.
Quick re-feeds can merge several points into one long 'rally': gaps of 1-2 s inside it may or may not be dead balls.
Confirm a cut point by looking at frames there (players walking back, picking up balls = dead ball)."""
import json, subprocess, sys
import numpy as np

wav = sys.argv[1]
args = [a for a in sys.argv[2:] if not a.startswith('--')]
GAP = float(args[0]) if args and not args[0].endswith('.json') else 1.8
keep = json.load(open(sys.argv[sys.argv.index('--check') + 1])) if '--check' in sys.argv else None

SR = 16000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-af', 'highpass=f=1500', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
hop = SR // 200                                                   # 5 ms frames
n = len(x) // hop * hop
db = 20 * np.log10(np.sqrt(np.add.reduceat(x[:n] ** 2, np.arange(0, n, hop)) / hop) + 1e-6)
bg = np.array([np.median(db[max(0, i-400):i+400]) for i in range(len(db))])   # 4 s rolling background
hits = []
for i in np.where(db - bg > 22)[0]:
    # a paddle pop is sharp: it rises >8 dB within 20 ms and falls >8 dB within 40 ms (voices and footsteps don't)
    if i + 8 < len(db) and db[i] - db[i+8] > 8 and db[i] - db[max(0, i-4)] > 8:
        if hits and i - hits[-1] < 30:                            # one hit per 150 ms burst, at its peak
            if db[i] > db[hits[-1]]: hits[-1] = i
        else: hits.append(i)
T = np.array(hits) / 200.0
rallies = []
for t in T:
    if rallies and t - rallies[-1][1] <= GAP: rallies[-1][1] = t; rallies[-1][2] += 1
    else: rallies.append([t, t, 1])
rallies = [r for r in rallies if r[2] >= 2]                       # a lone pop is a feed bounce or noise, not a rally
dur = len(x) / SR
if keep is None:
    prev = 0.0
    for a, b, n in rallies:
        if a - prev > 1.0: print(f"   dead ball {prev:6.1f} – {a:6.1f}  ({a-prev:4.1f}s)  safe cut zone")
        print(f"rally {a:6.1f} – {b:6.1f}  ({n} hits)"); prev = b + 0.4
    print(f"   dead ball {prev:6.1f} – {dur:6.1f}  (end)")
else:
    bad = 0
    for a, b in keep:
        for edge, name in ((a, 'start'), (b, 'end')):
            if edge <= 0.05 or edge >= dur - 0.05: continue
            r = next((r for r in rallies if r[0] - 0.4 <= edge <= r[1] + 0.4), None)
            before, after = T[T <= edge], T[T > edge]
            p = before[-1] if len(before) else 0.0; q = after[0] if len(after) else dur
            if not r: print(f"ok         keep {name} {edge:.1f}s is between rallies")
            elif q - p >= 1.0 and edge - p >= 0.3 and q - edge >= 0.3:
                print(f"VERIFY     keep {name} {edge:.1f}s sits in a {q-p:.1f}s pause ({p:.1f}–{q:.1f}) inside rally {r[0]:.1f}–{r[1]:.1f}: look at frames, a dead ball is OK")
            else: bad += 1; print(f"MID-RALLY  keep {name} {edge:.1f}s falls in rally {r[0]:.1f}–{r[1]:.1f} (hits at {p:.1f} and {q:.1f})")
    sys.exit(1 if bad else 0)
