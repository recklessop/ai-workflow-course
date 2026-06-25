#!/usr/bin/env bash
#
# verify.sh: Module 4 lab check.
#
# Exercises the `delete <index>` command the AI implemented across tasks.py and cli.py.
# It adds three tasks, deletes the middle one by index, and confirms the right task is gone
# and the other two remain. This is a behavior check on the multi-file change; it does not
# care HOW the AI implemented it, only that `delete` works end to end.
#
# Copy this into your tasks-app project directory, then run it from there:
#     cp ~/ai-workflow-course/modules/04-getting-the-ai-out-of-the-browser/lab/verify.sh .
#     bash verify.sh
#
# (It self-locates cli.py, so it also still works if you run it in place as `bash lab/verify.sh`.)
# It saves and restores your real tasks.json, so your actual task list is left untouched.

set -euo pipefail

# Find the project root: the directory containing cli.py. Works whether you run this from the
# project root or from the lab/ subfolder.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$here/cli.py" ]; then
  root="$here"
elif [ -f "$here/../cli.py" ]; then
  root="$(cd "$here/.." && pwd)"
else
  root="$(pwd)"
fi

if [ ! -f "$root/cli.py" ]; then
  echo "FAIL: couldn't find cli.py. Run this from your tasks-app project directory." >&2
  exit 1
fi

# Pick a Python interpreter.
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "FAIL: no python found on PATH." >&2
  exit 1
fi

cd "$root"

# Preserve any real task state, and always restore it on exit (even on failure).
state="tasks.json"
backup=""
if [ -f "$state" ]; then
  backup="$(mktemp)"
  cp "$state" "$backup"
fi
cleanup() {
  if [ -n "$backup" ]; then
    mv "$backup" "$state"
  else
    rm -f "$state"
  fi
}
trap cleanup EXIT

# Start from an empty list.
rm -f "$state"

echo "Running delete-command check with: $PY"

"$PY" cli.py add "alpha" >/dev/null
"$PY" cli.py add "beta"  >/dev/null
"$PY" cli.py add "gamma" >/dev/null

# Delete the middle task (index 1 = "beta").
if ! "$PY" cli.py delete 1 >/dev/null 2>&1; then
  echo "FAIL: 'python3 cli.py delete 1' errored. Is the delete command wired up in cli.py?" >&2
  exit 1
fi

out="$("$PY" cli.py list)"

ok=1
echo "$out" | grep -q "beta"  && { echo "FAIL: 'beta' should have been deleted but is still listed." >&2; ok=0; }
echo "$out" | grep -q "alpha" || { echo "FAIL: 'alpha' should still be present but is missing." >&2; ok=0; }
echo "$out" | grep -q "gamma" || { echo "FAIL: 'gamma' should still be present but is missing." >&2; ok=0; }

if [ "$ok" -ne 1 ]; then
  echo "--- current list ---" >&2
  echo "$out" >&2
  exit 1
fi

echo "PASS: delete removed the right task; alpha and gamma remain."
echo "The multi-file change works. Review it with 'git diff', then commit."
