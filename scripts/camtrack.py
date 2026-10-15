"""Frame-exact 60 fps camera track of the cut (hard cuts exactly on the joins). Run from edit/.
  python camtrack.py <oriented_intermediate.mp4> [out=work/camtrack.mp4]
Input: the camera file already rotated to display orientation (any size, e.g. 1080x1920 or 1920x1080 intermediate).
Writes the cover-fitted 1080x1920 track (full-cam picture), and for a LANDSCAPE source also work/camwide.mp4
(1890x1063 whole frame, the split-layout footage), plus <out>_map.json: [[out_frame, segment, source_frame], ...]."""
import cv2, json, subprocess, math, sys
src = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else 'work/camtrack.mp4'
E = json.load(open('work/edl.json')); segs = E['segs']; FPS = 60
cap = cv2.VideoCapture(src); SF = cap.get(cv2.CAP_PROP_FPS)
SW, SH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); WIDE = SW > SH
def cover(f):                       # centre slice, cover-fit to 1080x1920 (no zoom beyond cover)
    h, w = f.shape[:2]; s = max(1080 / w, 1920 / h); f = cv2.resize(f, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    y0 = (f.shape[0] - 1920) // 2; x0 = (f.shape[1] - 1080) // 2; return f[y0:y0 + 1920, x0:x0 + 1080]
def enc(path, size):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', size, '-r', '60', '-i', '-',
                             '-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p', '-g', '30', path], stdin=subprocess.PIPE)
wide = enc('work/camwide.mp4', '1890x1063') if WIDE else None
N = int(round(E['END'] * FPS)); cuts = [s['cut'] for s in segs]
ff = enc(OUT, '1080x1920')
cur = -1; frame = None; fmap = []
for i in range(N):
    t = i / FPS
    k = max(j for j in range(len(segs)) if cuts[j] <= t + 1e-9)
    fi = int(math.floor((t - segs[k]['delta']) * SF + 1e-6))
    if fi != cur:
        if fi != cur + 1: cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, raw = cap.read(); assert ok, fi
        frame = cover(raw); wf = cv2.resize(raw, (1890, 1063), interpolation=cv2.INTER_AREA) if WIDE else None
        cur = fi
    fmap.append([i, k, fi]); ff.stdin.write(frame.tobytes())
    if WIDE: wide.stdin.write(wf.tobytes())
ff.stdin.close(); ff.wait()
if WIDE: wide.stdin.close(); wide.wait()
json.dump(fmap, open(OUT.replace('.mp4', '_map.json'), 'w'))
# join report: the new take must show from its first frame
for k, s in enumerate(segs[1:], 1):
    c = int(round(s['cut'] * FPS)); exp = int(math.floor((s['cut'] - s['delta']) * SF + 1e-6))
    print(f'join {k:2d} frame {c}: prev src {fmap[c-1][2]} -> new src {fmap[c][2]} (expected {exp})' + ('' if fmap[c][2] == exp else '  MISMATCH'))
print('frames', N)
