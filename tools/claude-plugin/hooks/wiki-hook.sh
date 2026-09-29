#!/usr/bin/env bash
# Locate the wiki (override with SOFTHIER_WIKI) and run its hook entry point. Silent no-op if absent; never fails.
W="${SOFTHIER_WIKI:-${CLAUDE_PROJECT_DIR:-$PWD}/softhier_vla_wiki}"
[ -f "$W/tools/wiki.py" ] || exit 0
python3 "$W/tools/wiki.py" hook "$1" 2>/dev/null || true
exit 0
