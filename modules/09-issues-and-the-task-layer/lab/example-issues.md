<!--
  Worked example issues for the tasks-app, Module 9 of "The Workflow".

  These are a reference / answer key. Write your OWN three issues from issue-template.md FIRST, then
  compare. Yours don't need to match word for word; check that each has a specific title, real
  context (with repro for the bug), concrete acceptance criteria, and a stated scope.

  Note how the routing call is a property of the ISSUE (clear vs. ambiguous), not the model.

  Because the tasks-app carries forward across modules, some commands you might reach for (a
  `delete` command, task priorities) may already exist from earlier labs. These examples
  deliberately target work the app does NOT have yet, so each reads as a genuine open issue.
-->

# Issue 1: bug, route to AGENT

# Title: `done` command crashes on an out-of-range or non-integer index

## Context / problem

`python3 cli.py done 99` on a list with 3 tasks raises an uncaught `IndexError` and dumps a Python
traceback. `python3 cli.py done abc` raises `ValueError` the same way. The user sees a stack trace
instead of a helpful message, and the process exits as if it crashed.

Reproduce:

```
python3 cli.py add "first"
python3 cli.py done 99      # IndexError traceback
python3 cli.py done abc     # ValueError traceback
```

## Acceptance criteria

- [ ] `done <index>` with an out-of-range index prints a clear message (e.g. `no task at index 99`)
      and exits non-zero, with no traceback.
- [ ] `done <non-integer>` prints a clear message and exits non-zero, with no traceback.
- [ ] A valid `done <index>` still marks the task done exactly as before.

## Out of scope

Changing how tasks are stored, numbered, or displayed.

---
- **Type:** bug
- **Priority:** high
- **Ready:** yes
- **Route to:** agent. Contained, reproducible, and verifiable in seconds; clear acceptance criteria
  mean an agent's first pass is very likely correct.


# Issue 2: feature, route to AGENT

# Title: Add an `undone <index>` command to mark a completed task as not done

## Context / problem

You can mark a task `done`, but there's no way to undo it; flag the wrong index by mistake and the
only "fix" is to delete the task and re-add it. The command should mirror the existing `done <index>`
command, which already takes an index and flips a task's state; this is simply its inverse.

## Acceptance criteria

- [ ] `python3 cli.py undone <index>` clears the done flag on the task at that index and saves.
- [ ] `undone` with an out-of-range or non-integer index prints a clear error and exits non-zero
      (same behavior as the fixed `done`, see Issue 1).
- [ ] `list` after `undone` shows that task as not done (`[ ]`).
- [ ] Usage text mentions the new `undone` command.

## Out of scope

A general multi-step undo / command history (separate concern). Changing the storage format.

## Proposed approach (optional)

Add a `reopen(index)` method on `TaskList` in `tasks.py` (the inverse of the existing `complete`)
and wire an `undone` branch in `cli.py`, parallel to the existing `done` handling.

---
- **Type:** feature
- **Priority:** med
- **Ready:** yes
- **Route to:** agent. Well-scoped and patterned directly on existing code (the inverse of `done`);
  low ambiguity, easy to verify.


# Issue 3: feature, route to HUMAN

# Title: Support due dates on tasks

## Context / problem

Users want to attach a due date to a task so the list can reflect what's coming up, not just what
exists. Today a task is only a title and a done flag. This is desirable but underspecified; several
product decisions have to be made before any code is written.

Open questions (resolve before this is `ready`):
- What date format does the user type, and how forgiving is parsing? (ISO `2026-06-30` only, or
  relative like `tomorrow` / `friday`?)
- Does `list` re-sort by due date, group by it, or just display it inline?
- How is a due date set: at `add` time (a flag?) or with a separate command? Can it be cleared?
- How are overdue tasks surfaced (highlighted, flagged, sorted to the top), and in whose timezone?
- How is it stored, and what's the default for the existing tasks that have none?

## Acceptance criteria

- [ ] (Cannot be written yet; depends on the decisions above. Likely splits into 2-3 smaller,
      agent-ready issues once the design is settled.)

## Out of scope

TBD until the design questions are answered.

---
- **Type:** feature
- **Priority:** low
- **Ready:** no
- **Route to:** human. Genuine design ambiguity. An agent would answer these questions confidently
  and probably wrongly. A person decides the design, then splits this into clear sub-issues (which
  may then be agent-ready).
