# Festive ad cuts (Meta ads inbox), 12 Oct 2026

Requested by the social desk on 11 Oct, due Tue 13 Oct (`nixwoods-os/00-OS/HANDOFF-FOR-CLAUDE-CODE.md`, task
`CREATIVE-festive-ad-cuts-20261013`). The owner asked for both lengths on 12 Oct, so there are three products × a 10 s
and a 15 s cut × 9:16 and 4:5 = 12 files in `out/`. Script: `festive_cuts.py`. 30 fps, cuts on the music grid, CRF 17.

## The three cuts

**Aurora wall light**, FESTIVE-P1-01, music6-corners. Price from ₹1,999.
- Hook: "A new thing / for the house." Then: "Made the *slow* way."
- Shots: raw teak planks → routed teak bars with their diffusers → (15 s only: black-finish bars) → one bar lit on test
  → the Aurora on a wall coming on.
- Price on screen at 6.3 s (10 s) and 7.1 s (15 s).

**NixLine floor lamp**, FESTIVE-P1-06, music6-corners. Price ₹999.
- Hook: "Solid teak." Then: "Made to *keep*."
- Shots: a hand holding the unlit teak stem → the stem → (15 s: the bars before fitting) → the lamp standing at the
  bench, switching on → (15 s: a hand holding it lit).
- Price on screen at 5.2 s (10 s) and 6.0 s (15 s).

**Rubik's Cube lamp**, FESTIVE-P1-08, music1-aesthetic. Price from ₹2,999.
- Hook: "What a brother gives / on Bhai Dooj:" Then: "something she *keeps*."
- Shots: a warm close-up of the glass block → a hand turns the block → the lamp lit warm → (15 s: a second close-up,
  then a wider view).
- Price on screen at 5.9 s.

## Every cut

- **Price card:** product name, price, chips (material · COD) and nixwoods.com, on a cream card. 15 s cuts end on a
  Dusk end card with the logo, the line, the price and nixwoods.com. 10 s cuts end on the payoff shot with the card.
- **Prices:** live on Shopify, 12 Oct. Re-check them before the ads go live (D-021: no price change through festive).

## Rules checked

- **Footage:**
  - Real footage only. No generated frame, so no AI label is needed.
  - The NixLine is straightened in every shot where it stands or is held lit (MOTION.md: never leaning).
- **Hands:**
  - The NixLine and Rubik's Cube cuts have hands in frame.
  - **The Aurora cut has no hands.** Every Aurora hand clip on Drive is too large to download here: 442e65ee is
    7.4 MB, 148414D8 8.5 MB, IMG_8028/8029 over 20 MB and IMG_7683 63 MB; the connector stops at about 7 MB.
  - A hand version needs one of those clips saved under 7 MB into Drive.
- **Copy:**
  - No delivery date, "order by", "in time for Diwali" or ritual line. No "brass" or "not iron" claim.
  - "Rubik's" stays (D-017).
  - No banned words.
- **Text placement:** inside the 9:16 safe zone. The price card sits above y 1250 (Meta's CTA bar) and clear of the
  NixLine's lit channel.
- **Look:**
  - MOTION.md: Fraunces 600 with one amber italic accent word, Inter 600 for facts, cream and amber.
  - The montage grade: each shot keeps 35% of its own colour, the rest is one warm tint, and the shot lands at mean
    luma 0.31.
- **Brief vs MOTION.md:** the social desk's brief named Archivo and a Bone / Signal Amber palette. This tab follows
  MOTION.md, so those two values differ from the brief on purpose.
- **Ad copy:** "Free shipping across India" (ad formula) belongs in the ad copy, not burned into the video. Not
  verified here.

## Sources (on Drive; not committed, to keep the repo under GitHub's size warning)

| Clip | Drive file id | Used for |
|---|---|---|
| raw/2026-10-04-drop/FBB4C770-…MP4 | 1huxpGizOKXaBcgOu_mEdMJT_WlXrv5pm | raw teak planks |
| raw/2026-10-04-drop/IMG_7984.mov | 1yPhMSHiIveT_XYia7q_pMZD1AByJ3a0I | routed teak bars with diffusers |
| raw/2026-10-04-drop/IMG_7990.mov | 1xpjbeUCikVgDV7PHOP6hIPUtIzMWzy48 | black-finish bars |
| raw/2026-10-04-drop/IMG_7991.mov | 1K9uFn3TiPycKQVKkDjF20k7plRpqBnc7 | one bar lit on test |
| aurora-dimming-9x16.mp4 (0–3.85 s, before its logo) | 1QbiR4ZYZinkPSooHR20SdsKpj_rlys2l | Aurora on the wall coming on |
| raw/2026-10-11-drop/NW-RAW-20261011-unknown-ea1e0467.mov | 1CxH8umOnVDHmGrQQleZ93annOWXACZ1J | NixLine lit at the bench |
| raw/2026-10-11-drop/NW-RAW-20261011-unknown-2e5660bf.mov | 1XEG-jfYiHgogq--AS9IAeDCN0ZlQ8yeZ | Rubik's Cube close-up |
| raw/2026-10-11-drop/NW-RAW-20261011-unknown-92973dce.mov | 1me3AyIsN_8WI79RjVhBsTDOtePw74co1 | Rubik's Cube close-up |

From this repo:
- `floor-reels/src/nx03`, `nx04` and `nx06`: NixLine hand, stem, bench and lit-hand shots.
- `rubik-reels/src/14-1.mp4`: the hand at 12.2–13.95 s, warm at 5.7–10.4 s and 9.3–11.1 s (its red mode runs to 5.5 s). The green and red modes
  and the logo after 17 s are not used.

To re-render: download the Drive clips into `src/` (see `DRIVE-MAP.md`), then run
`python3 brand-reels/festive-ad-cuts/festive_cuts.py`.
