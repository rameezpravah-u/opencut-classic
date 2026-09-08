# Audio

Generated with ElevenLabs, ~900 credits per music track (about 4,500 for the first five, 1,800 more for the two takes of music6). They are committed because regenerating them costs real money and would not reproduce the same tracks — the beat grids (`styles.*.cut` in `system/presets.json`, or `cut` in a brief) are measured from these exact files — `python3 system/beatgrid.py <track>` does the measuring.

| File | Used by | Notes |
|---|---|---|
| `music1-aesthetic.mp3` | style `aesthetic` | dreamy lo-fi, 68 bpm, hit every 1.766 s |
| `music2-meaning.mp3` | styles `broad`, `social` | felt piano, ducked to −13 dB under the voice-over |
| `music3-design.mp3` | style `design` | minimal electronic 100 bpm; briefs start it 8 s in (`music_offset: -8`) |
| `music4-genz.mp3` | styles `genz`, `ugc` | phonk 140 bpm, 4-beat grid 1.714 s; briefs start it 26.6 s in |
| `music5-3040.mp3` | styles `3040`, `festive` | indie folk 95 bpm, grid 2.526 s |
| `music6-corners.mp3` | brief `B1-brand-corners` (brand `corners` cuts) | felted piano, warm pad, vinyl crackle and a distant tanpura drone; **71.8 bpm measured, grid 1.672 s**. Instrumental — confirmed, not assumed: eleven_scribe_v1 returns an empty transcript. Two takes were generated; this is the second. The first fades 38 dB across 25 s (down to −44 dB by the end) and is useless as a bed, so it was not kept. |
| `sfx-turn.mp3` | all | the colour turn; place it on the beat where the block moves |
| `sfx-whoosh.mp3` | all | transition accent, always 0.2 s *before* the cut |
| `vo-meaning.mp3` | brief `VO-story` | Sarah (ElevenLabs premade `EXAVITQu4vr4xnSDxMaL`), script in `system/scripts/vo-scripts.md` |

Licence note: these are generated tracks, cleared for paid placement. The older `NIXWOODS-brand-film-music-4x5.mp4` track used by the first NixWoods reel is not — confirm its licence before running that one as an ad.
