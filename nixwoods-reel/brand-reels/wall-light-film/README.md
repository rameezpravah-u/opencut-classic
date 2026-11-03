# Wall Light Film

A cinematic brand film (not a 9:16 reel) showing six real NixWoods wall-light SKUs across six
settings: home, office, hotel corridor, art gallery, restaurant, fancy hotel suite. Requested
directly by the owner ("Bentley/Rolls-Royce ad" feel), outside the usual single-product
brief-driven reel pipeline, so it lives here as its own small system rather than a `system/briefs/`
entry.

**Not committed to git.** `.git` is already ~2.3 GB (past the ceiling `nixwoods-reel/README.md`
documents), and every mp4/png here regenerates from this folder plus the real catalogue photos
below, so the media stays out of the repo (`.gitignore`'d) and lives only in the session that made
it and in the deliverable sent to the owner. Re-run `build.py` to reproduce the final cut once the
six source clips are back in `clips/`.

## Cast (one real SKU per scene, locked to its live catalogue photo — never invented)

| # | Space | Product (slug) | Reference photo |
|---|---|---|---|
| 1 | Home | Aurora Linear Wall Light (`aurora`) | `aurora-reels/hf/sh00-console-lit.png` + CDN `185118F0-8963-41ED-BD5B-45E95394C557.png` |
| 2 | Office | NixLine 30" Wall Light (`nixline`) | CDN `fccf0aa6-35fb-40da-8a78-fecb29c99492.png` |
| 3 | Hotel corridor | 30" Wall Sconce (`wall-sconce-30`) | CDN `19f564dc-6c38-44b6-9fa5-b27b0496896e.jpg` |
| 4 | Art gallery | Vertical Curved Wall Light (`vertical-curved-wall-light`) | CDN `product_gallery_960x960_webp_1.jpg` |
| 5 | Restaurant | Timber Wall Light (`timber-wall-light`) | CDN `c257ebec-85b5-435b-8fce-330c8425498d.jpg` |
| 6 | Fancy hotel suite | Arden (`arden`) | CDN `85b98c98-3e01-4bf1-9eca-275a47d718bf.jpg` |

All CDN paths are under `https://cdn.shopify.com/s/files/1/0650/8488/3079/files/`.

### QA note — Aure rejected (keep for the record)

Scene 6 was first built on **Aure** (`arden`'s neighbour in `PRODUCT-ID.md`: "a deep curved
U-profile teak piece, light out of the bottom edge"). Two generations in a row rendered it as a
plain flat rectangular block instead of the real curved channel — a genuine fidelity miss, not a
style note, per the "never invent a product's appearance" rule. Swapped to **Arden** (a real
rosewood box with up-and-down glow — a product whose true form *is* a simple box), which passed on
the first try. Do not reuse the Aure generations (`stills/06-suite-aure.png`,
`stills/06-suite-aure-v2.png`, `clips/06-suite-aure.mp4` if regenerated) in any finished cut.

## Pipeline

1. **Stills** — Higgsfield `nano_banana_2_1`, 16:9, 2k, each prompt locked to the product's real
   reference photo via `image_references` so the generated room can't drift from the product's
   actual form. House prompt pattern: scene, locked product placement, environment details,
   motivated practical light + a Kelvin-specified fill, lens/focus, mood, palette, quality markers,
   avoid-list, closing "stays exactly as in the reference image" line.
2. **Motion** — Higgsfield `cinematic_studio_video_v2` (mode `pro`), one cinematic camera move per
   scene from the house vocabulary (`system/PLAYBOOK.md` §5): push-in, rack-focus, dolly,
   horizontal drift + rack-focus, push-in, tilt-up. 6s each, genre `intimate`/`spectacle`, no
   generated sound (scored separately).
3. **Assembly** — `build.py`: scales/crops every clip to 1920×1080@24fps, applies the approved
   `aesthetic` grade from `system/presets.json`
   (`eq=contrast=0.97:brightness=0.015:saturation=0.94,vignette=angle=PI/4.6:mode=forward,noise=alls=5:allf=t+u`),
   crossfades scenes with a 0.8s dissolve, appends a 3s end card (logo + "solid wood lighting" /
   "nixwoods.com", Cormorant Garamond italic + DM Sans, matching the `aesthetic` style's fonts),
   and scores it with `rubik-reels/audio/music3-design.mp3` — one of the two tracks `brand.md`
   names as cleared for paid use — faded in/out. Final duration ~29.2s.

```
python3 build.py     # from this folder; needs clips/0N-*.mp4 present
```

## Still open

- **No human has watched the final cut end to end yet** (the house rule: "never deploy a creative
  nobody has watched"). Treat it as a strong draft, not an approved ad.
- **Generated-frame AI disclosure** (Meta/Instagram) is not ticked anywhere — required before any
  paid use, per `brand.md`.
- **Cross-repo filing** (`nixwoods-os` `ASSET_REGISTRY.md`, `TASK_LEDGER.md`, the `Code` repo's
  `creative/viral-reel/build_index.py`) could not be done from this session — those repos aren't
  attached here. If this film moves forward, file it there by hand per
  `nixwoods-reel/CLAUDE.md`'s OS contract.
- Scene 6 originally covered "fancy hotel suite" with Aure; it now runs Arden instead (see QA note
  above). If a true Aure match is wanted later, it needs art direction beyond a text prompt — the
  model consistently collapses its curved channel into a flat box.
