#!/usr/bin/env bash
# Module 26 lab: fleet dashboard.
#
# Prints every worktree, its branch, and how much work is in flight (uncommitted changes +
# commits ahead of main). Your "where is every agent?" view in one command. Run from anywhere
# inside the repo.

set -euo pipefail

git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo" >&2; exit 1; }

printf "%-32s %-22s %-10s %s\n" "WORKTREE" "BRANCH" "AHEAD" "DIRTY?"
printf "%-32s %-22s %-10s %s\n" "--------" "------" "-----" "------"

git worktree list --porcelain | awk '/^worktree /{wt=$2} /^branch /{print wt"\t"$2}' \
| while IFS=$'\t' read -r wt ref; do
    branch="${ref#refs/heads/}"
    name="$(basename "$wt")"
    # commits on this branch not yet in main
    ahead="$(git -C "$wt" rev-list --count main.."$branch" 2>/dev/null || echo "?")"
    # any uncommitted changes in this worktree?
    if [ -n "$(git -C "$wt" status --porcelain 2>/dev/null)" ]; then dirty="yes"; else dirty="no"; fi
    printf "%-32s %-22s %-10s %s\n" "$name" "$branch" "$ahead" "$dirty"
done
