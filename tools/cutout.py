"""Cut a picture out of its plain, flat background.

Works for line drawings on a single flat colour (no AI model needed):
  - finds the background colour from the image border
  - finds the drawn object, fills its inside so it stays solid, and drops stray specks
  - writes an RGBA PNG plus the object's bounding box for the video settings

Usage:
  python tools/cutout.py IN.png OUT.png [--mode keep|ink] [--ink #1d2440] [--paper #ffffff] [--gamma 1.12]

  keep: keep the original colours (for pages the same colour as the picture background)
  ink:  redraw the lines in --ink on --paper (for light pages)

Prints one JSON line: {"aspect": ..., "content": [left, top, right, bottom]}
"""
import argparse
import json

import cv2
import numpy as np
from PIL import Image


def hex_rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    # soft: for clouds and haze. No solid outline; the shading itself sets the transparency.
    ap.add_argument('--mode', default='keep', choices=['keep', 'ink', 'soft'])
    ap.add_argument('--ink', default='#1d2440')
    ap.add_argument('--paper', default='#ffffff')
    ap.add_argument('--gamma', type=float, default=1.12, help='ink tone curve; below 1 brings out soft shading')
    a = ap.parse_args()

    rgb = np.asarray(Image.open(a.src).convert('RGB')).astype(np.float32)
    h, w, _ = rgb.shape
    b = max(4, int(min(h, w) * 0.01))
    border = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3), rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
    bg = np.median(border, axis=0)

    dist = np.linalg.norm(rgb - bg, axis=2)
    noise = np.percentile(np.linalg.norm(border - bg, axis=1), 99)
    lo = max(10.0, noise * 1.5)
    strength = np.clip((dist - lo) / 55.0, 0, 1)

    if a.mode == 'soft':
        # Luminance difference from the paper, smoothed, becomes the ink's opacity.
        lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
        # Paper tone measured locally (a wide max-filter ignores the strokes), so uneven paper isn't ink.
        k = max(15, int(min(h, w) * 0.06)) | 1
        paper = cv2.GaussianBlur(cv2.dilate(lum, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))), (0, 0), k / 3)
        diff = np.clip(paper - lum, 0, 255)
        diff = cv2.GaussianBlur(diff, (0, 0), 1.0)
        soft_lo = max(6.0, noise * 0.8)
        top = max(soft_lo + 1, np.percentile(diff, 99.7))
        alpha = np.clip((diff - soft_lo) / (top - soft_lo), 0, 1) ** a.gamma
        ink = hex_rgb(a.ink)
        rgba = np.dstack([np.broadcast_to(ink, rgb.shape), alpha * 255]).astype(np.uint8)
        rgba[alpha <= 0.002] = 0
        Image.fromarray(rgba, 'RGBA').save(a.dst, optimize=True)
        ys, xs = np.where(alpha > 0.08)
        content = [round(xs.min() / w, 4), round(ys.min() / h, 4), round((xs.max() + 1) / w, 4), round((ys.max() + 1) / h, 4)]
        print(json.dumps({'aspect': round(w / h, 5), 'content': content, 'background': [int(v) for v in bg], 'kept_parts': 1, 'dropped_parts': 0}))
        return

    # Solid silhouette of the drawn object.
    marks = (dist > lo).astype(np.uint8)
    # Drop loose specks of background texture before joining strokes together.
    n0, lab0, st0, _ = cv2.connectedComponentsWithStats(marks, 8)
    big = np.zeros(n0, bool)
    big[1:] = st0[1:, cv2.CC_STAT_AREA] >= max(30, h * w * 0.00004)
    marks = big[lab0].astype(np.uint8)
    k = max(3, int(min(h, w) * 0.025)) | 1
    closed = cv2.morphologyEx(marks, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(closed, 8)
    if n <= 1:
        raise SystemExit('No object found')
    areas = stats[1:, cv2.CC_STAT_AREA]
    keep = [i + 1 for i, ar in enumerate(areas) if ar >= areas.max() * 0.02]
    solid = np.isin(labels, keep).astype(np.uint8)
    # Fill holes: everything not reachable from the border is inside the object.
    inv = (1 - solid).astype(np.uint8)
    ff = inv.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 2)
    solid = np.where(ff == 2, 0, 1).astype(np.uint8)
    # Smooth the outline: shave off small bumps, then grow back slightly so no stroke is clipped.
    ko = max(5, int(min(h, w) * 0.012)) | 1
    solid = cv2.morphologyEx(solid, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ko, ko)))
    solid = cv2.dilate(solid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    alpha = cv2.GaussianBlur(solid.astype(np.float32), (0, 0), 1.2)
    alpha = np.clip(alpha, 0, 1)

    if a.mode == 'keep':
        out_rgb = rgb
    else:
        ink, paper = hex_rgb(a.ink), hex_rgb(a.paper)
        # Map the drawing's tones onto ink without flattening bright areas into solid ink:
        # scale to the object's own brightest strokes and keep some paper showing through.
        inside = solid.astype(bool)
        top = np.percentile(dist[inside], 99.5) if inside.any() else 255.0
        tone = np.clip((dist - lo) / max(1.0, top - lo), 0, 1) ** a.gamma * 0.93
        s = tone[..., None]
        out_rgb = paper * (1 - s) + ink * s

    rgba = np.dstack([np.clip(out_rgb, 0, 255), alpha * 255]).astype(np.uint8)
    rgba[alpha <= 0.002] = 0  # fully clear pixels carry no colour, so files stay small
    Image.fromarray(rgba, 'RGBA').save(a.dst, optimize=True)

    ys, xs = np.where(alpha > 0.5)
    content = [round(xs.min() / w, 4), round(ys.min() / h, 4), round((xs.max() + 1) / w, 4), round((ys.max() + 1) / h, 4)]
    print(json.dumps({'aspect': round(w / h, 5), 'content': content, 'background': [int(v) for v in bg], 'kept_parts': len(keep), 'dropped_parts': int(n - 1 - len(keep))}))


if __name__ == '__main__':
    main()
