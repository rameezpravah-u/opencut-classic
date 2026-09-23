# Test fixtures

## hlg-10bit-sample.mp4
HEVC Main 10, `bt2020nc/bt2020/arib-std-b67`, 1080x1920, 5.9s.
Re-encoded from `shelf-reels/src/IMG_7745.mp4` to carry a genuine HLG transfer,
because every clip under `*-reels/src/` is a already-normalised bt709 copy —
the HLG originals came off the phone as .mov uploads and were never kept.

Use it to test the HLG->SDR rule. The check is on the output's colour tags,
not on pixels: encode it through your pipeline and read the tags back with

    ffmpeg -i out.mp4 2>&1 | grep -oP 'yuv420p\([^)]*\)'

- `yuv420p(tv, bt2020nc/bt2020/arib-std-b67, ...)` -> NOT tonemapped. Renders
  washed-out grey in any bt709 player.
- `yuv420p(tv, bt709, ...)` -> tonemapped correctly.
