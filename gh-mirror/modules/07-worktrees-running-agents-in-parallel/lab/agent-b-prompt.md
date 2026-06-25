# Agent B prompt: the `remaining` command

Paste this into the AI session you've pointed at the `tasks-app-remaining` worktree folder.

---

Add a `remaining` command to this task app that prints how many tasks are still pending.

- Reuse the existing `pending()` method on `TaskList` in `tasks.py`; don't reimplement it.
- Wire a `remaining` command into the dispatch in `cli.py`.
- Running `python3 cli.py remaining` should print something like `2 pending` (the number of tasks not
  marked done).

Make the change, then stop. I'll review the diff, then have you commit it on this branch.
