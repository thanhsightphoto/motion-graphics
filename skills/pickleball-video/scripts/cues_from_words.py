"""Build subtitle-sized cues from a word-level SRT (for videos already in English, or any time whisper's cues run long).
usage: python3 cues_from_words.py words.srt out.srt [max_chars=48] [max_gap=0.7]
A cue breaks at sentence ends, at a pause longer than max_gap, or before it would pass max_chars."""
import re, sys
src, out = sys.argv[1], sys.argv[2]
MAXC = int(sys.argv[3]) if len(sys.argv) > 3 else 48
GAP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
ts = lambda x: (lambda h, m, r: int(h)*3600 + int(m)*60 + float(r.replace(',', '.')))(*x.strip().split(':'))
fmt = lambda t: f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round(t%1*1000)) % 1000:03d}"
W = []
for b in re.split(r"\n\s*\n", open(src, encoding='utf-8').read().strip()):
    L = b.split("\n")
    if len(L) >= 3 and '-->' in L[1]:
        w = " ".join(L[2:]).strip()
        if w in ('-', '') : continue
        a, z = [ts(x) for x in L[1].split('-->')]; W.append([a, z, w])
for i in range(len(W) - 1):            # whisper stretches word ends across pauses: cap at the next start, and at 0.8s
    W[i][1] = min(W[i][1], W[i+1][0], W[i][0] + 0.8)
W[-1][1] = min(W[-1][1], W[-1][0] + 0.8)
cues, cur = [], []
for a, z, w in W:
    if cur and (a - cur[-1][1] > GAP or len(" ".join(x[2] for x in cur + [[a, z, w]])) > MAXC):
        cues.append(cur); cur = []
    cur.append([a, z, w])
    if re.search(r'[.!?]$', w): cues.append(cur); cur = []
if cur: cues.append(cur)
open(out, 'w', encoding='utf-8').write("\n".join(
    f"{i}\n{fmt(c[0][0])} --> {fmt(max(c[-1][1], c[0][0] + 0.8))}\n{' '.join(x[2] for x in c)}\n" for i, c in enumerate(cues, 1)))
print(f"wrote {out} ({len(cues)} cues)")
