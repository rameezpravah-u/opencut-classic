#!/bin/bash
# Cloud-session setup for OpenMontage (github.com/calesthio/OpenMontage), the agentic video toolkit.
#
# Runs in Claude Code cloud sessions only. On a local machine (the Mac) it exits at once and installs
# nothing: no clone, no venv, no npm packages, no certificate changes.
#
# What it does, each step skipped when already done (safe to re-run):
#   1. clones OpenMontage at a pinned, tested commit, beside this repo (never inside it)
#   2. runs its `make setup`: Python venv + requirements, Remotion npm packages, Piper TTS, HyperFrames cache
#   3. downloads Piper's default English voice (en_US-lessac-medium)
#   4. adds the sandbox's TLS-intercepting CAs to Chrome's NSS store. Remotion launches Chrome with the
#      proxy switched off, so its traffic meets the egress gateway's certificate, which Chrome does not
#      trust until it is in ~/.pki/nssdb. Without this, every Remotion render fails on Google Fonts.
#   5. exports OPENMONTAGE_DIR and appends the venv to PATH (appended, so the system python3 the
#      nixwoods-reel scripts use still comes first)
#
# Verbose output goes to $OPENMONTAGE_DIR/.session-setup.log; only a one-line summary reaches the session.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

OM_COMMIT="9327439db69021ab4b0e2776729bf3b58fdb5a87"   # tested 10 Oct 2026; bump deliberately
OM_REPO="https://github.com/calesthio/OpenMontage.git"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
OM_DIR="${OPENMONTAGE_DIR:-$(dirname "$PROJECT_DIR")/OpenMontage}"
VOICE="en_US-lessac-medium"
CA_BUNDLE="/root/.ccr/ca-bundle.crt"
NSSDB="$HOME/.pki/nssdb"

mkdir -p "$OM_DIR"
LOG="$OM_DIR/.session-setup.log"
: > "$LOG"
exec 3>&1 1>>"$LOG" 2>&1

# 1. clone at the pinned commit
if [ ! -d "$OM_DIR/.git" ]; then
  git -C "$OM_DIR" init -q
  git -C "$OM_DIR" remote add origin "$OM_REPO"
fi
if [ "$(git -C "$OM_DIR" rev-parse HEAD 2>/dev/null || true)" != "$OM_COMMIT" ]; then
  git -C "$OM_DIR" fetch -q --depth 1 origin "$OM_COMMIT"
  git -C "$OM_DIR" checkout -q --force FETCH_HEAD
fi

# 2. make setup (venv, pip, Remotion, Piper, HyperFrames)
if [ ! -x "$OM_DIR/.venv/bin/piper" ] || [ ! -d "$OM_DIR/remotion-composer/node_modules/remotion" ]; then
  make -C "$OM_DIR" setup
fi

# 3. Piper voice
if [ ! -f "$OM_DIR/$VOICE.onnx" ]; then
  (cd "$OM_DIR" && .venv/bin/python -m piper.download_voices "$VOICE")
fi

# 4. trust the sandbox CAs in Chrome's NSS store
if [ -f "$CA_BUNDLE" ]; then
  if ! command -v certutil >/dev/null; then
    apt-get install -y -q libnss3-tools || { apt-get update -q && apt-get install -y -q libnss3-tools; }
  fi
  mkdir -p "$NSSDB"
  [ -f "$NSSDB/cert9.db" ] || certutil -N -d "sql:$NSSDB" --empty-password
  tmp=$(mktemp -d)
  awk -v d="$tmp" '/BEGIN CERT/{n++} n{print > (d "/" n ".pem")}' "$CA_BUNDLE"
  for pem in "$tmp"/*.pem; do
    subj=$(openssl x509 -in "$pem" -noout -subject -nameopt sep_multiline 2>/dev/null) || continue
    case "$subj" in *"O=Anthropic"*) ;; *) continue ;; esac
    cn=$(printf '%s\n' "$subj" | sed -n 's/^ *CN=//p' | head -1)
    fp=$(openssl x509 -in "$pem" -noout -fingerprint -sha256 | tr -d ':' | sed 's/.*=//' | cut -c1-12)
    nick="$cn $fp"                         # several rotations share a CN; the fingerprint keeps them apart
    certutil -L -d "sql:$NSSDB" -n "$nick" >/dev/null 2>&1 || certutil -A -d "sql:$NSSDB" -n "$nick" -t "C,," -i "$pem"
  done
  rm -rf "$tmp"
fi

# 5. session environment
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export OPENMONTAGE_DIR=\"$OM_DIR\""
    echo "export PATH=\"\$PATH:$OM_DIR/.venv/bin\""
  } >> "$CLAUDE_ENV_FILE"
fi

echo "OpenMontage ready at $OM_DIR (commit ${OM_COMMIT:0:7}, Piper voice $VOICE, Chrome trusts sandbox CAs). Log: $LOG" >&3
