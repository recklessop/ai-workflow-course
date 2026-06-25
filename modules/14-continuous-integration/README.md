# Module 14: Continuous Integration

> **The AI writes code that looks right. CI checks whether it actually is: automatically, on every
> push, before anyone trusts it.** This module turns the tests you wrote in Module 13 into a gate
> that runs itself.

---

## Prerequisites

- **Module 2: Version Control.** Pushes, commits, and the diff habit are the substrate CI sits on.
- **Module 8: Remotes and Hosting.** CI runs *on the forge*, triggered by pushes. You need a repo
  pushed to a remote (any forge: GitHub, GitLab, a self-hosted Forgejo/Gitea, whatever you set up
  in Module 8) for there to be anything to trigger.
- **Module 13: Testing in the AI Era.** CI is mostly "run the tests, automatically." You need tests
  to run. If you skipped writing them, this module's lab ships a small suite so you're not blocked,
  but the real payoff is automating *your* tests.

You do **not** need Docker, secrets management, or your own runner yet; those are Modules 16, 17,
and 19. On a **SaaS forge** (GitHub, GitLab.com, Bitbucket, and the rest) this module uses the
forge's hosted runners, which require zero setup. **One honesty note for the self-host track:** a
self-hosted Forgejo/Gitea/GitLab CE has the CI *feature* but no hosted compute; nothing actually
runs until you attach a runner, and that's Module 19. The workflow you write here is correct either
way and will run the moment a runner is registered; to watch it go green *now*, use a SaaS forge's
hosted runners, then come back and own the compute end-to-end in Module 19.

---

## Learning objectives

By the end of this module you can:

1. Explain what CI actually is, automated checks bound to a trigger, and why "on every push" is the
   part that makes it valuable.
2. Write a forge-native CI workflow that checks out your code, installs its tools, and runs a linter
   and your test suite.
3. Read a CI run: find which step failed, read the log, and reproduce the failure locally.
4. Watch CI catch a breaking change *before* it reaches anyone who would trust the broken code.
5. Recognize that CI is the same concept on every forge, and port a pipeline from one to another.

---

## Key concepts

### What CI is, stripped down

Continuous Integration has a grand-sounding name and a mundane core: **a set of checks that run
automatically whenever you push code, on a clean machine you don't control.** That's it. The checks
are usually the same commands you'd run by hand (lint, build, test), and the magic is entirely in
the word *automatically*.

You already run checks. Before you commit, you (sometimes) run the tests, (sometimes) run the
linter, (sometimes) remember to. CI removes every "sometimes." It runs the checks the same way,
every time, on every push, whether you remember or not, whether you're tired or not, whether it's a
one-line fix you're *sure* about or not. The discipline you can't reliably enforce on yourself, a
machine enforces for free.

Three properties make CI more than a glorified shell script:

- **It's triggered, not invoked.** You don't run CI; pushing runs it. The check is bound to the
  event, so it can't be skipped by forgetting.
- **It runs on a clean machine.** The forge spins up a fresh, throwaway runner with nothing of yours
  on it: no half-installed dependency, no environment variable you set six months ago and forgot.
  If your code only works because of something special about your laptop, CI finds out immediately.
  ("Works on my machine" dies here. Module 16 takes the reproducibility idea further with
  containers.)
- **Its result is visible and shared.** A green check or a red X shows up on the commit and on the
  pull request (Module 10), where everyone (every human reviewer and, later, every agent) can see
  whether this code passed the gate.

### The pipeline: checkout → setup → checks

Almost every CI configuration, on every forge, is the same four moves:

1. **Check out the code** onto the runner. The runner starts empty; first you put your repo on it.
2. **Set up the environment**: install the language runtime, pin its version.
3. **Install the tools** the checks need: the test runner, the linter.
4. **Run the checks**: lint, then test. Any check that exits non-zero fails the whole run.

That last point is the load-bearing one. CI's entire enforcement mechanism is the **exit code**.
Every tool you'd run in a terminal returns 0 for success and non-zero for failure. `python3 -m
unittest` exits non-zero if a test fails. `ruff check` exits non-zero if it finds a lint problem. CI runs your
commands and watches those exit codes; one failure turns the run red. You're not learning a new
testing system; you're wiring the tools you already have to a trigger.

### What goes in a CI run for this audience

Three tiers of check, cheapest first, because a fast check that fails early saves you waiting on a
slow one:

- **Lint.** Static checks that don't run your code: style, unused imports, obvious mistakes. Fast,
  cheap, catches a surprising amount. We use a linter as the example here; the principle is
  tool-agnostic.
- **Build.** Does the code even assemble? For an interpreted language like our Python example
  there's no compile step, so "build" often collapses into "does it import without erroring." For
  compiled languages this is where a broken type or missing symbol gets caught.
- **Test.** The Module 13 suite. The expensive, high-value tier: it actually runs your code and
  checks behavior.

Order them cheap-to-expensive so the fast checks fail fast. There's no reason to spend two minutes
running the test suite if the linter would have rejected the push in three seconds.

### The worked example: a forge-native workflow

Here's a complete, real CI pipeline for the `tasks-app`. This is GitHub Actions YAML, the most
common dialect and our default example, but **read it as a concept, not a product.** Every forge
has the exact same pipeline in its own dialect; the GitLab version is in the lab folder, and it's
the same five moves.

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check out the code
        uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install tools
        run: pip install ruff
      - name: Lint
        run: ruff check .
      - name: Test
        run: python -m unittest
```

Reading it top to bottom: `on:` is the trigger (push and pull request). `runs-on:` picks the clean
machine. The `steps:` are the four moves: checkout, set up Python, install the tools, then the two
checks. `uses:` pulls in a pre-built action (someone else's reusable step); `run:` is just a shell
command. The linter runs first because it's cheap; the tests run last because they're the
expensive, decisive check. Only the linter needs a `pip install` here; the tests run on Python's
standard-library `unittest` runner from Module 13, so there's nothing to install for them.

This file lives *in the repo*, committed and versioned like everything else. That's deliberate:
your pipeline is code, it's reviewed as a diff in a PR (Module 10), and a teammate or an agent
inherits it automatically by cloning. The same logic as committing the AI's config in Module 5.
The automation around your work is itself a durable, shared artifact.

### Reading a failed run

When CI goes red, the skill is triage, and it's fast once you know the shape:

1. **Open the run.** The forge shows the job as a list of steps with a red X on the one that failed.
2. **The first red step is the cause.** Steps run in order and stop at the first failure; everything
   after it is skipped, not broken. Don't get distracted by the skipped steps.
3. **Read that step's log.** It's the same output the tool prints in your terminal: a failing
   `unittest` assertion, a `ruff` finding with a file and line number. CI didn't invent a new error
   format; it's showing you the command's own output.
4. **Reproduce it locally.** The same command from the failed step (`python3 -m unittest` or
   `ruff check .`) fails the same way on your own machine, because CI ran exactly that command. That
   reproducibility is the point: fix locally, confirm green locally, push again.

That loop (red on the forge, reproduce locally, fix, push) is the entire day-to-day of working
with CI. The clean-machine runner occasionally surfaces a failure you *can't* reproduce locally.
That's not CI being flaky; it's CI correctly catching that your machine has something the clean
one doesn't. (See "Where it breaks.")

---

## The AI angle

This is the module where CI stops being generic devops hygiene and becomes specifically about
AI-assisted work.

AI generates code that **looks right.** That's not a knock on the models; it's their defining
property. They produce fluent, plausible, well-formatted code that passes a human skim, because
"looks like correct code" is close to what they're optimizing for. The failure mode isn't garbage
that obviously won't run; it's the function that's 95% right with a flipped comparison, the refactor
that quietly drops an edge case, the "cleanup" that breaks one path you didn't think to re-check.
A human reviewer skimming a confident-looking diff is exactly the reviewer that misses these
(Module 10 is the whole skill of *not* missing them, and it's hard).

CI is the reviewer that doesn't skim. It runs the code. It doesn't care how clean the diff looks or
how confidently the commit message is worded; it executes the tests and reports the exit code. The
flipped comparison fails an assertion. The dropped edge case fails the test that covered it. The
plausibility that fools a human is invisible to a process that only checks behavior.

This compounds with everything else AI changes about your workflow:

- **AI raises your push rate.** You're making more changes, faster, more of them generated. Manual
  pre-push checking scales with discipline and doesn't survive volume. The automated gate scales
  for free; it doesn't get tired on the fortieth push of the day.
- **AI can fix what CI catches.** A red CI run is a precise, machine-readable problem statement: the
  exact command, the exact failing assertion, the exact line. That's ideal input for an agent. Paste
  the failed log into Claude Code (or your agent) and direct it to fix the failure. (Module 25
  automates this into agents that respond to a failing pipeline on their own. CI is the trigger that
  makes self-healing possible.)
- **CI is the gate that makes letting agents run safely possible at all.** Every later module that
  hands the AI more autonomy (issue-to-PR agents, unattended runs) relies on the fact that nothing
  the agent produces reaches anyone without passing CI first. The supervision is structural: it's
  this gate, not a human watching the agent type.

You don't add CI *despite* using AI. The faster and more confidently the AI writes plausible code,
the more you need a reviewer that checks behavior instead of believing the diff.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/14-continuous-integration/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 14"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** YAML (the CI config) plus the Python `tasks-app` and shell commands. You direct
the agent to place files, commit, and recover; you commit a starter workflow, watch it pass, then
break it on purpose and watch CI catch it.

**You'll need:**

- The `tasks-app` from Modules 1–2, **pushed to a forge** (Module 8). Any forge works.
- The starter files in this module's `lab/`:
  - `ci-starter.yml`: the workflow (GitHub Actions flavor).
  - `gitlab-ci-starter.yml`: the same pipeline for GitLab, if that's your forge.
  - `test_tasks.py`: a small test suite (use your Module 13 tests instead if you have them).
- Python 3.10+ locally, and your agent. Examples use **Claude Code**; sub your own agent anywhere.

### Part A: Run the checks locally first

Never push a workflow you haven't run by hand. CI just runs the same commands, so prove they work on
your machine first.

1. Direct your agent to set up the project, then run the checks yourself once. Tell Claude Code (sub
   your own agent): *"Copy the lab's `test_tasks.py` next to `tasks.py` in `~/ai-workflow-course/tasks-app`,
   then install `ruff` into this project."* The agent places the file and handles the install,
   including the PEP 668 fallback (a per-project venv) if the system Python refuses a global install.
   What it runs looks like:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   pip install ruff
   # if pip is refused with "externally-managed-environment" (PEP 668, common on recent
   # Debian/Ubuntu and Homebrew Python), the agent falls back to a per-project venv:
   #   python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   #   pip install ruff
   ```

   Then run both checks **yourself**, once. This is the one part you do by hand on purpose: feeling
   that CI is nothing more than these same two commands is what makes the rest of the module click.

   ```bash
   python3 -m unittest   # should report all tests passing
   ruff check .         # should report no issues (or fix what it flags)
   ```

   If both are clean locally, CI will be green. If not, fix it here; it's faster than waiting on a
   runner. (Only the linter needs installing. The stdlib `unittest` runner ships with Python.)

### Part B: Add the workflow and watch it pass

2. Direct the agent to put the workflow where your forge looks for it. Tell Claude Code which forge
   you're on and let it pick the path:
   - **GitHub / Forgejo / Gitea:** `lab/ci-starter.yml` goes to `.github/workflows/ci.yml` (Forgejo/Gitea
     also read `.forgejo/workflows/` or `.gitea/workflows/`; the agent checks which yours uses).
   - **GitLab:** `lab/gitlab-ci-starter.yml` goes to `.gitlab-ci.yml` at the repo root.

3. Direct the agent to commit and push it, then verify. Tell Claude Code: *"Stage the new workflow
   and `test_tasks.py`, commit with a message about adding CI, and push."* Let it decide what to
   stage and run the git for you. What it runs looks like:

   ```bash
   git add .github/workflows/ci.yml test_tasks.py    # path varies by forge; the agent picks it
   git commit -m "Add CI: lint and test on every push"
   git push
   ```

   Verify it committed the workflow and the test file (a `git show --stat HEAD` confirms what landed),
   not stray files.

4. Open your repo in the forge's web UI and find the run (usually an "Actions," "CI/CD," or
   "Pipelines" tab, and a status icon on the commit). Watch the steps execute and turn green.
   **That green check is the gate now standing guard on every future push.** (Self-host track: if
   the run sits queued with nothing picking it up, that's the no-hosted-runner situation from the
   prerequisites; the workflow is correct, it just has no compute until you attach a runner in
   Module 19. Run this part on a SaaS forge to see green right now.)

### Part C: Break it on purpose and watch CI catch it

This is the whole point. You're going to ship the kind of plausible-but-wrong change AI produces,
and watch CI stop it.

5. Introduce a breaking change with the agent. Ask Claude Code (sub your own) for something that
   *sounds* like a cleanup but changes behavior: *"Refactor `pending()` in tasks.py to be simpler."*
   If it stays correct, nudge it until the logic actually changes. The classic plausible break: have
   `pending()` return `self.tasks` (all tasks) instead of filtering out the done ones. It reads fine.
   It's wrong.

6. **Notice it still looks right.** Glance at the diff. The function is short, clean, plausible.
   This is exactly the trap from "The AI angle": nothing in the *appearance* warns you.

7. Direct the agent to commit and push the change it just made. Tell Claude Code: *"Commit this and
   push it."* What it runs looks like:

   ```bash
   git add tasks.py
   git commit -m "Simplify pending()"
   git push
   ```

   Then verify CI goes red.

8. Watch CI go red. Open the run, find the first failed step (`Test`), and read the log:
   `test_pending_excludes_completed_tasks` failed, with the assertion and the actual-vs-expected
   values. CI caught in seconds what a skim would have waved through.

9. Hand the failure to the agent and let it recover. Paste the red CI log (the failed `Test` step)
   into Claude Code and direct it: *"Reproduce this locally, then undo the bad change safely; it's
   already pushed."* Your job is to verify it makes the right call, not to type git. The check:
   because the commit is already on shared history, the team-safe undo is `git revert`, not
   `git restore` (Module 12). What the agent runs looks like:

   ```bash
   python3 -m unittest          # fails locally too: same command, same failure
   git revert --no-edit HEAD   # new commit that undoes "Simplify pending()" (Module 12)
   git push                    # CI re-runs on the fixed code and goes green again
   ```

   Verify CI goes green again, and that the agent chose revert (a new inverting commit) over a
   history-rewriting undo on a branch others may have pulled.

10. *(Optional, to feel the linter tier.)* Add an obviously unused import to `cli.py`
    (`import os` at the top, unused), then direct the agent to commit and push. Watch the **Lint**
    step fail *before* the tests even run: the cheap check failing fast. Have the agent remove it and
    push again.

You've now seen both halves: CI passing as a guardrail that stays out of your way, and CI failing as
the reviewer that caught a change you might have trusted.

---

## Where it breaks

The honest caveats, because a skeptical audience trusts the limits more than the pitch:

- **CI only catches what your checks check.** A green run means "the linter found nothing and the
  tests passed," not "the code is correct." If the AI broke behavior you have no test for, CI is
  cheerfully green while the bug ships. CI is exactly as good as your test suite (Module 13), and no
  better. The flipped-comparison bug above got caught *because a test covered it.*
- **Green CI is not "reviewed."** It checks behavior, not design, intent, security, or whether the
  feature is even the right one. It does not replace human review (Module 10) or the security gates
  in Module 15; it sits alongside them. Treating a green check as sign-off is how plausible-wrong
  code with no failing test sails straight through.
- **The clean machine is a feature that feels like a bug.** Sooner or later CI fails in a way you
  can't reproduce locally: a dependency you have installed but never declared, a file outside the
  repo your code quietly reads, a path that only exists on your machine. That's not flakiness; it's
  CI correctly catching that your code depends on something that isn't in the repo. Fix the
  dependency, don't blame the runner. (Module 16's containers make local and CI environments
  identical, which kills most of these.)
- **Slow CI gets ignored.** If the run takes fifteen minutes, people stop waiting for it and start
  merging around it, and the gate is worthless. Keep it fast: cheap checks first, and don't put
  things in CI that don't need to run on every push.
- **CI is not free compute, and it's not infinite.** Hosted runners have usage limits and queue
  times, and a workflow that triggers on every push to every branch can burn through them. (Module
  19 is where you understand and own that compute.)
- **A committed workflow runs code from the repo.** A pull request from an untrusted fork can
  propose changes to the workflow itself. Forges have settings for how CI handles fork PRs; the
  defaults are usually safe, but it's a real attack surface worth knowing exists (the supply-chain
  thread picks up in Modules 15 and 22).

---

## Check for understanding

**You're done when:**

- Your `tasks-app` has a committed CI workflow that runs a linter and your tests on every push, and
  you've watched it go green on the forge.
- You pushed a plausible-but-wrong change and watched CI catch it: found the failed step, read the
  log, reproduced the failure locally, and fixed it.
- You can explain, in your own words, why CI specifically matters for AI-generated code (it checks
  behavior, not appearance) and the one thing a green check does *not* tell you (that the code is
  correct; only that your checks passed).
- You can point at the same pipeline in two forge dialects and see it's the same five moves.

When pushing a change and *expecting* the gate to either bless it or stop it feels automatic, when
you'd be uneasy merging code that hadn't been through CI, you've got it. Module 15 adds the next
gates on the same pushes: scanning for vulnerable dependencies, leaked secrets, and the packages AI
hallucinates into existence.

---

## Verify-before-publish

CI YAML and the actions it references drift faster than the rest of this durable-core material.
Re-check at build time:

- [ ] **Action versions.** Confirm `actions/checkout` and `actions/setup-python` major versions in
      `ci-starter.yml` are current and not deprecated. Pinned majors (`@v7`, `@v6`) age.
- [ ] **Runner labels.** Confirm `ubuntu-latest` (and any GitLab `image:` tag) still resolves to a
      supported image; default runner OS versions roll forward.
- [ ] **Trigger and config syntax.** Verify the `on:` keys and overall workflow schema against the
      forge's current docs; Actions YAML keys do change.
- [ ] **Forge UI labels.** The tab names in the lab ("Actions," "CI/CD," "Pipelines") and the
      workflow file locations (`.github/workflows/`, `.gitlab-ci.yml`, `.forgejo/`, `.gitea/`) match
      what the current forge versions actually use.
- [ ] **Tool names.** The example linter (`ruff`) is current, installable, and still behaves as
      described, or swap in the equivalent the rest of the course uses. (The test runner is Python's
      standard-library `unittest`, which ships with Python; no install, nothing to drift.)
