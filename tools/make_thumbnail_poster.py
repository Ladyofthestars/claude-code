"""Builds a 1280x720 YouTube thumbnail from one square painting (made with the free Gemini image
model) plus big, sharp text: the painting sits on one side, its colours are stretched softly across
the rest of the frame with fresh stars, and two lines of text (white, then glowing gold) fill the
open side.

Usage:
  python tools/make_thumbnail_poster.py ART.jpg OUT.png --side left|right --top "IT'S NOT" --big "THE END"  (use | in --big for two gold lines)
                                        --font-dir DIR [--scale 1.0] [--shift-y 0]
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import make_thumbnail as mt  # noqa: E402

W, H = 1280, 720


def fit_font(path, text, max_w, start):
    size = start
    while size > 30:
        f = ImageFont.truetype(path, size)
        x0, y0, x1, y1 = f.getbbox(text)
        if x1 - x0 <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(path, size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('art')
    ap.add_argument('out')
    ap.add_argument('--side', choices=['left', 'right'], required=True, help='where the painting goes')
    ap.add_argument('--top', required=True)
    ap.add_argument('--big', required=True)
    ap.add_argument('--font-dir', required=True)
    ap.add_argument('--scale', type=float, default=1.0, help='painting height as a multiple of 720')
    ap.add_argument('--shift-y', type=int, default=0, help='move the painting up (negative) or down')
    a = ap.parse_args()

    art = Image.open(a.art).convert('RGB')
    art = ImageEnhance.Contrast(art).enhance(1.12)
    art = ImageEnhance.Color(art).enhance(1.15)
    side = int(H * a.scale)
    art = art.resize((side, side), Image.LANCZOS)

    # Background: the painting's own colours, stretched and blurred across the frame, darkened.
    bg = art.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(60))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    # Pull it toward the series' deep blue so the open side never turns muddy.
    yy0, xx0 = np.mgrid[0:H, 0:W]
    glow = np.clip(1 - np.sqrt(((xx0 - W / 2) / 900) ** 2 + ((yy0 - H * 0.45) / 520) ** 2), 0, 1)
    navy = np.zeros((H, W, 3), np.float32)
    navy[..., 0] = 8 + 22 * glow
    navy[..., 1] = 18 + 40 * glow
    navy[..., 2] = 44 + 90 * glow
    bg = Image.fromarray(np.clip(0.5 * np.asarray(bg, np.float32) + 0.5 * navy, 0, 255).astype(np.uint8))
    img = bg.convert('RGBA')
    img.alpha_composite(mt.stars(240).filter(ImageFilter.GaussianBlur(0.5)))

    # The sharp painting, feathered into the background on its open side.
    x = 0 if a.side == 'left' else W - side
    y = (H - side) // 2 + a.shift_y
    mask = np.ones((side, side), np.float32)
    feather = int(side * 0.28)
    ramp = np.linspace(0, 1, feather) ** 1.4
    if a.side == 'left':
        mask[:, side - feather:] *= ramp[::-1][None, :]
    else:
        mask[:, :feather] *= ramp[None, :]
    m = Image.fromarray((mask * 255).astype(np.uint8))
    img.paste(art, (x, y), m)

    # A soft dark pool behind the text for contrast.
    yy, xx = np.mgrid[0:H, 0:W]
    tx = W - 330 if a.side == 'left' else 330
    pool = np.exp(-(((xx - tx) / 420) ** 2 + ((yy - 360) / 300) ** 2))
    dark = np.zeros((H, W, 4), np.float32)
    dark[..., 3] = pool * 150
    img.alpha_composite(Image.fromarray(dark.astype(np.uint8), 'RGBA'))

    font = os.path.join(a.font_dir, 'Montserrat-900.ttf')
    max_w = 600
    bigs = a.big.split('|')
    f_top = fit_font(font, a.top, max_w, 104)
    f_big = min((fit_font(font, b, max_w, 150) for b in bigs), key=lambda f: f.size)
    cx = tx
    step = int(f_big.size * 1.02)
    block = f_top.size * 1.1 + step * len(bigs)
    ty = int(360 - block / 2 + f_top.size * 0.5)
    bys = [int(ty + f_top.size * 0.62 + step * (k + 0.5)) for k in range(len(bigs))]

    def shadow(xy, s, f, blur=14, alpha=230, stroke=10):
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text(xy, s, font=f, fill=(0, 0, 0, alpha), stroke_width=stroke, stroke_fill=(0, 0, 0, alpha), anchor='mm')
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))

    def gold(xy, s, f):
        g2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g2).text(xy, s, font=f, fill=(255, 170, 60, 210), stroke_width=8, stroke_fill=(255, 170, 60, 210), anchor='mm')
        img.alpha_composite(g2.filter(ImageFilter.GaussianBlur(26)))
        tm = Image.new('L', (W, H), 0)
        ImageDraw.Draw(tm).text(xy, s, font=f, fill=255, anchor='mm')
        bb = tm.getbbox()
        k = np.clip((yy - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)[..., None]
        grad = np.zeros((H, W, 4), np.float32)
        grad[..., :3] = (1 - k) * np.array([255, 242, 175]) + k * np.array([242, 148, 36])
        grad[..., 3] = 255
        ol = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ol).text(xy, s, font=f, fill=(0, 0, 0, 0), stroke_width=6, stroke_fill=(30, 14, 4, 255), anchor='mm')
        img.alpha_composite(ol)
        img.paste(Image.fromarray(grad.astype(np.uint8), 'RGBA'), (0, 0), tm)

    shadow((cx, ty), a.top, f_top)
    ImageDraw.Draw(img).text((cx, ty), a.top, font=f_top, fill=(255, 255, 255), stroke_width=6, stroke_fill=(8, 8, 20), anchor='mm')
    for b, by in zip(bigs, bys):
        shadow((cx, by), b, f_big)
        gold((cx, by), b, f_big)
    img.convert('RGB').save(a.out, quality=95)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
