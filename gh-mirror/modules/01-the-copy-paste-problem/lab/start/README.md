# Demo app: `tasks`

A deliberately tiny command-line task tracker. It exists to be *changed by an AI*, so it's small
enough to read in a minute but real enough to have more than one file, which is exactly where the
copy-paste workflow starts to hurt.

This is the running example for **Module 1** (where you feel the copy-paste problem) and **Module 2**
(where you put it under version control).

## Files

- `tasks.py`: the core logic (`Task`, `TaskList`).
- `cli.py`: the command-line front end. Reads/writes `tasks.json`.

## Run it

```bash
python3 cli.py add "read module 1"
python3 cli.py add "set up my editor"
python3 cli.py list
python3 cli.py done 0
python3 cli.py list
```

Requires Python 3.10+ (it uses `list[Task]` style type hints). No third-party packages.
