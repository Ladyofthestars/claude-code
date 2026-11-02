"""Builds the YouTube thumbnail (1280x720) for video 3, "You've Never Actually Touched Anything".

Same series look as videos 1 and 2: shapes from the videos filled with stars and nebula on deep blue,
gold and white text. Two hands reach toward each other; their fingertips never meet, and the gap
between them glows with electrons.

Usage: python tools/make_thumbnail_touch.py OUT.png --font-dir DIR
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
import make_thumbnail as mt  # noqa: E402

W, H = mt.W, mt.H
rng = np.random.default_rng(5)


def star_fill(img, mask, heart=None, glow=True):
    """Fill a mask with the series' nebula and stars, with a soft blue glow around it."""
    y, x = np.mgrid[0:H, 0:W]
    m = Image.fromarray((mask * 255).astype(np.uint8))
    if glow:
        for r, s, col in ((40, 0.5, (90, 130, 255)), (14, 0.75, (160, 190, 255)), (4, 0.9, (225, 235, 255))):
            g = np.asarray(m.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
            lay = np.zeros((H, W, 4), np.float32)
            lay[..., :3] = col
            lay[..., 3] = np.clip(g * 255 * s * 1.6, 0, 255)
            img.alpha_composite(Image.fromarray(lay.astype(np.uint8), 'RGBA'))
    neb = np.clip((mt.fbm() - 0.28) / 0.5, 0, 1) ** 1.3
    hot = np.zeros((H, W), np.float32)
    if heart is not None:
        hot = np.exp(-(((x - heart[0]) / 160) ** 2 + ((y - heart[1]) / 120) ** 2))
    t = np.clip(0.12 + neb * 0.72 + hot * 0.3, 0, 1)
    body = mt.palette(t) * (0.3 + 0.7 * neb[..., None]) + hot[..., None] * np.array([255, 215, 150]) * 0.35
    inside = np.zeros((H, W, 4), np.float32)
    inside[..., :3] = np.clip(body, 0, 255)
    inside[..., 3] = mask * 255
    img.alpha_composite(Image.fromarray(inside.astype(np.uint8), 'RGBA'))
    img.alpha_composite(mt.stars(260, mask=mask, big=0.06).filter(ImageFilter.GaussianBlur(0.4)))


def hand_mask(src, h, box_xy, mirror=False):
    im = src.copy()
    if mirror:
        im = ImageOps.mirror(im)
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    m = Image.new('L', (W, H), 0)
    m.paste(im.getchannel('A'), box_xy)
    return m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.0)), im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--font-dir', required=True)
    a = ap.parse_args()
    y, x = np.mgrid[0:H, 0:W]

    # Deep blue sky with a light behind the gap between the hands.
    haze = mt.fbm()
    d = np.sqrt(((x - 640) / 700) ** 2 + ((y - 470) / 420) ** 2)
    glow = np.clip(1 - d, 0, 1) ** 1.6
    sky = np.zeros((H, W, 3), np.float32)
    sky[..., 0] = 6 + 30 * glow + 8 * haze
    sky[..., 1] = 14 + 58 * glow + 14 * haze
    sky[..., 2] = 34 + 120 * glow + 22 * haze
    img = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8)).convert('RGBA')
    img.alpha_composite(mt.stars(220).filter(ImageFilter.GaussianBlur(0.5)))

    # Two hands from the videos, reaching toward each other.
    src = Image.open(os.path.join(mt.IMG, 'open_hand.png')).convert('RGBA')
    src = src.crop(src.getbbox())
    hh = 300
    ml, iml = hand_mask(src, hh, (0, 0))
    left_w = iml.width
    gap_x, gap_y = 640, 470
    # Fingertips: the right end of the left hand's drawing, at about 30% of its height.
    lx, ly = gap_x - 18 - left_w, gap_y - int(hh * 0.3)
    ml, _ = hand_mask(src, hh, (lx, ly))
    mr, _ = hand_mask(src, hh, (gap_x + 18, ly), mirror=True)
    star_fill(img, np.asarray(ml).astype(np.float32) / 255, heart=(gap_x - 60, gap_y))
    star_fill(img, np.asarray(mr).astype(np.float32) / 255, heart=(gap_x + 60, gap_y))
    # The drawing's own lines, faintly, so the shapes read as hands.
    for mirror, pos in ((False, (lx, ly)), (True, (gap_x + 18, ly))):
        _, im = hand_mask(src, hh, pos, mirror=mirror)
        arr = np.asarray(im).astype(np.float32)
        lum = arr[..., :3].mean(axis=2)
        lines = np.clip((200 - lum) / 160.0, 0, 1) * (arr[..., 3] / 255.0)
        ll = np.zeros(arr.shape, np.float32)
        ll[..., :3] = (215, 225, 255)
        ll[..., 3] = lines * 120
        img.alpha_composite(Image.fromarray(ll.astype(np.uint8), 'RGBA'), pos)

    # The gap: a bright line of light with electrons swirling, never crossed.
    gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    for _ in range(120):
        r = abs(rng.normal(0, 26))
        th = rng.uniform(0, 2 * np.pi)
        px, py = gap_x + r * 0.5 * np.cos(th), gap_y + r * np.sin(th)
        s = rng.choice([1.0, 1.6, 2.4], p=[0.5, 0.35, 0.15])
        col = (255, 225, 160) if rng.random() < 0.6 else (210, 228, 255)
        gd.ellipse((px - s, py - s, px + s, py + s), fill=col + (int(rng.uniform(140, 255)),))
    halo = np.exp(-(((x - gap_x) / 40) ** 2 + ((y - gap_y) / 70) ** 2))
    hl = np.zeros((H, W, 4), np.float32)
    hl[..., :3] = (255, 220, 150)
    hl[..., 3] = np.clip(halo * 230, 0, 255)
    img.alpha_composite(Image.fromarray(hl.astype(np.uint8), 'RGBA'))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(2)))
    img.alpha_composite(gl)

    # Text across the top: "YOU'VE NEVER" white, "TOUCHED ANYTHING" glowing gold.
    f_mid = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-900.ttf'), 70)
    f_big = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-900.ttf'), 96)

    def shadow(xy, s, font, blur=14, alpha=230, stroke=10):
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text(xy, s, font=font, fill=(0, 0, 0, alpha), stroke_width=stroke, stroke_fill=(0, 0, 0, alpha), anchor='mm')
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))

    def gold(xy, s, font):
        g2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g2).text(xy, s, font=font, fill=(255, 170, 60, 200), stroke_width=6, stroke_fill=(255, 170, 60, 200), anchor='mm')
        img.alpha_composite(g2.filter(ImageFilter.GaussianBlur(24)))
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

    shadow((640, 90), "YOU'VE NEVER", f_mid)
    ImageDraw.Draw(img).text((640, 90), "YOU'VE NEVER", font=f_mid, fill=(255, 255, 255), stroke_width=5, stroke_fill=(8, 8, 20), anchor='mm')
    shadow((640, 190), 'TOUCHED ANYTHING', f_big)
    bb = gold((640, 190), 'TOUCHED ANYTHING', f_big)
    img.convert('RGB').save(a.out, quality=95)
    print('wrote', a.out, 'text box', bb)


if __name__ == '__main__':
    main()
