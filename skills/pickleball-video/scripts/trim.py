"""Trim a video to kept segments and move everything timed on the source (subtitles, clips) onto the new timeline.

keep.json is a list of [start, end] source-time segments to KEEP, in order, e.g. [[0,10],[31.8,95],[111.7,172.9]].

usage:
  python3 trim.py cut  keep.json source.mp4 trimmed.mp4          # hard cuts, 30 ms audio fades at each join
  python3 trim.py cues keep.json cues.json out_cues.json out.srt  # subtitles onto the trimmed timeline
  python3 trim.py plan keep.json plan.source.json plan.json       # clip in/out onto the trimmed timeline + name renders by in-point
  python3 trim.py map  keep.json 43.0 54.6 ...                    # print where source times land (None = inside a cut)

Clips are authored against SOURCE time (that is where the word timings are). A clip's in-point must sit in a kept
segment; its out-point may run past a cut, the overlay simply continues over the next kept segment.
"""
import json, os, pathlib, shutil, subprocess, sys

def load_keep(p):
    K = [tuple(map(float, s)) for s in json.load(open(p))]
    assert all(a < b for a, b in K) and all(K[i][1] <= K[i+1][0] for i in range(len(K)-1)), "keep segments must be ordered and non-overlapping"
    return K

def remap(K, t):
    acc = 0.0
    for a, b in K:
        if a <= t <= b: return acc + t - a
        acc += b - a
    return None

def clamp_out(K, t_in, t_out):
    """Out-point on the new timeline: same duration as authored, measured from the remapped in-point."""
    return remap(K, t_in) + (t_out - t_in)

tc = lambda t: f"{int(t//60)}m{t%60:05.2f}".replace('.', 's')   # 61.0 -> 1m01s00
fmt = lambda t: f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round(t%1*1000)) % 1000:03d}"

def cut(K, src, dst):
    fc, parts = [], []
    for i, (a, b) in enumerate(K):
        d = b - a
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03[a{i}]")
        parts.append(f"[v{i}][a{i}]")
    fc.append("".join(parts) + f"concat=n={len(K)}:v=1:a=1[v][a]")
    fps = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', src],
                         capture_output=True, text=True).stdout.strip() or '30000/1001'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
                    '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-r', fps, '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', dst], check=True)
    total = sum(b - a for a, b in K)
    print(f"wrote {dst}: {int(total//60)}:{total%60:04.1f} ({total:.1f}s)")

def cues(K, src_json, out_json, out_srt):
    out = []
    for a, z, txt in json.load(open(src_json)):
        for ka, kb in K:
            s, e = max(a, ka), min(z, kb)
            if e - s >= 0.6: out.append((remap(K, s), remap(K, e), txt))
    json.dump(out, open(out_json, 'w'), ensure_ascii=False)
    open(out_srt, 'w', encoding='utf-8').write("\n".join(f"{i}\n{fmt(a)} --> {fmt(z)}\n{t}\n" for i, (a, z, t) in enumerate(out, 1)))
    print(f"wrote {out_json} and {out_srt} ({len(out)} cues)")

def plan(K, src_plan, dst_plan):
    P = json.load(open(src_plan)); base = pathlib.Path(src_plan).parent
    for c in P['clips']:
        t_in = remap(K, c['in'])
        if t_in is None: sys.exit(f"clip {c['id']} starts at {c['in']}s, inside a cut: move the clip or the cut")
        c['out'] = round(clamp_out(K, c['in'], c['out']), 2); c['in'] = round(t_in, 2)
        f = base / c['file']                              # render named out/NN-name.ext -> out/NN-name_1m01s00.ext
        stem = f.stem.split('_')[0] if '_' in f.stem and f.stem.split('_')[-1][0].isdigit() else f.stem
        new = f.with_name(f"{stem}_{tc(c['in'])}{f.suffix}")
        if not f.exists():                                 # re-trimming: the render already carries an older stamp
            old = [x for x in f.parent.glob(f"{stem}_*{f.suffix}") if not x.stem.endswith('_preview')]
            if old: f = old[0]
        if f.exists() and f != new: shutil.move(f, new)
        c['file'] = os.path.relpath(new, base)
        print(f"  {c['id']}  {c['in']:7.2f} – {c['out']:7.2f}  {c['file']}")
    P['video'] = P.get('trimmed_video', P['video'])
    P.setdefault('notes', []).insert(0, "Trimmed timeline. Kept source segments: " + ", ".join(f"{a:g}–{b:g}s" for a, b in K))
    json.dump(P, open(dst_plan, 'w'), ensure_ascii=False, indent=2); print(f"wrote {dst_plan}")

if __name__ == '__main__':
    cmd, keep, *rest = sys.argv[1:]; K = load_keep(keep)
    if cmd == 'cut': cut(K, *rest)
    elif cmd == 'cues': cues(K, *rest)
    elif cmd == 'plan': plan(K, *rest)
    elif cmd == 'map': [print(t, '->', None if remap(K, float(t)) is None else round(remap(K, float(t)), 2)) for t in rest]
    else: sys.exit(__doc__)
