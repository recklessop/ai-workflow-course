#!/usr/bin/env bash
#
# verify-backup.sh: prove that your remote is a real, complete offsite backup.
#
# Module 8 lab helper. Run it from inside your tasks-app repo:
#     bash verify-backup.sh
#
# It checks three things, the three that make "I pushed" actually mean "it's backed up":
#   1. A remote is configured at all.
#   2. Your current branch is fully pushed; no commits stranded only on this disk.
#   3. A fresh clone of the remote carries the EXACT SAME commit count as your local repo,
#      i.e. the offsite copy is the whole history, not a snapshot.
#
# Works on macOS, Linux, WSL, and Git Bash on Windows. No dependencies beyond git.

set -u

# Fail fast instead of hanging. The clone and fetch below talk to the remote,
# and on the HTTPS+token path with no cached credential (a common fresh-Linux
# state) Git would stop to prompt for a username/password on the tty and block
# this check forever. Disabling interactive prompts turns that into a clean,
# non-zero failure that drops into the graceful warn branch below. SSH keys,
# public repos, and cached credential helpers are unaffected.
export GIT_TERMINAL_PROMPT=0

# --- tiny output helpers (fall back to plain text if no color) ---------------
if [ -t 1 ]; then
  GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
  GREEN=""; RED=""; YELLOW=""; BOLD=""; RESET=""
fi
pass() { printf "%s  PASS%s %s\n" "$GREEN" "$RESET" "$1"; }
fail() { printf "%s  FAIL%s %s\n" "$RED" "$RESET" "$1"; }
warn() { printf "%s  NOTE%s %s\n" "$YELLOW" "$RESET" "$1"; }

# --- must be inside a git repo ----------------------------------------------
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  fail "This isn't a Git repository. cd into your tasks-app repo and try again."
  exit 1
fi

printf "%sChecking that your remote is a real offsite backup...%s\n\n" "$BOLD" "$RESET"

remote="${1:-origin}"
branch="$(git rev-parse --abbrev-ref HEAD)"
status=0

# --- 1. is there a remote? ---------------------------------------------------
remote_url="$(git remote get-url "$remote" 2>/dev/null)"
if [ -z "$remote_url" ]; then
  fail "No remote named '$remote'. Add one with: git remote add origin <URL>"
  exit 1
fi
pass "Remote '$remote' is configured -> $remote_url"

# --- 2. is the current branch fully pushed? ----------------------------------
# Refresh our view of the remote without merging anything.
git fetch --quiet "$remote" 2>/dev/null

upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
if [ -z "$upstream" ]; then
  warn "Branch '$branch' has no upstream set. Push it with: git push -u $remote $branch"
  status=1
else
  ahead="$(git rev-list --count "${upstream}..HEAD" 2>/dev/null || echo "?")"
  if [ "$ahead" = "0" ]; then
    pass "Branch '$branch' is fully pushed to $upstream, nothing stranded on this disk."
  else
    fail "Branch '$branch' is $ahead commit(s) ahead of $upstream. Run: git push"
    status=1
  fi
fi

# --- 3. does a fresh clone carry the whole history? --------------------------
local_count="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
tmp="$(mktemp -d 2>/dev/null || mktemp -d -t verifybackup)"
trap 'rm -rf "$tmp"' EXIT

if git clone --quiet "$remote_url" "$tmp/clone" 2>/dev/null; then
  # Count commits on the same branch in the fresh clone, if it exists there.
  if git -C "$tmp/clone" rev-parse --verify --quiet "origin/$branch" >/dev/null 2>&1; then
    clone_count="$(git -C "$tmp/clone" rev-list --count "origin/$branch" 2>/dev/null || echo 0)"
  else
    clone_count="$(git -C "$tmp/clone" rev-list --count HEAD 2>/dev/null || echo 0)"
  fi

  if [ "$clone_count" = "$local_count" ]; then
    pass "Fresh clone has $clone_count commit(s), identical to your local $local_count."
    printf "\n%sThe offsite copy is COMPLETE: every commit, not just the latest files.%s\n" "$GREEN$BOLD" "$RESET"
    printf "That is the backup half of the course's backup-and-recovery thread.\n"
  else
    fail "Clone has $clone_count commit(s) but local has $local_count. Push your branch: git push"
    status=1
  fi
else
  warn "Couldn't clone $remote_url (auth or network?). The push checks above still stand."
fi

exit "$status"
