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
- [x] Generate the 21 new pictures (Gemini, free), same style line as video 1
- [x] Cut out backgrounds; check each (text, colour, cut-off edges, style); remake failures (twice at most): lungs, roman_bust, marcus_bust, statue, planetary_nebula remade once
- [x] White-line versions of all pictures for the blue page (new + 11 reused)
- [x] `images/prompts.md` with every prompt used

## Step 3: voice
- [x] Kokoro setup script in the repo (so later sessions can recreate it)
- [x] One paragraph at a time, word timings, joined with natural pauses per part
- [x] Check word for word against `script.md` (timings), and proof-listened with speech recognition (`tools/proof_listen.py`): no real errors. Total 8:48.8

## Step 4: animation
- [x] Template: blue theme (gradient page, glowing white ink, text glow, drifting light dust) and atom streams
- [x] Settings for each part (9 parts), following the shot list
- [x] Frame check passes for every part
- [x] Stills review and fixes
- [x] Render, join, music, mix, loudness
- [x] Final checks

## Step 5: packaging
- [x] Thumbnail (the star-filled figure from video 1, now dissolving into stardust)
- [x] Title, description, chapters, tags (`youtube.md`)
- [x] Copy under 100 MB; commit and push; send to the user
