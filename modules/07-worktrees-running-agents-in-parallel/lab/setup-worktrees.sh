#!/usr/bin/env bash
#
# Module 7 lab: create two linked worktrees off the tasks-app repo, each on its own branch.
# This is the tool the coordinating AI session (the one already pointed at tasks-app) can run to
# set up the worktrees. Hand it to your agent, or copy it into tasks-app and let the agent run it:
#
#     cp ~/ai-workflow-course/modules/07-worktrees-running-agents-in-parallel/lab/setup-worktrees.sh .
#     bash setup-worktrees.sh
#
# It places the new worktree folders next to the repo, so you end up with:
#
#     <parent>/tasks-app              (your existing repo, on its current branch)
#     <parent>/tasks-app-wipe         (new worktree on branch feature/wipe)
#     <parent>/tasks-app-remaining    (new worktree on branch feature/remaining)
#
set -euo pipefail

# The directory that contains the repo, so the new worktrees become siblings of it.
ROOT="$(git rev-parse --show-toplevel)"
PARENT="$(cd "$ROOT/.." && pwd)"

git worktree add "$PARENT/tasks-app-wipe" -b feature/wipe
git worktree add "$PARENT/tasks-app-remaining" -b feature/remaining

echo
echo "Worktrees created. One repo, three checked-out branches:"
git worktree list
