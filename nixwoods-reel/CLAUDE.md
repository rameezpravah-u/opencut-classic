# nixwoods-reel

Creative system for NixWoods (solid-wood lighting, India). Turns a `brief.json` into a finished 9:16 reel and refuses to finish one that breaks a brand or ad rule. **Unrelated to the OpenCut app in the rest of this repo** — it shares the repository only as a store.

Invoke the `nixwoods-reels` skill, or read `system/PLAYBOOK.md` then `system/README.md`.

## Layout

```
system/          the system, ~3 MB, the part that matters
  PLAYBOOK.md      research, hooks, script rules, typography, camera, mechanisms, quality gates
  presets.json     safe zone, slots, 8 audience styles, camera moves, products, ads engine rules
  mechanisms.py    the 12 reel structures
  make_reel.py     brief -> lint -> build -> checks -> render -> cover, sheet, pre-flight timeline
  hooks.py         Gap/Truth/Pull gates and a /12 hook score
  qa.py            generated assets vs the real reference, with approve/reject status
  sources.py       detects a video's colour states and registers them
  briefs/          33 briefs: 13 for the cube lamp, 5 each for Aurora, Rosewood and Teak
  scripts/         product-scripts.md (four products) and vo-scripts.md (three registers)
rubik-reels/     one folder per product, named in presets.json (products.<key>.root)
aurora-reels/      src/ real footage · audio/ (symlink to the shared tracks) · hf/ stills
rosewood-reels/    ref/ design reference · out/ renders
teak-reels/
assets/          fonts and logo, shared across products
```

## Run

```bash
pip install pillow numpy imageio-ffmpeg     # ffmpeg 7 comes with imageio-ffmpeg
python3 system/make_reel.py system/briefs/T1-transformation.json
python3 system/make_reel.py system/briefs --all
```

No flags needed. `--root` only for assets outside a declared product folder.

## Conventions

- **Reference before generation.** Every product needs `ref/REFERENCE.md` and real frames before any AI imagery is made or judged. Generated assets carry an approve/reject verdict in `presets.json`; rejected ones are refused at render and fall back to real footage.
- **Commit renders as they pass review**, not in a batch — the session container is ephemeral. Storage rule and size ceiling in `README.md`.
- **Review sheets are JPEG**, never PNG.
- **Copy rules are enforced, not advisory**: banned words, 12 words a screen, no fabricated testimonials, no dispatch claims while backlogged, two colours minimum on the cube lamp, AI disclosure on generated frames in paid ads.
- Ads Engine, creative learnings and the decision ledger live in the `Code` repo, branch `claude/nixwoods-funnel-audit-hg4dk9`.
- **Drive** (root `nixwoods`): downloads work up to 10 MB a file, so photographs and short edits are fetchable but the 18 raw shoot clips (19–25 MB) are not. Reel photography comes from the public Shopify product CDN. Map, naming, download recipe and the do-not-use watermarked set: `DRIVE-MAP.md`.
