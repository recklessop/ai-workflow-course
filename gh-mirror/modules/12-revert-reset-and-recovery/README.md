# Module 12: When It Goes Wrong: Revert, Reset, and Recovery

> **A bad change already shipped. Now what?** Recovery is its own skill. Knowing the *right* undo for
> the situation is the difference between a clean five-second fix and force-pushing over your
> teammates' work.

---

## Prerequisites

- **Module 2: Version Control as a Safety Net.** You can commit, read a `diff`, and `git restore`
  uncommitted changes. This module is the rest of the undo toolkit: undoing things that are *already
  committed*, including things already shared.
- **Module 6: Branches: Sandboxes for Experiments.** You merge branches. The headline example here
  is undoing a bad *merge*, which only makes sense once you've made one.
- **Module 8: Remotes and Hosting.** You've pushed history somewhere others can pull it. That's what
  makes "shared history" real, and it's the dividing line between the safe undo and the dangerous
  one. Module 8 was the *backup* half of the backup-and-recovery thread; this is the *recovery* half.
- **Modules 10–11: Reviewing Code You Didn't Write / Collaboration.** A bad change usually arrives
  as a merged PR, and other people (and agents) are pulling from the same branch. Recovery has to be
  safe for *them*, not just you.

If you've parachuted in: you minimally need to be comfortable with commits, branches, merges, and
`git push` to a remote others share.

---

## Learning objectives

By the end of this module you can:

1. Choose the correct undo for a situation (`restore`, `revert`, or `reset`) and explain why the
   other two would be wrong.
2. Cleanly undo a change that's already on shared history with `git revert`, including the hard case:
   reverting a merge commit.
3. Recover commits you thought you'd destroyed using `git reflog`, even after a `reset --hard`.
4. Drop named recovery points with tags (and host releases) before risky work.
5. State precisely where Git's recovery powers end: what it is *not* a backup for, and why that
   matters before you trust it.

---

## Key concepts

### Three undos, three blast radii

Git has more than one "undo," and the failure mode is using the wrong one. They differ by *what they
touch* and *whether they're safe once history is shared*. Hold this table in your head; the rest of
the module is just filling it in:

| Command | Undoes | Touches history? | Safe on shared history? |
|---------|--------|------------------|--------------------------|
| `git restore <file>` | **Uncommitted** edits in your working tree | No | Yes; there's nothing shared to break |
| `git revert <commit>` | An **already-committed** change, by writing a *new* inverse commit | No; it *adds* | **Yes**; this is the team-safe undo |
| `git reset <commit>` | Moves your branch pointer **backward**, un-committing | **Yes; it rewrites** | **No**; dangerous once others have pulled |

`restore` you already met in Module 2; it's for the mess that hasn't been committed yet. This module
is the other two rows, because the AI's worst messes are the ones that already made it into a commit,
a merge, or a PR.

### `git revert`: undo by adding, not erasing

The mental model: a commit is a diff (a set of line changes). `git revert <commit>` computes the
*opposite* diff and commits it. The bad change is still in the history, but a new commit immediately
after it cancels it out. The net effect on your files is "as if it never happened"; the net effect on
your *history* is "we tried it, then we deliberately undid it," which is honest and readable.

```bash
git log --oneline
# a1b2c3d  Add "export to CSV" command   <- this turned out to be broken
git revert a1b2c3d
# opens an editor for the revert message, then commits the inverse
git log --oneline
# 9f8e7d6  Revert "Add export to CSV command"
# a1b2c3d  Add "export to CSV" command
```

**Why this is the one you reach for first:** it never rewrites history. Anyone who already pulled
`a1b2c3d` just pulls one more commit on top and they're in sync with you. Nobody's clone breaks,
nobody has to force-anything. On a branch other people (or agents) share, `revert` is almost always
the correct answer.

This also maps straight back to the Module 2 reframe: the repo is durable memory. A `revert` commit
is *more* informative than a silent erase. Six months later, `git log` tells you the feature was
tried and pulled, and the message says why. You're writing the project's memory, not editing it.

### Reverting a bad **merge**: the headline case

This is the one that bites people, because it's exactly what happens when a bad PR gets merged
(Modules 10–11): you don't have one bad commit, you have a *merge commit* that pulled in a whole
branch's worth of them. The naive `git revert <merge-sha>` fails:

```
error: commit abc123 is a merge but no -m option was given.
fatal: revert failed
```

A merge commit has **two parents**: the branch you were on, and the branch you merged in. Git can't
guess which side is "the mainline you want to keep." You tell it with `-m`:

```bash
git revert -m 1 <merge-sha>
```

`-m 1` means "treat parent #1 (the branch I was sitting on when I merged, i.e. `main`) as the line
to keep, and undo everything the *other* side brought in." `-m 2` would mean the opposite. For "a bad
feature got merged into main," it's almost always `-m 1`. You can confirm the parents before you act:

```bash
git show <merge-sha> --format="%P" --no-patch   # prints the two parent SHAs, in order
```

**The gotcha you must know about:** reverting a merge tells Git "the content of
that branch is undone." If you later fix the branch and try to merge it again, Git looks at the
*reverted* merge and decides those commits are already accounted for, so it brings in **nothing**,
or only the new commits, silently leaving your fix half-applied. The fix is counterintuitive: to
re-merge a branch whose merge you reverted, **revert the revert** first (`git revert <revert-sha>`),
then add your new work on top, then merge. This is a real, recurring source of "why didn't my merge
do anything," and now you know the cause.

### `git reset`: moving the branch pointer (and why it's sharp)

`git reset <commit>` doesn't write an inverse commit. It **moves your current branch to point at an
older commit**, effectively un-committing everything after it. Because it changes *which commits the
branch contains*, it rewrites history, and that's both its power and its danger.

It comes in three flavors that differ only in what they do to your files:

```bash
git reset --soft  HEAD~1   # un-commit, but KEEP the changes staged (ready to recommit)
git reset --mixed HEAD~1   # un-commit, keep changes in working tree but UNstaged  (the default)
git reset --hard  HEAD~1   # un-commit AND throw the changes away entirely          (destructive)
```

- `--soft` is the friendly one: "I committed too early / want to redo the message or squash." Your
  work is untouched, just no longer committed.
- `--mixed` (the default) un-commits and un-stages but leaves your edits in the files.
- `--hard` deletes the changes from your working tree too. This is the one that ruins days.

**When `reset` is correct:** *only on history you have not shared.* Cleaning up your own local
commits before you push (squashing three "wip" commits into one, fixing a botched last commit) is
exactly what it's for. The moment a commit has been pushed and someone else has pulled it, `reset`
becomes a way to *rewrite history out from under them*: your branch and theirs now disagree about
what happened, and the only way to push your rewritten version is `--force`, which overwrites the
shared record. On a shared branch, that's how you delete a teammate's (or an agent's) work.

The rule, stated plainly:

> **Already shared? Use `revert`. Only ever local? `reset` is fine.** When unsure, assume shared.

### `git reflog`: recovering commits you thought you destroyed

Here's the reassuring part. `reset --hard` *feels* like it nukes commits permanently. It almost
never does. Git keeps a private, local log of **everywhere `HEAD` has ever pointed**: every commit,
reset, checkout, merge, and rebase lands in the *reflog*. A commit you "lost" with `reset --hard` is no
longer reachable from your branch, but it's still in the object database, and the reflog still knows
its SHA.

```bash
git reflog
# 9f8e7d6 HEAD@{0}: reset: moving to HEAD~1
# a1b2c3d HEAD@{1}: commit: Add the feature I just "lost"      <- there it is
# ...
git reset --hard a1b2c3d      # branch pointer back to the lost commit, fully recovered
# or, more cautiously, inspect it first on a throwaway branch:
git branch recovered a1b2c3d
```

This is the answer to "an agent ran `git reset --hard` and ate an hour of my commits." As long as
the work was *committed at some point*, the reflog can almost certainly get it back. Most people
don't know it exists until the day they need it.

Two limits, because they matter: the reflog is **local only** (it's not pushed; a fresh clone
has an empty reflog), and entries **expire**. Unreachable ones are garbage-collected after roughly
30 days by default, reachable ones after about 90. The reflog is a recovery net for *recent* mistakes
on *your* machine, not an archive. (And it can only recover what was *committed*; see "Where it
breaks.")

### Tags and releases: named recovery points

Commits have SHAs; SHAs are unmemorable. A **tag** is a human-readable, permanent name pinned to a
specific commit, a recovery point you can actually find later.

```bash
git tag -a v1.0 -m "Last known-good before the big AI refactor"   # annotated tag on HEAD
git push origin v1.0                                              # tags don't push by default
# ...later, things have gone sideways...
git diff v1.0                 # what's changed since the known-good point
git checkout v1.0             # inspect the exact known-good state
```

Use them as deliberate checkpoints: **before you turn an agent loose on a large, sweeping change, tag
the known-good state.** If the refactor goes wrong, `v1.0` is a named anchor you can diff against or
return to without spelunking through `log` for the right SHA. On your git host, a **release** is a tag
plus notes and downloadable artifacts, the same idea dressed up as a thing the rest of the team can
point at. Tags are the durable, *shareable* recovery points the reflog is not.

---

## The AI angle

Recovery was always a real skill. AI raises its value on every axis:

- **AI makes bigger, bolder changes faster, and lands them through the same PR door.** A sweeping
  "refactor the whole module" that *looks* right, passes a human skim (Module 10), gets merged
  (Module 11), and only then reveals it broke something. That's a bad *merge* on shared history, the
  exact case `git revert -m 1` exists for. The faster code merges, the more you need the clean,
  team-safe undo.
- **Agents run destructive git commands.** An agent told to "clean up the branch history" can reach
  for `reset --hard` or a force-push and vaporize work. `reflog` is your net for precisely this,
  which is why an IT pro supervising agents needs it *cold*, not as trivia.
- **Recovery is durable memory, done right.** A `revert` commit records that something was tried and
  pulled, and why, readable by the next session (Module 2's reframe) and by the next teammate. A
  silent `reset` erases that memory. On a project where agents reconstruct state from `git log`,
  preferring `revert` over `reset` keeps the history honest for the next agent that reads it.
- **The "tag before the risky thing" habit is an AI habit.** The riskiest changes in your week are
  increasingly the ones you hand to an agent. Tagging the known-good state first turns "I think it was
  working yesterday" into a named anchor you can diff against in one command.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/12-revert-reset-and-recovery/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 12"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Git commands), on the `tasks-app` from Modules 1–2.

You'll do the two scenarios that matter most: **revert a bad merge** that's already on `main`, then
**lose a commit and get it back** with the reflog. Both are things that *will* happen to you for real;
do them once on purpose now.

**You'll need:**

- The `tasks-app` Git repo from Module 2 (with a few commits in its history).
- Git installed, and your agent in the repo. We use **Claude Code** as the worked example
  (`claude  # sub your own agent`); the directing-and-verifying pattern is the same for any of them.
- The starter file `lab/bad-clear-snippet.py` from this module, a deliberately broken `clear`
  command, so everyone produces the *same* bad merge instead of relying on the AI to misbehave on cue.

> **A note on realism.** By now (post–Module 4) your AI edits files directly. We hand you the exact
> broken snippet anyway so the lab is deterministic; the point is practicing the *recovery*, not
> waiting for a model to break something on demand.

You direct the agent to do the git work and you verify the result. The whole point of this lab is
that *you* hold the judgment: which undo, which parent, whether it actually worked.

1. Get the repo onto a clean `main`. Tell your agent:

   > Make sure `~/ai-workflow-course/tasks-app` is on a clean `main`; switch to it and confirm
   > there's nothing uncommitted.

   Verify before you go further:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   git status          # should be clean, on main
   ```

2. Stage the broken change. The snippet in `lab/bad-clear-snippet.py` *looks* reasonable and even
   "works" once; the bug is that it corrupts the saved state so the **next** command crashes. Hand it
   to your agent:

   > Create a branch `bad-clear`. Add the `elif command == "clear"` block from
   > `lab/bad-clear-snippet.py` into `cli.py`'s command dispatch inside `main()`, next to the other
   > `elif command == ...` branches. Commit it with the message `Add clear command`.

   Verify the agent did exactly that, on the branch:

   ```bash
   git log --oneline -1            # "Add clear command", on bad-clear
   git show HEAD -- cli.py | grep clear   # the clear branch is in the diff
   ```

3. Merge it into `main` as a real merge commit (a merged PR is a merge commit, not a fast-forward):

   > Switch to `main` and merge `bad-clear` with a real merge commit (no fast-forward), message
   > `Merge branch 'bad-clear'`.

   Verify the shape:

   ```bash
   git log --oneline --graph -3   # a merge commit sitting on main
   ```

4. **Now feel the bug.** It passes the first skim:

   ```bash
   python3 cli.py add "ship it"
   python3 cli.py clear          # prints "cleared all tasks", looks fine!
   python3 cli.py list           # CRASHES: it corrupted tasks.json, load() blows up
   ```

   This is the AI plausibility trap made concrete: the change reviewed fine and "worked," and broke
   the *next* command. It's merged on `main`. You need it gone, and safely, because in a real team
   others may have already pulled.

5. Direct the agent to undo the bad merge, and watch the trap. Reverting a merge is fiddly: a naive
   `git revert HEAD` refuses, because a merge has two parents and Git won't guess which side to keep.
   Tell your agent:

   > The merge we just put on `main` is bad. Undo it safely on shared history. Note that it's a merge
   > commit.

   A naive revert hits this, and a competent agent recognizes it:

   ```
   error: commit ... is a merge but no -m option was given
   fatal: revert failed
   ```

   The correct move keeps the `main` side, which is parent 1:

   ```bash
   git revert -m 1 <merge-sha>   # writes a NEW commit that undoes the whole merge
   ```

6. **Verify and decide; this is the part you own.** Don't take "I reverted it" on faith. Confirm the
   agent kept the *right* parent: parent 1 is the old `main` tip, parent 2 is `bad-clear`, and `-m 1`
   keeps parent 1. If it had used `-m 2` it would have kept the broken side.

   ```bash
   git show <merge-sha> --format="%P" --no-patch   # two SHAs: parent 1 is main, parent 2 is bad-clear
   git log --oneline -3                             # a "Revert ..." commit on top
   ```

7. Prove you're recovered, and notice nothing was erased:

   ```bash
   rm -f tasks.json                              # drop the corrupted state file the bug wrote
   python3 cli.py add "back to normal"
   python3 cli.py list                            # works again, the clear command is gone
   git log --oneline                             # the bad merge is STILL there, with a revert after it
   ```

   > **On Windows:** `rm -f` is bash. Run this lab from Git Bash or WSL (it works as-is), or use
   > PowerShell's `Remove-Item -Force tasks.json`. Every other command here is Git, identical across
   > shells.

   That last point is the whole lesson: you undid the effect **without rewriting history**. Anyone who
   pulled the bad merge just pulls your revert on top and they're fine.

### Part B: "Lose" a commit, recover it with the reflog

1. Make a small real commit you'd be sad to lose. Tell your agent:

   > Add a trivial `version` command to `cli.py` that prints a version string, and commit it with the
   > message `Add version command`.

   Verify it's there:

   ```bash
   git log --oneline -1         # "Add version command"
   python3 cli.py version        # prints the version
   ```

2. Now destroy it the way an over-eager "clean up the history" cleanup (or an agent) would, with a
   hard reset. Run this one yourself so you feel the floor drop out:

   ```bash
   git reset --hard HEAD~1
   git log --oneline -2         # the "Add version command" commit is GONE from the branch
   python3 cli.py version 2>/dev/null || echo "command no longer exists"
   ```

   It's not in `log`. It feels permanently lost. It isn't.

3. Direct the agent to recover it from the reflog. You need to know the reflog exists so you can ask
   for it and check the result:

   > My last commit was destroyed by a `git reset --hard`. Find it in the reflog and restore the
   > branch to it. Show me the reflog line you used before you reset.

   Then verify. The commit is back, and the app works again:

   ```bash
   git log --oneline -1         # "Add version command" is back
   python3 cli.py version        # works again
   ```

   You just recovered a commit that `log` swore was gone. Note the honest limit: step 2's `--hard`
   would have *also* eaten any uncommitted edits in the working tree at the time, and the reflog could
   **not** have saved those, because they were never committed. Recovery covers committed history, not
   unsaved scratch work.

### Part C (optional): Drop a named recovery point

Before you hand the agent something sweeping, have it tag the current known-good state:

> Tag the current commit as `known-good`, an annotated tag, message "Clean state at end of Module 12
> lab".

Confirm the anchor exists:

```bash
git tag                        # known-good is listed
git diff known-good            # later, this shows everything that changed since this anchor
```

Get in the habit of tagging before you hand an agent something sweeping.

---

## Where it breaks

This is the second half of the backup-and-recovery thread (Module 8 was the first), and the most
important thing it teaches is **where the analogy stops.** Git gives you excellent *point-in-time
logical recovery for versioned text*. It is emphatically **not** a general backup system. Treating it
like one is how people lose data they thought was safe.

- **It is not backup for your database, or any runtime state.** Your app's data lives in a database,
  in object storage, on a running server. None of that is in the repo (and shouldn't be). `git revert`
  rolls back *code*; it does nothing for the rows your buggy migration already mangled. Restoring data
  is a different discipline with different tools; Git has no opinion on it.
- **It is not backup for secrets, which shouldn't be in there anyway.** API keys, tokens, and
  credentials don't belong in the repo in the first place (Module 17 is the whole story). If they *did*
  leak in, note the trap: `revert` does **not** remove them from history; the secret is still sitting
  in the old commit for anyone with the repo. A committed secret is a *leaked* secret; rotate it, don't
  just revert it.
- **It only recovers what was committed.** This is Module 2's limit, sharpened. `reset --hard` and
  `git restore` both destroy *uncommitted* working-tree changes, and **the reflog cannot bring those
  back**; there's no object to recover because nothing was ever committed. The defense is the same one
  the whole course keeps repeating: commit often, so "uncommitted" is always a small window.
- **It is poor backup for large binaries.** Git versions text beautifully and binaries terribly
  (Module 3): every change to a big binary stores a whole new copy, bloating the repo, and the "diff"
  is useless noise you can't review or merge. Datasets, video, compiled artifacts, model weights:
  these need real artifact/object storage, not your Git history.
- **The reflog is local and temporary.** It's your machine only (not pushed, empty in a fresh clone),
  and it's garbage-collected (roughly 30 days for unreachable entries). It's a recovery net for recent
  local mistakes, not an offsite archive. The *offsite, distributed* durability comes from pushing to
  remotes, which is exactly Module 8's half of this thread. Recovery (this module) and backup
  (Module 8) are two different powers; you need both.
- **Reverting a merge has a sting in the tail.** As covered above: once you `revert -m 1` a merge,
  re-merging that branch later quietly does nothing useful until you *revert the revert*. Forget this
  and you'll burn an afternoon wondering why your fix won't merge.

The boundary in one line: Git is a near-perfect time machine for the *text you committed*, and nothing
more. Know that boundary and you'll trust it exactly as far as it deserves.

---

## Check for understanding

**You're done when:**

- You can state, without looking, which undo to use for (a) an uncommitted mess, (b) a bad change
  already pushed to a shared branch, and (c) three local "wip" commits you want to squash before
  pushing, and why the wrong choice is wrong in each case.
- You have reverted a real merge commit with `git revert -m 1` on your `tasks-app`, and your `git log`
  shows both the bad merge and the revert sitting on top of it (history preserved, effect undone).
- You have "lost" a commit with `reset --hard` and recovered it from `git reflog`.
- You can explain, in one breath, four things Git is *not* a backup for: your database, your secrets,
  your uncommitted changes, and your large binaries, and why the reflog wouldn't have saved the third.

When `revert` vs. `reset` is automatic, the reflog feels like a safety net instead of a rumor, and you
can name where Git's recovery stops, you've got the recovery half of the thread. That completes the
team layer (Unit 2); next, Unit 3 starts automating the checking and shipping, beginning with tests.
