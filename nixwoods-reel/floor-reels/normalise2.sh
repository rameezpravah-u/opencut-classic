#!/bin/bash
# Second batch, 5 Oct. Same recipe as normalise.sh: HLG -> SDR bt709, rotation auto-applied, 1080x1920/30.
set -e
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
U=/root/.claude/uploads/f863beaa-1937-5cac-8a95-89d282b7c923
O=$(dirname "$0")/src
TM="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
FIT="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30"
for pair in "90b758db-IMG_7920:nx05-7920" "f32b68b8-IMG_7921:nx06-7921" "a70801fa-IMG_7922:nx07-7922" "0b11f6f7-IMG_7924:nx08-7924"; do
  src="${pair%%:*}"; dst="${pair##*:}"
  echo "=== $dst"
  $FF -nostdin -v error -y -i "$U/$src.mov" -vf "$TM,$FIT" -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -an "$O/$dst.mp4"
done
echo DONE
