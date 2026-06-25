#!/usr/bin/env bash
# Module 26 lab: fan work out across a fleet of worktrees.
#
# Creates one worktree per issue, each on its own issue-named branch. main is left untouched
# and reserved as the integration point. Run from inside your tasks-app repo.
#
# This is Module 7's `git worktree add` repeated with a naming convention. The convention is the
# point: branch name carries the issue number, folder name mirrors the branch.

set -euo pipefail

# Each entry: "<worktree-folder> <branch>". Edit to match your coordination plan.
FLEET=(
  "../tasks-app-42-count feature/42-count"
  "../tasks-app-43-docs  feature/43-docs"
  "../tasks-app-44-clear feature/44-clear"
)

if [ ! -d .git ] && ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "error: run this from inside your tasks-app git repo." >&2
  exit 1
fi

for entry in "${FLEET[@]}"; do
  # shellcheck disable=SC2086
  set -- $entry
  path="$1"; branch="$2"
  if git worktree list --porcelain | grep -q "branch refs/heads/$branch"; then
    echo "skip: $branch already checked out in a worktree"
    continue
  fi
  echo "fan-out: $path  (branch $branch)"
  git worktree add "$path" -b "$branch"
done

echo
echo "Fleet is up. main is reserved for integration; no agent works there."
git worktree list
