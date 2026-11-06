"""Builds public/videos/never-touched-anything/p0..p8/settings.json from the shot list in
projects/never-touched-anything/script.md.

Same method and look as video 2 (tools/build_atoms_when_you_die.py): one camera that holds still and
moves on cue, the blue glowing page, and scenes that leave together. Adds atom diagrams: a nucleus as a
small gold glow, electrons as glowing dots that circle or swarm around it.
Run: python tools/build_never_touched.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from stars_lib import AMBIGUOUS, T, Part, Pictures  # noqa: E402
from build_atoms_when_you_die import (THEME, ARM, CHEST, FACE, close, mark, question, rise, scatter,  # noqa: E402
                                      settle_camera, waves)

ROOT = 'public/videos/never-touched-anything'
PICS = Pictures(f'{ROOT}/images', '/videos/never-touched-anything/images')
TITLES = {
    1: 'WHAT ARE YOU MADE OF, REALLY?',
    2: 'HOW DO WE KNOW?',
    3: 'WHY ARE THINGS SOLID?',
    4: 'WHAT HAPPENS WHEN YOU TOUCH?',
    5: 'HOW DO YOU FEEL IT?',
    6: 'HOW MUCH OF YOU IS EMPTY?',
    7: 'WHAT DOES IT MEAN TO TOUCH SOMEONE?',
}


def chapter(p, n, first):
    out = f'1:{first}-0.55'
    p.label(f'CHAPTER {n}', 960, 470, 0.25, out, size=28, space='screen', color='accent', spacing=0.5)
    p.label(TITLES[n], 960, 548, 0.45, out, size=min(58, round(1500 / (len(TITLES[n]) * 0.98))), space='screen')


# ---- atom helpers ---------------------------------------------------------------------------
def ring(cx, cy, r, n=40, ry=None, rot=0.0):
    ry = r if ry is None else ry
    a = math.radians(rot)
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        x, y = r * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return pts


def cloud(p, x, y, r, at, to=None, count=10, nucleus=True, size=None, spread=None, period=None):
    """An atom as a soft cloud: electrons swarming on a circle, a tiny gold nucleus in the middle."""
    size = size or max(10, r * 0.24)
    p.stream(ring(x, y, r, 36), at, to, count=count, period=period or (2.4 + r / 60), size=size, spread=spread if spread is not None else r * 0.35)
    if nucleus:
        p.glows([(x, y)], at, to, size=max(16, r * 0.35))


def atom_model(p, x, y, at, out=None, s=1.0, labels=False):
    """A classic atom: nucleus of protons (gold) and neutrons, two orbits with electrons travelling on them."""
    ps = [(0, 0), (16, 8), (-14, 10), (6, -15), (-8, -12), (18, -8), (-18, -4)]
    for i, (dx, dy) in enumerate(ps):
        p.circle(x + dx * s, y + dy * s, 11 * s, T(at, 0.05 * i), out, width=1.6, fill='accent' if i % 2 == 0 else 'paper', fillOpacity=0.8 if i % 2 == 0 else 1)
    p.glows([(x, y)], at, out, size=80 * s)
    for k, rot in enumerate((20, -40)):
        pts = ring(x, y, 190 * s, 60, 70 * s, rot)
        p.line(pts, T(at, 0.3 + 0.15 * k), out, width=1.4, color='muted', dashed=True)
        p.stream(pts, T(at, 0.5 + 0.2 * k), out, count=2, period=3.0 + k, size=16 * s, spread=0, curve=False)
    if labels:
        p.label('PROTONS', x - 150 * s, y - 120 * s, labels[0], out, size=24, color='accent')
        p.label('NEUTRONS', x + 150 * s, y - 120 * s, T(labels[0], 0.3), out, size=24)
        p.label('ELECTRONS  −', x, y + 140 * s, labels[1], out, size=28)


def two_rows(p, cx, cy, at, out=None, n=4, r=44, gap=56, arrows_at=None):
    """Two rows of atom clouds facing each other across a thin gap (the place where two things 'touch')."""
    pitch = r * 2.4
    x0 = cx - pitch * (n - 1) / 2
    for i in range(n):
        x = x0 + i * pitch
        cloud(p, x, cy - gap / 2 - r, r, T(at, 0.04 * i), out, count=7)
        cloud(p, x, cy + gap / 2 + r, r, T(at, 0.04 * i + 0.1), out, count=7)
    if arrows_at:
        for i in range(0, n, 2):
            x = x0 + i * pitch
            p.arrow((x, cy - 8), (x, cy - gap / 2 - r * 1.2), T(arrows_at, 0.08 * i), out, width=1.8, color='accent')
            p.arrow((x, cy + 8), (x, cy + gap / 2 + r * 1.2), T(arrows_at, 0.08 * i), out, width=1.8, color='accent')


def apart(p, x1, y1, x2, y2, at, out=None, color='accent'):
    """Two arrows pushing away from each other, between two points."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = (x2 - x1), (y2 - y1)
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    p.arrow((x1 - ux * 20, y1 - uy * 20), (x1 - ux * 110, y1 - uy * 110), at, out, width=2.2, color=color)
    p.arrow((x2 + ux * 20, y2 + uy * 20), (x2 + ux * 110, y2 + uy * 110), at, out, width=2.2, color=color)


def charge(p, x, y, at, out=None, r=34, sign='−'):
    p.circle(x, y, r, at, out, width=2.2, fill='accent', fillOpacity=0.35)
    p.label(sign, x, y - 2, T(at, 0.15), out, size=round(r * 0.9), spacing=0.02, upper=False)


def floor(p, x0, x1, y, at, out=None):
    p.line([(x0, y), (x1, y)], at, out, width=2.2)
    for x in range(int(x0) + 20, int(x1), 60):
        p.line([(x, y), (x - 26, y + 26)], T(at, 0.2), out, width=1.2, color='muted')


# ======================================================================================
def part0(p):
    p.cam('start', x=0, y=0, zoom=1.0)
    m = mark(p)
    p.label('YOU HAVE NEVER', 0, -50, '1:You have never', size=52)
    p.label('TOUCHED ANYTHING', 0, 40, '1:actually touched', size=52, color='accent')
    close(p, m, '1:Not the floor')
    fx = 1000
    floor(p, fx - 300, fx + 300, 160, '1:Not the floor')
    p.pic('feet', fx, 30, h=240, at='1:Not the floor')
    p.pic('phone', fx + 800, -10, h=430, at='1:Not this screen')
    hx = fx + 1750
    hands = p.pic('holding_hands', hx, 0, w=560, at='1:Not even')
    p.cam('1:Not the floor', x=fx, y=40, zoom=1.0)
    p.cam('1:Not this screen', x=fx + 800, y=0, zoom=1.0)
    p.cam('1:Not even', x=hx, y=0, zoom=1.0)
    # Inside the place where the hands meet: two rows of atoms that never meet
    m_rows = mark(p)
    two_rows(p, hx, 560, '1:The atoms of your', n=4, r=50, gap=60, arrows_at='1:anything else')
    p.label('YOUR ATOMS', hx - 420, 560 - 80, '1:The atoms of your', size=26)
    p.label('THEIR ATOMS', hx - 420, 560 + 80, '1:the atoms of anything', size=26)
    close(p, m_rows, '2:And yet')
    p.cam('1:The atoms of your', x=hx, y=520, zoom=1.0)
    p.glows([(hx - 60, 10), (hx + 40, -20), (hx + 120, 20)], '2:you feel', size=70, stagger=0.15)
    p.cam('2:And yet', x=hx, y=60, zoom=1.0)
    p.label('WHAT IS TOUCH?', hx, -330, "2:So what's", size=48, color='accent')
    # The three stops of the journey
    jx = hx + 1300
    atom_model(p, jx, -20, '2:inside the atom', s=1.1)
    floor(p, jx + 650, jx + 1050, 170, '2:fall through')
    p.pic('feet', jx + 850, 30, h=280, at='2:fall through')
    p.pic('brain', jx + 1550, -10, h=360, at='2:what touch')
    p.cam('2:In this video', x=jx + 300, y=0, zoom=0.86)
    p.cam('2:fall through', x=jx + 650, y=0, zoom=0.82)
    p.cam('2:what touch', x=jx + 780, y=0, zoom=0.8)
    p.end_all()


def part1(p):
    chapter(p, 1, 'Everything')
    p.cam('start', x=0, y=0, zoom=0.95)
    m = mark(p)
    me = p.pic('person', -250, 0, h=680, at='1:Everything')
    p.glows(scatter(-250, 0, 700, 760, 14, seed=4), '1:made of atoms', size=34, stagger=0.06)
    p.pic('open_hand', 350, -250, h=200, at='1:Your skin')
    waves(p, 200, 520, 10, '1:the air', n=2, gap=24, amp=8)
    p.pic('chair', 360, 250, h=240, at='1:the chair')
    p.cam('1:Your skin', x=40, y=0, zoom=0.95)
    close(p, m, '1:An atom is')
    p.label('0.0000000001 m', 1300, -40, '1:An atom is', size=60, spacing=0.06, upper=False)
    p.label('ONE TEN-BILLIONTH OF A METER', 1300, 50, '1:ten-billionth', size=26, color='accent')
    p.glows([(1300, 180)], '1:hard to picture', size=30)
    p.cam('1:An atom is', x=1300, y=20, zoom=1.0)
    # The parts of an atom
    ax = 2400
    m_atom = mark(p)
    atom_model(p, ax, 0, '2:Each atom', s=1.4, labels=('2:protons', '2:Around it'))
    p.cam('2:Each atom', x=ax, y=20, zoom=1.0)
    close(p, m_atom, '3:So picture')
    # The stadium and the blueberry
    sx = 3800
    m2 = mark(p)
    stad = p.pic('stadium', sx, 0, w=880, at='3:So picture+0.5')
    p.glows([(sx, 0)], '3:very center', size=40)
    p.mag(stad, (0.5, 0.5), 12, sx + 700, -230, 160, '3:blueberry', '4:The rest of', [{'picture': 'blueberry', 'scale': 1.6}])
    p.label('A BLUEBERRY', sx + 700, -30, '3:blueberry+0.4', '4:The rest of', size=30, color='accent')
    p.cam('3:So picture', x=sx - 300, y=0, zoom=0.9)
    p.cam('3:football stadium', x=sx + 150, y=0, zoom=0.92)
    p.stream(ring(sx, 0, 380, 48, 220), '4:The rest of', count=26, period=7, size=12, spread=110)
    p.cam('4:The rest of', x=sx, y=0, zoom=0.92)
    # 1 proton = 1,800 electrons
    bx = sx + 1500
    p.line([(bx, 260), (bx, -60)], '4:so light', width=2.2)
    p.line([(bx - 360, -60), (bx + 360, -60)], '4:so light+0.2', width=2.2)
    for sxn in (-1, 1):
        x = bx + sxn * 360
        p.line([(x - 120, 60), (x - 80, 95), (x + 80, 95), (x + 120, 60)], '4:so light+0.3', width=2.0)
        p.line([(x, -60), (x - 110, 60)], '4:so light+0.3', width=1.4, color='muted')
        p.line([(x, -60), (x + 110, 60)], '4:so light+0.3', width=1.4, color='muted')
    p.circle(bx - 360, 50, 34, '4:one proton', width=2.2, fill='accent', fillOpacity=0.7)
    p.label('1 PROTON', bx - 360, 170, '4:one proton', size=28)
    p.glows(scatter(bx + 360, 50, 190, 50, 18, seed=8), '4:it would take', size=14, stagger=0.03)
    p.label('{n} ELECTRONS', bx + 360, 170, '4:1,800', size=28, count={'to': 1800, 'duration': 1.4})
    p.cam('4:so light', x=bx, y=40, zoom=1.0)
    p.cam('4:Yet they', x=sx, y=0, zoom=0.92)
    p.label('ALMOST ALL THE WEIGHT', sx, -330, '5:weight', size=30, color='accent')
    p.line([(sx, -295), (sx, -25)], '5:weight', width=1.4, color='accent', dashed=True)
    p.label('ALMOST ALL THE SPACE', sx, 330, '5:size', size=36)
    close(p, m2, '6:So how')
    question(p, sx, -330, '6:So how', size=110)
    p.cam('5:Almost all of an', x=sx, y=20, zoom=0.92)
    p.end_all()


def part2(p):
    chapter(p, 2, 'A little')
    p.cam('start', x=0, y=0, zoom=0.95)
    m = mark(p)
    p.pic('microscope', -330, -30, h=520, at='1:A little')
    p.label('ERNEST RUTHERFORD', 230, -60, '1:Ernest Rutherford', size=32, align='left', spacing=0.14)
    p.label('FROM NEW ZEALAND', 230, 0, '1:New Zealand', size=24, color='accent', align='left', spacing=0.14)
    p.label('WITH HANS GEIGER', 230, 90, '1:Hans Geiger', size=24, align='left', spacing=0.14)
    p.label('AND ERNEST MARSDEN', 230, 140, '1:Ernest Marsden', size=24, align='left', spacing=0.14)
    p.cam('1:A little', x=200, y=0, zoom=0.95)
    close(p, m, '2:They fired')
    # The gold foil experiment
    gx = 2000
    m = mark(p)
    p.rect(gx - 620, 0, 150, 110, '2:They fired', width=2.2, fill='paper')
    p.glows([(gx - 620, 0)], '2:tiny particles', size=34)
    p.label('ALPHA PARTICLES', gx - 620, 120, '2:alpha particles', size=26, color='accent')
    p.rect(gx, 0, 16, 440, '2:gold foil', width=2.0, fill='accent', fillOpacity=0.6)
    p.label('GOLD FOIL', gx, -270, '2:gold foil', size=28)
    p.circle(gx, 0, 440, '2:glowing screen', width=1.6, color='muted', dashed=True)
    p.label('GLOWING SCREEN', gx, 480, '2:glowing screen', size=24)
    p.stream([(gx - 540, 0), (gx, 0), (gx + 430, 0)], '3:Most of', count=16, period=2.0, size=12, spread=60, curve=False)
    p.glows([(gx + 435, -40), (gx + 437, 25), (gx + 433, 60), (gx + 436, -10)], '3:straight through', size=40, stagger=0.25)
    p.stream([(gx - 540, 30), (gx - 8, 30), (gx - 500, -120)], '3:bounced', count=2, period=2.4, size=18, spread=0, color='accent', curve=False)
    p.glows([(gx - 430, -150)], '3:almost straight back', size=50)
    p.cam('2:They fired', x=gx - 250, y=0, zoom=0.95)
    p.cam('2:glowing screen', x=gx, y=0, zoom=0.92)
    close(p, m, '4:Rutherford realized+0.6')
    # What it meant: a close-up of the foil. Big, mostly empty atoms with tiny heavy centres;
    # particles fly straight through the empty space, and only one near a centre is knocked off course.
    ax = gx + 1500
    m = mark(p)
    p.label('WHAT IT MEANT', ax, -465, '4:Rutherford realized', size=36, color='accent')
    for k in range(3):
        y = -265 + 265 * k
        p.circle(ax, y, 122, T('4:mostly empty space', 0.15 * k), width=1.6, color='muted', dashed=True)
        p.glows(scatter(ax, y, 170, 170, 3, seed=k + 3), T('4:mostly empty space+0.5', 0.15 * k), size=12)
        p.glows([(ax, y)], T('4:tiny, heavy', 0.15 * k), size=30)
        p.label('+', ax + 30, y - 30, T('4:positive charge', 0.15 * k), size=24, color='accent', spacing=0.02)
    p.stream([(ax - 900, -132), (ax + 900, -132)], '4:Almost all of', count=6, period=2.6, size=12, spread=30, curve=False)
    p.stream([(ax - 900, 132), (ax + 900, 132)], '4:Almost all of+0.4', count=6, period=2.6, size=12, spread=30, curve=False)
    bend = p.line([(ax - 700, -20), (ax - 60, -8), (ax + 20, 20), (ax + 560, 300)], '4:knocked off', width=1.8, curve=True, color='accent')
    p.travel(bend, '4:knocked off', dur=1.4, size=44)
    p.label('THE SOLID WORLD WAS MOSTLY EMPTY', ax, 520, '4:The solid world', size=36)
    p.cam('4:Rutherford realized', x=ax, y=0, zoom=0.86)
    p.cam('4:mostly empty space', x=ax, y=0, zoom=0.95)
    p.cam('4:The solid world', x=ax, y=0, zoom=0.82)
    close(p, m, '5:So if')
    fx = ax + 1300
    floor(p, fx - 300, fx + 300, 160, '5:So if')
    p.pic('feet', fx, 30, h=240, at='5:So if')
    question(p, fx + 320, -160, '5:fall right', size=110)
    p.cam('5:So if', x=fx + 80, y=0, zoom=1.0)
    p.end_all()


def part3(p):
    chapter(p, 3, 'The answer')
    p.cam('start', x=0, y=0, zoom=1.0)
    m = mark(p)
    cloud(p, 0, 0, 180, '1:The answer', count=26, size=12)
    p.label('ELECTRONS', 0, -280, '1:in the electrons', size=36, color='accent')
    p.cam('1:wrapped', x=0, y=0, zoom=1.12)
    for k, (dx, dy) in enumerate(((-200, -60), (190, -90), (-120, 170), (150, 150))):
        p.label('−', dx, dy, T('1:negative charge', 0.12 * k), size=50, color='accent', spacing=0.02)
    p.circle(650, 0, 110, "1:hard little", width=2.4, fill='paper')
    p.line([(560, -90), (740, 90)], "1:aren't hard+0.6", width=2.6, color='accent')
    p.line([(740, -90), (560, 90)], "1:aren't hard+0.6", width=2.6, color='accent')
    p.cam("1:Atoms aren't", x=330, y=0, zoom=0.95)
    close(p, m, '1:clouds of electric')
    cx = 1700
    cloud(p, cx - 190, 0, 150, '1:clouds of electric', count=22, size=11)
    cloud(p, cx + 190, 0, 150, '1:clouds of electric+0.2', count=22, size=11)
    p.label('CLOUDS OF CHARGE', cx, -270, '1:clouds of electric', size=32, color='accent')
    p.label('THEY KEEP THEIR DISTANCE', cx, 280, '1:keep their distance', size=32)
    p.cam('1:clouds of electric', x=cx, y=20, zoom=1.0)
    # Same charges push apart
    qx = cx + 1200
    charge(p, qx - 130, 0, '2:Charges of the same')
    charge(p, qx + 130, 0, '2:Charges of the same+0.15')
    apart(p, qx - 130, 0, qx + 130, 0, '2:push each other')
    p.label('SAME CHARGES PUSH APART', qx, 160, '2:push each other', size=30, color='accent')
    p.cam('2:Charges of the same', x=qx, y=0, zoom=1.05)
    # Your feet and the floor, up close
    fx = qx + 1300
    m = mark(p)
    floor(p, fx - 380, fx + 380, -40, '2:atoms of your feet')
    p.pic('feet', fx, -170, h=240, at='2:atoms of your feet')
    close(p, m, '2:atoms of the floor+0.4')
    two_rows(p, fx, 330, '2:atoms of the floor', n=5, r=58, gap=110, arrows_at='2:push back')
    p.label('YOUR FEET', fx - 560, 330 - 113, '2:atoms of the floor', size=26)
    p.label('THE FLOOR', fx - 560, 330 + 113, '2:atoms of the floor', size=26)
    p.label('THE CLOSER, THE HARDER', fx, 610, '2:The closer', size=32, color='accent')
    p.cam('2:atoms of your feet', x=fx, y=0, zoom=0.95)
    p.cam('2:atoms of the floor', x=fx, y=330, zoom=1.0)
    # The exclusion principle
    ex = fx + 1400
    p.glows([(ex, 0)], "3:There's a second", size=50)
    p.label('RULE 2', ex, -360, "3:There's a second", size=36, color='accent')
    for k, r in enumerate((70, 130, 190)):
        p.circle(ex, 0, r, T("3:can't all crowd", 0.15 * k), width=1.4, color='muted', dashed=True)
    shells = [(70, 2), (130, 4), (190, 6)]
    dots, k = [], 0
    for r, n in shells:
        for i in range(n):
            a = -math.pi / 2 + 2 * math.pi * i / n + (0.3 if r > 100 else 0)
            dots.append((ex + r * math.cos(a), r * math.sin(a)))
    p.glows(dots, "3:can't all crowd+0.4", size=26, stagger=0.12)
    p.label('THE EXCLUSION PRINCIPLE', ex, 290, '3:exclusion principle', size=34)
    p.cam("3:There's a second", x=ex, y=0, zoom=1.0)
    # The floor pushes back
    gx = ex + 1300
    floor(p, gx - 380, gx + 380, 160, '4:Together')
    p.pic('feet', gx, 30, h=240, at='4:Together')
    for k in range(4):
        x = gx - 240 + 160 * k
        p.arrow((x, 330), (x, 190), T('4:pushing you away', 0.12 * k), width=2.4, color='accent')
    p.label('MATTER FEELS SOLID', gx, -230, '4:feel solid', size=36)
    p.label('THE FLOOR PUSHES BACK', gx, 420, '4:pushing you away', size=32, color='accent')
    question(p, gx + 480, -150, '5:So what', size=110)
    p.cam('4:Together', x=gx, y=80, zoom=1.0)
    p.cam('4:at the tiniest', x=gx, y=180, zoom=1.15)
    p.cam('5:So what', x=gx + 100, y=60, zoom=1.0)
    p.end_all()


def part4(p):
    chapter(p, 4, 'Press')
    p.cam('start', x=0, y=0, zoom=1.0)
    m = mark(p)
    p.pic('finger_press', -250, 0, h=330, at='1:Press')
    p.label('CONTACT?', -250, -260, '1:feels like contact', size=40, color='accent')
    p.circle(520, 0, 250, '1:never merge', width=1.8)
    p.line([(-330, 40), (270, 0)], '1:never merge', width=1.2, color='muted', dashed=True)
    two_rows(p, 520, 0, '1:never merge+0.2', n=4, r=40, gap=50, arrows_at='1:push each other apart')
    p.cam('1:Press', x=-250, y=0, zoom=1.0)
    p.cam('1:never merge', x=120, y=0, zoom=0.95)
    p.label('WHAT YOU FEEL IS THE PUSH', 120, 360, '2:What you feel', size=34)
    close(p, m, '2:electromagnetic force')
    # The electromagnetic force; magnets; electrons
    mx = 1600
    p.label('THE ELECTROMAGNETIC FORCE', mx, -330, '2:electromagnetic force', size=40, color='accent')
    p.pic('magnets', mx, -20, w=600, at='2:behind magnets')
    apart(p, mx - 320, -20, mx + 320, -20, '2:without ever touching')
    charge(p, mx - 120, 270, '2:Electrons do', r=36)
    charge(p, mx + 120, 270, '2:Electrons do+0.1', r=36)
    apart(p, mx - 120, 270, mx + 120, 270, '2:Electrons do+0.3')
    p.cam('2:electromagnetic force', x=mx, y=0, zoom=0.95)
    # The comb and the paper
    cx = mx + 1200
    p.pic('comb', cx, -150, w=520, at='3:Comb your hair')
    scraps = [(cx - 160, 230), (cx - 40, 250), (cx + 80, 225), (cx + 190, 245)]
    for k, (x, y) in enumerate(scraps):
        p.rect(x, y, 34, 22, T('3:scraps of paper', 0.1 * k), width=1.6, fill='paper')
        p.line([(x, y - 20), (x + 10, -100)], T('3:without touching', 0.1 * k), width=1.2, color='accent', dashed=True)
    p.label('ACROSS A GAP', cx, 360, '3:across a gap', size=32, color='accent')
    p.cam('3:Comb your hair', x=cx, y=40, zoom=1.0)
    # Almost every force you feel; except gravity
    fx = cx + 1300
    p.label('ALMOST EVERY FORCE YOU FEEL', fx + 200, -330, '4:almost every force', size=36)
    p.label('IS ONE FORCE', fx + 200, -262, '4:this one force', size=30, color='accent')
    p.pic('fist', fx - 250, 0, h=280, at='4:grip')
    p.pic('shoe', fx + 200, 40, w=320, at='4:friction')
    p.pic('rope', fx + 650, 10, h=230, at='4:pull of a rope')
    p.glows(scatter(fx + 200, 230, 900, 60, 12, seed=2), '4:All of it comes', size=22, stagger=0.05)
    p.label('ATOMS PUSHING AND PULLING', fx + 200, 330, '4:pushing and pulling', size=26)
    p.pic('earth', fx + 1400, 0, h=330, at='4:gravity')
    p.label('EXCEPT GRAVITY', fx + 1400, 250, '4:gravity', size=32, color='accent')
    p.cam('4:In fact', x=fx + 200, y=0, zoom=0.88)
    p.cam('4:The only', x=fx + 1100, y=0, zoom=0.88)
    # Rubbing hands: vibration into heat
    hx = fx + 2500
    p.pic('hands_rubbing', hx, -60, h=380, at='5:Rub your hands')
    p.lights.append({'worldPoints': [[hx, -60]], 'from': '5:get warm', 'size': 300, 'intensity': 0.55})
    for i in range(6):
        x = hx - 250 + 100 * i
        p.stream(ring(x, 260, 26, 16), T('5:clinging', 0.06 * i), count=3, period=0.9, size=13, spread=6)
    p.label('VIBRATION → HEAT', hx, 380, '5:heat', size=34, color='accent', upper=False)
    p.cam('5:Rub your hands', x=hx, y=40, zoom=1.0)
    # Leaning on a wall
    wx = hx + 1300
    p.pic('person', wx - 120, 20, h=640, at='6:So when you lean')
    p.rect(wx + 160, 20, 40, 700, '6:So when you lean', width=2.2, fill='paper')
    for k in range(5):
        y = -220 + 110 * k
        p.arrow((wx + 135, y), (wx + 20, y), T('6:atom by atom', 0.12 * k), width=2.2, color='accent')
    p.label('THE WALL PUSHES BACK', wx + 20, 420, '6:The wall pushes', size=32, color='accent')
    question(p, wx + 520, -180, '7:So how', size=110)
    p.cam('6:So when you lean', x=wx + 60, y=40, zoom=0.95)
    p.end_all()


def part5(p):
    chapter(p, 5, 'Your skin')
    p.cam('start', x=0, y=0, zoom=1.0)
    m = mark(p)
    skin = p.pic('skin', -200, 0, h=560, at='1:Your skin')
    pts = {'1:pressure': (0.45, 0.72), '1:vibration': (0.62, 0.62), '1:stretch': (0.33, 0.5), '1:single hair': (0.56, 0.2)}
    names = {'1:pressure': 'PRESSURE', '1:vibration': 'VIBRATION', '1:stretch': 'STRETCH', '1:single hair': 'A SINGLE HAIR'}
    for k, (at, uv) in enumerate(pts.items()):
        p.glow(skin, uv, at, None, size=60)
        p.label(names[at], 330, -150 + 90 * k, at, size=30, align='left')
    p.label('MECHANORECEPTORS', 140, 360, '1:mechanoreceptors', size=38, color='accent')
    p.cam('1:Your skin', x=100, y=20, zoom=1.0)
    close(p, m, '2:When the electrons')
    # The fingertip presses in; a signal leaves
    fx = 1400
    fp = p.pic('finger_press', fx, 0, h=330, at='2:When the electrons')
    p.glows([(fx - 90, 40)], '2:pressed in', size=70)
    p.stream([(fx - 90, 40), (fx + 100, -60), (fx + 500, -120)], '2:send a signal', count=6, period=1.6, size=14, spread=4, color='accent')
    p.cam('2:When the electrons', x=fx, y=0, zoom=1.0)
    # Up the nerves, the spinal cord, the thalamus, the cortex
    px = fx + 1300
    m = mark(p)
    me = p.pic('person', px, 0, h=720, at='3:The signal')
    path = [p.pt(me, uv) for uv in [(0.4, 0.55), (0.42, 0.42), (0.47, 0.32), (0.5, 0.45), (0.5, 0.33), (0.5, 0.22)]]
    route = p.line(path, '3:races up', width=1.8, curve=True, color='accent', duration=2.2)
    p.travel(route, '3:races up', dur=2.4, size=40)
    p.label('SPINAL CORD', px + 300, 0, '3:spinal cord', size=26, align='left')
    p.glows([p.pt(me, (0.5, 0.2))], '3:thalamus', size=60)
    p.label('THALAMUS', px + 300, -240, '3:thalamus', size=26, align='left', color='accent')
    p.cam('3:The signal', x=px + 150, y=0, zoom=0.95)
    close(p, m, '3:somatosensory')
    bx = px + 1200
    p.pic('brain', bx, -40, h=400, at='3:somatosensory')
    strip = p.line([(bx - 20, -230), (bx + 20, -120), (bx + 10, 0)], '3:somatosensory', width=5, curve=True, color='accent', duration=1.0)
    p.label('SOMATOSENSORY CORTEX', bx, 260, '3:somatosensory', size=30)
    face = p.line([(bx - 260, 120), (bx - 120, 40), (bx - 20, -60)], '3:Touch from your face', width=1.6, curve=True, dashed=True, color='accent')
    p.travel(face, '3:Touch from your face', dur=1.4, size=40)
    p.lights.append({'drawing': strip, 'from': '4:Only there', 'duration': 2.0, 'size': 70})
    for k, (txt, at, x, y) in enumerate((('THE HARD EDGE', '4:hard edge', bx - 480, -260), ('THE SMOOTH SURFACE', '4:smooth surface', bx + 480, -260), ('THE WARMTH OF ANOTHER HAND', '4:warmth', bx, -380))):
        p.label(txt, x, y, at, size=26, color='accent' if k == 2 else None)
    p.label('BUILT INSIDE YOUR BRAIN', bx, 360, '4:built inside', size=36)
    p.cam('3:From there', x=bx, y=0, zoom=0.95)
    p.cam('4:Only there', x=bx, y=-20, zoom=0.9)
    hx = bx + 1300
    p.pic('open_hand', hx, 40, h=300, at='5:So the world')
    for k in range(4):
        x = hx - 180 + 120 * k
        p.arrow((x, -180), (x, -40), T('5:pattern of forces', 0.1 * k), width=2.0, color='accent')
    p.label('A PATTERN OF FORCES', hx, 300, '5:pattern of forces', size=32)
    p.label('TRANSLATED BY YOUR BRAIN', hx, 360, '5:translated', size=26, color='accent')
    question(p, hx + 420, -200, '5:how much of you', size=110)
    p.cam('5:So the world', x=hx + 100, y=20, zoom=1.0)
    p.end_all()


def part6(p):
    chapter(p, 6, 'Almost all')
    p.cam('start', x=0, y=0, zoom=0.95)
    m = mark(p)
    me = p.pic('person', 0, 0, h=700, at='1:Almost all')
    inside = [p.pt(me, (0.45 + 0.1 * math.sin(i * 1.7), 0.15 + 0.75 * i / 13)) for i in range(14)]
    p.glows(inside, '1:nuclei', size=20, stagger=0.05)
    p.stream(ring(0, 0, 230, 40, 380), '1:Everything else', count=16, period=6, size=9, spread=80)
    p.label('ALMOST ALL OF YOUR MASS', 330, -60, '1:nuclei', size=26, align='left', color='accent', spacing=0.14)
    p.label('AND A LOT OF SPACE', 330, 10, '1:Everything else', size=26, align='left', spacing=0.14)
    p.cam('1:Almost all', x=200, y=0, zoom=0.95)
    close(p, m, '2:There is a place')
    # A dying star's core collapses into a neutron star
    sx = 1500
    m = mark(p)
    p.glows(scatter(sx + 300, -100, 1500, 700, 14, seed=12), '2:There is a place', size=30, stagger=0.08)
    p.label('WHERE THE SPACE IS GONE', sx + 250, -330, '2:that space is gone', '2:collapse', size=32, color='accent')
    p.pic('earth', sx, 0, h=380, at='2:When a giant')
    p.label('A CORE THE SIZE OF THE EARTH', sx, 280, '2:size of the Earth', size=26)
    p.arrow((sx + 230, 0), (sx + 480, 0), '2:collapse', width=2.4, color='accent')
    p.circle(sx + 560, 0, 10, '2:less than 20', width=2.2, fill='accent', fillOpacity=0.8)
    p.label('LESS THAN 20 KM', sx + 560, -70, '2:less than 20', size=26, color='accent')
    p.label('IN LESS THAN A SECOND', sx + 560, 70, '2:less than a second', size=22)
    p.cam('2:There is a place', x=sx + 250, y=0, zoom=0.92)
    close(p, m, "2:What's left+0.6")
    nx = sx + 1500
    m = mark(p)
    p.pic('neutron_star', nx, 0, h=380, at="2:What's left")
    p.label('THE DENSEST OBJECTS IN THE UNIVERSE', nx, -320, '2:densest', size=30)
    p.label('ONE GIANT NUCLEUS', nx, 280, '2:giant atomic nucleus', size=34, color='accent')
    p.label('{n}% NEUTRONS', nx, 350, '2:95 percent', size=28, count={'to': 95, 'duration': 1.2})
    for i in range(12):
        r, c = divmod(i, 4)
        p.circle(nx + 320 + c * 54 + (27 if r % 2 else 0), -50 + r * 48, 25, T('2:packed together', 0.04 * i), width=1.8, fill='paper')
    p.cam("2:What's left", x=nx, y=0, zoom=0.95)
    close(p, m, "3:It's so dense+0.4")
    # A sugar cube of neutron star; all of humanity in less than a sugar cube
    cx = nx + 1300
    p.pic('sugar_cube', cx, -20, h=240, at='3:a piece')
    p.label('ABOUT {n} TONS', cx, 230, '3:a billion tons', size=34, color='accent', count={'to': 1000000000, 'duration': 1.6})
    p.cam("3:It's so dense", x=cx, y=40, zoom=1.0)
    hx = cx + 1600
    crowd = scatter(hx, -40, 1500, 700, 46, seed=21)
    p.glows(crowd, '4:every person', size=24, stagger=0.03)
    p.label('EVERY PERSON ALIVE TODAY', hx, -500, '4:every person', '4:8 billion', size=30)
    p.label('ABOUT {n} PEOPLE', hx, -420, '4:8 billion', size=36, count={'to': 8000000000, 'duration': 1.6})
    p.pic('sugar_cube', hx, 260, h=120, at='4:squeezed')
    for k in range(6):
        q = crowd[k * 7]
        p.stream([q, ((q[0] + hx) / 2, (q[1] + 260) / 2 - 80), (hx, 250)], T('4:squeezed', 0.1 * k), count=4, period=1.8, size=10, spread=4, color='accent')
    p.label('LESS THAN A SUGAR CUBE', hx, 400, '4:less than a sugar', size=34, color='accent')
    p.cam('4:Now think', x=hx, y=0, zoom=0.72)
    p.cam('4:squeezed', x=hx, y=100, zoom=0.8)
    question(p, hx + 520, 0, '5:So what does', size=110)
    p.cam('5:All that life', x=hx, y=60, zoom=0.62)
    p.end_all()


def part7(p):
    chapter(p, 7, 'When you hold')
    p.cam('start', x=0, y=0, zoom=1.0)
    m = mark(p)
    p.pic('holding_hands', 0, -40, w=600, at='1:When you hold')
    m2 = mark(p)
    p.circle(0, 320, 210, '1:never merge', width=1.6)
    two_rows(p, 0, 320, '1:never merge+0.2', n=4, r=36, gap=46, arrows_at='1:push back')
    close(p, m2, '2:And yet')
    p.cam('1:When you hold', x=0, y=0, zoom=1.0)
    p.cam('1:never merge', x=0, y=150, zoom=0.9)
    p.glows([(-40, -60), (60, -40)], '2:warmth', size=90, stagger=0.4)
    p.pic('brain', 800, -120, h=300, at='2:Your brain')
    up = p.line([(120, -40), (450, -120), (660, -120)], '2:turns that push', width=1.6, curve=True, color='accent', dashed=True)
    p.travel(up, '2:turns that push', dur=1.4, size=46)
    p.cam('2:And yet', x=300, y=-40, zoom=0.9)
    close(p, m, '3:Maybe')
    # Never fully separate, never fully merged
    cx = 1900
    cloud(p, cx - 170, 0, 160, '3:never fully separate', count=22, size=11)
    cloud(p, cx + 170, 0, 160, '3:never fully separate+0.2', count=22, size=11)
    for k in range(3):
        y = -90 + 90 * k
        p.line([(cx - 30, y), (cx + 30, y)], T('3:through forces', 0.1 * k), width=1.6, color='accent')
    p.glows([(cx, 0)], '3:across a space', size=110)
    p.label('THE DEEPER LESSON', cx, -330, '3:deeper lesson', size=32, color='accent')
    p.label('NEVER FULLY SEPARATE', cx, -260, '3:never fully separate', size=26)
    p.label('NEVER FULLY MERGED', cx, 230, '3:never fully merged', size=26)
    p.label('WE MEET THROUGH FORCES', cx, 300, '3:through forces', size=32)
    p.cam('3:Maybe', x=cx, y=20, zoom=1.0)
    # Epictetus
    ex = cx + 1300
    p.pic('philosopher_bust', ex, 0, h=560, at='4:Almost two')
    p.label('EPICTETUS', ex, 330, '4:Epictetus', size=34)
    p.label('BORN THE SON OF A SLAVE', ex, 390, '4:son of a slave', size=22, color='accent')
    qx = ex + 330
    p.label('“NOT BY THINGS,', qx, -150, '4:not by things', size=26, align='left', spacing=0.14)
    p.label('BUT BY THE VIEWS WHICH THEY TAKE OF THINGS”', qx, -80, '4:but by the views', size=26, align='left', spacing=0.14)
    p.label('WITHIN OUR POWER', qx, 60, '4:things are within', size=28, align='left', spacing=0.14, color='accent')
    p.label('NOT WITHIN OUR POWER', qx, 120, '4:some things are not', size=28, align='left', spacing=0.14)
    p.cam('4:Almost two', x=ex + 300, y=0, zoom=0.86)
    p.cam('4:not by things', x=ex + 600, y=0, zoom=0.86)
    bx = ex + 2100
    p.pic('brain', bx, -20, h=380, at='4:science agrees')
    p.pic('earth', bx, -40, h=110, at='4:own picture')
    p.label('OUR PICTURE OF THE WORLD', bx, 260, '4:own picture', size=28)
    p.label('IS WITHIN OUR POWER', bx, 320, '4:And that picture', size=32, color='accent')
    p.cam('4:science agrees', x=bx, y=20, zoom=0.95)
    question(p, bx + 420, -220, '5:So if', size=110)
    p.end_all()


def part8(p):
    p.label('WHAT HAS BEEN TOUCHING YOU?', 960, 540, 0.25, "1:Let's-0.55", size=44, space='screen')
    p.cam('start', x=0, y=0, zoom=1.0)
    m = mark(p)
    p.pic('holding_hands', 0, 80, w=560, at="1:Let's")
    p.label('YOU HAVE NEVER', 0, -300, '1:You have never', size=40)
    p.label('TOUCHED ANYTHING', 0, -230, '1:You have never+0.3', size=40, color='accent')
    two_rows(p, 0, 420, '1:The atoms of your', n=4, r=36, gap=46)
    p.glows([(-40, 60), (60, 80)], '2:felt everything', size=90, stagger=0.3)
    p.cam("1:Let's", x=0, y=0, zoom=1.0)
    p.cam('1:The atoms of your', x=0, y=200, zoom=0.9)
    close(p, m, '2:The ground')
    gx = 1200
    floor(p, gx - 300, gx + 300, 160, '2:The ground')
    p.pic('feet', gx, 30, h=240, at='2:The ground')
    for k in range(3):
        x = gx - 160 + 160 * k
        p.arrow((x, 330), (x, 190), T('2:held you up', 0.12 * k), width=2.4, color='accent')
    p.pic('hug', gx + 800, 0, h=460, at='2:Every hug')
    p.pic('handshake', gx + 1400, 0, w=380, at='2:every handshake')
    p.pic('open_hand', gx + 1950, 0, h=280, at='2:every hand on')
    atom_model(p, gx + 2800, 0, '2:Not through contact', s=1.0)
    p.cam('2:The ground', x=gx, y=80, zoom=1.0)
    p.cam('2:Every hug', x=gx + 1100, y=0, zoom=0.86)
    p.cam('2:every hand on', x=gx + 1700, y=0, zoom=0.86)
    p.cam('2:Not through contact', x=gx + 2800, y=0, zoom=0.95)
    bx = gx + 4000
    m = mark(p)
    p.pic('brain', bx, -20, h=380, at='3:And what you made')
    for k, (txt, at, x, y) in enumerate((('COMFORT', '3:comfort', bx - 420, -220), ('LOVE', '3:the love', bx + 420, -220), ('STRENGTH', '3:the strength', bx, -340))):
        p.label(txt, x, y, at, size=30, color='accent')
    p.label('BUILT BY YOU', bx, 290, '3:built by you', size=36)
    p.cam('3:And what you made', x=bx, y=-40, zoom=0.95)
    close(p, m, '4:So the next time+0.6')
    hx = bx + 1400
    p.pic('holding_hands', hx, -40, w=560, at='4:So the next time')
    for k in range(4):
        x = hx - 210 + 140 * k
        cloud(p, x, 230, 46, T('4:Two worlds', 0.1 * k), count=7, size=8)
    p.glows([(hx - 40, -60), (hx + 60, -40)], "4:someone's hand", size=80, stagger=0.3)
    p.label('WHAT IS REALLY HAPPENING', hx, -330, '4:really happening', '5:And yet', size=32)
    p.label('ALMOST ENTIRELY EMPTY', hx, 320, '4:almost entirely', size=26)
    p.label('HOLDING EACH OTHER UP', hx, 380, '4:holding each other', size=32, color='accent')
    p.cam('4:So the next time', x=hx, y=40, zoom=0.95)
    p.label('YOU HAVE BEEN TOUCHED', hx, -330, '5:And yet+0.5', size=40)
    p.label('BY EVERYTHING', hx, -260, '5:touched by everything', size=40, color='accent')
    p.cam("5:You've never", x=hx, y=0, zoom=0.88)
    p.cam('5:touched by everything@end', x=hx, y=0, zoom=0.8)
    p.end_all('end-0.2')


BUILDERS = [part0, part1, part2, part3, part4, part5, part6, part7, part8]


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
            p.camera[0]['zoom'] = oz
            for c in p.camera:
                if c['at'] == 'start':
                    c['zoom'] = oz
        p.shift(ox - p.camera[0]['x'], oy - p.camera[0]['y'])
        end_cam = p.camera[-1]
        if end_cam['at'] != 'end':
            p.camera.append({'at': 'end', 'x': end_cam['x'], 'y': end_cam['y'], 'zoom': end_cam['zoom']})
        ox, oy, oz = p.camera[-1]['x'], p.camera[-1]['y'], p.camera[-1]['zoom']
        p.camera = settle_camera(p.camera, words)
        title = "You've Never Actually Touched Anything" + ('' if n == 0 else f' — part {n}')
        s = p.settings(THEME, title)
        s['clock'] = round(clock, 4)
        clock += part_seconds(n)
        json.dump(s, open(f'{d}/settings.json', 'w'), indent=1)
        print(f'p{n}: {len(p.items)} pictures, {len(p.drawings)} drawings, {len(p.lights)} lights, {len(p.streams)} streams, {len(p.labels)} labels, {len(p.camera)} camera keys')


if __name__ == '__main__':
    main()
    for a in sorted(AMBIGUOUS):
        print('ambiguous:', a)
