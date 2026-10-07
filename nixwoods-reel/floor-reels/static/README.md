# NixLine native static ad

Built by `native_ad.py` from a reference post (sannidhyabaweja, Instagram `DeGkawhCB2j`, slide 3:
"Make it look pretty" ✗ vs "Make it look native" ✓). Lesson used: a phone-shot product in a hand, in
a real place, with text that looks typed in the Instagram app. Not used: the reference's
"reply to a customer comment" sticker — we have no real customer comment to quote, and testimonials
are never fabricated.

Our own account agrees with the lesson: the raw workshop reels drew 174 and 95 likes; the polished
posts 3–23.

| file | use |
|---|---|
| `out/static/nixline-native-lit-4x5.jpg` | feed, single image — the ad |
| `out/static/nixline-native-lit-9x16.jpg` | Stories / Reels placement (text inside y 230–1500, x 70–950) |
| `out/static/nixline-native-back-4x5.jpg` / `-9x16.jpg` | optional carousel card 2: the plain teak back |

Frames: Rameez's own footage (`src/nx07-7922.mp4` @0.05 s, `src/nx06-7921.mp4` @0.25 s). No AI, so no
AI disclosure needed. Hook "stop buying metal floor lamps." scores 9/12, all three gates.

## Ad copy

**Primary text**

> Stop buying metal floor lamps.
>
> NixLine is a slim column of solid Indian teak — no MDF, no veneer — with one warm line of LED
> light, 2700–3000K. 30 inches. Plug in and place, no assembly.
>
> Made by hand in our workshop in Khatauli, Uttar Pradesh. 3 years on the wood.

**Headline** Solid teak floor lamp, made by hand
**CTA** Shop Now → https://nixwoods.com/products/nix-line-solid-wood-floor-lamp

No price anywhere: the PDP lists NixLine at ₹999 against ₹6,999–9,999 for the other floor lamps,
which looks like a listing error (Rameez chose to leave price off on 23 Sep).

## Generated version (7 Oct) — `out/static/nixline-native-gen-4x5.jpg`

Rameez asked for one generated entirely, inspired by the same post. Higgsfield `gpt_image_2_5`
(1 credit for two variants, from the plan's included credits), with the real PDP marble-corner
photo as the product reference, prompted as a customer's own night-time phone photo of a lived-in
Indian bedroom corner. Variant 2 kept (`hf/nx-gen-native-bedroom.jpg`); verdict recorded in
`presets.json → products.floor.assets.status.native_bedroom`.

- **AI disclosure required**: tick it in Ads Manager; `isAiGenerated: true` if posted organically.
- **No size claim**: the lamp reads taller than its real 30 in beside the bed, so "30 inches" is
  left out of this ad's copy.
- Boxes: "stop buying metal floor lamps." / "solid teak. warm light. plug in." (11 words).

**Primary text**

> Stop buying metal floor lamps.
>
> NixLine is solid Indian teak — no MDF, no veneer — with one warm line of LED light, 2700–3000K.
> Lean it in a corner, plug it in. No assembly.
>
> Made by hand in Khatauli, Uttar Pradesh. 3 years on the wood.

**Headline** Solid teak floor lamp, made by hand · **CTA** Shop Now → the NixLine PDP
