# Picture prompts: "You've Never Actually Touched Anything"

**Model:** Nano Banana 2 Lite (Google Gemini) through the Gemini connector, square, 1K, free. Same style line as videos 1 and 2.

**Prompt pattern:** what it is and from which angle, then "drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges.", then the style line word for word, then the ending.

- **Style line:** Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered.
- **Ending:** plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

**Pipeline:** `tools/cutout.py raw.jpg images/NAME.png --mode ink --ink '#24262b' --paper '#ffffff'`, then `tools/blueprint.py` for the blue page.

**Reused (blue-page versions):** person, open_hand, earth (from video 2); neutron_star, sugar_cube, fist (from video 1).

**Checks:** text, colour, cut-off edges (all content boxes inside the 2% border), extra objects or frames, style. Remakes: at most two; 4 needed one remake.

## feet.png  (final: v1)

> **v1:** A pair of bare human feet standing flat, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## phone.png  (final: v1)

> **v1:** A modern smartphone standing upright, seen from the front, with a blank screen, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## holding_hands.png  (final: v2 (remake))

> **v1:** Two human hands gently holding each other, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** Two hands gently holding each other, only the hands and short wrists, small in the middle of the picture, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 had forearms running off both edges.

## chair.png  (final: v1)

> **v1:** A simple wooden chair, seen from a three-quarter angle, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## stadium.png  (final: v1)

> **v1:** An empty oval football stadium seen from above at an angle, with its pitch and rows of seats, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## blueberry.png  (final: v1)

> **v1:** A single blueberry with its little crown on top, seen from a slight angle, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## microscope.png  (final: v1)

> **v1:** A vintage brass laboratory microscope from the early 1900s, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## finger_press.png  (final: v2 (remake))

> **v1:** A human index fingertip pressing down on the flat top of a wooden table, close up, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** A small human hand with one index finger pressing down on the corner of a small wooden block, the whole hand and wrist fully visible and small in the middle of the picture, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 ran off the right edge (the hand was cut off).

## magnets.png  (final: v1)

> **v1:** Two horseshoe magnets facing each other with a small gap between them, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## comb.png  (final: v1)

> **v1:** A plain hair comb lying flat, seen from above, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## shoe.png  (final: v1)

> **v1:** A walking shoe with a ridged sole, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## rope.png  (final: v1)

> **v1:** A neatly coiled length of thick rope, seen from a slight angle above, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## hands_rubbing.png  (final: v2 (remake))

> **v1:** Two human hands rubbing their palms together, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** Two hands rubbing their palms together, only the hands and short wrists, small in the middle of the picture, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 had arms running off the left edge.

## skin.png  (final: v1)

> **v1:** A cross-section block of human skin showing its layers, nerve endings, small round touch receptors and one hair with its root, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## brain.png  (final: v1)

> **v1:** A human brain seen from the left side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## philosopher_bust.png  (final: v1)

> **v1:** A classical marble bust of an ancient Greek philosopher with a long beard and simple robe, seen from a three-quarter angle, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## hug.png  (final: v2 (remake))

> **v1:** Two people in simple clothes embracing in a warm hug, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** Two people in simple clothes embracing in a warm hug, full figures standing, small in the middle of the picture, drawn directly on pure white with no paper edge, no sheet of paper and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 was drawn on a visible sheet of paper.

## handshake.png  (final: v1)

> **v1:** Two hands in a firm handshake, seen from the side, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame
