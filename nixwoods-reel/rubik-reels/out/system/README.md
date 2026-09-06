# System demo renders

Twelve mechanisms plus a 27 s ad cut, each as `-music.mp4` (with the generated track) and `-clean.mp4` (no music, for trending audio in-app), with `-cover.jpg`, `-sheet.png` (2 fps contact sheet) and `-timeline.json` (every shot, cue, audio entry and the ads pre-flight result).

These are outputs, not sources. Everything here regenerates from the committed briefs, presets and assets:

```bash
python3 ../../../system/make_reel.py ../../../system/briefs --all --root <asset root> --audio both
```

The asset root needs `src/14-1.mp4` (Drive hero clip), `audio/*.mp3` (generated music, VO, SFX) and `hf/` (the stills and clips committed in `rubik-reels/hf/`). Files over ~21 MB are re-encoded at CRF 23 before being committed here; the originals render at CRF 18.
