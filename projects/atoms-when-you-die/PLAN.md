# PLAN: "What Happens to Your Atoms When You Die?" (video 2, about 10 minutes)

Follow-up to "Almost Every Atom in You Is Older Than the Earth" (video 1), made the same way, with three changes the user asked for:
- **Voice:** open source from now on (Kokoro, Apache 2.0), voice A: am_michael 70% + am_onyx 30%, speed 1.02. Chosen as the closest free match to Brian by voice print, depth and pace. Brian himself is not cloned (his voice belongs to a voice actor licensed to ElevenLabs).
- **Look:** more captivating: deep blue page, glowing white lines and text, gold highlights, atoms as glowing dots that flow between things.
- **Music:** the subtle piano bed the user approved for video 1.

Tick each box as it is done. If work stops, continue from the first unticked box.

## Step 1: plan and script
- [x] Research facts from primary sources (OpenStax Chemistry, Biology, Anatomy & Physiology, Astronomy; Science News; Marcus Aurelius, *Meditations*)
- [x] `facts.md`: every fact with its source (37 facts)
- [x] `script.md`: narration (1,469 words: opening + 7 chapters + ending), shot list for every sentence, picture list, style line

## Step 2: pictures
- [ ] Generate the 21 new pictures (Gemini, free), same style line as video 1
- [ ] Cut out backgrounds; check each (text, colour, cut-off edges, style); remake failures (twice at most)
- [ ] White-line versions of all pictures for the blue page (new + 11 reused)
- [ ] `images/prompts.md` with every prompt used

## Step 3: voice
- [ ] Kokoro setup script in the repo (so later sessions can recreate it)
- [ ] One paragraph at a time, word timings, joined with natural pauses per part
- [ ] Check word for word against `script.md`

## Step 4: animation
- [ ] Template: blue theme (gradient page, glowing white ink, text glow, drifting light dust) and atom streams
- [ ] Settings for each part (9 parts), following the shot list
- [ ] Frame check passes for every part
- [ ] Stills review and fixes
- [ ] Render, join, music, mix, loudness
- [ ] Final checks

## Step 5: packaging
- [ ] Thumbnail (the star-filled figure from video 1, now dissolving into stardust)
- [ ] Title, description, chapters, tags (`youtube.md`)
- [ ] Copy under 100 MB; commit and push; send to the user
