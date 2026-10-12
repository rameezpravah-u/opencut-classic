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

# 6. MoneyPrinterTurbo (github.com/harry0703/MoneyPrinterTurbo, MIT): Edge TTS voices (Hindi, Indian English),
#    caption timing and assembly for the voice-over reels in nixwoods-reel/brand-reels/mpt-voice/.
#    Pinned commit, its own Python 3.11 venv, beside this repo. Edge TTS verifies TLS against certifi only,
#    so the sandbox CAs are appended to the venv's certifi bundle (verification stays on).
MPT_COMMIT="4204d0f39afa8ada6f3edc31604141f959fe254e"                  # tested 11 Oct 2026
MPT_DIR="${MPT_DIR:-$(dirname "$PROJECT_DIR")/MoneyPrinterTurbo}"
{
  mkdir -p "$MPT_DIR"
  if [ ! -d "$MPT_DIR/.git" ]; then
    git -C "$MPT_DIR" init -q && git -C "$MPT_DIR" remote add origin https://github.com/harry0703/MoneyPrinterTurbo.git
  fi
  if [ "$(git -C "$MPT_DIR" rev-parse HEAD 2>/dev/null || true)" != "$MPT_COMMIT" ]; then
    git -C "$MPT_DIR" fetch -q --depth 1 origin "$MPT_COMMIT" && git -C "$MPT_DIR" checkout -q --force FETCH_HEAD
  fi
  if [ ! -x "$MPT_DIR/.venv/bin/python" ] || ! "$MPT_DIR/.venv/bin/python" -c "import moviepy, edge_tts" 2>/dev/null; then
    python3.11 -m venv "$MPT_DIR/.venv"
    "$MPT_DIR/.venv/bin/pip" install -q -r "$MPT_DIR/requirements.txt"
  fi
  [ -f "$MPT_DIR/config.toml" ] || cp "$MPT_DIR/config.example.toml" "$MPT_DIR/config.toml"
  certs=$("$MPT_DIR/.venv/bin/python" -c "import certifi; print(certifi.where())")
  if [ -f "$CA_BUNDLE" ] && ! grep -q "sandbox egress CAs" "$certs"; then
    printf '\n# sandbox egress CAs (cloud session only)\n' >> "$certs"
    python3 - "$CA_BUNDLE" "$certs" <<'PY'
import re, subprocess, sys
pems = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", open(sys.argv[1]).read(), re.S)
have = open(sys.argv[2]).read()
with open(sys.argv[2], "a") as f:
    for p in pems:
        s = subprocess.run(["openssl", "x509", "-noout", "-subject"], input=p, capture_output=True, text=True).stdout
        if "Anthropic" in s and p not in have:
            f.write(f"# {s.strip()}\n{p}\n")
PY
  fi
  cp "$PROJECT_DIR/nixwoods-reel/assets/Inter-600.ttf" "$PROJECT_DIR/nixwoods-reel/assets/Hind-SemiBold.ttf" "$MPT_DIR/resource/fonts/"
  mkdir -p "$MPT_DIR/storage/bgm"
  cp "$PROJECT_DIR/nixwoods-reel/floor-reels/audio/music6-corners.mp3" "$MPT_DIR/storage/bgm/"
} || echo "MoneyPrinterTurbo setup failed; see $LOG" >&3
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export MPT_DIR=\"$MPT_DIR\"" >> "$CLAUDE_ENV_FILE"
fi
echo "MoneyPrinterTurbo ready at $MPT_DIR (commit ${MPT_COMMIT:0:7}, Edge TTS trusts sandbox CAs)." >&3

# 7. NixWoods OS: what the social tab is waiting on, and what it has asked this tab for (D-086).
#    Best effort: fast-forwards ../nixwoods-os when it is there and clean, never clones, never fails the session.
NW_OS="${NIXWOODS_OS:-$(dirname "$PROJECT_DIR")/nixwoods-os}"
if [ -f "$NW_OS/40-Content/scripts/creative_index.py" ]; then
  { git -C "$NW_OS" fetch -q origin main && git -C "$NW_OS" merge -q --ff-only origin/main; } || true
  python3 "$NW_OS/40-Content/scripts/creative_index.py" --check --renders "$PROJECT_DIR" >&3 2>&1 || true
  echo "D-086: deliver every REQUEST above and mark its heading in 00-OS/HANDOFF-FOR-CLAUDE-CODE.md '— DONE <date>: <IDs>'; every render you commit must be registered before you stop (the Stop hook checks)." >&3
else
  echo "nixwoods-os is not cloned at $NW_OS: attach rameezpravah-u/nixwoods-os (add_repo) and clone it there before filing any asset (D-081, D-086)." >&3
fi
