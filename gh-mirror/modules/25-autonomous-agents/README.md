# Module 25. Autonomous Agents: Issue-to-PR and Self-Healing CI

> **Now the AI acts on its own: it takes an assigned issue, opens a pull request, even fixes its own
> failing build.** The thing that makes that safe isn't watching it work. It's that everything it
> produces still lands as a reviewable PR behind the same gates you already built.

---

## Prerequisites

This is the module the whole back half of the course was load-bearing for. It assumes a lot, on
purpose; each piece is a wall the autonomous agent has to land behind.

- **Module 5**: your committed AI instructions file: the agent's standing brief, the half of the
  spec that isn't in the issue.
- **Module 6**: branches. The agent's work goes on a branch, never straight onto `main`.
- **Module 9**: issues as an agent's task specification, including the `ready` label and the idea of
  an agent as an *assignee*. An issue is the agent's input here.
- **Modules 10 and 11**: the PR review gate and the full issue → branch → implementation → PR →
  review → merge → close loop. The PR *is* the unit of supervision in this module.
- **Module 12**: revert, reset, recovery. The backstop for when a gate misses something.
- **Modules 13 and 14**: tests and CI. The automated gate that runs on the agent's PR.
- **Module 15**: security scanning as another gate on the same pushes. Autonomy makes this
  non-optional, not optional.
- **Modules 16, 17, 22**: containers (sandboxing), secrets (scoped credentials), and the prompt-
  injection attack surface. An unattended agent with a push token is a security boundary; these are
  why.
- **Module 19**: runners. A triggered or scheduled agent is just a runner job; you need to know
  what's executing it and whose compute it's burning.
- **Module 24**: assistive agents, where the AI helped and *you* decided every step. This module is
  the escalation: the agent now takes a step on its own. The only reason that's responsible is the
  rest of this list.

If you skipped straight here, the lesson will read as reckless, because without those gates, it
*would* be.

---

## Learning objectives

By the end of this module you can:

1. Explain the difference between *assistive* (Module 24) and *autonomous-but-supervised* agents, and
   state where supervision actually happens in each.
2. Run an issue-to-PR agent: hand it a well-formed issue and have it produce a change on a branch
   that arrives as a reviewable pull request, not a merge.
3. Watch your existing CI / review / security gates catch a bad agent change before it can reach
   `main`, and explain why that's *structural* supervision rather than *behavioral*.
4. Build a bounded self-healing loop: when a gate fails, feed the failure back to the agent for a
   fix, capped at N attempts, with the result landing as a PR you review.
5. Decide how much autonomy to grant by reasoning about the strength of your gates, not the
   intelligence of your model.

---

## Key concepts

### The escalation: where supervision moved

In Module 24 the agent *advised*. It commented on a PR; it triaged and labeled an issue. A human
read the suggestion and took the action. Supervision was **behavioral**: you were in the loop on
every decision, watching, approving, clicking the button.

That doesn't scale, and watching an agent type is a terrible use of your attention anyway. This
module makes the agent *take the action*: branch, edit files, commit, open a PR. The obvious worry
is: if I'm not watching, what stops it from shipping garbage?

The answer is the reframe of the whole unit:

> **You don't supervise an autonomous agent by watching it work. You supervise it structurally, by
> making everything it produces pass through gates that don't care whether a human or a machine wrote
> the change.**

You already built those gates, for exactly this reason, before you needed them:

| Gate | Built in | What it catches on an agent's PR |
|------|----------|----------------------------------|
| **Review** | Module 10 | Plausible-but-wrong logic, scope creep, dropped edge cases. Read the diff, not the agent's summary. |
| **CI** | Module 14 | Lint failures, broken tests, anything that doesn't build. Runs identically on a human's PR and an agent's. |
| **Security** | Module 15 | Hardcoded secrets, vulnerable or hallucinated dependencies, SAST findings. |
| **Recovery** | Module 12 | The backstop: if something slips through and merges, `revert` cleanly undoes it. |

The agent is autonomous *inside* that box and powerless to escape it. It cannot merge past a failing
check or an unapproved review. That's the entire safety model, and it's why this module sits at the
end of the course instead of the start: the box had to exist first.

### Pattern 1: Issue-to-PR

The headline pattern, and the one Module 9 set up when it called an agent a possible *assignee*. The
loop is exactly the human collaboration loop from Module 11, with one participant swapped:

```
issue (assigned/labeled)  →  agent reads it  →  branch  →  implement  →  commit  →  open PR
                                                                                      │
                                                                  CI + security + human review
                                                                                      │
                                                                              merge → issue closed
```

What the agent reads as its brief is two artifacts you already maintain:

- **The issue** (Module 9): the *specific* task: title, context, acceptance criteria, scope. The
  acceptance criteria are the agent's literal definition of done.
- **The committed config** (Module 5): the *standing* brief: conventions, the build and test
  commands, "don't touch these files," house style. Every assignee inherits it, including this one.

Together they're enough for the agent to attempt the work with **no live conversation**. That's the
point of having spent modules making both artifacts good: a well-formed issue plus a committed config
is a complete, handoff-ready spec. Hand it a vague issue and you get the Module 9 failure mode at
full volume: a confident, plausible, wrong PR that costs more to review than the work would have
taken.

Crucially: the agent's last step is **open a PR**, not **merge**. The output is a proposal. Nothing
about "autonomous" means "merges to `main` unseen"; if that's your mental model, this is where you
fix it.

### Pattern 2: Self-healing CI

The second pattern points the agent at a *failure* instead of an issue. CI goes red on a branch; an
agent reads the failing job's logs, proposes a fix, and pushes it back to the same branch so CI runs
again.

```
push  →  CI fails  →  agent reads the failure  →  proposes a fix  →  push  →  CI re-runs
                            ▲                                                     │
                            └──────────── bounded retry (cap at N) ──────────────┘
                                                                                  │
                                                                       still red? hand to a human
                                                                       green? PR for review
```

Two design rules make this safe rather than a runaway loop:

1. **Bound the retries.** Two or three attempts, then stop and tag a human. An agent that can retry
   forever *will*, on a flaky test, producing an endless stream of plausible "fixes" and a runner
   bill to match.
2. **Watch what it's fixing.** The classic failure mode: the test fails, so the agent "fixes" it by
   *editing the test to pass* instead of fixing the bug. That's why the green result still lands as a
   **reviewable PR**: a human confirms it fixed the code, not the evidence. Self-healing CI proposes
   a fix; it doesn't certify one.

### Pattern 3: Triggered and scheduled agent jobs

How does an agent *start* without you launching it? It runs as a runner job (Module 19), the same
machinery that runs your CI, pointed at an agent instead of a test suite. Two triggers cover almost
everything:

- **Triggered**: an event fires the job: an issue gets a `ready`/`agent` label, a comment says
  `/agent fix this`, a CI run goes red. Event in, agent runs, PR out.
- **Scheduled**: a cron-style timer fires it: "every night, attempt the top `ready`-labelled issue,"
  or "hourly, retry any red `main` build." This is where "the workflow starts running itself" stops
  being a slogan.

Either way it's a job on a runner, which means everything Module 19 taught applies: hosted vs.
self-hosted, whose compute, and, new and important here, **what credentials that job holds.** A
scheduled agent with a push token and write access is unattended automation acting in your name. It
needs scoped secrets (Module 17), ideally a sandboxed environment (Module 16), and a healthy
suspicion of anything it reads, because an issue body or a dependency's README is untrusted input
that lands straight in its context (prompt injection, Module 22). Triggered autonomy is a real attack
surface; treat it like one.

### The one number that actually governs autonomy

Here's the load-bearing idea of the module, and it's not about the model:

> **An autonomous agent is exactly as safe as the gates it lands behind; no safer.** How much
> autonomy you can responsibly grant is a property of *your CI, review, and security setup*, not of
> how smart the model is.

If your test suite covers 30% of behavior, an autonomous agent can silently break the other 70% and
still go green. If your only "review" is rubber-stamping the diff, the review gate isn't real and the
agent is effectively merging unseen. The work of making agents trustworthy is mostly the unglamorous
work of making your gates strong, which is the work of Modules 10, 13, 14, and 15. Autonomy doesn't
ask you to trust the model more. It asks you to trust your gates more, and to have earned it.

---

## The AI angle

Scripting a runner job is ordinary automation. What's specific to AI here is that **the actor inside
the job is non-deterministic and persuasive**, and that changes what "automation" has to mean:

- **The output is a proposal, not a result.** A normal scheduled job (back up the database, rotate
  logs) you trust to *complete*. An agent job you trust only to *propose*, because its output is a
  confident artifact that might be subtly wrong. That's why the universal endpoint is a PR behind a
  gate, never a merge. The structure absorbs the non-determinism.
- **Supervision shifts from the action to the gate.** With deterministic automation you review the
  *script* once. With an agent you can't, because it writes something new every run, so you review
  the *output* every run, automatically (CI, security) and by sample (human review). The supervision
  didn't disappear; it moved from watching the agent to hardening the wall it hits.
- **Self-healing tempts the worst shortcut in the toolkit.** Pointed at a failing test, an agent will
  delete or weaken the test, because that does technically make CI green. A human would feel the
  dishonesty; the agent just optimizes the objective you gave it. The defense is structural: the fix
  is a reviewable diff, and the reviewer's job (Module 10) explicitly includes reading the `-` lines
  on the *test* file.
- **Autonomy multiplies your earlier discipline, for good or ill.** A clean repo with strong gates
  and a good committed config lets an agent contribute real work on a timer. A repo with flaky tests,
  no security scanning, and an empty config lets the same agent generate mess on a timer. The agent
  doesn't fix your engineering; it amplifies it.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** This lab is self-contained and does not depend
> on the earlier labs. Its files live in `modules/25-autonomous-agents/lab/`. Copy them into a working folder
> and make a first commit so you start clean:
>
> ```bash
> cp -r ~/ai-workflow-course/modules/25-autonomous-agents/lab ~/ai-workflow-course/25-autonomous-agents-lab
> cd ~/ai-workflow-course/25-autonomous-agents-lab && git init -b main && git add -A && git commit -m "start: module 25"
> ```
**Lab language:** Python (one orchestrator script) plus a little shell and Git. It runs on your own
machine, any OS, against the `tasks-app` repo from Module 1, with no forge account or paid agent
required to complete it.

You'll drive an issue-to-PR run and a self-healing loop *locally*, so the moving parts are visible
and reproducible. The "PR" in the local lab is a branch plus a diff you review; the optional Part D
shows how the exact same flow runs on a real forge as a triggered/scheduled job.

**You'll need:**

- Your `tasks-app` Git repo (Modules 1–2), with the `test_tasks.py` from Module 14 present and
  `pytest` and `ruff` installed (`pip install pytest ruff`). The lab runs these as the CI gate,
  locally, the same checks `ci.yml` runs in Module 14.
- The starter files in this module's `lab/` folder:
  - `agent_runner.py`: the orchestrator. Drives the agent (real or simulated), then runs the gate,
    and only ever produces a branch + PR proposal, never a merge.
  - `issue-delete-command.md`: a well-formed issue (Module 9 format) for a `delete <index>` command:
    the agent's input.
  - `agent-job.yml`: a reference forge workflow showing the triggered + scheduled runner version.
    Read it; you'll run it for real only in Part D.
- *Optional, for the "for real" path:* an agentic coding tool that has a non-interactive / headless /
  one-shot mode (most expose a flag for running a single prompt without the interactive UI). If you
  don't have one wired up, the script's `--simulate` mode demonstrates every gate and loop
  deterministically with no agent at all; do that first regardless.

> **What `--simulate` actually does (read this before Part A).** To stay deterministic and never
> touch your real `cli.py` / `tasks.py`, `--simulate` does **not** implement
> `issue-delete-command.md`. Instead it writes a small, self-contained stand-in (`agent_demo.py` with
> a `discount()` function, plus its test) and runs the *real* gate (ruff + pytest) against that. So
> Parts A–C exercise the machinery and the gates, not the delete feature itself. The issue is only
> actually implemented in **Part D**, with a live agent. When you review the simulated diff you'll see
> the `discount()` demo, not a `delete` command; that's expected, and it's why the simulation is
> reproducible enough to teach with.

### Part A: See the gate catch a bad change (simulated, no agent needed)

Copy `agent_runner.py` and `issue-delete-command.md` into your `tasks-app` folder, along with this
module's `lab/.gitignore` (append its lines to the `.gitignore` you already have from Module 2 rather
than overwriting it). Direct your agent (Claude Code as the worked example; sub your own) to commit
that updated `.gitignore`, then verify with `git log`. It keeps the lab scaffolding and Python caches
out of the agent's `git add -A`, so the change you review in Part B is clean. Then, from
`~/ai-workflow-course/tasks-app`, run the orchestrator:

```bash
# Simulate an agent that produces a BROKEN change, then run the gate on it:
python3 agent_runner.py issue-to-pr issue-delete-command.md --simulate bad
```

The orchestrator creates and switches to its own `agent/issue-delete-command` branch first (the same
`git switch -c` the runner does in `agent-job.yml`), so you direct the automation and verify the
branch with `git branch` rather than typing `git checkout`. Then watch the output: the "agent" plants
a change, the script runs the gate (`ruff check` then `pytest -q`), a test fails, and the script
**stops and refuses to call the work ready**, exit code non-zero, no PR proposed. That is structural
supervision. It didn't matter that the change looked plausible; the gate caught it, and nothing
reached `main`.

### Part B: See a good change land as a PR proposal

```bash
python3 agent_runner.py issue-to-pr issue-delete-command.md --simulate good
```

This time the planted change is correct. The gate passes, the script commits to the branch and prints
the diff plus the push / open-PR command it would run. **It does not merge.** Review the diff with the
Module 10 checklist, then direct your agent (Claude Code; sub your own) to run that push and open the
PR, and verify the PR appeared. Remember (from the note above) that the simulated diff is the
self-contained `discount()` stand-in, not a `delete` command. The review *motion* is the real lesson:
you are the human gate, and that step doesn't go away just because an agent did the typing. The agent
stops at a PR; it never merges.

### Part C: Run the self-healing loop

```bash
python3 agent_runner.py self-heal --simulate bad
```

The orchestrator switches to its own `agent/self-heal` branch (again, you direct the automation, not
your fingers), then plants a failing change, runs the gate (red), feeds the failure back to the "agent" for a
fix, re-runs the gate, and repeats up to its retry cap. With `--simulate bad` the fix succeeds on the
second attempt and the result is offered as a PR proposal. Run it with `--simulate stuck` to watch the
cap trip: after N attempts it gives up and tags the work for a human instead of looping forever.

### Part D: Do it for real (optional)

Two ways to go from simulation to a genuine autonomous run:

1. **Local, real agent.** Point the script at your agentic tool by setting one environment variable to
   its headless invocation, then drop `--simulate`:

   ```bash
   export AGENT_CMD='your-agent-cli --print --prompt-file {prompt_file}'   # your tool's one-shot mode
   python3 agent_runner.py issue-to-pr issue-delete-command.md
   ```

   The script builds the prompt from the issue **and** your committed config (Module 5), runs your
   agent against `tasks-app`, then applies the *same* gate. A real agent, your real gate, a real PR
   proposal.

2. **On a forge, triggered/scheduled.** Read `agent-job.yml`. It's a runner workflow (Module 19) that
   fires when an issue gets an `agent` label *and* on a nightly schedule, runs the agent on the
   runner, and opens a PR, which then hits your normal CI (Module 14) and security (Module 15) gates
   and waits for review. Wiring it up needs a scoped token in your forge's secrets (Module 17); the
   file is commented with exactly what to set and what *not* to grant. This is the "workflow runs
   itself" endpoint, and it's intentionally the last thing you turn on.

---

## Where it breaks

The honest limits, and for autonomous agents the limits *are* the lesson:

- **Your gates are the ceiling, and most gates are weaker than they look.** Thin test coverage,
  skipped security scans, or review-by-rubber-stamp don't just reduce quality, they directly set how
  much an autonomous agent can quietly break. Don't grant more autonomy than your gates can verify.
  The honest version of "should I let an agent do this unattended?" is "would my CI catch it if it got
  it wrong?"
- **Self-healing can fix the evidence instead of the bug.** Editing the test until it passes, widening
  an exception so the error is swallowed, deleting an assertion: all turn CI green and all are wrong.
  The bounded-retry cap stops the *loop*; only human review of the diff stops the *cheat*. Never let a
  self-heal PR auto-merge on green alone.
- **"Autonomous" is not "auto-merge."** Everything in this module stops at a PR. The moment you wire
  an agent to merge its own work to `main` without a gate that a human controls, you've left supervised
  autonomy and you own whatever it ships. That's a deliberate decision, not a default, and it's out
  of scope for this course.
- **Unattended agents are an attack surface, not just a convenience.** A scheduled agent holds
  credentials and reads untrusted input (issue bodies, comments, dependency files) straight into its
  context. Prompt injection (Module 22) means a malicious issue can try to redirect it; an over-broad
  token (Module 17) means success is expensive. Scope the credentials, sandbox the run (Module 16),
  and assume everything it reads is hostile.
- **Runaway cost and churn are real.** An agent in a retry loop, or a scheduled job that re-attempts
  the same impossible issue every night, burns runner minutes and review attention. Cap retries, cap
  concurrency, and put a human checkpoint on anything that hasn't converged.
- **Flaky gates make autonomy actively worse.** A nondeterministic test that fails 1-in-5 will send a
  self-healing agent chasing a bug that isn't there. Autonomy demands *more* gate discipline than
  manual work, not less. Fix the flake before you point an agent at it.

---

## Check for understanding

**You're done when:**

- You ran an issue-to-PR flow (simulated or real) and the result was a **branch + PR proposal**, not a
  merge, and you can point to exactly where a human or a gate still has to say yes.
- You watched the gate **reject a bad agent change** (`--simulate bad`) and accept a good one, and you
  can explain why that's structural supervision rather than watching the agent work.
- You ran a self-healing loop, saw it propose a fix on failure, and saw the retry **cap trip**
  (`--simulate stuck`) instead of looping forever.
- You can finish this sentence without hand-waving: *"I'd let an agent do X unattended because my
  gates would catch it if it got X wrong, specifically the gate from Module ___."*
- You can name the three patterns (issue-to-PR, self-healing CI, triggered/scheduled jobs) and the
  four gates that make any of them safe (review M10, CI M14, security M15, recovery M12).

When "let the agent take the first pass" feels safe because you trust the wall it lands behind, not
because you trust the model. You've got the model right. Module 26 takes the next step: more than one
agent working at once without colliding, which is where the worktrees from Module 7 finally pay off at
scale.

---

## Verify-before-publish

This is an expansion-zone module sitting on fast-moving ground. Re-check at build time:

- [ ] **Native issue-to-PR / "coding agent" offerings.** Forges and vendors are shipping built-in
  assign-an-issue-to-an-agent and PR-fixing features fast, and renaming them faster. Confirm whether a
  mainstream forge now offers this natively, and keep the lab's mechanism-agnostic framing if it's
  still in flux. Don't name a specific product as *the* answer.
- [ ] **Agentic-tool headless invocation.** The `AGENT_CMD` example assumes a non-interactive / one-
  shot flag. Verify the major agentic CLIs still expose one and that the flag names in the example
  read as plausible placeholders, not as one vendor's exact syntax.
- [ ] **Self-healing CI integrations.** Marketplace actions and bots that auto-fix red builds appear
  and disappear. Re-verify any referenced capability still exists and is still described neutrally.
- [ ] **Triggered/scheduled workflow syntax.** The event names and `schedule`/cron syntax in
  `agent-job.yml` are stable on the GitHub Actions flavor used in Module 14, but re-confirm the
  trigger events (issue-labeled, comment command) match current forge behavior, and that the GitLab /
  Forgejo equivalents in the comments are still accurate.
