# Skill: Add a new tasks-app command, end to end

> A reusable playbook. Don't paste this whole file into a chat and hope. Point your agentic tool at
> it by name ("follow `add-command.md` to add a `clear` command"), or drop it wherever your tool
> auto-discovers procedures (a skills/commands folder). The steps are the same either way.

## When to use this

Invoke this whenever the task is **"add a new subcommand to the `tasks-app` CLI."** It exists so a
new command lands the *same* way every time: real code, a real test, a changelog line, and a clean
commit; never just the code with the rest forgotten.

If the task is *not* "add a CLI command" (a bug fix, a refactor, a docs change), this skill does not
apply. Don't force it.

## Inputs you need before starting

Ask for these if they weren't given:

- `COMMAND_NAME`: the subcommand word, e.g. `clear`.
- `WHAT_IT_DOES`: one sentence of intended behavior, e.g. "remove all tasks."

## Project facts (so you don't have to rediscover them)

- Core logic lives in `tasks.py` (the `TaskList` class). The CLI front end is `cli.py`. State
  persists to `tasks.json`. **Never edit `tasks.json` by hand; it's generated.**
- Tests live in `test_tasks.py` and run with `python3 -m unittest`. Standard library only; no
  third-party packages, no new dependencies.
- The human-facing change log is `CHANGELOG.md`, newest entry on top.

## Procedure: do these in order, do not skip

1. **Core logic in `tasks.py`.** If the command needs new behavior on the task list, add a small
   method to `TaskList` (e.g. `clear()`). Keep it minimal; match the existing style. If the command
   only reads existing state, skip to step 2.

2. **Wire the CLI in `cli.py`.** Add a branch to `main()` for `COMMAND_NAME`, call into `tasks.py`,
   `save()` if it mutated state, and print a short confirmation. Add the command to the `usage:`
   string so it's discoverable.

3. **Add a real test in `test_tasks.py`.** Test the *behavior you intended*, not just "it doesn't
   crash." Assert the end state (e.g. after `clear()`, `len(tasks) == 0` and `pending()` is empty).
   A test that passes against a broken implementation is worse than no test.

4. **Run the tests.** `python3 -m unittest` from the project root. Do not claim success until it's
   green. If it fails, fix the code, not the test, and run again.

5. **Smoke-test the CLI.** Actually run it: `python3 cli.py COMMAND_NAME`, then `python3 cli.py list`
   to confirm the visible result. Paste what you ran and what it printed.

6. **Add a `CHANGELOG.md` entry.** One line under the top heading, present tense:
   `- Add \`COMMAND_NAME\` command: WHAT_IT_DOES.` Newest on top.

7. **Commit as one logical change.** Stage code + test + changelog together and commit with a
   message that names the command: `git add tasks.py cli.py test_tasks.py CHANGELOG.md && git commit
   -m "Add COMMAND_NAME command"`. Do **not** stage `tasks.json`.

## Done when

- `python3 -m unittest` is green and includes a new test that actually exercises `COMMAND_NAME`.
- `python3 cli.py COMMAND_NAME` does `WHAT_IT_DOES` and you've shown the output.
- `CHANGELOG.md` has a new top line for the command.
- One commit contains the code, the test, and the changelog line, and nothing else (no
  `tasks.json`, no unrelated reformatting).

If any of those is missing, the skill isn't finished. Report which step failed and stop; don't
paper over it.
