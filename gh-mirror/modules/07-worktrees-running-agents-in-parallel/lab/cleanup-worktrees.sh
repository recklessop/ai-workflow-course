#!/usr/bin/env bash
#
# Module 7 lab: tear down the two worktrees created by setup-worktrees.sh.
# The tool the coordinating AI session runs to clean up. Hand it to your agent, or copy it into
# tasks-app and let the agent run it:
#
#     cp ~/ai-workflow-course/modules/07-worktrees-running-agents-in-parallel/lab/cleanup-worktrees.sh .
#     bash cleanup-worktrees.sh
#
# `git worktree remove` deletes the folder AND clears Git's record of it; `prune` mops up any
# worktrees whose folders were deleted by hand (which leaves a stale record otherwise).
#
# NOTE: --force discards UNCOMMITTED work in a worktree. Commit (or merge) before cleaning up.
# This script assumes you already merged feature/wipe and feature/remaining back into main.
#
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
PARENT="$(cd "$ROOT/.." && pwd)"

git worktree remove "$PARENT/tasks-app-wipe" --force 2>/dev/null || true
git worktree remove "$PARENT/tasks-app-remaining" --force 2>/dev/null || true
git worktree prune

echo
echo "Cleanup done. Remaining worktrees:"
git worktree list

echo
echo "If you merged both branches you can also delete them:"
echo "    git branch -d feature/wipe feature/remaining"
