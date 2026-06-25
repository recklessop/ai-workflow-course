#!/usr/bin/env bash
#
# security-scan.sh: the security gate for tasks-app (Module 15).
#
# Runs two scanners and exits non-zero if EITHER finds something. That non-zero exit is what turns
# a CI run red (Module 14). One script, two homes: run it by hand for fast local feedback, and call
# it from the pipeline so the same definition of "a finding" enforces the merge.
#
# These two tools (pip-audit, detect-secrets) are concrete examples of their categories, SCA and
# secret scanning. Swap in any equivalent; keep the contract the same: scan, print, fail on findings.
#
# Usage:   ./security-scan.sh
# Install: pip install pip-audit detect-secrets

set -u  # treat unset vars as errors; we manage exit codes explicitly below.

# A security gate must fail CLOSED. If the interpreter the secret gate needs isn't here, abort with a
# non-zero exit rather than sailing past the check and reporting a false "passed".
command -v python3 >/dev/null 2>&1 || {
  echo ">> python3 is required for the secret gate but was not found. Aborting." >&2
  exit 2
}

status=0

echo "=== Gate 1: SCA / dependency scan (pip-audit) ==="
if [ -f requirements.txt ]; then
  if ! pip-audit -r requirements.txt; then
    echo ">> SCA gate FAILED: unresolvable or vulnerable dependency. See above." >&2
    status=1
  fi
else
  echo "(no requirements.txt found; skipping SCA)"
fi

echo
echo "=== Gate 2: secret scan (detect-secrets) ==="
# detect-secrets prints a JSON report of any secrets it finds. NOTE: with no path it scans the files
# git TRACKS, so stage the starter files (`git add`) before running this, or an untracked file is
# invisible to the gate. We parse the JSON with `python3` (no jq dependency) and fail CLOSED: the
# parser returns 0=secrets found, 1=clean, anything else=couldn't tell; "couldn't tell" must
# count as a failure, never a silent pass.
report="$(detect-secrets scan)"
printf '%s' "$report" | python3 -c 'import sys, json
try:
    found = bool(json.load(sys.stdin).get("results"))
except Exception:
    sys.exit(2)
sys.exit(0 if found else 1)'
secret_rc=$?
case "$secret_rc" in
  0)
    echo "$report"
    echo ">> SECRET gate FAILED: a credential was detected in the tree. See report above." >&2
    status=1
    ;;
  1)
    echo "no secrets detected."
    ;;
  *)
    echo ">> SECRET gate ERROR: could not parse the scan output (exit $secret_rc). Failing closed." >&2
    status=1
    ;;
esac

echo
if [ "$status" -ne 0 ]; then
  echo "SECURITY GATE: FAILED" >&2
else
  echo "SECURITY GATE: passed"
fi
exit "$status"
