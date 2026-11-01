"""Builds public/videos/made-of-stars/p0..p8/settings.json from the shot list in script.md.

Each part is written around its own origin; the builder then shifts it so it starts
exactly where the previous part's camera ended (seamless joins).
Run: python tools/build_made_of_stars.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from stars_lib import AMBIGUOUS, T, Part, Pictures  # noqa: E402

ROOT = 'public/videos/made-of-stars'
PICS = Pictures(f'{ROOT}/images', '/videos/made-of-stars/images')
THEME = {
    'background': '#ffffff',
    'dotColor': 'rgba(36, 38, 43, 0.11)',
    'dotSpacing': 40,
    'dotSize': 1.7,
    'dotParallax': 0.75,
    'ink': '#24262b',
    'accent': '#5b8fd8',
    'lightBlend': 'normal',
    'font': 'Montserrat',
}
TITLES = {
    1: 'WHAT ARE YOU MADE OF?',
    2: 'WHERE DID THE FIRST ATOMS COME FROM?',
    3: 'WHAT DO STARS DO?',
    4: 'WHERE DOES CARBON COME FROM?',
    5: 'WHERE DOES IRON COME FROM?',
    6: 'WHERE DOES GOLD COME FROM?',
    7: 'HOW DID IT END UP IN YOU?',
}
CHEST = (0.49, 0.40)
FACE = (0.495, 0.29)


def chapter(p, n, first):
    """Chapter title on the empty page while the voice is silent."""
    out = f'1:{first}-0.55'
    p.label(f'CHAPTER {n}', 960, 470, 0.25, out, size=28, space='screen', color='accent', spacing=0.5)
    p.label(TITLES[n], 960, 548, 0.45, out, size=min(58, round(1500 / (len(TITLES[n]) * 0.98))), space='screen')


def ring_points(cx, cy, r, n, start=-90):
    return [(cx + r * math.cos(math.radians(start + 360 * i / n)), cy + r * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


# ======================================================================================
def part0(p):
    me = p.pic('person', -500, 0, h=720, at='1:Almost', id='me')
    earth = p.pic('earth', 60, -40, h=330, at='1:older', out='2:So-0.4')
    p.label('OLDER THAN THE EARTH', -220, 430, '1:older than', '1:hydrogen-0.3', size=40)
    p.cam('start', x=-220, y=20, zoom=0.95)
    p.cam('1:Earth@end', x=-220, y=20, zoom=1.0)
    glass = p.pic('water_glass', 650, 130, h=300, at='1:hydrogen', out='2:So-0.4')
    p.tile('H', 'HYDROGEN', 650, -230, '1:hydrogen+0.3', '2:So-0.4')
    p.pic('hourglass', 1080, -120, h=420, at='1:first few', out='2:So-0.4')
    p.label('FIRST FEW MINUTES', 870, 400, '1:few minutes', '2:So-0.4', size=36)
    p.hold_cam('1:hydrogen-0.1')
    p.cam('1:universe@end', x=820, y=40, zoom=0.92)
    blood = p.pic('blood_cell', 1500, 170, h=170, at='1:iron', out='2:So-0.4')
    p.tile('Fe', 'IRON', 1500, -150, '1:iron+0.3', '2:So-0.4')
    p.pic('supernova', 2100, -120, h=480, at='1:stars that', out='2:So-0.4')
    ln = p.line([(1930, -60), (1760, 40), (1590, 140)], '1:blew', out='2:So-0.4', dashed=True, color='muted', curve=True)
    p.travel(ln, '1:blew up', dur=1.3, size=60)
    p.hold_cam('1:iron-0.2')
    p.cam('1:far away@end', x=1700, y=40, zoom=0.9)
    # Part 2 of the opening: back to the person, five tiles around them
    p.items[[i['id'] for i in p.items].index(me)]['out'] = '1:hydrogen'
    me = p.pic('person', 2900, 0, h=720, at='2:So', id='me_b')
    p.hold_cam('2:So-0.3')
    p.cam('2:come from@end', x=2900, y=30, zoom=0.92)
    chest = p.pt(me, CHEST)
    spots = [('H', 'HYDROGEN', (2440, -260)), ('C', 'CARBON', (2390, 0)), ('O', 'OXYGEN', (2440, 260)), ('Fe', 'IRON', (3360, -200)), ('Au', 'GOLD', (3360, 200))]
    for i, (sym, name, (x, y)) in enumerate(spots):
        dx, dy = x - chest[0], y - chest[1]
        L = math.hypot(dx, dy)
        end = (x - dx / L * 70, y - dy / L * 70)
        start = (chest[0] + dx / L * 40, chest[1] + dy / L * 40)
        ln = p.line([start, end], T('2:rest', 0.12 * i), color='muted', width=1.8, duration=0.7)
        p.tile(sym, name, x, y, T('2:By the end', 0.35 * i), s=105)
        p.travel(ln, T('2:not separate', 0.22 * i), dur=1.0, size=46, reverse=True)
    p.glow(me, CHEST, '2:made of stars', size=90)
    p.label('YOU ARE MADE OF STARS', 2900, 470, '2:made of stars', 'end-0.8', size=46)
    p.cam('2:stars@end', x=2900, y=40, zoom=0.95)
    p.end_all()


def part1(p):
    chapter(p, 1, "Let's")
    p.cam('start', x=0, y=0, zoom=0.95)
    me = p.pic('person', 0, 0, h=720, at="1:Let's", id='me')
    p.hold_cam("1:Let's-0.3")
    p.cam('1:you@end', x=150, y=0, zoom=1.0)
    # Atoms: a magnifying circle from the hand, with an atom drawn inside
    p.mag(me, (0.405, 0.53), 22, 470, -60, 230, '1:built', '1:many-0.35')
    nuc = p.circle(470, -60, 22, '1:tiny', width=2.4, fill='accent', fillOpacity=0.6, out='1:many-0.35')
    for k, rot in enumerate((0, 60, 120)):
        orb = p.ellipse(470, -60, 168, 58, T('1:tiny+0.2', 0.25 * k), rot=rot, width=1.8, out='1:many-0.35')
        if k == 0:
            p.travel(orb, '1:called atoms', dur=1.6, size=40)
    p.label('ATOMS', 470, 215, '1:called atoms', '1:many-0.35', size=34)
    # Elements: the first three rows of the periodic table (main groups)
    rows = [['H', '', '', '', '', '', '', 'He'], ['Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne'], ['Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar']]
    gx0, gy0, pitch, s = 1450, -100, 96, 86
    life = {'H', 'C', 'N', 'O', 'P', 'S'}
    k = 0
    for r, row in enumerate(rows):
        for c, sym in enumerate(row):
            if not sym:
                continue
            x, y = gx0 + c * pitch, gy0 + r * pitch
            fill = 'accent' if sym in life else None
            p.rect(x, y, s, s, T('1:many kinds', 0.035 * k), width=2.0, duration=0.5, fill=fill or 'paper', fillOpacity=0.3 if fill else 1,
                   fillAt=T('1:few', 0.12 * sorted(life).index(sym)) if fill else T('1:many kinds', 0.035 * k + 0.1), id=f'g_{sym}', out='2:oxygen')
            p.label(sym, x, y, T('1:many kinds', 0.035 * k + 0.2), '2:oxygen', size=34, spacing=0.02, upper=False)
            k += 1
    p.label('ELEMENTS', gx0 + 3.5 * pitch, gy0 + 3 * pitch + 10, '1:elements', '2:oxygen', size=34)
    p.hold_cam('1:many-0.2')
    p.cam('1:elements@end', x=gx0 + 3.5 * pitch, y=gy0 + pitch, zoom=1.1)
    p.cam('1:work@end', x=gx0 + 3.5 * pitch, y=gy0 + pitch, zoom=1.15)
    # Ranked list by weight
    lx, ly = 2750, -260
    names = [('O', 'OXYGEN', '2:oxygen'), ('C', 'CARBON', '2:carbon'), ('H', 'HYDROGEN', '2:Then hydrogen'), ('N', 'NITROGEN', '2:nitrogen'), ('P', 'PHOSPHORUS', '2:phosphorus'), ('S', 'SULFUR', '2:sulfur')]
    p.label('BY WEIGHT', lx + 150, ly - 120, '2:By weight', '3:Each-0.2', size=36, color='accent')
    for i, (sym, name, at) in enumerate(names):
        y = ly + i * 104
        p.tile(sym, None, lx, y, at, '3:Each-0.2', s=86)
        p.label(f'{i + 1} · {name}', lx + 70, y, T(at, 0.2), '3:Each-0.2', size=34, align='left')
    p.line([(lx + 640, ly - 40), (lx + 680, ly - 40), (lx + 680, ly + 5 * 104 + 40), (lx + 640, ly + 5 * 104 + 40)], '2:these six', '3:Each-0.2', width=2.2, duration=0.8)
    p.label('MORE THAN', lx + 940, -70, '2:more than', '3:Each-0.2', size=30)
    p.label('{n}%', lx + 940, 30, '2:97', '3:Each-0.2', size=110, spacing=0.04, count={'to': 97, 'duration': 1.3})
    p.label('OF YOUR BODY', lx + 940, 130, '2:your body', '3:Each-0.2', size=30)
    p.hold_cam('2:By-0.3')
    p.cam('2:By weight@end', x=lx + 280, y=-20, zoom=1.0)
    p.cam('2:sulfur', x=lx + 300, y=0, zoom=1.0)
    p.cam('2:body@end', x=lx + 470, y=0, zoom=0.9)
    # Jobs around a person
    jx = 4700
    me2 = p.pic('person', jx, 30, h=640, at='3:Each', id='me2')
    p.pic('water_glass', jx - 480, -200, h=200, at='3:Hydrogen and', out='4:None of these+0.2')
    o = p.circle(jx - 480, 100, 36, '3:join', width=2.2, fill='paper', out='4:None of these+0.2')
    for sx in (-1, 1):
        p.line([(jx - 480 + sx * 26, 126), (jx - 480 + sx * 44, 146)], '3:join+0.2', width=2.2, out='4:None of these+0.2')
        p.circle(jx - 480 + sx * 58, 158, 20, '3:join+0.3', width=2.2, fill='paper', out='4:None of these+0.2')
    p.label('O', jx - 480, 100, '3:join+0.4', '4:None of these+0.2', size=26, upper=False)
    p.label('H', jx - 538, 158, '3:join+0.5', '4:None of these+0.2', size=18, upper=False)
    p.label('H', jx - 422, 158, '3:join+0.5', '4:None of these+0.2', size=18, upper=False)
    p.label('WATER', jx - 480, 230, '3:water', '4:None of these+0.2', size=28)
    chain = [(jx - 160 + 80 * i, -420 + (20 if i % 2 else -20)) for i in range(5)]
    for i, (x, y) in enumerate(chain):
        p.circle(x, y, 17, T('3:Carbon is', 0.12 * i), width=2.0, fill='paper', out='4:None of these+0.2')
        p.label('C', x, y, T('3:Carbon is', 0.12 * i + 0.15), '4:None of these+0.2', size=16, upper=False)
    cl = p.line(chain, '3:backbone', width=1.6, duration=0.8, out='4:None of these+0.2', color='muted')
    p.travel(cl, '3:molecules', dur=1.2, size=40)
    dna = p.pic('dna', jx + 480, -150, h=320, at='3:Nitrogen', out='4:None of these+0.2')
    p.tile('N', None, jx + 660, -250, '3:Nitrogen+0.3', '4:None of these+0.2', s=70)
    p.tile('P', None, jx + 660, -110, '3:phosphorus', '4:None of these+0.2', s=70)
    p.travel_on(dna, PICS.outline('dna', 0.0, 0.5, 40), '3:DNA', dur=1.4, size=40)
    bone = p.pic('bone', jx + 480, 250, w=230, at='3:Calcium', out='4:None of these+0.2')
    p.tile('Ca', None, jx + 680, 250, '3:Calcium+0.3', '4:None of these+0.2', s=70)
    p.travel_on(bone, PICS.outline('bone', 0.0, 1.0, 60), '3:bones', dur=1.4, size=40)
    p.pic('blood_cell', jx - 480, 390, h=80, at='3:iron', out='4:None of these+0.2')
    p.tile('Fe', None, jx - 640, 390, '3:iron+0.3', '4:None of these+0.2', s=66)
    chest2 = p.pt(me2, CHEST)
    loop = p.ellipse(chest2[0], chest2[1] + 120, 110, 220, '3:blood', width=1.4, color='muted', out='4:None of these+0.2', dashed=True)
    p.travel(loop, '3:carries oxygen', dur=2.2, size=46)
    p.hold_cam('3:Each-0.3')
    p.cam('3:Each@end', x=jx, y=0, zoom=0.86)
    p.cam('3:inside you@end', x=jx - 160, y=0, zoom=0.94)
    p.cam('3:cells@end', x=jx - 20, y=-60, zoom=0.95)
    p.cam('3:DNA@end', x=jx + 160, y=-40, zoom=0.95)
    p.cam('3:hard@end', x=jx + 160, y=50, zoom=0.95)
    p.cam('3:iron in', x=jx - 120, y=60, zoom=0.94)
    p.cam('3:body@end', x=jx, y=20, zoom=0.86)
    # None made inside you; food, water, air; not made on Earth
    p.label('NOT MADE INSIDE YOU', jx, 470, '4:None of these', '4:food-0.2', size=36)
    p.pic('apple', jx + 620, -230, h=170, at='4:food', out='4:So where-0.2')
    p.pic('water_glass', jx + 620, 30, h=180, at='4:your water', out='4:So where-0.2')
    for i in range(3):
        y = 250 + i * 34
        p.line([(jx + 520 + 30 * k, y + (10 if k % 2 else -10)) for k in range(8)], T('4:air', 0.1 * i), width=1.8, curve=True, out='4:So where-0.2')
    for at, y in (('4:food', -230), ('4:your water', 30), ('4:air', 280)):
        p.arrow((jx + 520, y), (jx + 170, y * 0.4), T(at, 0.2), width=1.8, color='muted', out='4:So where-0.2')
    p.cam('4:None of these@end', x=jx + 100, y=20, zoom=0.82)
    earth = p.pic('earth', jx + 1500, 0, h=480, at='4:Earth', out='4:So where-0.2')
    p.label('NOT MADE ON EARTH', jx + 1500, 340, '4:made on Earth', '4:So where-0.2', size=36)
    p.hold_cam('4:almost-0.2')
    p.cam('4:either@end', x=jx + 1500, y=30, zoom=1.0)
    stars = [(jx + 1500 + dx, -720 + dy) for dx, dy in [(-420, -60), (-250, 120), (-60, -150), (140, 60), (330, -90), (460, 140), (-560, 160), (20, 190)]]
    p.glows(stars, '4:So where', size=40, stagger=0.12)
    p.cam('4:they made@end', x=jx + 1500, y=-700, zoom=1.0)
    p.end_all()


def part2(p):
    chapter(p, 2, 'To find')
    p.cam('start', x=0, y=0, zoom=1.0)
    hg = p.pic('hourglass', 0, 0, h=560, at='1:To find')
    p.travel_on(hg, [[0.5, 0.33], [0.5, 0.45], [0.5, 0.52], [0.5, 0.6], [0.5, 0.74]], '1:beginning', dur=1.6, size=40)
    p.hold_cam('1:To find-0.3')
    p.cam('1:beginning@end', x=0, y=0, zoom=1.1)
    # Timeline and the Big Bang
    bx = 900
    tl = p.arrow((bx, 0), (bx + 2300, 0), '1:About', width=2.4, duration=2.2)
    p.glows([(bx, 0)], '1:Big Bang', size=160)
    p.label('BIG BANG', bx, 110, '1:Big Bang', '2:In the-0.2', size=34)
    p.label('{n} BILLION YEARS AGO', bx + 430, -170, '1:13.8', '1:far too-0.2', size=38, count={'to': 13.8, 'decimals': 1, 'duration': 1.4})
    p.hold_cam('1:About-0.3')
    p.cam('1:Big Bang@end', x=bx + 400, y=0, zoom=1.0)
    hot = [(bx + 110 * math.cos(a) * r, 110 * math.sin(a) * r) for a, r in zip([i * 2.4 for i in range(14)], [0.3, 0.9, 0.6, 1.0, 0.4, 0.8, 0.7, 1.0, 0.5, 0.95, 0.6, 0.85, 0.35, 0.75])]
    p.glows(hot, '1:far too', '1:spread-0.1', size=34, stagger=0.05)
    p.label('TOO HOT FOR ATOMS', bx, -200, '1:too hot', '1:spread', size=36)
    p.cam('1:exist@end', x=bx + 80, y=0, zoom=1.25)
    for i, r in enumerate((130, 230, 330)):
        p.circle(bx, 0, r, T('1:spread out', 0.3 * i), width=1.6, color='muted', duration=0.9, out='2:In the')
    p.cam('1:cooled@end', x=bx + 250, y=0, zoom=0.92)
    # The first three elements
    p.tile('H', 'HYDROGEN', bx + 280, 250, '2:hydrogen', '3:Now-0.2', s=120)
    p.tile('He', 'HELIUM', bx + 430, 250, '2:helium', '3:Now-0.2', s=120)
    p.tile('Li', 'LITHIUM', bx + 560, 262, '2:lithium', '3:Now-0.2', s=84)
    p.label('THE FIRST FEW MINUTES', bx + 420, 100, '2:first few', '3:Now-0.2', size=34)
    p.line([(bx + 200, 345), (bx + 620, 345)], '2:That was', '3:Now-0.2', width=2.0)
    for i, (sym, at) in enumerate((('C', '2:No carbon'), ('O', '2:No oxygen'), ('Fe', '2:No iron'))):
        x = bx + 820 + i * 150
        p.tile(sym, None, x, 250, at, '3:Now-0.2', s=110, dashed=True)
        p.line([(x - 50, 300), (x + 50, 200)], T(at, 0.3), '3:Now-0.2', width=2.4, duration=0.4)
    p.hold_cam('2:In the-0.3')
    p.cam('2:lithium@end', x=bx + 450, y=140, zoom=1.05)
    p.cam('2:No iron@end', x=bx + 650, y=150, zoom=1.0)
    sun_x = bx + 2050
    p.pic('sun', sun_x, -200, h=220, at='2:wait', out='3:Now-0.2')
    p.glows([(sun_x, -200)], '2:stars', '3:Now-0.2', size=120)
    p.label('STARS', sun_x, -40, '2:stars', '3:Now-0.2', size=34)
    p.cam('2:stars@end', x=sun_x - 300, y=0, zoom=0.95)
    # The strange part: a glass of water
    gx = sun_x + 1300
    glass = p.pic('water_glass', gx, 30, h=430, at='3:strange')
    p.cam('3:strange@end', x=gx - 150, y=0, zoom=1.0)
    p.cam('3:of water@end', x=gx, y=0, zoom=1.05)
    mx, my = gx + 560, -60
    p.mag(glass, (0.5, 0.6), 30, mx, my, 210, '3:Every water', '3:So the-0.3')
    p.circle(mx, my - 10, 50, '3:molecule', width=2.4, fill='paper', out='3:So the-0.3')
    for sx in (-1, 1):
        p.line([(mx + sx * 36, my + 26), (mx + sx * 62, my + 56)], '3:molecule+0.2', width=2.4, out='3:So the-0.3')
        p.circle(mx + sx * 82, my + 78, 28, '3:two hydrogen', width=2.4, fill='accent', fillOpacity=0.35, out='3:So the-0.3')
        p.label('H', mx + sx * 82, my + 78, T('3:two hydrogen', 0.2), '3:So the-0.3', size=24, upper=False)
    p.label('O', mx, my - 10, '3:molecule+0.3', '3:So the-0.3', size=32, upper=False)
    p.cam('3:atoms@end', x=gx + 280, y=0, zoom=1.0)
    bb = (gx - 300, -420)
    back = p.line([(mx - 82, my + 78), (gx + 150, -300), bb], '3:And the hydrogen', width=1.8, color='muted', curve=True, dashed=True, out='3:So the')
    p.travel(back, '3:comes from', dur=1.6, size=56)
    p.glows([bb], '3:first few minutes', '3:So the', size=130)
    p.label('FIRST FEW MINUTES', bb[0], bb[1] - 90, '3:first few minutes', '3:So the', size=30)
    p.tile('H', None, bb[0] - 220, bb[1], '3:no other', '3:So the', s=100, fill='accent')
    p.label('NO OTHER REAL SOURCE', bb[0] - 220, bb[1] + 95, '3:no other real', '3:So the', size=28)
    p.cam('3:few minutes@end', x=gx, y=-150, zoom=0.9)
    me = p.pic('person', gx + 650, 20, h=600, at='3:hydrogen in you')
    to_me = p.line([(gx + 90, -40), (gx + 330, -120), p.pt(me, CHEST)], '3:as old', '4:So who-0.2', width=1.6, color='muted', curve=True)
    p.travel(to_me, '3:as old', dur=1.3, size=50)
    p.label('ABOUT 13.8 BILLION YEARS OLD', gx + 330, 430, '3:old as', '4:But-0.2', size=36)
    p.cam('3:itself@end', x=gx + 330, y=20, zoom=0.92)
    # Not enough to build a person
    p.tile('H', None, gx + 1100, -180, '4:hydrogen and', '4:So who-0.2', s=100)
    p.tile('He', None, gx + 1230, -180, '4:helium', '4:So who-0.2', s=100)
    p.label('NOT ENOUGH', gx + 1165, -50, '4:build', '4:So who-0.2', size=32)
    p.pic('bone', gx + 1165, 140, w=230, at='4:bones', out='4:So who-0.2')
    p.line([(gx + 1050, 200), (gx + 1280, 80)], '4:bones+0.3', '4:So who-0.2', width=2.6, duration=0.4)
    p.pic('blood_cell', gx + 1165, 330, h=90, at='4:blood', out='4:So who-0.2')
    p.line([(gx + 1080, 380), (gx + 1250, 280)], '4:blood+0.3', '4:So who-0.2', width=2.6, duration=0.4)
    p.cam('4:helium@end', x=gx + 900, y=40, zoom=0.92)
    p.cam('4:them@end', x=gx + 1000, y=80, zoom=0.95)
    sx_, sy_ = gx + 1000, -900
    p.pic('sun', sx_, sy_, h=460, at='4:sky')
    p.glows([(sx_, sy_)], '4:every day', size=200)
    p.hold_cam('4:So who-0.2')
    p.cam('4:day@end', x=sx_, y=sy_, zoom=1.0)
    p.end_all()


def part3(p):
    chapter(p, 3, 'Look')
    p.cam('start', x=0, y=0, zoom=1.0)
    sun = p.pic('sun', 0, 0, h=520, at='1:Look')
    p.hold_cam('1:Look-0.2')
    p.cam('1:Sun@end', x=0, y=0, zoom=1.08)
    p.travel_on(sun, PICS.outline('sun', 0, 1, 80, shrink=0.02), '1:huge ball', dur=2.4, size=60)
    p.label('MOSTLY HYDROGEN', 0, 370, '1:mostly of hydrogen', '2:Hydrogen', size=36)
    for i, (x, y) in enumerate(ring_points(0, 0, 410, 8)):
        x2, y2 = x * 0.66, y * 0.66
        p.arrow((x, y), (x2, y2), T('1:squeezes', 0.15 * i), '2:Hydrogen', width=2.0, duration=0.5)
    p.pic('fist', -760, 0, h=330, at='1:own weight', out='2:Hydrogen')
    p.label('GRAVITY', -760, 230, '1:weight', '2:Hydrogen', size=32)
    p.glows([(0, 0)], '1:hot enough', size=180)
    p.cam('1:center@end', x=-250, y=0, zoom=0.92)
    p.cam('1:happen@end', x=-150, y=0, zoom=0.95)
    # Fusion inside the core
    cx, cy = 820, -20
    p.mag(sun, (0.5, 0.5), 30, cx, cy, 235, '2:Hydrogen', '3:The numbers-0.3')
    for sx in (-1, 1):
        p.circle(cx + sx * 140, cy, 40, '2:Hydrogen+0.6', width=2.4, fill='accent', fillOpacity=0.3, out='2:helium')
        p.label('H', cx + sx * 140, cy, '2:Hydrogen+0.7', '2:helium', size=30, upper=False)
        ln = p.line([(cx + sx * 98, cy), (cx + sx * 64, cy)], '2:crash', width=1.4, color='muted', duration=0.6, out='2:helium')
        p.travel(ln, '2:crash+0.3', dur=0.8, size=40)
    p.circle(cx, cy, 60, '2:helium', width=2.6, fill='accent', fillOpacity=0.35, out='3:The numbers-0.3')
    p.label('He', cx, cy, '2:helium+0.2', '3:The numbers-0.3', size=40, upper=False)
    p.label('FUSION', cx, cy + 300, '2:fusion', '3:The numbers-0.3', size=46)
    for i, (x, y) in enumerate(ring_points(cx, cy, 160, 6, start=-60)):
        ray = p.line([((x - cx) * 0.38 + cx, (y - cy) * 0.38 + cy), (x, y)], T('2:energy', -0.6 + 0.07 * i), width=1.6, color='accent', duration=0.4, out='3:The numbers-0.3')
        p.travel(ray, T('2:energy', 0.05 * i), dur=0.8, size=34)
    p.hold_cam('2:Hydrogen-0.2')
    p.cam('2:together@end', x=430, y=0, zoom=0.88)
    p.cam('2:energy@end', x=480, y=0, zoom=0.9)
    # The numbers
    nx = 1150
    p.label('{n} TONS', nx, -140, '3:600', '3:Just-0.2', size=44, count={'to': 600000000, 'duration': 1.6})
    p.label('EVERY SECOND', nx, -250, '3:Every second', '3:Just-0.2', size=34, color='accent')
    p.label('OF HYDROGEN BECOMES HELIUM', nx, -60, '3:into helium', '3:Just-0.2', size=26)
    p.label('{n} TONS', nx, 110, '3:4 million', '3:Just-0.2', size=44, count={'to': 4000000, 'duration': 1.4})
    p.label('BECOMES ENERGY', nx, 190, '3:becomes energy', '3:Just-0.2', size=26)
    p.hold_cam('3:The numbers-0.3')
    p.cam('3:huge@end', x=640, y=0, zoom=0.84)
    p.cam('3:becomes energy@end', x=660, y=0, zoom=0.86)
    house = p.pic('house', 1750, 40, h=300, at='3:American home', out='4:In a way-0.2')
    p.label('1 KG OF HYDROGEN', 1000, -200, '3:one kilogram', '4:In a way-0.2', size=34)
    to_house = p.line([(300, -60), (1000, -120), p.pt(house, (0.592, 0.548))], '3:electricity', width=1.6, color='muted', curve=True, dashed=True, out='4:In a way-0.2')
    p.travel(to_house, '3:power', dur=1.4, size=50)
    p.glow(house, (0.592, 0.548), T('3:power', 1.3), '4:In a way-0.2', size=80)
    p.label('{n} YEARS', 1750, 300, '3:17,000', '4:In a way-0.2', size=54, count={'to': 17000, 'duration': 1.4})
    p.cam('3:years@end', x=780, y=40, zoom=0.75)
    me = p.pic('person', 2350, 0, h=600, at='3:sunlight', out='4:In a way-0.2')
    face = p.line([(320, -120), (1500, -420), p.pt(me, FACE)], '3:sunlight', width=1.4, color='muted', curve=True, dashed=True, out='4:In a way-0.2')
    p.travel(face, '3:reaches', dur=1.8, size=56)
    p.cam('3:face@end', x=1120, y=0, zoom=0.58)
    # 4.5 billion years; every star a furnace
    p.label('{n} BILLION YEARS', 1300, -380, '4:4.5', '4:In a way-0.2', size=50, count={'to': 4.5, 'decimals': 1, 'duration': 1.2})
    p.pic('hourglass', 2100, -260, h=300, at='4:doing this', out='4:In a way-0.2', depth=1.8)
    stars = [(1300 + dx, dy) for dx, dy in [(-700, -300), (-420, 260), (-150, -380), (130, 300), (380, -260), (620, 220), (860, -120), (-900, 120), (1050, 280), (-560, -60), (300, 20), (980, -360)]]
    p.glows(stars, '4:every star', '4:light atoms', size=46, stagger=0.06)
    p.label('EVERY STAR IS A FURNACE', 1300, 430, '4:every star', '4:light atoms', size=38)
    p.cam('4:furnace@end', x=1300, y=0, zoom=0.68)
    sizes = ((960, 30), (1240, 48), (1560, 70))
    for i, (x, r) in enumerate(sizes):
        p.circle(x, 0, r, T('4:light atoms', 0.35 * i), width=2.4, fill='accent', fillOpacity=0.3, out='4:But a-0.2')
        if i:
            px, pr = sizes[i - 1]
            p.arrow((px + pr + 18, 0), (x - r - 18, 0), T('4:presses', 0.3 * i), width=2.0, out='4:But a-0.2')
    p.cam('4:ones@end', x=1260, y=0, zoom=1.0)
    p.cam('4:But a star', x=700, y=0, zoom=0.9)
    p.tile('He', 'HELIUM', 420, -320, '4:like the Sun', s=110)
    p.pic('bone', 750, -80, w=230, at='4:bones')
    p.line([(560, -300), (690, -110)], T('4:bones', 0.3), width=2.6, duration=0.4, color='muted')
    p.line([(640, -190), (580, -230)], T('4:bones', 0.5), width=2.6, duration=0.3)
    p.tile('C', 'CARBON', 750, 180, '4:carbon', s=110, dashed=True)
    p.glows([(750, 168)], T('4:carbon', 0.3), size=80)
    p.cam('4:makes helium@end', x=300, y=0, zoom=0.95)
    p.cam('4:from@end', x=420, y=0, zoom=1.0)
    p.end_all()


def part4(p):
    chapter(p, 4, 'Carbon')
    p.cam('start', x=0, y=0, zoom=1.0)
    rg = p.pic('red_giant', 0, 0, h=560, at='1:Carbon')
    p.tile('C', 'CARBON', 470, -220, '1:Carbon+0.4', '1:When-0.2', s=100)
    p.hold_cam('1:Carbon-0.2')
    p.cam('1:old@end', x=120, y=0, zoom=1.0)
    # Sun core shrinks
    sx = -1400
    sun = p.pic('sun', sx, 0, h=420, at='1:When a', id='sun4')
    for i, r in enumerate((150, 110, 75)):
        p.circle(sx, 0, r, T('1:core shrinks', 0.3 * i), width=1.6, color='accent', duration=0.6, out='1:outer-0.2')
    p.glows([(sx, 0)], '1:heats up', size=130)
    p.label('SUN TODAY', sx, 300, '1:outer', size=32)
    p.label('RED GIANT', 0, 360, '1:red giant', size=32)
    for i, r in enumerate((320, 380)):
        p.circle(0, 0, r, T('1:spread out', 0.3 * i), width=1.4, color='muted', duration=0.8, out='2:Deep-0.2')
    p.hold_cam('1:When-0.3')
    p.cam('1:center@end', x=sx, y=0, zoom=1.0)
    p.cam('1:heats up@end', x=sx, y=0, zoom=1.05)
    p.cam('1:giant@end', x=sx / 2, y=20, zoom=0.62)
    # Deep inside: 100 million degrees, triple alpha
    p.glows([(0, 0)], '2:Deep', size=200)
    p.cam('2:hotter@end', x=0, y=0, zoom=1.0)
    p.label('{n} MILLION DEGREES', 0, -380, '2:100', '3:Why-0.2', size=50, count={'to': 100, 'duration': 1.2})
    cx, cy = 820, 0
    p.mag(rg, (0.5, 0.5), 30, cx, cy, 240, '2:Three', '3:Why-0.3')
    for i, (x, y) in enumerate(ring_points(cx, cy, 130, 3)):
        p.circle(x, y, 28, T('2:Three', 0.6 + 0.12 * i), width=2.2, fill='accent', fillOpacity=0.3, out='2:carbon atom')
        p.label('He', x, y, T('2:Three', 0.7 + 0.12 * i), '2:carbon atom', size=20, upper=False)
        ln = p.line([(x + (cx - x) * 0.25, y + (cy - y) * 0.25), (x + (cx - x) * 0.75, y + (cy - y) * 0.75)], '2:slam', width=1.4, color='muted', duration=0.5, out='2:carbon atom')
        p.travel(ln, '2:slam+0.2', dur=0.7, size=40)
    p.circle(cx, cy, 48, '2:one carbon', width=2.6, fill='accent', fillOpacity=0.4, out='3:Why-0.3')
    p.label('C', cx, cy, '2:one carbon+0.2', '3:Why-0.3', size=36, upper=False)
    p.cam('2:degrees@end', x=200, y=-60, zoom=0.92)
    p.cam('2:atom@end', x=430, y=0, zoom=0.9)
    # Why three and not two
    wx = 2000
    for side, (n, tag, at) in enumerate(((2, 'TWO', '3:not two'), (3, 'THREE', '3:Why three'))):
        x0 = wx + (0 if n == 2 else 640)
        for i in range(n):
            px, py = (x0 - 70 + 140 * i, 0) if n == 2 else ring_points(x0, 0, 85, 3)[i]
            p.circle(px, py, 26, T(at, 0.1 * i), width=2.2, fill='accent', fillOpacity=0.25, out='4:In the-0.2')
        p.label(tag, x0, -190, at, '4:In the-0.2', size=36)
    two_a = p.line([(wx - 70, 0), (wx - 10, 0)], '3:join', width=1.2, color='muted', duration=0.3, out='3:falls apart+0.8')
    two_b = p.line([(wx + 70, 0), (wx + 10, 0)], '3:join', width=1.2, color='muted', duration=0.3, out='3:falls apart+0.8')
    p.travel(two_a, '3:join', dur=0.6, size=36)
    p.travel(two_b, '3:join', dur=0.6, size=36)
    p.travel(two_a, '3:falls apart', dur=0.6, size=36, reverse=True)
    p.travel(two_b, '3:falls apart', dur=0.6, size=36, reverse=True)
    p.label('FALLS APART', wx, 170, '3:falls apart', '4:In the-0.2', size=30)
    p.glows([(wx + 640, 0)], '3:same time', '4:In the-0.2', size=110)
    p.label('LASTS', wx + 640, 170, '3:lasts', '4:In the-0.2', size=30)
    p.circle(wx + 1240, 0, 46, '3:carbon atom', width=2.6, fill='accent', fillOpacity=0.3, out='4:In the-0.2')
    p.label('C', wx + 1240, 0, '3:carbon atom+0.2', '4:In the-0.2', size=32, upper=False)
    he = p.circle(wx + 1240 - 190, -110, 26, '3:one more helium', width=2.2, out='3:makes oxygen')
    feed = p.line([(wx + 1240 - 165, -95), (wx + 1240 - 50, -25)], '3:grab', width=1.4, color='muted', duration=0.5, out='3:makes oxygen')
    p.travel(feed, '3:grab+0.3', dur=0.8, size=40)
    p.tile('O', 'OXYGEN', wx + 1240, 210, '3:oxygen', '4:In the-0.2', s=110)
    p.hold_cam('3:Why-0.3')
    p.cam('3:not two@end', x=wx + 320, y=0, zoom=1.0)
    p.cam('3:lasts@end', x=wx + 400, y=0, zoom=0.95)
    p.cam('3:oxygen@end', x=wx + 900, y=50, zoom=1.0)
    # Planetary nebula: outer layers out, carbon drifts away
    nx = wx + 1950
    neb = p.pic('nebula', nx, 0, h=520, at='4:In the')
    for i, r in enumerate((200, 290, 380)):
        p.circle(nx, 0, r, T('4:pushes', 0.3 * i), width=1.4, color='muted', duration=0.9, out='4:Put simply-0.2')
    drift = []
    for i, ang in enumerate((-150, -60, 20, 100, 170)):
        a = math.radians(ang)
        pts = [(nx + 60 * math.cos(a), 60 * math.sin(a)), (nx + 260 * math.cos(a + 0.25), 260 * math.sin(a + 0.25)), (nx + 470 * math.cos(a + 0.4), 470 * math.sin(a + 0.4))]
        ln = p.line(pts, T('4:drifts', 0.1 * i), width=1.2, color='muted', curve=True, dashed=True, out='4:Put simply-0.2')
        p.travel(ln, T('4:drifts', 0.1 * i), dur=1.6, size=40)
        drift.append(pts[-1])
    for i, (x, y) in enumerate(drift[:3]):
        p.tile('C', None, x, y, T('4:between', 0.15 * i), '4:Put simply-0.2', s=64)
    p.cam('4:In the', x=nx - 300, y=0, zoom=0.85)
    p.cam('4:space@end', x=nx, y=0, zoom=0.9)
    p.cam('4:the stars@end', x=nx, y=0, zoom=0.82)
    me = p.pic('person', nx + 1150, 20, h=600, at='4:Put simply')
    p.label('MADE INSIDE A STAR', nx + 1150, 420, '4:inside a star', size=34)
    to_me = p.line([(nx + 260, -80), (nx + 700, -260), p.pt(me, CHEST)], '4:carbon in your', width=1.6, color='muted', curve=True, dashed=True)
    p.travel(to_me, '4:carbon in your', dur=1.6, size=56)
    p.glow(me, CHEST, '4:made inside', size=80)
    p.cam('4:simply@end', x=nx + 600, y=20, zoom=0.82)
    # The Sun stops here; where does iron come from
    p.pic('sun', nx + 1900, -170, h=240, at='5:But a star')
    p.label('STOPS HERE', nx + 1900, -10, '5:any further', size=32)
    p.pic('blood_cell', nx + 1900, 230, h=120, at='5:iron')
    p.tile('Fe', 'IRON', nx + 2130, 230, '5:iron+0.3', s=100, dashed=True)
    p.glows([(nx + 2130, 222)], '5:blood', size=70)
    p.hold_cam('5:But-0.3')
    p.cam('5:further@end', x=nx + 1700, y=20, zoom=0.92)
    p.cam('5:from@end', x=nx + 1950, y=40, zoom=1.0)
    p.end_all()


def part5(p):
    chapter(p, 5, 'For')
    p.cam('start', x=0, y=0, zoom=1.0)
    p.pic('sun', -500, 120, h=160, at='1:For iron', out='2:Carbon-0.2')
    big = p.circle(200, 0, 360, '1:much bigger', width=2.2, duration=1.0, id='bigstar')
    p.label('SUN', -500, 250, '1:For iron+0.3', '2:Carbon-0.2', size=28)
    p.label('MANY TIMES HEAVIER', 200, -430, '1:many times', '2:Carbon-0.2', size=34)
    p.travel(big, '1:burn hotter', dur=1.6, size=56)
    p.glows([(200, 0)], '1:centers', size=150)
    p.hold_cam('1:For-0.3')
    p.cam('1:star@end', x=-100, y=0, zoom=0.95)
    p.cam('1:going@end', x=150, y=0, zoom=1.0)
    # Layers
    layers = [(270, 'O · Ne · Mg', '2:oxygen'), (185, 'Si · S · Ca', '2:silicon'), (100, 'Fe', '2:finally')]
    for r, txt, at in layers:
        p.circle(200, 0, r, at, width=2.0, duration=0.8)
        p.label(txt, 200, -r + (40 if r > 100 else 0) if r > 100 else 0, T(at, 0.3), size=30 if r > 100 else 44, upper=False)
    p.label('H · He · C', 200, -315, '2:Carbon fuses', size=26, upper=False)
    inward = p.line([(200, -360), (200, -180), (200, 0)], '2:layers', width=1.2, color='muted', duration=0.6)
    p.travel(inward, '2:heaviest', dur=1.4, size=50)
    p.label('MONTHS', 760, -60, '2:months', '3:But-0.2', size=40)
    p.label('DAYS', 760, 40, '2:days', '3:But-0.2', size=40)
    p.cam('2:magnesium@end', x=200, y=0, zoom=1.05)
    p.cam('2:middle@end', x=330, y=0, zoom=1.0)
    p.label('DEAD END', 200, 150, '3:dead end', '3:Up to-0.2', size=34, color='accent')
    # Chain of fusion steps
    cy = 760
    chain = ['H', 'He', 'C', 'O', 'Si', 'Fe']
    for i, sym in enumerate(chain):
        x = -400 + 230 * i
        p.tile(sym, None, x, cy, T('3:Up to', 0.18 * i), '3:So when-0.2', s=90)
        if i:
            a = p.arrow((x - 170, cy), (x - 60, cy), T('3:Up to', 0.18 * i - 0.08), '3:So when-0.2', width=2.0, duration=0.4)
            p.travel(a, T('3:gives off', 0.12 * i), dur=0.6, size=36)
    p.arrow((900, cy), (990, cy), "3:doesn't", '3:So when-0.2', width=2.0, duration=0.4)
    p.line([(1010, cy - 50), (1010, cy + 50)], "3:doesn't+0.3", '3:So when-0.2', width=4.0, duration=0.3)
    p.label('GIVES OFF ENERGY', 175, cy + 110, '3:gives off', '3:So when-0.2', size=28)
    p.hold_cam('3:Up to-0.3')
    p.cam('3:energy@end', x=300, y=cy, zoom=1.0)
    p.cam("3:doesn't@end", x=420, y=cy, zoom=1.0)
    p.glows([(200, 0)], '3:fills up', '3:goes out', size=160)
    p.cam('3:fills@end', x=250, y=0, zoom=1.0)
    p.cam('3:anymore@end', x=200, y=0, zoom=1.08)
    # Collapse
    ex = 1700
    p.pic('earth', ex, 0, h=420, at='4:What happens', out='4:Then the-0.2')
    p.label('SIZE OF THE EARTH', ex, 290, '4:size of', '4:Then the-0.2', size=30)
    p.arrow((ex + 280, 0), (ex + 640, 0), '4:collapses', '4:Then the-0.2', width=2.2)
    p.circle(ex + 760, 0, 8, '4:collapses+0.5', '4:Then the-0.2', width=2.4, fill='accent', fillOpacity=0.8)
    p.label('LESS THAN 20 KM', ex + 760, 110, '4:20 kilometers', '4:Then the-0.2', size=30)
    p.label('LESS THAN A SECOND', ex + 380, -300, '4:In less than', '4:Then the-0.2', size=40, color='accent')
    p.hold_cam('4:What-0.6')
    p.cam('4:What happens@end', x=ex + 200, y=0, zoom=0.95)
    p.cam('4:fast@end', x=ex + 380, y=0, zoom=0.95)
    p.cam('4:across@end', x=ex + 420, y=0, zoom=1.0)
    snx = ex + 2100
    sn = p.pic('supernova', snx, 0, h=600, at='4:blown apart')
    for i, r in enumerate((340, 430)):
        p.circle(snx, 0, r, T('4:blown apart', 0.2 + 0.25 * i), width=1.4, color='muted', duration=0.8, out='5:The blast-0.2')
    p.label('SUPERNOVA', snx, 400, '4:supernova', '5:For a-0.2', size=44)
    p.cam('4:apart@end', x=snx, y=0, zoom=0.9)
    # Outshine the galaxy
    gx = snx + 1150
    spiral = []
    for arm in (0, math.pi):
        pts = [(gx + (20 + 9 * t) * math.cos(arm + t * 0.17), (20 + 9 * t) * 0.55 * math.sin(arm + t * 0.17)) for t in range(0, 34)]
        spiral.append(p.line(pts, T('5:galaxy', 0.2 * (arm > 0)), width=1.8, curve=True, duration=1.2, out='5:The blast-0.2'))
    p.label('ITS WHOLE GALAXY', gx, 260, '5:galaxy', '5:The blast-0.2', size=30)
    p.glows([(snx, 0)], '5:outshine', '5:The blast', size=320)
    p.pic('sun', gx + 300, -200, h=110, at='5:brightest', out='5:The blast-0.2')
    p.label('{n}', gx - 80, -330, '5:10 billion', '5:The blast-0.2', size=40, count={'to': 10000000000, 'duration': 1.5})
    p.label('TIMES BRIGHTER THAN THE SUN', gx - 80, -270, '5:brighter', '5:The blast-0.2', size=24)
    rays = []
    for i, ang in enumerate(range(-150, 210, 45)):
        a = math.radians(ang)
        rays.append(p.line([(snx + 180 * math.cos(a), 180 * math.sin(a)), (snx + 460 * math.cos(a), 460 * math.sin(a))], T('5:flies out', 0.03 * i), width=1.2, color='accent', duration=0.5, out='5:Much of the iron-0.2'))
        p.travel(rays[-1], T('5:flies out', 0.05 * i), dur=0.7, size=40)
    p.label('{n} KM EVERY SECOND', snx, -400, '5:10,000', '5:The blast-0.2', size=40, count={'to': 10000, 'duration': 1.2})
    p.hold_cam('5:For-0.3')
    p.cam('5:galaxy@end', x=snx + 560, y=0, zoom=0.72)
    p.cam('5:second@end', x=snx + 200, y=0, zoom=0.8)
    for i, (sym, word) in enumerate((('C', 'carbon'), ('O', 'oxygen'), ('Ca', 'calcium'), ('Fe', 'iron out'))):
        a = math.radians(-150 + 45 * i * 2)
        p.tile(sym, None, snx + 520 * math.cos(a), 520 * math.sin(a), f'5:{word}', '5:Much of the iron-0.2', s=86)
    p.cam('5:space@end', x=snx, y=0, zoom=0.82)
    blood = p.pic('blood_cell', snx + 1150, 60, h=170, at='5:Much of the iron')
    p.tile('Fe', 'IRON', snx + 1150, -170, '5:iron in', s=100)
    to_b = p.line([(snx + 200, -40), (snx + 600, -150), (snx + 1000, 40)], '5:Much of the iron', width=1.6, color='muted', curve=True, dashed=True)
    p.travel(to_b, '5:made in', dur=1.5, size=56)
    p.cam('5:far away@end', x=snx + 600, y=0, zoom=0.82)
    # The crushed core
    p.hold_cam('6:But-0.3')
    p.cam('6:there@end', x=snx, y=0, zoom=1.0)
    p.pic('neutron_star', snx, 0, h=150, at='6:crushed core')
    p.glows([(snx, 0)], '6:strangest', size=110)
    p.pic('gold_ring', snx + 450, 40, h=200, at='6:gold')
    p.cam('6:universe@end', x=snx, y=0, zoom=1.2)
    p.cam('6:from@end', x=snx + 220, y=20, zoom=1.15)
    p.end_all()


def part6(p):
    chapter(p, 6, 'That crushed')
    p.cam('start', x=0, y=0, zoom=1.0)
    ns = p.pic('neutron_star', 0, 0, h=420, at='1:That crushed')
    p.label('NEUTRON STAR', 0, 300, '1:neutron star', '1:packed-0.2', size=40)
    p.hold_cam('1:That crushed-0.2')
    p.cam('1:star@end', x=0, y=20, zoom=1.08)
    # Same mass as the Sun, size of a city
    p.pic('sun', -1100, 0, h=520, at='1:as much mass', out='1:packed-0.2')
    p.label('SAME MASS', -1100, 330, '1:mass', '1:packed-0.2', size=34)
    p.label('ABOUT 20 KM ACROSS', 0, -300, '1:city', '1:packed-0.2', size=34)
    p.cam('1:Sun@end', x=-550, y=0, zoom=0.75)
    p.cam('1:city@end', x=-500, y=0, zoom=0.78)
    cube = p.pic('sugar_cube', 900, 30, h=240, at='1:sugar cube')
    p.label('{n} TONS', 900, 280, '1:would weigh', '2:Sometimes-0.2', size=40, count={'to': 1000000000, 'duration': 1.6})
    p.label('A SUGAR-CUBE-SIZED PIECE', 900, -200, '1:sugar cube+0.3', '2:Sometimes-0.2', size=28)
    p.cam('1:tons@end', x=450, y=20, zoom=0.9)
    # Two neutron stars spiral in and crash
    cx, cy = 2100, 0
    p.pic('neutron_star', cx - 380, 0, h=180, at='2:two neutron', out='2:crash')
    p.pic('neutron_star', cx + 380, 0, h=180, at='2:two neutron+0.3', out='2:crash')
    arms = []
    for s0 in (0, math.pi):
        pts = [(cx + (380 - 11 * t) * math.cos(s0 + t * 0.19), (380 - 11 * t) * 0.45 * math.sin(s0 + t * 0.19)) for t in range(0, 33)]
        arms.append(p.line(pts, '2:circle', width=1.4, color='muted', curve=True, duration=1.4, out='3:On-0.2'))
    for a in arms:
        p.travel(a, '2:Little by', dur=2.6, size=60)
    p.glows([(cx, cy)], '2:crash', size=260)
    for i, r in enumerate((140, 240, 340)):
        p.circle(cx, cy, r, T('2:crash', 0.2 * i), width=1.4, color='accent', duration=0.7, out='3:Then-0.2')
    p.hold_cam('2:Sometimes-0.3')
    p.cam('2:other@end', x=cx, y=0, zoom=0.92)
    p.cam('2:closer@end', x=cx, y=0, zoom=1.05)
    p.cam('2:crash@end', x=cx, y=0, zoom=0.95)
    p.label('17 AUGUST 2017', cx, -290, '3:August', '3:Then-0.2', size=44)
    # Gravitational waves
    wy = 640
    wave = []
    for k in range(0, 120):
        x = cx - 900 + 15 * k
        f = 0.05 + 0.0025 * k
        wave.append((x, wy + 50 * (0.4 + k / 160) * math.sin(f * k * 15 / 15 * 6)))
    wv = p.line(wave, '3:ripples', width=2.0, curve=True, duration=2.0, out='3:Then-0.2')
    p.travel(wv, '3:gravitational', dur=1.6, size=40)
    p.label('GRAVITATIONAL WAVES', cx, wy - 150, '3:gravitational', '3:Then-0.2', size=36)
    p.label('USA', cx - 600, wy + 140, '3:United States', '3:Then-0.2', size=30)
    p.label('ITALY', cx + 600, wy + 140, '3:Italy', '3:Then-0.2', size=30)
    p.hold_cam('3:Detectors-0.3')
    p.cam('3:Italy@end', x=cx, y=wy, zoom=0.95)
    p.cam('3:waves@end', x=cx, y=wy - 60, zoom=0.92)
    p.hold_cam('3:About two')
    # Gamma-ray burst two seconds later
    p.label('2 SECONDS LATER', cx, -230, '3:two seconds', '3:Then-0.2', size=38, color='accent')
    p.glows([(cx, 0)], '3:burst', '3:Then', size=220)
    for i, ang in enumerate((-30, 30, 150, 210)):
        a = math.radians(ang)
        p.line([(cx + 120 * math.cos(a), 120 * math.sin(a)), (cx + 300 * math.cos(a), 300 * math.sin(a))], T('3:burst', 0.05 * i), width=1.6, color='accent', duration=0.35, out='3:Then-0.2')
    p.cam('3:later@end', x=cx, y=-60, zoom=0.95)
    p.cam('3:sky@end', x=cx, y=-40, zoom=1.0)
    # Telescopes saw the light
    tx = cx + 1150
    tel = p.pic('telescope', tx, 60, h=460, at='3:telescopes around')
    to_t = p.line([(cx + 60, -20), (cx + 700, -260), p.pt(tel, (0.78, 0.15))], '3:saw the light', width=1.6, color='muted', curve=True, dashed=True, out='4:Scientists-0.2')
    p.travel(to_t, '3:saw the light', dur=1.6, size=56)
    p.label('{n} MILLION LIGHT-YEARS', cx + 600, 380, '3:130', '4:The gold in-0.2', size=40, count={'to': 130, 'duration': 1.3})
    p.cam('3:Then telescopes', x=cx + 500, y=20, zoom=0.75)
    p.cam('3:crash@end', x=cx + 600, y=40, zoom=0.68)
    p.cam('3:away@end', x=cx + 600, y=40, zoom=0.7)
    # Gold and platinum
    p.tile('Au', 'GOLD', cx - 90, -190, '4:including gold', '4:Scientists-0.2', s=110)
    p.tile('Pt', 'PLATINUM', cx + 90, -190, '4:platinum', '4:Scientists-0.2', s=110)
    p.label('HEAVY ELEMENTS', cx, -310, '4:heavy elements', '4:Scientists-0.2', size=30)
    p.cam('4:being made@end', x=cx + 300, y=-40, zoom=0.82)
    ring = p.pic('gold_ring', cx + 700, 60, h=330, at='4:gold in your')
    p.travel_on(ring, PICS.outline('gold_ring', 0, 1, 70, shrink=0.03), '4:likely', dur=2.0, size=50)
    p.cam('4:jewelry@end', x=cx + 500, y=80, zoom=0.95)
    p.cam('4:like this@end', x=cx + 600, y=60, zoom=1.0)
    # Still being studied
    p.pic('supernova', cx + 1350, -60, h=260, at='4:other kinds', out='5:So now-0.2')
    p.label('STILL BEING STUDIED', cx + 900, -380, '4:still working', '5:So now-0.2', size=36, color='accent')
    p.cam('4:these crashes@end', x=cx + 800, y=-40, zoom=0.75)
    p.cam('4:exploding stars@end', x=cx + 850, y=-40, zoom=0.72)
    # Scattered elements, then you
    px = cx + 2700
    spots = [('H', '5:hydrogen', (-640, -300), 1.6), ('C', '5:carbon', (520, -320), 1.3), ('O', '5:oxygen', (-700, 260), 1.2), ('Fe', '5:iron', (640, 280), 1.5), ('Au', '5:gold', (0, -430), 1.9)]
    ids = []
    for sym, at, (dx, dy), depth in spots:
        ids.append(p.tile(sym, None, px + dx, dy, at, s=96))
    me = p.pic('person', px, 40, h=560, at='5:How did')
    chest = p.pt(me, CHEST)
    for i, (sym, at, (dx, dy), depth) in enumerate(spots):
        ln = p.line([(px + dx * 0.86, dy * 0.86), (chest[0] + dx * 0.12, chest[1] + dy * 0.12)], T('5:end up', 0.1 * i), width=1.4, color='muted', dashed=True)
        p.travel(ln, T('5:here', 0.12 * i), dur=1.1, size=44)
    p.hold_cam('5:So now-0.3')
    p.cam('5:space@end', x=px, y=-20, zoom=0.8)
    p.cam('5:you@end', x=px, y=0, zoom=0.88)
    p.end_all()


def part7(p):
    chapter(p, 7, 'The space')
    p.cam('start', x=0, y=0, zoom=0.88)
    neb = p.pic('nebula', 0, 0, h=600, at='1:The space')
    p.label('GAS AND DUST', 0, 380, '1:gas and dust', '2:4.5 billion years ago-0.2', size=36)
    drift = [(dx, dy) for dx, dy in [(-180, -120), (-60, 90), (120, -60), (200, 120), (-260, 60), (40, -200)]]
    p.glows(drift, '1:thin clouds', '2:collapse', size=40, stagger=0.15)
    p.hold_cam('1:The space-0.2')
    p.cam('1:empty@end', x=0, y=0, zoom=1.0)
    p.pic('supernova', -950, -100, h=280, at='1:star dies', out='2:4.5 billion years ago-0.2')
    for i, dy in enumerate((-160, -60, 40)):
        ln = p.line([(-800, -100 + dy * 0.3), (-480, dy), (-240, dy * 0.6)], T('1:adds new', 0.15 * i), width=1.2, color='muted', curve=True, dashed=True, out='2:4.5 billion years ago-0.2')
        p.travel(ln, T('1:adds new', 0.15 * i + 0.1), dur=1.3, size=40)
    p.cam('1:dies@end', x=-450, y=0, zoom=0.85)
    p.cam('1:these clouds@end', x=-350, y=0, zoom=0.88)
    # Collapse into the Sun and disk
    p.label('{n} BILLION YEARS AGO', 0, -390, '2:4.5 billion years ago', '2:Most of-0.2', size=46, count={'to': 4.5, 'decimals': 1, 'duration': 1.2})
    for i, (x, y) in enumerate(ring_points(0, 0, 420, 8, start=-67.5)):
        p.arrow((x, y), (x * 0.72, y * 0.72), T('2:collapse', 0.08 * i), '2:Most of-0.2', width=1.8, duration=0.5)
    p.hold_cam('2:4.5 billion years ago-0.3')
    p.cam('2:collapse@end', x=0, y=0, zoom=0.92)
    disk = p.pic('young_sun_disk', 0, 0, w=1100, at='2:center', id='disk')
    p.items[[i['id'] for i in p.items].index(neb)]['out'] = '2:center+0.2'
    p.glow(disk, (0.508, 0.47), '2:our Sun', size=120)
    p.travel_on(disk, PICS.outline('young_sun_disk', 0, 1, 90, shrink=0.12), '2:flat disk', dur=2.4, size=50)
    p.cam('2:Sun@end', x=0, y=0, zoom=1.0)
    p.cam('2:around it@end', x=0, y=0, zoom=0.95)
    # Grains to rocks to planets (magnifier from the disk)
    mx, my = 300, -330
    p.mag(disk, (0.66, 0.55), 26, mx + 520, my + 330, 230, '2:Inside that', '2:One of them-0.2')
    grains = [(mx + 420 + dx, my + 330 + dy) for dx, dy in [(-30, -40), (10, -20), (-10, 15), (35, 30), (-45, 25), (20, 55)]]
    for i, (x, y) in enumerate(grains):
        p.circle(x, y, 6, T('2:tiny grains', 0.05 * i), width=1.6, fill='accent', fillOpacity=0.6, out='2:then into planets')
    p.pic('rock', mx + 580, my + 330, h=110, at='2:into rocks', out='2:One of them-0.2')
    p.circle(mx + 680, my + 330, 48, '2:planets', width=2.2, fill='paper', out='2:One of them-0.2')
    p.cam('2:dust@end', x=380, y=-20, zoom=0.92)
    ex = 2000
    earth = p.pic('earth', ex, 0, h=480, at='2:Earth')
    p.hold_cam('2:One of them-0.3')
    p.cam('2:Earth@end', x=ex, y=0, zoom=1.0)
    rock = p.pic('rock', ex + 620, 60, h=220, at='2:check the date', id='meteor')
    p.label('{n} BILLION YEARS OLD', ex + 620, 290, '2:4.5 billion years old', '3:So the-0.2', size=40, count={'to': 4.5, 'decimals': 1, 'duration': 1.2})
    p.label('METEORITE', ex + 620, -110, '2:oldest meteorites', '3:So the-0.2', size=30)
    p.travel_on(rock, PICS.outline('rock', 0, 1, 60, shrink=0.02), '2:building blocks', dur=1.8, size=46)
    p.cam('2:date@end', x=ex + 320, y=40, zoom=0.95)
    p.cam('2:old@end', x=ex + 320, y=40, zoom=1.0)
    # Earth built from leftovers of stars
    stars = ring_points(ex, 0, 430, 6, start=-90)
    p.glows(stars, '3:leftovers', size=46, stagger=0.1)
    for i, (x, y) in enumerate(stars):
        p.line([(x + (ex - x) * 0.15, y * 0.85), (x + (ex - x) * 0.55, y * 0.45)], T('3:older stars', 0.08 * i), width=1.2, color='muted', duration=0.5)
    p.hold_cam('3:So the-0.3')
    p.cam('3:stars@end', x=ex, y=0, zoom=0.88)
    # The cycle: rock, air, plant, apple, you
    cx, cy, R = ex + 1900, 0, 470
    cyc = p.ellipse(cx, cy, R + 60, R - 40, '3:passed around', width=1.6, color='muted', n=96, duration=1.6)
    stations = [('rock', '3:in a rock', -90), ('air', '3:in the air', -18), ('plant', '3:in a plant', 54), ('apple', '3:in an apple', 126), ('person', '3:in you', 198)]
    for name, at, ang in stations:
        a = math.radians(ang)
        x, y = cx + (R + 60) * math.cos(a), cy + (R - 40) * math.sin(a)
        if name == 'air':
            for i in range(3):
                p.line([(x - 70 + 20 * k, y - 30 + 30 * i + (8 if k % 2 else -8)) for k in range(8)], T(at, 0.08 * i), width=1.8, curve=True)
            p.label('AIR', x, y + 80, T(at, 0.2), size=26)
        else:
            p.pic(name, x, y, h=260 if name == 'person' else 160, at=at)
    p.travel(cyc, '3:A carbon atom', dur=5.4, size=56)
    p.cam('3:and again@end', x=cx, y=0, zoom=0.88)
    p.cam('3:you@end', x=cx, y=0, zoom=0.9)
    # Stars made of the same ingredients
    sx = cx + 1900
    me = p.pic('person', sx, 40, h=560, at='4:And the stars', id='me7')
    p.glows([(sx + dx, dy) for dx, dy in [(-400, -300), (380, -260), (-460, 120), (450, 160), (-200, -420), (220, -430)]], '4:same ingredients', size=48, stagger=0.1)
    p.hold_cam('4:And-0.3')
    p.cam('4:us@end', x=sx, y=0, zoom=0.92)
    tel = p.pic('telescope', sx + 900, 40, h=420, at='4:astronomers')
    many = [(sx + 900 + 520 * math.cos(t) * (0.4 + 0.6 * ((i * 37) % 10) / 10), -260 + 200 * math.sin(t * 1.7)) for i, t in enumerate([j * 0.55 for j in range(22)])]
    p.glows(many, '4:150,000', size=30, stagger=0.04)
    p.label('MORE THAN {n} STARS', sx + 900, 340, '4:150,000', size=40, count={'to': 150000, 'duration': 1.4})
    p.cam('4:galaxy@end', x=sx + 600, y=0, zoom=0.78)
    six = ['C', 'H', 'N', 'O', 'S', 'P']
    for i, sym in enumerate(six):
        p.tile(sym, None, sx + 280 + 120 * i, -420, T('4:six main', 0.12 * i), s=96)
    p.label('MORE THAN {n}% OF YOUR BODY', sx + 580, -300, '4:97', size=34, count={'to': 97, 'duration': 1.0})
    p.cam('4:body@end', x=sx + 520, y=-60, zoom=0.82)
    p.glow(me, CHEST, '5:So', size=90)
    p.hold_cam('5:So-0.3')
    p.cam('5:stars@end', x=sx, y=20, zoom=1.0)
    p.end_all()


def part8(p):
    p.cam('start', x=0, y=0, zoom=1.0)
    me = p.pic('person', -500, 0, h=700, at="1:Let's", id='me8')
    p.pic('earth', 60, -40, h=330, at='1:where we')
    p.label('OLDER THAN THE EARTH', -220, 430, '1:older than', '1:hydrogen-0.3', size=40)
    p.hold_cam("1:Let's-0.2")
    p.cam('1:started@end', x=-220, y=20, zoom=0.95)
    p.cam('1:Earth@end', x=-220, y=20, zoom=1.0)
    p.pic('water_glass', 650, 130, h=260, at='1:hydrogen')
    p.tile('H', None, 650, -200, '1:hydrogen+0.3', s=96)
    ln = p.line([(-150, -480), (300, -420), (600, -280)], '1:first few', width=1.4, color='muted', curve=True, dashed=True)
    p.travel(ln, '1:first few', dur=1.4, size=50)
    p.pic('red_giant', 1180, -150, h=300, at='1:carbon')
    p.tile('C', None, 1180, 200, '1:carbon+0.3', s=96)
    p.cam('1:universe@end', x=300, y=20, zoom=0.82)
    p.cam('1:stars@end', x=600, y=20, zoom=0.78)
    p.pic('bone', 1650, -230, w=260, at='2:calcium')
    p.tile('Ca', None, 1650, -40, '2:calcium+0.3', s=90)
    p.pic('blood_cell', 1650, 160, h=110, at='2:iron')
    p.tile('Fe', None, 1650, 330, '2:iron+0.3', s=90)
    p.pic('supernova', 2150, -60, h=360, at='2:exploding')
    p.hold_cam('2:The calcium-0.3')
    p.cam('2:exploding stars@end', x=1350, y=40, zoom=0.82)
    p.pic('gold_ring', 2650, 30, h=230, at='2:gold')
    p.tile('Au', None, 2650, -200, '2:gold+0.3', s=96)
    p.pic('neutron_star', 3100, -150, h=140, at='2:two dead')
    p.pic('neutron_star', 3250, 60, h=140, at='2:two dead+0.3')
    p.cam('2:together@end', x=2450, y=20, zoom=0.82)
    # Everything around the person
    p.hold_cam('3:Carl-0.3')
    p.cam('3:best@end', x=1100, y=0, zoom=0.42)
    p.label('WE ARE MADE OF STAR-STUFF', 1100, -620, '3:We are', '3:So the-0.2', size=60)
    p.label('CARL SAGAN', 1100, -520, '3:star-stuff', '3:So the-0.2', size=30, color='accent')
    p.cam('3:star-stuff@end', x=1100, y=-120, zoom=0.45)
    # Night sky and the open hand
    hx, hy = 1100, -1500
    for it in p.items:
        it.setdefault('out', '3:So the-0.2')
    for d in p.drawings:
        d.setdefault('out', '3:So the-0.2')
    hand = p.pic('open_hand', hx, hy + 260, h=300, at='3:look up')
    sky = [(hx + dx, hy - 250 + dy) for dx, dy in [(-700, -60), (-480, 80), (-260, -120), (-40, 40), (200, -140), (420, 60), (640, -80), (-600, 180), (560, 190), (0, -230)]]
    p.glows(sky, '3:night sky', size=46, stagger=0.1)
    palm = p.pt(hand, (0.53, 0.45))
    for i, (x, y) in enumerate(sky[1::2]):
        ln = p.line([(x, y + 20), (palm[0] + (x - palm[0]) * 0.1, palm[1] - 30)], T('3:where you', 0.1 * i), width=1.0, color='muted', duration=0.8)
        p.travel(ln, T('3:where you', 0.12 * i), dur=1.2, size=40)
    p.glow(hand, (0.53, 0.45), '3:came from', size=110)
    p.label('AS ABOVE, SO BELOW', hx, hy - 360, '3:night sky', 'end-0.6', size=40, color='accent')
    p.label('YOU ARE MADE OF STARS', hx, hy + 520, '3:came from@end', 'end-0.6', size=54)
    p.hold_cam('3:So the-0.4')
    p.cam('3:sky@end', x=hx, y=hy, zoom=0.92)
    p.cam('3:stars@end', x=hx, y=hy + 60, zoom=0.92)
    p.cam('3:came from@end', x=hx, y=hy + 100, zoom=0.88)
    p.cam('end', x=hx, y=hy + 120, zoom=0.82)
    p.end_all('end-0.9')


BUILDERS = [part0, part1, part2, part3, part4, part5, part6, part7, part8]


def main():
    ox, oy, oz = 0.0, 0.0, None
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
        last = max(p.camera, key=lambda c: (c['at'] == 'end', 0))
        end_cam = p.camera[-1]
        # The camera holds its last framing until the end of the part.
        if end_cam['at'] != 'end':
            p.camera.append({'at': 'end', 'x': end_cam['x'], 'y': end_cam['y'], 'zoom': end_cam['zoom']})
        ox, oy, oz = p.camera[-1]['x'], p.camera[-1]['y'], p.camera[-1]['zoom']
        title = 'You Are Made of Stars' + ('' if n == 0 else f' — part {n}')
        json.dump(p.settings(THEME, title), open(f'{d}/settings.json', 'w'), indent=1)
        pass
        print(f'p{n}: {len(p.items)} pictures, {len(p.drawings)} drawings, {len(p.lights)} lights, {len(p.labels)} labels, {len(p.camera)} camera keys')


if __name__ == '__main__':
    main()
    for a in sorted(AMBIGUOUS):
        print('ambiguous:', a)
