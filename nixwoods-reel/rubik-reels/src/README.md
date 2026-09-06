# Source footage

Real product video. Everything else in the reels is either this or a generated frame checked against `../ref/`.

| File | What | Drive |
|---|---|---|
| `14-1.mp4` | Rubik's Cube Lamp hero shot, 19 s: green → red → amber → warm, then a hand cycling the colours | `NixWoods Creatives`, "14-1 - Rubiks Cube Glass Block Lamp - green-red-amber + hand colour cycle (HERO SHOT).mp4", id `1QTPhO9FoUjfeA37asYg4yt9nr0_LjsKQ` |

Colour states are registered in `system/presets.json` (`products.rubik.states` / `state_max`). They were derived by `system/sources.py`, not typed by hand — run it on any new footage:

```bash
python3 ../../system/sources.py src/14-1.mp4 --write rubik
```
