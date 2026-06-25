# Module 27. Evals: Trusting an Agent That Acts Without You

> **You will swap the model. Evals are the only thing that tells you whether the swap was safe.**
> This is the instrument that turns "the agent's output looks fine" into a number you can gate on,
> and it's where the whole course's thesis finally pays out.

---

## Prerequisites

This is the closer. It assumes the whole course, but it leans hardest on:

- **Module 1**: the thesis (the model is the cheap, swappable part; the workflow is the durable
  skill) and the `tasks-app` we've carried the whole way. This module is where the thesis gets its
  proof.
- **Module 10, Reviewing Code You Didn't Write**: the human review skill evals partially automate
  and partially *replace* once a human isn't in the loop.
- **Module 13, Testing in the AI Era**: you can write a deterministic pass/fail check. Evals are
  the next thing up the ladder: scoring output that a single test can't fully pin down.
- **Module 14, Continuous Integration**: running checks automatically on every change, with an
  exit code that gates. Evals run the same way and gate the same way.
- **Modules 24–26, the Unit 5 agent ladder**: assistive agents (24), autonomous-but-supervised
  agents (25), and orchestrated fleets (26). Evals are what decide how far up that ladder any given
  agent is allowed to climb.

---

## Learning objectives

By the end of this module you can:

1. State precisely what an eval is and how it differs from a test, and when you need one instead of
   the other.
2. Build a small eval set for a concrete agent task: representative cases plus a grader that turns
   output into a score.
3. Score agent output programmatically, and use an LLM-as-judge where you must, honestly, knowing
   its failure modes.
4. Run a **regression eval** across a model or prompt change and read whether the change was safe.
5. Set a **guardrail**: tie an autonomy level to an eval score so an agent earns the right to act
   unattended instead of being granted it on faith.

---

## Key concepts

### The question Unit 5 has been building toward

Unit 5 walked the agent from your elbow into the pipeline: assisting you (Module 24), then acting
under supervision (Module 25), then several of them at once (Module 26). Each step removed a human
from a loop. So the question this module exists to answer is blunt:

> **An agent did work while you were asleep. How do you *know* it did good work?**

"I read the diff" doesn't scale: the whole point of an unattended agent is that you weren't there.
"CI passed" is necessary but thin. CI proves the code builds and your existing tests are green, not
that the agent actually did the *right thing*, well, on the cases that matter. You need a way to
measure agent output **systematically**, the same way every time, on a fixed set of cases, with a
score you can compare across runs. That measurement is an **eval**.

### What an eval actually is

An eval has exactly three parts. None of them are exotic:

1. **An eval set**: a fixed list of representative cases. Inputs the agent will face, chosen to
   cover the normal path *and* the edges where it tends to fail.
2. **A grader**: something that turns each case's output into a result. Pass/fail, or a score. The
   grader can be code (`==`, a regex, "does it compile, run, and produce this output") or, when the
   output is open-ended, another model (LLM-as-judge).
3. **An aggregate + a threshold**: roll the per-case results into one number, and a line that number
   has to clear. "18/20 = 90%, and I require 90%."

That's it. An eval is a test suite pointed at *agent behavior* instead of a function, with a score
instead of a single green check, run against a moving target (the model) instead of frozen code.

### Eval vs. test: the distinction that matters

This audience already writes tests (Module 13). The instinct to ask "isn't an eval just a test?" is
correct enough to be dangerous. Where they diverge:

| | A test (Module 13) | An eval |
|---|---|---|
| **Subject** | Your code, frozen | An agent/model's output, which changes under you |
| **Result** | Binary: pass/fail | A score across many cases (90%, not "green") |
| **Determinism** | Same input → same output | Same input may give *different* output run to run |
| **Failure meaning** | The code is broken | The agent is *less good*, maybe still acceptable |
| **What it gates** | "Is the code correct?" | "Is this model/prompt good enough to trust here?" |

The practical upshot: a single failing case doesn't condemn an agent the way a failing unit test
condemns code. You're measuring a *rate*. An agent that gets 19/20 right may be exactly what you
want unattended on low-stakes work and nowhere near enough for high-stakes work. The eval gives you
the rate; *you* set the bar per task.

And the inverse: **where a deterministic test is possible, write the test, not an eval.** Evals are
for the band of behavior tests can't pin down: open-ended output, judgment calls, "did it pick a
reasonable approach." Reaching for an LLM judge to grade something `==` could have caught is how you
get a slower, flakier, more expensive test that you trust less. (The lab's grader is deliberately
programmatic for exactly this reason.)

### Building the eval set

The eval set is the asset. The grader is plumbing; the *cases* are where the judgment lives, and a
good set is mostly edges. Three sources fill it fast:

- **The normal path**: a couple of cases proving the agent does the obvious thing. These rarely
  catch anything; they're the floor.
- **The edges you already know break**: every "it looked right but" bug your agents have shipped is
  a permanent case. Module 13 left us a perfect one: an agent implemented `pending_count()` as
  `len(self.tasks)`. It passes any quick manual check (add three tasks, count says three) and is
  wrong the instant a task is marked done. *That bug becomes case #4 in this module's lab and never
  escapes again.*
- **The cases you'd manually check anyway**: write down the inputs you reflexively try when
  reviewing this kind of change. That list *is* your eval set; you've just been running it in your
  head and forgetting the results.

Keep it small and sharp. Twenty discriminating cases beat two hundred that all test the happy path.
A case that every candidate passes tells you nothing; the cases that *separate* a good agent from a
bad one are the whole value. And the eval set is code-adjacent data: commit it, review changes to it
in PRs (Module 10), and grow it every time an agent surprises you. It is durable in exactly the way
the syllabus means: it outlives every model it ever judges.

### Scoring: programmatic first, LLM-as-judge only when you must

Two graders, in strict priority order.

**Programmatic.** If "correct" is checkable in code (exact value, output matches, exit code is 0,
the file it shouldn't have touched is untouched), do that. It's deterministic, free, fast, and you
trust it completely. Most of what an agent does to a codebase is checkable this way, because code
either runs and produces the right thing or it doesn't.

**LLM-as-judge.** Some output has no `==`: "is this commit message clear?", "does this PR
description explain the change?", "is this refactor actually cleaner?" The standard move is to ask
*another* model to grade it against a rubric. It works, and sometimes it's the only option, but be
honest about what you've built:

- **Correlated blind spots.** A judge is a model grading a model. It can share the candidate's
  confusion and pass a wrong answer because both are wrong the same way. Your grader and the thing
  it grades are not independent.
- **Bias.** Judges favor longer, more confident, and first-presented answers regardless of
  correctness. Control for position and length or your scores measure verbosity.
- **Drift.** Swap the judge model and your scores move while the candidate didn't change. The ruler
  is made of rubber, which is poison for *regression* evals, whose entire job is to hold the ruler
  still.

So when you must use a judge: pin it (fixed model, `temperature: 0`), keep it **separate** from the
model under test, and **calibrate it against human labels**: hand-grade ~20 examples, run the judge
on the same 20, and confirm it agrees with you *before* you let it gate anything. An uncalibrated
judge is a vibe with a number attached. The lab ships a model-agnostic judge stub (`llm_judge.py`)
that abstains until you point it at your own endpoint, with these limits written into the file.

### Regression evals: the safety check on a swap

Here is where the course thesis stops being a slogan and becomes a procedure.

You *will* swap the model. A cheaper one ships, your provider deprecates the one you're on, a new
release benchmarks better, someone edits the agent's prompt or its committed instructions file
(Module 5). Every one of those changes the behavior of every agent you run, silently. The code
around the model didn't change; the model did, and the model is the part you don't control.

A **regression eval** is the discipline of running the *same eval set* before and after the change
and comparing the scores. The current model/prompt earns a baseline score. After the change (a new
model, a new prompt), the same eval set runs again and the two scores get compared. A score that
held or rose means the swap is safe by this eval; a score that dropped is a regression caught
*before* it ran unattended against real work, not after.

This is the answer to "the model is swappable." It's swappable **because** the eval set is what
makes swapping safe. Your prompts, your pipeline, your review reflexes, and, most of all, your
eval set don't expire when the model does. They're the durable skill the course promised in Module
1. The model is a component you can replace; the eval is the regression test that tells you the
replacement fits. That's the whole argument, made operational.

### Guardrails: tying autonomy to a score

The last piece, and the real subject of Unit 5: **how much is this agent allowed to do without a
human?** Don't answer that by gut. Answer it with the eval score, and make the score *gate* the
autonomy.

| Eval score on this task | Reasonable autonomy (the Unit 5 ladder) |
|---|---|
| Low / unmeasured | Assistive only; it suggests, a human decides (Module 24). |
| Solid, below your bar | Autonomous but fully gated; opens a PR, a human reviews and merges (Module 25). |
| At/above bar, stable across runs | Unattended on this *narrow* task, landing behind CI + the eval as a gate. |
| High across a broad set, held over time | Orchestrate it; let it run in a fleet (Module 26). |

Two things make a guardrail bite:

- **The threshold blocks.** The eval returns an exit code; below-bar exits non-zero and stops the
  pipeline exactly like a failing test (Module 14). The lab does this. An eval whose result nobody is
  forced to act on is a dashboard, not a guardrail.
- **Autonomy is per-task, not per-agent.** The same model can be trustworthy enough to merge
  doc fixes unattended and nowhere near enough to touch auth code. You hold a *different* eval and a
  *different* bar for each. "Trust the agent" is the wrong granularity; "trust this agent, on this
  task, to this score" is the right one.

---

## The AI angle

Every other module made a tool more valuable *because* you're using AI. This module closes the
argument the course opened with.

Module 1 claimed the model is the cheap, swappable part and the workflow is the durable skill. Every
module since has been an installment on that claim: version control, review, CI, containers,
secrets, MCP, agents. **Evals are where it's proven.** An eval set is, literally, a model-agnostic
instrument: it judges output without caring which model produced it, which is exactly why it survives
the swap that retires the model. You don't trust an agent because you trust the vendor or this
quarter's benchmark; you trust it because *your* eval, on *your* cases, scored it above *your* bar,
and you'll re-run that same eval the day the model changes under you, which it will.

That's the durable skill. Models are weather. The eval set is the thermometer you keep.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** This lab is self-contained and does not depend
> on the earlier labs. Its files live in `modules/27-evals/lab/`. Copy them into a working folder
> and make a first commit so you start clean:
>
> ```bash
> cp -r ~/ai-workflow-course/modules/27-evals/lab ~/ai-workflow-course/27-evals-lab
> cd ~/ai-workflow-course/27-evals-lab && git init -b main && git add -A && git commit -m "start: module 27"
> ```
**Lab language:** Python + shell. You'll run a tiny eval harness, point an agent at a task, and run
a regression eval across a "model swap."

The lab files are in [`lab/`](lab/):

- `eval_set.py`: five cases for the `pending_count` task (data only).
- `run_eval.py` is the runner; it imports a candidate, scores it, prints a scorecard, exits non-zero
  below threshold.
- `candidates/current_model/tasks.py`: a correct candidate (stand-in for your current model's
  output).
- `candidates/swapped_model/tasks.py`: a plausible-but-wrong candidate (stand-in for a bad swap).
- `llm_judge.py`: a model-agnostic LLM-as-judge stub, with its limits written in.

**You'll need:** Python 3.10+, the `tasks-app` you've carried since Module 1, and Claude Code (sub
your own agent). No API key or paid model is required to complete the lab; the bundled candidates let
the regression demo run offline. The real payoff comes when you replace them with your own agent's
output.

### Part A: Run the eval against the current model

1. From the lab folder, run the eval against the passing candidate:

   ```bash
   cd modules/27-evals/lab
   python3 run_eval.py candidates/current_model
   echo "exit code: $?"
   ```

   Five cases pass, the score is 100%, and the exit code is `0`. **This is your baseline**: the
   score the current model earns on this task. Read the cases in `eval_set.py`: notice case #4,
   "completed tasks are NOT pending." That's the Module 13 bug, now a permanent case.

### Part B: Swap the model and re-run (the whole point)

2. Now simulate the swap: run the *exact same eval set* against the other candidate:

   ```bash
   python3 run_eval.py candidates/swapped_model
   echo "exit code: $?"
   ```

   It drops to 60% and exits `1`. Look at *which* cases failed: the easy ones still pass; this
   output would sail through a casual manual check. The eval caught a regression that a skim would
   have missed, **and the non-zero exit code means a pipeline would have blocked it.** That is a
   guardrail doing its job.

### Part C: Make it real with your own agent

3. Open your `tasks-app` and tell Claude Code (sub your own agent) to implement (or re-implement)
   `pending_count()` and write its version straight into `candidates/my_run_1/tasks.py`, creating the
   folder if it doesn't exist. You direct; the agent does the file plumbing. Then run the eval
   yourself and read the scorecard:

   ```bash
   python3 run_eval.py candidates/my_run_1
   ```

4. Now actually swap something. Either change the model Claude Code uses, or change the *prompt* (ask
   the same thing a different way, or tweak your committed instructions file from Module 5). Have the
   agent write this run into `candidates/my_run_2/`, then run `run_eval.py` yourself and compare the
   two scores. You just ran a regression eval on a real model/prompt change and got a number that
   tells you whether the change was safe. If a run scores below 100%, read the failing case and direct
   the agent to append the input that broke it as a new permanent case in `eval_set.py`; verify the
   case it added. The set gets sharper every time an agent surprises you.

5. *(Optional, needs a model endpoint.)* Open `llm_judge.py`, read the limits at the bottom, set the
   `EVAL_JUDGE_*` environment variables to your own endpoint, and grade an open-ended output, say a
   commit message your agent wrote. Note how much shakier that score feels than the programmatic one.
   That feeling is correct, and it's why programmatic graders come first.

### Part D: Set the guardrail (on paper, then in CI)

6. Decide the autonomy for this task using the ladder in Key concepts. Write one sentence:
   *"`pending_count` changes may merge unattended only when `run_eval.py` scores 100%; otherwise a
   human reviews."* Then make it enforceable. This is one job in a CI workflow (Module 14), so direct
   Claude Code (sub your own agent) to add an eval-gate job to the workflow it already wired up in
   Module 14, running the same command from Parts A–B. The job it adds should look like this:

   ```yaml
   - name: Eval gate
     working-directory: modules/27-evals/lab
     run: python run_eval.py candidates/current_model --threshold 1.0
   ```

   Review the diff before you accept it, and confirm the path logic is right. The
   `working-directory:` line makes the CI job `cd` into the lab folder first, so the
   `candidates/...` path and `run_eval.py`'s own `from eval_set import CASES` resolve exactly as they
   did on your machine. (Drop it and point a repo-root job straight at
   `python3 modules/27-evals/lab/run_eval.py candidates/current_model`, and `candidates/`
   won't exist from the repo root: the gate crashes with a *false* failure, which is worse than no
   gate. If the agent prefers a single line, it can spell both paths out from the repo root:
   `python3 modules/27-evals/lab/run_eval.py modules/27-evals/lab/candidates/current_model
   --threshold 1.0`.)

   Below threshold exits non-zero and the pipeline blocks, exactly like a failing test. The guardrail
   is now structural, not a promise.

   **One honest caveat, or this gate guards nothing.** `candidates/current_model` is the bundled,
   always-correct stand-in: it scores 100% on every run, forever, so a gate pointed at it can never
   fail. That's a dashboard, not a guardrail: the exact trap this section warns about. In a real
   pipeline, point the gate at the candidate that actually *varies*: your agent's real output for
   this task (the `candidates/my_run_2` you made in Part C, or wherever your pipeline writes the
   model's output before merge). Prove the gate bites by aiming it at `candidates/swapped_model`: the
   same command drops to 60%, exits `1`, and blocks the merge.

---

## Where it breaks

The honesty this course has insisted on all the way through applies hardest to its own closer.

- **Evals measure what you put in them, and nothing else.** A 100% score means the agent passed
  *your cases*, not that it's correct in general. The gap between "passes my eval" and "is actually
  good" is exactly the cases you didn't think to write. An eval set is a lower bound on quality, never
  a proof. Treat a green eval as "no known regression," not "verified correct."
- **Eval sets rot.** Cases that no model ever fails stop discriminating; tasks drift away from what
  you actually do. An eval set you don't prune and grow becomes a comforting green light that's
  measuring last year's problems. Budget maintenance for it like any other test suite.
- **LLM-as-judge is a model grading a model.** Re-read that section: correlated blind spots, bias,
  and drift are not edge cases, they're the default behavior. An uncalibrated judge can hand you a
  confident wrong score, which is worse than no score. Where you can grade in code, do.
- **A score is not a decision.** The eval tells you the rate; *you* still set the bar, and the right
  bar depends on stakes the eval can't see. 95% might be plenty for triaging issue labels and
  reckless for anything touching auth, money, or customer data. The number informs the judgment; it
  doesn't replace it.
- **Evals don't catch novel harms, only measured ones.** A genuinely new failure mode (a class of
  mistake no case anticipates) passes every eval until the day it doesn't and you add the case after
  the fact. Evals make agents *trustworthy on known territory*. They are not a substitute for the
  recovery muscles (Module 12) that exist for when something gets through anyway.

---

## Check for understanding

**You're done when:**

- You can explain the difference between a test and an eval, and say when you'd reach for each.
- You've run `run_eval.py` against both bundled candidates and watched the same eval set pass one and
  fail the other, including the exit code flipping to `1`.
- You've graded your *own* agent's output, then changed the model or prompt and re-run the same eval
  set as a regression check, and you can read the before/after scores as "safe" or "not safe."
- You can state, for one concrete task, the eval score that would let an agent act unattended on it,
  and where that threshold would live in your pipeline.
- You can say, in your own words, why the eval set is the durable skill and the model is the swappable
  part. That's the whole course in one sentence, and you can now run it from the keyboard.

That's the close. You started by copy-pasting out of a chat window; you're ending by letting an agent
act without you and holding a measured, enforceable line on whether to trust it. The model under that
line will change many times. The line is yours to keep.

---

## Verify-before-publish

This is an expansion-zone module over fast-moving ground. Re-check at build/publish time:

- [ ] **No vendor pinned.** Confirm the module text, lab, and `llm_judge.py` still name no specific LLM
  provider, model id, or pricing, and that `llm_judge.py`'s endpoint config is still generic
  (env-var driven, OpenAI-style-compatible but not branded).
- [ ] **Eval frameworks named.** If the module names any eval framework or LLM-as-judge tool by
  name (it currently names none on purpose), verify it still exists and behaves as described. Prefer
  keeping it tool-agnostic.
- [ ] **LLM-as-judge claims.** The bias/drift/correlation caveats are durable, but re-check that no
  cited best practice (e.g., calibration-against-human-labels guidance) has been superseded.
- [ ] **Module cross-references.** Confirm Modules 13, 14, 10, and 24–26 still carry the
  responsibilities referenced here (tests, CI gating, review, the agent autonomy ladder) and that
  none were renumbered.
- [ ] **Lab still runs.** `python3 run_eval.py candidates/current_model` exits 0 at 100%, and
  `candidates/swapped_model` exits 1 below threshold, on a current Python 3.x.
