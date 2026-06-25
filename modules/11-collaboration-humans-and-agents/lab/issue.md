<!--
  Module 11 lab: the issue to file (the "contract" / station 1 of the loop).

  Create a new issue on your git host. Paste the line below as the TITLE and everything under
  "Body" as the issue description. Note the number the host assigns it (e.g. #42); every later
  step references it. Assign it to yourself for the first run-through.
-->

Title: Add a `clear-done` command to remove completed tasks

Body:

**What**
Add a `clear-done` command to the tasks CLI that removes every task already marked done, leaving
the pending ones untouched.

**Why**
After working through a list, the completed items pile up as noise. There's currently no way to
clear them out short of editing `tasks.json` by hand.

**Acceptance criteria**
- `python3 cli.py clear-done` removes all completed tasks and keeps all pending ones.
- It prints how many tasks were removed.
- The removal logic lives in `tasks.py` (a `TaskList` method), not in `cli.py`.
- Running it when nothing is done is a no-op that removes 0 tasks (no crash).
