# PLAN: "You've Never Actually Touched Anything" (video 3, about 9 minutes)

Video 3 of the "made of stars" series, made the same way as video 2: open-source channel voice (Kokoro, voice A), the blue glowing look, original subtle music, every fact sourced.

Tick each box as it is done. If work stops, continue from the first unticked box.

## Step 1: plan and script
- [x] Research facts from primary sources (OpenStax Chemistry, University Physics, College Physics, Anatomy & Physiology, Astronomy; NASA Chandra; UN; Epictetus, *Enchiridion*)
- [x] `facts.md`: every fact with its source (25 facts)
- [x] `script.md`: narration (1,355 words: opening + 7 chapters + ending), shot list, picture list, style line

## Step 2: pictures
- [ ] Generate the 18 new pictures (Gemini, free), same style line
- [ ] Cut out, check each, remake failures (twice at most)
- [ ] Glowing white-line versions for the blue page (new + reused)
- [ ] `images/prompts.md`

## Step 3: voice
- [ ] Record every paragraph with the channel voice (`tools/voice_kokoro.py`)
- [ ] Join into parts with pauses; check word for word; proof-listen (`tools/proof_listen.py`)

## Step 4: animation
- [ ] Builder for the 9 parts (`tools/build_never_touched.py`), following the shot list
- [ ] Frame check, empty-moment check and label check pass for every part
- [ ] Stills review and fixes
- [ ] Render, join, music, mix, loudness; final checks

## Step 5: packaging
- [ ] Thumbnail in the series style
- [ ] Title, description, chapters, tags (`youtube.md`)
- [ ] Copy under 100 MB; commit and push; send to the user
