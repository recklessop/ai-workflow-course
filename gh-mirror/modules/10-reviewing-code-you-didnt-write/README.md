# Module 10: Reviewing Code You Didn't Write

> **The AI wrote a diff that reads beautifully and is wrong in one line you'll skim right past.**
> Reviewing for *plausibility traps*, not just bugs, is a skill almost nobody teaches. This module
> gives you a gate to run it at and a checklist to run.

---

## Prerequisites

- **Module 2: Version Control as a Safety Net.** You read changes with `git diff`. This module
  turns that one-off habit into a disciplined review pass over a whole change.
- **Module 8: Remotes and Hosting.** Your repo lives on a host now, and a change arrives as a
  *pull request* (GitHub/Gitea/Forgejo) or *merge request* (GitLab): same thing, different name.
  We'll write "PR" throughout; it's the unit of review.
- **Module 9: Issues and the Task Layer** (helpful, not required). A PR usually answers an issue;
  the issue is the "what I asked for" you review the diff against.

If you only have Modules 1–2, you can still do the core skill of this module locally (reviewing a
diff between two branches with `git diff`) and skip the part where you open it as a PR on a host.

---

## Learning objectives

By the end of this module you can:

1. Use a pull request as a **review gate**: nothing reaches the main branch without passing through
   a diff someone (or something) signed off on, even on a solo repo.
2. Read an AI-generated diff the right way: against the request, deletions first, the diff over the
   AI's own description of it.
3. Name and spot the four **plausibility traps** (invented APIs, silent scope creep, deleted
   edge-case handling, convincing-but-wrong logic) that pass a human skim and a quick run.
4. Run a repeatable **AI-diff review checklist** and end every review with an explicit
   *approve* / *request changes* decision you can defend.

---

## Key concepts

### The gate, not the formality

A pull request proposes merging a branch into another (usually `main`) and pauses there so the
change can be looked at *before* it lands. On a team that pause is where review happens. The trap
is treating it as a rubber stamp ("looks good, merge"), which is exactly how bad changes get the
institutional blessing of "it was reviewed."

Reframe it the way you already think about change control: **a PR is a change gate, and merge is a
one-way door.** Once it's on `main`, it's in everyone's next clone, in CI, on its way to a deploy.
The cheapest place to catch a problem is in the diff, before the door closes. You can recover after
(that's Module 12), but recovery is always more expensive than the review you skipped.

This holds **even when you're the only human on the repo.** That's not bureaucracy for its own
sake. The syllabus's own course repo opens a PR for every module for exactly two reasons that
apply to you solo:

- **Traceability.** The PR is a durable record of *what changed and why*, linked to the issue it
  answers. `git log` tells you the change happened; the PR tells you the reasoning, the discussion,
  and what was rejected.
- **A forced read.** Opening the PR makes you look at the *whole* change as one diff, away from the
  editor you wrote it in. That context switch is where you catch the thing you were too close to
  see while generating it.

When the author is an AI, both reasons get sharper. The AI produced the change with total
confidence and no memory of why; the PR is where a human supplies the judgment and the record the
AI can't.

### Why this is a new skill

You already know how to review human code. Reviewing AI code is *not the same activity*, and
assuming it is gets people burned.

When a human writes a function, the bugs cluster where the human was uncertain: the gnarly edge,
the bit they rushed, the TODO they meant to come back to. You can often *feel* the soft spots, and
the code's roughness is a signal: confusing code is suspicious code.

AI output inverts that signal. It is **uniformly fluent.** The variable names are good, the
structure is clean, the comment above the broken line confidently states the correct intention,
and the one wrong line looks exactly as polished as the forty right ones. The fluency is constant;
the correctness is not, and your eye has spent a career using fluency as a proxy for correctness.
That proxy is now actively misleading.

So the question shifts. With human code you mostly ask *"is this good code?"* With AI code you have
to ask *"is this code true?"*: does it do what it claims, against the request I actually made,
using things that actually exist. That's reviewing for **plausibility traps**: code engineered (by
a process optimizing for plausible-looking output) to pass exactly the skim you're tempted to give
it.

### The four plausibility traps

These are the failure modes to hunt for specifically. They're not random bugs; they're the
characteristic ways fluent-but-untrue code goes wrong.

**1. Invented APIs.** The model reaches for a function, method, keyword argument, flag, config key,
or endpoint that *should* exist by analogy, and doesn't, or exists with a different signature.
It's the same generative move behind hallucinated package names (the supply-chain version of this
gets its own treatment in Module 15). The tell is that it reads *more* natural than the real API,
because it was generated to be plausible rather than recalled from docs. Classic shape: assuming
`list.pop(i, default)` works because `dict.pop(k, default)` does. Verify every unfamiliar
symbol against real docs or source. Confidence in the surrounding words is not evidence.

**2. Silent scope creep.** You asked for one thing; the diff does that thing *and* quietly
"improves" three others it was never asked to touch: reformatting a file, reshuffling imports,
renaming a variable across the module, "simplifying" an unrelated function. Each extra edit is an
unrequested change you now have to review with no stated intent behind it, and it's where
regressions hide. The discipline: **every hunk must trace back to the request.** Anything that
doesn't is guilty until proven innocent, and the right move is often "take it out and do it in its
own PR."

**3. Deleted edge-case handling.** The most dangerous trap, because it lives in the `-` lines you
skim. While implementing the feature, the model drops a bounds check, removes a `None` guard,
collapses a `try/except` into the happy path, or, worst, *replaces a real error with a silent
swallow* (`except: pass`) under the banner of "making it robust." The code now looks cleaner and
passes every test you'd casually run, because you'd test the path that works. The bad input that
the deleted guard existed to catch now fails silently. **Read every deletion. Deletions are where
behavior disappears.**

**4. Convincing-but-wrong logic.** An inverted condition (`if not x` where it meant `if x`), an
off-by-one, `<` where it meant `<=`, `and` where it meant `or`, a filter quietly dropped from a
comprehension. On the happy path it often produces a believable-enough result, and the comment
above it cheerfully describes the *correct* behavior, so the comment actively vouches for the bug.
The defense is to **trace one real call through the changed code yourself** instead of trusting the
narration.

A real AI diff usually has *most lines correct* and one trap buried in legitimate work, which is
what makes it dangerous. The feature really does work when you try it; the trap is somewhere you
didn't look.

### How to actually read the diff

You want the change as one reviewable unit, separate from the editor you generated it in. On your
host's PR page that's the default view: the whole change as a diff, with line comments,
file-by-file navigation, and CI results attached. The same change reads as a block of `+`/`-`
lines, for example a hunk that quietly drops a guard:

```diff
 def charge(amount):
-    if amount <= 0:
-        raise ValueError("amount must be positive")
     gateway.charge(amount)
```

That block is the unit of review, whether you read it in the browser or have the agent pull it up
in the terminal. You already know the git for this from Module 2, and from Module 4 on the agent
fetches the branch and surfaces the diff for you. Your job is the reading, and reading the `-`
lines first: the deleted guard above is exactly the kind of thing a skim sails past.

Run the pass in this order (the full version is in
[`lab/ai-diff-review-checklist.md`](lab/ai-diff-review-checklist.md), keep it open while you work):

1. **State the request in one sentence.** This is your scope yardstick. If it answers an issue
   (Module 9), that's your sentence.
2. **Read the diff, not the AI's summary.** The summary tells you what it *intended*; the diff is
   what it *did*. Only the diff is real.
3. **Scope check.** Every hunk maps to the request. Flag everything that doesn't.
4. **Deletions first.** Read every `-` line and ask what behavior just left the codebase.
5. **Verify the unfamiliar.** Every API, flag, and key you don't personally know exists:
   check it.
6. **Trace one real call**, including a failure case. Not the happy path, the bad input.
7. **Decide.** Approve only if you can explain every hunk. Otherwise request changes. The burden of
   proof is on the diff, not on you.

That last point is the whole posture: **a diff is guilty until proven correct.** "It runs" is the
weakest evidence there is; the traps above are *designed* to run.

---

## The AI angle

Every other module here makes a tool more valuable because of AI. This module is the one where the
*human stays in the loop on purpose*, and it's worth being precise about why.

The thing AI is best at, producing fluent, confident, well-structured output, is precisely the
thing that defeats the review reflex you built reviewing humans. You learned to trust clean code
and distrust messy code; AI produces uniformly clean code regardless of whether it's correct, so
that heuristic now points the wrong way. Reviewing AI diffs means consciously *overriding* an
instinct that served you well for years.

And the volume cuts against you. AI makes generating a 300-line PR almost free, which shifts the
bottleneck from *writing* to *reviewing* and tempts everyone to review at the speed they generate.
Review is now the gate that writing no longer is. The fluent-but-wrong line costs nothing to
produce and everything to miss.

This is the human half of a loop you'll keep building. Module 11 wires this review gate into the
full issue → branch → PR → review → merge motion with humans *and* agents as contributors. Much
later, Module 24 looks at AI *reviewers* that comment on PRs automatically, but an automated
reviewer is an assistant to this skill, not a replacement for it. You can't supervise a review bot
you couldn't do yourself.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/10-reviewing-code-you-didnt-write/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 10"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell + the Python `tasks-app`. You won't write Python; you'll open a PR for a
real change, then review a diff the "AI" produced and catch the trap planted in it.

**You'll need:**

- Git, Python 3.10+, and your coding agent (Claude Code in the examples; sub your own).
- The starter base app in [`lab/tasks-app/`](lab/tasks-app/) (`tasks.py`, `cli.py`). It's the
  Module 1/2 app with one addition: `complete()` validates the index and `done` turns a bad index
  into a clean error. Note that behavior; the trap will mess with it.
- The planted AI change in [`lab/ai-change.patch`](lab/ai-change.patch).
- The review checklist in [`lab/ai-diff-review-checklist.md`](lab/ai-diff-review-checklist.md).
- **Optional (Part A as a real PR):** the repo you pushed to a host in Module 8. If you don't have
  one, do Part A locally as a branch; the review skill in Parts B–C is identical either way.

### Part A: Open a PR as a gate

1. Have your agent set up the base app as a throwaway `review-lab` repo, then confirm the baseline
   behavior yourself. This `review-lab` is *separate* from the `tasks-app` you've built up across
   earlier modules; you can delete it when you're done, and nothing here touches your main app. From
   Module 4 on the agent drives the git and setup, so direct Claude Code (sub your own agent) to
   scaffold it:

   > *"Make a new directory `~/ai-workflow-course/review-lab` and copy the two Python files from
   > `~/ai-workflow-course/the-workflow-course/modules/10-reviewing-code-you-didnt-write/lab/tasks-app/`
   > into it. Add a `.gitignore` that ignores `tasks.json` and `__pycache__/` so runtime state stays
   > out of the diffs. Initialize a git repo on a branch named `main`, stage everything, and make one
   > commit: `base: tasks-app`."*

   The branch name is load-bearing: the steps below diff against `main` and switch back to it, so
   verify the agent actually used `main` (not whatever its default is). Confirm the result:

   ```bash
   cd ~/ai-workflow-course/review-lab
   git log --oneline        # one commit, "base: tasks-app", on branch main
   git status               # clean tree; tasks.json ignored, not tracked
   ```

   Then see the baseline behavior with your own eyes, because the trap is going to change it:

   ```bash
   python3 cli.py add "write the review module"
   python3 cli.py done 99        # baseline: prints "error: no task at index 99", exits non-zero
   echo "exit code: $?"
   ```

   Remember that last result. A bad index is a clean, loud error today.

2. Now practice the gate on a trivial, honest change. Tell the agent to make a one-line tweak on
   its own branch and put it up for review:

   > *"On a new branch `tweak-empty-message`, change the empty-list message in `tasks.py` from
   > '(no tasks yet)' to '(nothing to do)'. Commit it as 'Friendlier empty-list message'. If this
   > repo has a remote, push the branch and open a pull request; otherwise leave it on the branch."*

   Your job is the review, not the plumbing. Read the resulting diff before it lands: on the PR page
   if the agent opened one, or with `git diff main..tweak-empty-message` if you're local-only. It's
   one line, and that's the point. Make reading-before-merging a reflex on a trivial change so it's
   automatic on a dangerous one. Once you've read it and it's exactly what you asked for, tell the
   agent to merge it into `main`.

### Part B: Review the AI's diff (the real exercise)

3. Now a teammate-who-is-an-AI has opened a PR. The prompt it was given was exactly:
   **"Add a `delete <index>` command to the tasks app."** The change is captured as a patch in the
   lab so the review is reproducible. Have the agent stage it as that teammate's PR, on its own
   branch:

   > *"From `main`, create a branch `ai-delete-command`. Apply the patch at
   > `~/ai-workflow-course/the-workflow-course/modules/10-reviewing-code-you-didnt-write/lab/ai-change.patch`
   > to the working tree, then commit it as 'Add delete command'. Don't review or 'fix' it; just
   > land it on the branch so I can review it."*

   `git apply` is how the lab injects the incoming change so you can read it before deciding whether
   to keep it, exactly what you'd do in a real PR review. Telling the agent not to clean it up
   matters: left to its own judgment it might "helpfully" repair the planted problem before you
   ever see it.

4. **Review it before you run it.** Open the checklist and read the diff as one unit:

   ```bash
   git diff main..ai-delete-command
   ```

   Work the checklist. The request was *one sentence*: add a `delete` command. Hold every hunk up
   to it. Read the `-` lines. Find the line that does something the request never asked for and
   that changes behavior you tested in Part A. Write down what you think the trap is *before*
   step 5.

### Part C: Confirm the trap by running the failure case

5. Now verify your read by running the *failure* path, not the happy one:

   ```bash
   python3 cli.py add "a real task"
   python3 cli.py delete 0        # the requested feature: works fine on the happy path
   python3 cli.py add "another"
   python3 cli.py done 99         # the trap: compare this to your Part A baseline
   echo "exit code: $?"
   python3 cli.py list            # did task 99 (which doesn't exist) get marked done? did anything?
   ```

   In the base app, `done 99` was a clean error with a non-zero exit. After this "add a delete
   command" change, it prints `updated` and exits `0`, silently claiming success while marking
   nothing. The diff *only said* it was adding `delete`. While in the file it also rewrote
   `complete()` to swallow the `IndexError` "for robustness," deleting the edge-case handling and
   turning a loud failure into a silent lie. That's three traps in one small hunk: **scope creep**
   (it touched `complete`, which the request never mentioned), **deleted edge-case handling**, and
   **convincing-but-wrong logic** wearing a reassuring comment.

6. Play it out. On your host's PR you'd leave a line comment on the `complete()` hunk
   (*"out of scope, and this swallows the error `done` relied on; please drop it"*) and **request
   changes** rather than approve. The feature you were asked for was fine; the PR still doesn't
   merge. That's the gate doing its job.

---

## Where it breaks

- **A checklist is a floor, not a ceiling.** It catches the characteristic traps reliably; it will
  not catch a deep logic error that requires understanding the whole system. For changes in code
  you don't know, reviewing the diff in isolation isn't enough; that harder case (pointing AI at
  an unfamiliar codebase, and reviewing safely there) is Module 23.
- **Tests catch what review misses, and vice versa.** This module is human review; it pairs with
  automated testing and CI (Modules 13–14), which catch the regressions a tired reviewer skims
  past. Neither replaces the other: the trap in this lab passes a casual run *and* would pass a
  test suite that only tests the happy path. Review is what notices the test you *should* have.
- **Review fatigue is real and AI makes it worse.** Twenty fluent PRs in a day will wear down the
  exact attention this skill needs, and a rubber-stamped review is worse than none because it
  launders the change as "reviewed." Smaller PRs are the mitigation: insist the AI's changes stay
  small and single-purpose so each one is reviewable in full. A PR too big to review honestly
  should be sent back to be split, not skimmed.
- **You can't review what you don't understand.** If a diff uses an API or a corner of the language
  you don't know, "looks fine" is not a review; that's the moment to verify it exists and does
  what it claims, or to pull in someone who knows. The honest output of a review is sometimes
  "I'm not qualified to approve this," and that's a valid result.

---

## Check for understanding

**You're done when:**

- You've opened (or branched) a change and reviewed it as a diff *before* merging, so the gate is a
  reflex even on a one-liner.
- You found the planted trap in `ai-change.patch` by reading the diff against the one-sentence
  request, and named *why* it's a trap (it changed `complete()`, which the request never mentioned,
  and swallowed the error `done` depended on).
- You confirmed it by running the **failure** case (`done 99`) and seeing the silent `updated` +
  exit `0`, instead of trusting the happy path (`delete 0`) that worked fine.
- You can name the four plausibility traps from memory (invented APIs, silent scope creep, deleted
  edge-case handling, convincing-but-wrong logic) and you treat a diff as guilty until proven
  correct.

When "it runs" stops feeling like sufficient evidence and "I read every `-` line" starts feeling
mandatory, you've got the skill. Module 11 takes this gate and wires it into the full collaboration
loop (issues, branches, PRs, and merges) with both humans and agents as contributors.
