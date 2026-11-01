"""Generates an original, calm ambient music bed (no samples, no licensing issues),
plus soft "swell" sound effects for big moments.

Usage:
  python tools/make_music.py --seconds 570 --out music.wav [--swells 12.3,45.6]
"""
import argparse
import wave

import numpy as np

SR = 44100


def note(f, n, seed):
    """A soft pad voice: three slightly detuned sines plus a quiet octave, slowly breathing."""
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for det in (-0.0018, 0.0, 0.0021):
        ph = rng.uniform(0, 2 * np.pi)
        out += np.sin(2 * np.pi * f * (1 + det) * t + ph).astype(np.float32)
    out += 0.16 * np.sin(2 * np.pi * 2 * f * t + rng.uniform(0, 6)).astype(np.float32)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * rng.uniform(0.03, 0.07) * t + rng.uniform(0, 6))
    return out * lfo.astype(np.float32)


def lowpass(x, cutoff):
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([1 - a], [1, -a], x).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--swells', default='')
    a = ap.parse_args()
    n = int(a.seconds * SR)

    # A slow, warm progression in D major: Dmaj9 – Bm7 – Gmaj7 – A(sus4), 16 s each.
    chords = [
        [146.83, 220.00, 329.63, 369.99],
        [123.47, 185.00, 293.66, 440.00],
        [98.00, 146.83, 246.94, 369.99],
        [110.00, 164.81, 293.66, 329.63],
    ]
    seg, xf = 16.0, 6.0
    mix = np.zeros(n + int((seg + xf) * SR), np.float32)
    k = 0
    pos = 0
    while pos < n:
        ch = chords[k % len(chords)]
        L = int((seg + xf) * SR)
        env = np.ones(L, np.float32)
        r = int(xf * SR)
        env[:r] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, r))
        env[-r:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
        block = np.zeros(L, np.float32)
        for i, f in enumerate(ch):
            block += note(f, L, seed=k * 10 + i) * (0.9 if i == 0 else 0.6)
        # A faint shimmer an octave above the top note.
        t = np.arange(L) / SR
        block += 0.10 * np.sin(2 * np.pi * ch[-1] * 2 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t))
        mix[pos:pos + L] += block * env
        pos += int(seg * SR)
        k += 1
    mix = mix[:n]
    try:
        mix = lowpass(mix, 1800)
    except Exception:
        pass

    # Soft swells: filtered noise that rises and fades, with a deep, quiet tone underneath.
    rng = np.random.default_rng(7)
    for s in [float(x) for x in a.swells.split(',') if x.strip()]:
        start = int(max(0, s - 1.2) * SR)
        L = int(4.5 * SR)
        if start + L > n:
            L = n - start
        t = np.arange(L) / SR
        envs = np.where(t < 1.2, (t / 1.2) ** 2, np.exp(-(t - 1.2) / 1.1))
        noise = rng.standard_normal(L).astype(np.float32)
        try:
            noise = lowpass(noise, 700)
        except Exception:
            pass
        boom = np.sin(2 * np.pi * 55 * t) * np.exp(-np.maximum(0, t - 1.2) / 1.6) * (t > 1.1)
        mix[start:start + L] += (0.9 * noise * envs + 1.4 * boom).astype(np.float32)

    # Gentle fade in and out, then normalise to a quiet level (it sits under the voice).
    fi, fo = int(3 * SR), int(6 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    rms = np.sqrt(np.mean(mix ** 2)) + 1e-9
    mix *= (10 ** (-24 / 20)) / rms
    mix = np.clip(mix, -0.98, 0.98)
    # Slight stereo width: the right channel a few milliseconds later.
    d = int(0.012 * SR)
    right = np.concatenate([np.zeros(d, np.float32), mix[:-d]])
    st = np.stack([mix, right], axis=1)
    with wave.open(a.out, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((st * 32767).astype(np.int16).tobytes())
    print(f'wrote {a.out}: {a.seconds:.1f}s, {len([x for x in a.swells.split(",") if x.strip()])} swells')


if __name__ == '__main__':
    main()
