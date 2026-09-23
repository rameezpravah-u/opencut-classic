#!/bin/bash
set -e
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
U=/root/.claude/uploads/f863beaa-1937-5cac-8a95-89d282b7c923
O=/home/user/opencut-classic/nixwoods-reel/floor-reels/src
TM="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
FIT="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30"

# HLG originals -> tonemapped SDR bt709, rotation auto-applied by ffmpeg
for pair in "3e7d0ba9-IMG_7923:nx01-7923" "6bbbcabb-IMG_7925:nx02-7925" "e8ca8a78-IMG_7926:nx03-7926" "60d94998-IMG_7930:nx04-7930"; do
  src="${pair%%:*}"; dst="${pair##*:}"
  echo "=== $dst  (HLG -> SDR)"
  $FF -nostdin -v error -y -i "$U/$src.mov" -vf "$TM,$FIT" \
      -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -profile:v high -an "$O/$dst.mp4"
done

# already SDR bt709 portrait - no tonemap, just conform
echo "=== nx00-hero  (already SDR)"
$FF -nostdin -v error -y -i "$U/6c9e97ea-42B74939-FC94-49F5-A910-4AD8D3AB0BA3.mov" \
    -vf "$FIT" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -profile:v high -an "$O/nx00-hero.mp4"
echo DONE
