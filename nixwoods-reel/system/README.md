# NixWoods reel system

```
brief.json ──▶ make_reel.py ──▶ mechanisms.py (12 styles) ──▶ reelkit.py (camera, text, ffmpeg)
                    │                    │
               presets.json        auto-placement off the product (reelkit.auto_slot)
          (fonts · palettes · slots · safe zone · camera moves · product assets)
```

Read `PLAYBOOK.md` first: it has the evidence (own ad account + competitors + 2026 platform data), the hook library, the script rules, the typography/placement rules, the camera system and the twelve mechanisms.

## Run

```bash
pip install pillow numpy imageio-ffmpeg
# asset root needs: src/14-1.mp4 (Drive clip), audio/*.mp3 (ElevenLabs music/VO/SFX), hf/*.jpg|mp4 (Higgsfield)
python3 system/make_reel.py system/briefs/T1-transformation.json --root <asset-root> --audio both
```

Outputs in `<root>/out/system/`: `<name>-music.mp4`, `<name>-clean.mp4` (for trending audio in-app), `<name>-cover.jpg`, `<name>-sheet.png` (contact sheet, 2 fps) and `<name>-timeline.json` (every shot, cue, audio and check result).

The runner refuses to render when copy contains a banned word or a screen has more than 12 words (`--force` overrides) and warns when a text layer leaves the safe zone or the hook is late.

## Brief schema

| key | meaning |
|---|---|
| `name` | output name |
| `mechanism` | one of `transformation colour_loop before_after triptych kinetic listicle spec_sheet vo_story ugc_pov price_reveal unboxing testimonial` |
| `product` | key in `presets.json → products` (assets, colour states, default copy) |
| `style` | audience preset: `aesthetic broad design genz 3040 festive ugc` (fonts, palette, case, grade, default music, shake/punch) |
| `style_overrides` | any style field, e.g. `{"headline_size": 72}` |
| `music`, `music_offset`, `music_gain` | track path (relative to root), negative offset = start inside the track |
| `copy` | mechanism-specific lines; anything omitted falls back to the product defaults |
| `assets` | override `video`, `stills{}`, `clips{}`, `sfx{}` per brief |
| `vo`, `vo_offset`, `vo_lines` | voice-over reels only: `[[start, end, caption, colour|null], …]` |
| `cut`, `per_word`, `cover_t`, `grade`, `sfx` | pacing, kinetic word gap, cover frame time, custom ffmpeg grade, SFX on/off |

Twelve example briefs live in `briefs/`, one per mechanism. `TESTI-testimonial.json` will not render until a real quote and name are pasted in.

## Adding a product

Add an entry under `products` in `presets.json`: name, price, URL, default copy, the source video with its colour-state timestamps, the Higgsfield stills by role (`hero flatlay macro hands room bedside_red desk_green unbox backlit mirror diwali dutch_green hero_off room_before`) and any Kling clips. The twelve cinematic angles to generate for every product are listed in `PLAYBOOK.md §5`; the Higgsfield prompts that produced this set are in `rubik-reels/hf/PROMPTS.md`.

## Adding a mechanism

Decorate a function in `mechanisms.py` with `@mechanism(name, funnel, note)`; use `Build` (`state / still / clip / pre / card` for shots, `say / cue` for text, `music / sfx` for audio) and return `B.reel()`.

## The existing system, wired in (added 6 Sep)

- `presets.json → engine`: the Ads Engine's locked rules, six-check pre-flight, naming, kill threshold, controls, category focus, hypotheses H1–H4, proven and failed hooks, the tag index, and the Social Playbook's palette, type, slots, pillars and festive dates. Sources are named in `engine._source`.
- `hooks.py`: Gap / Truth / Pull gates + a /12 hook score (the Growth System's layer-3 rubric, re-implemented from its published description). `python3 hooks.py "your line"`.
- `make_reel.py briefs --rank`: orders the briefs by tag index × hook score.
- Every render's `<name>-timeline.json` now carries `preflight`: the ad name, the colours shown (the ≥2-colour rule), the hook score, whether generated frames are used (AI disclosure), and the ten checks with the automatic ones filled in.
- Brief keys added: `tags`, `pillar`, `hypothesis`, `channel`, `stretch` (1.5 turns an 18 s cut into a 27 s ad cut), `copy.name_ad`.
- Style `social`: Fraunces 600 + Inter, espresso / warm bone / amber glow, per the Social Master Playbook.

## Quality gates (added 6 Sep, after the hands-frame miss)

- `qa.py --root <root> --out qa-sheet.jpg`: every generated still/clip beside the real reference frame with its status; `presets.json → assets.status / clip_status` is where approval lives, and `mechanisms.Build` refuses anything rejected (falls back to the real footage).
- `sources.py <video> [--write rubik]`: finds the colour states of any product video and registers them.
- `make_reel.py briefs --all --root <root>`: renders every brief and prints one summary line each (length, hook score, pre-flight counts, checks).
- `rubik-reels/ref/REFERENCE.md`: the product's true form, the real reference frames, the campaign video record and how to get the file into the system.
