"""Eye-contact contact sheets: 8 frames per kept segment (add 100 ms steps around head turns by hand). Run from edit/.
  python eyesheet.py <proxy.mp4>   (any small, display-oriented proxy of the camera file)"""
import cv2, json, numpy as np, sys, os
E = json.load(open('work/edl.json')); os.makedirs('work/eye', exist_ok=True)
cap = cv2.VideoCapture(sys.argv[1]); fps = cap.get(cv2.CAP_PROP_FPS)
def grab(t):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t*fps)); ok, f = cap.read()
    h, w = f.shape[:2]; f = cv2.resize(f, (240, int(240 * h / w))); cv2.putText(f, '%.2f' % t, (8, 28), 0, 0.9, (0,255,255), 2); return f
rows = []
for k, s in enumerate(E['segs']):
    n = 8; ts = np.linspace(s['on'], s['end'], n)
    rows.append(np.hstack([grab(t) for t in ts]))
    if len(rows) == 4 or k == len(E['segs'])-1:
        cv2.imwrite('work/eye/sheet_%02d.jpg' % k, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 70]); rows = []
