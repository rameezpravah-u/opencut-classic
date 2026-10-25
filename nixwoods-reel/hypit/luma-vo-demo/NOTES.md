# Hypit demo for NixWoods: word-anchored reel, code-only path (25 Oct 2026)

What this proves: one Luma Pillar VO reel authored in Hypit (SVML) where every cut, the hook line,
the captions and the end card are tied to **spoken words** (Script Selections/Moments), not seconds.
Changing the hook (v2) or swapping the product footage (v3) re-renders on the same word anchors.

No generation models, no hosted providers, no HypiHub, no sign-up, no API keys, no credentials.
Every Build request was a local Endpoint (`hypit plan` shows "local, no Provider charge" for all).

## Deliverables (`out/`)
| File | Build | What changed | Duration | Decode |
|---|---|---|---|---|
| `nixwoods-luma-v1.mp4` (+ `-sheet.jpg`) | `bld_20261025T083529171Z_3F4E160111` | baseline: Luma footage, hook "The corner checklist." | 21.2 s | clean |
| `nixwoods-luma-v2-hook.mp4` (+ sheet) | `bld_20261025T084008691Z_AE8F1700C2` | one line: hook → "Your corner is / missing one thing." | 21.2 s | clean |
| `nixwoods-nixline-v3-swap.mp4` (+ sheet) | `bld_20261025T084229162Z_D65B508A7D` | footage → NixLine nx00 (2.5–8.7 s only) + nx04; end card "NixLine Floor Lamp" | 21.2 s | clean |

All 1080x1920, 30 fps, H.264 yuv420p + AAC. Decode check: `ffmpeg -v error -i x.mp4 -f null -` printed nothing.
Evidence: v1→v2 frames differ only in the top third and only in frames 0–98 (0–3.27 s = the `hook`
Selection, which ends on "And" at frame 99); outside that span no 2 fps sample differs by more than
encoder noise (mean abs diff < 0.5/255). v1 and v3 have picture cuts at
the same frames — 29, 58, 99, 151, 181, 222, 276, 331, 413, 486, 541 — and each one is the aligned onset of
candle / cute / And / off / That's / light / Meet / Solid / and(grain) / Just / nixwoods
(`drafts/cut-compare.txt`).

## Layout
- `productions/luma-vo/reel-v1.svml` — the Source (Script, Timeline, word Windows, picture, captions, end card).
  `reel-v2.svml` / `reel-v3.svml` are copies with the stated changes (`diff reel-v1.svml reel-v2.svml` = 1 line).
- `productions/luma-vo/look.svs` — Recipes (caption, type sizes, Film background) from MOTION.md.
- `productions/luma-vo/runs/v{1,2,3}.svrun` — v2 and v3 reuse v1's VO normalization + word alignment through
  `build-record`/`satisfy` (v2 also reuses the normalized footage), so they only re-render.
- `assets/` — copies of the inputs (VO mp3 + words.json, Luma .mov, nx00/nx04, Fraunces/Inter TTFs, logo) and
  code-made stills (`tools/make_stills.py`: caption/hook scrims, Dusk end-card ground, cream logo).
- `tools/fw_service.py` — the local speech-timing service (see below). `tools/sheet.py`, `tools/check.sh`.
- `hypit.runtime.json` — the Profile. `.hypit/results/` — all Build Results (keep it; v2/v3 Runs point at v1's).

## Setup that worked (exact)
```bash
hypit version                       # @hypit/hypit 0.3.1, Node 22.22 (global, preinstalled)
P=/tmp/claude-0/-home-user-opencut-classic/f863beaa-1937-5cac-8a95-89d282b7c923/scratchpad/hypit-demo
cd "$P"                             # package.json with "hypit": {"project": true}; no npm deps needed
hypit runtime init                  # then REPLACED hypit.runtime.json (see below)
hypit doctor
hypit runtime up                    # starts Worker + programs; ~37 s first time (fw service loads model)
hypit programs status --verbose     # html.local, media.local, whisperx.local: ready
cd productions/luma-vo
hypit check runs/v1.svrun && hypit plan runs/v1.svrun
hypit build runs/v1.svrun --title "v1 luma" --follow
cd "$P" && tools/check.sh <build-id> nixwoods-luma-v1   # export, decode check, duration, 2 fps sheet
```
- **npm packages:** none installed in the project. Every `@hypit/*@1` module used (script, whisperx,
  narrative-temporal, narrative-caption, caption, caption-fine, media, media-operations, timeline-author,
  spatial, visual-track, audio-track, text-fine, film, html-video) resolved from the Distribution's default
  packages. Fonts come from local TTFs via `media:Font` (no fontsource packages).
- **Profile changes vs `runtime init`:** removed `hypihub.default` and the credential store (`credentials: {}`);
  removed `image.opencv.local` (unused); `html.local.config.chromePath =
  /opt/pw-browsers/chromium-1194/chrome-linux/chrome` (+ `workers: 3`) so no browser download;
  added `whisperx.local` with `serviceCommand` = `/usr/local/bin/python3 <project>/tools/fw_service.py`,
  `expectedModel: small.en`, `expectedWhisperXVersion: "none (faster-whisper 1.2.1)"`, and the binding
  `@hypit/whisperx@1#whisperx-alignment → whisperx.local`.
- **Env vars:** none were needed (nothing went to the network; NODE_EXTRA_CA_CERTS etc. not used).

## Word timing: how it was done, and why not WhisperX
- Hypit has no "supply your own alignment" input for a fresh Script: `NarrativeAlignment` is produced by
  `<whisperx:Alignment>` and carries the normalized media's domain identity, so the precomputed
  `luma-vo-words.json` cannot be dropped in as a `<value>`.
- The packaged local WhisperX (`programs prepare`) does `uv sync --frozen` of whisperx 3.8.6 + torch 2.x
  with the CUDA wheel set (nvidia-cublas/cudnn/nccl…, several GB) plus wav2vec2 alignment weights. Not
  "cheap" for a CPU sandbox, so it was **not** prepared.
- Instead the Provider's documented `serviceCommand` runs `tools/fw_service.py`: a ~150-line loopback
  service speaking the same `hypit.whisperx-service@1` protocol, backed by the system python3's
  faster-whisper 1.2.1 `small.en` (already in `~/.cache/huggingface`, loaded `local_files_only`). It
  reports itself honestly (`whisperxVersion: "none (faster-whisper 1.2.1)"`) and the Profile expects that
  exact string. Hypit's own deterministic aligner (`@hypit/narrative-speech-alignment`) then maps those
  measured words onto the Script, including M:N matches ("$15 .99" ↔ "fifteen ninety-nine",
  "nixwoods .com" ↔ the Dual Text `<nixwoods.com|nixwoods dot com>`).
- **Problem hit:** faster-whisper's word times drift around pauses ("candle" came back 1.38–1.38 when it
  is spoken at ~0.95–1.5 s; "off?" 0.26 s late). The first v1 cut to "Candle" fired 0.55 s early.
  **Fix:** the service refines boundaries on the same 16 kHz samples: silences ≥150 ms in a 10 ms RMS
  envelope are assigned to the word boundary whose whisper end/start are nearest, so word k ends at the
  silence and k+1 starts where speech resumes. After that every cut onset matches the waveform
  (candle 0.98, off 5.04, That's 6.04). `hypit transcribe <audio> --language en --to x.json` uses the same
  Endpoint and is a quick way to inspect it.
- Residual: at "…ninety-nine. [pause] On nixwoods" the refinement is ambiguous and leaves "On" early. So
  the Script makes "On" spoken-not-captioned (`<|On>`) and the end-card Moment `card` sits on the URL
  (18.04 s, measured onset of "On nixwoods" ≈ 18.0 s).

## Problems hit and fixes
1. `Text Recipe does not accept letter-spacing` → text-fine uses `tracking` (px) and `weight`.
2. `Visual Track picture already contains w-card` → one Visual Track can't hold two Clips on the same
   Window; the logo got its own Track.
3. Pause-ownership: `@{~x}` (meet at previous word's end) gave "off?" a one-frame shot because whisper made it
   ~0 s long. Switched every cut to `@{/x~} @{y}` = cut on the onset of the shot's first word.
4. v2's two-line hook wrapped inside a word ("missin|g") with default wrapping → explicit
   `<typo:P>…<typo:Break/>…</typo:P>` + `wrap="none"`.
5. Last shot ended at the hidden "On" token leaving 0.5 s of empty ground → moved `@{/price~}` after `<|On>`.

## Timings (4 vCPU, 15 GB, CPU only)
- `runtime up`: 37 s (first). Fresh v1 Build (2 normalizations, transcription+alignment ~5 s, 636 frames
  rasterized with 3 Chromium workers, encode, mux): ~1 m 30 s – 1 m 45 s.
- v2 (reuse: render only, 3 requests): 1 m 21 s. v3 (reuse VO+alignment; 2 new normalizations): 2 m 18 s.

## What a future session must re-run (global npm, ~/.cache, ~/.local/state do not persist)
1. `npm i -g @hypit/hypit@0.3.1` (needs Node 22; installed globally under /opt/node22 here).
2. Python: `pip install faster-whisper==1.2.1` into the python3 named in `serviceCommand`, and have
   `Systran/faster-whisper-small.en` in `~/.cache/huggingface/hub` (e.g. one online run with
   `local_files_only=False`, or `huggingface-cli download Systran/faster-whisper-small.en`). The service
   refuses to download at inference time. If the python path changes, edit `serviceCommand`.
3. Chromium at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (else change `chromePath`, or remove it
   and run `hypit programs prepare --endpoint html.local` to download Hypit's managed Chrome).
4. `ffmpeg`/`ffprobe` on PATH. Then from the project root: `hypit runtime up`, build the Runs.
5. `.hypit/results/` must travel with the project: v2/v3 Runs reference v1's Build id. If it is lost, delete
   the `build-record`/`satisfy` lines and the Builds recompute alignment (≈ +10 s).
6. Stop when done: `hypit runtime down; hypit programs down --endpoint whisperx.local`.

## Caveats
- v3 is a structural demo, **not postable**: the VO still says "Meet the Luma Pillar" and "fifteen
  ninety-nine" (Luma's price) over NixLine footage, and the NixLine is lit from the first frame, so "off?" /
  "light" have no on/off beat. The end card says "NixLine Floor Lamp · nixwoods.com".
- Captions show the VO's price line as words ("Just fifteen ninety-nine."), because the script says it; the
  end card carries no price. Re-check the ₹1,599 price before any Luma post.
- The VO is synthetic (ElevenLabs, owner-approved earlier); the post caption must say so as for E2.
- Shots are fitted (stretched/compressed) to their word Windows by frame repetition, no motion
  interpolation; the 480x848 Luma source is upscaled; no colour grade or music was added; VO peaks ~3 dB
  lower than the source mp3 after Hypit's mix.
- Hypit Studio was not opened (no browser UI here); review was by contact sheets and frame diffs.
