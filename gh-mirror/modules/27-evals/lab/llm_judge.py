"""LLM-as-judge: the pattern, and its limits, in one file.

Some agent output can't be graded by `==`. "Is this commit message clear?" or
"Does this PR description actually explain the change?" has no exact answer. The
common move is to ask *another* model to grade it. This file shows the shape of
that grader and is deliberately honest about what it can't do.

It is vendor-agnostic by design. Point it at whatever model endpoint you already
use by setting two environment variables; if they're not set, it abstains rather
than pretending. NOTHING here pins a provider.

    EVAL_JUDGE_URL    # an OpenAI-style /chat/completions-compatible endpoint, or your own
    EVAL_JUDGE_KEY    # the bearer token for it
    EVAL_JUDGE_MODEL  # the model name to ask for

Run it standalone to grade one sample:
    python3 llm_judge.py "Add count command" "fix"
"""

import json
import os
import sys
import urllib.request

RUBRIC = """You are grading one piece of agent output against a rubric.
Score 1 if the commit message clearly and specifically describes the change.
Score 0 if it is vague, generic, or could describe almost any change.
Reply with ONLY a JSON object: {"score": 0 or 1, "reason": "<one short sentence>"}
"""


def judge(candidate_text: str) -> dict:
    url = os.environ.get("EVAL_JUDGE_URL")
    key = os.environ.get("EVAL_JUDGE_KEY")
    model = os.environ.get("EVAL_JUDGE_MODEL")
    if not (url and key and model):
        return {"score": None, "reason": "judge not configured; abstaining (set EVAL_JUDGE_* to enable)"}

    payload = json.dumps({
        "model": model,
        "temperature": 0,  # determinism matters for a grader; you want repeatable scores
        "messages": [
            {"role": "system", "content": RUBRIC},
            {"role": "user", "content": f"Output to grade:\n{candidate_text}"},
        ],
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read())
    content = body["choices"][0]["message"]["content"]
    return json.loads(content)


if __name__ == "__main__":
    sample = sys.argv[1] if len(sys.argv) > 1 else "fix stuff"
    print(judge(sample))

# ---------------------------------------------------------------------------
# READ THIS BEFORE TRUSTING A SCORE FROM HERE.
#
# An LLM judge is a model grading a model. Its failure modes are real:
#   - Correlated blind spots: the judge can share the candidate's confusion, so
#     a wrong answer gets a passing grade because both models are wrong the same way.
#   - Bias: judges favor longer, more confident, or first-presented answers
#     regardless of correctness. Hold position and length constant when you can.
#   - Drift: change the judge model and your scores move even though nothing
#     about the candidate changed. The ruler is itself made of rubber.
#
# So: use a programmatic grader (run_eval.py) wherever a deterministic check is
# possible; that is most of the time. Reach for an LLM judge only for genuinely
# open-ended output, and CALIBRATE it first: hand-label ~20 examples yourself,
# run the judge on them, and confirm it agrees with you before you let it gate
# anything. An uncalibrated judge is a vibe with a number attached.
# ---------------------------------------------------------------------------
