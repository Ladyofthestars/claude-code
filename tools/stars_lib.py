"""Small helpers for writing the settings of a long video part by part.

Coordinates are page units (1 unit = 1 pixel at zoom 1). Each part is written around its
own origin and then shifted so it starts exactly where the previous part's camera ended.
Times are word references like "2:Big Bang" (paragraph 2 of this part), see src/template/time.ts.
"""
import json
import math
import os
import re

import cv2
import numpy as np
from PIL import Image

W, H = 1920, 1080
SAFE = {'top': 0.06, 'bottom': 0.06, 'side': 0.05}
SAFE_W = W * (1 - 2 * SAFE['side'])
SAFE_H = H * (1 - SAFE['top'] - SAFE['bottom'])


def T(ref, delta):
    """Shift a time reference by delta seconds ("2:sun+0.2" + 0.3 -> "2:sun+0.5")."""
    if isinstance(ref, (int, float)):
        return round(ref + delta, 3)
    m = re.match(r'^(.*?)\s*([+-]\d+(?:\.\d+)?)$', ref)
    base, off = (m.group(1), float(m.group(2))) if m and m.group(1) else (ref, 0.0)
    off = round(off + delta, 3)
    return base if off == 0 else f'{base}{"+" if off > 0 else ""}{off}'


class Pictures:
    def __init__(self, folder, url_prefix):
        self.folder = folder
        self.url = url_prefix
        self.info = {}
        for line in open(os.path.join(folder, 'manifest.txt')):
            name, js = line.split(' ', 1)
            d = json.loads(js)
            self.info[name] = {'src': f'{url_prefix}/{name}.png', 'aspect': d['aspect'], 'content': d['content']}
        self._outlines = {}

    def outline(self, name, a=0.0, b=1.0, n=48, shrink=0.0):
        """Points (UV) along the drawn object's outline, clockwise from its top, from fraction a to b."""
        if name not in self._outlines:
            im = np.asarray(Image.open(os.path.join(self.folder, f'{name}.png')).convert('RGBA'))[..., 3]
            mask = (im > 128).astype(np.uint8)
            cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            c = max(cs, key=cv2.contourArea)[:, 0, :].astype(float)
            h, w = mask.shape
            top = int(np.argmin(c[:, 1]))
            c = np.roll(c, -top, axis=0)
            seg = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
            self._outlines[name] = (c, seg / seg[-1], w, h)
        c, s, w, h = self._outlines[name]
        cxy = c.mean(axis=0)
        out = []
        for f in np.linspace(a, b, n):
            i = int(np.searchsorted(s, f % 1.0))
            i = min(i, len(c) - 1)
            p = c[i] + (cxy - c[i]) * shrink
            out.append([round(p[0] / w, 4), round(p[1] / h, 4)])
        return out


class Part:
    def __init__(self, pics, n, words):
        self.pics = pics
        self.n = n
        self.words = words
        self.items, self.camera, self.drawings, self.lights, self.labels, self.mags = [], [], [], [], [], []
        self.geo = {}
        self.boxes = {}
        self._k = 0

    # ---- references -----------------------------------------------------------
    def check_ref(self, ref):
        if isinstance(ref, (int, float)) or ref.split('+')[0].split('-')[0] in ('start', 'end', 'voiceEnd'):
            return
        body = re.match(r'^(.*?)(\s*[+-]\d+(?:\.\d+)?)?$', ref).group(1)
        m = re.match(r'^(\d+):(.+?)(@end)?$', body)
        norm = lambda s: re.sub(r"[^a-z0-9']", '', s.lower())
        line = int(m.group(1))
        toks = [norm(t) for t in m.group(2).split() if norm(t)]
        ws = [norm(w['text']) for w in self.words['words'] if w['line'] == line]
        for i in range(len(ws) - len(toks) + 1):
            if ws[i:i + len(toks)] == toks:
                return
        raise SystemExit(f'Part {self.n}: phrase "{m.group(2)}" not in paragraph {line}')

    def uid(self, p):
        self._k += 1
        return f'{p}{self._k}'

    # ---- pictures -----------------------------------------------------------------
    def pic(self, name, cx, cy, h=None, w=None, at=None, out=None, depth=None, id=None, fade=None):
        """Place a picture so its drawn content is centred at (cx, cy) with content height h (or width w)."""
        p = self.pics.info[name]
        c = p['content']
        ch, cw = c[3] - c[1], c[2] - c[0]
        if h is not None:
            ih = h / ch
            iw = ih * p['aspect']
        else:
            iw = w / cw
            ih = iw / p['aspect']
        icx = cx - ((c[0] + c[2]) / 2 - 0.5) * iw
        icy = cy - ((c[1] + c[3]) / 2 - 0.5) * ih
        id = id or self.uid(name)
        d = {'id': id, 'picture': name, 'x': round(icx, 1), 'y': round(icy, 1), 'width': round(iw, 1)}
        for k, v in (('in', at), ('out', out), ('depth', depth), ('fade', fade)):
            if v is not None:
                d[k] = v
                if k in ('in', 'out'):
                    self.check_ref(v)
        self.items.append(d)
        self.geo[id] = (icx, icy, iw, ih, name)
        cbw = (c[2] - c[0]) * iw
        cbh = (c[3] - c[1]) * ih
        self.boxes[id] = (cx - cbw / 2, cy - cbh / 2, cx + cbw / 2, cy + cbh / 2)
        return id

    def pt(self, id, uv):
        icx, icy, iw, ih, _ = self.geo[id]
        return (icx + (uv[0] - 0.5) * iw, icy + (uv[1] - 0.5) * ih)

    # ---- drawings -----------------------------------------------------------------------
    def _draw(self, d):
        self.check_ref(d['draw'])
        if 'out' in d:
            self.check_ref(d['out'])
        self.drawings.append(d)
        return d['id']

    def line(self, pts, at, out=None, id=None, **kw):
        kw['out'] = out
        d = {'id': id or self.uid('line'), 'kind': 'path', 'points': [[round(x, 1), round(y, 1)] for x, y in pts], 'draw': at}
        d.update({k: v for k, v in kw.items() if v is not None})
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.boxes[d['id']] = (min(xs), min(ys), max(xs), max(ys))
        return self._draw(d)

    def circle(self, cx, cy, r, at, out=None, id=None, **kw):
        kw['out'] = out
        d = {'id': id or self.uid('circle'), 'kind': 'circle', 'cx': round(cx, 1), 'cy': round(cy, 1), 'r': round(r, 1), 'draw': at}
        d.update({k: v for k, v in kw.items() if v is not None})
        self.boxes[d['id']] = (cx - r, cy - r, cx + r, cy + r)
        return self._draw(d)

    def rect(self, x, y, w, h, at, out=None, id=None, **kw):
        kw['out'] = out
        d = {'id': id or self.uid('rect'), 'kind': 'rect', 'x': round(x, 1), 'y': round(y, 1), 'w': round(w, 1), 'h': round(h, 1), 'draw': at}
        d.update({k: v for k, v in kw.items() if v is not None})
        self.boxes[d['id']] = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        return self._draw(d)

    def ellipse(self, cx, cy, rx, ry, at, rot=0, n=72, **kw):
        a = math.radians(rot)
        pts = []
        for i in range(n + 1):
            t = -math.pi / 2 + 2 * math.pi * i / n
            x, y = rx * math.cos(t), ry * math.sin(t)
            pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
        return self.line(pts, at, **kw)

    def arrow(self, a, b, at, out=None, **kw):
        return self.line([a, b], at, out, arrow=True, **kw)

    # ---- text -----------------------------------------------------------------------------
    def label(self, text, x, y, at, out=None, size=40, space='world', color=None, weight=None, spacing=None, count=None):
        self.check_ref(at)
        d = {'text': text, 'x': round(x, 1), 'y': round(y, 1), 'space': space, 'size': size, 'in': at}
        if out is not None:
            self.check_ref(out)
            d['out'] = out
        for k, v in (('color', color), ('weight', weight), ('spacing', spacing), ('count', count)):
            if v is not None:
                d[k] = v
        self.labels.append(d)
        return d

    def tile(self, sym, name, x, y, at, out=None, s=110, fill=None, fill_at=None, dashed=None):
        """An element tile: a square with the symbol and, below it, the element's name."""
        rid = self.rect(x, y, s, s, at, out=out, width=2.6, duration=0.6, fill=fill or 'paper',
                        fillOpacity=0.28 if fill == 'accent' else 1, fillAt=fill_at or T(at, 0.1), dashed=dashed, color='muted' if dashed else None)
        self.label(sym, x, y - s * 0.06, T(at, 0.25), out, size=round(s * 0.42), spacing=0.02)
        if name:
            self.label(name, x, y + s * 0.3, T(at, 0.35), out, size=round(s * 0.105), weight=500, spacing=0.18)
        return rid

    # ---- lights --------------------------------------------------------------------------------
    def glow(self, item, uv, at, to=None, size=60):
        self.check_ref(at)
        d = {'item': item, 'at': list(uv), 'from': at, 'size': size}
        if to is not None:
            self.check_ref(to)
            d['to'] = to
        self.lights.append(d)

    def glows(self, pts, at, to=None, size=40, stagger=0.0):
        self.check_ref(at)
        d = {'worldPoints': [[round(x, 1), round(y, 1)] for x, y in pts], 'from': at, 'size': size, 'stagger': stagger}
        if to is not None:
            self.check_ref(to)
            d['to'] = to
        self.lights.append(d)

    def travel(self, drawing, at, dur=1.2, size=50, reverse=None):
        self.check_ref(at)
        d = {'drawing': drawing, 'from': at, 'duration': dur, 'size': size}
        if reverse:
            d['reverse'] = True
        self.lights.append(d)

    def travel_on(self, item, path, at, dur=1.4, size=50):
        self.check_ref(at)
        self.lights.append({'item': item, 'path': path, 'from': at, 'duration': dur, 'size': size})

    # ---- magnifier --------------------------------------------------------------------------------
    def mag(self, item, uv, src_r, x, y, r, open, close=None, contents=None):
        self.check_ref(open)
        d = {'source': {'item': item, 'at': list(uv), 'radius': src_r}, 'x': round(x, 1), 'y': round(y, 1), 'radius': r, 'open': open, 'contents': contents or []}
        if close is not None:
            self.check_ref(close)
            d['close'] = close
        self.mags.append(d)
        self.boxes[self.uid('mag')] = (x - r, y - r, x + r, y + r)
        return d

    # ---- camera ------------------------------------------------------------------------------------
    def frame(self, ids, fit=0.85, dx=0, dy=0):
        bs = [self.boxes[i] for i in ids]
        x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
        x1, y1 = max(b[2] for b in bs), max(b[3] for b in bs)
        z = fit * min(SAFE_W / max(1, x1 - x0), SAFE_H / max(1, y1 - y0))
        return ((x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy, z)

    def cam(self, at, x=None, y=None, zoom=None, focus=None, fit=0.85, dx=0, dy=0, hold=None):
        self.check_ref(at)
        if focus is not None:
            x, y, z = self.frame(focus, fit, dx, dy)
            zoom = zoom or z
        d = {'at': at, 'x': round(x, 1), 'y': round(y, 1), 'zoom': round(zoom, 4)}
        if hold:
            d['hold'] = hold
        self.camera.append(d)
        return (x, y, zoom)

    def hold_cam(self, at):
        """Repeat the last framing at a new time (the next move starts from here)."""
        last = self.camera[-1]
        self.check_ref(at)
        self.camera.append({'at': at, 'x': last['x'], 'y': last['y'], 'zoom': last['zoom']})

    # ---- finish -----------------------------------------------------------------------------------------
    def end_all(self, at='end-1.1'):
        for it in self.items:
            it.setdefault('out', at)
        for d in self.drawings:
            d.setdefault('out', at)
        for l in self.labels:
            if l['space'] == 'world':
                l.setdefault('out', at)
        for L in self.lights:
            if 'to' not in L and 'duration' not in L:
                L['to'] = at

    def shift(self, ox, oy):
        for it in self.items:
            it['x'] = round(it['x'] + ox, 1)
            it['y'] = round(it['y'] + oy, 1)
        for d in self.drawings:
            if 'points' in d:
                d['points'] = [[round(p[0] + ox, 1), round(p[1] + oy, 1)] for p in d['points']]
            for kx, ky in (('cx', 'cy'), ('x', 'y')):
                if kx in d:
                    d[kx] = round(d[kx] + ox, 1)
                    d[ky] = round(d[ky] + oy, 1)
        for l in self.labels:
            if l['space'] == 'world':
                l['x'] = round(l['x'] + ox, 1)
                l['y'] = round(l['y'] + oy, 1)
        for m in self.mags:
            m['x'] = round(m['x'] + ox, 1)
            m['y'] = round(m['y'] + oy, 1)
        for L in self.lights:
            if 'worldPoints' in L:
                L['worldPoints'] = [[round(p[0] + ox, 1), round(p[1] + oy, 1)] for p in L['worldPoints']]
        for c in self.camera:
            c['x'] = round(c['x'] + ox, 1)
            c['y'] = round(c['y'] + oy, 1)

    def settings(self, theme, title):
        used = sorted({it['picture'] for it in self.items} | {c['picture'] for m in self.mags for c in m['contents']})
        return {
            'title': title,
            'size': {'width': W, 'height': H},
            'audio': 'narration.mp3',
            'words': 'words.json',
            'tailSeconds': 0,
            'safeArea': SAFE,
            'theme': theme,
            'pictures': {n: self.pics.info[n] for n in used},
            'items': self.items,
            'camera': self.camera,
            'threads': [],
            'drawings': self.drawings,
            'lights': self.lights,
            'magnifiers': self.mags,
            'labels': self.labels,
        }
