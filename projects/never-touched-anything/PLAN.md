# PLAN: "You've Never Actually Touched Anything" (video 3, about 9 minutes)

Video 3 of the "made of stars" series, made the same way as video 2: open-source channel voice (Kokoro, voice A), the blue glowing look, original subtle music, every fact sourced.

Tick each box as it is done. If work stops, continue from the first unticked box.

## Step 1: plan and script
- [x] Research facts from primary sources (OpenStax Chemistry, University Physics, College Physics, Anatomy & Physiology, Astronomy; NASA Chandra; UN; Epictetus, *Enchiridion*)
- [x] `facts.md`: every fact with its source (25 facts)
- [x] `script.md`: narration (1,355 words: opening + 7 chapters + ending), shot list, picture list, style line

## Step 2: pictures
- [x] Generate the 18 new pictures (Gemini, free), same style line
- [x] Cut out, check each, remake failures (twice at most): finger_press, hands_rubbing, holding_hands, hug remade once
- [x] Glowing white-line versions for the blue page (new + reused)
- [x] `images/prompts.md`

## Step 3: voice
- [x] Record every paragraph with the channel voice (`tools/voice_kokoro.py`)
- [x] Join into parts with pauses; check word for word; proof-listen (`tools/proof_listen.py`): fixed "Geiger" (said with a J) and a clipped first word; total 8:21.8

## Step 4: animation
- [x] Builder for the 9 parts (`tools/build_never_touched.py`), following the shot list
- [x] Frame check, empty-moment check and label check pass for every part
- [x] Stills review and fixes (parts 2–8: scenes exit cleanly, bigger atoms, fixed overlapping end text, filled two empty moments)
- [x] Render, join, music, mix, loudness; final checks (30,114 frames, 8:21.9, −14.8 LUFS, true peak −1.2 dB; swells on "Not even the hand", "neutron star", "touched by everything")

## Step 5: packaging
- [x] Thumbnail in the series style
- [x] Title, description, chapters, tags (`youtube.md`)
- [ ] Copy under 100 MB; commit and push; send to the user
