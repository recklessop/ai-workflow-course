# Agent prompt: issue #43, branch `feature/43-docs`

Run this in the `tasks-app-43-docs` worktree. This agent owns documentation only, different files
from every other agent in the fleet, so it merges cleanly no matter what the others do. This is what
a *genuinely* parallel split looks like: disjoint files, no shared interface.

---

You are working in this worktree only. Do not touch any other folder, and do not edit `cli.py` or
`tasks.py`; code is owned by other agents.

**Task:** Document the `tasks-app` and start a changelog.

- In `README.md`, add a "Commands" section documenting the existing commands: `add <title>`, `list`,
  and `done <index>`. Show an example invocation for each.
- Create `CHANGELOG.md` with a "Keep a Changelog"–style `## [Unreleased]` section and an `### Added`
  list. (Other agents are adding commands in parallel; leave a placeholder line noting that new
  commands are landing; the human will reconcile the exact list at merge.)

**Acceptance criteria:**

- `README.md` documents the three existing commands accurately.
- `CHANGELOG.md` exists and is valid markdown.
- No code files change.

When done, commit your work on this branch with a message referencing #43, then push the branch. Stop
there; the human opens and reviews the PR.
