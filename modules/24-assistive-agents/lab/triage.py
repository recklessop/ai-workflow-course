"""Assistive issue-triage agent: local simulation of a triage bot.

Stands in for a forge-native triage agent (triggered when an issue opens) without a hosted account.
It assembles the prompt, then validates and renders the AI's suggestion, and stops at a human
confirm. The agent proposes labels and a route; it does not apply them.

    python3 triage.py prompt                          # taxonomy + issue -> prompt for the agent
    python3 triage.py apply ai-triage.sample.json     # validate + render + confirm gate

The validation step matters: the agent may only use labels that exist in label-taxonomy.md. A
hallucinated label is rejected. Stdlib only, no pip install.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent

PROMPT_HEADER = """\
You are an assistive issue-triage agent. Using ONLY the taxonomy below, propose labels, a route,
and a rationale for the issue that follows. Return ONLY the JSON object the taxonomy specifies.

================ LABEL TAXONOMY ===============
{taxonomy}

================ INCOMING ISSUE ===============
{issue}
"""

# Allowed labels are the backticked `prefix:value` tokens in the taxonomy file. Keeping the source
# of truth in the committed markdown (not hardcoded here) is the point.
LABEL_RE = re.compile(r"`([a-z]+:[a-z0-9-]+)`")


def allowed_labels(taxonomy_text: str) -> set[str]:
    return set(LABEL_RE.findall(taxonomy_text))


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


def cmd_prompt(args: argparse.Namespace) -> int:
    taxonomy = Path(args.taxonomy).read_text()
    issue = Path(args.issue).read_text()
    print(PROMPT_HEADER.format(taxonomy=taxonomy, issue=issue))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    allowed = allowed_labels(Path(args.taxonomy).read_text())
    try:
        sug = load_json_response(Path(args.response))
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"error: could not read a JSON suggestion from {args.response}: {exc}")
        return 1

    labels = sug.get("labels", [])
    bogus = [l for l in labels if l not in allowed]
    if bogus:
        print("=" * 70)
        print("REJECTED: the agent suggested labels that aren't in the taxonomy:")
        for l in bogus:
            print(f"  - {l}")
        print(
            "\nThis is the guardrail working. The agent can only use labels you've committed to\n"
            "label-taxonomy.md. Fix the prompt or the taxonomy and re-run; do not apply this.\n"
        )
        return 1

    print("=" * 70)
    print("TRIAGE AGENT: suggestion (advisory only)")
    print("=" * 70)
    print(f"\n  Labels:        {', '.join(labels) or '(none)'}")
    print(f"  Route to:      {sug.get('assignee_type', '?')}")
    print(f"  Confidence:    {sug.get('confidence', '?')}")
    print(f"  Rationale:     {sug.get('rationale', '')}\n")

    print("-" * 70)
    print(
        "Human confirm gate. The agent did NOT apply these labels or assign anyone.\n"
        "You decide:\n"
        "  - confirm   apply the labels and route as proposed\n"
        "  - edit      change a label or the route, then apply\n"
        "  - reject    the triage is wrong; do it yourself\n"
        "\nA wrong label here costs one glance and one click to fix, which is exactly why\n"
        "triage is the safe place to let an agent in first.\n"
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prompt", help="assemble the triage prompt for the agent to act on")
    p.add_argument("--taxonomy", default=str(HERE / "label-taxonomy.md"))
    p.add_argument("--issue", default=str(HERE / "sample-issue.md"))
    p.set_defaults(func=cmd_prompt)

    a = sub.add_parser("apply", help="validate + render the AI's suggestion, then gate it")
    a.add_argument("response", help="path to the JSON the AI returned")
    a.add_argument("--taxonomy", default=str(HERE / "label-taxonomy.md"))
    a.set_defaults(func=cmd_apply)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
