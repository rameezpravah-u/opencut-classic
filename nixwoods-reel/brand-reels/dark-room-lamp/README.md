# Dark room: "Switch off the tube light. Turn this up instead." (20 Nov 2026)

**The ask:** the owner, after the `/last30days` run on wooden lamps and home lighting (15 Nov): "make the reel with the
dark room lamp hook".

**Why this hook:**
- The most-reacted lighting post of that month was a warm, lamp-lit room (r/CozyPlaces, about 27k upvotes).
- People ask whether a dark room "can be fixed with lamps" (r/InteriorDesign).
- Indian homes are lit by white tube lights, so the line names the thing the viewer has overhead. It is clear (a
  dark room, one lamp) and curious (turn what up?).

## Footage and product
- **Source:** the owner's shoot clip 16, Drive's small copy `../lamps-under-3000/src/drive-edison-dimmer-demo-wa.mp4`
  (1080×1920, 25 fps, 19.1 s). Every frame was checked at 2 fps.
  - 0–3.5 s: the dark room with the lamp low.
  - 4.0–5.0 s: a baked-in dissolve. Not used.
  - 5–10.5 s: a hand on the brass dimmer, the filament barely lit.
  - 10.8–11.5 s: the bulb comes up to full; full glow until 12.7 s.
  - From 16.5 s: the NX logo. Not used.
- **Product:** the oblong tube bulb is the PRODUCT-ID tell for the Bedside Dimmer Lamp (Classic Edison), handle
  `bedside-dimmer-lamp-soft-adjustable`. Shopify title: "Rosewood Vintage Ambient Table Lamp – Edison Bulb with Brass
  Dimmer". On screen it is called "Edison Dimmer Lamp".
- **Live 20 Nov:** ₹2,499 (was ₹3,399).
- **Claims, all from PRODUCT-FACTS.md:** solid rosewood base, solid-brass dimmer, free shipping on prepaid orders.
- Real footage only, so no AI label. A hand is on screen; no face.

## The cut (`dark_room_lamp.py`, music1-aesthetic, 0.8823 s beats, 10.0 s)
| Time | Shot | Text |
|---|---|---|
| 0–2.65 s | the dark room, the lamp low, a slow push | "Switch off / the *tube light.*" |
| 2.65–5.29 s | the hand on the dimmer, the filament dim | "Turn *this* up / instead." |
| 5.29–7.94 s | the dimmer turns: the bulb blooms at about 6.0 s and is full by 6.6 s | none: the light is the line |
| 7.94–10 s | end card on the full-glow frame, the top darkened | social: name, "Solid rosewood · brass dimmer", nixwoods.com. Ad: name, the facts, ₹2,499, "Free shipping on prepaid orders", "Shop at nixwoods.com" |

**The ad cut also carries:**
- an "Edison Dimmer Lamp · ₹2,499" chip above the headline from 0.5 s, for the price-checker;
- every line of text above y 1250 (the paid 9:16 CTA zone).

**Sound:** `cues.json` adds text pops on the two lines and an end hit on the card. There is no switch click: a dimmer
has none.

```bash
/usr/bin/python3 brand-reels/dark-room-lamp/dark_room_lamp.py              # both cuts into out/
/usr/bin/python3 system/sfx/place.py out/<name>.mp4 <final>.mp4 --cues brand-reels/dark-room-lamp/cues.json \
    --no-auto-cuts --style calm --master -14
```

## Hook check, the six-viewer read
| Viewer | Where they'd swipe | Fixed by |
|---|---|---|
| Doom-scroller | a slow start | The headline is on screen by 0.35 s, and the bloom pays it off at 6 s. |
| Sceptic | "one lamp can't light a room" | The footage answers it: one bulb fills the frame with warm light. |
| "Is this for me" buyer | "not my house" | Everyone in India knows the tube light. |
| Price-checker (ad) | no price | ₹2,499 is in the chip from 0.5 s and on the end card. |
| Aesthete | a muddy dark frame | The text sits on the dark wall; the lamp glows in frame 1. |
| Skimmer, sound off | unreadable text | 92 px serif in cream, with one amber italic accent. |
