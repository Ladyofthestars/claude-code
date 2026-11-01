# Video template

A reusable Remotion template for short vertical explainer videos (1080×1920, 60 fps).
Each video is one folder in `public/videos/<name>/` with:

- `settings.json`: the pictures, where they sit on the page, the camera, lines, lights, magnifiers, labels and all timings
- `images/`: the cut-out pictures
- `narration.mp3` and `words.json`: the voice and the time of every word

The video is as long as the voice plus `tailSeconds`.

## Make a new video

1. Copy `public/videos/new-earth` to `public/videos/<new-name>` and replace the pictures, voice and `words.json`.
2. Cut pictures out of a flat background:
   `python tools/cutout.py raw.png public/videos/<new-name>/images/name.png --mode ink`
   It prints the `aspect` and `content` box to paste into `settings.json`.
3. Edit `settings.json`. Times are written against the narration, for example:
   - `"3:small light"`: when "small light" starts in line 3
   - `"3:small light@end"`: when it ends
   - `"4:Fear-0.4"`: 0.4 s before "Fear"
   - `"start"`, `"end"`
4. Check every frame for pictures cut off at the edge, or inside the top 8% / bottom 18%:
   `npx tsx tools/check.ts <new-name>`
5. Render review stills (every half second and every line start) as contact sheets:
   `npx tsx tools/stills.ts <new-name>`
6. Render:
   `npx remotion render Video out/video.mp4 --props='{"video":"<new-name>"}'`

## How things move

- **One camera** films the whole page. Camera keys either frame items (`focus` + `fit`) or set `x`, `y`, `zoom`. Moves are interpolated so each one starts slowly, speeds up and settles, and moves flow into each other without overshooting. Repeat a framing to hold.
- **Depth**: items with `depth` above 1 move slower than the page and are slightly blurred.
- **Fades**: everything fades in and out over half a second with a little scale and blur. Lines draw themselves on.
- **Lights** are soft glows. They travel along a traced `path` on a picture or along a `thread`, or glow in place at `at` / `points`.
- **Magnifiers** grow out of a detail and stay joined to it by two lines.
- **Labels** are bold, uppercase and widely spaced.
