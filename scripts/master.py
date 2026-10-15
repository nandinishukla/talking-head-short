"""Sum the four stems, apply a transparent look-ahead true-peak limiter only where needed, measure everything.
Run from edit/. Writes final_master.wav and work/loudness.json."""
import numpy as np, soundfile as sf, subprocess, json, re
from scipy.signal import resample_poly
from scipy.ndimage import minimum_filter1d
SR = 48000; CEIL = 10 ** (-1.3 / 20)
x = sum(sf.read(f'stems/{k}.wav')[0] for k in ['voice', 'sfx', 'riser', 'music'])   # no per-stem changes
up = np.max(np.abs(resample_poly(x, 4, 1, axis=0)), axis=1).reshape(-1, 4).max(axis=1)[:len(x)]
need = np.minimum(1.0, CEIL / np.maximum(up, 1e-9))
g = minimum_filter1d(need, size=2 * int(0.005 * SR) + 1, mode='nearest')    # 5 ms look-ahead
rel = np.exp(-1 / (0.12 * SR)); out = np.empty_like(g); cur = 1.0             # 120 ms release, no pumping
for i in range(len(g)):
    cur = g[i] if g[i] < cur else cur * rel + g[i] * (1 - rel); out[i] = cur
sf.write('final_master.wav', x * out[:, None], SR, subtype='PCM_24')
print('limiter active on %.1f s, max reduction %.2f dB' % ((out < 0.999).sum() / SR, 20 * np.log10(out.min())))
def measure(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = re.findall(r'I:\s+(-?[\d.]+|-inf) LUFS', r); TP = re.findall(r'Peak:\s+(-?[\d.]+|-inf) dBFS', r)
    return dict(I=float(I[-1]) if I else float('-inf'), TP=float(TP[-1]) if TP else float('-inf'))
res = {k: measure(f'stems/{k}.wav') for k in ['voice', 'sfx', 'riser', 'music']}
res['master'] = measure('final_master.wav')
json.dump(res, open('work/loudness.json', 'w'), indent=1)
for k, v in res.items(): print(f'{k:7s} I {v["I"]:7.1f} LUFS   TP {v["TP"]:6.1f} dBTP')
cfg = json.load(open('project.json')) if __import__('os').path.exists('project.json') else {}
mus = cfg.get('music', {}); want = mus.get('lufs', -24.0)
music_ok = mus.get('mode') == 'none' or abs(res['music']['I'] - want) <= 0.5
ok = abs(res['voice']['I'] + 14) <= 0.5 and music_ok and res['master']['TP'] <= -1.0
print('LEVELS OK' if ok else 'LEVELS OFF TARGET')
