# Capstone: The Full Loop

> **One feature, taken end to end, with every module doing its job in sequence.** This is the finale:
> not new material, but proof that the twenty-seven pieces you learned separately are actually one
> motion. By the end you'll have shipped a real change to `tasks-app`, from prompt to running
> container. The model did the typing. The *workflow* is what made that safe and repeatable, and the
> workflow is the part you built.

---

## This is a finale, not a module

There's nothing to learn here that the modules didn't already teach. The capstone exists to **wire it
together**. Every step below names the module it comes from, so you can see the dependency chain you
climbed now collapse into a single fluent pass. If a step feels unfamiliar, that's a pointer back to
the module to re-read, not new content to absorb.

You'll do it twice:

1. **The main loop.** You direct, the AI executes. You file the issue and make the calls; the AI does
   the git and the edits; you verify each result. The full pipeline, once.
2. **The stretch variant (optional).** The *same* feature run the Unit 5 way, with autonomous agents
   inside the pipeline, so you watch the workflow start to run itself.

---

## Prerequisites

All of it. Concretely, you need the `tasks-app` repo in the state the course left it:

- A Git repo (Module 2) with a committed AI instructions file at the root (Module 5), a remote on
  your forge (Module 8), and a protected `main` that requires a PR to merge (Module 11).
- `test_tasks.py` and a green test suite (Module 13).
- A CI workflow that lints and tests on every push and PR (Module 14), with a security-scan step
  wired in (Module 15), running on a runner you understand (Module 19).
- A `Dockerfile` and `.dockerignore` (Module 16), `serve.py` exposing `/health` and `/tasks`
  (Module 18), `.env`/`.env.example` for config (Module 17), and a `deploy.sh` that tags by commit
  SHA, injects env, health-checks, and rolls back (Module 18).

If any of those is missing, build it from its module first. The capstone assumes the machine is
already standing; it doesn't re-pour the foundation.

---

## The feature we're shipping

Pick something small enough to finish in one sitting and real enough to touch the whole stack. We'll
add **due dates**:

- A task can carry an optional due date: `python3 cli.py add "file taxes" --due <YYYY-MM-DD>`.
- A new `overdue` command lists pending tasks whose due date has already passed.
- The deployed service grows a matching `GET /overdue` endpoint, so the change is visible in the
  running container, not just the CLI.

This deliberately spans the core (`tasks.py`), the CLI (`cli.py`), and the deployable service
(`serve.py`): one feature, three surfaces, exactly the kind of change that used to mean three
copy-paste sessions and a prayer (Module 1). And it has a built-in trap for the review step: "is a
task due *today* overdue?" is the kind of off-by-one an AI will answer confidently and wrongly.

---

## The loop, step by step

Read this once as a map before you touch the keyboard. Each arrow is a module.

**Prompt → issue (M9).** Don't start in your editor. Start with the work written down. File an issue:
*"Add optional due dates to tasks, an `overdue` command, and a `/overdue` endpoint."* Acceptance
criteria in the body. Label it. The issue is the contract the rest of the loop closes against.

**Issue → branch (M6/M11).** Never work on `main`. Have the AI branch off main, named for the issue
(something like `47-due-dates`). The branch is a sandbox you can throw away wholesale (M6); that
disposability is what lets you turn the AI loose on three files at once without risking `main`.

**Branch → AI implementation (M4), config already in place (M5).** Now the AI edits the files
directly in your editor or CLI, with no browser and no paste. It already knows your conventions because the
committed instructions file has been in the repo since the first commit (M5): core logic in
`tasks.py`, CLI wiring in `cli.py`, standard library only, run the tests before claiming done. You
didn't re-explain any of that. That's the file earning its keep.

**Implementation → tests (M13).** The feature isn't done when it runs; it's done when it's *pinned*.
Have the AI extend `test_tasks.py` with cases for the new logic, and name the boundary cases
yourself, because the boundary is exactly where the AI guesses: due yesterday (overdue), due tomorrow
(not), **due today (not yet)**, no due date at all (never overdue, never crashes).

**Secrets stay clean (M17).** This feature needs no new secret; it reads the system clock. The
discipline is that nothing got hardcoded *anyway*: the service still reads its config from the
environment via `.env`, and `.env.example` documents any new keys. The win here is a non-event, and
that is the point. The failure mode (M17: AI hardcodes a value) simply didn't happen, because the
pattern was already there.

**Tests → PR (M10/M11).** Have the AI push the branch and open the PR, with `Closes #47` in the
description so the merge closes the issue automatically (M11). The PR is the review gate even though
it's your own code, and *especially* because an AI wrote most of it.

**PR → CI → security scan (M14/M15/M19).** Opening the PR triggers the pipeline on your runner (M19):
lint, build, tests (M14), then the security gate (M15): dependency audit, secret scan, SAST. The
feature added no dependencies, so SCA should be quiet, and the secret scan confirms you didn't smuggle
a key into a fixture. CI catches code that *looks* right (M14); the security scan catches the failure
classes a build check never would (M15).

**Review (M10).** Green CI is necessary, not sufficient. Read the diff like you didn't write it
(M10). Go straight for the plausibility trap: open `overdue()` and check the comparison. Did it use
`<` or `<=`? Does a task due today show up as overdue? Does a task with no due date crash the
comparison or get silently treated as overdue? This is the single least-automatable skill in the
course, and the capstone is where you prove you have it.

**Merge (M11).** Once CI is green and the diff is honest, squash-merge. Issue #47 closes itself. `main`
is now ahead by one clean, tested, scanned commit.

**Merge → containerized deploy (M16/M18).** The merge to `main` triggers delivery (M18): CI builds the
image from your `Dockerfile` (M16), tags it with the new commit SHA (immutable, not `latest`), runs
`deploy.sh` to start the container with env injected (M17), polls `/health`, and rolls back to the
previous SHA if health fails. Hit `GET /overdue` on the running container. The feature is live, in a
reproducible artifact, behind a health check that can undo itself.

**If it goes wrong (M12).** Something slips past every gate eventually. Because you squash-merged, the
bad change is one ordinary commit on `main`, so you direct the AI to revert it and verify the revert
lands as a clean new commit on shared history, without needing the `-m 1` flag (M12). A bad deploy is
already handled by `deploy.sh`'s rollback to the last good SHA. Recovery is a move you rehearsed.

That's the whole motion. Notice what carried it: not the model. **The model wrote the diff; the
workflow is everything that made the diff safe to merge and trivial to undo.** Swap the model next
quarter and every arrow above is unchanged. That's the Module 1 thesis (*the model is the cheap,
swappable part; the workflow is the durable skill*), and you just lived it instead of reading it.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** The capstone runs the whole loop on one feature.
> To begin from a clean app, copy the snapshot into a fresh `tasks-app` and make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/capstone/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: capstone"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell + Python, on the `tasks-app` repo. You'll direct Claude Code (`claude`; sub
your own agent) to do the git and the edits (M4); you make the calls and verify each result.

**You'll need:** the `tasks-app` repo in the prerequisite state above, Claude Code (or your own
agent), your forge account, and a working Docker install.

### Part A: Issue and branch (M9, M6, M11)

1. File the issue on your forge. Title: *"Task due dates + `overdue` command + `/overdue` endpoint."*
   In the body, write the acceptance criteria as you'd hand them to a contributor you don't trust to
   guess:

   - `add` takes an optional `--due YYYY-MM-DD`.
   - `overdue` lists pending tasks with a due date strictly before today.
   - A task due **today** is **not** overdue. A task with **no** due date is **never** overdue.
   - `serve.py` exposes `GET /overdue` returning the same set as the CLI.

2. Point Claude Code at the repo and tell it to sync `main` and cut the branch:

   > *"Sync `main` with the remote, then create a branch named `47-due-dates` for issue #47."* (Use
   > your real issue number.)

   Then verify it did what you asked:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   git status        # on 47-due-dates, clean, up to date with main
   git branch        # the new branch exists and is checked out
   ```

### Part B: Implement with the AI (M4, M5)

3. Give Claude Code the issue, not a vague wish:

   > *"Implement issue #47. Add an optional due date to tasks (core in `tasks.py`), wire `--due` into
   > the `add` command and a new `overdue` command in `cli.py`, and add a `GET /overdue` endpoint to
   > `serve.py`. Follow the acceptance criteria exactly. Run the tests before you tell me it's done."*

   You should *not* have to specify "stdlib only" or "don't touch `tasks.json`"; that's in the
   committed instructions file (M5). If the agent reaches for a date library or hand-edits the JSON,
   your file is missing a line, and that gap is the useful signal.

4. Run it yourself to confirm it's real. Choose the two dates relative to *your* today (one comfortably
   in the future, one safely in the past) so the assertion below holds whenever you run this:

   ```bash
   python3 cli.py add "file taxes" --due <a date a few months out>   # future → NOT overdue
   python3 cli.py add "renew domain" --due 2020-01-01                # past   → overdue
   python3 cli.py overdue        # should list "renew domain", not "file taxes"
   ```

   > *Verify-before-publish: refresh the example due dates so the "future" one is still in the future
   > at publish time; a hardcoded near-future date silently inverts this assertion once it passes.*

### Part C: Tests (M13)

5. Have the AI extend `test_tasks.py`, then **read the test names** and confirm the boundaries are
   actually covered. If "due today" and "no due date" aren't each their own test, tell the AI to add
   them by name. Confirm the suite is green:

   ```bash
   pytest        # or: python3 -m unittest
   ```

   Once it's green, tell the AI to commit the change. Then verify what it actually staged and wrote:

   ```bash
   git show --stat HEAD     # the right files, with a sensible message
   git status               # nothing stray left uncommitted
   ```

### Part D: PR, CI, security, review (M10, M11, M14, M15, M19)

6. Tell the AI to push the branch and open the PR, with `Closes #47` in the description. Then verify
   on the forge that the PR exists, targets `main`, and carries the closing keyword:

   ```bash
   git log --oneline origin/47-due-dates -1   # the branch is on the remote
   # then open the PR in the forge UI and confirm "Closes #47" is in the description
   ```

7. Watch the pipeline run on your runner (M19): lint + tests (M14), then the security scan (M15).
   Don't proceed until it's green.

8. **Review the diff as if a stranger wrote it** (M10). Open `overdue()` and answer, from the code:

   - Is the comparison strict (`<` today) or inclusive (`<=`)? A task due today must **not** appear.
   - What happens for a task with `due == None`? It must be skipped, not crash, not counted.

   If either is wrong (and an AI gets at least one of these wrong more often than you'd like), have the
   AI fix it on the branch, let CI re-run, and review again. Catching this *here*, before merge, is the
   entire point of the gate.

### Part E: Merge and deploy (M11, M16, M18, M17)

9. With CI green and the diff honest, squash-merge. Issue #47 closes itself.

10. Let delivery run, or run it locally if that's your setup (M18):

    ```bash
    ./deploy.sh           # builds image tagged by commit SHA, injects env, health-checks, can roll back
    curl localhost:8000/overdue
    ```

    You should see your overdue task served from the running container: the feature live in a
    reproducible artifact (M16), configured from the environment (M17), behind a self-rolling-back
    health check (M18).

### Part F: Rehearse recovery (M12)

11. **Have the AI sync local `main` first.** The squash-merge in step 9 happened on the forge, so the
    new commit lives only on the remote and your local `main` is one behind. Tell the AI to pull
    `main` and report the SHA of the squash commit you're about to rehearse undoing. Verify:

    ```bash
    git log --oneline -1     # the top line is your squash commit; note its SHA
    ```

12. Prove you can undo it, without typing the git yourself. Direct the AI:

    > *"Cut a throwaway branch off `main`, revert the squash commit `<sha>`, run the tests, then delete
    > the branch. The squash merge is a single-parent commit, so confirm a plain revert is correct and
    > that you do not need `-m 1`."*

    The `-m 1` check is the teaching point you carried from Module 12: that flag is only for the
    two-parent merge commits `git merge --no-ff` makes, and a squash merge isn't one. Have the AI say
    which it used and why. Then verify the rehearsal landed and left no mess:

    ```bash
    git branch       # throwaway-revert-test is gone; you're back on main
    git status       # clean
    ```

    You just confirmed the escape hatch is real before you need it.

---

## Stretch variant: run the same feature the Unit 5 way (optional)

The main loop kept you in the driver's seat, directing each step. Now run the **identical** feature
with autonomous agents *inside* the pipeline and watch how much of the loop keeps running when you
step back. Do this only after the main loop succeeded; you can't supervise a pipeline you haven't
driven yourself once.

The feature, the branch flow, the gates, and the deploy are unchanged. What changes is *who does each
step*:

1. **Issue-to-PR agent does the first pass (M25).** Assign the issue to an autonomous agent instead of
   driving the work step by step yourself. It reads issue #47, creates the branch, implements across
   `tasks.py`, `cli.py`, and `serve.py`, writes tests, and opens the PR, all landing as a reviewable
   PR behind CI, exactly like a human contributor's. It is allowed to *propose*, never to merge. The
   supervision is structural: the same CI (M14) and security (M15) gates stand whether the author is a
   human or an agent.

2. **An assistive reviewer comments first (M24).** Before you look, an AI reviewer reads the diff
   against your committed rubric and posts comments on the PR, flagging, ideally, the very `overdue()`
   boundary you hunted yourself. It comments; it does not approve and does not merge (M24). A human
   still decides. You read its comments, then read the diff yourself, and notice the reviewer caught
   the off-by-one, or notice it *missed* it, which is its own lesson about not trusting the assistant
   blindly.

3. **Evals tell you whether to trust any of it (M27).** Turn the boundary cases from Part C into an
   eval set (due yesterday, due today, due tomorrow, no due date) and score the agent's implementation
   against it. Now do the thing the whole course was building to: **swap the model** behind the agent
   and re-run the *same* eval. If the new model's `overdue()` regresses on the "due today" case, the
   eval catches it before the PR ever merges. That closes the thesis: evals are how you judge a model
   swap, so the swap you *will* make stays safe (M27).

When this runs, look at what's left for you: filing a crisp issue, reading a diff the assistant
already annotated, and reading an eval score. The agent drafted, the gates held, the eval judged. The
workflow didn't just make AI safe to use; it started running itself, with you supervising. That only
works because every catch-net from Units 2–3 was already in place. Take those away and "let an agent
open a PR" is reckless; with them, it's just another contributor (M11).

---

## Where it breaks

- **A finale is not a shortcut.** The loop is fluent *because* you climbed the modules. Running the
  capstone without the foundation (no protected `main`, no CI, no tests) isn't "the full loop," it's
  the copy-paste problem with extra steps. The pipeline's value is entirely in the gates; skip them
  and you've kept the ceremony and thrown away the safety.
- **Green CI is not correctness.** Every gate in this loop is a filter, not a guarantee. CI proves the
  tests pass; it can't prove the tests test the right thing. The `overdue()` boundary trap passes a
  weak test suite happily. The human review step (M10) is load-bearing and stays load-bearing; the
  automation raises the floor, it doesn't remove the ceiling.
- **The stretch variant moves the work, it doesn't delete it.** An issue-to-PR agent doesn't reduce
  the importance of a well-written issue; it *raises* it, because a vague issue now produces a vague
  PR with no human in the authoring loop to course-correct. The work shifts from typing toward
  specifying and judging. That shift is a good one, but it isn't free.
- **Evals are only as honest as their cases.** An eval set that omits the "due today" boundary will
  bless a broken model swap. The eval doesn't know what you forgot to test (M27); it can only scale
  the judgment you already bring to the cases you write.

---

## Check for understanding

**You're done when:**

- You shipped the due-dates feature from a filed issue to a running container, and `curl
  .../overdue` returns the right tasks from the deployed artifact.
- Issue #47 closed itself on merge, `main` is one clean commit ahead, and you caught (or consciously
  verified) the `overdue()` boundary in review rather than in production.
- You can point at each step and name the module it came from without looking, and explain why the
  *order* is the dependency chain, not an arbitrary checklist.
- You can state, from what you just did rather than from the syllabus, why the model is the swappable
  part: every step would survive replacing the model, and the stretch variant's eval is exactly how
  you'd prove a swap was safe.

If you ran the stretch variant, add one more: you watched an agent author the PR and an assistant
review it, and you can name precisely which catch-nets from earlier units made it reasonable to hand
that work to an agent at all.

That's the course. The model wrote the code. **You built the workflow that made the code matter**,
and that's the part that's still yours when the next model ships.
