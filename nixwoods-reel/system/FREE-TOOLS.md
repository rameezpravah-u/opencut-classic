# Free generation tools — what is actually free (checked 7 Oct 2026)

Standing preference: **free only**. Claims on Instagram "free tools" posts are not evidence — check the
tool's own pricing page before relying on it. Sources: each site's homepage / pricing page, 7 Oct.

| Tool | Claimed (gameofai1 carousel) | Actually | Usable from a cloud session? | For NixWoods ads |
|---|---|---|---|---|
| **Hugging Face Spaces** (FLUX Kontext, Qwen-Image, Wan 2.2) | — | free GPU (ZeroGPU), no watermark | yes, via the HF connector — but `invoke` is off (`gradio=none`) and the anonymous quota runs out; a free HF token in the environment fixes both | **best free option** once a token is added |
| **Higgsfield** | — | plan credits (601 on 7 Oct, ~1 credit per 2 images with gpt_image_2_5) | yes, connector | usable; credits are part of the existing plan |
| **ZSky AI** (zsky.ai) | no card, no watermark, no cap | unlimited, but free output carries a **"MADE WITH / zsky.ai" wordmark**; Pro $19/mo removes it; API only on Max $99/mo | web only, needs a free account (never logged into on the person's behalf) | not clean enough for a paid ad on free; fine for mood boards |
| **Wireflow** (wireflow.ai) | no card, no watermark, no cap | free account **builds** workflows; running video models needs a **paid plan's credits** | web only, needs an account | not free for generation |
| **D-ID Studio** | photo-to-video, avatars | trial ~5 min/month, **watermarked, commercial use excluded** | — | no |
| **Pictory** | text-to-video | trial: 3 projects, **watermarked**; paid ~$19–25/mo | — | no |
| **Steve AI** | text-to-video, avatars | free plan **watermarked**; cartoon/animated style | — | no |

Rule that does not change with the tool: a generated image of a product must be checked against the real
product (`<product>-reels/ref/`, PDP photos) and its verdict recorded in `presets.json`; paid ads with
generated frames need Meta's AI disclosure ticked.

## Content skills installed 7 Oct (from github.com/Ootto-AI/claude-content-skills @ 07b5294, MIT)

Read in full before installing; they are prompt templates (plus one CSV parser) in `.claude/skills/`:
`reel-analyzer`, `viral-hook-writer`, `reel-scripter`, `on-screen-text-writer`, `caption-and-hashtags`,
`carousel-builder`, `competitor-teardown`, `social-proof-mining`, `paid-social-brief`, `ab-hook-tester`,
`hook-mining`, `comment-responder`.

Deliberately **not** installed: `content-factory` (auto-posts 3×/day through Apify + Composio — conflicts
with D-018 scheduling authority and the OS hand-off), `reel-builder` (renders on paid Runway/Seedance;
`nixwoods-reels` already renders), `agent-reach` (scrapes with exported browser cookies).
NixWoods rules win where they differ: `hooks.py` gates, banned words, no fabricated testimonials.

To study a reference post: carousels → `system/ig_carousel.py` (needs approval per run, not Auto mode);
reels → download the video URL from `vibiz_read_social_post`, 1 fps frames + faster-whisper transcript.
Never brief from the post reader's text description alone — it sees only the cover.

## Motion skills installed 8 Oct (all free, all in `.claude/skills/`, licences in `.claude/skills/_licenses/`)

Copied from pinned commits and read before installing. None of them auto-posts or logs in anywhere.

| Source | Commit, licence | Skills |
|---|---|---|
| github.com/heygen-com/hyperframes | `188475a`, Apache-2.0 | core: `hyperframes` (entry point), `hyperframes-core`, `-cli`, `-animation`, `-keyframes`, `-creative`, `-audio`, `-registry`, `-studio`, `media-use`; workflows: `motion-graphics`, `general-video`, `music-to-video` |
| github.com/charlie947/motion-graphics-skills | `4cd156a`, MIT | `brand-intake`, `motion-brief-writer`, `motion-effects`, `animated-chart`, `milestone-reveal`, `launch-video`, `title-sequence-3d`, `newsletter-promo`, `model-showdown`, `loop-cover`, `apple-launch-film`, `reel-export`, `vox-explainer` |
| github.com/emilkowalski/skills | `e8a175d`, MIT | `apple-design`, `review-animations`, `improve-animations`, `animation-vocabulary` |
| github.com/Vibha-Ramprakash/claude-video-effects (added 24 Oct, owner's ask from instagram.com/reel/DezSAGzt1iB) | `77e0044`, MIT | `effects`: 36 effects driven by `/effects <name>` |

**`effects` (24 Oct).**
- **Audit:** read in full before installing. It calls only ffmpeg and ffprobe, with no network calls. It ships its
  own models: `yunet.onnx` (OpenCV) and `selfie_segmenter.tflite` (MediaPipe). Its one `exec` loads an optional
  `fx_private.py`, which is not shipped and is ignored by `.gitignore`.
- **Setup:** `bash .claude/skills/effects/scripts/setup.sh` builds `.venv` inside the skill folder (not committed)
  and printed READY here on 24 Oct.
- **Not yet done:** on 24 Oct the session's safety check blocked running `fx.py`. A test on our footage needs the
  owner to allow it.
- **Built for a person on camera:** most effects track a face or cut the speaker out (orbit, locked-on, spotlight,
  lean-in, backdrop-word, glass-widgets, todo, checklist). Use them only on owner, staff or creator footage with a
  release.
- **For faceless product clips,** try the effects that need no face: moody, swipe, dot-reveal, rabbit-hole,
  reject-stamp, countdown-flip, comment-box, tap, reel-frame, uninstall. Check every frame.
- **Still ours:**
  - restyle `text`, `color` and `font` to MOTION.md;
  - add our own sound and captions, because it adds neither;
  - follow the AI-label rules;
  - the "Edited by Claude" pill in glass-widgets needs the owner's OK;
  - never use it to copy another creator's branding.

**`nixwoods-reel/motion-libs/` (24 Oct, Ian Tang's "Claude Motion Tips", instagram.com/reel/DeWzv0mMi8_).**
- **What it is:** p5.js with p5.brush, Rough.js, Matter.js, Anime.js, PixiJS and pixi-filters, pinned and vendored
  with their licences.
- **`beats.py`:** beats and downbeats from our music.
- **`render.py`:** renders any seek-safe HTML sketch to video in the pre-installed Chromium.
- **A template:** `brush-reveal`, the NixLine painted in on the beat.
- **More:** a brand-file prompt template is in `motion-libs/README.md`.

**Free product cut-outs:** use rembg 2.0.67 (MIT, `isnet-general-use`) in a throwaway venv, with
`SSL_CERT_FILE=/root/.ccr/ca-bundle.crt` for the one-time model download (179 MB from GitHub releases). The recipe is
in `brand-reels/lamps-from-999/make_cutouts.py`. A lit strip reads as background, so fill the holes back in. Use
GrabCut where a dark base is lost.

**Not installed:**
- The other HyperFrames workflows: `embedded-captions`, `faceless-explainer`, `pr-to-video`,
  `product-launch-video`, `slideshow`, `talking-head-recut`, `remotion-to-hyperframes` and `figma`.
  Install one with `npx skills add heygen-com/hyperframes --skill <name>` when a job needs it.
- Emil's UI-only skills.

**Which skill for what:**
- Brand rules: `MOTION.md` and `brand.md` (written with `brand-intake`) come first, every time.
- An animated end card, price hit or logo sting: `motion-graphics` (HyperFrames).
- A beat-cut montage from music: `music-to-video`, or our own Python scripts.
- A 9:16 export check: `reel-export`.
- A frame-by-frame critique of a finished reel: `apple-design` plus `review-animations`. Read the
  `review-animations` standards for the subject of the reel, not for web UI. See
  `floor-reels/concepts/MOTION-CRITIQUE-20261008.md`.

**Running HyperFrames in a cloud session.** Use `hyperframes/hf.sh <command>`. It pins the CLI
(0.8.141), installs ffmpeg from apt if it is missing, and points at the pre-installed headless shell
in `/opt/pw-browsers`; the CLI's own Chrome download is blocked here. Start a project with
`hyperframes/new.sh <name>`.
- All scripts and fonts must be local. The render browser does not trust the session proxy, so a CDN
  `<script>` fails with `ERR_CERT_AUTHORITY_INVALID`. The starter ships GSAP 3.14.2.
- `check` is the gate: lint, runtime, layout and WCAG contrast. It caught a real authoring bug on day one.
- Measured on 8 Oct: a 3.5 s 1080×1920 composition renders in about 10 s on the fast `beginframe`
  path. Nothing is uploaded.
- `publish` and `cloud` send files to HeyGen. Do not use them without Rameez's go-ahead.

**HyperFrames gotchas found building the first reel** (`floor-reels/concepts/showcase/README.md`):
- GSAP rounds px values, so draw SVG lines with the path's real length (`getTotalLength()`), not
  `pathLength="1"`.
- Flex columns shrink their children. A rolling digit strip needs `flex: none`, and a counter placed
  per value with `tl.set` is safer than a rolling one.
- `tl.set` and `fromTo` are seek-safe. Do not drive visuals from `onUpdate` callbacks.
