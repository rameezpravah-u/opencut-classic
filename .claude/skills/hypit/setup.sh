#!/usr/bin/env bash
# NixWoods: install the pinned Hypit executable for this session (global npm does not persist in cloud sessions).
# Needs the owner's permission to run externally fetched code. Prints READY when `hypit` answers.
set -e
need=0.3.1
if command -v hypit >/dev/null 2>&1 && hypit version 2>/dev/null | grep -q "$need"; then echo READY; exit 0; fi
node -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit(a>22||(a===22&&b>=15)?0:1)' \
  || { echo "NEED_NODE: Hypit needs Node 22.15+"; exit 1; }
npm install --global "@hypit/hypit@$need"
hypit version
hypit paths || true
echo READY
