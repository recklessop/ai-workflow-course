#!/usr/bin/env bash
# Test suite for ai-workflow-course. Exits non-zero on any failure.
#
# Used two ways:
#   1. CI (.gitea/workflows/ci.yml, .github/workflows/ci.yml) on every PR + push.
#   2. The claude-deck autopilot review gate's `test` command (runs on the
#      merged-throwaway tree before an auto-merge).
#
# Dependency-light: python3 + grep + bash. The YAML check is skipped (not failed)
# if PyYAML is unavailable, so the suite still runs on a bare runner.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
fail=0
note() { printf '%s\n' "$*"; }

# 1) Lab Python compiles (skip the intentional paste-in fragment in Module 12).
while IFS= read -r f; do
  python3 -m py_compile "$f" 2>/dev/null || { note "FAIL py-compile: $f"; fail=1; }
done < <(find modules capstone -name '*.py' ! -name 'bad-clear-snippet.py')

# 2) Shell scripts parse.
while IFS= read -r f; do
  bash -n "$f" 2>/dev/null || { note "FAIL sh-parse: $f"; fail=1; }
done < <(find modules capstone tools -name '*.sh')

# 3) JSON parses.
while IFS= read -r f; do
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null || { note "FAIL json: $f"; fail=1; }
done < <(find modules capstone -name '*.json')

# 4) YAML parses (only if PyYAML is present; otherwise skipped, not failed).
if python3 -c "import yaml" 2>/dev/null; then
  while IFS= read -r f; do
    python3 -c "import yaml,sys; list(yaml.safe_load_all(open(sys.argv[1])))" "$f" 2>/dev/null || { note "FAIL yaml: $f"; fail=1; }
  done < <(find modules capstone .gitea .github -name '*.yml' -o -name '*.yaml' 2>/dev/null)
else
  note "skip yaml (PyYAML not installed)"
fi

# 5) No-slop guard: no em-dash in prose. The character is built from its codepoint
#    so this script holds no literal em-dash. Binaries and __pycache__ are skipped;
#    the only allowed em-dash is the regex character class in tools/build_wiki.py.
emd=$(printf '\u2014')
emdash=$(grep -rlI --exclude-dir=__pycache__ --exclude='*.pyc' "$emd" \
  README.md AGENTS.md _TEMPLATE.md handoff.md the-workflow-syllabus.md \
  modules capstone blog tools 2>/dev/null | grep -v 'tools/build_wiki.py' || true)
if [ -n "$emdash" ]; then
  note "FAIL em-dash present in:"; printf '  %s\n' $emdash; fail=1
fi

# 6) Structure: every module + capstone README has the core template sections.
for d in modules/*/ capstone/; do
  f="${d}README.md"
  [ -f "$f" ] || { note "FAIL missing README: $d"; fail=1; continue; }
  for h in "## Prerequisites" "## Hands-on lab" "## Where it breaks"; do
    grep -qF "$h" "$f" || { note "FAIL missing section '$h': $f"; fail=1; }
  done
done

if [ "$fail" = 0 ]; then note "check.sh: PASS"; else note "check.sh: FAIL"; fi
exit "$fail"
