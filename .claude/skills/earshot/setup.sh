#!/usr/bin/env bash
# NixWoods: install Earshot pinned at v0.4.0 for this session (~/.cache does not persist in cloud sessions).
# Needs the owner's permission to run externally fetched code. Prints READY when `earshot sfx list` works.
set -e
REV=591fa3e028032e6dce56620a20e932e35667e8d8
DIR="${EARSHOT_DIR:-$HOME/.cache/earshot}"
if [ -x "$DIR/.venv/bin/earshot" ] && "$DIR/.venv/bin/earshot" sfx list >/dev/null 2>&1; then echo READY; exit 0; fi
[ -d "$DIR/.git" ] || git clone -q https://github.com/Leonxlnx/earshot "$DIR"
git -C "$DIR" fetch -q origin "$REV" 2>/dev/null || true
git -C "$DIR" checkout -q "$REV"
python3 -m venv "$DIR/.venv"
export PIP_CERT="${PIP_CERT:-/root/.ccr/ca-bundle.crt}"
"$DIR/.venv/bin/python" -m pip install -q --upgrade pip
"$DIR/.venv/bin/python" -m pip install -q torch --index-url https://download.pytorch.org/whl/cpu
"$DIR/.venv/bin/python" -m pip install -q -e "$DIR[mcp]"
"$DIR/.venv/bin/earshot" doctor || true
"$DIR/.venv/bin/earshot" sfx list >/dev/null && echo READY
