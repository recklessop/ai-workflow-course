<!--
  Module 11 lab: the pull request description (station 4 of the loop).

  Paste this as the body when you open the PR from your branch into main. The "Closes" line is the
  load-bearing part: replace 42 with YOUR issue number. On merge to the default branch, the host
  closes that issue automatically and cross-links the two.

  Closing keywords that work across the major hosts: Closes / Fixes / Resolves (and their
  variants). A bare "#42" links the issue but does NOT close it on merge.
-->

## What this does

Adds a `clear-done` command that removes all completed tasks. The removal logic is a new `TaskList`
method in `tasks.py`; `cli.py` just wires up the command and reports how many tasks were removed.

## How I tested it

- Added a mix of pending and done tasks, ran `clear-done`, confirmed only the done ones were removed
  and the count printed.
- Ran `clear-done` with nothing marked done: removed 0, no crash.

## Review notes

Small two-file change. Check that the logic sits in `tasks.py` (not the CLI) and that the empty /
nothing-done case is handled.

Closes #42
