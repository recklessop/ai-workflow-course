# Label taxonomy: the triage agent's instructions

The triage agent reads this file, then reads one incoming issue, and proposes labels, a priority,
and where the issue should be routed. Like the review rubric, this is committed and versioned: your
triage taxonomy is a project decision, not a setting buried in some bot's web UI.

**The labels below are the only labels that exist.** The agent must choose from this list. If it
invents a label that isn't here, the lab's `triage.py` rejects the whole suggestion; that rejection
is a guardrail, not a bug. An agent that can mint arbitrary labels is an agent that can quietly
reshape your taxonomy; keeping the allowed set in version control and validating against it is how
you keep the agent inside its lane (the least-privilege idea from Module 22).

## Allowed labels

Type (exactly one):
- `type:bug`: something is broken or behaves wrong
- `type:feature`: a request for new behavior
- `type:docs`: documentation only
- `type:question`: a usage question, not a code change

Priority (exactly one):
- `priority:p0`: data loss, security, or the app is unusable for everyone
- `priority:p1`: a serious bug with no good workaround
- `priority:p2`: a real bug with a workaround, or a wanted feature
- `priority:p3`: minor, cosmetic, or nice-to-have

Area (zero or more):
- `area:cli`: the command-line front end (`cli.py`)
- `area:core`: task logic (`tasks.py`)
- `area:docs`: README and lesson text

Readiness (exactly one). This is the one that decides routing, and it's the Module 9 idea made
concrete: an issue can go to a person *or* be handed to an agent.
- `ready:ai-ready`: small, well-scoped, reproducible; safe to hand to an issue-to-PR agent (the
  kind of agent Module 25 builds). Route `assignee_type: agent`.
- `ready:needs-human`: ambiguous, risky, or needs a product decision. Route `assignee_type: human`.

## Output format

Return one JSON object, nothing else:

```json
{
  "labels": ["type:bug", "priority:p2", "area:cli", "ready:ai-ready"],
  "assignee_type": "agent | human",
  "rationale": "one or two sentences justifying the labels and the route",
  "confidence": "high | medium | low"
}
```
