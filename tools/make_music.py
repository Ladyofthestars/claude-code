"""Generates original, calm background music (no samples, no licensing issues): slow, soft
piano-like notes with a faint high shimmer, in a gentle hall reverb. Nothing sits low enough to
hum. Also adds soft "swell" sound effects for big moments.

Usage:
  python tools/make_music.py --seconds 570 --out music.wav [--swells 12.3,45.6]
"""
import argparse
import wave

import numpy as np
from scipy.signal import butter, oaconvolve, sosfilt

SR = 44100
BAR = 4.0  # seconds per bar (60 beats per minute, 4 beats)


def hz(name):
    """Note name like 'D4' or 'F#5' to frequency."""
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    n, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)


# Eight bars, then repeat: D – Bm – G – A, D/F# – G – Em – A(sus). The left hand plays one soft note per
# bar (never below D3, so there is no hum); the right hand plays the chord as slow broken notes, mostly
# in the bright middle of the keyboard.
PROGRESSION = [
    ('D3', ['A3', 'D4', 'F#4', 'A4', 'C#5', 'E5']),
    ('B3', ['B3', 'D4', 'F#4', 'B4', 'D5', 'F#5']),
    ('G3', ['B3', 'D4', 'G4', 'B4', 'D5', 'F#5']),
    ('A3', ['C#4', 'E4', 'A4', 'C#5', 'E5', 'A5']),
    ('F#3', ['A3', 'D4', 'F#4', 'A4', 'D5', 'F#5']),
    ('G3', ['B3', 'D4', 'G4', 'B4', 'D5', 'G5']),
    ('E3', ['B3', 'E4', 'G4', 'B4', 'E5', 'G5']),
    ('A3', ['A3', 'D4', 'E4', 'A4', 'D5', 'E5']),
]
# Broken-chord patterns: (beat, index into the chord, loudness).
PATTERNS = [
    [(0, 2, 1.0), (1, 3, 0.75), (2, 4, 0.8), (3, 3, 0.65)],
    [(0, 2, 1.0), (1, 4, 0.7), (2, 5, 0.8), (3, 4, 0.6)],
    [(0, 3, 1.0), (1.5, 4, 0.7), (2, 5, 0.75), (3, 2, 0.6)],
    [(0, 2, 1.0), (2, 4, 0.85), (2.5, 5, 0.6)],
]

_cache = {}


def piano(f):
    """One soft, felt-piano-like note at frequency f (cached; scaled later by loudness)."""
    if f in _cache:
        return _cache[f]
    dur = 6.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    t1 = 4.2 * (440 / f) ** 0.35  # lower notes ring longer
    for k in range(1, 8):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 9000:
            break
        amp = 1.0 / k ** 1.35
        tau = t1 / (1 + 0.55 * (k - 1))
        for det in (-0.0006, 0.0006):  # two slightly detuned strings
            out += (0.5 * amp * np.sin(2 * np.pi * fk * (1 + det) * t) * np.exp(-t / tau)).astype(np.float32)
    att = int(0.008 * SR)
    out[:att] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, att))
    rel = int(0.6 * SR)
    out[-rel:] *= np.linspace(1, 0, rel)
    _cache[f] = out
    return out


def place(buf, x, at, gain):
    s = int(max(0.0, at) * SR)
    if s >= len(buf):
        return
    e = min(len(buf), s + len(x))
    buf[s:e] += gain * x[:e - s]


def hall(n_ir, seed):
    """Synthetic hall reverb: decaying noise, darker as it fades."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_ir) / SR
    ir = rng.standard_normal(n_ir) * np.exp(-t / 0.75)
    ir = sosfilt(butter(2, 5000, 'low', fs=SR, output='sos'), ir)
    ir[:int(0.02 * SR)] = 0  # 20 ms pre-delay
    return (ir / np.sqrt(np.sum(ir ** 2))).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--swells', default='')
    a = ap.parse_args()
    n = int(a.seconds * SR)
    rng = np.random.default_rng(3)
    dry = np.zeros(n, np.float32)
    shimmer = np.zeros(n, np.float32)

    bars = int(np.ceil(a.seconds / BAR)) + 1
    for b in range(bars):
        t0 = b * BAR
        bass, chord = PROGRESSION[b % len(PROGRESSION)]
        # Every 4 bars switch pattern; the first 8 bars are sparser so the music enters gently.
        pat = PATTERNS[(b // 4) % len(PATTERNS)] if b >= 8 else PATTERNS[0][:2]
        place(dry, piano(hz(bass)), t0 + rng.normal(0, 0.01), 0.3)
        for beat, idx, vel in pat:
            at = t0 + beat * (BAR / 4) + rng.normal(0, 0.012)
            place(dry, piano(hz(chord[idx])), at, 0.55 * vel * rng.uniform(0.88, 1.05))
        # A high melody note now and then.
        if b >= 8 and b % 2 == 0:
            top = chord[-1] if rng.random() < 0.6 else chord[-2]
            f = hz(top) * 2 if hz(top) < 600 else hz(top)
            place(dry, piano(f), t0 + 2 * (BAR / 4) + rng.normal(0, 0.01), 0.32)
        # Shimmer: two very quiet high tones from the chord that fade in and out over the bar.
        L = int(BAR * 1.5 * SR)
        tt = np.arange(L) / SR
        env = np.sin(np.pi * tt / (BAR * 1.5)) ** 2
        for idx in (-1, -2):
            f = hz(chord[idx]) * 2
            place(shimmer, (np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * env).astype(np.float32), t0, 0.05)

    # Hall reverb, a little wider on one side than the other.
    n_ir = int(3.2 * SR)
    src = dry + shimmer
    left = 0.78 * dry + 0.55 * oaconvolve(src, hall(n_ir, 1))[:n]
    right = 0.78 * dry + 0.55 * oaconvolve(src, hall(n_ir, 2))[:n]

    # Remove anything low enough to hum or rumble, and soften the very top.
    hp = butter(4, 140, 'high', fs=SR, output='sos')
    lp = butter(2, 7000, 'low', fs=SR, output='sos')
    left = sosfilt(lp, sosfilt(hp, left)).astype(np.float32)
    right = sosfilt(lp, sosfilt(hp, right)).astype(np.float32)

    # Soft swells: airy noise that rises into the moment and fades away (no deep boom).
    srng = np.random.default_rng(7)
    bp = butter(2, [400, 4000], 'band', fs=SR, output='sos')
    for s in [float(x) for x in a.swells.split(',') if x.strip()]:
        start = int(max(0, s - 1.5) * SR)
        L = min(int(5.0 * SR), n - start)
        t = np.arange(L) / SR
        envs = np.where(t < 1.5, (t / 1.5) ** 2.5, np.exp(-(t - 1.5) / 1.2))
        for ch, buf in enumerate((left, right)):
            noise = sosfilt(bp, srng.standard_normal(L)).astype(np.float32)
            buf[start:start + L] += (0.35 * noise * envs).astype(np.float32)

    st = np.stack([left, right], axis=1)
    fi, fo = int(3 * SR), int(6 * SR)
    st[:fi] *= np.linspace(0, 1, fi)[:, None]
    st[-fo:] *= np.linspace(1, 0, fo)[:, None]
    rms = np.sqrt(np.mean(st ** 2)) + 1e-9
    st *= (10 ** (-26 / 20)) / rms
    st = np.clip(st, -0.98, 0.98)
    with wave.open(a.out, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((st * 32767).astype(np.int16).tobytes())
    print(f'wrote {a.out}: {a.seconds:.1f}s, {len([x for x in a.swells.split(",") if x.strip()])} swells')


if __name__ == '__main__':
    main()
