"""Builds the YouTube thumbnail (1280x720) for "You Are Made of Stars" from the video's own
illustrations: a dark night sky, a supernova glowing in gold and blue, and a person lit by it,
with big, bold text.

Usage: python tools/make_thumbnail.py OUT.png --font-dir DIR
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
IMG = 'public/videos/made-of-stars/images'


def glow_lines(name, height, color, alpha_boost=1.0):
    """Turn an ink drawing (dark lines on a light fill) into glowing light lines on transparent."""
    im = Image.open(os.path.join(IMG, f'{name}.png')).convert('RGBA')
    bb = im.getbbox()
    im = im.crop(bb)
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    lum = a[..., :3].mean(axis=2)
    strength = np.clip((255 - lum) / 200.0, 0, 1) * (a[..., 3] / 255.0)
    out = np.zeros_like(a)
    out[..., :3] = color
    out[..., 3] = np.clip(strength * 255 * alpha_boost, 0, 255)
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def add_glow(base, layer, pos, radius, strength=1.0):
    big = Image.new('RGBA', base.size, (0, 0, 0, 0))
    big.alpha_composite(layer, pos)
    g = big.filter(ImageFilter.GaussianBlur(radius))
    ga = np.asarray(g).astype(np.float32)
    ga[..., 3] = np.clip(ga[..., 3] * strength, 0, 255)
    base.alpha_composite(Image.fromarray(ga.astype(np.uint8), 'RGBA'))
    base.alpha_composite(big)


def radial(cx, cy, r, color, max_alpha):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** 2 * max_alpha
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = color
    out[..., 3] = a
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--font-dir', required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(11)

    # Night sky: deep navy to black, with a scatter of soft stars.
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt((x - 900) ** 2 + (y - 330) ** 2) / 900
    sky = np.zeros((H, W, 4), np.float32)
    sky[..., 0] = 10 + 12 * np.clip(1 - d, 0, 1)
    sky[..., 1] = 14 + 22 * np.clip(1 - d, 0, 1)
    sky[..., 2] = 28 + 48 * np.clip(1 - d, 0, 1)
    sky[..., 3] = 255
    img = Image.fromarray(sky.astype(np.uint8), 'RGBA')
    stars = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(stars)
    for _ in range(170):
        sx, sy = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.choice([0.8, 1.1, 1.5, 2.2], p=[0.5, 0.3, 0.15, 0.05])
        al = int(rng.uniform(90, 230))
        ds.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(220, 230, 255, al))
    img.alpha_composite(stars.filter(ImageFilter.GaussianBlur(0.6)))

    # The supernova on the right: gold core, blue halo.
    img.alpha_composite(radial(905, 330, 470, (90, 140, 230), 120))
    img.alpha_composite(radial(905, 330, 260, (255, 190, 90), 150))
    sn = glow_lines('supernova', 600, (255, 236, 200), 1.25)
    add_glow(img, sn, (905 - sn.width // 2, 330 - sn.height // 2), 14, 1.6)
    img.alpha_composite(radial(905, 330, 120, (255, 248, 230), 235))

    # A beam of light from the star to the person.
    beam = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(beam)
    db.polygon([(860, 300), (860, 360), (330, 300), (330, 285)], fill=(150, 190, 255, 70))
    img.alpha_composite(beam.filter(ImageFilter.GaussianBlur(18)))

    # The person on the left, drawn in light, with a glowing heart.
    pe = glow_lines('person', 600, (225, 235, 255), 1.4)
    px, py = 300 - pe.width // 2, 430 - pe.height // 2
    add_glow(img, pe, (px, py), 10, 1.3)
    img.alpha_composite(radial(300, 430 - int(pe.height * 0.19), 70, (255, 210, 120), 230))

    # Text: small line on top, two big words below, gold on the key word.
    f_small = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-700.ttf'), 40)
    f_big = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-900.ttf'), 132)
    td = ImageDraw.Draw(img)

    def text(xy, s, font, fill, stroke=8, anchor='la', spacing=0):
        shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text(xy, s, font=font, fill=(0, 0, 0, 230), stroke_width=stroke + 6, stroke_fill=(0, 0, 0, 230), anchor=anchor)
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(img).text(xy, s, font=font, fill=fill, stroke_width=stroke, stroke_fill=(10, 12, 20), anchor=anchor)

    text((640, 54), 'THE IRON IN YOUR BLOOD WAS', f_small, (210, 225, 255), stroke=4, anchor='mt')
    text((640, 102), 'FORGED', f_big, (255, 255, 255), anchor='mt')
    text((640, 236), 'IN STARS', f_big, (255, 196, 84), anchor='mt')

    img.convert('RGB').save(a.out, quality=95)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
