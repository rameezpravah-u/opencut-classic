# NixWoods Reel System — research, structure and rules

Built 6 Sep 2026 from: your own Meta ad account (last 90 days, 40 ads), the Meta Ad Library (India, "wooden lamp" / "table lamp"), competitor sites (Ikari Homes, Phanash), the store's Rubik's Cube product page, and current 2026 short-form research (sources listed at the end).

---

## 0. Where this sits in the system you already run

This reel system is the **creative layer** of the NixWoods system that exists elsewhere. It does not replace any of it; it feeds it.

| Existing piece | Where it lives | What the reel system takes from it | What it hands back |
|---|---|---|---|
| **Ads Engine (.com) v2** | `Code` repo, branch `claude/nixwoods-funnel-audit-hg4dk9`, `NIXWOODS-ADS-ENGINE-COM.md` | the locked creative rules (§7), the six-check pre-flight, the naming convention `COM \| Product \| Audience \| Objective \| Date`, the kill threshold, the category focus (wall lights + pendants get new money first until 2026-11-04) | every render writes a pre-flight sheet into `<name>-timeline.json` with the checks a script can verify already filled (two colours, banned words, trademark, dispatch claims, hook timing, safe zone, AI disclosure, length) and the manual ones left as boxes |
| **Creative learnings** | same branch, `ads-system/COM-creative-learnings.md` | the control creative (Rubik's warm-ambient video, 5.69x), the proven lines, the failed hooks, hypotheses H1–H4 | each brief carries its hypothesis id; `--rank` orders briefs the way layer 3 of the Growth System orders concepts |
| **Growth System** (router + 12 layers, `run_system.py`) | artifact 2026-08-31; the code was never pushed from your machine | layer 3's idea: every opening line passes Gap / Truth / Pull gates and a trademark check before it prints, and concepts are ordered by content-tag index × hook score; the night tag's 2.17x return | `system/hooks.py` re-implements the gates and a /12 score from the published description (labelled as such); `presets.json → engine.tag_index` holds the one tag value on record and is where the rest go when the router's numbers are exported |
| **Social Master Playbook** | Drive, `NixWoods-Social-Master-Playbook.md` (2026-07-03) | the five pillars and the weekly rotation, the 13:00 / 20:30 IST slots, the palette (espresso, warm bone, one amber accent), Fraunces + Inter, "hook < 3 s, warm ambient audio, no meme/EDM", the Sep–Nov festive calendar | a `social` style preset (Fraunces/Inter, the playbook palette); every brief names its pillar so the monthly grid can pull reels by slot |
| **AD-COPY.md** (wall-light ad copy set) | Drive, 2026-09-04 | the copy formula (parallel contrast + one material + one real number + persona + free shipping + ORDER_NOW), "short copy wins", the length finding (27.7 s Medium bucket 4.54x vs 0.98x Short), the AI-disclosure step | `brief.stretch` makes a 25–30 s ad cut from any organic cut (`T1-transformation-ad27.json`); the pre-flight lists the disclosure |
| **NixWoods-Master.md** | Drive | brand voice and the banned-word list | the copy lint refuses to render a banned word |

Three consequences worth stating plainly:

1. **Rubik's reels are organic-first right now.** The category focus says new ad money and new creative go to wall lights and pendants until 4 Nov; the Sep03 Rubik's campaign was turned off deliberately and stays off. So this set posts on Instagram (hero slots, 4–5 reels a week) and YouTube Shorts; the ad cuts wait for the next Rubik's window, or the same mechanisms get run on Aurora and the pendants first (add them under `products` in `presets.json`; the twelve angles in §5 are the shot list).
2. **The trademark.** The Growth System flagged the trademark in the product's Shopify title and AD-COPY.md bans trademark references in ads. Organic reels keep the store name; the ad cut uses `copy.name_ad` ("Cube Lamp"). The lint prints a warning on every trademark hit so it is never silent.
3. **Generated frames.** Fourteen stills and five clips here are Higgsfield. The engine's own data says the one AI-rendered problem image was the account's lowest-quality ad, and that real footage wins the hero slot. Use these frames as B-roll around the real product clip (every demo does), disclose them in Ads Manager, and shoot the real "before" (tubelight room, lamp off) when the next shoot happens.

---

## 1. What is working — evidence, not opinion

### 1.1 Your own account (last 90 days)

| Ad | CTR | Purchases | ROAS | Lesson |
|---|---|---|---|---|
| GlassBlock "Bedside video" | 4.29 % | 98 | 4.7 | A dark bedroom + the lamp as the only light + colour change is your single best creative. Night scene beats daylight. |
| Aurora "Wood changes everything" | 3.66 % | 62 | 3.6 | A contrast claim in five words. Material as the hook. |
| Wall Lights, Teak, Women 35–64 | 5.59 % | 9 | 3.3 | Highest CTR on the account: women 35–64 respond to warmth + wood. |
| Aurora "Transform your walls" | 3.5 % | 13 | 10.8 | Transformation promise, wall-light context. |
| "Test / Craftsmanship" · "Test / In-Room Night" | 4.1–4.2 % | – | – | Craft and night-room hooks stop the thumb even when the funnel isn't set up. |
| GlassBlock "Three Moods red-green lifestyle" static | 4.27 % | – | – | Two colours in one frame is the strongest static. |
| Rubik's "Single image, glass + sheesham" | 1.36 % | 1 | 1.1 | A plain product photo with a materials headline does not stop anyone. |
| Rosewood pendant statics | 1.2–1.5 % | – | – | Pendants need a room and a person, not a packshot. |

Rules that fall out of this:
1. **Night + glow + colour change** is the NixWoods hook. Every Rubik's reel opens in the dark.
2. **Contrast copy in ≤5 words** ("Wood changes everything", "Not brighter. Warmer.") beats feature lists.
3. **Transformation** (before/after, off/on, one colour → another) outperforms description.
4. **Women 35–64 and 45–54** are your best buyers; write for them first, Gen-Z second.
5. Statics only work when two colour states share one frame; otherwise use video.

### 1.2 Competitors (Ad Library IN + sites)

- **Ikari Homes**: "Boho furniture & lamps for modern homes", constant "UP TO 60 % OFF", monsoon/festive sale hooks, treated seasoned wood, COD + 7-day returns. Price ladder ₹999 → ₹24,990.
- **Phanash**: cordless/rechargeable is the whole pitch ("Cordless Beauty, Everyday Ease"), touch dimming, 3000K, 1-year warranty, ₹1,499–₹8,500, tiers named Premium/Elite/Signature.
- **Mâzia Home / UrbanNivasa / VibeCrafts / Lumitop**: "hand-carved solid wood lamp", multi-product catalog carousels, generic "modern floor lamp for living room" SEO-style titles.
- Nobody in the Indian set is running a **single-hero, night-scene, colour-turn video**. That lane is still open (your master doc said this in June; the Ad Library confirms it in September).

Selling points to press that competitors can't: three hand-painted faces / **turn = colour** (no app, no remote, nothing to charge), real glass + solid sheesham, one-of-a-kind grain, 25,000-hour LED, 3-year wood warranty, made in Khatauli, ₹2,999 with free shipping and COD.

### 1.3 Platform research (2026)

- Viewers decide in **~1.7 s**; ~90 % of failing reels lose in the first 3 s. Pattern-interrupt hooks hold 72–84 % at 3 s, curiosity 65–78 %, questions 58–72 %, bold claims 55–70 %.
- Ranking: **completion rate**, then **shares (DM sends 3–5× a like)**, then **saves (~3×)**. Likes and follower count barely matter. Under 90 s for non-follower reach; 15–30 s is the sweet spot for ads.
- **Originality**: near-duplicate uploads get suppressed. Every variant must differ in cut, copy and colour, not just music.
- **85 % watch muted**: the caption is the video. Text hook ≤ 12 words, on screen inside 2 s.
- Converting formats by hit-rate: Demo, Testimonial, Unboxing, Before/After, Listicle, Split-screen. Before/After beats plain product shots by 60–80 % in engagement; ASMR unboxing lifts saves 25–40 %. Top of funnel: ASMR / trend; mid: demo, before-after, listicle; bottom: review, social proof.
- India small-brand signals: raw phone-camera reels outperform studio polish for reach; humour and "internal debate" (two personas) formats are rising; festive (Diwali) framing works Sept–Nov.

---

## 1.4 The four top products, and what the numbers say to write (6 Sep 2026)

Ranked by 90-day net sales, from Shopify:

| Product | Net sales / orders | Best ad signal | What that means for the writing |
|---|---|---|---|
| **Aurora Linear Wall Light** ₹1,999 | ₹525k · 194 | "Wood changes everything" 3.66% CTR, 3.64x · "Transform your walls" 9.41x on warm · Wall lights to women 35–64 **5.56% CTR**, the account's highest | Write to **stop**. Short contrast claims, a visible before and after, the wall as the subject. This product carries the top of the funnel. |
| **Rubik's Cube Lamp** ₹2,999 | ₹347k · 121 | Bedside video 4.31% CTR, 4.71x · "Not just a lamp. A mood." 5.69x · single-image static 1.31% | Night, glow, colour change. A plain packshot does not work on this product and never has. |
| **Scandinavian Rosewood Pendant** ₹7,599 | ₹124k · 13 | Static B **1.52% CTR but 13.1x ROAS** · Nordic pendant 14.9x | Write to **qualify**, not to stop. Low CTR is fine and even correct: name a person who owns a dining table in the first two seconds and let everyone else scroll. Price early — it is a shortlisted purchase, not an impulse. |
| **Double Arm Teak Pendant** ₹9,999 | ₹59k · 4 | thin data; inherits the pendant pattern | Sell the object. Twin lines cut into one piece of teak is the whole idea; the specification is the romance. |

The split that matters: **wall lights are a CTR product, pendants are a ROAS product.** A pendant reel judged on CTR looks like a failure and is not one. Judge pendants on purchases and ROAS, wall lights on CTR and reach.

**A second finding, from the same pull:** a horizontal fixture in a vertical frame is a craft problem, not a cropping problem. A centre 9:16 crop of a four-foot pendant removes the four feet. Every wide shot of a linear product uses `fit: contain` (the whole fixture over a blurred, dimmed copy of its own scene); only diagonal macros are cropped to fill.

---

## 2. Hook library (tested patterns → NixWoods lines)

Each hook = text on frame 1 + a visual pattern interrupt + the first sound.

| Type | Pattern | NixWoods lines (≤ 12 words) |
|---|---|---|
| Pattern interrupt | dark → light snaps on; colour flips on beat | *Still lit by one tubelight?* · *Watch the room change.* |
| Contrast claim | X not Y | *Not brighter. Warmer.* · *Wood changes everything.* · *A lamp, not a gadget.* |
| Curiosity gap | withhold the mechanism | *Nobody guesses how the colour changes.* · *There's no switch. Watch.* |
| POV / relatable | pov: + situation | *pov: your room at 2am* · *pov: guests keep asking about the lamp* |
| Confession / social proof | number + moment | *98 homes bought this after one video.* · *175 homes in 90 days.* |
| Question | one they already ask | *Why does your room feel like an office?* |
| Price shock | reveal late | *Everyone asks about it. Nobody guesses the price.* |
| Listicle | 3 things | *3 moods. 1 turn.* · *3 reasons this isn't plastic.* |
| Festive | occasion | *The gift they'll actually remember.* (Diwali / wedding season) |

Lines already proven on the account or in organic (from the Ads Engine, the creative learnings, the Social Playbook), with their evidence, live in `presets.json → engine.hooks_proven`; `python3 hooks.py` scores them and any new line the same way (gates gap/truth/pull, then brevity, specificity and family match, out of 12). Failed framings to avoid: gifting/nostalgia as a static, an AI render as the hero, a single-colour cube, discount-led copy.

---

## 3. Script-writing rules (voice-over and captions)

- Structure: **Hook → Problem → Turn (mechanism) → Proof → CTA**. Or PAS: name the pain, twist it, show the turn.
- Voice-over pace **130–150 wpm**: 15 s ≈ 40 words, 20 s ≈ 50, 30 s ≈ 75. Sentences under 12 words. Contractions. Mark stress in the script. Conversational, never announcer.
- Caption ≠ transcript: captions carry the 3–6 word version of each VO line.
- The CTA repeats the benefit in operational language: *Turn the block. nixwoods.com* beats *Shop now*.
- Brand voice: warm, plain, specific. Banned: discover, elevate, luxury, premium, exquisite, journey, curated, unlock, stunning, delve, realm.
- Three VO registers to alternate (see `scripts/vo-scripts.md`): **Narrator** (Reel 2 style), **UGC-casual** (first person, phone-mic energy), **Spec-fast** (numbers, staccato).

---

## 4. Typography and placement system

Safe area on 1080×1920 (Instagram 2026): top 220 px and bottom ~400 px are covered by UI, right ~130 px by the action rail. **Everything important lives in y = 230…1500, x = 70…950.**

Slots used by the engine (`reelkit.SLOTS`): `top` 300 · `upper` 560 · `centre` 880 · `lower` 1200 · `low` 1330 · `bottom` 1420. `reelkit.auto_slot()` reads the frame, finds the bright product band and picks the first slot that doesn't cover it (lower third first, then upper).

Sizes at 1080 wide: headline **64–88 px**, caption box **66–84 px**, secondary **36–44 px**, kicker **28–30 px** tracked. Minimum readable 36 px. Max 12 words per screen, 2–3 lines.

Type pairs by audience (fonts in `assets/`):

| Audience | Headline | Support | Why |
|---|---|---|---|
| Aesthetic / editorial | Cormorant Garamond italic, lowercase | DM Sans | quiet, film-caption feel; shares for taste |
| Broad 28–45 / VO reels | Playfair Display 600 | DM Sans 500 | matches existing NixWoods reels |
| Design crowd | Space Grotesk 700 | Inter 300 | product-page / keynote register |
| Gen-Z | Archivo Black in colour boxes (Space Grotesk 700 for ₹) | – | native caption-box look; note Archivo Black has no ₹ glyph |
| 30–40 trust | Playfair Display 600/700 | DM Sans | serif = considered purchase; one jewel-tone box for price |

Placement rules: never on the glass block; hook text appears by 0.3 s and holds ≥ 1.2 s; one idea per screen; colour-name words take the lamp's actual colour; price gets its own screen; end card = logo + one line + URL, 2–2.6 s.

---

## 5. Camera system (works on static images)

All moves are rendered at 2× supersample so they are sub-pixel smooth (`reelkit.cam_filter`).

| Move | Params | Use |
|---|---|---|
| Push-in | z 1.0→1.12 over the shot | hero reveals, hooks |
| Pull-out | z 1.12→1.0 | endings, loops |
| Drift / pan | z 1.12, px −0.3→0.3 | wide rooms, shelves |
| Tilt | py 0.3→−0.1 | tall scenes, reveal from table to lamp |
| Beat punch | punch 0.08–0.10 for 5 frames | every cut on a fast track |
| Handheld | shake 2–3 px | UGC / Gen-Z |
| Slow motion | slow 1.2–1.5 (motion-interpolated) | the colour turn |
| Dutch | source shot tilted (Higgsfield still #11) | graphic beats |

Cinematic angles to shoot or generate for every product: low-angle hero, top-down flat lay, 100 mm macro corner, hands-turning closeup, wide room at blue hour, bedside three-quarter, desk, unboxing, backlit silhouette, mirror reflection, festive console, dutch detail. Twelve of these were generated for the Rubik's Cube with Higgsfield (`hf/`), locked to the real product photo.

For real parallax (foreground/background separation) use Higgsfield image-to-video (Kling 3.0, ~9 credits per 5 s) on a generated still, then cut it like footage. Five are done for the Rubik's Cube (`rubik-reels/hf/k00`–`k04`: hero dolly, hands turning amber→green, room dolly, backlit arc, Diwali push) plus two "before" states (`hf12` lamp off at dusk, `hf13` room under a tubelight) for the transformation and before/after mechanisms. Prompts and credits: `rubik-reels/hf/PROMPTS.md`. The mechanisms use a clip when it exists and fall back to the still it was made from.

Transitions (`reelkit.TRANS`): cut (default), dissolve, fade, **flash** (white dip, 0.18 s, for beat hits), dip-to-black, zoom, whip (smoothleft), circle, slide.

---

## 6. Reel mechanisms (the different styles)

Each mechanism is a function in `mechanisms.py` that turns a brief into a reel. Pick by funnel stage.

| # | Mechanism | Funnel | What it does | Best music |
|---|---|---|---|---|
| 1 | **Off→On transformation** | top | dark room, flash, lamp on, colour cycle | cinematic hit |
| 2 | **Colour-cycle loop** | top | seamless amber→green→red→amber loop, no CTA until the end card | lo-fi |
| 3 | **Before/After wipe** | mid | overhead-light room wipes to lamp-lit room | soft build |
| 4 | **Triptych** | top/mid | three colour states side by side, moving | electronic |
| 5 | **Kinetic-text hook** | top | word-by-word pop over a static hero, one claim | phonk / trap |
| 6 | **Listicle 3-1-3** | mid | numbered "3 reasons", counter + caption | indie |
| 7 | **Spec sheet** | mid | design-notes callouts with rules | minimal |
| 8 | **Voice-over story** | mid | narrator reel (R2 style) | felt piano, ducked |
| 9 | **UGC / POV** | top | handheld shake, lowercase, "pov:" boxes | trending sound |
| 10 | **Price reveal** | bottom | value stack → big price box → COD/warranty | acoustic |
| 11 | **Unboxing / gift** | bottom / festive | kraft box, tissue, reveal, "the gift they'll remember" | warm |
| 12 | **Testimonial card** | bottom | real review text over night footage (needs a real quote) | soft |

Rotation that respects the originality rule: never post two of the same mechanism in a row; change hook type, colour palette and music every time.

---

## 7. Production system (how to run it)

```
brief.json  →  make_reel.py  →  out/<name>-music.mp4 + out/<name>-clean.mp4 + cover.jpg + sheet.png
```

A brief names the mechanism, product, style (audience), assets, copy lines and music. `make_reel.py` lints the copy (banned words, ≤12 words a screen), builds the mechanism, checks every text layer against the safe zone and the hook rule, renders music + clean versions, and writes a cover, a contact sheet and a timeline JSON for review. Fonts, palettes, slots, camera moves and product assets come from `system/presets.json`. Twelve example briefs, one per mechanism, are in `system/briefs/`; rendered demos are in `rubik-reels/out/system/`. Schema and how to add a product or a mechanism: `system/README.md`.

Weekly cadence (3–5 reels/week): Mon transformation · Wed mechanism of the week · Fri UGC/POV · plus one price/festive reel; re-cut the best performer after 7 days with a new hook, never a straight repost.

Measure: hook rate (3-s views ÷ plays), hold (completion), shares, saves, then CTR and CPA. A reel that gets shares but no clicks becomes an ad with a price-reveal cut.

---

## 8. Quality gates (what the system refuses to do)

Every reel passes six gates before it exists as an mp4. The first five run in code; the sixth is you.

| Gate | Runs where | Refuses | Why it exists |
|---|---|---|---|
| **1. Asset fidelity** | `presets.json → assets.status / clip_status`, enforced in `mechanisms.Build` | any generated still or clip marked `rejected`; falls back to the real product footage | 6 Sep: a generated "hands turning" frame showed the glass as a loose cube lifted off the base. The product is an 8×8×3 in slab that turns *on* its base. `qa.py` puts every generated asset next to the real reference frames in `rubik-reels/ref/`; nothing enters a cut until it is compared and marked approved. For hands shots, give the model a real frame of the gesture as a second reference, not just the packshot. |
| **2. Copy lint** | `make_reel.lint` | banned words, more than 12 words on a screen; warns on the trademark | brand voice (NixWoods-Master.md), AD-COPY.md trademark rule |
| **3. Hook gates** | `hooks.py` | prints the Gap / Truth / Pull result and a /12 score on every render; `--rank` orders briefs by it | Growth System layer 3 |
| **4. Placement** | `reelkit.auto_slot` + per-asset slot overrides + `make_reel.check_cues` | text on the lamp, text outside the safe zone, a hook later than 0.3 s or shorter than 1.2 s | the captions-on-the-lamp note from the first Rubik's set; Instagram UI overlays |
| **5. Ads pre-flight** | `make_reel.preflight` → `<name>-timeline.json` | nothing (it reports): ≥2 colours, dispatch claims, trademark, AI disclosure, length bucket, plus the manual boxes (landing, visual confirmation, control, kill threshold) | Ads Engine §7 six checks; the 3 Sep H1 ads were created PAUSED for exactly the checks this sheet now fills in |
| **6. Visual confirmation** | you, on the mp4 | anything the contact sheet cannot show: motion, pacing, sound | the locked rule: never deploy a creative that hasn't been watched |

Sources, registered not typed: `sources.py` scans any product video for its red / green / amber / warm segments and writes them into `presets.json`, so a new clip (the campaign video, a new shoot) becomes cut-ready without hand-timed timestamps. On the hero clip it reproduces the hand-timed states within 0.25 s.

---

## Sources

Own data: Meta ad account 9020821008043944 (ads_get_ad_entities, last 90 days). Meta Ad Library search, India, "wooden lamp", "table lamp". Sites: ikarihomes.com, phanash.com, nixwoods.com/products/rubiks-cube-table-lamp-sheesham-wood.

- [Instagram Safe Zone Guide 2026 (Outfy)](https://www.outfy.com/blog/instagram-safe-zone/) · [Kreatli Reels safe zone](https://kreatli.com/guides/instagram-reels-safe-zone) · [Pod2Reels safe zone](https://www.pod2reels.com/blog/instagram-reels-safe-zone-guide)
- [OpusClip: hooks that go viral 2026](https://www.opus.pro/blog/tiktok-hooks-that-go-viral-2026) · [Trendtrack: best performing ad hooks](https://www.trendtrack.io/blog-post/best-performing-ad-hooks) · [Taggbox: Instagram hooks](https://taggbox.com/blog/best-instagram-hooks/)
- [Sovran: Hook-Body-CTA framework](https://sovran.ai/blog/hook-body-cta-video-ad-structure) · [ChatCut: script writing 2026](https://chatcut.io/blog/how-to-write-a-script-for-a-video-2026) · [Lazybird: voice-over script templates](https://www.lazybird.app/blog/voice-over-script-example)
- [SocialPilot: Reels algorithm 2026](https://www.socialpilot.co/blog/instagram-reels-algorithm) · [CreatorFlow: algorithm 2026](https://creatorflow.so/blog/instagram-algorithm-2026/) · [Fastlane: Reels algorithm 2026](https://www.usefastlane.ai/blog/instagram-reels-algorithm-2026)
- [Vaizle: Reel trends 2026](https://insights.vaizle.com/instagram-reel-trends/) · [Passionbits: viral Instagram trends India 2026](https://passionbits.io/blog/10-viral-instagram-trends-in-india-for-consumer-brands-march-2026-part-1/) · [Inspire Product: Reels for small business India](https://inspireproduct.in/instagram-reels-small-business-growth-india/)
- [Blitzcut: caption fonts 2026](https://blitzcutai.com/blog/best-caption-fonts-reels-2026) · [Made Good Designs: fonts for Reels](https://madegooddesigns.com/best-fonts-for-reels/) · [EMAX: caption fonts readability](https://emax.studio/blog/best-caption-fonts-for-ai-reels-2026)
- [RocketShip HQ: text overlays in video ads](https://www.rocketshiphq.com/text-overlays-video-ads-mobile/) · [Highviz: Reels benchmarks from 346 reels](https://www.highviz.io/instagram-reels-report/) · [OpusClip: caption best practices](https://www.opus.pro/blog/instagram-reels-caption-subtitle-best-practices)
- [Motion: visual ad formats library](https://motionapp.com/library/formats/) · [Balistro: Instagram ad creative ideas 2026](https://www.balistro.com/instagram-ad-creative-ideas-convert-2026/) · [Creetr: unboxing video guide](https://creetr.com/blog/unboxing-video-guide)
- [Hawky: DTC Meta ad hooks 2026](https://hawky.ai/blog/best-dtc-meta-ad-hooks) · [Webtonic: 31 ad hooks](https://www.webtonic.io/blog/best-ad-hooks) · [AdLibrary: Meta creative best practices](https://adlibrary.com/posts/meta-ad-creative-best-practices)
- [Kudoflix: Ken Burns effect](https://kudoflix.com/blog/2026/08/04/ken-burns-effect/) · [Sketchbooky: Ken Burns and 2.5D](https://sketchbooky.wordpress.com/2023/06/07/the-ken-burns-effect-and-2-5d-for-after-effects/)
