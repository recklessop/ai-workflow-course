"""Cloud-sync config for tasks-app: a realistic snapshot of what an AI hands you.

Asked to "sync tasks to a cloud service," a model will produce something like this: it works, it
reads naturally, it passes lint and tests... and it carries two planted flaws: a live credential
baked straight into the source (caught by Gate 2, secret scanning) and a weak-crypto "signature"
using MD5 (caught by Gate 3, SAST). Two different gates, two different blind spots.

DO NOT copy these patterns. The point of this file is to be caught by a scanner, not imitated.
The fix (read from the environment) is shown at the bottom, commented out, so you can see the
difference once Part C of the lab is done.
"""

import hashlib

# --- The problem the SECRET scanner should flag (Gate 2) ---------------------------------------
# A hardcoded API key. Looks like a normal string literal; lint and tests will never complain.
SYNC_API_KEY = "k7c9f2a4b8d6e1039284756abcdef0123456789abcdef0123456789abcdef0123"
SYNC_ENDPOINT = "https://api.example-task-cloud.com/v1/sync"


def sync_headers() -> dict:
    return {"Authorization": f"Bearer {SYNC_API_KEY}"}


# --- The problem the SAST scanner should flag (Gate 3) -----------------------------------------
# AI-classic: "sign" the request body with a quick hash. MD5 is broken for anything
# security-relevant; a textbook weak-crypto idiom. A secret scanner won't catch this (it's not a
# secret); a SAST tool like bandit will (it's insecure code you wrote). DO NOT imitate.
def sign_payload(body: str) -> str:
    return hashlib.md5(body.encode()).hexdigest()


# --- The fix (Part C) --------------------------------------------------------------------------
# Read the secret from the environment instead of committing it. Proper secret management (env
# files, secret stores, per-environment config) is Module 17. This is just enough to make the
# scanner go quiet honestly.
#
# import os
# SYNC_API_KEY = os.environ["SYNC_API_KEY"]   # set it outside the repo; never commit the value
