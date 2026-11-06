"""Records a script's narration with Chatterbox (open source, MIT licence), which delivers lines with
more energy and emotion than Kokoro. It speaks in the voice of a short reference clip; we use a clip
of the channel voice made with Kokoro, so the voice stays the same and only the delivery changes.

Word timings come afterwards from tools/align_words.py (speech recognition, matched to the script).

Usage (Chatterbox environment):
  python tools/voice_chatterbox.py projects/<video>/script.md OUT_DIR --ref REF.wav [--only 0,3]
         [--exaggeration 0.6] [--cfg 0.45]
"""
import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
from voice_kokoro import PRONOUNCE, read_paras  # noqa: E402

# Chatterbox reads plain text; spell tricky words the way they should sound.
SPELL = {'Geiger': 'Guy-ger'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('out')
    ap.add_argument('--ref', required=True, help='reference clip of the voice to use')
    ap.add_argument('--only', default='')
    ap.add_argument('--exaggeration', type=float, default=0.6)
    ap.add_argument('--cfg', type=float, default=0.45)
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args()
    import torch
    from chatterbox.tts import ChatterboxTTS

    torch.manual_seed(a.seed)
    os.makedirs(a.out, exist_ok=True)
    paras = read_paras(a.script)
    json.dump({'paras': paras}, open(os.path.join(a.out, 'paras.json'), 'w'), indent=1)
    only = {int(x) for x in a.only.split(',') if x.strip()}
    model = ChatterboxTTS.from_pretrained(device='cpu')
    sr = model.sr
    for p in paras:
        n = p['i']
        if only and n not in only:
            continue
        text = p['text']
        for w, s in SPELL.items():
            text = text.replace(w, s)
        wav = model.generate(text, audio_prompt_path=a.ref, exaggeration=a.exaggeration, cfg_weight=a.cfg)
        x = wav.squeeze().cpu().numpy().astype(np.float32)
        loud = np.where(np.abs(x) > 0.01)[0]
        a0 = max(0, loud[0] - int(0.05 * sr))
        a1 = min(len(x), loud[-1] + int(0.12 * sr))
        x = x[a0:a1]
        rms = np.sqrt(np.mean(x ** 2)) + 1e-9
        x = np.clip(x * (10 ** (-20 / 20)) / rms, -0.99, 0.99)
        sf.write(os.path.join(a.out, f'p{n:02d}.wav'), x, sr)
        print(f'p{n:02d} part {p["part"]}: {len(x) / sr:.1f}s  {p["text"][:60]}', flush=True)


if __name__ == '__main__':
    main()
