# Agent prompt: issue #44, branch `feature/44-clear`

Run this in the `tasks-app-44-clear` worktree. **This agent deliberately collides with #42.** Both
add a new `elif` to the same dispatch chain in `cli.py`: same file, same region. That's the
agent-vs-agent merge conflict the lab wants you to predict in Part A and resolve in Part C. It is not
a mistake in the lab; it is the lesson. Two agents on the same file is a *joint*, not a seam.

---

You are working in this worktree only. Do not touch any other folder.

**Task:** Add a `clear` command to `cli.py` that removes all tasks.

- Add a new `elif command == "clear":` branch to the dispatch in `main()` in `cli.py`.
- It should empty the task list and save, then print `cleared`.
- Reuse the existing `load()` / `save()` helpers. Do not change `tasks.py`.

**Acceptance criteria:**

- `python3 cli.py clear` removes all tasks and prints `cleared`.
- `python3 cli.py list` afterward shows `(no tasks yet)`.

When done, commit your work on this branch with a message referencing #44, then push the branch. Stop
there; the human opens and reviews the PR, and should expect a conflict against `feature/42-count` at
merge.
