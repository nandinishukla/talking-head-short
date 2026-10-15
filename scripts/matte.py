"""Background-removal mattes for every split run, keyed by SOURCE frame (so the head can never drift from the card,
even if the cut is retimed later). Run from edit/ after camtrack.py and plan.py.
  python matte.py [camtrack=work/camtrack.mp4]
Only unique source frames are matted (a 29.97 fps source shows each frame twice at 60 fps), at 540x960;
u2net works at 320 px internally, so full-res input buys nothing. CoreML first, CPU retry on failure."""
import json, subprocess, sys, os
CT = sys.argv[1] if len(sys.argv) > 1 else 'work/camtrack.mp4'
fm = json.load(open(CT.replace('.mp4', '_map.json'))); P = json.load(open('work/plan.json'))
SRC = 'work/camwide.mp4' if os.path.exists('work/camwide.mp4') else CT   # matte the footage the split card shows
SCALE = 'scale=960:540' if SRC.endswith('camwide.mp4') else 'scale=540:960'
H = os.path.abspath('tools/node_modules/.bin/hyperframes'); os.makedirs('work/matte', exist_ok=True)
for a, b, lay, name in P['runs']:
    if lay != 'split': continue
    key = name.split()[0]; f0, f1 = round(a / 1000 * 60), round(b / 1000 * 60)
    frames = []
    for i in range(f0, f1):
        if not frames or fm[i][2] != fm[frames[-1]][2]: frames.append(i)
    out = f'work/matte/{key}.mov'
    if os.path.exists(out) and json.load(open(f'work/matte/{key}.json'))['src'] == [fm[i][2] for i in frames]:
        print(key, 'up to date'); continue
    sel = '+'.join(f'eq(n\\,{i})' for i in frames)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vf', f"select='{sel}',{SCALE},setpts=N/30/TB", '-r', '30',
                    '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', f'work/matte/{key}_in.mp4'], check=True)
    for dev in ('auto', 'cpu'):
        rc = subprocess.run([H, 'remove-background', f'work/matte/{key}_in.mp4', '-o', out, '--device', dev],
                            stdout=open(f'work/matte/{key}.log', 'w'), stderr=subprocess.STDOUT).returncode
        if rc == 0 and os.path.exists(out): break
        print(key, f'remove-background failed on {dev}, retrying' if dev == 'auto' else 'FAILED on cpu too')
    json.dump(dict(src=[fm[i][2] for i in frames]), open(f'work/matte/{key}.json', 'w'))
    print(key, len(frames), 'unique frames matted ->', out)
