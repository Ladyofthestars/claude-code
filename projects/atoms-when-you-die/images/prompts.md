# Picture prompts: "What Happens to Your Atoms When You Die?"

**Model:** Nano Banana 2 Lite (Google Gemini) through the Gemini connector, square, 1K, free. Same model and the same style line as video 1, so old and new pictures match.

**Prompt pattern:** what it is and from which angle, then "lots of empty space around it, nothing touching the edges", then the style line word for word, then the ending.

- **Style line:** Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered.
- **Ending:** plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

**Pipeline:** `tools/cutout.py raw.jpg images/NAME.png --mode ink --ink '#24262b' --paper '#ffffff'` (same dark ink as video 1), then `tools/blueprint.py images/NAME.png public/videos/atoms-when-you-die/images/NAME.png` (glowing white lines over a see-through navy fill, for the blue page).

**Reused from video 1 (blueprint versions only):** person, earth, sun, red_giant, nebula, open_hand, bone, blood_cell, dna, hourglass, young_sun_disk.

**Checks on every picture:** text, colour, cut-off edges (all content boxes are inside the 2% border), extra objects or frames, style. Remakes: at most two per picture; 5 needed one remake, none needed two.

## lungs.png  (final: v2 (remake))

> **v1:** A pair of human lungs with the windpipe, seen from the front, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** A pair of human lungs with the windpipe, seen from the front, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 was drawn on a visible sheet of paper (page edges).

## roman_bust.png  (final: v2 (remake))

> **v1:** A classical marble bust of a Roman man with short hair and a laurel wreath, seen from a three-quarter angle, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** A classical marble bust of a Roman man with short hair and a laurel wreath, seen from a three-quarter angle, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 was drawn on a visible sheet of paper.

## statue.png  (final: v2 (remake))

> **v1:** A small stone statue of a standing robed figure on a square pedestal, seen from the front, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** A small ancient Greek marble statue of a standing young man in a simple draped tunic on a square plinth, seen from the front, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 looked like a particular religious figure (a robed friar), which the narration does not mean.

## bacteria.png  (final: v1)

> **v1:** A small cluster of rod-shaped bacteria as seen under a microscope, drawn as a loose group of capsule shapes, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## mushroom.png  (final: v1)

> **v1:** A small group of three wild mushrooms growing from a little patch of soil, seen from the side, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## leaf.png  (final: v1)

> **v1:** A single fallen oak leaf lying flat, seen from above, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## tree.png  (final: v1)

> **v1:** A lone broad oak tree with a full crown, seen from the side, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## wheat.png  (final: v1)

> **v1:** Three ripe stalks of wheat with long grain heads, standing upright, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## bread.png  (final: v1)

> **v1:** A round rustic loaf of bread, seen from a slight angle, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## deer.png  (final: v1)

> **v1:** A standing deer, seen from the side, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## fish.png  (final: v1)

> **v1:** A single fish, seen from the side, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## shell.png  (final: v1)

> **v1:** A single spiral seashell, seen from the side, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## mountain.png  (final: v1)

> **v1:** A rocky mountain with steep layered cliffs, seen from the side, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## volcano.png  (final: v1)

> **v1:** A cone-shaped volcano with a thin plume of smoke rising from its top, seen from the side, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## coal.png  (final: v1)

> **v1:** A single lump of coal with sharp, glassy facets, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## cloud.png  (final: v1)

> **v1:** A single puffy rain cloud with light rain falling from it, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## venus.png  (final: v1)

> **v1:** The planet Venus as a sphere covered in thick swirling clouds, seen straight on, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## planetary_nebula.png  (final: v2 (remake))

> **v1:** A ring-shaped planetary nebula: a glowing ring of gas around a tiny bright star in the center, seen straight on, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** A planetary nebula in space: a thin, round, glowing ring of gas like a smoke ring, with wisps around it and one tiny bright star in the exact center, seen straight on, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 read a little like an eye.

## marcus_bust.png  (final: v2 (remake))

> **v1:** A classical marble bust of a bearded Roman emperor with curly hair, seen from a three-quarter angle, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

> **v2:** A classical marble bust of a bearded Roman emperor with curly hair, seen from a three-quarter angle, drawn directly on pure white with no paper edge and no border, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

Remade because v1 was a paper page on a grey background.

## log.png  (final: v1)

> **v1:** A short cut log lying on its side, its cut end showing tree rings, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame

## cloth.png  (final: v1)

> **v1:** A folded piece of old hand-woven linen cloth with a visible weave, lots of empty space around it, nothing touching the edges. Black and white scientific illustration, fine ink lines and soft graphite shading, like a page from an old textbook; one single object, isolated and centered. plain white background, no text, no labels, no numbers, no arrows, no shadows, no frame
