"""A 'sync' command for the tasks-app: the BEFORE picture for Module 17.

This is exactly the kind of file an AI hands you when you ask it to "add a command that syncs
tasks to our backend." It works. It also has two AI-classic mistakes baked in:

  1. The API key is hardcoded right here in the source (see API_KEY below).
  2. The backend URL is hardcoded too, so there is no way to point dev at a dev server and
     prod at the prod one without editing code.

Your job in the lab is to refactor BOTH out of the source and into the environment. Don't read
ahead and fix it yet; first run it as-is so you can see the smell.

Run it:
    python3 sync.py

It does not actually hit the network (so the lab works offline, on any OS); it simulates the
request and prints what it *would* send.
"""

import json
from pathlib import Path

# --- The anti-pattern. This is what we are here to remove. ---------------------------------
API_KEY = "sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c"   # <-- a real-looking secret, in source
BACKEND_URL = "https://api.example-tasks.com/v1"        # <-- environment baked into code
# -------------------------------------------------------------------------------------------

STATE = Path(__file__).parent / "tasks.json"


def load_task_count() -> int:
    """Count tasks from the tasks-app state file, if it exists."""
    if not STATE.exists():
        return 0
    return len(json.loads(STATE.read_text()))


def sync() -> int:
    count = load_task_count()
    # In a real client this would be an authenticated HTTP request. We just show what it'd send.
    print(f"POST {BACKEND_URL}/tasks/sync")
    print(f"Authorization: Bearer {API_KEY}")
    print(f"Body: {{\"task_count\": {count}}}")
    print("(simulated) sync OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(sync())
