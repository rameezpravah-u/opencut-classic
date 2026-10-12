# NixWoods wall lights: exact copy of @horon_design's "RIFT" reel

Reference: instagram.com/reel/DeLU26cRM8M (23.68 s). The owner asked for its script, style, font, text placement and
look, so this piece deliberately sets MOTION.md aside where the reference differs (as the lamps-under-3000 v2 copy did).
9:16, 30 fps, 23.67 s, music1-aesthetic. All footage is real; nothing is generated.

## What was copied (measured off the reference's frames)
- **Type:** thin grotesk caps (here Inter 300, +0.03 em), white on dark ground, near-black on light ground. Every word is
  rotated to run along an edge; the hook's lines step down a ~36° diagonal.
- **Timing:** a 9.6 s macro hook, then four form shots of 3.3, 3.7, 2.0 and 5.08 s. Each word fades in and out over
  ~0.3 s at the reference's times, and the end title fades up at 21.3 s over the last shot.
- **Script**, the reference's lines with our words:

| Time | Footage (product) | Words |
|---|---|---|
| 0–9.6 s | Aurora linear wall light, macro drift, graded dark (`src/drive-aurora-wall-6p.mp4`, 7.6–13.36 s at 0.6×) | THIS IS NIXWOODS / WALL LIGHTING SERIES / STARTED WITH / SIMPLE GEOMETRY / JUST OPENED UP / LINE OF LIGHT |
| 9.6–12.9 s | Compact wall light, lit (DSLR AC4I9644) | RECTANGLE / SOFTER / CALM |
| 12.9–16.6 s | NixLine 30" wall light, pine, unlit (AC4I9658) | VERTICAL / BOLDER / ARCHITECTURAL |
| 16.6–18.6 s | Vertical curved wall light, rosewood, unlit (AC4I9652) | SLIM / SHARP |
| 18.6–23.67 s | Aurora linear wall light, front (same clip, 13.8 s on) | LINE / WASH / EDGE, then "NixWoods Wall Series / Available at nixwoods.com" |

"FIRST LIGHTING SERIES" became "WALL LIGHTING SERIES": "first" would be a claim.

## Where it differs, and why
- **No hand touching the lamp:** none of our real wall-light footage has one.
- **The NixLine and vertical lights are unlit:** the only real photos of them are switched off. The reference's lamps all
  light up. On our two lit shots the light comes up by starting with only the lit areas dimmed (an edit of the real
  frame, not generated).
- **The Aurora is the only wall light with real video under Drive's 10 MB download cap.** The 4:5 clip is cropped to 9:16,
  so it is a little soft. The hook and the last shot use it, graded darker like the reference's moody ground.
- **Words that collided with our glowing bar were moved down:** the hook's first three lines and LINE.

## Footage checked on Drive and not used
- WL-wave-* clips: the 360° pendant, not a wall light.
- this_is_a_wall_light_i_need_y.mp4: carries a Gemini/Veo watermark (AI).
- The "5 Wall Lights" montage: a finished edit with baked text and rendered rooms.
- The NXWDPF* store images: AI-rendered rooms.

The Aurora shot shows two parallel light lines (see PRODUCT-ID.md); it is named Aurora from the owner's Drive files.

    python3 brand-reels/wall-forms-copy/wall_forms_copy.py
