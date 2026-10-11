# Instagram references, read slide by slide

Captured 7 Oct with `system/ig_carousel.py` (headless Chromium, logged out). Every slide was looked
at, not summarised by a tool. The post reader (`vibiz_read_social_post`) only ever returns the
cover image plus a text description; it does not see a carousel. Do not brief from it alone.

`ig_carousel.py` needs the person's approval each run (it tells Chromium to trust the session's
egress-proxy CA), so it cannot run in Auto mode: switch to "Accept edits", approve the prompt.

## DeGkawhCB2j — @sannidhyabaweja, "bad ad vs good ad" (7 slides)

| # | Bad ad | Good ad | Rule |
|---|---|---|---|
| 1 | Native hair care: lavender studio still life | URO jars in a hand on concrete, a comment-reply sticker and two native caption boxes | Make it look native, not pretty |
| 2 | "Stop overexplaining" infographic: 9 boxes of text | Hand-written pink sticky note "Moms! This acne killer works!" stuck above the product, plus a **real** customer review screenshot (named reviewer) | Stop the thumb and sell the next click; don't explain every feature |
| 3 | Hamfest flyer: ten messages in one poster | Man's back, written on with a marker: "5 years of bacne gone in 8 days" | One messaging angle, the USP, stated literally on the body / product |
| 4 | Likes and comments | Ads Manager: purchase ROAS 0.43–0.60, conversion 1.12–2.77 % | Judge on ROAS and conversion, not vanity metrics |
| 5 | Busy multi-product store page | Landing page that repeats the ad's angle ("Stop acne & save 40%", press logos) | The page must match the ad |
| 6 | — | — | "Stop making pretty ads that flop in Ads Manager" |
| 7 | — | — | Share / follow CTA |

**Three NixLine statics built from this post were rejected by Rameez on 7 Oct ("the shittiest").**
Why, so it is not repeated:
- The lesson was applied as decoration (caption boxes, then a sticky note) pasted onto whatever frame
  was at hand. In the good ads the *photo itself* sells; the text is part of the scene.
- "Native" was read as "messy". The good ads are phone photos, but clean and product-first: you know
  instantly what the product is. The workshop frames show a lit stick over a dirty floor, plastic
  bags and cables — nobody can tell it is a floor lamp or picture it at home.
- A marker font on a pink square is not a sticky note. The reference note is physically in the photo.
- It was rendered before the concept was agreed with Rameez.
The real gap: there is no real photo of NixLine standing lit in a room. Get that shot (with a real
note in it) or agree a generated concept first; do not paper over the gap with overlays.

What the good ads have in common: a **real** photo; **one** claim; the claim is written **onto the
scene by hand** (sticky note, marker on skin), not set in a designer font; proof is a **real**
review with a name. The first NixLine "native" attempt (7 Oct) copied only slide 1's surface.

## DeJCF5-mrLl — @gameofai1, "these websites should be hidden" (8 slides)

Format: one AI-generated character carried through every slide (arrest, then a cell); a huge
two-tone headline; "$0 / month"; three icon rows; a closing "FOLLOW / comment WEBSITE" slide, a
comment-to-DM bait that drove 1.2K comments. Account is labelled "AI content".

| # | Tool | Slide claim | Checked 7 Oct |
|---|---|---|---|
| 2 | Steve AI | free text-to-video, scripts, avatars | free plan is watermarked; no watermark from $19/mo. Animated explainers, no product fidelity |
| 3 | Wireflo(w) | no card, no watermark, no cap | wireflow.ai: multi-model canvas; the free account only **builds** workflows — running video models needs a paid plan's credits |
| 4 | D-ID Studio | photo-to-video, talking avatars, lip-sync | trial only: ~5 min/month, **watermarked, commercial use excluded** |
| 5 | ZSky AI | no card, no watermark, no cap | zsky.ai: unlimited on a free account, but free output carries a "MADE WITH / zsky.ai" wordmark (Pro $19 removes it); API only on Max $99 |
| 6–7 | Pictory | text-to-video, summaries, drafts | trial: 3 projects, **watermarked**; paid from ~$19–25/mo |

None of the five is free *and* clean enough for a paid ad: ZSky watermarks free output, Wireflow
needs paid credits to generate, D-ID/Pictory/Steve AI watermark (D-ID also bars commercial use).
First pass on 7 Oct read only the search snippets and called ZSky and Wireflow usable; their own
pages corrected that. Full table: `system/FREE-TOOLS.md`.

## DeUFGDJE7kb: @suraj.dsgn, "Claude Motion: Designer's Resource Guide" (7 slides, captured 11 Oct)

Dark grain cover with a peach glow, then one website screenshot a slide, then a "follow and comment Claude"
slide that sells an eBook. Five resources, none an installable free tool:

| # | Resource | What it is | Checked 11 Oct |
|---|---|---|---|
| 2 | Prompt Motion | gallery of motion videos made with Claude, with the prompt or skill behind each | website; nothing to install. Reference library |
| 3 | Promptslove | `/promptslove-motion-gfx` Claude skill: questions, storyboard, 1080p video with beat-synced music | **paid**, $49 one-time (said to rise to $99), account needed; renderer not named. Not installed (free-first) |
| 4 | AI × Leaders | free prompt wall for Claude and ChatGPT motion graphics, no account | website; nothing to install |
| 5 | Claude Code Club | guide "Three levels of motion graphics with Claude Design" (build a motion system from a reference video) | article plus a paid club ($9/month); the method is what `brand-intake` and `MOTION.md` already do |
| 6 | Promptcat | 161 Opus 5.5 animation prompts: Lottie UI, procedural, product films | website; nothing to install. Lottie output is covered by the HyperFrames Lottie adapter |
