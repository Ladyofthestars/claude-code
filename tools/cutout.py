"""Cut a picture out of its plain, flat background.

Works for line drawings on a single flat colour (no AI model needed):
  - finds the background colour from the image border
  - finds the drawn object, fills its inside so it stays solid, and drops stray specks
  - writes an RGBA PNG plus the object's bounding box for the video settings

Usage:
  python tools/cutout.py IN.png OUT.png [--mode keep|ink] [--ink #1d2440] [--paper #ffffff]

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
    ap.add_argument('--mode', default='keep', choices=['keep', 'ink'])
    ap.add_argument('--ink', default='#1d2440')
    ap.add_argument('--paper', default='#ffffff')
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

    # Solid silhouette of the drawn object.
    marks = (dist > lo).astype(np.uint8)
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
    solid = cv2.dilate(solid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    alpha = cv2.GaussianBlur(solid.astype(np.float32), (0, 0), 1.2)
    alpha = np.clip(alpha, 0, 1)

    if a.mode == 'keep':
        out_rgb = rgb
    else:
        ink, paper = hex_rgb(a.ink), hex_rgb(a.paper)
        s = strength[..., None]
        out_rgb = paper * (1 - s) + ink * s

    rgba = np.dstack([np.clip(out_rgb, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(a.dst, optimize=True)

    ys, xs = np.where(alpha > 0.5)
    content = [round(xs.min() / w, 4), round(ys.min() / h, 4), round((xs.max() + 1) / w, 4), round((ys.max() + 1) / h, 4)]
    print(json.dumps({'aspect': round(w / h, 5), 'content': content, 'background': [int(v) for v in bg], 'kept_parts': len(keep), 'dropped_parts': int(n - 1 - len(keep))}))


if __name__ == '__main__':
    main()
