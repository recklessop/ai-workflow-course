#!/usr/bin/env bash
#
# make-conflict.sh: manufacture a guaranteed merge conflict to practice on.
#
# AI edits are nondeterministic, so the lab's organic conflict (two branches editing the same usage
# line in cli.py) doesn't ALWAYS land. This script guarantees one: it creates two branches that each
# append a different line to the same spot in README.md, then leaves you mid-merge with a real
# conflict in your working tree. The resolution mechanic is identical to the code case in the lab:
# read the <<<<<<< / ======= / >>>>>>> markers, edit to the version you want, remove the markers,
# then `git add` + `git commit`.
#
# Copy it into your tasks-app repo, then run it from inside the repo:
#     cp ~/ai-workflow-course/the-workflow-course/modules/06-branches-sandboxes-for-experiments/lab/make-conflict.sh .
#     bash make-conflict.sh
#
# It is non-destructive to your real work: it only touches README.md on two throwaway practice
# branches and refuses to run if your working tree is dirty.

set -euo pipefail

BRANCH_A="practice/conflict-a"
BRANCH_B="practice/conflict-b"
FILE="README.md"

# 1. Must be inside a Git repo.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: not inside a Git repository. cd into your tasks-app first." >&2
  exit 1
fi

# 2. Working tree must be clean, or switching branches would clobber uncommitted work.
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "error: you have uncommitted changes. commit or stash them first (git status)." >&2
  exit 1
fi

# 3. README.md must exist (it ships with the Module 1 tasks-app).
if [ ! -f "$FILE" ]; then
  echo "error: $FILE not found. run this from your tasks-app repo root." >&2
  exit 1
fi

# 4. Remember where we started, and clean up any leftover practice branches from a prior run.
START_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
git branch -D "$BRANCH_A" >/dev/null 2>&1 || true
git branch -D "$BRANCH_B" >/dev/null 2>&1 || true

# 5. Branch A: append one version of a line, commit.
git switch -c "$BRANCH_A" >/dev/null
printf '\n<!-- practice line added on branch A -->\n' >> "$FILE"
git add "$FILE"
git commit -q -m "practice: append line (branch A)"

# 6. Branch B (off the original branch): append a DIFFERENT version to the same spot, commit.
git switch "$START_BRANCH" >/dev/null
git switch -c "$BRANCH_B" >/dev/null
printf '\n<!-- practice line added on branch B -->\n' >> "$FILE"
git add "$FILE"
git commit -q -m "practice: append line (branch B)"

# 7. Merge A into B to trigger the conflict. Disable the editor so it doesn't block.
echo
echo "Merging $BRANCH_A into $BRANCH_B to create a conflict..."
set +e
GIT_EDITOR=true git merge "$BRANCH_A" >/dev/null 2>&1
set -e

echo
echo "================================================================"
echo " A merge conflict now exists in: $FILE"
echo " You are on branch: $BRANCH_B"
echo "================================================================"
echo
echo " Next steps (the skill you're practicing):"
echo "   1. git status                # see $FILE under 'Unmerged paths'"
echo "   2. open $FILE and read the <<<<<<< / ======= / >>>>>>> markers yourself FIRST"
echo "      (this is your chance to see a real conflict before an agent resolves it away)"
echo "   3. ask your agent to resolve the conflict in $FILE and complete the merge"
echo "      (\"resolve the conflict markers in $FILE and finish the merge\")"
echo "   4. verify: open $FILE, confirm no <<<<<<< / ======= / >>>>>>> markers remain"
echo "   5. git log --oneline --graph # confirm the merge commit landed"
echo "   (to do it by hand instead: edit out the markers, then git add $FILE && git commit)"
echo
echo " Chicken out? Undo the whole thing with:  git merge --abort"
echo
echo " When you're done practicing, clean up the throwaway branches:"
echo "   git switch $START_BRANCH"
echo "   git branch -D $BRANCH_A $BRANCH_B"
echo
