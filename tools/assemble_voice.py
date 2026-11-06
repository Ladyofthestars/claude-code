"""Joins paragraph recordings into one narration file per part, with natural pauses,
and writes each part's word timings for the video template.

Input:
  --paras  JSON {"paras": [{"part": 0, "i": 0, "text": "..."}...]}
  --clips  folder with pNN.mp3 or pNN.wav + pNN.json (character alignment, ElevenLabs format) per paragraph
  --out    public/videos/<video>   (writes p<part>/narration.wav and p<part>/words.json)

Pauses: a lead-in before each part (room for the chapter title), a gap between
paragraphs (longer after a question), and a tail after the last paragraph.
Word "line" = paragraph number inside its part (1-based), so settings can say "2:Big Bang".
"""
import argparse
import json
import os
import re
import subprocess
import wave

import numpy as np

SR = 44100


def decode(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def words_from_alignment(al, offset, line):
    words, cur = [], None
    for c, s, e in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if c.isspace():
            if cur:
                words.append(cur)
                cur = None
            continue
        if cur is None:
            cur = {'text': '', 'start': s + offset, 'end': e + offset, 'line': line}
        cur['text'] += c
        cur['end'] = e + offset
    if cur:
        words.append(cur)
    prev_end = True
    for w in words:
        # Mark sentence starts, so review stills can be taken at every sentence.
        w['sentence'] = prev_end
        prev_end = w['text'].rstrip('"').endswith(('.', '?', '!'))
        w['text'] = w['text'].strip('.,!?;:"')
        w['start'] = round(w['start'], 3)
        w['end'] = round(w['end'], 3)
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--paras', required=True)
    ap.add_argument('--clips', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--lead', type=float, default=1.8, help='silence before a chapter part starts')
    ap.add_argument('--first-lead', type=float, default=0.35, help='silence before the very first part')
    ap.add_argument('--gap', type=float, default=0.55, help='pause between paragraphs')
    ap.add_argument('--question-gap', type=float, default=0.8, help='pause after a paragraph ending in a question')
    ap.add_argument('--tail', type=float, default=1.0)
    ap.add_argument('--last-tail', type=float, default=3.0)
    ap.add_argument('--source', default='ElevenLabs, voice Brian (nPczCjzI2devNBz1zQrb), eleven_multilingual_v2, one paragraph at a time with previous/next text, character timestamps')
    a = ap.parse_args()

    paras = json.load(open(a.paras))['paras']
    parts = sorted({p['part'] for p in paras})
    norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('’', "'")).split()
    report = []
    for part in parts:
        mine = [p for p in paras if p['part'] == part]
        lead = a.first_lead if part == parts[0] else a.lead
        chunks = [np.zeros(int(lead * SR), np.float32)]
        t = lead
        words = []
        for k, p in enumerate(mine):
            n = paras.index(p)
            clip = os.path.join(a.clips, f'p{n:02d}.wav')
            audio = decode(clip if os.path.exists(clip) else os.path.join(a.clips, f'p{n:02d}.mp3'))
            al = json.load(open(os.path.join(a.clips, f'p{n:02d}.json')))
            got = words_from_alignment(al, t, k + 1)
            if norm(' '.join(w['text'] for w in got)) != norm(p['text']):
                raise SystemExit(f'Part {part} paragraph {k + 1}: timed words do not match the script')
            words += got
            chunks.append(audio)
            t += len(audio) / SR
            last = k == len(mine) - 1
            gap = (a.last_tail if part == parts[-1] else a.tail) if last else (a.question_gap if p['text'].rstrip().endswith('?') else a.gap)
            chunks.append(np.zeros(int(gap * SR), np.float32))
            t += gap
        audio = np.concatenate(chunks)
        d = os.path.join(a.out, f'p{part}')
        os.makedirs(d, exist_ok=True)
        with wave.open(os.path.join(d, 'narration.wav'), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
        dur = round(len(audio) / SR, 3)
        json.dump({'duration': dur, 'source': a.source, 'words': words}, open(os.path.join(d, 'words.json'), 'w'), indent=1)
        report.append((part, len(mine), len(words), dur))
    total = sum(r[3] for r in report)
    for part, n, nw, dur in report:
        print(f'part {part}: {n} paragraphs, {nw} words, {dur:.2f}s')
    print(f'total {total:.1f}s = {int(total // 60)}:{total % 60:04.1f}, words {sum(r[2] for r in report)}')


if __name__ == '__main__':
    main()
