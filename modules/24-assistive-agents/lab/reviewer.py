"""Assistive AI reviewer: local simulation of a PR-reviewer bot.

This stands in for a forge-native reviewer (an app/bot triggered when a PR opens, running on a
runner from Module 19) without needing any hosted account. It does the two deterministic halves of
the job and leaves the one judgment call (what actually happens to the PR) to you.

    python3 reviewer.py prompt              # assemble the prompt: rubric + diff, for the agent to review
    python3 reviewer.py apply ai-review.sample.json   # ingest the agent's JSON, render it, gate it

The point of this module: the agent produces comments and a recommendation. It never approves,
never requests-changes-as-a-gate, never merges. The `apply` step ends at a HUMAN DECISION, every
time. Stdlib only, no pip install.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def load_json_response(path: Path):
    """Parse the JSON the AI returned.

    Chat assistants very often wrap their output in a ```json ... ``` code fence (or add a stray
    line of text) even when told to "return only the JSON", so a strict json.loads on the raw paste
    fails on the most likely real output. Try a strict parse first; if that fails, fall back to the
    outermost { ... } block, which survives a code fence or surrounding text. Stdlib only."""
    raw = path.read_text()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end > start:
            return json.loads(raw[start : end + 1])
        raise


PROMPT_HEADER = """\
You are an assistive code reviewer. Follow the rubric below exactly, then review the diff that
follows it. Return ONLY the JSON object the rubric specifies, with no extra text before or after.

================ REVIEW RUBRIC ================
{rubric}

================ DIFF UNDER REVIEW ============
{diff}
"""


def cmd_prompt(args: argparse.Namespace) -> int:
    rubric = Path(args.rubric).read_text()
    diff = Path(args.patch).read_text()
    print(PROMPT_HEADER.format(rubric=rubric, diff=diff))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    try:
        review = load_json_response(Path(args.response))
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"error: could not read a JSON review from {args.response}: {exc}")
        return 1

    summary = review.get("summary", "(no summary)")
    recommendation = review.get("recommendation", "comment")
    comments = review.get("comments", [])

    print("=" * 70)
    print("AI REVIEWER: first pass (advisory only)")
    print("=" * 70)
    print(f"\nSummary: {summary}\n")

    if not comments:
        print("No line comments.\n")
    order = {"blocker": 0, "suggestion": 1, "nit": 2}
    for c in sorted(comments, key=lambda c: order.get(c.get("severity", "nit"), 9)):
        sev = c.get("severity", "nit").upper()
        loc = f"{c.get('file', '?')}:{c.get('line', '?')}"
        print(f"  [{sev:10}] {loc}")
        print(f"             {c.get('comment', '')}\n")

    print("-" * 70)
    print(f"Agent's recommendation: {recommendation}")
    print("-" * 70)
    print(
        "\nThis is the human decision gate. The agent did NOT merge, approve, or block.\n"
        "It only commented. You decide what happens next:\n"
        "  - merge          you read the comments, you disagree or they're addressed\n"
        "  - request changes you agree; push the fix on the branch and re-run\n"
        "  - dismiss         the agent is wrong or noisy; ignore and move on\n"
        "\nNothing in this repo changes until you act. That's the whole point of Module 24.\n"
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prompt", help="assemble the review prompt for the agent to act on")
    p.add_argument("--rubric", default=str(HERE / "review-rubric.md"))
    p.add_argument("--patch", default=str(HERE / "feature.patch"))
    p.set_defaults(func=cmd_prompt)

    a = sub.add_parser("apply", help="ingest the AI's JSON review and render the decision gate")
    a.add_argument("response", help="path to the JSON the AI returned")
    a.set_defaults(func=cmd_apply)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
