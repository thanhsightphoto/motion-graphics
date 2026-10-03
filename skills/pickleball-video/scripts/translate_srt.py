"""Build the English subtitle file from the source-language SRT plus your translation (one line per cue, same order).
usage: python3 translate_srt.py transcript.srt en.txt out_en.srt out_cues.json
Long cues (whisper often stretches one phrase over a silent rally) are capped so a line never lingers:
a cue lasts at most max(2s, min(4s, 1s + 0.3s per word))."""
import re, sys, json
src, en_txt, out_srt, out_json = sys.argv[1:5]
EN = [l.rstrip() for l in open(en_txt, encoding='utf-8').read().strip().split("\n")]
blocks = re.split(r"\n\s*\n", open(src, encoding='utf-8').read().strip())
if len(blocks) != len(EN):
    sys.exit(f"cue count mismatch: {len(blocks)} cues in {src}, {len(EN)} lines in {en_txt}")
ts = lambda s: (lambda h, m, x: int(h)*3600 + int(m)*60 + float(x.replace(',', '.')))(*s.strip().split(':'))
fmt = lambda t: f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round(t%1*1000)) % 1000:03d}"
cues, out = [], []
for i, (b, en) in enumerate(zip(blocks, EN), 1):
    a, z = [ts(x) for x in b.split("\n")[1].split('-->')]
    z = min(z, a + max(2.0, min(4.0, 1.0 + 0.3 * len(en.split()))))
    cues.append((a, z, en)); out.append(f"{i}\n{fmt(a)} --> {fmt(z)}\n{en}\n")
open(out_srt, 'w', encoding='utf-8').write("\n".join(out))
json.dump(cues, open(out_json, 'w'), ensure_ascii=False)
print(f"wrote {out_srt} and {out_json} ({len(cues)} cues)")
