#!/usr/bin/env bash
# Module 26 lab: tear down the fleet after the work has merged.
#
# Removes each worktree and prunes stale records. Refuses to remove a worktree with uncommitted
# work (Git's safety); commit or merge first. Run from inside your tasks-app repo.

set -euo pipefail

FLEET=(
  "../tasks-app-42-count"
  "../tasks-app-43-docs"
  "../tasks-app-44-clear"
)

git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo" >&2; exit 1; }

for path in "${FLEET[@]}"; do
  if [ -d "$path" ]; then
    echo "remove: $path"
    git worktree remove "$path"   # fails if dirty; that's intentional, commit first
  fi
done

git worktree prune
echo
echo "Fleet torn down. Remaining worktrees:"
git worktree list
