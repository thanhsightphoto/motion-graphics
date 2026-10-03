"""Print word timings as lines of speech separated by '--- gap' markers: where nobody talks is where you can cut.
usage: python3 gaps.py words.srt [min_gap_seconds=2.5]
Word times from whisper are approximate; a long gap is reliable, the exact word inside a line is not."""
import re, sys
MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
ts = lambda x: (lambda h, m, r: int(h)*3600 + int(m)*60 + float(r.replace(',', '.')))(*x.strip().split(':'))
W = []
for b in re.split(r"\n\s*\n", open(sys.argv[1], encoding='utf-8').read().strip()):
    L = b.split("\n")
    if len(L) >= 3 and '-->' in L[1]:
        a, z = [ts(x) for x in L[1].split('-->')]; W.append((a, z, " ".join(L[2:]).strip()))
# whisper stretches each word's end to the next word's start, so measure start-to-start
# and allow ~0.8s for the last word before a pause to be spoken
prev, line = 0.0, []
for a, z, w in W:
    if a - prev > MIN:
        if line: print(" ".join(line))
        print(f"   --- gap {prev+0.8:.1f} -> {a:.1f} (~{a-prev-0.8:.1f}s, no talking)"); line = []
    line.append(f"{a:.1f}:{w}"); prev = a
if line: print(" ".join(line))
