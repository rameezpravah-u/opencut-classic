# NixWoods "Too warm to care": the NixLine bullet reel

**The ask:** the owner sent instagram.com/reel/DeuQ7gQtvsM on 21 Oct. It is a 15.4 s reel by @nninecoffee_ with no
sound. Their brief:
- "Use the same concept… NixLine standing instead of the glass. The bullet gets burned instead of the freeze";
- "No compromise with quality of the reel. It needs to be as I have shared."

## The reference against ours

| Time | Reference | Ours |
|---|---|---|
| 0–6.6 s | Iced coffee on a white set, with viewfinder corners, a REC timecode and a round badge. A bullet creeps in slowly, with a vapour trail. "FRAMES TO IMPACT" counts down 070 → 017. | The NixLine leans lit on a white set, with the same corners, REC timecode and our round badge. The bullet creeps in. "FRAMES TO IMPACT" counts down 088 → 017. |
| 6.6 s | Cut in closer. A "● chilling" timer counts up. | Cut in closer. A "● glowing" timer counts up. |
| 7–9.5 s | The bullet frosts over: "THEN IT GOT / too close". | The bullet heats from copper to orange to gold, throws sparks and starts to smoke: "THEN IT GOT / too close". |
| 9.5–12.8 s | Frozen, it drops: "It never stood / a chance". | It melts and crumples, and a charred lump drops by the lamp's foot and smoulders: "IT NEVER STOOD / a chance". |
| 12.8–15.4 s | "NNINE Cold Brew / Too chill to care". | "NIXLINE FLOOR LAMP / Too warm to care" · solid teak · ₹999 · nixwoods.com |

**Sound:** ours, because the reference has none.
- a low drone and soft ticks under the countdown;
- a whoosh on the cut;
- a sizzle and crackle as it burns;
- a thud when it lands;
- music1 under the end line.

## How it was made

**The free attempt:** first we tried the free Hugging Face Spaces (FLUX Kontext, Wan 2.2). Two things blocked it:
- the connector's `invoke` is switched off (`gradio=none`);
- the anonymous ZeroGPU quota was used up ("exceeded your ZeroGPU runs limit").

**Higgsfield:** so the owner chose to spend about 6 credits. Nano Banana 2.1 made three stills at 2k, 2 credits each:

| File | What | Verdict |
|---|---|---|
| `gen/set.jpg` | The NixLine on a white studio set. References: the owner's clip nx04 and the page's marble-corner photo. | Approved. It passes the tell: one honey-teak bar, a frosted strip down its face, no base, leaning almost upright, cord at the foot. |
| `gen/bullet.jpg` | A copper bullet, side view, on white. | Approved (prop). |
| `gen/lump.jpg` | A charred, melted bullet on white. | Approved (prop). |

**Motion:** everything that moves is done in `bullet_burn.py`.
- The bullet and lump are cut out of their white backgrounds.
- The creep and the cut are camera moves on the set.
- The heat is a blackbody tint plus a glow.
- Sparks, embers and smoke are particles.
- The melt crumples the bullet from the nose back.
- The fall drops the lump onto the floor with a contact shadow.

**Encode:** CRF 17, 2.2 MB.

## Rules held
- **Claims:** solid teak and ₹999 only (`PRODUCT-FACTS.md`). The heat is a visual metaphor: no line says the lamp
  gets hot, and "warm" means the 3000K light.
- **AI disclosure:** the stills are AI and there is no on-screen label (the owner's call, as for the heist reel).
  Instagram's "Made with AI" toggle must be on, and the caption says so.
- **Organic only:** a bullet in a paid ad risks Meta's weapons and violence review. Do not propose it as an ad
  without the owner.

<details><summary>Prompts</summary>

**set:** Hyper-realistic high-key commercial product photograph on a pure white seamless studio set: a clean white
wall meeting a soft white floor with a gentle horizon. Standing alone, slightly right of centre, is EXACTLY the floor
lamp from the reference images: one single slim straight bar of honey-coloured solid teak with visible grain, square
cross-section with softly rounded ends, about 70 cm tall, a frosted white LED strip running almost its full length
down its front face, switched on and glowing warm 3000K. It has no base: it stands almost upright, leaning very
slightly so its top rests against the white wall, a thin black cord at its foot. A soft warm glow falls on the white
wall around it and a soft contact shadow sits on the floor. Bright, crisp, clean studio light, sharp focus, lots of
empty white space on the left. No text, no logos, no people.

**bullet:** Hyper-realistic macro studio photograph of a single rifle bullet projectile in flight, perfect side view,
pointing straight to the right, horizontal, centred, isolated on a pure flat white background. Polished copper jacket
with a brass sheen, pointed ogive nose, a crisp cannelure ring, flat base. Crisp edges, studio softbox reflections
along the top, no shadow, no motion blur, nothing else in frame. No text.

**lump:** Hyper-realistic macro studio photograph of a small melted, charred and deformed bullet lying on a pure white
seamless floor: a slumped blackened lump of copper and lead with a few dying glowing orange-red cracks, a wisp of grey
smoke rising from it, a faint soft shadow under it. Side view at floor level, centred, lots of empty pure white space
around it. Clean high-key studio light. No text.

</details>

```bash
python3 brand-reels/bullet-burn/bullet_burn.py
```
