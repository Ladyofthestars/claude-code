"""Joins the stills listed in <dir>/index.json into labelled contact sheets (4 x 3 per sheet)."""
import json
import os
import sys

from PIL import Image, ImageDraw

d = sys.argv[1]
index = json.load(open(os.path.join(d, 'index.json')))
first = Image.open(index[0]['file'])
landscape = first.width > first.height
cols, rows, tw, th, pad, bar = (3, 4, 480, 270, 8, 26) if landscape else (4, 3, 270, 480, 8, 26)
per = cols * rows
for s in range(0, len(index), per):
    batch = index[s:s + per]
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, rows * (th + bar + pad) + pad), (60, 60, 60))
    draw = ImageDraw.Draw(sheet)
    for i, e in enumerate(batch):
        im = Image.open(e['file']).convert('RGB').resize((tw, th))
        x = pad + (i % cols) * (tw + pad)
        y = pad + (i // cols) * (th + bar + pad)
        sheet.paste(im, (x, y + bar))
        # Mark the unsafe top 8% and bottom 18% so they are easy to check (vertical videos).
        if not landscape:
            draw.line([(x, y + bar + th * 0.08), (x + tw, y + bar + th * 0.08)], fill=(255, 80, 80), width=1)
            draw.line([(x, y + bar + th * 0.82), (x + tw, y + bar + th * 0.82)], fill=(255, 80, 80), width=1)
        draw.text((x + 4, y + 6), f"{e['frame']}  {e['label']}"[:70], fill=(255, 255, 255))
    out = os.path.join(d, f'sheet_{s // per + 1:02d}.jpg')
    sheet.save(out, quality=88)
    print(out)
