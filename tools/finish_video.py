"""Joins the rendered parts into one video and gives it its final soundtrack.

1. Pads each part's narration to the exact length of its rendered video (so voice and
   picture never drift), and joins them.
2. Makes the music bed (tools/make_music.py) with soft swells at the given moments.
3. Mixes: music ducks under the voice; the mix is normalised for YouTube (-14 LUFS,
   true peak -1.5 dB).
4. Joins the part videos without re-encoding and adds the final soundtrack.

Usage: python tools/finish_video.py made-of-stars "2:1:Big Bang" "5:4:blown apart" "6:2:crash"
       (each swell = part:paragraph:phrase)
"""
import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np

SR = 44100
FPS = 60


def norm(s):
    return re.sub(r"[^a-z0-9']", '', s.lower())


def phrase_time(words, line, phrase):
    toks = [norm(t) for t in phrase.split() if norm(t)]
    ws = [w for w in words['words'] if w['line'] == line]
    for i in range(len(ws) - len(toks) + 1):
        if [norm(w['text']) for w in ws[i:i + len(toks)]] == toks:
            return ws[i]['start']
    raise SystemExit(f'phrase not found: {phrase}')


def main():
    video = sys.argv[1]
    swells = sys.argv[2:]
    root = f'public/videos/{video}'
    out = f'out/{video}'
    os.makedirs(out, exist_ok=True)
    parts = sorted(int(d[1:]) for d in os.listdir(root) if re.fullmatch(r'p\d+', d))
    offsets, chunks, total = {}, [], 0.0
    for n in parts:
        words = json.load(open(f'{root}/p{n}/words.json'))
        frames = math.ceil(words['duration'] * FPS)
        length = frames / FPS
        with wave.open(f'{root}/p{n}/narration.wav') as wf:
            a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16)
        target = int(round(length * SR))
        a = np.pad(a, (0, max(0, target - len(a))))[:target]
        chunks.append(a)
        offsets[n] = total
        total += length
    voice = np.concatenate(chunks)
    with wave.open(f'{out}/voice.wav', 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(voice.tobytes())
    times = []
    for s in swells:
        n, line, phrase = s.split(':', 2)
        words = json.load(open(f'{root}/p{n}/words.json'))
        times.append(offsets[int(n)] + phrase_time(words, int(line), phrase))
    py = sys.executable
    subprocess.run([py, 'tools/make_music.py', '--seconds', f'{total:.3f}', '--out', f'{out}/music.wav', '--swells', ','.join(f'{t:.3f}' for t in times)], check=True)
    # Duck the music under the voice, mix, and normalise for YouTube.
    subprocess.run([
        'ffmpeg', '-v', 'error', '-y', '-i', f'{out}/voice.wav', '-i', f'{out}/music.wav', '-filter_complex',
        '[0:a]aformat=channel_layouts=stereo,asplit=2[v][sc];'
        '[1:a][sc]sidechaincompress=threshold=0.02:ratio=4:attack=60:release=900:makeup=1[m];'
        '[v]volume=1.0[vv];[m]volume=0.55[mm];'
        '[vv][mm]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]',
        '-map', '[a]', '-ar', str(SR), f'{out}/mix.wav'], check=True)
    # Join the part videos (same codec settings) and add the final soundtrack.
    with open(f'{out}/parts.txt', 'w') as f:
        for n in parts:
            f.write(f"file '{os.path.abspath(f'{out}/p{n}.mp4')}'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{out}/parts.txt', '-i', f'{out}/mix.wav',
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'{out}/{video}.mp4'], check=True)
    print(f'total {total:.2f}s; part starts: ' + ', '.join(f'p{n} {offsets[n]:.2f}s' for n in parts))
    print('swells at ' + ', '.join(f'{t:.2f}s' for t in times))
    print(f'wrote {out}/{video}.mp4')


if __name__ == '__main__':
    main()
