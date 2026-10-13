# NixWoods "light-trace build": the Sculpted Glow drawn in light, made, then lit

**Reference:** instagram.com/reel/DeAfrWxvAdd by @enrriquesdesign (7.07 s, 192k views). It is AI video with a "Comment
PROMPT" lead magnet. The owner asked on 13 Oct to "adapt and use the same music and pattern".

## The pattern
- **Layout:** three panels on black: a "Video prompt" text column, a small "Project image" and a big "Result".
- **The Result:**
  1. an empty plot at dusk;
  2. golden lines sweep the ground, rise up the real edges into a glowing wireframe, and the surfaces materialise;
  3. the lines fade, leaving the finished house exactly as in the project image.
- **Camera:** a slow push with a slight drift.

## This version (`light_trace.py`)
**Free, and made from one real photo:** the 5 Aug shoot's AC4I9882. No generative model is used, so no AI label is
needed.

**Panels** (positions measured off the reference):
- **Left, "Made *by hand*":** Inter 600 with a Fraunces italic accent. The reference's prompt paragraph becomes six
  steps that light up as the Result reaches them: Solid wood. / Cut. / Shaped. / Joined. / Wired. / Lit.
  - That is 9 words.
  - Only what the photo shows and brand.md supports ("handmade"). No finish claims and no wood species: the Shopify
    title says rosewood, but the handle and tags say sheesham.
  - From 5.9 s a cream price card follows: "Sculpted Glow floor lamp, ₹9,999" (live on Shopify, 13 Oct).
- **Top right, "The drawing":** the lamp's own edges in teak ink on Paper, in place of "Project image".
  - MOTION.md says never the same photo twice on screen at once.
  - The shoot's other photo of this lamp (AC4I9751) is framed differently.
- **Result:**

  | Time | What happens |
  |---|---|
  | 0–0.55 s | The room without the lamp (gravity-build's clean plate), dimmed. |
  | 0.55–1.3 s | Lines sweep out along the surface. |
  | 1.05–3.0 s | Lines rise up the frame's outline and its joints. |
  | 2.3–3.4 s | Lines trace the rope's path. |
  | 3.15–4.5 s | The wood materialises from the bottom up, on a warm glow front. |
  | 4.8 s | The rope light draws itself along its path, and the room comes up. |
  | 5.4–6.5 s | The lines fade. |

  The last frame is the photo.

**Camera:** a 4% push with a slight drift, no rotation.

**Lines:** a cream core (#FFEED2) with an amber halo and a wide amber bloom (MOTION.md "the glowing line"). A fresh
line glows brighter at its head.

## Files in `out/`
| File | Audio | Use |
|---|---|---|
| `…-in-app-audio.mp4` | silent track | **Posting master.** The reference's audio could not be downloaded here (its stream was video-only). On Instagram, tap "Use audio" on the reference reel. The Result follows its visual timeline second by second. |
| `…-music3.mp4` | music3-design | Postable as is, and usable in ads. The rope lights on beat 8 (4.80 s). |
| `…-cover.jpg`, `…-sheet.jpg` | | The lit last frame, and the review sheet. |

## Reuse
The lamp masks, the clean plate, the rebuilt wood and the rope's draw order come from
`../gravity-build/gravity_build.py` (`scene_glow`).
