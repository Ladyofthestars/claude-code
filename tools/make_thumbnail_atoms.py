"""Builds the YouTube thumbnail (1280x720) for video 2, "What Happens to Your Atoms When You Die?".

It continues video 1's thumbnail, so the two read as a series: the same star-filled figure, now
dissolving upward into stardust, on the deep blue of video 2, with "WHEN YOU DIE / NOTHING IS LOST".

Usage: python tools/make_thumbnail_atoms.py OUT.png --font-dir DIR
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import make_thumbnail as mt  # noqa: E402

W, H = mt.W, mt.H
rng = np.random.default_rng(21)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--font-dir', required=True)
    a = ap.parse_args()
    y, x = np.mgrid[0:H, 0:W]

    # Deep blue sky (video 2's page) with a soft light behind the figure, and stars.
    haze = mt.fbm()
    d = np.sqrt(((x - 380) / 760) ** 2 + ((y - 330) / 560) ** 2)
    glow = np.clip(1 - d, 0, 1) ** 1.6
    sky = np.zeros((H, W, 3), np.float32)
    sky[..., 0] = 6 + 30 * glow + 8 * haze
    sky[..., 1] = 14 + 58 * glow + 14 * haze
    sky[..., 2] = 34 + 120 * glow + 22 * haze
    img = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8)).convert('RGBA')
    img.alpha_composite(mt.stars(240).filter(ImageFilter.GaussianBlur(0.5)))

    # The figure from the videos, as a mask.
    src = Image.open(os.path.join(mt.IMG, 'person.png')).convert('RGBA')
    src = src.crop(src.getbbox())
    ph = 640
    src = src.resize((int(src.width * ph / src.height), ph), Image.LANCZOS)
    px, py = 370 - src.width // 2, H - ph - 30
    m = Image.new('L', (W, H), 0)
    m.paste(src.getchannel('A'), (px, py))
    m = m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    mask = np.asarray(m).astype(np.float32) / 255

    # Dissolve: the top of the figure breaks up into stardust (more at the head, none at the feet).
    yn = np.clip((y - py) / ph, 0, 1)
    n = mt.noise(18) * 0.6 + mt.noise(6) * 0.4
    keep = np.clip((yn - 0.08 + 0.42 * n - 0.21) / 0.12, 0, 1)
    body_mask = mask * keep
    gone = mask * (1 - keep)

    # Glow around what is left of the figure.
    bm = Image.fromarray((body_mask * 255).astype(np.uint8))
    for r, s, col in ((50, 0.5, (90, 130, 255)), (18, 0.75, (160, 190, 255)), (5, 0.9, (225, 235, 255))):
        g = np.asarray(bm.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
        lay = np.zeros((H, W, 4), np.float32)
        lay[..., :3] = col
        lay[..., 3] = np.clip(g * 255 * s * 1.6, 0, 255)
        img.alpha_composite(Image.fromarray(lay.astype(np.uint8), 'RGBA'))

    # Inside: a nebula in blues and violets, brightest (gold) at the heart.
    neb = np.clip((mt.fbm() - 0.28) / 0.5, 0, 1) ** 1.3
    hx, hy = px + src.width * 0.5, py + ph * 0.36
    heart = np.exp(-(((x - hx) / 70) ** 2 + ((y - hy) / 80) ** 2))
    t = np.clip(0.1 + neb * 0.7 + heart * 0.35, 0, 1)
    body = mt.palette(t) * (0.3 + 0.7 * neb[..., None]) + heart[..., None] * np.array([255, 215, 150]) * 0.45
    inside = np.zeros((H, W, 4), np.float32)
    inside[..., :3] = np.clip(body, 0, 255)
    inside[..., 3] = body_mask * 255
    img.alpha_composite(Image.fromarray(inside.astype(np.uint8), 'RGBA'))
    img.alpha_composite(mt.stars(380, mask=body_mask, big=0.06).filter(ImageFilter.GaussianBlur(0.4)))
    a_ = np.asarray(src).astype(np.float32)
    lum = a_[..., :3].mean(axis=2)
    lines = np.clip((200 - lum) / 160.0, 0, 1) * (a_[..., 3] / 255.0)
    ll = np.zeros(a_.shape, np.float32)
    ll[..., :3] = (215, 225, 255)
    ll[..., 3] = lines * 110
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.alpha_composite(Image.fromarray(ll.astype(np.uint8), 'RGBA'), (px, py))
    la = np.asarray(lay).astype(np.float32)
    la[..., 3] *= keep
    img.alpha_composite(Image.fromarray(la.astype(np.uint8), 'RGBA'))

    # Stardust: particles from the dissolved part, rising and drifting right, fading as they go.
    ys, xs = np.nonzero(gone > 0.3)
    pick = rng.choice(len(xs), size=min(900, len(xs)), replace=False)
    dust = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for i in pick:
        sx, sy = xs[i], ys[i]
        lift = rng.random() ** 1.4
        dx = lift * rng.uniform(80, 420) + rng.normal(0, 14)
        dy = -lift * rng.uniform(60, 300) + rng.normal(0, 14)
        r = rng.choice([0.8, 1.2, 1.7, 2.4], p=[0.35, 0.35, 0.2, 0.1]) * (1.15 - 0.5 * lift)
        col = (255, 222, 160) if rng.random() < 0.45 else (210, 228, 255)
        al = int(255 * (1 - 0.8 * lift))
        dd.ellipse((sx + dx - r, sy + dy - r, sx + dx + r, sy + dy + r), fill=col + (al,))
    img.alpha_composite(dust.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(dust)
    hl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    mt.sparkle(hl, int(hx), int(hy), 40)
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(1.5)))
    img.alpha_composite(hl)

    # Text: "WHEN YOU DIE," in white, "NOTHING IS LOST" big in glowing gold.
    f_mid = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-900.ttf'), 68)
    f_big = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-900.ttf'), 104)
    cx = 920

    def shadow(xy, s, font, blur=14, alpha=230, stroke=10):
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text(xy, s, font=font, fill=(0, 0, 0, alpha), stroke_width=stroke, stroke_fill=(0, 0, 0, alpha), anchor='mm')
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))

    def gold(xy, s, font):
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).text(xy, s, font=font, fill=(255, 170, 60, 200), stroke_width=6, stroke_fill=(255, 170, 60, 200), anchor='mm')
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(24)))
        tm = Image.new('L', (W, H), 0)
        ImageDraw.Draw(tm).text(xy, s, font=font, fill=255, anchor='mm')
        bb = tm.getbbox()
        k = np.clip((y - bb[1]) / (bb[3] - bb[1]), 0, 1)[..., None]
        grad = np.zeros((H, W, 4), np.float32)
        grad[..., :3] = (1 - k) * np.array([255, 240, 170]) + k * np.array([240, 150, 40])
        grad[..., 3] = 255
        ol = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ol).text(xy, s, font=font, fill=(0, 0, 0, 0), stroke_width=5, stroke_fill=(30, 14, 4, 255), anchor='mm')
        img.alpha_composite(ol)
        img.paste(Image.fromarray(grad.astype(np.uint8), 'RGBA'), (0, 0), tm)
        return bb

    shadow((cx, 250), 'WHEN YOU DIE,', f_mid)
    ImageDraw.Draw(img).text((cx, 250), 'WHEN YOU DIE,', font=f_mid, fill=(255, 255, 255), stroke_width=5, stroke_fill=(8, 8, 20), anchor='mm')
    shadow((cx, 360), 'NOTHING', f_big)
    b1 = gold((cx, 360), 'NOTHING', f_big)
    shadow((cx, 470), 'IS LOST', f_big)
    b2 = gold((cx, 470), 'IS LOST', f_big)
    img.convert('RGB').save(a.out, quality=95)
    print('wrote', a.out, 'text boxes', b1, b2)


if __name__ == '__main__':
    main()
