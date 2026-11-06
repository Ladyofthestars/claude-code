"""Proof-listens recorded narration with speech recognition (faster-whisper) and lists every place
where what was heard differs from the script, so mumbled, skipped or wrong words can be re-recorded.

Usage: python tools/proof_listen.py CLIPS_DIR [--model small.en]
CLIPS_DIR has paras.json and pNN.wav (from tools/voice_kokoro.py).
"""
import argparse
import difflib
import json
import os
import re

NUM = {'120': 'one hundred twenty', '5,730': 'five thousand seven hundred thirty', '50,000': 'fifty thousand',
       '200': 'two hundred', '350': 'three hundred fifty', '12': 'twelve', '14': 'fourteen'}


def norm(s):
    s = s.lower().replace('’', "'").replace('-', ' ')
    s = re.sub(r"[^a-z0-9' ]", ' ', s)
    return s.split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('clips')
    ap.add_argument('--model', default='small.en')
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    global sf, librosa
    import soundfile as sf
    import librosa
    model = WhisperModel(a.model, device='cpu', compute_type='int8')
    paras = json.load(open(os.path.join(a.clips, 'paras.json')))['paras']
    issues = 0
    for p in paras:
        x, sr = sf.read(os.path.join(a.clips, f"p{p['i']:02d}.wav"), dtype='float32')
        x = librosa.resample(x, orig_sr=sr, target_sr=16000) if sr != 16000 else x
        segs, _ = model.transcribe(x, language='en', beam_size=5)
        heard = ' '.join(s.text for s in segs)
        want = p['text']
        for k, v in NUM.items():
            want = want.replace(k, v)
            heard = heard.replace(k, v)
        A, B = norm(want), norm(heard)
        diffs = [(op, ' '.join(A[i1:i2]), ' '.join(B[j1:j2])) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B).get_opcodes() if op != 'equal']
        if diffs:
            issues += 1
            print(f"p{p['i']:02d}: " + ' | '.join(f'script "{x}" -> heard "{y}"' for _, x, y in diffs))
    print(f'{issues} of {len(paras)} paragraphs differ')


if __name__ == '__main__':
    main()
