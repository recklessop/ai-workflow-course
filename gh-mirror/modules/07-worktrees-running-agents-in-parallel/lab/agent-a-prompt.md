# Agent A prompt: the `wipe` command

Paste this into the AI session you've pointed at the `tasks-app-wipe` worktree folder.

---

Add a `wipe` command to this task app that removes **all** tasks.

- Put the deletion logic on `TaskList` in `tasks.py` (a `wipe()` method that empties the list),
  and wire a `wipe` command into the dispatch in `cli.py` that calls it and saves.
- Running `python3 cli.py wipe` should empty the list and print a short confirmation like
  `wiped all tasks`.
- After `wipe`, `python3 cli.py list` should print `(no tasks yet)`.

Make the change, then stop. I'll review the diff, then have you commit it on this branch.
