# Agent prompt: issue #42, branch `feature/42-count`

Run this in the `tasks-app-42-count` worktree. This agent's work is genuinely parallel with #43
(docs), which touches different files, and deliberately collides with #44 (clear) at `cli.py`'s dispatch chain.

---

You are working in this worktree only. Do not touch any other folder.

**Task:** Add a `count` command to `cli.py` that prints the number of *pending* (not-done) tasks.

- Add a new `elif command == "count":` branch to the dispatch in `main()` in `cli.py`.
- Use the existing `TaskList.pending()` method from `tasks.py`; do not change `tasks.py`.
- Print just the integer, e.g. `3`.

**Acceptance criteria:**

- `python3 cli.py count` prints the number of pending tasks and exits 0.
- No other files change. (`README.md`, `CHANGELOG.md`, and `tasks.py` are owned by other agents;
  stay out of them.)

When done, commit your work on this branch with a message referencing #42, then push the branch. Stop
there; the human opens and reviews the PR.
