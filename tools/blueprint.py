"""Turns an ink cut-out (dark lines on a solid white fill, from tools/cutout.py --mode ink) into a
picture for a dark page: glowing light lines over a see-through dark fill.

The fill keeps a little of the page out from behind the object, so it still reads as solid, but the
page's own gradient and grid show through. The soft glow is baked in, so rendering stays fast.

Usage:
  python tools/blueprint.py IN.png OUT.png [--line #eef4ff] [--fill #0a1a33] [--fill-alpha 0.55]
                            [--glow #8fb8ff] [--glow-alpha 0.55] [--glow-radius 0.012]
"""
import argparse

import numpy as np
from PIL import Image, ImageFilter


def rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--line', default='#eef4ff')
    ap.add_argument('--fill', default='#0a1a33')
    ap.add_argument('--fill-alpha', type=float, default=0.55)
    ap.add_argument('--glow', default='#8fb8ff')
    ap.add_argument('--glow-alpha', type=float, default=0.55)
    ap.add_argument('--glow-radius', type=float, default=0.012, help='as a share of the picture size')
    a = ap.parse_args()

    im = np.asarray(Image.open(a.src).convert('RGBA')).astype(np.float32)
    sil = im[..., 3] / 255
    lum = im[..., :3].mean(axis=2)
    # Line strength: 0 on the white fill, 1 on full ink.
    s = np.clip((250 - lum) / 200, 0, 1) * sil
    line, fill = rgb(a.line), rgb(a.fill)
    alpha = sil * (a.fill_alpha * (1 - s) + s)
    col = (fill * (a.fill_alpha * (1 - s))[..., None] + line * s[..., None]) / np.maximum(alpha, 1e-6)[..., None]
    body = np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.uint8)

    # Soft glow from the lines and the outline.
    r = max(2, int(a.glow_radius * max(im.shape[:2])))
    edge = np.clip(s + 0.5 * (sil - np.asarray(Image.fromarray((sil * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))) / 255), 0, 1)
    g = np.asarray(Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
    glow = np.zeros_like(im)
    glow[..., :3] = rgb(a.glow)
    glow[..., 3] = np.clip(g * 2.2, 0, 1) * a.glow_alpha * 255
    out = Image.fromarray(glow.astype(np.uint8), 'RGBA')
    out.alpha_composite(Image.fromarray(body, 'RGBA'))
    out.save(a.dst)


if __name__ == '__main__':
    main()
