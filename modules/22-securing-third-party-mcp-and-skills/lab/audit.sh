#!/usr/bin/env bash
#
# audit.sh: a runnable version of the Module 22 vetting checklist.
#
# Static red-flag scan over a third-party MCP server or skill BEFORE you install it. It does not
# execute anything in the target; it only reads. A clean run is NOT a guarantee (see "Where it
# breaks"); it is a cheap first pass that catches the obvious and the lazy.
#
# Usage:  bash audit.sh <path-to-skill-or-server-dir>
#
set -euo pipefail

TARGET="${1:-}"
if [[ -z "$TARGET" || ! -d "$TARGET" ]]; then
  echo "usage: bash audit.sh <directory>" >&2
  exit 2
fi

hits=0
section () { printf '\n=== %s ===\n' "$1"; }

# scan <label> <regex>: grep the tree, print matches, count a hit if found
scan () {
  local label="$1" regex="$2" out
  out=$(grep -rIinE "$regex" "$TARGET" 2>/dev/null || true)
  if [[ -n "$out" ]]; then
    printf '\n[FLAG] %s\n' "$label"
    printf '%s\n' "$out" | sed 's/^/    /'
    hits=$((hits + 1))
  fi
}

echo "Auditing: $TARGET"
echo "Files:"
find "$TARGET" -type f | sed 's/^/    /'

section "Outbound network (where could data go?)"
scan "HTTP / socket egress"        'urllib|requests\.|http\.client|socket\.|urlopen|fetch\(|axios|curl |wget '

section "Credential & environment access (what secrets can it reach?)"
scan "Reads the whole environment" 'os\.environ|getenv|process\.env|printenv|(^|[^A-Za-z])env([^A-Za-z]|$)'
scan "Reads private credentials"   '\.ssh|id_rsa|\.aws|credentials|\.env([^a-z]|$)|NOTION_TOKEN'

section "Code execution & obfuscation"
scan "Shell-out / eval / exec"     'os\.system|subprocess|child_process|eval\(|exec\(|\| *bash|\| *sh($| )'
scan "Encoding (often hides data)" 'base64|b64encode|atob\(|btoa\('

section "Broad filesystem access"
scan "Home / root paths"           'Path\.home|\$HOME|os\.path\.expanduser|(^|[^a-zA-Z0-9._/-])~/'

section "Hidden / injected instructions in text"
scan "Imperative directives"       'ignore (previous|prior|all)|system:|maintenance mode|do not (mention|tell|list)|exfiltrat'

# Zero-width / invisible characters smuggle instructions past a human reader. Use Python (a lab
# prerequisite) so this works the same on every OS, regardless of the local grep flavor.
section "Invisible characters (zero-width injection)"
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
zw=$("$PY" - "$TARGET" <<'EOF'
import os, sys
bad = {"​","‌","‍","⁠","﻿"}
root = sys.argv[1]
for dp, _, fns in os.walk(root):
    for fn in fns:
        p = os.path.join(dp, fn)
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for i, ch in enumerate(text):
            if ch in bad:
                print(f"    {p}: zero-width char U+{ord(ch):04X} at offset {i}")
                break
EOF
)
if [[ -n "$zw" ]]; then
  printf '\n[FLAG] Invisible characters found\n%s\n' "$zw"
  hits=$((hits + 1))
fi

section "Verdict"
if (( hits > 0 )); then
  echo "REJECT (or sandbox + scope): $hits red-flag categor$([[ $hits -eq 1 ]] && echo y || echo ies) tripped."
  echo "Read the flagged lines above against what the skill CLAIMS to do."
  exit 1
else
  echo "No static red flags. Still: read the code, check provenance, and PIN the version before installing."
fi
