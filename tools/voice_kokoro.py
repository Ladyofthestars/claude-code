"""Records a script's narration with Kokoro (open-source text-to-speech, Apache 2.0), one paragraph
at a time, with the time of every word. Writes clips that tools/assemble_voice.py joins into parts.

Voice "A" (the channel voice from video 2 on): am_michael 70% + am_onyx 30% at speed 1.02, the closest
free match to the deep, calm narrator of video 1.

Usage (Python 3.12 environment from tools/setup_voice.sh):
  python tools/voice_kokoro.py projects/<video>/script.md OUT_DIR [--only 3,7]

OUT_DIR gets paras.json, and pNN.wav + pNN.json per paragraph (character timings in the same format
as ElevenLabs, so tools/assemble_voice.py reads them unchanged).
"""
import argparse
import json
import os
import re

import numpy as np
import soundfile as sf

SR = 24000
VOICE = {'am_michael': 0.7, 'am_onyx': 0.3}
SPEED = 1.02
# Pronunciation fixes, as Kokoro/misaki phonemes (checked by ear and with tools/proof_listen.py).
PRONOUNCE = {'Geiger': 'ɡˈIɡəɹ'}


def read_paras(script):
    """Narration paragraphs from script.md: '### Part N' headings and '> ' quote lines, up to section 2."""
    text = open(script).read()
    text = text.split('## 2.')[0]
    paras, part = [], None
    for line in text.splitlines():
        m = re.match(r'### Part (\d+)', line)
        if m:
            part = int(m.group(1))
            continue
        if line.startswith('> ') and part is not None:
            paras.append({'part': part, 'i': len(paras), 'text': line[2:].strip()})
    return paras


def alignment(tokens, offset, length):
    """Kokoro tokens -> ElevenLabs-style character timings (characters spread evenly over each word)."""
    chars, starts, ends = [], [], []
    for t in tokens:
        if t.start_ts is None or t.end_ts is None:
            continue
        s, e = t.start_ts + offset, min(t.end_ts + offset, length)
        n = max(1, len(t.text))
        for k, c in enumerate(t.text):
            chars.append(c)
            starts.append(s + (e - s) * k / n)
            ends.append(s + (e - s) * (k + 1) / n)
        if t.whitespace:
            chars.append(' ')
            starts.append(e)
            ends.append(e)
    return chars, starts, ends


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('out')
    ap.add_argument('--only', default='', help='comma-separated paragraph numbers to (re)record')
    ap.add_argument('--speed', type=float, default=SPEED, help='speaking speed (channel default 1.02)')
    a = ap.parse_args()
    from kokoro import KPipeline

    os.makedirs(a.out, exist_ok=True)
    paras = read_paras(a.script)
    json.dump({'paras': paras}, open(os.path.join(a.out, 'paras.json'), 'w'), indent=1)
    only = {int(x) for x in a.only.split(',') if x.strip()}
    pipe = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    voice = sum(w * pipe.load_voice(v) for v, w in VOICE.items())

    for p in paras:
        n = p['i']
        if only and n not in only:
            continue
        audio, chars, starts, ends, t = [], [], [], [], 0.0
        text = p['text']
        for word, ph in PRONOUNCE.items():
            text = re.sub(rf'\b{word}\b', f'[{word}](/{ph}/)', text)
        first_ts = None
        for r in pipe(text, voice=voice, speed=a.speed):
            if first_ts is None:
                timed = [tk.start_ts for tk in r.tokens if tk.start_ts is not None]
                first_ts = t + (timed[0] if timed else 0.0)
            x = r.audio.numpy()
            c, s, e = alignment(r.tokens, t, t + len(x) / SR)
            if chars and c and not chars[-1].isspace():
                chars.append(' ')
                starts.append(t)
                ends.append(t)
            chars += c
            starts += s
            ends += e
            audio.append(x)
            t += len(x) / SR
        x = np.concatenate(audio)
        # Trim the silence Kokoro leaves at both ends; keep a short natural edge.
        loud = np.where(np.abs(x) > 0.01)[0]
        # Start just before the first word as Kokoro timed it (a soft first word can be quieter
        # than the loudness threshold), or before the first loud sample, whichever is earlier.
        a0 = max(0, min(loud[0] - int(0.06 * SR), int(((first_ts or 0.0) - 0.08) * SR)))
        a1 = min(len(x), loud[-1] + int(0.12 * SR))
        x = x[a0:a1]
        shift = a0 / SR
        dur = len(x) / SR
        starts = [min(max(0.0, v - shift), dur) for v in starts]
        ends = [min(max(0.0, v - shift), dur) for v in ends]
        # Same loudness for every paragraph.
        rms = np.sqrt(np.mean(x ** 2)) + 1e-9
        x = np.clip(x * (10 ** (-20 / 20)) / rms, -0.99, 0.99)
        sf.write(os.path.join(a.out, f'p{n:02d}.wav'), x, SR)
        json.dump({'characters': chars, 'character_start_times_seconds': starts, 'character_end_times_seconds': ends},
                  open(os.path.join(a.out, f'p{n:02d}.json'), 'w'))
        print(f'p{n:02d} part {p["part"]}: {dur:.1f}s  {p["text"][:60]}', flush=True)


if __name__ == '__main__':
    main()
