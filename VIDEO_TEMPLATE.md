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

## Long videos in parts

A long video is a folder of parts: `public/videos/<video>/p0`, `p1`, … Each part has its own `settings.json`, `narration.mp3`/`.wav` and `words.json`, and is rendered on its own. Parts join seamlessly when each part starts with the camera where the previous one ended (`tools/build_made_of_stars.py` does this automatically).

- `tools/assemble_voice.py`: joins paragraph recordings into one narration per part, with natural pauses and word timings (it checks them word for word against the script).
- `tools/render_parts.sh <video>`: renders every part to `out/<video>/pN.mp4`.
- `tools/finish_video.py <video> [swells]`: joins the parts, adds the generated music bed (`tools/make_music.py`) and soft swells, ducks the music under the voice and normalises loudness for YouTube (-14 LUFS).

Settings can also use, beyond the short-video features:
- `size`: frame size, e.g. `{"width": 1920, "height": 1080}`
- `drawings`: diagrams that draw themselves (`path` with points, `circle`, `rect`, with `arrow`, `curve`, `dashed`, `fill`)
- labels with `count` (numbers that count up, `{n}` in the text), `align: "left"`, `upper: false`
- lights that travel along a `drawing` (optionally `reverse`) or glow at page points (`worldPoints`)
- picture paths starting with `/` are read from the public folder, so parts can share one `images` folder

## How things move

- **One camera** films the whole page. Camera keys either frame items (`focus` + `fit`) or set `x`, `y`, `zoom`. Moves are interpolated so each one starts slowly, speeds up and settles, and moves flow into each other without overshooting. Repeat a framing to hold.
- **Depth**: items with `depth` above 1 move slower than the page and are slightly blurred.
- **Fades**: everything fades in and out over half a second with a little scale and blur. Lines draw themselves on.
- **Lights** are soft glows. They travel along a traced `path` on a picture or along a `thread`, or glow in place at `at` / `points`.
- **Magnifiers** grow out of a detail and stay joined to it by two lines.
- **Labels** are bold, uppercase and widely spaced.
- **Nothing is ever cut off**: anything that nears the edge of the safe area fades out smoothly, and fades back in when the camera returns.

## Dark pages, atom streams and the open-source voice (from video 2)

Theme extras (all optional; leave them out and nothing changes):
- `backgroundImage`: a CSS gradient over the background colour, fixed to the screen (a soft centre light and a vignette).
- `labelGlow`, `drawingGlow`: a soft glow around labels and drawn lines (CSS colours).
- `dust`: `{count, color, size, parallax, drift}`: drifting, twinkling specks of light behind everything. They follow the camera at `parallax` and the whole video's clock, so set `clock` in each part's settings (seconds since the video started) and parts join without a jump.
- Use `lightBlend: "screen"` on dark pages so glows add light.

`streams`: flows of small glowing dots ("atoms") along a path on the page, looping while they are on: `{points, curve, from, to, count, period, size, spread, color, reverse}`. In the builder: `p.stream(points, at, to, ...)`.

Pictures for a dark page: `tools/blueprint.py IN.png OUT.png` turns an ink cut-out into glowing light lines over a see-through dark fill (glow baked in).

Voice (open source, from video 2 on): `tools/setup_voice.sh DIR` installs Kokoro (Apache 2.0) in a Python 3.12 environment; `DIR/bin/python tools/voice_kokoro.py projects/<video>/script.md CLIPS` records every paragraph with word timings; `tools/assemble_voice.py --clips CLIPS --source "..."` joins them per part; `tools/proof_listen.py CLIPS` proof-listens with speech recognition and lists anything that differs from the script.

Time references: avoid phrases that end in a hyphen and a number, such as "carbon-14": "-14" reads as "14 seconds earlier". Use a neighbouring phrase instead.
