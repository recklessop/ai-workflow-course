"""Tiny command-line front end for the demo task app.

Run it:
    python3 cli.py add "write the lesson"
    python3 cli.py list
    python3 cli.py done 0

State is kept in tasks.json next to this file. The `done` command turns a bad index into a
clean error message and a non-zero exit code; note that behavior before you review the AI
change, so you can tell if the change quietly alters it.
"""

import json
import sys
from pathlib import Path

from tasks import Task, TaskList

STATE = Path(__file__).parent / "tasks.json"


def load() -> TaskList:
    if not STATE.exists():
        return TaskList()
    raw = json.loads(STATE.read_text())
    return TaskList(tasks=[Task(**t) for t in raw])


def save(tlist: TaskList) -> None:
    STATE.write_text(json.dumps([t.__dict__ for t in tlist.tasks], indent=2))


def main(argv: list[str]) -> int:
    tlist = load()
    if not argv:
        print("usage: python3 cli.py [add <title> | list | done <index>]")
        return 1

    command = argv[0]
    if command == "add":
        title = " ".join(argv[1:])
        tlist.add(title)
        save(tlist)
        print(f"added: {title}")
    elif command == "list":
        print(tlist.render())
    elif command == "done":
        try:
            tlist.complete(int(argv[1]))
        except IndexError as exc:
            print(f"error: {exc}")
            return 1
        save(tlist)
        print("updated")
    else:
        print(f"unknown command: {command}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
