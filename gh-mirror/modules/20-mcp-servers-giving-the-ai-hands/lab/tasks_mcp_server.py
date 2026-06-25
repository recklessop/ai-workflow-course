"""A tiny MCP server that gives an AI client hands on the tasks-app.

It exposes the tasks-app over the Model Context Protocol (MCP) so an agentic tool can read and
change your real task list directly, with no copy-paste and no pasting tasks.json into a chat window.

The whole server is the decorated functions below. FastMCP (from the official Python SDK) turns
each `@mcp.tool()` function into a tool the AI client can discover and call. That's it: a tool is
a normal Python function plus a docstring the client reads to know what it does.

Setup (once):
    pip install "mcp[cli]"

Drop this file into your tasks-app folder, next to tasks.py and cli.py (it reuses them, and shares
the same tasks.json, so a task the AI adds through this server shows up in `python3 cli.py list`).

Sanity-check that it starts (it will sit waiting for a client to talk to it; Ctrl-C to stop):
    python3 tasks_mcp_server.py

You don't normally run it by hand, though. Your agentic tool launches it for you; see the lab.
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from tasks import Task, TaskList

STATE = Path(__file__).parent / "tasks.json"

# The name is how the server identifies itself to the client.
mcp = FastMCP("tasks")


def _load() -> TaskList:
    if not STATE.exists():
        return TaskList()
    raw = json.loads(STATE.read_text())
    return TaskList(tasks=[Task(**t) for t in raw])


def _save(tlist: TaskList) -> None:
    STATE.write_text(json.dumps([t.__dict__ for t in tlist.tasks], indent=2))


@mcp.tool()
def list_tasks() -> str:
    """List every task in the tasks-app, with its index and whether it's done."""
    return _load().render()


@mcp.tool()
def add_task(title: str) -> str:
    """Add a new task to the tasks-app. `title` is the text of the task to add."""
    tlist = _load()
    tlist.add(title)
    _save(tlist)
    return f"added: {title}"


if __name__ == "__main__":
    # stdio transport by default: the client launches this process and talks to it over
    # stdin/stdout. That's why the server "just sits there" when you run it by hand: it's
    # waiting for a client on the other end of the pipe.
    mcp.run()
