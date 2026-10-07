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
