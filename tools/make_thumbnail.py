"""Builds the YouTube thumbnail (1280x720) for "You Are Made of Stars": the person from the video,
filled with stars and glowing nebula against a black sky, next to the words "YOU ARE STARDUST".

Usage: python tools/make_thumbnail.py OUT.png --font-dir DIR
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
IMG = 'public/videos/made-of-stars/images'
rng = np.random.default_rng(7)


def noise(scale, size=(H, W)):
    """Smooth random field in 0..1: random pixels at a coarse scale, scaled up smoothly."""
    h, w = max(2, size[0] // scale), max(2, size[1] // scale)
    small = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8), 'L')
    big = small.resize((size[1], size[0]), Image.BICUBIC).filter(ImageFilter.GaussianBlur(scale / 3))
    a = np.asarray(big).astype(np.float32) / 255
    return (a - a.min()) / (a.max() - a.min() + 1e-6)


def fbm(size=(H, W)):
    total, amp, norm = 0, 1.0, 0
    for s in (160, 80, 40, 20, 10):
        total = total + amp * noise(s, size)
        norm += amp
        amp *= 0.55
    return total / norm


def palette(t):
    """Map 0..1 to deep blue -> violet -> magenta -> warm gold."""
    stops = np.array([0.0, 0.35, 0.6, 0.8, 1.0])
    cols = np.array([(6, 10, 40), (40, 40, 140), (120, 60, 190), (230, 110, 170), (255, 210, 130)], np.float32)
    out = np.zeros(t.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(t, stops, cols[:, c])
    return out


def stars(n, mask=None, big=0.04, color=(235, 240, 255)):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    placed = 0
    while placed < n:
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        if mask is not None and mask[int(y), int(x)] < 0.5:
            continue
        r = rng.choice([0.7, 1.0, 1.4, 2.0, 3.0], p=[0.45, 0.3, 0.15, 0.1 - big, big])
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (int(rng.uniform(120, 255)),))
        placed += 1
    return layer


def sparkle(layer, x, y, size, color=(255, 245, 225)):
    """A bright star with four soft rays."""
    d = ImageDraw.Draw(layer)
    for i in range(size, 0, -1):
        a = int(255 * (1 - i / size) ** 2.2)
        d.line((x - i * 2.2, y, x + i * 2.2, y), fill=color + (a // 3,), width=1)
        d.line((x, y - i * 2.2, x, y + i * 2.2), fill=color + (a // 3,), width=1)
    d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=color + (255,))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--font-dir', required=True)
    a = ap.parse_args()

    # Black sky with a faint violet haze and a few stars.
    haze = fbm()
    sky = palette(haze * 0.42) * (0.35 + 0.65 * haze[..., None])
    y, x = np.mgrid[0:H, 0:W]
    vign = np.clip(1.15 - np.sqrt(((x - 400) / 900) ** 2 + ((y - 360) / 600) ** 2), 0.25, 1)
    img = Image.fromarray(np.clip(sky * 0.55 * vign[..., None], 0, 255).astype(np.uint8)).convert('RGBA')
    img.alpha_composite(stars(220).filter(ImageFilter.GaussianBlur(0.5)))

    # The person from the video, as a mask.
    src = Image.open(os.path.join(IMG, 'person.png')).convert('RGBA')
    src = src.crop(src.getbbox())
    ph = 660
    src = src.resize((int(src.width * ph / src.height), ph), Image.LANCZOS)
    px, py = 330 - src.width // 2, H - ph - 20
    m = Image.new('L', (W, H), 0)
    m.paste(src.getchannel('A'), (px, py))
    m = m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    mask = np.asarray(m).astype(np.float32) / 255

    # Glow around the figure.
    for r, s, col in ((60, 0.55, (90, 110, 255)), (22, 0.8, (170, 150, 255)), (6, 0.9, (225, 230, 255))):
        g = np.asarray(m.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
        lay = np.zeros((H, W, 4), np.float32)
        lay[..., :3] = col
        lay[..., 3] = np.clip(g * 255 * s * 1.6, 0, 255)
        img.alpha_composite(Image.fromarray(lay.astype(np.uint8), 'RGBA'))

    # Inside the figure: a bright nebula, brightest at the heart.
    neb = fbm()
    hx, hy = px + src.width * 0.5, py + ph * 0.36
    neb = np.clip((neb - 0.28) / 0.5, 0, 1) ** 1.3
    heart = np.exp(-(((x - hx) / 75) ** 2 + ((y - hy) / 85) ** 2))
    t = np.clip(0.12 + neb * 0.78 + heart * 0.3, 0, 1)
    body = palette(t) * (0.3 + 0.7 * neb[..., None]) + heart[..., None] * np.array([255, 215, 150]) * 0.4
    inside = np.zeros((H, W, 4), np.float32)
    inside[..., :3] = np.clip(body, 0, 255)
    inside[..., 3] = mask * 255
    img.alpha_composite(Image.fromarray(inside.astype(np.uint8), 'RGBA'))
    img.alpha_composite(stars(420, mask=mask, big=0.06).filter(ImageFilter.GaussianBlur(0.4)))

    # The robe's ink lines, drawn faintly in light so it reads as the same person as in the video.
    a_ = np.asarray(src).astype(np.float32)
    lum = a_[..., :3].mean(axis=2)
    lines = np.clip((200 - lum) / 160.0, 0, 1) * (a_[..., 3] / 255.0)
    ll = np.zeros(a_.shape, np.float32)
    ll[..., :3] = (215, 225, 255)
    ll[..., 3] = lines * 120
    img.alpha_composite(Image.fromarray(ll.astype(np.uint8), 'RGBA'), (px, py))

    # A star glowing at the heart, and stardust drifting off the figure to the right.
    hl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sparkle(hl, int(hx), int(hy), 46)
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(1.5)))
    img.alpha_composite(hl)
    dust = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(140):
        u = rng.random() ** 1.6
        sx = px + src.width * 0.75 + u * 420 + rng.normal(0, 18)
        sy = py + ph * 0.25 - u * 160 + rng.normal(0, 40 + 60 * u)
        r = rng.choice([0.8, 1.2, 1.8, 2.6], p=[0.4, 0.3, 0.2, 0.1]) * (1.1 - u * 0.5)
        dd.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 225, 170, int(255 * (1 - u * 0.75))))
    img.alpha_composite(dust.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(dust)

    # Text: "YOU ARE" in white, "STARDUST" big in glowing gold.
    f_mid = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-900.ttf'), 92)
    f_big = ImageFont.truetype(os.path.join(a.font_dir, 'Montserrat-900.ttf'), 112)
    cx = 905

    def shadow(xy, s, font, blur=14, alpha=230, stroke=10):
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text(xy, s, font=font, fill=(0, 0, 0, alpha), stroke_width=stroke, stroke_fill=(0, 0, 0, alpha), anchor='mm')
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))

    def glow(xy, s, font, color, blur, alpha):
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).text(xy, s, font=font, fill=color + (alpha,), stroke_width=6, stroke_fill=color + (alpha,), anchor='mm')
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))

    y1, y2 = 282, 392
    shadow((cx, y1), 'YOU ARE', f_mid)
    ImageDraw.Draw(img).text((cx, y1), 'YOU ARE', font=f_mid, fill=(255, 255, 255), stroke_width=5, stroke_fill=(8, 8, 20), anchor='mm')

    shadow((cx, y2), 'STARDUST', f_big)
    glow((cx, y2), 'STARDUST', f_big, (255, 170, 60), 26, 200)
    # Gold gradient fill, light at the top and deep at the bottom.
    tm = Image.new('L', (W, H), 0)
    ImageDraw.Draw(tm).text((cx, y2), 'STARDUST', font=f_big, fill=255, anchor='mm')
    bb = tm.getbbox()
    grad = np.zeros((H, W, 4), np.float32)
    k = np.clip((y - bb[1]) / (bb[3] - bb[1]), 0, 1)[..., None]
    grad[..., :3] = (1 - k) * np.array([255, 240, 170]) + k * np.array([240, 150, 40])
    grad[..., 3] = 255
    outline = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(outline).text((cx, y2), 'STARDUST', font=f_big, fill=(0, 0, 0, 0), stroke_width=5, stroke_fill=(30, 14, 4, 255), anchor='mm')
    img.alpha_composite(outline)
    img.paste(Image.fromarray(grad.astype(np.uint8), 'RGBA'), (0, 0), tm)

    img.convert('RGB').save(a.out, quality=95)
    print('wrote', a.out, 'text box', bb)


if __name__ == '__main__':
    main()
