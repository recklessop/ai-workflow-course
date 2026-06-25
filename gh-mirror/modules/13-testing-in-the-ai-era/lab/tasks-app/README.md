# Demo app: `tasks` (Module 13 copy)

The same tiny task tracker from Modules 1 and 2, with one feature added: a `count` command backed
by `TaskList.pending_count()`. Use this copy for the Module 13 lab so everyone starts from the same
code, including the same latent bug.

If you already have a `tasks-app` from earlier modules, you can use that instead; just make sure it
has a `count` command (the Module 2 lab added one). The planted bug in this copy is there on purpose.

## Files

- `tasks.py`: core logic (`Task`, `TaskList`), now with `pending_count()`.
- `cli.py`: command-line front end. Adds `count`.

## Run it

```bash
python3 cli.py add "write the tests"
python3 cli.py add "fix the bug"
python3 cli.py done 0
python3 cli.py list
python3 cli.py count
```

Requires Python 3.10+. No third-party packages; tests use the standard library `unittest`.
