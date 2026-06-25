Title: `done` command crashes on an empty list

When I run `python3 cli.py done 0` right after a fresh checkout, before adding any tasks, it throws
an IndexError and dumps a stack trace instead of a friendly message. Every other command handles the
empty-list case fine, so this one feels like an oversight.

Steps to reproduce:
1. Delete tasks.json (or clone fresh).
2. Run `python3 cli.py done 0`.
3. See the traceback.

Expected: a clear message like "no task at index 0", exit non-zero, no traceback.

Environment: Python 3.12, macOS.
