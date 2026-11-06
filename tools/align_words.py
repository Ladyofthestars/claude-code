"""Times every word of the script in recorded paragraphs (any voice engine), using speech recognition
(faster-whisper) and matching the heard words to the script's words. Writes pNN.json in the same
character-timing format tools/assemble_voice.py reads. Words the recogniser missed get times
in proportion between their matched neighbours.

Usage (Kokoro environment, which has faster-whisper):
  python tools/align_words.py CLIPS_DIR [--model small.en]
"""
import argparse
import difflib
import json
import os
import re

import numpy as np
import soundfile as sf

NUM = {'8': 'eight', '20': 'twenty', '1909': 'nineteen oh nine'}


def norm(w):
    return re.sub(r"[^a-z0-9']", '', w.lower().replace('’', "'"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('clips')
    ap.add_argument('--model', default='small.en')
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    import librosa

    model = WhisperModel(a.model, device='cpu', compute_type='int8')
    paras = json.load(open(os.path.join(a.clips, 'paras.json')))['paras']
    for p in paras:
        n = p['i']
        path = os.path.join(a.clips, f'p{n:02d}.wav')
        if not os.path.exists(path):
            continue
        x, sr = sf.read(path, dtype='float32')
        dur = len(x) / sr
        audio = librosa.resample(x, orig_sr=sr, target_sr=16000) if sr != 16000 else x
        segs, _ = model.transcribe(audio, language='en', word_timestamps=True, initial_prompt=p['text'][:200])
        heard = [w for s in segs for w in s.words]
        script = p['text'].split()
        A = [norm(w) for w in script]
        B = [norm(w.word) for w in heard]
        starts = [None] * len(script)
        ends = [None] * len(script)
        sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    starts[i1 + k] = heard[j1 + k].start
                    ends[i1 + k] = heard[j1 + k].end
            elif tag == 'replace' and j2 > j1:
                # spread the script words over the heard span (numbers said as words, etc.)
                t0, t1 = heard[j1].start, heard[j2 - 1].end
                cnt = i2 - i1
                for k in range(cnt):
                    starts[i1 + k] = t0 + (t1 - t0) * k / cnt
                    ends[i1 + k] = t0 + (t1 - t0) * (k + 1) / cnt
        # fill any gaps by interpolation between known neighbours
        known = [i for i in range(len(script)) if starts[i] is not None]
        if not known:
            starts = [dur * i / len(script) for i in range(len(script))]
            ends = [dur * (i + 1) / len(script) for i in range(len(script))]
        else:
            for i in range(len(script)):
                if starts[i] is None:
                    prev = max([k for k in known if k < i], default=None)
                    nxt = min([k for k in known if k > i], default=None)
                    t0 = ends[prev] if prev is not None else 0.0
                    t1 = starts[nxt] if nxt is not None else dur
                    lo = prev if prev is not None else -1
                    hi = nxt if nxt is not None else len(script)
                    f0 = (i - lo) / (hi - lo)
                    f1 = (i - lo + 1) / (hi - lo)
                    starts[i] = t0 + (t1 - t0) * f0 - (t1 - t0) * 0.0
                    ends[i] = t0 + (t1 - t0) * f1
        chars, cs, ce = [], [], []
        for k, w in enumerate(script):
            s, e = float(starts[k]), float(max(ends[k], starts[k] + 0.05))
            for j, c in enumerate(w):
                chars.append(c)
                cs.append(s + (e - s) * j / len(w))
                ce.append(s + (e - s) * (j + 1) / len(w))
            if k < len(script) - 1:
                chars.append(' ')
                cs.append(e)
                ce.append(e)
        json.dump({'characters': chars, 'character_start_times_seconds': cs, 'character_end_times_seconds': ce},
                  open(os.path.join(a.clips, f'p{n:02d}.json'), 'w'))
        miss = sum(1 for i in range(len(script)) if i not in known)
        print(f'p{n:02d}: {len(script)} words, {len(script) - miss} matched by ear, {miss} interpolated')


if __name__ == '__main__':
    main()
