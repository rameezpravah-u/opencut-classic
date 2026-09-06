# Rubik's Cube Lamp — five reels, five audiences

All 1080×1920, 25 fps, H.264. Every reel ships in two versions:

- `*-music.mp4` — with the generated music bed (and voice-over / sound effects where used). Ready to post.
- `*-clean.mp4` — no music, only voice-over / sound effects. Use this one when you want to add an in-app **trending sound** on Instagram or TikTok: trending audio only counts for reach when it is attached inside the app, it cannot be baked into the file.

Footage: the one real Rubik's Cube clip from Drive (`14-1`), the store's own product photos (three of them DSLR), and three of the in-room stills already in the Vibiz gallery. No new AI video was generated. Camera movement is virtual: sub-pixel push-ins, drifts and pans, beat "punch" zooms, handheld micro-shake on the Gen-Z cut, and motion-interpolated slow motion on the colour turns.

| # | File | Audience / job | Length | Music (generated, ElevenLabs Music v2) | Palette | Type |
|---|---|---|---|---|---|---|
| 1 | `R1-aesthetic` | Shared for how it looks. Loops seamlessly (ends on the opening amber frame). | 22 s | Dreamy lo-fi, 68 bpm; every colour change lands on a 2-beat hit | Muted film grade, light grain, cream captions, dusty-rose URL | Cormorant Garamond italic, lowercase, bottom-left |
| 2 | `R2-meaning` | Shared for what it does for your evening. **Voice-over reel.** | 24 s | Felt piano + nylon guitar, ducked −13 dB under the voice | Ivory + honey amber, the three colour words tinted to the lamp | Playfair Display, centred |
| 3 | `R3-design` | Design / architecture crowd: why a modern room needs it | 22 s | Minimal electronic, 100 bpm; cuts on the 4-beat grid | Monochrome-leaning grade, white + one amber accent, thin rules | Space Grotesk + Inter, left-aligned spec callouts |
| 4 | `R4-genz` | Gen-Z: fast, meme cadence, lowercase | 16 s | Phonk-style, 140 bpm; cut every 4 beats (1.71 s), punch zoom on every cut | Saturated +28 %, neon boxes: green `#3DFF8F`, red `#FF3B5C`, amber `#FFC542`, lilac `#C77DFF` | Archivo Black in caption boxes |
| 5 | `R5-3040` | 30–40 metro home-upgraders (female-led purchase): trust, price, warranty | 22 s | Indie-folk acoustic, 95 bpm; cuts every 4 beats (2.53 s) | Ivory + gold, one plum price box, warm vignette | Playfair Display + DM Sans kickers |

## Why these colours per audience

- **Aesthetic sharers** save and repost muted, film-like frames; the grade lowers contrast, lifts blacks and adds grain so the lamp's own colour is the only saturated thing on screen.
- **Meaning / broad 28–45**: ivory and honey amber read as home and warmth; the word "Amber / Green / Red" is tinted the exact lamp colour on screen so copy and product agree.
- **Design crowd**: near-monochrome with a single accent is the visual language of product design pages; the amber accent `#E8A24A` is the accent already used on nixwoods.com.
- **Gen-Z**: high saturation and neon caption boxes match how native creators caption; each box takes the colour of the lamp state it labels.
- **30–40**: warm neutrals plus one jewel tone (plum) signal premium and festive without shouting; gold is the trust/occasion colour for this buyer.

## Copy (all inside the brand's banned-word rules)

- R1: `9:40 pm` · `10:15 pm` · `11:58 pm` · *the lamp that knows what time it is.* · *rubik's cube lamp · nixwoods.com*
- R2 VO (Sarah, ElevenLabs premade — the Indian-English library voices need the Creator tier on this account): "Most lamps give you one light. This one gives you three. Amber, when the workday winds down. Green, for a slow evening. Red, for movie night. No app, no remote… you just turn the block. Solid sheesham. Hand-painted glass. Made in India. One lamp, for every version of your evening."
- R3: Design notes 01/02 → Glass → Base → Mechanism → Interface → At rest → Lifespan (8×8 in glass, 9×4.5 in sheesham base, three painted faces, no buttons/remote, 25,000-hour LED, 3-year wood warranty).
- R4: pov: your room at 2am → it changes colour btw → red = movie night → green = locked in → amber = golden hour. indoors. → no app. no remote. you just turn it. → it's real wood btw (not the plastic kind) → ₹2,999. yes really. → nixwoods.com / link in bio
- R5: Everyone asks about it. → Nobody guesses the price. → Three moods. One turn. → Solid sheesham. Hand-painted glass. → No bulbs to change. Nothing to charge. → Made by hand in Khatauli. → ₹2,999 (Free shipping · 3-year wood warranty · COD) → Stop buying boring lights.

## Suggested trending-sound direction for the clean versions

- R1: any slowed + reverb ambient sound trending in the "aesthetic room" niche.
- R3: clean tech-keynote / "satisfying" percussive sounds.
- R4: whatever phonk / speed-up edit sound is charting that week; cuts are on a 140 bpm 4-beat grid so most 140–150 bpm sounds will line up.
- R5: acoustic / feel-good home-tour sounds.

## Rebuild

```bash
pip install pillow numpy imageio-ffmpeg
# src/14-1.mp4 from Drive, rubik/ product stills (script: see products list), audio/ generated beds
python3 reels.py all both       # or: python3 reels.py 4 music
```
`reelkit.py` is the engine (camera moves, text layers, assembly); `reels.py` holds the five edits, timings and copy.

## Notes

- Ads Manager: the three Vibiz in-room stills are AI-generated images, so tick the AI-disclosure box when any of these reels runs as a paid ad (same as your existing Aurora ad).
- Music beds and the voice-over were generated on the NixWoods ElevenLabs workspace (about 4,800 credits total, roughly 50 US cents).

## System demos (`out/system/`)

Twelve reels rendered by `../system/make_reel.py` from the briefs in `../system/briefs/`, one per mechanism, all from the Higgsfield stills and Kling clips in `hf/` plus the real product clip. Each comes as `-music.mp4` and `-clean.mp4` (delivered as files; the mp4s are not committed, ~20 MB each), with a cover, a contact sheet and a `-timeline.json` that carries the pre-flight sheet.

| brief | mechanism | style / audience | length | funnel |
|---|---|---|---|---|
| T1-transformation | dark → flash → on → colour cycle | broad | 18 s | top |
| T1-transformation-ad27 | the same cut stretched ×1.5 for ads (Medium bucket 4.54x vs 0.98x Short) | broad, `Cube Lamp` name | 27 s | ad |
| LOOP-colour-loop | seamless amber → green → red → amber | aesthetic | 19 s | top |
| BA-before-after | tubelight room wipes to lamp-lit room | 30–40 | 16 s | mid |
| TRI-triptych | red · amber · green side by side, moving | design | 12 s | top/mid |
| K-kinetic | word-by-word hook over the backlit arc | Gen-Z | 14 s | top |
| L-listicle | 3 reasons, counter + caption | broad | 12 s | mid |
| SPEC-spec-sheet | numbers-only callouts with rules | design | 15 s | mid |
| VO-story | narrator script over new visuals | broad | 21 s | mid |
| UGC-pov | handheld, lowercase boxes, "pov:" | ugc | 16 s | top |
| PRICE-price-reveal | value stack → ₹2,999 → COD | 30–40 | 15 s | bottom |
| UNBOX-unboxing | kraft box → reveal → Diwali console | festive | 17 s | bottom / festive |
| TESTI-testimonial | real review over night footage | broad | – | not rendered: needs a real quote |
