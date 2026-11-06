"""Makes the sound-effects track for a video: soft whooshes on picture changes, a deep hit on big
reveals, a riser into a new section and a shimmer on magical moments. All synthesised here (no
samples, no licensing issues), kept quiet and below the voice.

Events come from public/videos/<video>/sfx.json:
  [{"part": 0, "at": "1:You're not", "type": "hit"}, {"part": 0, "at": "2:Squeeze the", "type": "whoosh"}, ...]
"at" is "paragraph:phrase" (start of that phrase) or a number of seconds into the part; "offset" (s) is optional.

Usage: python tools/make_sfx.py VIDEO --seconds TOTAL --offsets 0,30.05,... --out sfx.wav
"""
import argparse
import json
import re
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(11)


def norm(s):
    return re.sub(r"[^a-z0-9']", '', s.lower())


def phrase_time(words, line, phrase):
    toks = [norm(t) for t in phrase.split() if norm(t)]
    ws = [w for w in words['words'] if w['line'] == line]
    for i in range(len(ws) - len(toks) + 1):
        if [norm(w['text']) for w in ws[i:i + len(toks)]] == toks:
            return ws[i]['start']
    raise SystemExit(f'sfx: phrase not found: {line}:{phrase}')


def env_ad(n, a, peak_at=None):
    t = np.arange(n) / SR
    peak = peak_at if peak_at is not None else a
    up = np.clip(t / peak, 0, 1) ** 2
    down = np.exp(-np.clip(t - peak, 0, None) / max(0.05, (n / SR - peak) / 3))
    return up * down


def whoosh():
    n = int(0.75 * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # sweep a band-pass through the noise in short blocks
    blk = 512
    for i in range(0, n, blk):
        u = i / n
        fc = 300 + 2600 * np.sin(np.pi * u) ** 1.5
        sos = butter(2, [fc * 0.6, min(fc * 1.6, 16000)], 'band', fs=SR, output='sos')
        out[i:i + blk] = sosfilt(sos, noise[i:i + blk])
    out *= env_ad(n, 0.0, peak_at=0.38)
    pan = np.linspace(-0.6, 0.6, n)
    L, R = out * (1 - pan) / 2, out * (1 + pan) / 2
    st = np.stack([L, R], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.10, 0.38


def hit():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = 42 + 38 * np.exp(-t / 0.08)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    click = sosfilt(butter(2, [800, 6000], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t / 0.012)
    air = sosfilt(butter(2, [200, 2500], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t / 0.35) * 0.25
    x = body + 0.35 * click + air
    x = sosfilt(butter(2, 38, 'high', fs=SR, output='sos'), x)
    st = np.stack([x, x], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.30, 0.0


def riser():
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    blk = 512
    for i in range(0, n, blk):
        u = i / n
        fc = 400 + 5000 * u ** 2
        sos = butter(2, [fc * 0.7, min(fc * 1.4, 18000)], 'band', fs=SR, output='sos')
        out[i:i + blk] = sosfilt(sos, noise[i:i + blk])
    tone = np.sin(2 * np.pi * np.cumsum(220 + 440 * (t / t[-1]) ** 2) / SR) * 0.15
    x = (out + tone) * (t / t[-1]) ** 2.5
    x[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR))
    st = np.stack([x, x], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.12, 2.2


def shimmer():
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(9):
        f = rng.uniform(1800, 5200)
        t0 = rng.uniform(0, 0.6)
        e = np.where(t > t0, np.exp(-(t - t0) / 0.6), 0)
        x += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * e * rng.uniform(0.4, 1.0)
    L = x * rng.uniform(0.6, 1.0)
    R = np.roll(x, int(0.011 * SR))
    st = np.stack([L, R], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.07, 0.0


KINDS = {'whoosh': whoosh, 'hit': hit, 'riser': riser, 'shimmer': shimmer}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--offsets', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    offsets = [float(x) for x in a.offsets.split(',')]
    events = json.load(open(f'public/videos/{a.video}/sfx.json'))
    out = np.zeros((int(a.seconds * SR) + SR * 3, 2))
    cache = {}
    for e in events:
        part = int(e.get('part', 0))
        if isinstance(e['at'], (int, float)):
            t = float(e['at'])
        else:
            line, phrase = e['at'].split(':', 1)
            words = cache.setdefault(part, json.load(open(f'public/videos/{a.video}/p{part}/words.json')))
            t = phrase_time(words, int(line), phrase)
        t += offsets[part] + float(e.get('offset', 0))
        snd, lead = KINDS[e['type']]()
        s = int(max(0, t - lead) * SR)
        out[s:s + len(snd)] += snd[:max(0, len(out) - s)]
    out = np.clip(out[:int(a.seconds * SR)], -0.95, 0.95)
    with wave.open(a.out, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())
    print(f'wrote {a.out}: {len(events)} sound effects')


if __name__ == '__main__':
    main()
