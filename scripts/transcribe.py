"""Word-level transcript with faster-whisper. Run from edit/.
  python transcribe.py [model=medium.en] ["prompt with product names"]
Reads work/voice_src48.wav, writes work/tx/words.json and prints words with gaps > 250 ms marked
(use that listing to group words into takes)."""
import json, sys, os, subprocess
from faster_whisper import WhisperModel
model = sys.argv[1] if len(sys.argv) > 1 else 'medium.en'
prompt = sys.argv[2] if len(sys.argv) > 2 else None
os.makedirs('work/tx', exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/voice_src48.wav', '-ac', '1', '-ar', '16000', 'work/tx/v16.wav'], check=True)
m = WhisperModel(model, device='cpu', compute_type='int8')
segs, _ = m.transcribe('work/tx/v16.wav', language='en', word_timestamps=True, vad_filter=False,
                       condition_on_previous_text=False, beam_size=5, initial_prompt=prompt)
out = [dict(text=w.word.strip(), start=round(w.start, 3), end=round(w.end, 3), p=round(w.probability, 3)) for s in segs for w in s.words]
json.dump(out, open('work/tx/words.json', 'w'), indent=0)
for i, x in enumerate(out):
    gap = x['start'] - out[i - 1]['end'] if i else 0
    print(f"{i:3d} {x['start']:7.3f} {x['end']:7.3f} {x['p']:.2f} {x['text']}" + (f'   <<gap {gap:.2f}' if gap > 0.25 else ''))
