"""Minimal HTTP face for the tasks-app, so there is something long-running to *deploy*.

Standard library only, no pip install, so the container image stays tiny and the lab has no
dependencies to drift. It reuses the TaskList from tasks.py (Modules 1-2) unchanged.

Run it:
    python3 serve.py            # serves on http://localhost:8000

Endpoints:
    GET /health   -> {"status": "ok", "version": <APP_VERSION>}   (200)
    GET /tasks    -> the current tasks as JSON

Two environment knobs make this realistic for the CD lab (config injected at run time, Module 17):
    APP_VERSION   what /health reports as the running version (set by deploy.sh to the commit SHA)
    BREAK=1       force /health to return 500, a stand-in for "this build starts but is broken",
                  used in Part D to trigger an automatic rollback.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tasks import Task, TaskList

STATE = Path(__file__).parent / "tasks.json"
PORT = int(os.environ.get("PORT", "8000"))
APP_VERSION = os.environ.get("APP_VERSION", "dev")
BREAK = os.environ.get("BREAK") == "1"


def load() -> TaskList:
    if not STATE.exists():
        return TaskList()
    raw = json.loads(STATE.read_text())
    return TaskList(tasks=[Task(**t) for t in raw])


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            # A real health check would also confirm dependencies (db, etc.) are reachable.
            if BREAK:
                self._send(500, {"status": "unhealthy", "version": APP_VERSION})
            else:
                self._send(200, {"status": "ok", "version": APP_VERSION})
        elif self.path == "/tasks":
            tlist = load()
            self._send(200, {"tasks": [t.__dict__ for t in tlist.tasks]})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args) -> None:  # keep the lab output clean
        pass


if __name__ == "__main__":
    print(f"serving tasks-app version={APP_VERSION} on http://localhost:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
