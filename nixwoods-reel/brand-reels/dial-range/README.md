# NixWoods range, "dial a light"

**Reference:** instagram.com/reel/DeUjhgAId3t by @kalenjehgold (10.1 s, 282k views). The owner asked on 14 Oct:
"Another idea. Use clean images."

## The reference, every frame seen
1. **0–3.7 s:** a white phone keypad. One key at a time fills with a round photo of a pendant:
   - keys 1–8 every 0.23 s;
   - then 9 at 2.6 s and 0 at 3.2 s, on its sound hits.
2. **3.73 s:** the green call button is pressed, and the keys burst outward in a blur.
3. **3.85–9.3 s:** nine to ten products, one per beat (about 0.6 s each), full screen. Each has a small gram weight
   under it and a small mark low in the frame. Its sound is dialling hits and a pause, then a beat drop on the first
   product.
4. **End:** the logo on white.

## Ours (`dial_range.py`)
**Photos:** the clean 5 Aug 2026 shoot only (`drive-pull/shoot-20260805`), never the watermarked archive.

**Products:** nine, cheapest first, each a real photo.
- **Naming:** each is named by its visible tell or by the owner on 14 Oct (see `PRODUCT-ID.md`, "The 5 Aug 2026 shoot,
  photo by photo"). Several shoot filenames name the wrong product.
- **Prices:** checked live on Shopify on 14 Oct.

| Key | Photo | Product | On screen |
|---|---|---|---|
| 1 | AC4I9815 | NixLine floor lamp | ₹999 |
| 2 | AC4I9658 | NixLine 30" wall light | from ₹1,799 |
| 3 | AC4I9861 | Bedside dimmer lamp | ₹2,499 |
| 4 | AC4I9652 | 30" wall sconce | ₹2,500 |
| 5 | AC4I9873 | Globe Edison table lamp | ₹2,999 |
| 6 | AC4I9629 | Compact wall light | from ₹4,999 |
| 7 | AC4I9776 | Minimalist floor lamp | from ₹6,999 |
| 8 | AC4I9736 | Rosewood hollow pendant | ₹7,999 |
| 9 | AC4I9882 | Sculpted Glow floor lamp | ₹9,999 |
| 0 | the NX mark | (brand) | |

**Look:**
- The keypad follows the reference's layout and timing.
- The call icon is Material Icons "call" (Apache 2.0; `assets/icon-call.png`, licence beside it).
- The burst out is nine sub-frame motion blur.
- Each product photo gets a slow 4 % push. Its price sits on a small cream chip, since our walls are light and bare
  text would not hold. "NIXWOODS" sits under the chip.
- It ends on the NX logo and nixwoods.com, on white.

## Sound
| File | Audio | Cuts | Use |
|---|---|---|---|
| `…-in-app-audio.mp4` | silent track | the reference's own times | **Organic posting.** Tap "Use audio" on the reference reel and start it at 0:00. |
| `…-music3.mp4` | ours | music3's kicks | **Ads and organic.** Real keypad tones (DTMF) on each key, the call click, a beat of silence, then music3-design's first full kick (10.80 s in the track) landing on the first product. |

The review copy with the reference's audio went to the owner from scratch storage. It is not committed or posted.

```bash
python3 brand-reels/dial-range/dial_range.py [--ref-audio ref.wav --preview /tmp/preview.mp4]
```
