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
- **Never poll for a background render with a `pgrep` wait-loop.** The harness sends a completion
  notification when a backgrounded command exits — that is the signal. A loop like
  `while pgrep -f "make_reel.py <brief>"; do sleep 15; done` also matches its OWN command line,
  so it never exits, and a second one matches the first. Two of these span silently on 9 Sep while
  the render they were watching had already finished. If a wait is genuinely needed, wait on a
  condition that cannot match the watcher (a file appearing, a marker written by the job itself).
- **Copy rules are enforced, not advisory**: banned words, 12 words a screen, no fabricated testimonials, no dispatch claims while backlogged, two colours minimum on the cube lamp, AI disclosure on generated frames in paid ads.
- Ads Engine, creative learnings and the decision ledger live in the `Code` repo, branch `claude/nixwoods-funnel-audit-hg4dk9`.
- **Drive** (root `nixwoods`): downloads work up to 10 MB a file, so photographs and short edits are fetchable but the 18 raw shoot clips (19–25 MB) are not. Reel photography comes from the public Shopify product CDN. Map, naming, download recipe and the do-not-use watermarked set: `DRIVE-MAP.md`.

## NixWoods OS contract (OPERATING_MANUAL §6b / §6c — standing, no need to be asked)

Nothing produced here is finished until all five are true. A session that skips a step has produced
nothing as far as the OS is concerned; the weekly health check lists it as an "orphan producer".

1. **Filed** — the render lives in the tree, not only in a scratch folder or a branch. Text
   (scripts, prompts, captions, hooks, briefs, manifests) goes to repo `Code` under
   `creative/<engine>/` and is **merged to `main` the same session** — branches are invisible to
   Cowork and to the Mac.
2. **Named** — `NW-<FRONT>-<TYPE>-<YYYYMMDD>-<shopify-handle|brand>-<slug>-v#`.
   `system/file_for_os.py` does this: `python3 system/file_for_os.py --date <YYYYMMDD>`.
3. **Registered** — one row per asset in `nixwoods-os` `00-OS/ASSET_REGISTRY.md` with product,
   product_id, shot_type, orientation, duration, location, tool/credits, and
   `status` = **READY** (post-able as is) | **STAGED** (needs a caption/crop/VO) | **UNUSED**.
   `git pull --rebase` before pushing — the Mac writes to the same files.
4. **Reachable** — the mp4s live in this repo, which is not in the Cowork project sync, so a
   registry row alone leaves a consumer knowing an asset exists and unable to open it. After a
   status change or a new batch, rebuild the index in repo `Code`:
   `python3 creative/viral-reel/build_index.py --registry ../nixwoods-os/00-OS/ASSET_REGISTRY.md --renders ../opencut-classic`
   It refuses to write a path that does not exist. `creative/viral-reel/FETCH.md` carries the
   fetch commands — a partial + sparse clone pulls one reel in ~14 MB.
5. **Handed off** — a TASK_LEDGER row plus a HANDOFF line naming the consumers:
   `next: SOCIAL (Mac social engine) · ADS (Decision Pass creative pipeline) · PIN (pinterest-engine) · EMAIL (EMAIL tab)`.

Consumers read the registry, never this chat: the Mac social engine takes `READY` rows for the
weekly calendar, the .com Decision Pass (Thursday step 10) proposes ad tests from `READY` 9:16/4:5
rows whose `usable-for` contains ADS, pinterest-engine takes 2:3/9:16, the EMAIL tab takes heroes.

### Source-media bus (§6c) — reuse before you generate

Cloud sessions cannot read Drive or the Mac. The library you may build from is mirrored by Mac
Claude Code into **`source/<shopify-handle>/`** in this repo, with **`source/INDEX.tsv`**
(asset ID, handle, path, shot type, orientation, usage rule).

- **Read `source/INDEX.tsv` before generating anything new.** Reuse beats re-render, and beats
  spending Higgsfield credits.
- **Never use a frame flagged `DO NOT REUSE`.**
- If `source/` is absent, the Mac mirror has not landed yet — say so rather than assuming there is
  no footage, and fall back to `<product>-reels/src/` and the Shopify product CDN.

### Settled decisions

- **D-017 (2026-09-07).** "Rubik's Cube" stays in all creative — end cards, captions, everywhere.
  No re-render, no rename. Do not raise the trademark question again in any session.
