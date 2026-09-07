---
name: nixwoods-reels
description: Make, review or extend NixWoods 9:16 social reels and ad cuts from the brief-driven system in nixwoods-reel/. Use when asked to build a reel, video, Instagram or TikTok creative, ad cut, hook, caption or voice-over for a NixWoods product (Aurora Linear Wall Light, Rubik's Cube Lamp, Scandinavian Rosewood Pendant, Double Arm Teak Pendant, and other lamps and pendants), to add a new product to the reel system, to review or approve generated product imagery, or to check a creative against the NixWoods ad rules before it runs.
---

# NixWoods reel system

A brief-driven renderer for 9:16 reels. `brief.json` → twelve reel mechanisms → ffmpeg, with quality gates that refuse creative breaking the brand or ad rules. Everything lives in `nixwoods-reel/`; it is self-contained, needs no network, and needs no flags.

## Read first, in this order

1. `nixwoods-reel/system/PLAYBOOK.md` — evidence from the ad account, hook library, script rules, typography and placement, camera system, the twelve mechanisms, the six quality gates. **Section 0 says how this connects to the Ads Engine, Growth System and Social Playbook that live in the `Code` repo and Drive.**
2. `nixwoods-reel/system/README.md` — brief schema, how to add a product or mechanism.
3. `nixwoods-reel/<product>-reels/ref/REFERENCE.md` — what the product actually looks like. **Read this before generating or judging any imagery.**

## Setup

```bash
pip install pillow numpy imageio-ffmpeg
```

## Commands

```bash
cd nixwoods-reel
python3 system/make_reel.py system/briefs/T1-transformation.json          # one reel, music + clean
python3 system/make_reel.py system/briefs --all                           # every brief, summary table
python3 system/make_reel.py system/briefs --rank                          # order briefs by hook score × tag index
python3 system/make_reel.py <brief> --dry                                 # build and run all checks, no render
python3 system/hooks.py "Still lit by one tubelight?"                     # score a line out of 12
python3 system/qa.py --out qa.jpg                                         # generated assets vs the real reference
python3 system/sources.py <product>-reels/src/clip.mp4 --write <product>   # register a new video's colour states
```

No `--root` needed: each product declares its asset folder in `system/presets.json` (`products.<key>.root`).

## Hard rules — do not work around these

- **Never invent a product's appearance.** Compare every generated still and clip against `ref/` and record the verdict in `presets.json` (`assets.status`, `assets.clip_status`). Anything marked `rejected` is refused at render time and falls back to real footage. A packshot alone is not enough reference for a hands shot; supply a real frame of the gesture too.
- **Never fabricate a testimonial.** The `testimonial` mechanism refuses to render without a real quote and a real name.
- **Never claim a dispatch time** while orders are backlogged, and no lumens or CRI figures without a datasheet.
- **Banned words** (the lint enforces): discover, elevate, luxury, premium, exquisite, journey, curated, unlock, stunning, delve, realm.
- **Any Rubik's / Glass Block creative must show at least two colours.** A single-colour static breaks the locked rule.
- **Generated frames in a paid ad** need Meta's AI-disclosure ticked by hand, and the trademarked product name swapped for `copy.name_ad`.
- **Never deploy a creative nobody has watched.** The contact sheet is not a substitute for the mp4.
- **Judge each product on the right metric.** Wall lights are a CTR product (5.56% to women 35–64); pendants are a ROAS product (1.52% CTR at 13.1x). A pendant reel with low CTR is not a failure — see PLAYBOOK 1.4.
- **Never pull from `90-Archive/photoshoot-20260805-WATERMARKED-do-not-use`.** It is the same 5 Aug shoot as the clean `NW-CREATIVE-IMG-20260805-*` files, but its filenames are bare camera names (`AC4I9586.JPG`), so it is easy to grab by mistake. Match the frame number to the clean original instead; do not remove a watermark to reuse a frame.
- **Drive downloads work up to 10 MB per file**; over that the connector refuses. That rules out the 18 raw shoot clips (19–25 MB) but not the photographs or the shorter edits. Oversized tool results are written to disk — decode the base64 from there, never through context. See `nixwoods-reel/DRIVE-MAP.md`.
- **A horizontal fixture is not a cropping problem.** A centre 9:16 crop of a four-foot pendant removes the four feet. Wide shots of linear products use `fit: contain` in the presets.
- Renders are committed as each passes review — the session container is ephemeral. See the storage rule in `nixwoods-reel/README.md`.

## Where things are

| | |
|---|---|
| System code and config | `nixwoods-reel/system/` |
| Product assets | `nixwoods-reel/<product>-reels/` — `src/` real footage, `audio/` music+VO+SFX (symlinked to the shared set), `hf/` stills, `ref/` reference, `out/` renders |
| Finished reels | `rubik-reels/out/system/` (12 mechanisms + a 27 s ad cut) · `aurora-reels/`, `rosewood-reels/`, `teak-reels/` `out/system/` (5 each) |
| Scripts and voice-overs | `system/scripts/product-scripts.md` (four products) and `vo-scripts.md` (registers) |
| Ads Engine, creative learnings | `Code` repo, branch `claude/nixwoods-funnel-audit-hg4dk9` |
| Source footage and briefs | Google Drive, root `nixwoods` — map and access limits in `nixwoods-reel/DRIVE-MAP.md` |
