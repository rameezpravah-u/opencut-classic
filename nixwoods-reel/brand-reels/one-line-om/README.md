# NixLine: One line of light

The first NixWoods reel made through OpenMontage (github.com/calesthio/OpenMontage at the commit pinned in
`.claude/hooks/session-start.sh`). It uses the hybrid pipeline and a hand-built HyperFrames composition.

The reel is 9:16, 30 fps and 10.03 s long. Its music is music6-corners from its first beat, and every cut lands on the beat.
Every frame is real: the NixLine workshop clips and the 5 Aug shoot photo AC4I9815. Nothing is generated,
so the reel needs no AI label.

| Time | Shot | On screen |
|---|---|---|
| 0–1.67 s | The bare teak bar (nx06). A line of light draws down it on beat 1. | It starts as / one line. |
| 1.67–3.33 s | The same bar, flipped. Its real lit channel stands where the drawn line was. | Solid / teak. · Made by / hand. |
| 3.33–4.17 s | A bundle of lit bars (nx03). | — |
| 4.17–5.00 s | One bar standing upright (nx04). | — |
| 5.00–6.70 s | NixLine in a real room (AC4I9815), with a 5% push. | Then it warms the *corner.* |
| 6.70–10.03 s | The Dusk ground covers the room. The lamp's channel becomes the brand line. | Logo · NixLine. ₹999 ~~₹1,599~~ · Solid teak · Cash on delivery · Free delivery · nixwoods.com |

The line holds still on x 540 across the cuts. `prep.py` tracks each lit channel, and the bare bar in shot 1, frame by frame.
It rotates and shifts every frame so the line stands vertical on x 540, using the smallest zoom that shows no frame edge.
It then applies MOTION.md's montage grade.

## Files
- `prep.py`: footage prep. It writes into the OpenMontage project's `hyperframes/assets/`.
- `index.html`: the HyperFrames composition. It goes in the OpenMontage project's `hyperframes/` folder.
- `openmontage/`: the run's canonical artifacts (brief, script, scene_plan, asset_manifest, edit_decisions,
  decision_log) and the three stage scripts that wrote them.

## Reproduce (cloud session; the start-up script installs OpenMontage)
1. In `$OPENMONTAGE_DIR`, run `PYTHONPATH=. .venv/bin/python <repo>/nixwoods-reel/brand-reels/one-line-om/openmontage/stage_idea_script.py`.
2. From `nixwoods-reel`, run `python3 brand-reels/one-line-om/prep.py`.
3. Copy the fonts, `gsap-3.14.2.min.js`, `hyperframes.json`, `music6-corners.mp3` and `index.html` into the workspace.
4. Run `stage_plan_assets.py`, then `stage_edit_compose.py` (renders `projects/nixline-one-line-of-light/renders/final.mp4`).

## Review notes (r2)
- r1: "corner." touched the lamp's cap. The headline is now one line at 64 px, clear of the lamp all through the push.
- r1: the logo faded in over the fading lamp. It now waits until the ground has covered the room.
- OpenMontage's final review passed. Its audio check reported narration that isn't there (a false positive).
- OpenMontage issue: its checkpoint guide says to record a full-run approval as `category: "approval_policy"`, but
  the decision_log schema doesn't allow that category. The entry (d-007) was written straight to the log.
