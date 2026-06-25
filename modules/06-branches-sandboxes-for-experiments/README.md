# Module 6: Branches as Sandboxes for Experiments

> **A branch is a disposable copy of your project where the AI can try anything, and `main` never
> finds out unless you decide it should.** This is what turns "let the agent attempt something bold"
> from a gamble into a one-line decision: keep it or throw it away.

---

## Prerequisites

- **Module 2: Version Control as a Safety Net.** You can `init`, `commit`, read `git diff`/`git
  log`/`git status`, and `git restore` an unwanted change. Branches build directly on commits: a
  branch is just a label on the commit history you already understand.
- **Module 3: Version Control for Words.** You first met `git branch`, `git switch -c`, `git merge`,
  and `git branch -d` there, on a markdown doc, where a mistake costs nothing and the merge always
  fast-forwarded. This module takes those same verbs to *code*, where branches actually diverge and
  merges can conflict.
- **Module 4: Getting the AI Out of the Browser.** The AI now edits your real files directly from
  your editor. That's exactly the capability that makes branches matter; you're about to let it edit
  files *fast and confidently*, and you want a wall around the blast radius.
- **Module 5: Commit the AI's Config, Not Just the Code.** Your committed instructions file travels
  with the branch automatically, so an agent working on a branch inherits the same setup. (You'll see
  this for free in the lab; nothing to do, just notice it.)

Module 2's `git restore` undoes *uncommitted* changes back to your last checkpoint. This module is
the next size up: isolating *a whole line of committed work* so you can keep or discard it as a unit.

---

## Learning objectives

By the end of this module you can:

1. Explain what a branch actually *is* (a movable pointer, not a copy of your files) and direct your
   AI agent to create and switch between branches, verifying the result with `git branch`/`git status`.
2. Let the AI make a bold, multi-commit change on a branch while `main` stays untouched and runnable.
3. Decide the experiment's fate and have the agent carry it out: **merge** it into `main` to keep it,
   or **delete the branch** to throw it away with zero trace. You make the call and check the result.
4. Recognize a merge conflict (the `<<<<<<<`/`=======`/`>>>>>>>` markers) when you see one, and
   verify the AI's resolution even when the agent resolved it silently and you never saw a marker.
5. Tell the difference between a fast-forward merge and a merge commit, and know which one you got.

---

## Key concepts

### What a branch actually is (quick recap)

You already drove the branch loop by hand in Module 3 (create, merge, delete) on a markdown doc,
where the merge always fast-forwarded because nothing else had moved. You won't re-learn those
commands here. From Module 4 on, the AI runs them for you; this module is about how the AI works
*inside* a branch and how you decide what to keep. So just one line of recap before we get there.

A branch is **a named, movable pointer to a commit.** Your commit history is a chain of snapshots
(Module 2); a branch is a sticky label that points at one of them and moves forward every time you
commit on it. `main` is the branch Git made for you in Module 2; every commit moved that label
forward. You were "on a branch" the whole time.

The property that makes branches the right tool here: **creating one copies nothing.** No second
folder, no duplicated files, no disk cost worth mentioning. Git writes a new label pointing at the
commit you're already on. That's why branches are cheap enough to be disposable, and disposable is
exactly what we want for an AI experiment you might throw away.

### The reframe: a branch is a sandbox you can blow away

You already have the instinct for this. A branch is the Git equivalent of a **scratch VM you can
snapshot and roll back, a staging environment nobody depends on, a feature-flag you can rip out.**
You spin one up precisely *because* you're about to do something you might regret, and you want a
clean way to make it never have happened.

In Module 2 the safety net was "commit, then `restore` if the AI makes a mess." That's perfect for a
single bad edit. But some experiments are bigger than one edit: "rewrite the storage layer," "try a
totally different CLI structure," "add a feature that touches four files." Those take several commits
to even evaluate, and you don't want that half-finished, possibly-broken work sitting on `main`. A
branch gives the whole experiment its own track:

```
main:         A───B───C                  (always runnable; this is your "known good")
                       \
experiment:             D───E───F         (the AI's bold attempt, however messy)
```

While you're on `experiment`, `main` is frozen at C: runnable, shippable, untouched. The AI can leave
`experiment` a broken mess at F and `main` doesn't care. When you're done you make one decision:

- **Keep it:** merge `experiment` into `main` (C gains D, E, F).
- **Kill it:** delete `experiment`. D, E, F evaporate. `main` is still exactly C, as if the
  experiment never happened.

That "kill it, no trace" path is the one this module exists for. It's the difference between "I have
to carefully undo everything the AI did" and "I delete the branch."

### Switching branches changes your files

One detail trips people up the first time. When you switch to another branch, **Git rewrites the
files in your folder to match that branch.** Switch to `experiment` and the AI's half-built feature
appears in your editor. Switch back to `main` and it's gone; your files are back to commit C. Same
folder, different contents, instantly.

This is why you can't switch with uncommitted changes lying around that would be clobbered. Git stops
you, because switching would silently throw work away. The fix is the Module 2 habit: commit (or
stash) before you switch. On a branch, "commit often" pays off again, since each commit is a safe
point to switch away from. When the agent is driving, this is one of the things you verify after it
works: `git status` clean before a switch.

> **One folder, one branch at a time.** Switching swaps the *whole* folder between branches, so you
> can only have one branch checked out at once. The moment you want *two* branches live at the same
> time (say, two agents working in parallel without overwriting each other's files) you've hit the
> limit of branches alone. That's what **Module 7 (Worktrees)** solves: multiple working directories
> from one repo. Branches are the concept; worktrees are how you run several at once.

### Merging: keeping the experiment

Merging takes the commits from one branch and brings them into another. The receiving branch (usually
`main`) is the one you switch to, and the other branch merges into it. You don't type this; you tell
the agent "merge `experiment` into `main`," and it runs the equivalent of `git merge experiment`.

There are two outcomes, and it's worth recognizing which you got when you read the log:

- **Fast-forward.** If `main` hasn't moved since you branched (still at C), Git slides the `main`
  label forward to F. The history stays a straight line. This is the common case for a solo
  experiment.
- **Merge commit.** If `main` *did* move on (you committed to `main` while `experiment` was off doing
  its thing), the two lines of history diverged. Git stitches them together with a new commit that
  has two parents.

Git picks between these based on whether the branches diverged. You recognize them in the log: a
fast-forward is a straight line, a merge commit is a visible fork-and-join.

```console
$ git log --oneline --graph
*   9f3c1a2 Merge branch 'experiment'
|\
| * 4b8d0e1 Add task priorities (experiment)
* | 2a1f9c7 Fix list ordering on main
|/
* 7c0e3d4 Initial tasks app
```

After a successful merge the branch has done its job, and `git branch -d experiment` deletes it. The
lowercase `-d` refuses if the branch isn't fully merged, which is a safety check. Again, the agent
runs this once you've decided; you confirm the branch is gone with `git branch`.

### Discarding: killing the experiment

This is the payoff. The AI tried something bold on the branch, you looked at it, and you don't want
it. You don't undo anything. You don't `restore` file by file. You switch away and delete the branch
(`git switch main`, then `git branch -D experiment`, which force-deletes even though it was never
merged). The agent runs both on your say-so.

That's it. The experiment is gone. `main` never changed. `git log` on `main` shows no sign it ever
happened. **The whole bold attempt cost you one branch and one delete.**

This is the mental shift the module is selling: when discarding is this cheap, you stop being precious
about what you let the AI try. Risky refactor? Branch it. Want to compare two approaches? A branch
each, keep the winner, delete the loser. The branch is the unit of "maybe."

### Merge conflicts: when two changes collide

Most merges just work; Git is good at combining changes that touch *different* lines. A **conflict**
happens only when two branches changed **the same lines** in different ways, and Git refuses to
guess which one you meant. It stops the merge and marks the collision *inside the file* so you can
decide:

```python
<<<<<<< HEAD
    print("usage: python3 cli.py [add <title> | list | done <index> | stats]")
=======
    print("usage: python3 cli.py [add <title> | list | done <index> | purge]")
>>>>>>> experiment
```

Read it like this:

- `<<<<<<< HEAD` to `=======` is **your current branch's version** (the branch you're merging *into*,
  `main`, here).
- `=======` to `>>>>>>> experiment` is **the incoming branch's version**.
- Both markers and the divider are real text Git inserted into your file. Resolving means **editing
  the file so it contains the version you want and deleting all three marker lines.**

Resolving isn't picking a side mechanically. It's deciding what the line *should* say. Often that's
one side; sometimes it's a blend of both (here, a usage string that lists *both* `stats` and `purge`).
This is the kind of bounded reasoning task the AI is good at: it sees both versions and the
surrounding code. Once the file is correct and marker-free, telling Git the conflict is settled is
two more commands the agent runs (`git add cli.py` to mark the file resolved, then `git commit` to
complete the merge).

Here's the part that has changed under your feet, and it's the real lesson of this module's lab. The
markers above are what a conflict looks like *if you ever see one*. Tell a current frontier
editor-agent to "merge `feature/stats` into `feature/purge`" and it usually never stops: it reads
both sides, resolves the collision, completes the merge, and reports a clean result, all in one turn.
You never saw a marker. From your seat the conflict simply did not happen. That is convenient right
up until the silent resolution is wrong (it can keep the worse of the two sides, or blend them into a
line that satisfies neither), and now a bad merge is sitting in your history with nothing that looked
like an error.

So the skill is no longer "edit the markers by hand." It is two things: **know what a conflict is**
(so you recognize one when an agent does surface it) and **check `git diff` after every merge** (so a
silent resolution can't slip a wrong line past you). `git status` during a conflict is your map; it
lists every file still "unmerged." If you want to *see* the markers before the agent touches them,
tell it to stop on conflict and show you (you'll do exactly that in the lab). And if things go
sideways, `git merge --abort` rewinds to before the merge with no harm done.

---

## The AI angle

Everything above is standard Git. Here's why it matters *more* in an AI-assisted workflow, not less:

- **The branch is the blast-radius container for an autonomous attempt.** An agent editing your files
  directly (Module 4) is fast and confident, including when it's confidently wrong across four
  files. On `main`, cleaning that up is a chore. On a branch, you delete the branch. The riskier and
  more autonomous the AI work, the more a branch earns its keep, which is why this concept underpins
  everything in Unit 5, where agents run with far less supervision.
- **"Throw it away" is the feature, not the failure.** With copy-paste, a rejected AI attempt still
  cost you the manual work of pasting it in and the manual work of ripping it back out. With a
  branch, a rejected attempt costs *nothing*: `git branch -D` and it's as if it never happened. That
  flips the economics: you can let the AI try things you'd never risk if undoing were expensive.
- **Compare, don't commit-and-hope.** Ask the AI for approach A on one branch and approach B on
  another. Run both. Keep the winner, delete the loser. You're using branches as cheap A/B
  experiments on implementation, something that's painful without them and trivial with them.
- **The AI resolves conflicts so well you may never see one.** A merge conflict is a small, perfectly
  bounded reasoning task: here are two versions of the same lines and the surrounding code; produce
  the correct combined version. A current editor-agent is good enough at this that, told to "merge X
  into Y," it usually resolves the collision and completes the merge in the same turn, no markers
  shown, no question asked. That's the highest-hit-rate convenience of the tool and its sharpest trap:
  you still decide whether the resolution is right (it can absolutely merge two changes into something
  that satisfies neither), except now you might not even know there *was* a conflict to second-guess.
  The defense is mechanical and non-negotiable: read `git diff` after every merge. You'll feel both
  the convenience and the trap in the lab.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/06-branches-sandboxes-for-experiments/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 6"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Git commands), driving the `tasks-app` from Modules 1–2 with your
editor-integrated AI from Module 4.

You'll do three things: let the AI try a bold change on a branch, decide its fate, and then engineer
a merge conflict so you can see one once, undo it, and watch the AI resolve it silently while you do
the one job that's still yours: verify the result.

**You'll need:**

- The `tasks-app` Git repo from Module 2 (committed, clean working tree; run `git status` and make
  sure it says "nothing to commit").
- Your editor-integrated AI from Module 4.
- Git (you've had it since Module 2).

> Throughout, "ask your AI" now means your **editor-integrated** agent (Module 4) editing the files
> directly, no more copy-paste. After it edits, you still read `git diff` before committing. That
> habit doesn't go away; the branch just decides how *much* damage a bad diff can do.

### Part A: Branch it and let the AI go bold

1. Make sure you're in the repo, then **tell the agent to set up the branch.** Ask:

   > *"We're on the `tasks-app` repo. Confirm we're on `main` with a clean working tree, then create
   > a branch called `experiment/priorities` and switch to it."*

   Then **verify** it did what you asked, by hand:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   git status                       # should be clean, on experiment/priorities
   git branch                       # the * should be on experiment/priorities
   ```

   You're not typing the branch commands; you're confirming the agent ran them correctly. This is the
   pattern for the whole module: you direct, the agent does the git, you check.

2. Give the AI a deliberately *bold* task, the kind you'd hesitate to run straight on `main`:

   > *"Add task priorities (low/medium/high) to this app. Store a priority on each task, let me set
   > it when adding (`add "thing" --priority high`), show it in `list`, and sort `list` so high
   > priority comes first. Change whatever files you need to."*

   Let it edit `tasks.py` and `cli.py` freely. This is a multi-file change: nerve-wracking on `main`,
   relaxed on a branch.

3. Review the change, then have the agent commit it **on the branch**. First read the diff and run
   the app yourself:

   ```bash
   git diff                         # read what it actually changed
   python3 cli.py add "ship module 6" --priority high
   python3 cli.py add "water plants" --priority low
   python3 cli.py list               # see if priorities work and sort
   ```

   Once the diff looks right and the feature runs, tell the agent:

   > *"Commit this on the branch with a message like 'Add task priorities (experiment)'."*

   The agent decides what to stage and writes the commit. Confirm it landed with `git log --oneline`.

4. Now prove the isolation. Ask the agent to switch back to `main`, then watch the feature
   **disappear**:

   > *"Switch back to `main`."*

   ```bash
   python3 cli.py list               # no priorities; main is exactly as you left it
   ```

   Your bold change exists only on the branch. `main` never saw it, and that's the whole point.

### Part B: Decide its fate

**The decision is yours; the execution is the agent's.** Pick the path that matches reality. Do at
least one; ideally do **Path 2 (discard)** on this experiment so you feel how clean it is, then re-run
Part A and do **Path 1 (keep)** so you've done both.

**Path 1: Keep it (merge).** Tell the agent:

> *"Merge `experiment/priorities` into `main`, then delete the branch."*

Then verify the result yourself:

```bash
git log --oneline --graph            # straight line = fast-forward merge
python3 cli.py list                   # the feature is now on main
git branch                           # experiment/priorities is gone
```

**Path 2: Throw it away (discard).** Tell the agent:

> *"Switch to `main` and discard the `experiment/priorities` branch entirely."*

Then verify:

```bash
git log --oneline                    # no trace of the experiment on main
python3 cli.py list                   # main is untouched, exactly as before
git branch                           # the branch is gone
```

Notice what you did *not* do in Path 2: no file-by-file `restore`, no manual undo, no hunting through
diffs. The agent deleted a label and the entire experiment was gone. That's the economics shift: bold
AI attempts become free to reject.

### Part C: Create a merge conflict and resolve it with the AI

Merge conflicts have an outsized reputation for difficulty. You'll engineer a guaranteed one by having
**two branches change the same line in different ways**, then resolve it with the agent.

> **Starting state.** By now your `tasks-app` has accumulated commands from earlier modules, so your
> `usage:` line is longer than the bare `[add <title> | list | done <index>]` you started with, and
> that's fine. This lab works *regardless* of what's on that line, because the collision is just "two
> branches each appended a different new command to the same usage line." To make it reproduce even on
> a carried-forward app, we deliberately add two commands you **haven't** built yet: `stats` and
> `purge`. (Any two brand-new commands would do; the point is the same line, edited two ways.) The
> marker examples below show the shape; your real markers will carry your fuller usage string.

1. From a clean `main`, set up the first branch and the `stats` command in one instruction to the
   agent:

   > *"From `main`, create a branch `feature/stats`, add a `stats` command to `cli.py` that prints how
   > many tasks are total, done, and pending, update the usage string to include it, then commit it
   > with the message 'Add stats command'."*

   Verify the agent edited the usage line and committed:

   ```bash
   git diff main                    # the usage line changed + the command was added
   git log --oneline               # the commit is there, on feature/stats
   ```

2. Now the second branch, which touches **the same usage line** a different way:

   > *"Switch back to `main`, create a branch `feature/purge`, add a `purge` command to `cli.py` that
   > removes all completed (done) tasks, update the usage string to include it, then commit it with
   > the message 'Add purge command'."*

   Verify the collision is set up:

   ```bash
   git diff main                    # feature/purge edited the same usage line
   ```

   Both branches changed the same `usage:` line, each adding a *different* command. Git won't be able
   to auto-merge that line.

3. **Witness the conflict first.** If you tell a current agent to just "merge them," it will resolve
   the collision and finish the merge in one turn, and you'll never see a marker (you'll do exactly
   that in step 5, on purpose). So this once, ask it to stop and show you instead, the same way
   Module 26 does it:

   > *"You're on `feature/purge`. Merge `feature/stats` into it. If it conflicts, stop and show me the
   > conflict; do not resolve it yet."*

   The merge stops on the usage line. Confirm the conflict state yourself, then open `cli.py` and find
   the markers (your usage string will be longer (it carries the commands from earlier modules), but
   the collision is exactly this: both branches appended a different new command to the same line):

   ```bash
   git status                       # cli.py listed under "Unmerged paths"
   ```

   ```python
   <<<<<<< HEAD
       print("usage: python3 cli.py [add <title> | list | done <index> | purge]")
   =======
       print("usage: python3 cli.py [add <title> | list | done <index> | stats]")
   >>>>>>> feature/stats
   ```

   This is the whole point of the step: *see one real conflict* so you can recognize the shape. `HEAD`
   is your current branch (`feature/purge`); the block below the `=======` is what `feature/stats`
   wants. (The command bodies for `stats` and `purge` touch different lines, so Git merged *those*
   cleanly on its own; the only collision is the usage string both branches edited.)

4. **Undo it.** You've seen the conflict; now rewind so the AI can handle it from scratch. Tell the
   agent (or run it yourself, it's the safe-undo from the Key concepts section):

   > *"Abort the merge."*

   ```bash
   git merge --abort
   git status                       # clean again, back on feature/purge, no merge in progress
   ```

   You're now exactly where you were before step 3, mid-experiment with two colliding branches and no
   merge underway.

5. **Now let the AI do it for real, and watch it auto-resolve.** This time, no stop-on-conflict guard.
   Direct it the way you actually would in a real workflow:

   > *"You're on `feature/purge`. Merge `feature/stats` into it. The usage line collides; the final
   > version should list BOTH the `stats` and `purge` commands."*

   Notice what happens: the agent hits the same conflict you just saw, resolves it, and completes the
   merge in one turn. It probably never shows you a marker. From your seat the merge just "worked." It
   should have produced a single, marker-free line listing both commands, e.g.:

   ```python
       print("usage: python3 cli.py [add <title> | list | done <index> | stats | purge]")
   ```

   **Here is the punchline of the whole module: you have no idea yet whether that's right, so verify.**
   The conflict was invisible, which means a wrong resolution would have been invisible too. A resolver
   can confidently drop one side, leave a stray marker, or "blend" the lines into something that runs
   but means the wrong thing. The only thing standing between you and a silently-bad merge is the
   `git diff` you run *after every merge*, conflict or not:

   ```bash
   git diff HEAD~1                  # what the merge actually changed; confirm no markers remain
   git log --oneline --graph        # the fork-and-join: this is a merge commit
   python3 cli.py                    # run with no args, see the merged usage string
   python3 cli.py stats              # both commands actually work
   python3 cli.py purge
   ```

   If the usage line lists both commands and both run, the AI's silent resolution was correct. If it
   dropped one, you just caught a bug that left no error message behind, which is precisely why the
   check isn't optional. You directed the merge, the agent did the plumbing *and* the resolution, and
   the verify was yours. That last part is the skill: not reading markers by hand, but knowing a
   conflict can happen and checking the AI's work even when it never tells you one did.

> **Guaranteed-conflict generator.** AI edits are nondeterministic, so if the agent didn't touch the
> same line on both branches and you *didn't* get a conflict in step 3, run the helper script to
> manufacture one deterministically, then practice the witness-and-verify flow on it. Copy it into
> your `tasks-app` first (the course's lab scripts live in the course repo, not in `tasks-app`; see
> Module 4's *You'll need*), then run it from inside the repo:
>
> ```bash
> cp ~/ai-workflow-course/the-workflow-course/modules/06-branches-sandboxes-for-experiments/lab/make-conflict.sh .
> bash make-conflict.sh
> ```
>
> It creates two branches that both edit the same line of `README.md`, leaving you mid-conflict with
> on-screen instructions. From there, hand it to the agent the same way (step 5), then verify. The
> resolution mechanic is identical to the code case above.

---

## Where it breaks

The honest limits, so you don't over-trust the sandbox:

- **A branch isolates *files in the repo*, nothing else.** Switching branches rewrites your tracked
  files; it does **not** roll back a database the app wrote to, files Git is ignoring, running
  processes, or anything outside version control. If your AI experiment ran a migration or wrote to
  `tasks.json` (which the Module 2 `.gitignore` excludes), deleting the branch won't undo *that*. The
  sandbox is the repo, not the world. (Real environment isolation is a later problem: containers,
  Module 16.)
- **Branches are local until you push them.** Everything in this module lives on your laptop. A
  branch isn't shared, backed up, or visible to anyone else until there's a remote; that's
  **Module 8**. Right now `git branch -D` deletes work that exists nowhere else, permanently. Treat
  an unpushed branch as exactly as fragile as the rest of your local-only repo.
- **The AI can resolve a conflict into something plausible and wrong, and you may never know one
  happened.** It sees both sides and the intent, which makes it good at this, but "good" isn't
  "trusted." Worse, a current agent resolves silently: told to merge, it fixes the collision and
  finishes the merge in one turn, so a resolution that runs cleanly but means the wrong thing
  (silently keeping the worse of two changes, or merging two behaviors into one that satisfies
  neither) leaves no marker, no prompt, no error behind. That invisibility is exactly *why* the
  post-merge `git diff` is the safeguard, not optional ceremony: it's the only thing that surfaces a
  conflict the agent already swallowed. Reviewing AI output is its own discipline; that's Module 10.
- **Long-lived branches drift and conflict harder.** The longer a branch lives away from `main`, the
  more `main` moves underneath it and the gnarlier the eventual merge. The defense is the same as
  "commit often": branch small, merge soon, delete promptly. A branch that's been open for three
  weeks is a future conflict, not a sandbox.
- **Force-delete (`-D`) and `merge --abort` are sharp.** `-D` discards unmerged commits with no
  confirmation; `--abort` throws away an in-progress resolution. Both are exactly what you want at
  the right moment and a foot-gun at the wrong one. Know which one you're reaching for.

---

## Check for understanding

**You're done when:**

- You directed the agent to branch, let the AI make a multi-file change on it, and confirmed `main`
  was untouched by switching back and seeing the change vanish.
- You have **discarded** an experiment (the agent ran `git branch -D`) and confirmed `main` shows no
  trace, and you have **merged** one in and seen it land on `main`.
- You can explain, in one sentence, why creating a branch costs essentially nothing (it's a movable
  pointer, not a copy).
- You saw a real merge conflict at least once (the `<<<<<<<`/`=======`/`>>>>>>>` markers), then let
  the AI merge for real and resolve it silently, and you verified the result with `git diff` even
  though no marker was ever shown to you, confirming the merged file runs.
- You can name the limit: a branch isolates tracked files, not your database, ignored files, or the
  outside world.

When "let the agent try something wild" feels like a one-line decision instead of a risk assessment,
you've got it. Module 7 takes the next step: running several of these branches *live at the same
time* in separate working directories, so multiple agents can work in parallel without colliding.
