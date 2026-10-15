"""QA the audio joins in the J-cut voice track: longest quiet run (< -35 dB source-relative) around each join.
Any join over 150 ms -> add a negative gap_override for that segment index in project.json and re-run cut.py."""
import soundfile as sf, numpy as np, json
v, sr = sf.read('work/voice_raw.wav'); m = v.mean(1); w = 480; n = len(m) // w
r = 20 * np.log10(np.sqrt(np.mean(m[:n * w].reshape(n, w) ** 2, 1)) + 1e-9)
E = json.load(open('work/edl.json')); bad = []
for k in range(1, len(E['segs'])):
    j = E['segs'][k]['cut']; q = r[int((j - 0.5) * 100):int((j + 0.5) * 100)] < -35
    best = c = 0
    for x in q: c = c + 1 if x else 0; best = max(best, c)
    flag = '  <-- over 150 ms' if best * 10 > 150 else ''
    if flag: bad.append(k)
    print(f'segment {k:2d} join at {j:6.3f}s: longest quiet {best*10} ms{flag}')
print('joins to fix (segment indices):', bad or 'none')
