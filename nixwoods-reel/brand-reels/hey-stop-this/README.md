# NixWoods "Hey… Stop! Look at… This": the range on @wisherypottery's lyric pattern

**Reference:** instagram.com/reel/DeMwSfCoP2a by @wisherypottery (8.4 s, 37k views, handmade mugs). The owner sent it
on 13 Oct as "another good idea".

## The pattern (every frame seen)
The song's words appear on screen as they are sung, in a white serif:

| Time | Word | Picture |
|---|---|---|
| 0–0.6 s | "H… Heeeeeeee" | An iris opens from black onto a stack of mugs. |
| 0.6–1.75 s | "Stop!" | Stop-motion stills; the word jumps top-left, then right, then centre, while mugs leave the stack. |
| 1.75 s | "Look at" | |
| 2.17–6.37 s | "This" × 7 | Seven cuts, one mug held up each time. The word sits near the mug. |
| 6.37–7.67 s | "Aaaaaaaand" | The hero mug. |
| 7.67 s | "This" | One last mug. |

## This version (`hey_stop_this.py`)
The cut and word times are the reference's to the frame. All footage and photos are real; nothing is generated.

- **Opening:** the Rubik's Cube lamp's colour modes stand in for the stack. One held still per sung word: green, red,
  warm, white, warm. The colours are kept, so at least two show (the cube rule).
- **The seven "This" cuts:**
  1. the NixLine lit in a hand;
  2. the Sculpted Glow by a bed;
  3. a linear pendant over a dining table;
  4. the compact wall light;
  5. the bedside dimmer lamp;
  6. the Aurora coming on;
  7. the minimalist floor lamp.
- **"Aaaaaaaand":** the Rubik's Cube lamp turned by hand as its colour changes.
- **Last "This":** the Sculpted Glow in its dark-room shot.
- **Words:** Fraunces 600 in cream with a soft shadow, inside the safe zone. No names or prices on screen, as in the
  reference.
- **Left out:**
  - The sleek cylindrical floor lamp (AC4I9771) is unlisted on Shopify (13 Oct).
  - The pendant is not named anywhere: three listed pendants could match it (PRODUCT-ID rule).

## Files in `out/`
| File | Audio | Use |
|---|---|---|
| `…-in-app-audio.mp4` | silent track | **Posting master.** On Instagram, tap "Use audio" on the reference reel and start it at 0:00. The words only make sense with that song, so there is no own-music version, and this reel is for organic posting only. |
| `…-cover.jpg`, `…-sheet.jpg` | | The "Aaaaaaaand" frame as cover, and the review sheet. |

## Re-render
```bash
python3 brand-reels/hey-stop-this/hey_stop_this.py [--ref-audio ref.mp4 --preview /tmp/preview.mp4]
```
