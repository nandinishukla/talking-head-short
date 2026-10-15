"""Sync + audio analysis. Run from edit/.
  python analyze_audio.py <camera.mp4> [clean_audio.wav]
Writes work/cam48.wav, work/voice_src48.wav (the audio used from here on), work/rms10.npy (10 ms RMS dB),
work/sync.json, and prints quiet stretches (< -35 dB, >100 ms) next to the transcript words if tx exists."""
import sys, json, subprocess, os, numpy as np, soundfile as sf
from scipy.signal import correlate, resample_poly
cam = sys.argv[1]; clean = sys.argv[2] if len(sys.argv) > 2 else None
os.makedirs('work', exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cam, '-map', '0:a:0', '-ar', '48000', '-c:a', 'pcm_s24le', 'work/cam48.wav'], check=True)
c, sr = sf.read('work/cam48.wav'); cm = c.mean(1) if c.ndim > 1 else c
sync = {}
if clean:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', clean, '-ar', '48000', '-c:a', 'pcm_s24le', 'work/clean48.wav'], check=True)
    k, _ = sf.read('work/clean48.wav'); km = k.mean(1) if k.ndim > 1 else k
    a = resample_poly(cm, 1, 3); b = resample_poly(km, 1, 3)         # 16 kHz mono
    xc = correlate(a, b, mode='full', method='fft'); ax = np.abs(xc)
    i = int(np.argmax(ax)); lag = (i - (len(b) - 1)) / 16000.0       # clean starts `lag` s after camera start
    side = np.concatenate([ax[:max(0, i - 1600)], ax[i + 1600:]])
    ratio = float(ax[i] / (side.max() + 1e-12))
    sync = dict(offset_s=lag, peak_ratio=ratio, source='clean')
    print(f'offset {lag*1000:.1f} ms (camera time = clean time + offset), peak/next {ratio:.1f}x')
    # place clean audio on the camera timeline
    n = len(cm); out = np.zeros(n); o = int(round(lag * sr))
    src = km[max(0, -o):]; dst0 = max(0, o); m = min(len(src), n - dst0); out[dst0:dst0 + m] = src[:m]
    sf.write('work/voice_src48.wav', out, sr, subtype='FLOAT')
else:
    # no clean file: confirm the camera channels agree and use the camera track (log this in the report)
    if c.ndim > 1:
        a = resample_poly(c[:, 0], 1, 3)[:16000 * 30]; b = resample_poly(c[:, 1], 1, 3)[:16000 * 30]
        xc = np.abs(correlate(a, b, mode='full', method='fft')); i = int(np.argmax(xc))
        sync = dict(offset_s=(i - (len(b) - 1)) / 16000, peak_ratio=float(xc[i] / np.sort(xc)[-200]), source='camera L/R (no clean file)')
    sf.write('work/voice_src48.wav', cm, sr, subtype='FLOAT')
    print('No clean audio given: using the camera track.', sync)
x, _ = sf.read('work/voice_src48.wav')
w = 480; n = len(x) // w
r = 20 * np.log10(np.sqrt(np.mean(x[:n * w].reshape(n, w) ** 2, 1)) + 1e-9)
np.save('work/rms10.npy', r)
sync.update(clipped=int((np.abs(x) >= 0.999).sum()), floor_db=float(np.percentile(r, 3)))
json.dump(sync, open('work/sync.json', 'w'), indent=1)
print('clipped samples', sync['clipped'], 'noise floor', round(sync['floor_db'], 1), 'dB')
W = json.load(open('work/tx/words.json')) if os.path.exists('work/tx/words.json') else []
q = r < -35; i = 0
while i < n:
    if q[i]:
        j = i
        while j < n and q[j]: j += 1
        if j - i >= 10:
            s, e = i / 100, j / 100
            b4 = [x['text'] for x in W if x['end'] <= s + 0.15][-1:]; af = [x['text'] for x in W if x['start'] >= e - 0.15][:1]
            print(f'quiet {s:7.2f}-{e:7.2f} ({e-s:.2f}s)  {b4} | {af}')
        i = j
    else: i += 1
