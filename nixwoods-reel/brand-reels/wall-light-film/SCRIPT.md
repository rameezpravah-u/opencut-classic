# Wall Light Film — ad cuts (Meta + Instagram)

Two brand-driven edits cut down from the six-scene cinematic film, built for paid placement.
Same hook, same six scenes, same score, reframed per platform. Not a hard-sell: no price, no
claim beyond what the footage shows, per `brand.md` ("the light does the selling, the type stays
quiet").

## Hook

Scored against `system/hooks.py` (Gap/Truth/Pull gates + the /12 rubric):

| Line | Score | Gates | Families |
|---|---|---|---|
| Watch what one wall light does to a room. | 10/12 | ✓✓✓ | curiosity, listicle |
| **One wall light. Six rooms. Watch what changes.** | **11/12** | ✓✓✓ | curiosity, listicle, transformation |

Using the second line — it names the film's own structure (one product, six spaces), which is the
actual promise the cut delivers on, not an invented claim. On screen over scene 1, in by 0.2s, held
to 1.8s, inside the safe zone (left-aligned, Cormorant Garamond italic, lower case, per the
`aesthetic` style).

No other on-screen copy. End card only: "solid wood lighting" / "nixwoods.com" (the approved
`linear` product's cta line), same as the brand film.

## Cut list (identical structure, different frame)

6 scenes × a 3.0s window (not the full 6s camera move — the first ~0.8–1s of each clip is cut
before the motion reads clearly on a phone screen, so each window starts at the 0.8s mark), 0.4s
dissolve between every cut, 2.5s end card. Total ≈ 18.1s — inside Meta's and Instagram's recommended
15–20s band for a brand-awareness cut.

| # | Space / product | Window (source clip) | Move |
|---|---|---|---|
| 1 | Home — Aurora | 0.8–3.8s | push-in |
| 2 | Office — NixLine | 0.8–3.8s | rack-focus |
| 3 | Hotel corridor — Wall Sconce | 0.8–3.8s | dolly |
| 4 | Art gallery — Vertical Curved | 0.8–3.8s | drift + rack-focus |
| 5 | Restaurant — Timber | 0.8–3.8s | push-in |
| 6 | Hotel suite — Arden | 0.8–3.8s | tilt-up |
| — | End card | 2.5s held | static, logo fades in |

## Motion / cinematic moves

Unchanged from the house camera vocabulary (`system/PLAYBOOK.md` §5) used in the long cut: one
sanctioned move per scene, no handheld, no whip, no jump cuts — dissolves only, so the six rooms
read as one continuous walk rather than six separate ads stapled together.

## Audio

- **Bed**: `rubik-reels/audio/music3-design.mp3` — one of the two tracks `brand.md` names as
  cleared for paid use. Trimmed to the cut's length, in over 0.6s, out over the last 1s.
- **Cut SFX**: `rubik-reels/audio/sfx-whoosh.mp3`, a short burst ducked under the music at each of
  the five scene-to-scene dissolves — the only thing that marks a cut, since there's no text to do
  it.
- **End card SFX**: `brand-reels/edison-stages/sfx/sfx-dimmer-click.mp3` on the card's fade-in — a
  real product sound (a dimmer click), not a generic whoosh, so the close lands on the brand's own
  material rather than a stock sting.

## The two deliverables

| | Meta | Instagram |
|---|---|---|
| Frame | 1080×1350 (4:5, Feed) | 1080×1920 (9:16, Reels) |
| Reframe | Each shot fit-within-frame over a blurred, dimmed copy of itself (the house rule for a horizontal fixture: a centre crop cuts its ends off, so nothing is cropped — the full wall light stays in frame on both cuts) | same technique, taller canvas |
| File | `out/NixWoods-Wall-Light-Film-Meta-4x5.mp4` | `out/NixWoods-Wall-Light-Film-Instagram-9x16.mp4` |

Both still need, before they run as paid: a human watch end to end, and Meta's / Instagram's
AI-generated-content disclosure ticked by hand (per `brand.md` — this session has no ad-account
access to tick it).

Built by `build_ads.py` (same folder). Media isn't committed — see the main `README.md`'s note on
the repo's size ceiling.

## Voiceover version

`build_vo.py` adds narration to the base (non-ad) six-scene film — `out/NixWoods-Wall-Light-Film-VO.mp4`.
Uses OpenMontage (`/home/user/OpenMontage`, already set up this session with Piper TTS) for both
the voice and the mix:

- **Voice**: Piper, `en_US-lessac-medium` (offline, no API key), `length_scale=1.08` and
  `sentence_silence=0.35` for an unhurried, deliberate read rather than Piper's brisker default —
  the closest this free local voice gets to a "classy" delivery. Honest caveat: Piper is clear and
  warm, not an expressive/sultry voice-actor read — ElevenLabs (already wired into this session via
  MCP) would get closer to a true "sexy" read if that matters more than staying free and offline.
- **Script** (7 lines, timed to the film's own scene cuts — see delays in `build_vo.py`): short,
  confident, no banned words, no claim beyond what the footage shows.
  1. "Most rooms stop at the wall."
  2. "We did not think that was good enough."
  3. "So we built one that lives in the wood itself."
  4. "No glare. No clutter. No excuse."
  5. "Just the one thing every room was missing."
  6. "Somewhere for the eye to rest."
  7. "NixWoods. Solid wood lighting." (end card)
- **Mix**: OpenMontage's `tools/audio/audio_mixer.py` `AudioMixer` (`operation: "duck"`) —
  ffmpeg `sidechaincompress` using the narration as the key signal, music ducked 14dB under it,
  120ms attack / 600ms release. The end-card dimmer-click SFX layers on top, same touch as the ad
  cuts. Final mux upsamples to 48kHz stereo (Piper renders 22050Hz mono).
- The base film's end card was extended from 3.0s to 3.6s (`build.py`'s `END_DUR`) so the closing
  line has room to land before the film ends — rebuild the base film before re-running this if that
  constant moves again.

```
python3 build_vo.py     # from this folder; needs vo/line*.wav (regenerate via Piper, see below) +
                         # out/NixWoods-Wall-Light-Film.mp4 already built
```

To regenerate the narration lines from scratch:
```
/home/user/OpenMontage/.venv/bin/piper -m /home/user/OpenMontage/en_US-lessac-medium.onnx \
  --length-scale 1.08 --sentence-silence 0.35 -f vo/lineN.wav <<< "line text"
```
