# PLAN: "You Are Made of Stars" (10-minute YouTube video)

Topic chosen because no topic was given: where every atom in your body came from. It is fully fact-based, fits the channel's tone after "The New Earth", and reuses the short's Earth, person and hand pictures.

Tick each box as it is done. If work stops, continue from the first unticked box.

## Step 1: plan and script
- [x] Check what's available: Higgsfield (0 credits, free plan, so no GPT Image 2.5), ElevenLabs (works, but the key can't read the voice library), web (direct downloads work)
- [x] Research facts from primary sources (NASA, OpenStax, ESO, SDSS)
- [x] `facts.md`: every number and fact, with its source
- [x] `script.md`: narration (~1,500 words, opening + 7 chapters + ending), shot list for every sentence, picture list, style line
- [x] Word count (1,413 words, 139 sentences, 38 paragraphs), and no hype words

## Step 2: pictures
- [x] Generate 17 new pictures (Nano Banana 2 Lite via the Gemini connector, because Higgsfield has no credits)
- [x] Cut out backgrounds (tools/cutout.py), save to `images/`
- [x] Check each picture: text, colour, cut-off edges, style. Remake failures (twice at most): bone x1, telescope x2, hourglass x2, nebula x1
- [x] Re-ink the 4 reused pictures (earth, person, open_hand, fist) in the same ink as the new ones
- [x] `images/prompts.md` with every prompt used

## Step 3: voice
- [x] ElevenLabs, voice Brian (calm, deep), one paragraph at a time, same settings, stitched with previous/next text
- [x] Join paragraphs with natural pauses; one audio file + word timings per part
- [x] Check word for word against script.md (1,499 words; total 9:28.7 with pauses). Added four sourced passages (facts 38–42) to reach about 10 minutes

## Step 4: animation
- [x] Template: any frame size (1920x1080), multi-part videos, counting numbers, self-drawing diagrams, lights on diagrams
- [x] Check tool: also reports gaps of more than 5 s with nothing new on screen
- [x] Settings for each part (9 parts), following the shot list
- [x] Frame check passes for every part (template now fades anything out before it could be cut off)
- [ ] Stills every half second and at every sentence start; review and fix
- [ ] Background music (original, generated here) and a few soft sound effects
- [ ] Render all parts, join them, mix voice and music, normalise loudness for YouTube
- [ ] Final checks: length, audio, a few frames
- [ ] Commit and push
