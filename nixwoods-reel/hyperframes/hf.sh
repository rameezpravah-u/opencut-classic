#!/usr/bin/env bash
# Run the HyperFrames CLI in a cloud session: pinned version, the pre-installed Chromium headless
# shell (the CLI's own download is blocked here), ffmpeg/ffprobe from apt.
#   hyperframes/hf.sh check | render --quality draft --output out.mp4 | snapshot --at 0.5,5,9.5
set -euo pipefail
HF_VERSION=0.8.141
if ! command -v ffprobe >/dev/null; then
  echo "[hf] installing ffmpeg (apt)…" >&2
  apt-get update -qq && apt-get install -y -qq --no-install-recommends ffmpeg >/dev/null
fi
shell=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell 2>/dev/null | tail -1 || true)
[ -n "$shell" ] && export HYPERFRAMES_BROWSER_PATH="${HYPERFRAMES_BROWSER_PATH:-$shell}"
export HYPERFRAMES_SKIP_SKILLS=1      # skills live in .claude/skills, installed from a pinned commit
export DO_NOT_TRACK=1
exec npx -y "hyperframes@${HF_VERSION}" "$@"
