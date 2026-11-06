"""Builds the settings for the new-format pilot (opening of "You've Never Actually Touched Anything").

New format: full-screen cinematic paintings, one every ~3 seconds, each with a slow push-in or pull-out
and a short dissolve; big kinetic words on the key lines; warm drifting dust; no title cards and no
dead air.

Usage: python tools/build_pilot.py [VIDEO] [IMAGE_VIDEO]
  VIDEO        folder under public/videos with p0/words.json (default pilot-touch)
  IMAGE_VIDEO  folder whose images/ to use (default: same as VIDEO)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from stars_lib import Part, Pictures  # noqa: E402

VIDEO = sys.argv[1] if len(sys.argv) > 1 else 'pilot-touch'
IMGV = sys.argv[2] if len(sys.argv) > 2 else VIDEO
ROOT = f'public/videos/{VIDEO}'
PICS = Pictures(f'public/videos/{IMGV}/images', f'/videos/{IMGV}/images')

THEME = {
    'background': '#04070e',
    'dotColor': 'rgba(0, 0, 0, 0)',
    'dotSpacing': 40,
    'dotSize': 0.1,
    'dotParallax': 0.75,
    'ink': '#ffffff',
    'accent': '#ffc865',
    'lightBlend': 'screen',
    'font': 'Montserrat',
    'labelGlow': 'rgba(0, 0, 0, 0.95)',
    'dust': {'count': 70, 'color': '#ffe2b0', 'size': 2.0, 'parallax': 0.45, 'drift': 7},
}

# (painting, when it appears)
SHOTS = [
    ('phone_touch', 'start'),
    ('touch_gap', '1:You never'),
    ('foot_floor', '1:Not the floor'),
    ('hands_held', '1:Not even the'),
    ('empty_atom', '2:Because every'),
    ('earth_night', '2:Squeeze the'),
    ('sugar_cube_glow', '2:would fit'),
    ('hand_table', '3:So why'),
    ('punch', '3:Why does a punch'),
    ('embrace', '3:And if nothing'),
    ('manchester', '4:To find out'),
    ('student_lab', '4:student named'),
    ('gold_foil', '4:firing tiny'),
    ('professor', '5:His professor'),
    ('shell_paper', '5:like firing'),
    ('nucleus_glow', '5:So what was'),
]


def word(p, text, at, out, size=96, y=780, accent=False, count=None):
    p.label(text, 960, y, at, out, size=size, space='screen', color='accent' if accent else None, spacing=0.06, count=count)


def main():
    words = json.load(open(f'{ROOT}/p0/words.json'))
    p = Part(PICS, 0, words)
    # Paintings: each dissolves in over the previous one, which leaves just after.
    for k, (name, at) in enumerate(SHOTS):
        nxt = SHOTS[k + 1][1] if k + 1 < len(SHOTS) else None
        out = f'{nxt}+0.4' if nxt else 'end-0.6'
        width = max(2120, 1110 * PICS.info[name]['aspect'])
        # the first painting is already there on frame one: the hook starts instantly
        p.painting(name, None if k == 0 else at, out, width=width, fade=0.35)
    # A soft cinematic vignette over everything, so the words always read.
    p.painting('vignette', None, None, width=2400, fade=0.3)
    # Camera: one slow move per shot, alternating push-in / pull-out with a gentle drift.
    for k, (_, at) in enumerate(SHOTS):
        z = 1.0 if k % 2 == 0 else 1.08
        x = (-28, 30, -18, 24)[k % 4]
        p.cam(at, x=x, y=0, zoom=z)
    p.cam('end', x=0, y=0, zoom=1.0 if len(SHOTS) % 2 == 0 else 1.08)
    # Kinetic words on the key lines.
    word(p, "YOU'RE NOT.", "1:You're not", '1:You never+0.6', size=120, y=540, accent=True)
    word(p, 'NOT ONCE.', '1:Not once', '2:Because every', size=120, y=540, accent=True)
    word(p, 'ALMOST ENTIRELY EMPTY', '2:almost entirely', '2:Squeeze the', size=80)
    word(p, '{n} PEOPLE', '2:every person', '2:would fit', size=84, count={'to': 8000000000, 'duration': 1.6})
    word(p, 'IN ONE SUGAR CUBE', '2:a sugar cube', '3:So why', size=92, accent=True)
    p.glows([(0, -10)], '2:a sugar cube', '3:So why', size=320)
    word(p, 'WHY DON\'T YOU SINK IN?', '3:sink into', '3:Why does a punch', size=80)
    word(p, 'WHY DOES IT HURT?', '3:punch still', '3:And if nothing', size=88)
    word(p, 'SO WHAT IS TOUCH?', '3:holds you', '4:To find out', size=96, accent=True)
    word(p, 'MANCHESTER · 1909', '4:Manchester', '4:student named', size=72, y=160)
    word(p, 'ERNEST MARSDEN, 20', '4:Ernest Marsden', '4:firing tiny', size=72, y=160)
    word(p, 'GOLD FOIL · THINNER THAN A HAIR', '4:thinner than', '4:And every few', size=64, y=160)
    word(p, 'ONE IN THOUSANDS CAME STRAIGHT BACK', '4:comes flying', '5:His professor', size=64, accent=True)
    p.glows([(-339, 166)], '4:comes flying', '5:His professor', size=260)
    word(p, 'ERNEST RUTHERFORD', '5:Ernest Rutherford', '5:like firing', size=72, y=160)
    word(p, 'LIKE A SHELL BOUNCING OFF TISSUE PAPER', '5:bounce back', '5:So what was', size=60, accent=True)
    word(p, 'SO WHAT WAS IT HITTING?', '5:So what was', 'end-0.6', size=100, y=540, accent=True)
    # Sound effects: a soft whoosh on each new painting, hits on the reveals, a riser into the story.
    sfx = [{'part': 0, 'at': at, 'type': 'whoosh'} for _, at in SHOTS[1:]]
    sfx += [{'part': 0, 'at': "1:You're not", 'type': 'hit'},
            {'part': 0, 'at': '1:Not once', 'type': 'hit'},
            {'part': 0, 'at': '2:a sugar cube', 'type': 'shimmer'},
            {'part': 0, 'at': '4:To find out', 'type': 'riser'},
            {'part': 0, 'at': '4:comes flying', 'type': 'hit'},
            {'part': 0, 'at': '5:bounce back', 'type': 'hit'}]
    json.dump(sfx, open(f'{ROOT}/sfx.json', 'w'), indent=1)
    s = p.settings(THEME, 'Pilot: You have never touched anything')
    s['clock'] = 0.0
    json.dump(s, open(f'{ROOT}/p0/settings.json', 'w'), indent=1)
    print(f'{VIDEO}: {len(p.items)} paintings, {len(p.labels)} words, {len(p.camera)} camera keys')


if __name__ == '__main__':
    main()
