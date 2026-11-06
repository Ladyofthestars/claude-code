"""Composes and renders an original soundtrack that changes with the story, played by real sampled
instruments: the FluidR3 GM soundfont (MIT licence, so safe for YouTube) through FluidSynth.

Every chapter gets its own section, with its own instruments, chords, rhythm and energy. Energy
builds through the video (a lift in the middle, where attention tends to dip), peaks near the end,
and resolves on solo piano and strings. Chapter changes land on the chapter-title pause, with a soft
harp sweep or timpani touch. Optional swells (a timpani roll, a reverse cymbal and a strings
crescendo) rise into big moments.

Needs: apt-get install fluidsynth fluid-soundfont-gm; pip install mido.

Usage:
  python tools/make_score.py --seconds 474.4 --sections 0,30.04,84.85 --out music.wav [--swells 12.3,45.6]
                             [--key D] [--seed 1]
"""
import argparse
import os
import subprocess
import tempfile
import wave

import mido
import numpy as np
from scipy.signal import butter, oaconvolve, sosfilt

SR = 44100
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
TPB = 480
KEYS = {'C': 60, 'C#': 61, 'D': 62, 'Eb': 63, 'E': 64, 'F': 65, 'F#': 66, 'G': 67, 'Ab': 68, 'A': 69, 'Bb': 70, 'B': 71}
MAJOR = [0, 2, 4, 5, 7, 9, 11]
DEGREE = {'I': 0, 'ii': 1, 'iii': 2, 'IV': 3, 'V': 4, 'vi': 5}

# General MIDI programs used (all from the FluidR3 GM soundfont).
PROG = {'piano': 0, 'celesta': 8, 'vibes': 11, 'cello': 42, 'trem': 44, 'pizz': 45, 'harp': 46, 'timp': 47,
        'strings': 48, 'slowstr': 49, 'choir': 52, 'revcym': 119}
CHAN = {'piano': 0, 'celesta': 1, 'vibes': 2, 'cello': 3, 'trem': 4, 'pizz': 5, 'harp': 6, 'timp': 7,
        'strings': 8, 'slowstr': 10, 'choir': 11, 'revcym': 12}

# The story arc. Each chapter section picks the next preset: layers, chords, tempo and energy.
PRESETS = [
    dict(name='hook', bpm=66, prog=['vi', 'IV', 'I', 'V'], layers=['motif', 'high'], energy=0.42),
    dict(name='flow', bpm=72, prog=['I', 'V', 'vi', 'IV'], layers=['harp', 'motif', 'pad'], energy=0.5),
    dict(name='reflect', bpm=66, prog=['vi', 'iii', 'IV', 'I'], layers=['pad', 'celesta', 'lowpiano'], energy=0.45),
    dict(name='journey', bpm=76, prog=['I', 'iii', 'vi', 'IV', 'I', 'V', 'IV', 'V'], layers=['pizz', 'harp', 'motif', 'pad'], energy=0.6),
    dict(name='clock', bpm=80, prog=['vi', 'V', 'IV', 'V'], layers=['pizz8', 'celesta', 'pad', 'motif'], energy=0.66, lift=2),
    dict(name='deep', bpm=70, prog=['IV', 'I', 'vi', 'V'], layers=['cello', 'lowpiano', 'pad', 'harp'], energy=0.55, lift=2),
    dict(name='tension', bpm=72, prog=['vi', 'IV', 'ii', 'V'], layers=['trem', 'timp', 'lowpiano', 'cello'], energy=0.68),
    dict(name='wonder', bpm=74, prog=['IV', 'V', 'iii', 'vi', 'ii', 'V', 'I', 'I'], layers=['pad', 'harp', 'choir', 'motif', 'celesta'], energy=0.82),
    dict(name='ending', bpm=66, prog=['I', 'V', 'vi', 'IV'], layers=['motif', 'pad'], energy=0.45, ending=True),
]


def chord_notes(root, degree, lift=0):
    """Triad (plus the 7th degree as colour) on a scale degree; returns semitones from the key root."""
    d = DEGREE[degree]
    tones = [MAJOR[(d + k) % 7] + 12 * ((d + k) // 7) for k in (0, 2, 4, 6)]
    return [root + lift + t for t in tones]


class Track:
    """Collects note events in seconds for one section, then writes a MIDI file."""

    def __init__(self, bpm):
        self.bpm = bpm
        self.ev = []  # (time_s, order, message)

    def sec(self, beats):
        return beats * 60.0 / self.bpm

    def program(self, inst, t=0.0):
        self.ev.append((t, 0, mido.Message('program_change', channel=CHAN[inst], program=PROG[inst])))

    def cc(self, inst, ctrl, val, t=0.0):
        self.ev.append((t, 1, mido.Message('control_change', channel=CHAN[inst], control=ctrl, value=int(np.clip(val, 0, 127)))))

    def note(self, inst, pitch, t, dur, vel):
        ch = CHAN[inst]
        if inst == 'timp_drum':
            ch = 9
        pitch = int(np.clip(pitch, 21, 108))
        vel = int(np.clip(vel, 1, 127))
        self.ev.append((t, 2, mido.Message('note_on', channel=ch, note=pitch, velocity=vel)))
        self.ev.append((t + dur, 1, mido.Message('note_off', channel=ch, note=pitch, velocity=0)))

    def swell(self, inst, t0, t1, lo, hi, steps=24):
        """Expression (CC11) ramp from lo to hi between t0 and t1."""
        for k in range(steps + 1):
            u = k / steps
            self.cc(inst, 11, lo + (hi - lo) * u, t0 + (t1 - t0) * u)

    def write(self, path, end_s):
        mid = mido.MidiFile(ticks_per_beat=TPB)
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        tempo = mido.bpm2tempo(self.bpm)
        tr.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
        ev = sorted(self.ev, key=lambda e: (e[0], e[1]))
        last = 0
        for t, _, msg in ev:
            tick = int(round(mido.second2tick(max(0.0, t), TPB, tempo)))
            msg.time = max(0, tick - last)
            last = max(last, tick)
            tr.append(msg)
        end_tick = int(round(mido.second2tick(end_s, TPB, tempo)))
        tr.append(mido.MetaMessage('end_of_track', time=max(0, end_tick - last)))
        mid.save(path)


def compose(preset, length, root, rng, swells, first, last):
    """One chapter section as note events: length in seconds; swells in seconds from its start."""
    P = preset
    tr = Track(P['bpm'])
    E = P['energy']
    beat = tr.sec(1)
    bar = 4 * beat
    nbars = int(np.ceil(length / bar)) + 1
    lift = P.get('lift', 0)
    for inst in PROG:
        tr.program(inst)
        tr.cc(inst, 7, 100)
        tr.cc(inst, 11, 100)
        tr.cc(inst, 91, 70)  # reverb send
    tr.cc('pizz', 7, 92)
    tr.cc('celesta', 7, 80)
    tr.cc('choir', 7, 70)
    tr.cc('revcym', 7, 70)
    # A short melodic idea for this section, varied as it repeats.
    rhythms = [[(0, 1.5), (1.5, 0.5), (2, 2)], [(0, 1), (1, 1), (2, 1.5), (3.5, 0.5)], [(0, 2), (2, 1), (3, 1)],
               [(0.5, 1), (1.5, 1.5), (3, 1)]]
    motif_r = [rhythms[rng.integers(len(rhythms))], rhythms[rng.integers(len(rhythms))]]
    contour = rng.choice([-2, -1, 1, 2], size=8)
    prev_top = root + 12 + rng.choice([4, 7])
    # Each section opens on its chapter-title pause with a soft colour.
    if not first:
        if rng.random() < 0.5 or 'harp' in P['layers']:
            ch = chord_notes(root, P['prog'][0], lift)
            for k, n in enumerate(sorted(ch * 2)[:7]):
                tr.note('harp', n + (12 if k >= 4 else 0), 0.05 + k * 0.07, 2.5, 38 + 3 * k)
        else:
            tr.note('timp', root - 24 + (0 if root - 24 >= 38 else 12), 0.05, 2.0, 46)
    for b in range(nbars):
        t0 = b * bar
        if t0 >= length + 0.5:
            break
        deg = P['prog'][b % len(P['prog'])]
        ch = chord_notes(root, deg, lift)
        rootn = ch[0]
        # gentle rise through the section (each ends on a question), and a soft start
        grow = min(1.0, 0.75 + 0.35 * b / max(1, nbars - 1))
        enter = 0.6 if (b == 0 and first) else 1.0
        e = E * grow * enter
        if P.get('ending') and t0 > length - 2.5 * bar:
            e *= 0.8
        layers = P['layers']
        if 'motif' in layers:
            # left hand: root and fifth; right hand: the motif
            tr.note('piano', rootn - 12, t0 + rng.normal(0, 0.01), 3.5 * beat, 34 + 26 * e)
            if b % 2 == 1:
                tr.note('piano', rootn - 5, t0 + 2 * beat, 2 * beat, 30 + 22 * e)
            r = motif_r[b % 2]
            if b % 4 == 3 and rng.random() < 0.5:
                r = r[:2]  # leave space at phrase ends
            pool = sorted(set([n + 12 for n in ch] + [n + 24 for n in ch[:2]]))
            for k, (on, du) in enumerate(r):
                target = prev_top + contour[(b * 3 + k) % len(contour)]
                n = min(pool, key=lambda x: abs(x - target))
                n = int(np.clip(n, root + 5, root + 26))
                prev_top = n
                tr.note('piano', n, t0 + on * beat + rng.normal(0, 0.012), du * beat * 1.4, 44 + 30 * e + rng.normal(0, 4))
        if 'lowpiano' in layers:
            for k, idx in enumerate([0, 2, 1, 2]):
                n = ch[idx] - 12 + (12 if idx == 1 else 0)
                tr.note('piano', n, t0 + k * beat + rng.normal(0, 0.01), 1.6 * beat, 30 + 22 * e)
        if 'pad' in layers or 'high' in layers:
            inst = 'strings' if 'pad' in layers else 'slowstr'
            octave = 0 if 'pad' in layers else 12
            voicing = [ch[0] - 12 + octave, ch[1] + octave, ch[2] + octave] + ([ch[3] + octave] if rng.random() < 0.4 else [])
            for n in voicing:
                tr.note(inst, n, t0, bar + 0.05, 40 + 34 * e)
            # breathing: a slow rise over one bar and an easing over the next, so the chords never sit still
            lo, hi = 66 + 18 * e, 90 + 28 * e
            if b % 2 == 0:
                tr.swell(inst, t0, t0 + bar, lo, hi, 12)
            else:
                tr.swell(inst, t0, t0 + bar, hi, lo, 12)
        if 'trem' in layers:
            for n in [ch[0], ch[2], ch[1] + 12]:
                tr.note('trem', n, t0, bar + 0.05, 36 + 34 * e)
            tr.swell('trem', t0, t0 + bar, 60 + 25 * e, 90 + 30 * e, 12)
        if 'cello' in layers:
            n = rootn - 12
            while n > 55:
                n -= 12
            while n < 43:
                n += 12
            tr.note('cello', n, t0, bar * 0.98, 44 + 30 * e)
            tr.swell('cello', t0, t0 + bar, 70, 100, 8)
        if 'harp' in layers:
            arp = sorted(set(ch[:3] + [n + 12 for n in ch[:3]] + [ch[0] + 24]))
            step = 0.5 if e > 0.5 else 1.0
            k = 0
            pos = 0.0
            while pos < 4:
                idx = k % (2 * len(arp) - 2)
                idx = idx if idx < len(arp) else 2 * len(arp) - 2 - idx
                tr.note('harp', arp[idx], t0 + pos * beat + rng.normal(0, 0.008), 1.5 * beat, 34 + 26 * e + rng.normal(0, 3))
                pos += step
                k += 1
        if 'pizz' in layers or 'pizz8' in layers:
            step = 0.5 if 'pizz8' in layers else 1.0
            pat = [0, 2, 1, 2, 0, 2, 3, 2]
            pos, k = 0.0, 0
            while pos < 4:
                n = ch[pat[k % len(pat)] % len(ch)]
                n = n - 12 if n > root + 7 else n
                accent = 1.15 if pos in (0.0, 2.0) else 0.9
                tr.note('pizz', n, t0 + pos * beat + rng.normal(0, 0.006), 0.6 * beat, (34 + 32 * e) * accent)
                pos += step
                k += 1
        if 'celesta' in layers:
            for pos in np.arange(0, 4, 0.5):
                if rng.random() < 0.22 + 0.15 * e:
                    n = int(rng.choice(ch)) + 24
                    tr.note('celesta', n, t0 + pos * beat, 1.2 * beat, 30 + 26 * e)
        if 'choir' in layers and b % 2 == 0:
            for n in [ch[0], ch[2], ch[1] + 12]:
                tr.note('choir', n, t0, 2 * bar, 26 + 26 * e)
            tr.swell('choir', t0, t0 + 2 * bar, 50, 100, 12)
        if 'timp' in layers and b % 4 == 0:
            n = rootn - 24
            while n < 41:
                n += 12
            tr.note('timp', n, t0, 2 * beat, 40 + 26 * e)
    # Swells into big moments: timpani roll + reverse cymbal + a strings crescendo, peaking at the moment.
    for s in swells:
        bi = int(max(0, s) // bar)
        ch = chord_notes(root, P['prog'][bi % len(P['prog'])], lift)
        n = ch[0] - 24
        while n < 41:
            n += 12
        for k in range(int(1.8 / 0.075)):
            t = s - 1.8 + k * 0.075
            if t > 0:
                tr.note('timp', n, t, 0.1, 22 + 40 * k / 24)
        tr.note('timp', n, s, 2.5, 66)
        tr.note('revcym', 60, max(0, s - 2.2), 2.25, 60)
        for nn in [ch[0], ch[2], ch[1] + 12, ch[0] + 12]:
            tr.note('slowstr', nn, max(0, s - 1.5), 5.0, 60)
        tr.swell('slowstr', max(0, s - 1.5), s, 50, 120, 10)
        tr.swell('slowstr', s, s + 5, 120, 60, 10)
    if last:
        # Final resolution: tonic chord held on strings and piano, fading out.
        t = max(0.0, length - 4.5)
        ch = chord_notes(root, 'I', 0)
        for n in [ch[0] - 12, ch[0], ch[1], ch[2], ch[0] + 12]:
            tr.note('strings', n, t, 6.0, 50)
        for n in [ch[0] - 12, ch[2], ch[0] + 12, ch[1] + 12]:
            tr.note('piano', n, t, 5.0, 46)
        tr.swell('strings', t, t + 6, 100, 30, 14)
    return tr


def render(tr, end_s, workdir, idx):
    mid = os.path.join(workdir, f's{idx}.mid')
    wav = os.path.join(workdir, f's{idx}.wav')
    tr.write(mid, end_s)
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.5', '-r', str(SR), '-R', '1', '-C', '0', '-F', wav, SF2, mid],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(wav) as wf:
        ch = wf.getnchannels()
        a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768.0
    a = a.reshape(-1, ch)
    return a if ch == 2 else np.repeat(a, 2, axis=1)


def hall(n_ir, seed):
    rng = np.random.default_rng(seed)
    t = np.arange(n_ir) / SR
    ir = rng.standard_normal(n_ir) * np.exp(-t / 0.9)
    ir = sosfilt(butter(2, 6000, 'low', fs=SR, output='sos'), ir)
    ir[:int(0.025 * SR)] = 0
    return (ir / np.sqrt(np.sum(ir ** 2))).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--sections', required=True, help='section start times in seconds (chapter starts)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--swells', default='')
    ap.add_argument('--key', default='D')
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    total = a.seconds
    starts = [float(x) for x in a.sections.split(',') if x.strip()]
    swells = [float(x) for x in a.swells.split(',') if x.strip()]
    rng = np.random.default_rng(a.seed)
    base = KEYS[a.key]
    # Key plan: home key, a lift up a tone in the middle (attention reset), back home for the end.
    n = len(starts)
    presets = [PRESETS[min(len(PRESETS) - 2, round(i * (len(PRESETS) - 2) / max(1, n - 2)))] for i in range(n - 1)] + [PRESETS[-1]]
    out = np.zeros((int(total * SR) + SR, 2), np.float32)
    xfade = 1.6
    with tempfile.TemporaryDirectory() as wd:
        for i, t0 in enumerate(starts):
            t1 = starts[i + 1] if i + 1 < n else total
            length = t1 - t0
            P = presets[i]
            root = base + (2 if P['name'] in ('clock', 'deep') else 0)
            mine = [s - t0 for s in swells if t0 <= s < t1]
            tr = compose(P, length, root, rng, mine, i == 0, i == n - 1)
            audio = render(tr, length + 4.0, wd, i)
            s0 = int(t0 * SR)
            seg = audio[:int((length + (xfade if i + 1 < n else 0.0)) * SR)].copy()
            fi = int(0.25 * SR)
            seg[:fi] *= np.linspace(0, 1, fi)[:, None]
            if i + 1 < n:
                fo = int(xfade * SR)
                seg[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
            e = min(len(out), s0 + len(seg))
            out[s0:e] += seg[:e - s0]
            print(f'  section {i}: {P["name"]:8s} {t0:7.2f}s–{t1:7.2f}s  key {"+2" if root != base else "home"}  swells {len(mine)}')
    out = out[:int(total * SR)]
    # A little shared hall for cohesion; trim rumble (but keep the body) and the harsh top.
    n_ir = int(2.6 * SR)
    wetL = oaconvolve(out[:, 0], hall(n_ir, 1))[:len(out)]
    wetR = oaconvolve(out[:, 1], hall(n_ir, 2))[:len(out)]
    out = np.stack([0.85 * out[:, 0] + 0.28 * wetL, 0.85 * out[:, 1] + 0.28 * wetR], axis=1).astype(np.float32)
    hp = butter(2, 55, 'high', fs=SR, output='sos')
    lp = butter(2, 11000, 'low', fs=SR, output='sos')
    out = sosfilt(lp, sosfilt(hp, out, axis=0), axis=0).astype(np.float32)
    fi, fo = int(2.0 * SR), int(3.0 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    rms = np.sqrt(np.mean(out ** 2)) + 1e-9
    out *= (10 ** (-27 / 20)) / rms
    peak = np.max(np.abs(out))
    if peak > 0.95:
        out *= 0.95 / peak
    with wave.open(a.out, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())
    print(f'wrote {a.out}: {total:.1f}s, {n} sections, {len(swells)} swells')


if __name__ == '__main__':
    main()
