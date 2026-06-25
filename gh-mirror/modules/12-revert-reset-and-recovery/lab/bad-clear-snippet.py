# Module 12 lab: the deliberately BROKEN `clear` command.
#
# Paste the elif block below into cli.py's main(), alongside the other
# `elif command == "..."` branches (e.g. right after the "done" branch).
# Do NOT paste this header or the import line into cli.py if json is already
# imported there (it is); just the elif block.
#
# Why it's broken: it "works" once (prints a friendly message), but it writes
# the state file in the WRONG SHAPE. The next time the app loads tasks.json,
# load() tries to build Task(**t) from a plain string and crashes. Classic
# AI plausibility trap: reviews fine, runs fine once, breaks the next command.
#
# This exists so the lab's bad merge is deterministic across every learner.

    elif command == "clear":
        # BAD on purpose: dumps a bare string list instead of a list of task
        # dicts, so the next load() -> Task(**t) blows up with a TypeError.
        STATE.write_text(json.dumps(["cleared"]))
        print("cleared all tasks")
