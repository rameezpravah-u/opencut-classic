#!/usr/bin/env bash
# New NixWoods HyperFrames project: 1080x1920, brand fonts, local GSAP (the render browser does not
# trust the session proxy, so nothing may load from a CDN).
#   hyperframes/new.sh <name>        -> hyperframes/projects/<name>/
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd); root=$(dirname "$here")
name=${1:?usage: new.sh <name>}; dst="$here/projects/$name"
[ -e "$dst" ] && { echo "exists: $dst" >&2; exit 1; }
mkdir -p "$dst/fonts"
cp "$here/starter/index.html" "$here/starter/gsap-3.14.2.min.js" "$here/starter/hyperframes.json" "$dst/"
cp "$root/assets/"{Fraunces-600,Fraunces-500-i,Inter-400,Inter-600,GochiHand-400}.ttf "$dst/fonts/"
cp "$root/assets/logo.png" "$dst/"
printf '{\n  "id": "%s",\n  "name": "%s"\n}\n' "$name" "$name" > "$dst/meta.json"
echo "$dst  —  read MOTION.md, edit index.html, then: (cd $dst && ../../hf.sh check)"
