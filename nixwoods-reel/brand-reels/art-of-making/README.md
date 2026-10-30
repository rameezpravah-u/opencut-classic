# NixWoods "the art of making" (30 Oct 2026)

**Reference:** instagram.com/reel/DfDCMtChEYy by A-DIY (@decks), posted 28 Oct with 14k views. The owner, 30 Oct:
"Make like this".

## The reference, every frame seen (8.1 s, music only, no speech)
- **Cuts:** 13 static shots, each held about 0.62 s, with a cut every 18–19 frames at 30 fps. No camera moves and no
  transitions.
- **Shots:** materials and machines as texture. Stacked stick ends open it as the hook, then:
  - a control panel, timber, ducting, sawdust;
  - a machine wheel, belts, chips on a conveyor, a green machine;
  - steel rods, the shop floor, planks.
- **Text:** one small lowercase line, "the art of making", white and centred at mid-frame, on screen throughout.
- **Grade:** muted near-neutral warm, measured per shot: R/G 1.03–1.15 and B/G 0.81–0.98.
- **No brand furniture:** no logo, no price, no end card.

## Ours
**Picture:** the same grammar on our real footage, with no faces. Each shot is the sharpest steady 0.6 s of its clip,
chosen with `system/clip_triage.py`:
1. the routed bars in rows (the repeating-pattern hook);
2. teak planks;
3. the router in pine;
4. strips in the sawdust;
5. flame grain and the holes of the Circular Hole Wall Light, light off (4K at 2×, native);
6. black-finished bars fanned out;
7. the row of holes above the painting;
8. lit bars bundled;
9. a bar on test;
10. a lit bar over the black bars;
11. lit holes under dark grain;
12. a lit teak bar on the floor;
13. the finished light over the painting, held two beats, with "nixwoods.com" under the line.

**Timing:** music3-design (99.4 bpm, beat 0.6036 s, ours and cleared), the closest of our tracks to the reference's
0.62 s. It starts at 10.161 s, so its drop lands on the first cut. Every cut falls on a beat. The reel runs 8.45 s.

**Grade:** MOTION.md's montage grade structure, with the reference's tint instead of our orange one:
- 20 % of each shot's own colour, the rest a muted tint (1.08, 1.0, 0.90);
- every shot at mean luma 0.31, except the two 4K grain shots at 0.42, so the grain doesn't go black against the
  bright wall;
- result: R/G spread 0.16 and B/G spread 0.17, against the reference's own 0.13 / 0.17.

**Text:** "the art of making" in Inter 400, 34 px, white with a soft shadow, at y 960.

**Sound:** music only, as in the reference, plus one soft end hit (`cues.json`), mastered to −14 LUFS.

**Sources:**
- `../festive-ad-cuts/src/`: Drive copies, not committed (see that README);
- `../art-light/src/` and `../../floor-reels/src/`: committed.
