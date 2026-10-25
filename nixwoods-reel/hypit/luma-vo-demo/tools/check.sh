#!/usr/bin/env bash
# usage: tools/check.sh <build-id> <name>   (run from the project root)
set -euo pipefail
B="${1:?build id}"; N="${2:?name}"
rm -f "out/${N}.mp4"
hypit get "$B" --output final.video --to "out/${N}.mp4" | tail -1
if ffmpeg -v error -i "out/${N}.mp4" -f null - 2> "out/${N}-decode.log" && [ ! -s "out/${N}-decode.log" ]; then echo "DECODE_OK"; else echo "DECODE_ERRORS:"; cat "out/${N}-decode.log"; fi
echo "duration $(ffprobe -v error -show_entries format=duration -of csv=p=0 "out/${N}.mp4") s"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt -of compact "out/${N}.mp4"
python3 tools/sheet.py "out/${N}.mp4" "out/${N}-sheet.jpg" 2 8
