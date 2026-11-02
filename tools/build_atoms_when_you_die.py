"""Builds public/videos/atoms-when-you-die/p0..p8/settings.json from the shot list in
projects/atoms-when-you-die/script.md.

Same method as tools/build_made_of_stars.py (one camera, parts joined where the previous camera
ended), with the blue page: glowing white lines, gold highlights, drifting dust and atom streams.
Run: python tools/build_atoms_when_you_die.py
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from stars_lib import AMBIGUOUS, T, Part, Pictures  # noqa: E402

ROOT = 'public/videos/atoms-when-you-die'
PICS = Pictures(f'{ROOT}/images', '/videos/atoms-when-you-die/images')
THEME = {
    'background': '#0c1d3a',
    'backgroundImage': 'radial-gradient(ellipse 70% 65% at 50% 42%, rgba(46, 92, 168, 0.55) 0%, rgba(24, 52, 104, 0.28) 45%, rgba(6, 14, 32, 0) 75%), '
                       'radial-gradient(ellipse 130% 110% at 50% 50%, rgba(0, 0, 0, 0) 55%, rgba(2, 6, 16, 0.7) 100%)',
    'dotColor': 'rgba(190, 215, 255, 0.10)',
    'dotSpacing': 40,
    'dotSize': 1.5,
    'dotParallax': 0.75,
    'ink': '#eef4ff',
    'accent': '#ffc865',
    'lightBlend': 'screen',
    'font': 'Montserrat',
    'labelGlow': 'rgba(130, 175, 255, 0.55)',
    'drawingGlow': 'rgba(130, 175, 255, 0.55)',
    'dust': {'count': 60, 'color': '#cfe0ff', 'size': 1.8, 'parallax': 0.45, 'drift': 5},
}
TITLES = {
    1: 'ARE YOUR ATOMS REALLY YOURS?',
    2: 'WHAT HAPPENS WHEN YOU DIE?',
    3: 'WHERE DOES IT GO NEXT?',
    4: 'WHICH ATOMS CHANGE?',
    5: 'WHERE DO YOUR BONES GO?',
    6: 'DOES THE EARTH KEEP THEM FOREVER?',
    7: 'WHERE DO THEY GO IN THE END?',
}
CHEST = (0.49, 0.40)
FACE = (0.495, 0.29)
ARM = (0.40, 0.50)
LUNGS_TOP = (0.5, 0.2)
BUST_LIPS = (0.55, 0.45)


def chapter(p, n, first):
    """Chapter title on the empty page while the voice is silent."""
    out = f'1:{first}-0.55'
    p.label(f'CHAPTER {n}', 960, 470, 0.25, out, size=28, space='screen', color='accent', spacing=0.5)
    p.label(TITLES[n], 960, 548, 0.45, out, size=min(58, round(1500 / (len(TITLES[n]) * 0.98))), space='screen')


# ---- small diagram helpers ------------------------------------------------------------------
def atom(p, x, y, sym, at, out=None, r=26, accent=False):
    p.circle(x, y, r, at, out, width=2.2, fill='accent' if accent else 'paper', fillOpacity=0.55 if accent else 1)
    p.label(sym, x, y, T(at, 0.15), out, size=round(r * 0.62), spacing=0.02, upper=False)


def co2(p, x, y, at, out=None, r=24):
    atom(p, x, y, 'C', at, out, r, accent=True)
    for sx in (-1, 1):
        ox = x + sx * r * 2.6
        p.line([(x + sx * r, y), (ox - sx * r * 0.9, y)], T(at, 0.15), out, width=2.0)
        atom(p, ox, y, 'O', T(at, 0.2), out, r * 0.9)


def h2o(p, x, y, at, out=None, r=24):
    atom(p, x, y, 'O', at, out, r)
    for sx in (-1, 1):
        hx, hy = x + sx * r * 1.9, y + r * 1.5
        p.line([(x + sx * r * 0.6, y + r * 0.8), (hx - sx * r * 0.45, hy - r * 0.55)], T(at, 0.15), out, width=2.0)
        atom(p, hx, hy, 'H', T(at, 0.2), out, r * 0.7)


def waves(p, x0, x1, y, at, out=None, n=3, gap=26, amp=9, wl=90):
    ids = []
    for i in range(n):
        pts = [(x, y + i * gap + amp * math.sin((x - x0) / wl * 2 * math.pi + i)) for x in range(int(x0), int(x1) + 1, 15)]
        ids.append(p.line(pts, T(at, 0.12 * i), out, width=1.8, duration=1.0, color='muted' if i else None))
    return ids


def layers(p, x0, x1, y, at, out=None, n=4, gap=34, amp=6, step=0.15):
    ids = []
    for i in range(n):
        pts = [(x, y + i * gap + amp * math.sin((x - x0) / 140 + i * 1.7)) for x in range(int(x0), int(x1) + 1, 20)]
        ids.append(p.line(pts, T(at, step * i), out, width=1.6, duration=0.9, color='muted'))
    return ids


def mark(p):
    """Remember where a scene starts, so close() can end everything added after this."""
    return (len(p.items), len(p.drawings), len(p.labels), len(p.lights), len(p.streams), len(p.mags))


def close(p, m, at):
    """Everything added since mark() leaves at `at` (unless it already has its own exit)."""
    p.check_ref(at)
    for it in p.items[m[0]:]:
        it.setdefault('out', at)
    for d in p.drawings[m[1]:]:
        d.setdefault('out', at)
    for l in p.labels[m[2]:]:
        l.setdefault('out', at)
    for L in p.lights[m[3]:]:
        if 'duration' not in L:
            L.setdefault('to', at)
    for S in p.streams[m[4]:]:
        S.setdefault('to', at)
    for g in p.mags[m[5]:]:
        g.setdefault('close', at)


def question(p, x, y, at, out=None, size=96):
    p.label('?', x, y, at, out, size=size, color='accent', spacing=0.02)


def scatter(cx, cy, w, h, n, seed=1):
    pts = []
    for i in range(n):
        a = math.sin(i * 12.9898 + seed * 78.233) * 43758.5453
        b = math.sin(i * 39.3468 + seed * 11.135) * 24634.6345
        pts.append((cx + (a - math.floor(a) - 0.5) * w, cy + (b - math.floor(b) - 0.5) * h))
    return pts


def rise(x, y, dx, dy, bend=0.25):
    """A gently curved path from (x, y) to (x + dx, y + dy)."""
    return [(x, y), (x + dx * 0.35 + dy * bend * 0.3, y + dy * 0.35), (x + dx * 0.7 - dy * bend * 0.2, y + dy * 0.7), (x + dx, y + dy)]


# ======================================================================================
def part0(p):
    p.cam('start', x=-150, y=-20, zoom=0.86)
    lungs = p.pic('lungs', 260, -10, h=500, at='1:Every breath', id='lungs')
    bust = p.pic('roman_bust', -560, -30, h=430, at='1:Every breath+0.6')
    a, b = p.pt(bust, BUST_LIPS), p.pt(lungs, LUNGS_TOP)
    p.stream([a, (a[0] + 260, a[1] - 160), (b[0] - 240, b[1] - 170), b], '1:molecule', 'end-1.1', count=10, period=3.0, size=20, spread=8, color='accent')
    p.label('ABOUT 1 MOLECULE IN EVERY BREATH', -150, 380, '1:on average', '1:The atoms in-0.2', size=34)
    p.label('JULIUS CAESAR', -560, 230, '1:Julius', '1:The atoms in-0.2', size=30, color='accent')
    p.cam('1:molecule of air@end', x=-150, y=-20, zoom=0.95)
    p.hold_cam('1:last breath@end')
    # The atoms in your hand may once have been part of a tree, a fish, or another person
    hx = 1750
    hand = p.pic('open_hand', hx, 120, h=300, at='1:The atoms in')
    palm = p.pt(hand, (0.55, 0.45))
    p.glows([(palm[0] - 30, palm[1] - 20), (palm[0] + 25, palm[1] - 35), (palm[0], palm[1] + 10)], '1:right now', size=34, stagger=0.15)
    others = [('tree', hx - 520, -240, 300, '1:a tree'), ('fish', hx + 560, -260, None, '1:a fish'), ('person', hx + 560, 150, 330, '1:another person')]
    for name, x, y, h, at in others:
        if name == 'fish':
            p.pic(name, x, y, w=300, at=at, out='1:Nothing in this-0.1')
        else:
            p.pic(name, x, y, h=h, at=at, out='1:Nothing in this-0.1')
        p.line([(palm[0], palm[1] - 60), (x + (hx - x) * 0.25, y + (palm[1] - y) * 0.25)], T(at, 0.2), '1:Nothing in this-0.1', width=1.6, dashed=True, color='muted')
    p.cam('1:The atoms in', x=hx, y=-20, zoom=0.85)
    p.label('NOTHING DISAPPEARS', hx, 430, '1:Nothing in this', '1:And when you-0.2', size=44)
    p.cam('1:really disappears', x=hx, y=60, zoom=0.92)
    # When you die, almost none of your atoms will be destroyed
    mx = 3300
    me = p.pic('person', mx, 0, h=700, at='1:And when you', id='me')
    for k, (u, v) in enumerate([CHEST, FACE, ARM, (0.55, 0.62)]):
        s = p.pt(me, (u, v))
        p.stream(rise(s[0], s[1], 140 - 90 * k, -520 - 60 * k), T('1:almost none', 0.3 * k), '2:In this video', count=6, period=4.2, size=18, spread=18)
    p.label('ALMOST NONE ARE DESTROYED', mx, 440, '1:almost none', '2:So where-0.2', size=36)
    p.cam('1:And when you', x=mx, y=0, zoom=0.95)
    p.label('WHERE DO THEY GO?', mx, -430, '2:So where', '2:follow them@end', size=44, color='accent')
    # We'll follow them: a path out to the right, past everything the video will visit
    path = [(mx + 260, 40), (4300, 180), (5200, -30), (6100, 120), (7000, -60), (7900, -320)]
    trip = p.line(path, '2:follow them', width=2.0, curve=True, duration=8.2, color='muted')
    p.travel(trip, '2:follow them', dur=8.2, size=56)
    layers(p, 3900, 4700, 300, '2:the soil', n=3, gap=26)
    p.label('SOIL', 4300, 420, '2:the soil', size=26)
    p.pic('cloud', 4250, -300, h=200, at='2:the air')
    waves(p, 4700, 5200, 260, '2:the sea', n=3)
    p.pic('tree', 5350, -150, h=360, at='2:Into other')
    p.pic('deer', 5800, 160, h=240, at='2:living things')
    p.pic('fish', 6150, -230, w=220, at='2:living things+0.3')
    p.pic('mountain', 6900, 160, w=560, at='2:Deep into')
    layers(p, 6620, 7180, 330, '2:the Earth', n=3, gap=30)
    p.pic('nebula', 8000, -330, h=440, at='2:back to')
    p.glows([(7900, -320), (7650, -540), (8280, -140), (8200, -580), (7620, -180), (8380, -400)], '2:the stars', size=70, stagger=0.12)
    p.cam('2:follow them@end', x=4200, y=40, zoom=0.9)
    p.cam('2:the sea@end', x=4600, y=40, zoom=0.9)
    p.cam('2:living things@end', x=5700, y=0, zoom=0.9)
    p.cam('2:the Earth@end', x=6800, y=40, zoom=0.9)
    p.cam('2:And finally', x=7500, y=-200, zoom=0.78)
    p.cam('2:the stars@end', x=7950, y=-330, zoom=0.92)
    p.end_all()


def part1(p):
    chapter(p, 1, "Let's")
    p.cam('start', x=0, y=0, zoom=0.95)
    me = p.pic('person', 0, 0, h=720, at="1:Let's", id='me')
    p.hold_cam("1:Let's-0.3")
    p.cam('1:right now@end', x=0, y=0, zoom=1.0)
    p.pic('statue', -480, 30, h=600, at='1:like a statue', out="1:But it's-0.1")
    p.label('A STATUE?', -480, 420, '1:like a statue+0.3', "1:But it's-0.1", size=34)
    p.cam('1:might think', x=-240, y=0, zoom=0.95)
    # The river: two banks drawn in long curves, atoms flowing down between them
    rx = 620
    left = [(rx, -470), (rx + 170, -230), (rx + 60, 20), (rx + 230, 260), (rx + 180, 470)]
    right = [(x + 230, y) for x, y in left]
    mid = [(x + 115, y) for x, y in left]
    p.line(left, "1:But it's", width=2.2, curve=True, duration=1.4)
    p.line(right, "1:But it's+0.2", width=2.2, curve=True, duration=1.4)
    p.stream(mid, '1:The water', count=16, period=4.5, size=14, spread=40)
    p.label('ALWAYS CHANGING', rx + 640, -340, '1:never', '2:The red-0.3', size=34)
    p.label('YET STILL A RIVER', rx + 640, -260, '1:yet the', '2:The red-0.3', size=26, weight=500, color='accent')
    p.cam("1:But it's", x=rx + 200, y=0, zoom=0.95)
    p.cam('1:The water', x=rx + 380, y=-40, zoom=0.95)
    # Red blood cells: up to 120 days, then replaced
    bx = 2000
    old = p.pic('blood_cell', bx, -120, h=230, at='2:The red', out='2:broken down+0.2')
    p.label('UP TO {n} DAYS', bx, 120, '2:120', '2:Even your-0.2', size=40, count={'to': 120, 'duration': 1.2})
    p.pic('blood_cell', bx, -120, h=230, at='2:new ones', out='2:Even your-0.2')
    loop = p.ellipse(bx, -120, 190, 150, '2:take their', width=1.6, color='muted', out='2:Even your-0.2', dashed=True)
    p.travel(loop, '2:take their', dur=1.6, size=44)
    p.cam('2:The red', x=bx, y=-20, zoom=1.1)
    # Bones are rebuilt: 5–10 % every year
    gx = 2900
    bone = p.pic('bone', gx, -40, w=560, at='2:Even your')
    p.travel_on(bone, PICS.outline('bone', 0.0, 1.0, 60), '2:taken apart', dur=1.8, size=42)
    p.label('5–10% EVERY YEAR', gx, 200, '2:five to ten', '3:And every-0.2', size=44, color='accent')
    p.cam('2:Even your', x=gx, y=20, zoom=1.0)
    # Breathing out carbon from food
    lx = 3800
    lungs = p.pic('lungs', lx, -40, h=460, at='3:breathe out')
    p.pic('bread', lx - 520, 250, h=170, at='3:your food')
    p.arrow((lx - 400, 200), (lx - 180, 90), '3:burns', width=2.0, color='muted')
    top = p.pt(lungs, LUNGS_TOP)
    p.stream(rise(top[0], top[1], 420, -200, 0.4), '3:let go', '4:So the atoms', count=10, period=3.0, size=14, spread=12)
    co2(p, lx + 560, -330, '3:carbon dioxide', '4:So the atoms', r=26)
    p.label('CARBON DIOXIDE', lx + 560, -230, '3:carbon dioxide+0.3', '4:So the atoms', size=30)
    p.cam('3:And every', x=lx, y=-20, zoom=0.95)
    p.cam('3:carbon dioxide', x=lx + 180, y=-80, zoom=0.92)
    # Passing through; what stays is the pattern
    px = 5300
    me2 = p.pic('person', px, 0, h=720, at='4:So the atoms', id='me2')
    c2 = p.pt(me2, CHEST)
    p.stream([(px - 620, 260), (px - 260, 120), c2, (px + 260, -160), (px + 640, -300)], '4:passing through', '4:pattern', count=12, period=3.4, size=13, spread=14)
    p.label('THE PATTERN', px, 450, '4:pattern', '5:So what', size=40, color='accent')
    p.travel_on(me2, PICS.outline('person', 0.0, 1.0, 80), '4:The shape', dur=2.0, size=40)
    p.glow(me2, FACE, '4:think', '5:stops', size=90)
    p.glow(me2, CHEST, '4:love', '5:stops', size=110)
    p.cam('4:So the atoms', x=px, y=0, zoom=0.95)
    p.cam('4:The shape', x=px, y=0, zoom=1.0)
    question(p, px + 420, -200, '5:So what', size=110)
    p.items[-1]['out'] = '5:stops+0.4'
    p.cam('5:stops@end', x=px, y=0, zoom=0.86)
    p.end_all()


def part2(p):
    chapter(p, 2, 'First')
    p.cam('start', x=0, y=0, zoom=0.95)
    m0 = mark(p)
    p.label('THE RULE', 0, -360, '1:a rule', '1:Nothing is-0.2', size=44, color='accent')
    # A balance: the same atoms on both sides, only rearranged
    p.line([(0, 300), (0, -80)], '1:When matter', width=2.4)
    p.line([(-160, 300), (160, 300)], '1:When matter', width=2.4)
    p.line([(-430, -80), (430, -80)], '1:When matter+0.2', width=2.4)
    for sx in (-1, 1):
        x = sx * 430
        p.line([(x, -80), (x - 120, 70)], '1:When matter+0.35', width=1.6, color='muted')
        p.line([(x, -80), (x + 120, 70)], '1:When matter+0.35', width=1.6, color='muted')
        p.line([(x - 150, 70), (x - 100, 110), (x + 100, 110), (x + 150, 70)], '1:When matter+0.45', width=2.2)
    cluster = [(-470, 30), (-430, 0), (-390, 30), (-450, 62), (-410, 62), (-430, 32)]
    for i, (x, y) in enumerate(cluster):
        p.circle(x, y, 17, T('1:form', 0.08 * i), width=2.0, fill='accent', fillOpacity=0.5)
    for i in range(6):
        x = 355 + 30 * i
        p.circle(x, 75 - (i % 2) * 30, 17, T('1:into another', 0.08 * i), width=2.0, fill='accent', fillOpacity=0.5)
    p.label('BEFORE', -430, 190, '1:form', size=26, weight=500)
    p.label('AFTER', 430, 190, '1:into another', size=26, weight=500)
    p.label('CONSERVATION OF MATTER', 0, 420, '1:law of', size=36)
    p.label('NOTHING IS LOST', 0, -360, '1:Nothing is+0.4', size=56)
    close(p, m0, '2:After death')
    p.cam('1:When matter', x=0, y=20, zoom=1.0)
    p.cam('1:Scientists', x=0, y=40, zoom=0.95)
    # Bacteria and fungi break down what is left
    gx, gy = 1900, 260
    m1 = mark(p)
    p.line([(gx - 650, gy), (gx + 1250, gy)], '2:After death', width=2.0)
    leaf = p.pic('leaf', gx - 150, gy - 165, h=300, at='2:After death')
    p.mag(leaf, (0.5, 0.55), 22, gx - 150, -330, 170, '2:bacteria', '2:Every ecosystem',
          [{'picture': 'bacteria', 'scale': 1.7}])
    p.pic('mushroom', gx + 300, gy - 120, h=250, at='2:fungi')
    p.stream(rise(gx - 150, gy - 20, -140, 200, 0.2), '2:They break', '3:Your water', count=8, period=3.6, size=12, spread=14)
    p.stream(rise(gx - 150, gy - 40, 230, -380, 0.3), '2:recycle', '3:Your carbon', count=8, period=3.2, size=13, spread=14)
    tree = p.pic('tree', gx + 900, gy - 300, h=600, at='2:Every ecosystem')
    p.pic('mushroom', gx + 600, gy - 70, h=150, at='2:depends')
    loop = p.line([(gx + 900, gy - 520), (gx + 450, gy - 520), (gx - 150, gy - 120), (gx + 400, gy + 40), (gx + 860, gy + 10)], '2:Without them', width=1.8, curve=True, arrow=True, duration=1.4, color='muted')
    p.travel(loop, '2:materials', dur=1.8, size=44)
    p.cam('2:After death', x=gx, y=0, zoom=0.95)
    p.cam('2:Every ecosystem', x=gx + 350, y=-20, zoom=0.85)
    # Carbon to the air and soil; nitrogen as ammonium; water to sky and sea
    co2(p, gx + 50, -330, '3:carbon dioxide', r=24)
    p.pic('cloud', gx + 250, -650, h=220, at='3:rises into')
    p.stream(rise(gx - 150, gy - 30, 380, -820, 0.25), '3:rises into', '4:Nothing is', count=12, period=3.6, size=14, spread=16)
    layers(p, gx - 600, gx + 1200, gy + 70, '3:stays in', n=3, gap=30)
    p.stream(rise(gx - 100, gy, -300, 140, 0.1), '3:stays in', '4:Nothing is', count=7, period=4.5, size=12, spread=8)
    atom(p, gx + 1500, gy + 110, 'N', '3:nitrogen', r=30, accent=True)
    p.label('AMMONIUM', gx + 1500, gy + 210, '3:ammonium', '4:Nothing is', size=28)
    p.stream([(gx - 150, gy + 80), (gx + 400, gy + 130), (gx + 900, gy + 90)], '3:passed along', '4:Nothing is', count=8, period=3.6, size=12, spread=6, color='accent')
    waves(p, gx + 1300, gx + 1900, gy - 60, '3:the sea', n=3)
    p.stream(rise(gx + 1550, gy - 80, -900, -560, 0.3), '3:Your water', '4:Nothing is', count=10, period=3.8, size=12, spread=14)
    p.cam('3:Your carbon', x=gx + 150, y=-260, zoom=0.82)
    p.cam('3:Some of it', x=gx + 200, y=150, zoom=0.9)
    p.cam('3:The nitrogen', x=gx + 800, y=150, zoom=0.88)
    p.cam('3:Your water', x=gx + 700, y=-150, zoom=0.72)
    close(p, m1, '4:Nothing is')
    # Handed on
    hx = gx + 2900
    p.label('NOTHING IS DESTROYED', hx, -330, '4:Nothing is', size=48)
    hand = p.pic('open_hand', hx, 140, h=320, at='4:handed')
    palm = p.pt(hand, (0.55, 0.45))
    p.stream(rise(palm[0], palm[1], 180, -820, 0.3), '4:handed', count=9, period=3.4, size=14, spread=10, color='accent')
    p.cam('4:Nothing is', x=hx, y=0, zoom=0.95)
    question(p, hx + 420, -150, '4:So where', size=110)
    p.cam('4:next@end', x=hx, y=-80, zoom=0.86)
    p.end_all()


def part3(p):
    chapter(p, 3, "Let's")
    p.cam('start', x=0, y=0, zoom=1.0)
    m0 = mark(p)
    atom(p, 0, 200, 'C', "1:Let's follow", r=40, accent=True)
    p.glows([(0, 200)], '1:one carbon', '1:It drifts', size=120)
    p.cam("1:Let's follow", x=60, y=150, zoom=1.3)
    up = p.line([(0, 160), (120, 40), (260, -90), (420, -170)], '1:It drifts', width=1.6, curve=True, dashed=True, color='muted')
    p.travel(up, '1:It drifts', dur=1.6, size=40)
    co2(p, 560, -190, '1:molecule', r=26)
    p.label('CARBON DIOXIDE', 560, -95, '1:carbon dioxide', '2:Plants-0.2', size=28)
    p.hold_cam('1:It drifts-0.2')
    p.cam('1:carbon dioxide@end', x=300, y=-30, zoom=1.0)
    close(p, m0, '2:Plants')
    # A leaf, sunlight, sugar
    lx = 1200
    m1 = mark(p)
    p.pic('leaf', lx, -200, h=320, at='2:reaches a leaf')
    p.glows([(lx + 520, -560)], '2:sunlight', size=180)
    for k in range(3):
        p.line([(lx + 450 - 30 * k, -490 + 40 * k), (lx + 170 - 30 * k, -300 + 40 * k)], T('2:sunlight', 0.1 * k), width=1.6, color='accent', dashed=True)
    p.label('CO₂ + SUNLIGHT → SUGAR', lx, 90, '2:into sugar', '3:An animal', size=34, color='accent', upper=False)
    p.cam('2:One day', x=lx, y=-150, zoom=1.0)
    p.cam('2:Plants', x=lx + 150, y=-200, zoom=0.88)
    close(p, m1, '2:Now your')
    m2 = mark(p)
    tree = p.pic('tree', lx + 1050, -80, h=560, at='2:part of a tree')
    wheat = p.pic('wheat', lx + 1600, 0, h=440, at='2:field of wheat')
    p.cam('2:Now your', x=lx + 1300, y=-40, zoom=0.9)
    deer = p.pic('deer', lx + 2250, -170, h=250, at='2:Almost every')
    p.pic('mushroom', lx + 2250, 240, h=170, at='2:living thing')
    p.line([(lx + 1700, -120), (lx + 2080, -170)], '2:Almost every+0.2', width=1.6, color='muted', dashed=True)
    p.line([(lx + 1700, 120), (lx + 2120, 220)], '2:living thing+0.2', width=1.6, color='muted', dashed=True)
    p.cam('2:Almost every', x=lx + 1850, y=0, zoom=0.88)
    # An animal eats the plant; a person eats the bread; the atom becomes part of someone else
    p.cam('3:An animal', x=lx + 2250, y=-120, zoom=1.15)
    close(p, m2, '3:A person')
    px = lx + 3300
    p.pic('bread', px - 520, 230, h=160, at='3:the bread')
    me = p.pic('person', px, 0, h=700, at='3:A person', id='me')
    chest = p.pt(me, CHEST)
    p.stream([(px - 520, 180), (px - 330, 40), chest], '3:becomes part', '4:Other', count=6, period=2.6, size=18, spread=6, color='accent')
    p.glow(me, CHEST, '3:their blood', '4:Other', size=90)
    p.glow(me, ARM, '3:muscles', '4:Other', size=80)
    p.glow(me, FACE, '3:brain', '4:Other', size=90)
    p.cam('3:A person', x=px - 220, y=0, zoom=0.95)
    p.cam('3:Part of their', x=px, y=-40, zoom=1.05)
    # The ocean: carbon sinks in, and swaps with the air
    ox = px + 1500
    waves(p, ox - 600, ox + 600, 0, '4:Other', n=3)
    p.stream([(ox - 200, -260), (ox - 160, -60), (ox - 120, 180), (ox - 60, 400)], '4:sink', count=9, period=3.6, size=13, spread=14)
    up = p.line([(ox + 220, 260), (ox + 300, 60), (ox + 260, -260)], '4:back and forth', width=1.8, curve=True, arrow=True)
    down = p.line([(ox + 380, -260), (ox + 460, -60), (ox + 420, 240)], '4:back and forth+0.4', width=1.8, curve=True, arrow=True)
    p.stream([(ox + 220, 260), (ox + 300, 60), (ox + 260, -260)], '4:back and forth', count=6, period=2.6, size=12, spread=6)
    p.stream([(ox + 380, -260), (ox + 460, -60), (ox + 420, 240)], '4:back and forth+0.4', count=6, period=2.6, size=12, spread=6)
    p.label('THE OCEAN', ox, 330, '4:The ocean is', '5:The air works-0.2', size=36)
    p.label('A HUGE STORE OF CARBON', ox, 400, '4:biggest stores', '5:The air works-0.2', size=30, color='accent')
    p.cam('4:Other', x=ox, y=60, zoom=0.92)
    # The air mixes around the whole planet: Caesar's breath, and yours for people not yet born
    ex = ox + 1700
    p.pic('earth', ex, 0, h=480, at='5:The air works')
    wind = [p.ellipse(ex, 0, 360, 130, T('5:works the same', 0.2 * k), rot=-18 + 30 * k, width=1.4, color='muted', dashed=True) for k in range(2)]
    lungs = p.pic('lungs', ex + 700, -60, h=320, at='5:Every breath')
    lt = p.pt(lungs, LUNGS_TOP)
    ring = [(ex + 360 * math.cos(a), 130 * math.sin(a)) for a in [i * 2 * math.pi / 24 for i in range(25)]]
    p.stream([lt, (ex + 420, -120)] + ring[3:20], '5:mixes into', count=16, period=5.0, size=13, spread=10)
    bust = p.pic('roman_bust', ex - 720, -40, h=340, at="5:Caesar's")
    bl = p.pt(bust, BUST_LIPS)
    p.stream([bl, (ex - 300, -330), (ex + 300, -330), lt], "5:Caesar's", '5:And one day', count=8, period=3.0, size=16, spread=8, color='accent')
    p.label('THE FUTURE', ex + 1300, 260, "5:aren't born", size=34)
    p.stream([(lt[0] + 60, lt[1] + 60), (ex + 1000, 40), (ex + 1300, 160)], "5:aren't born", count=8, period=3.0, size=14, spread=8, color='accent')
    p.cam('5:The air works', x=ex, y=0, zoom=0.88)
    p.cam('5:Every breath', x=ex + 300, y=0, zoom=0.82)
    p.cam("5:That's why", x=ex, y=-40, zoom=0.72)
    p.cam('5:And one day', x=ex + 600, y=40, zoom=0.78)
    # One atom among many turns gold
    fx = ex + 2700
    field = scatter(fx, 0, 900, 560, 26, seed=3)
    for i, (x, y) in enumerate(field):
        p.circle(x, y, 15, T('6:But a few', 0.04 * i), width=1.8, fill='paper')
    gold = field[11]
    p.circle(gold[0], gold[1], 15, '6:something different', width=1.8, fill='accent', fillOpacity=0.9)
    p.glows([gold], '6:They change', size=110)
    question(p, gold[0] + 130, gold[1] - 120, '6:So which', size=90)
    p.cam('6:But a few', x=fx, y=0, zoom=1.0)
    p.cam('6:So which', x=gold[0], y=gold[1], zoom=1.25)
    p.end_all()


def part4(p):
    chapter(p, 4, 'Most')
    p.cam('start', x=0, y=0, zoom=1.0)
    field = scatter(0, 0, 900, 500, 24, seed=7)
    for i, (x, y) in enumerate(field):
        p.circle(x, y, 15, T('1:Most of the', 0.04 * i), width=1.8, fill='paper', out='2:It\'s made')
    p.label('CARBON-12', 0, 340, '1:body is@end', "2:It's made", size=44, upper=False)
    p.label('STABLE', 0, -340, '1:stable', "2:It's made", size=40, color='accent')
    # Carbon-14
    cx = 760
    p.circle(cx, 0, 54, '2:part of it is@end', width=2.4, fill='accent', fillOpacity=0.75)
    p.label('C', cx, 0, '2:part of it is@end+0.15', size=34, upper=False, spacing=0.02)
    p.glows([(cx, 0)], '2:radioactive', size=150)
    p.label('CARBON-14', cx, 130, '2:part of it is@end+0.2', size=40, color='accent', upper=False)
    p.label('RADIOACTIVE', cx, 190, '2:radioactive', size=26, weight=500)
    p.cam('2:But a very', x=420, y=0, zoom=1.0)
    # Made in the sky: rays from space strike nitrogen
    sx, sy = 1500, -760
    m_sky = mark(p)
    p.glows([(sx - 380, sy - 330), (sx + 120, sy - 380), (sx + 420, sy - 260)], '2:high in the sky', size=36, stagger=0.15)
    for k in range(3):
        p.line([(sx - 260 + 120 * k, sy - 420), (sx - 20 + 20 * k, sy - 60)], T('2:rays from space', 0.12 * k), width=1.6, color='accent', dashed=True)
    atom(p, sx, sy, 'N', '2:high in the sky', r=40)
    p.arrow((sx + 60, sy), (sx + 230, sy), '2:nitrogen in the air', width=2.0)
    p.circle(sx + 300, sy, 40, '2:in the air+0.2', width=2.2, fill='accent', fillOpacity=0.75)
    p.label('C', sx + 300, sy, '2:in the air+0.35', size=30, upper=False, spacing=0.02)
    p.label('MADE IN THE SKY', sx + 150, sy + 150, '2:made in the sky', size=40)
    p.cam("2:It's made", x=sx + 120, y=sy - 60, zoom=1.0)
    # Taken in with food while alive; the level stays the same
    wx = 2500
    close(p, m_sky, "2:While you're")
    m_level = mark(p)
    p.pic('wheat', wx, 0, h=420, at='2:your food')
    me = p.pic('person', wx + 650, 0, h=700, at="2:While you're", id='me', out='3:that stops+0.2')
    p.arrow((wx + 180, 0), (wx + 450, 0), '2:taking it in', width=2.0)
    p.stream([(wx + 120, -40), (wx + 450, -20), p.pt(me, CHEST)], '2:taking it in', '3:that stops', count=6, period=2.6, size=14, spread=6, color='accent')
    lvl = p.line([(wx + 1000, -120), (wx + 1400, -120)], '2:stays the same', width=2.4, color='accent', duration=1.2)
    p.label('CARBON-14 LEVEL', wx + 1200, -190, '2:stays the same', '3:After 5,730-0.2', size=26, upper=False)
    p.cam("2:While you're", x=wx + 500, y=0, zoom=0.9)
    p.cam('2:stays the same', x=wx + 700, y=-20, zoom=0.9)
    # Decay: half every 5,730 years
    atom(p, wx + 650, -420, 'C', '3:And the@end', r=34, accent=True)
    p.drawings[-1]['out'] = '3:nitrogen'
    p.labels[-1]['out'] = '3:nitrogen'
    atom(p, wx + 650, -420, 'N', '3:nitrogen', r=34)
    gx, gy = wx + 1000, 260
    close(p, m_level, '3:After 5,730')
    m_graph = mark(p)
    p.arrow((gx, gy), (gx + 1150, gy), '3:After 5,730', width=2.0)
    p.arrow((gx, gy), (gx, gy - 520), '3:After 5,730', width=2.0)
    half = 420

    def decay(a, b):
        return [(gx + t * half, gy - 480 * 0.5 ** t) for t in [a + (b - a) * i / 24 for i in range(25)]]
    c1 = p.line(decay(0, 1), '3:After 5,730+0.3', width=2.6, color='accent', duration=1.4)
    p.line([(gx + half, gy), (gx + half, gy - 240)], '3:half of it', width=1.4, dashed=True, color='muted')
    p.label('5,730 YEARS', gx + half, gy + 50, '3:half of it', size=22, upper=False)
    p.label('½', gx + half + 50, gy - 270, '3:half of it', size=34, upper=False, spacing=0.02)
    p.line(decay(1, 2), '3:After another', width=2.6, color='accent', duration=1.4)
    p.line([(gx + 2 * half, gy), (gx + 2 * half, gy - 120)], "3:half of what's", width=1.4, dashed=True, color='muted')
    p.label('11,460 YEARS', gx + 2 * half, gy + 50, "3:half of what's", size=22, upper=False)
    p.label('¼', gx + 2 * half + 50, gy - 150, "3:half of what's", size=34, upper=False, spacing=0.02)
    p.cam('3:When you die', x=wx + 650, y=-150, zoom=0.95)
    p.cam('3:After 5,730', x=gx + 500, y=0, zoom=1.0)
    # A clock that starts when a life ends: radiocarbon dating
    hx = gx + 1800
    close(p, m_graph, '4:like a clock')
    p.pic('hourglass', hx, -30, h=480, at='4:like a clock')
    p.label('HOW LONG AGO?', hx, 320, '4:how long ago', size=40, color='accent')
    rx = hx + 900
    p.label('RADIOCARBON DATING', rx, -260, '4:radiocarbon dating', size=40)
    p.label('UP TO {n} YEARS', rx, -180, '4:50,000', size=34, color='accent', count={'to': 50000, 'duration': 1.4})
    p.pic('bone', rx - 380, 120, w=300, at='4:ancient bones')
    p.pic('log', rx, 130, h=200, at='4:wood')
    p.pic('cloth', rx + 380, 130, w=300, at='4:cloth')
    p.cam("4:It's like", x=hx, y=0, zoom=1.0)
    p.cam('4:They call', x=rx - 200, y=-40, zoom=0.9)
    p.cam("4:It's how", x=rx, y=0, zoom=0.92)
    # A few change; almost everything moves on, some very slowly
    fx = rx + 1600
    field = scatter(fx, 0, 760, 460, 20, seed=11)
    for i, (x, y) in enumerate(field):
        p.circle(x, y, 14, T('5:A few', 0.03 * i), width=1.8, fill='accent' if i % 6 == 0 else 'paper', fillOpacity=0.85 if i % 6 == 0 else 1, out='5:Almost everything+0.6')
    p.glows([q for i, q in enumerate(field) if i % 6 == 0], '5:slowly change', '5:Almost everything+0.6', size=70, stagger=0.1)
    p.stream([(fx - 200, 0), (fx + 400, -60), (fx + 1000, 20)], '5:Almost everything', count=14, period=2.4, size=14, spread=60)
    p.stream([(fx + 200, 200), (fx + 600, 220), (fx + 1000, 210)], '5:very, very', count=5, period=14, size=14, spread=10, color='accent')
    p.label('JUST MOVES ON', fx + 400, -330, '5:moves on', '5:So where', size=34)
    p.label('VERY, VERY SLOWLY', fx + 600, 320, '5:very, very', size=30)
    bone = p.pic('bone', fx + 1500, -40, w=440, at='5:So where')
    question(p, fx + 1500, -300, '5:So where', size=110)
    p.cam('5:A few', x=fx, y=0, zoom=1.0)
    p.cam('5:Almost everything', x=fx + 400, y=0, zoom=0.92)
    p.cam('5:So where', x=fx + 1300, y=-60, zoom=0.95)
    p.end_all()


def part5(p):
    chapter(p, 5, 'Your bones')
    p.cam('start', x=0, y=0, zoom=0.95)
    p.pic('bone', 0, -40, w=560, at='1:Your bones')
    p.tile('Ca', 'CALCIUM', -150, 210, '1:calcium', s=110)
    p.tile('P', 'PHOSPHORUS', 150, 210, '1:calcium and phosphorus', s=110)
    p.pic('dna', 820, -20, h=440, at='1:DNA')
    p.tile('P', None, 1050, -170, '1:DNA+0.3', s=70)
    p.stream([(-200, 380), (400, 400), (1000, 380)], '1:slowest', count=4, period=12, size=16, spread=6, color='accent')
    p.label('ONE OF THE SLOWEST TRAVELERS', 400, -360, '1:slowest', '2:Rain-0.2', size=34)
    p.cam('1:Phosphorus is in', x=420, y=0, zoom=0.9)
    p.cam('1:slowest', x=420, y=0, zoom=0.88)
    # Rain and rivers to the sea; sea life; remains sink to the ocean floor
    cx = 1800
    p.pic('cloud', cx, -380, h=220, at='2:Rain')
    river = p.line([(cx + 60, -200), (cx + 220, -40), (cx + 520, 40), (cx + 860, 100)], '2:rivers', width=2.2, curve=True, duration=1.2)
    p.stream([(cx + 60, -200), (cx + 220, -40), (cx + 520, 40), (cx + 860, 100)], '2:carry it', '3:Once', count=8, period=3.0, size=13, spread=6, color='accent')
    sea = cx + 1350
    waves(p, sea - 450, sea + 550, 110, '2:the sea', n=3)
    fish = p.pic('fish', sea + 50, 360, w=260, at='2:sea life')
    p.stream([(cx + 860, 110), (sea - 150, 250), (sea - 40, 360)], '2:taken up', '3:Once', count=6, period=2.4, size=12, spread=6, color='accent')
    sink = p.line([(sea + 50, 440), (sea + 120, 600), (sea + 60, 770)], '2:remains sink', width=1.6, curve=True, dashed=True, color='muted')
    p.travel(sink, '2:remains sink', dur=1.6, size=40)
    floor = layers(p, sea - 600, sea + 700, 820, '2:ocean floor', n=2, gap=30)
    p.cam('2:Rain', x=cx + 350, y=-60, zoom=0.88)
    p.cam('2:There', x=sea, y=200, zoom=0.95)
    p.cam('2:When those', x=sea, y=500, zoom=0.92)
    # 20,000 to 100,000 years in the ocean
    p.label('ONE PHOSPHORUS ATOM STAYS IN THE OCEAN', sea + 560, 470, '3:a phosphorus atom', '4:Calcium-0.2', size=26, weight=500)
    p.label('20,000 – 100,000 YEARS', sea + 560, 560, '3:twenty thousand', '4:Calcium-0.2', size=52, color='accent', spacing=0.1)
    p.cam('3:Once', x=sea + 300, y=560, zoom=0.95)
    # Calcium into shells; shells into limestone, the largest store of carbon
    lx = sea + 1300
    m_shell = mark(p)
    p.tile('Ca', None, lx - 380, 600, '4:Calcium has', s=90)
    road = p.line([(lx - 330, 600), (lx - 230, 540), (lx - 130, 600)], '4:long road', width=1.6, curve=True, dashed=True, color='muted')
    p.travel(road, '4:long road', dur=1.4, size=46)
    p.pic('shell', lx, 600, h=240, at='4:built into shells')
    lim = layers(p, lx - 650, lx + 650, 820, '4:Over time', n=5, gap=32, step=0.25)
    p.label('LIMESTONE', lx, 1010, '4:become limestone', size=36)
    p.label('THE LARGEST STORE OF CARBON ON EARTH', lx, 420, '4:Limestone is the', '5:And over-0.2', size=30, color='accent')
    p.cam('4:Calcium', x=lx - 150, y=650, zoom=0.98)
    p.cam('4:Over time', x=lx, y=780, zoom=0.92)
    # The ground rises; old sea floor becomes a mountain
    for k in range(3):
        x = lx - 400 + 400 * k
        p.arrow((x, 900), (x, 640), T('5:the ground itself', 0.15 * k), width=2.4)
    close(p, m_shell, '5:lifted up')
    m_mtn = mark(p)
    mtn = p.pic('mountain', lx, 330, w=760, at='5:lifted up')
    into = p.line([(lx - 520, 960), (lx - 300, 700), (lx - 60, 420)], '5:stone of a mountain', width=1.6, curve=True, dashed=True, color='muted')
    p.travel(into, '5:stone of a mountain', dur=1.6, size=46)
    p.cam('5:And over', x=lx, y=620, zoom=0.72)
    p.cam('5:Atoms that', x=lx, y=420, zoom=0.92)
    # Coal: carbon locked away; sunlight caught 200–350 million years ago
    kx = lx + 1500
    close(p, m_mtn, '6:Some carbon')
    atom(p, kx - 400, 300, 'C', '6:Some carbon', r=32, accent=True)
    p.pic('leaf', kx, 610, h=260, at='6:living things')
    layers(p, kx - 450, kx + 450, 440, '6:buried deep', n=4, gap=-30, step=0.2)
    coal = p.pic('coal', kx + 650, 500, h=230, at='6:how coal formed')
    p.glows([(kx + 650, -100)], '6:sunlight', size=170)
    beam = p.line([(kx + 640, -40), (kx + 760, 200), (kx + 660, 400)], '6:plants caught', width=1.8, curve=True, color='accent', dashed=True)
    p.travel(beam, '6:plants caught', dur=1.6, size=50)
    p.label('200–350 MILLION YEARS AGO', kx + 650, 690, '6:between 200', size=34, color='accent')
    p.cam('6:Some carbon', x=kx - 100, y=420, zoom=0.95)
    p.cam("6:That's how", x=kx + 400, y=420, zoom=0.95)
    p.cam('6:The energy', x=kx + 600, y=300, zoom=0.82)
    # Does the Earth keep our atoms forever?
    ex = kx + 1900
    p.pic('earth', ex, 300, h=480, at='7:Earth')
    question(p, ex + 380, 80, '7:forever', size=110)
    p.cam('7:So does', x=ex, y=300, zoom=0.92)
    p.end_all()


def part6(p):
    chapter(p, 6, 'For a very')
    p.cam('start', x=0, y=0, zoom=0.92)
    p.pic('earth', 0, 0, h=520, at='1:For a very')
    loop = p.line([(300, -240), (390, 0), (300, 240), (0, 350), (-300, 240), (-390, 0), (-300, -240)], '1:recycles', width=1.8, curve=True, arrow=True, duration=1.4)
    p.travel(loop, '1:recycles', dur=1.8, size=44)
    p.cam('1:recycles', x=0, y=0, zoom=0.92)
    # One plate slides under another; volcanoes breathe carbon back out
    sx = 1500
    p.line([(sx - 500, -40), (sx + 200, -40), (sx + 420, 120), (sx + 560, 420)], '1:Sea floor carrying', width=2.6, curve=True, duration=1.4)
    p.line([(sx - 500, 30), (sx + 140, 30), (sx + 340, 180), (sx + 470, 450)], '1:Sea floor carrying+0.2', width=2.0, curve=True, duration=1.4, color='muted')
    p.line([(sx + 1100, -70), (sx + 330, -70), (sx + 230, -40)], '1:one great plate', width=2.6, duration=1.0)
    p.line([(sx + 1100, 0), (sx + 470, 0)], '1:one great plate+0.2', width=2.0, duration=1.0, color='muted')
    p.stream([(sx - 400, -10), (sx + 160, -10), (sx + 380, 150), (sx + 510, 430)], '1:dragged', count=10, period=3.4, size=13, spread=6, color='accent')
    p.label('ONE PLATE SLIDES BENEATH ANOTHER', sx + 300, 330, '1:slides beneath', size=26, weight=500)
    vx = sx + 750
    p.pic('volcano', vx, -280, h=320, at='1:volcanoes')
    p.stream([(sx + 520, 400), (vx - 40, 120), (vx, -280), (vx + 60, -620)], '1:breathe that', count=12, period=3.2, size=13, spread=14, color='accent')
    p.cam('1:Sea floor carrying', x=sx + 200, y=60, zoom=0.92)
    p.cam('1:And volcanoes', x=sx + 450, y=-120, zoom=0.88)
    # The Sun brightens; in a billion years water splits and hydrogen escapes; Earth like Venus
    ex = sx + 2100
    p.pic('earth', ex, 80, h=380, at='2:But the Earth')
    p.pic('sun', ex + 820, -120, h=380, at='2:The Sun is')
    p.glows([(ex + 820, -120)], '2:getting brighter', size=420)
    h2o(p, ex + 120, -330, '2:break water', r=30)
    p.label('IN ABOUT 1 BILLION YEARS', ex + 120, -470, '2:one billion', size=30, color='accent')
    for k, dx in enumerate((-90, 90)):
        p.stream(rise(ex + 120 + dx, -280, dx * 1.5, -700, 0.2), T('2:its hydrogen', 0.2 * k), count=5, period=3.0, size=14, spread=10)
    p.label('HYDROGEN ESCAPES INTO SPACE', ex + 120, 380, '2:escape into', size=28, weight=500)
    p.cam('2:But the Earth', x=ex + 300, y=0, zoom=0.88)
    p.cam('2:In about', x=ex + 150, y=-260, zoom=0.95)
    vx = ex + 1700
    p.pic('venus', vx, 0, h=460, at='2:like Venus')
    p.label('DRY, AND MUCH TOO HOT FOR LIFE', vx, 330, '2:dry', size=28)
    p.cam('2:Our planet', x=vx, y=0, zoom=0.95)
    # The red giant swallows Mercury and Venus, maybe the Earth
    gx = vx + 1700
    p.pic('red_giant', gx, 0, h=900, at='3:red giant')
    for k, (dx, dy, r) in enumerate(((-600, -140, 22), (-760, 120, 30))):
        p.circle(gx + dx, dy, r, T('3:Billions', 0.2 * k), width=2.0, fill='paper', out='3:swallow Mercury+0.6')
    p.label('MERCURY', gx - 600, -190, '3:Billions+0.3', '3:swallow Mercury+0.6', size=20, weight=500)
    p.label('VENUS', gx - 760, 70, '3:Billions+0.5', '3:swallow Mercury+0.6', size=20, weight=500)
    p.pic('earth', gx - 950, 160, h=110, at='3:Whether the Earth', out='3:swallowed too+0.4')
    question(p, gx - 950, 30, '3:not certain', '3:swallowed too+0.4', size=70)
    p.cam('3:Billions', x=gx - 200, y=0, zoom=0.62)
    p.cam('3:Whether the Earth', x=gx - 500, y=60, zoom=0.72)
    p.label('NOTHING IS DESTROYED', gx - 300, -540, '4:nothing is destroyed', size=44)
    p.glows(scatter(gx - 950, 160, 220, 180, 7, seed=5), '4:its atoms', size=40, stagger=0.15)
    p.stream(rise(gx - 950, 160, -200, -300, 0.2), '4:still be there', count=8, period=4.0, size=12, spread=30)
    p.cam('4:It can feel', x=gx - 400, y=-40, zoom=0.68)
    p.cam('4:Even when', x=gx - 500, y=40, zoom=0.7)
    question(p, gx - 300, 520, '5:So what', size=100)
    p.cam('5:then@end', x=gx - 300, y=40, zoom=0.62)
    p.end_all()


def part7(p):
    chapter(p, 7, 'If the Earth')
    p.cam('start', x=0, y=0, zoom=0.82)
    p.pic('red_giant', 0, 0, h=760, at='1:If the Earth')
    p.circle(0, 0, 450, '1:outer layers', width=2.2, color='accent', duration=1.2)
    ring = [(430 * math.cos(a), 430 * math.sin(a)) for a in [i * 2 * math.pi / 40 for i in range(41)]]
    p.stream(ring, '1:its atoms', count=14, period=6.0, size=14, spread=12)
    p.circle(0, 0, 600, '1:let go', width=1.8, color='muted', dashed=True)
    p.cam('1:And those are', x=0, y=0, zoom=0.72)
    # Loses almost half its mass; a glowing cloud; a white dwarf; tens of thousands of them
    p.label('ALMOST HALF ITS MASS', 0, -680, '2:almost half', '2:Its outer-0.2', size=40, color='accent')
    p.cam('2:A star', x=0, y=-120, zoom=0.72)
    nx = 1700
    p.pic('planetary_nebula', nx, 0, h=660, at='2:Its outer')
    p.glows([(nx, 0)], '2:white dwarf', size=60)
    p.label('WHITE DWARF', nx, 400, '2:white dwarf', size=34)
    p.cam('2:Its outer', x=nx, y=0, zoom=0.92)
    p.cam('2:In the center', x=nx, y=60, zoom=1.15)
    p.glows(scatter(nx, 0, 3000, 1400, 24, seed=9), '2:tens of thousands', size=34, stagger=0.06)
    p.label('TENS OF THOUSANDS IN OUR GALAXY', nx, -560, '2:tens of thousands', size=40)
    p.cam('2:There are', x=nx, y=-60, zoom=0.62)
    # Gas joins the clouds between stars; raw material; a new star and planets
    cx = nx + 2000
    p.pic('nebula', cx, 0, h=620, at='3:joins')
    p.stream([(nx + 300, 0), (nx + 900, -60), (cx - 200, 0)], '3:The gas', count=12, period=3.4, size=13, spread=30)
    p.label('RAW MATERIAL', cx, 400, '3:raw material', size=40, color='accent')
    p.cam('3:The gas', x=cx - 500, y=0, zoom=0.8)
    p.cam('3:raw material', x=cx, y=60, zoom=0.92)
    dx = cx + 1300
    p.pic('young_sun_disk', dx, 0, w=760, at='3:gather and collapse')
    p.cam('3:One day', x=dx, y=0, zoom=0.95)
    sx = dx + 1250
    p.pic('sun', sx, -40, h=320, at='3:our own solar')
    p.pic('earth', sx + 380, 120, h=120, at='3:our own solar+0.4')
    p.label('LEFTOVERS OF OLDER STARS', sx + 150, 330, '3:leftovers', size=36)
    p.cam('3:Just like', x=sx + 150, y=40, zoom=1.0)
    # The atoms a star gives back are richer than the ones it took in
    kx = sx + 1500
    p.glows([(kx, 0)], "4:And here's", size=260)
    for k, (sym, y) in enumerate((('H', -90), ('He', 90))):
        p.tile(sym, None, kx - 520, y, T('4:The atoms a star', 0.2 * k), s=90)
        p.arrow((kx - 450, y), (kx - 170, y * 0.4), T('4:The atoms a star', 0.2 * k + 0.2), width=2.0)
    for k, (sym, y) in enumerate((('C', -180), ('O', 0), ('Fe', 180))):
        p.arrow((kx + 170, y * 0.4), (kx + 430, y), T("4:aren't the same", 0.2 * k), width=2.0)
        p.tile(sym, None, kx + 520, y, T("4:aren't the same", 0.2 * k + 0.2), s=90, fill='accent', fill_at='4:new elements')
    p.label('A LITTLE RICHER', kx, 380, '4:a little richer', size=44, color='accent')
    p.cam("4:And here's", x=kx, y=0, zoom=1.0)
    p.cam('4:So every time', x=kx, y=40, zoom=0.92)
    # Something alive again, on a new planet
    px = kx + 1500
    p.pic('earth', px, 80, h=360, at='5:one of those planets')
    p.pic('tree', px, -200, h=170, at='5:alive again')
    p.glows([(px, -200)], '5:alive again', size=120)
    question(p, px + 420, -260, '6:So, what', size=110)
    p.cam('5:And on one', x=px, y=0, zoom=1.0)
    p.cam('6:you@end', x=px, y=0, zoom=0.9)
    p.end_all()


def part8(p):
    p.label('WHAT DOES IT MEAN FOR YOU?', 960, 540, 0.25, "1:Let's-0.55", size=44, space='screen')
    p.cam('start', x=0, y=0, zoom=0.92)
    me = p.pic('person', 0, 0, h=700, at="1:Let's")
    lungs = p.pic('lungs', 640, -60, h=340, at='1:Every breath')
    bust = p.pic('roman_bust', -640, -60, h=340, at='1:holds a little')
    p.stream([p.pt(bust, BUST_LIPS), (-200, -420), (300, -420), p.pt(lungs, LUNGS_TOP)], '1:the past', '2:Some will rise', count=9, period=3.2, size=15, spread=8, color='accent')
    p.label('ALMOST NONE ARE DESTROYED', 0, 440, '1:almost none', '2:Some will rise', size=38)
    p.cam('1:Every breath', x=0, y=0, zoom=0.86)
    # Some to the air; trees, animals, people; the sea floor and mountains; a new star
    p.pic('cloud', 1300, -430, h=210, at='2:rise into')
    p.stream(rise(80, -200, 1150, -260, 0.2), '2:rise into', count=10, period=3.2, size=13, spread=14)
    p.pic('tree', 1900, 20, h=420, at='2:trees')
    p.pic('deer', 2350, 110, h=250, at='2:animals')
    p.pic('person', 2800, 20, h=460, at='2:other people')
    layers(p, 3200, 4000, 360, '2:bottom of the sea', n=3, gap=30)
    p.pic('mountain', 3600, 120, w=560, at='2:stone of a')
    p.glows([(4500, -250)], '2:shine again', size=240)
    p.stream([(3700, 0), (4100, -200), (4480, -250)], '2:shine again', count=9, period=3.0, size=14, spread=12, color='accent')
    p.cam('2:Some will rise', x=700, y=-150, zoom=0.86)
    p.cam('2:Some will become', x=2350, y=40, zoom=0.86)
    p.cam('2:Some will rest', x=3600, y=160, zoom=0.92)
    p.cam('2:And one day', x=2400, y=0, zoom=0.4)
    # Marcus Aurelius
    mx = 5800
    p.pic('marcus_bust', mx, 0, h=600, at='3:Almost two')
    p.label('ALMOST 2,000 YEARS AGO', mx, -380, '3:Almost two', '3:Its elements', size=30, color='accent')
    p.label('MARCUS AURELIUS', mx, 380, '3:Marcus Aurelius', size=36)
    p.label('MEDITATIONS, BOOK VIII', mx, 440, '3:Marcus Aurelius+0.3', size=22, weight=500, color='accent')
    qx = mx + 1050
    p.label('“IT CANNOT FALL OUT OF THE WORLD”', qx, -200, '3:cannot fall', size=30)
    p.label('“THE SAME ARE THE WORLD’S ELEMENTS”', qx, -80, "3:Its elements", size=30)
    p.label('“THEY MURMUR NOT”', qx, 40, '3:do not complain', size=30)
    p.label('WHY SHOULDEST THOU?', qx, 200, '3:So why', size=48, color='accent')
    p.cam('3:Almost two', x=mx + 300, y=40, zoom=0.86)
    p.cam('3:Its elements', x=mx + 500, y=20, zoom=0.86)
    # You came from the stars, and one day you'll go back
    yx = qx + 1500
    me3 = p.pic('person', yx, 40, h=660, at='4:You came')
    stars = [(yx + dx, -430 + dy) for dx, dy in [(-500, -40), (-300, 90), (-80, -110), (160, 40), (380, -80), (560, 100), (-650, 140), (60, 150)]]
    p.glows(stars, '4:the stars', size=40, stagger=0.1)
    for k, (u, v) in enumerate([CHEST, FACE, ARM]):
        s = p.pt(me3, (u, v))
        p.stream(rise(s[0], s[1], [-300, 60, 380][k], -560, 0.3), T("4:you'll go back", 0.25 * k), count=8, period=3.6, size=13, spread=12, color='accent' if k == 1 else None)
    p.label('NOTHING IS LOST', yx, 470, "4:go back@end", size=50)
    p.cam('4:You came', x=yx, y=0, zoom=0.92)
    p.cam("4:you'll go back", x=yx, y=-60, zoom=0.82)
    p.cam('end', x=yx, y=-60, zoom=0.74)
    p.end_all('end-0.2')


BUILDERS = [part0, part1, part2, part3, part4, part5, part6, part7, part8]


def resolve(words, ref):
    """Seconds for a time reference, exactly as src/template/time.ts reads it."""
    if isinstance(ref, (int, float)):
        return float(ref)
    norm = lambda x: re.sub(r"[^a-z0-9']", '', x.lower())
    body, off = ref.strip(), 0.0
    m = re.match(r'^(.*?)\s*([+-]\s*\d+(?:\.\d+)?)$', body)
    if m and m.group(1):
        body, off = m.group(1).strip(), float(m.group(2).replace(' ', ''))
    if body == 'start':
        return off
    if body in ('end', 'voiceEnd'):
        return words['duration'] + off
    m = re.match(r'^(\d+):(.+?)(@end)?$', body)
    line = int(m.group(1))
    toks = [norm(t) for t in m.group(2).split() if norm(t)]
    ws = [w for w in words['words'] if w['line'] == line]
    for i in range(len(ws) - len(toks) + 1):
        if all(norm(ws[i + j]['text']) == tk for j, tk in enumerate(toks)):
            return (ws[i + len(toks) - 1]['end'] if m.group(3) else ws[i]['start']) + off
    raise SystemExit(f'cannot resolve {ref}')


MOVE = 1.3


def settle_camera(camera, words):
    """The camera holds still, and moves only when a key asks for a new framing: it starts moving
    at the key's time and arrives MOVE seconds later (slower for small zooms), never overlapping
    the next move. Without this, the spline drifts toward each next key the whole time."""
    keys = sorted(((resolve(words, c['at']), i, c) for i, c in enumerate(camera)), key=lambda k: (k[0], k[1]))
    out = []
    for n, (t, _, c) in enumerate(keys):
        if not out:
            out.append({**c, 'at': round(t, 3)})
            continue
        prev = out[-1]
        same = abs(prev['x'] - c['x']) < 1 and abs(prev['y'] - c['y']) < 1 and abs(prev['zoom'] - c['zoom']) < 1e-3
        if same:
            if t > prev['at'] + 0.01:
                out.append({**c, 'at': round(t, 3)})
            continue
        t = max(t, prev['at'] + 0.05)
        t_next = keys[n + 1][0] if n + 1 < len(keys) else t + 4
        dist = math.hypot(c['x'] - prev['x'], c['y'] - prev['y']) * c['zoom']
        move = MOVE if dist > 140 else 2.6
        move = max(0.5, min(move, t_next - t - 0.15))
        out.append({'at': round(t, 3), 'x': prev['x'], 'y': prev['y'], 'zoom': prev['zoom']})
        out.append({**c, 'at': round(t + move, 3)})
    return out


def part_seconds(n):
    w = json.load(open(f'{ROOT}/p{n}/words.json'))
    return math.ceil(w['duration'] * 60) / 60


def main():
    ox, oy, oz = 0.0, 0.0, None
    clock = 0.0
    for n, build in enumerate(BUILDERS):
        d = f'{ROOT}/p{n}'
        words = json.load(open(f'{d}/words.json'))
        p = Part(PICS, n, words)
        build(p)
        if oz is not None:
            # Start exactly where the previous part's camera ended.
            first = p.camera[0]
            first['zoom'] = oz
            for c in p.camera:
                if c['at'] == 'start':
                    c['zoom'] = oz
        p.shift(ox - p.camera[0]['x'], oy - p.camera[0]['y'])
        end_cam = p.camera[-1]
        if end_cam['at'] != 'end':
            p.camera.append({'at': 'end', 'x': end_cam['x'], 'y': end_cam['y'], 'zoom': end_cam['zoom']})
        ox, oy, oz = p.camera[-1]['x'], p.camera[-1]['y'], p.camera[-1]['zoom']
        p.camera = settle_camera(p.camera, words)
        title = 'What Happens to Your Atoms When You Die?' + ('' if n == 0 else f' — part {n}')
        s = p.settings(THEME, title)
        s['clock'] = round(clock, 4)
        clock += part_seconds(n)
        json.dump(s, open(f'{d}/settings.json', 'w'), indent=1)
        print(f'p{n}: {len(p.items)} pictures, {len(p.drawings)} drawings, {len(p.lights)} lights, {len(p.streams)} streams, {len(p.labels)} labels, {len(p.camera)} camera keys')


if __name__ == '__main__':
    main()
    for a in sorted(AMBIGUOUS):
        print('ambiguous:', a)
