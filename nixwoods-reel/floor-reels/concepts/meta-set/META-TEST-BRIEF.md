# NixLine Diwali creative test — nixwoods.com (Meta)

Written 7 Oct 2026 with the `paid-social-brief` skill.

**Status, 7 Oct: built and paused, all 10 ads.** Nothing has spent.
- Campaign `120251841620130275` "COM | NixLine | Diwali creative test | Oct07": Sales, Advantage+
  campaign budget ₹3,500 a day (set by Rameez), PAUSED.
- Ad set `120251841624240275` "Broad IN 25-65 | Purchase": pixel `1018384867031221`, Purchase.
- Ads, each with Facebook and Instagram (@nix_woods, `17841470815671852`) and the AI label declared:
  V1A `120251841889860275`, V1B `120251841890390275`, V2A `120251841891080275`,
  V2B `120251841891510275`, S-G `120251841891980275`, S-A `120251841892410275`,
  S-B `120251841892970275`, S-C `120251841894220275`, S-D `120251841894550275`,
  S-F `120251841894950275`. The statics have 4:5 for Feed and 9:16 for Stories and Reels.
- How the videos got in: the Meta connector can't upload video to this account yet, so Adspirer
  (connected to the same account) uploaded them. The final ads were then built with the Meta
  connector, because Adspirer cannot set the AI label. The intermediate ads, plus a first set of
  statics without Instagram, were deleted unrun.
- To launch: publish the campaign in Ads Manager after the ads pass review.

## 1. Foundation (all checked 7 Oct)

| | |
|---|---|
| Product | NixLine – Solid Teakwood Floor Lamp |
| Landing page | https://nixwoods.com/products/nix-line-solid-wood-floor-lamp |
| Offer | ₹999, compare-at ₹1,599 (compare-at set in Shopify today; was ₹1,399, backup in `web/nixline-price-backup-20261007.json`) |
| COD / delivery | True on .com: Shopify domestic rates "Prepaid – Free Express Shipping" ₹0 and "COD – Standard Shipping" ₹0 |
| Ad account | NixWoods `9020821008043944` (.com only, never the Shopdeck / .in accounts) |
| Page / Instagram | Nix Woods `1206467462858268` / @nix_woods |
| Pixel, event | nixwoods.com `1018384867031221`, Purchase |
| Deadline | Diwali 8 Nov. Ads tire in about 20 days, so launch this week |

**Claims allowed:** solid Indian teak, no MDF, no veneer, 30 inches, upright on its own teak block,
2700–3000K LED, plug in, no assembly, handmade in Uttar Pradesh, ₹999 (₹1,599), cash on delivery,
free delivery. **Not allowed:** brightness numbers, delivery times, reviews or ratings (none
are permission-cleared), "Big Billion" or any other marketplace sale name, banned words
(luxury, premium, exquisite and the rest of the list).

## 2. The test

**Question:** which of the new NixLine concepts sell on .com, so that 2–3 can be scaled into Diwali?

| Code | Asset | Hypothesis it tests |
|---|---|---|
| V1A | Tubelight → teak, hook "Still lit by one tubelight?" | Recognition: people stop for their own problem |
| V1B | Same video, hook "Watch this corner. Wait for the switch." | Anticipation: people wait for the change |
| V2A | One line of light, hook "Count the cuts. The line won't move." | A small game holds attention |
| V2B | Same video, hook "₹999. Solid teak. One warm line." | Price first, the Shopdeck winner's lever |
| S-A | Static: Diwali dusk corner, "Light up the corner." | The .in winner's look on .com |
| S-B | Static: tubelight vs NixLine split | Before/after in one frame |
| S-C | Static: reading chair, "Your evening, in warm light." | A person in the scene |
| S-D | Static: gift crate, "A gift that glows." | Diwali gifting |
| S-F | Static: metal lamp vs solid teak | Material comparison |
| S-G | Static: "The tallest diya in the family." | Quirky, festive |

The two hook pairs differ only in the first 2 seconds of on-screen text. Everything else is held
the same: video, caption, headline, landing page, ad set and start time.

## 3. Build sheet (Ads Manager)

**Campaign:** `COM | NixLine | Diwali creative test | Oct07`, Sales, Advantage+ campaign budget,
highest volume. **Daily budget: open, Rameez to set.** For scale, the account's cold NixLine-type
spend has run at about ₹3,500 a day, and each ad needs roughly ₹1,000+ before it can be judged.

**Ad set:** `Broad IN 25-65 | Purchase`. India; age 25–65 with Advantage+ audience on;
Advantage+ placements; conversion location Website; pixel `1018384867031221`, Purchase; 7-day click
and 1-day view attribution. One ad set holds all ten ads, because Meta's current delivery system
rewards many distinct concepts in one place.

**Every ad:**
- **Identity:** Nix Woods page plus **@nix_woods**. Without the Instagram account the ad runs on Facebook only.
- **AI info: switch ON for all ten.** Every ad contains generated room scenes, and India requires the label.
- **Primary text,** identical on all ten so the tests stay clean:
  > One line of warm light, in solid Indian teak. No MDF, no veneer.
  >
  > NixLine · 30 inches · upright on its own teak block · 2700–3000K LED. Plug in, no assembly.
  >
  > ₹999 (was ₹1,599) · Cash on delivery · Free delivery.
- **Headline:** `NixLine solid teak floor lamp · ₹999`
- **Description:** `Cash on delivery · Free delivery`
- **Call to action:** Shop now
- **Website URL:** `https://nixwoods.com/products/nix-line-solid-wood-floor-lamp?utm_source=meta&utm_medium=paid_social&utm_campaign=nixline_diwali_test_oct&utm_content=<CODE>`
- **Advantage+ creative enhancements:** off. They would change the hook text being tested.

**Files.** Download from the links below. In the repo they sit in `floor-reels/concepts/meta-set/`.
For the statics, use the 4:5 file for Feed and add the 9:16 file for Stories and Reels.

Base: `https://raw.githubusercontent.com/rameezpravah-u/opencut-classic/00fa5a84caeb4a062cb3b5d09bef3899fb0dda66/nixwoods-reel/floor-reels/concepts/meta-set/`

| Code | Ad name | Files (append to the base URL) |
|---|---|---|
| V1A | `NixLine V1A tubelight recognition` | `NX-META-V1-tubelight-to-teak-9x16.mp4` (cover `thumbs/NX-META-V1-tubelight-to-teak-9x16.jpg`) |
| V1B | `NixLine V1B tubelight anticipation` | `NX-META-V1-tubelight-to-teak-9x16-hookB.mp4` (cover `thumbs/NX-META-V1-tubelight-to-teak-9x16-hookB.jpg`) |
| V2A | `NixLine V2A one-line game` | `NX-META-V2-one-line-9x16-hookA.mp4` (cover `thumbs/NX-META-V2-one-line-9x16-hookA.jpg`) |
| V2B | `NixLine V2B one-line price-first` | `NX-META-V2-one-line-9x16-hookB.mp4` (cover `thumbs/NX-META-V2-one-line-9x16-hookB.jpg`) |
| S-A | `NixLine S-A diwali corner` | `NX-META-A-diwali-price-drop-4x5.jpg` + `-9x16.jpg` |
| S-B | `NixLine S-B tubelight vs teak` | `NX-META-B-before-after-4x5.jpg` + `-9x16.jpg` |
| S-C | `NixLine S-C her evening` | `NX-META-C-her-evening-4x5.jpg` + `-9x16.jpg` |
| S-D | `NixLine S-D diwali gift` | `NX-META-D-diwali-gift-4x5.jpg` + `-9x16.jpg` |
| S-F | `NixLine S-F metal vs teak` | `NX-META-F-metal-vs-teak-4x5.jpg` + `-9x16.jpg` |
| S-G | `NixLine S-G tallest diya` | `NX-META-G-tallest-diya-4x5.jpg` + `-9x16.jpg` |

## 4. Guardrails and review

**Launch check:** all ten ads approved; the AI label on; @nix_woods attached; open one ad's URL
and confirm it shows ₹999 / ₹1,599 and COD at checkout.

**Day 3 read** (pull ad-level data: spend, impressions, 3-second plays, ThruPlays, outbound
clicks, add to cart, purchases, purchase value):
- **Hook pairs:** compare 3-second plays ÷ impressions within each pair, once both ads have about
  3,000 impressions. If one side of a pair is starved (under 1,000 impressions while its twin
  has 3,000 or more), move the four videos into their own ad set with an even split, or run a
  Meta A/B test, rather than calling a winner.
- **Concepts:** pause any ad that has spent twice the target cost per purchase with no add to
  cart. The target cost per purchase is open: Rameez to set it from the NixLine margin.

**Day 7 decision:** keep the 2–3 ads with the lowest cost per purchase (at least 3 purchases
each); make one new variation of each winner; turn the rest off. Report paid results separately
from the organic posts of V1 and V2 (Instagram, 10 and 11 Oct).

**Still open, for the owner:** daily budget; target cost per purchase; excluding recent
purchasers (only if that audience already exists in the account).
