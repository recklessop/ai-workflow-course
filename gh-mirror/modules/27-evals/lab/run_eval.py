"""Run the eval set against one candidate and print a scorecard.

Usage:
    python3 run_eval.py candidates/current_model
    python3 run_eval.py candidates/swapped_model
    python3 run_eval.py candidates/current_model --threshold 0.9

A "candidate" is a directory containing a tasks.py that an agent produced. The
runner imports that tasks.py, runs every case in eval_set.py against it, prints
a pass/fail line per case, and reports an aggregate score.

The exit code is the guardrail: 0 if the score meets the threshold, 1 if it
doesn't. That single integer is what lets an eval gate a model swap, a prompt
change, or an unattended agent in CI (Module 14) instead of a human eyeballing
output. "Below threshold" should block exactly like a failing test does.
"""

import argparse
import importlib.util
import sys
from pathlib import Path

from eval_set import CASES


def load_candidate(candidate_dir: Path):
    """Import the tasks.py living in candidate_dir as an isolated module."""
    tasks_py = candidate_dir / "tasks.py"
    if not tasks_py.exists():
        sys.exit(f"no tasks.py in {candidate_dir}")
    spec = importlib.util.spec_from_file_location("candidate_tasks", tasks_py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_case(candidate, items, expected):
    """Build the input state with the candidate's own classes, then grade."""
    tlist = candidate.TaskList()
    for title, done in items:
        tlist.tasks.append(candidate.Task(title=title, done=done))
    try:
        actual = tlist.pending_count()
    except Exception as exc:  # a crash is a failed case, not a crashed harness
        return False, f"raised {type(exc).__name__}: {exc}"
    return actual == expected, f"expected {expected}, got {actual}"


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", help="path to a candidate dir with tasks.py")
    parser.add_argument("--threshold", type=float, default=1.0,
                        help="minimum passing fraction to exit 0 (default 1.0)")
    args = parser.parse_args(argv)

    candidate_dir = Path(args.candidate)
    candidate = load_candidate(candidate_dir)

    passed = 0
    print(f"\neval set: {len(CASES)} cases   candidate: {candidate_dir}\n")
    for name, items, expected in CASES:
        ok, detail = run_case(candidate, items, expected)
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name:<40} ({detail})")
        passed += ok

    score = passed / len(CASES)
    print(f"\nscore: {passed}/{len(CASES)} = {score:.0%}   threshold: {args.threshold:.0%}")

    if score < args.threshold:
        print("RESULT: below threshold; this change is NOT safe to ship.\n")
        return 1
    print("RESULT: at or above threshold; safe by this eval.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
