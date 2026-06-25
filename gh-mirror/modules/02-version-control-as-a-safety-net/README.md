# Module 2: Version Control as a Safety Net

> **Version control is undo for the AI, and it's the AI's memory between sessions.** This is the one
> module that makes every riskier thing in the rest of the course safe to attempt.

---

## Prerequisites

- **Module 1**: you have a real local project (`tasks-app`), an editor, and a terminal, and you've
  felt the three seams where copy-paste breaks. This module installs the fix for the third seam (no
  undo, no record) and, surprisingly, the second (no memory across time) as well.

You do **not** need Git installed yet; that's the first step of the lab.

---

## Learning objectives

By the end of this module you can:

1. Initialize a repository and capture your work as commits: checkpoints you can always return to.
2. Read what changed with `git status`, `git diff`, and `git log`, and undo unwanted changes with
   `git restore`.
3. Recover cleanly after an AI confidently makes a mess, without retyping anything.
4. Use the repo as **durable memory**: have a fresh AI session reconstruct "where were we?" entirely
   from Git, with no chat history.
5. Explain the one thing Git *can't* see, and why that's the argument for committing often.

---

## Key concepts

### What Git actually is (for this audience)

Strip away the open-source mythology and Git is one thing: **a tool that records snapshots of your
files over time and lets you move between them.** Each snapshot is a *commit*. A commit is a labeled
checkpoint: "here is exactly what every file looked like at this moment, and here's a note about
why." You can compare any two checkpoints, and you can return to any of them.

That's it. Everything else (branches, remotes, merges) is built on "snapshots you can move
between." For now we only need the local core: `init`, `commit`, `diff`, `log`, `restore`.

### Reframe 1: Commits are undo for the AI

Module 1's third seam was: when the AI makes a mess, you have no checkpoint to return to. A commit
*is* that checkpoint. The workflow becomes:

1. Get the project to a working state.
2. **Commit it.** Now this exact state is saved forever, with a message.
3. Let the AI try something, anything, however risky.
4. If it worked, commit again. If it didn't, **`git restore` throws away the mess and you're back at
   step 2's checkpoint, byte for byte.**

This is what the whole course is built on. Every later module asks you to let the AI do something
bolder: edit real files (Module 4), work on a branch (Module 6), open a PR (Module 10), run
unattended (Unit 5). You can say yes to all of it *because* you can always get back to a known-good
checkpoint. Without this, every AI change is a gamble. With it, the downside is "throw away five
minutes of work."

The core commands:

```bash
git init -b main         # turn the current folder into a repository, first branch named "main" (once per project)
git status               # what's changed since the last commit?
git add .                # stage the changes you want in the next commit
git commit -m "message"  # save a checkpoint with a note
git diff                 # show the exact line-level changes not yet committed
git log --oneline        # list past checkpoints, newest first
git restore <file>       # discard uncommitted changes to a file (the undo)
```

A note on `restore`: `git restore <file>` throws away **uncommitted** edits and resets the file to
the last commit. That's the everyday AI-undo. (Returning to an *older* commit, reverting a merge, and
the reflog are recovery topics with their own module (Module 12) once you've got remotes and PRs to
make them meaningful. Here we only need "undo back to my last checkpoint.")

### Reframe 2: The repo is durable memory the AI can read

This is the part most people miss, and it directly fixes Module 1's *second* seam.

An AI session is ephemeral. Close the tab and the agent's working context is gone. It cannot
remember yesterday. But here's the thing: **the changes on disk aren't gone.** And Git turns the
disk into a structured, queryable record of exactly what happened and what's in flight. A fresh
session (a brand-new chat, or tomorrow's agent that's never seen this project) can answer "where
were we?" entirely from ground truth by reading Git:

| Command | What it tells a cold session |
|---------|------------------------------|
| `git status` | What's changed but **not yet committed**, including brand-new files Git isn't tracking yet. The "in-flight, unsaved" picture. |
| `git diff` | The **actual line-level edits** sitting uncommitted. Not a summary; the real changes. |
| `git log --oneline` | What's already **committed and settled**: the project's decision history. |
| `git log main..HEAD` + the ahead/behind line in `git status` | How this branch compares to `main` and to the remote: the **not-yet-shared** work. (Fully meaningful once you have branches and a remote, Modules 6 and 8, but the habit starts here.) |

Together those cover every state a change can be in: **untracked, uncommitted, committed, and
not-yet-pushed.** That's the entire surface area of "what's going on in this project," and a fresh
agent can read all of it in one pass, with no chat history required and no re-explaining yesterday.

This reframes the whole point of committing. You're not just saving your work; you're **writing the
project's memory in a form the next AI session can read.** The chat forgets. The repo remembers.

### Why this makes "commit often" non-negotiable

Put the two reframes together and the discipline falls out on its own:

- The more granular your commits, the **smaller the blast radius** when the AI makes a mess: you
  restore to a checkpoint ten minutes back, not yesterday.
- The more granular your commits, the **cleaner the reconstruction**: `git log` reads like a
  decision journal instead of one giant "stuff" commit.

Commit at every working state. Treat it as the autosave you control. "It runs and does what I
expect" is a good enough reason to commit.

---

## The AI angle

Everything above is standard Git. What's *specific* to AI-assisted work:

- **The AI raises the value of undo.** You're making more changes, faster, with more confidence
  (yours and the model's), and confidence is exactly what precedes a quiet mistake. The frequency of
  "wait, undo that" goes *up* with AI, so cheap, reliable undo matters more, not less.
- **The AI has no memory; the repo is the memory you give it.** This is the habit that pays off most
  across the course. When you start a session with *"read `git log`, `git status`, and `git diff`,
  then tell me where we are,"* you've replaced "re-explain the project from memory" with "read the
  ground truth." Agents are *good* at this; reading state is what they're best at.
- **AI changes are reviewable as diffs.** `git diff` turns "the AI rewrote my file" into a precise,
  line-by-line account of what it actually did. That's the foundation the review skill (Module 10) is
  built on, and it starts here.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/02-version-control-as-a-safety-net/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 2"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Git commands), on the `tasks-app` project from Module 1.

**You'll need:** Git installed (`git --version`; if it's missing, install from
[git-scm.com](https://git-scm.com) or your package manager), the `tasks-app` folder from Module 1,
and your AI assistant.

> **How you work with the AI in this lab: still the browser.** You haven't moved the AI into your
> editor yet; that's **Module 4** ("Getting the AI Out of the Browser"), and it comes *after* this
> one on purpose. The whole point of this module is to install the safety net **first**: you only
> let an AI edit your real files directly once you can see and revert exactly what it did. So for now,
> keep doing what you did in Module 1: **ask in your browser chat, then copy the result into the
> file yourself.** Every time you read "ask your AI" below, that means: paste the relevant file(s)
> into your chat, ask for the change, and paste the result back. Yes, it's the copy-paste loop from
> Module 1, and that friction is exactly what Module 4 removes. You'll appreciate it more for having
> felt it one more time with a net underneath you.

### Part A: First checkpoint

1. In your project folder, initialize the repo and make the first commit:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   git init -b main           # start the repo with its first branch named "main" (Git 2.28+)
   git status                 # everything shows as "untracked"; Git sees the files but isn't saving them yet
   ```

   > **Why `-b main`, and what if your Git is older.** Stock Git still names the first branch
   > `master`, but every later module in this course says `main` (you'll `git switch main`, compare
   > `git log main..HEAD`, merge into `main`). `git init -b main` settles that name once so those
   > commands resolve. The `-b` flag needs Git 2.28+ (`git --version` to check); on an older Git, run
   > plain `git init`, finish the first commit in step 2, then rename the branch once with
   > `git branch -m master main`. Either route leaves you on `main`.

2. Add a `.gitignore` so you don't version generated junk. Copy this module's
   `lab/gitignore-starter` to a file named exactly `.gitignore` in the project root, then:

   ```bash
   git status                 # tasks.json and __pycache__ should no longer appear
   git add .
   git commit -m "Initial commit: tasks app from Module 1"
   git log --oneline          # one checkpoint exists now
   ```

   **You now have a net.** Everything after this is recoverable.

### Part B: A change you can see and trust

3. Get `cli.py` in front of your AI first. The browser chat can't see your disk, so you have to hand
   it the file: run `cat cli.py` and copy the output, or copy the contents straight from your editor.
   Paste that into the chat, then ask for a small feature, e.g. *"add a `count` command to `cli.py`
   that prints how many tasks are pending."* Paste the AI's version back over `cli.py`.

4. **Before committing, read the diff:**

   ```bash
   git diff
   ```

   This is the habit that replaces "paste it back and hope." You're reading exactly what changed,
   nothing more, nothing less. Confirm it does what you asked and didn't touch anything it shouldn't.
   Run it (`python3 cli.py count`), then commit:

   ```bash
   git add .
   git commit -m "Add count command"
   ```

### Part C: Recover from a mess (the whole point)

5. Now let the AI make a mess on purpose. Ask it to *"aggressively refactor `tasks.py`"* and paste
   the result over your file **without reading it**. Run the app. Maybe it's broken, maybe it's
   subtly wrong, maybe it's fine but unrecognizable. Doesn't matter.

6. Decide you don't want it. Undo it completely:

   ```bash
   git status                 # shows tasks.py as modified
   git restore tasks.py       # discard the change; back to your last commit, byte for byte
   git diff                   # empty: nothing changed. you're clean.
   python3 cli.py list         # works again
   ```

   You just recovered from a bad AI change in one command, with zero retyping and zero guesswork.
   *This is the safety net.* Internalize how cheap that just was; that cheapness is what lets you say
   yes to riskier AI work for the rest of the course.

### Part D: The repo as the AI's memory

7. Make one more committed change and one *uncommitted* change, so the project has real state:

   ```bash
   # (with the AI) add a "help" command, then:
   git add . && git commit -m "Add help command"
   # (with the AI) start a "delete <index>" command but DON'T commit it; leave it modified
   ```

8. Open a **brand-new AI chat** (or clear the context). Paste it nothing about the project. Instead,
   run these and paste the *output* into the chat:

   ```bash
   git log --oneline
   git status
   git diff
   ```

   Then ask: *"Based only on this Git output, tell me where this project is: what's settled, what's
   in progress, and what I should do next."*

   Watch a session that has never seen your project reconstruct its exact state: settled history
   from `log`, in-flight work from `status`/`diff`, with no chat history at all. **That's durable
   memory.** Make this your standard way to start a session on any project.

9. Close the loop and leave the repo clean. The cold session just told you what's in progress and
   what to do next: finish the `delete <index>` command. Do that with the AI (paste in `cli.py` the
   same way as Part B), run it to confirm it works (`python3 cli.py delete 1`), then commit:

   ```bash
   git add .
   git commit -m "Add delete command"
   git status                 # "nothing to commit, working tree clean"
   ```

   No dangling uncommitted work follows you into Module 3.

---

## Where it breaks

The backup-and-recovery thread starts here, and so does the honesty about its limits. (It's picked
up again in Module 8 for the *backup* half and Module 12 for the *recovery* half.)

- **Git only sees what was written to disk.** This is the one limit to teach yourself hard. If the
  AI reasoned brilliantly about an approach in the conversation but you never wrote it to a file, it
  is *gone* with the session. Git can't recover what was never on disk. The repo is ground truth,
  but only for things that became files. (This is also the practical argument for committing often:
  the more you write down, the less lives only in ephemeral context.)
- **A single local repo is not a backup.** Everything in this module lives on one disk. Drop the
  laptop in a lake and it's all gone, history included. Git gives you *recovery* (move between
  checkpoints); it does not yet give you *backup* (an offsite copy). That's Module 8's job, and we'll
  be just as honest there about where the analogy holds.
- **`git restore` is a loaded gun pointed at uncommitted work.** It discards changes permanently.
  That's exactly what you want for "throw away the AI's mess," but run it on edits you actually wanted
  and they're gone. The defense is the same habit: commit often, so "uncommitted" is always a small
  window.

---

## Check for understanding

**You're done when:**

- Your `tasks-app` is a Git repo with several commits, and `git log --oneline` reads like a sensible
  history of what you did.
- You have personally restored a file after a bad change and watched `git diff` go empty.
- You've had a fresh AI session correctly describe your project's state from Git output alone.
- You can explain the one thing Git can't recover (anything never written to disk) and why that
  argues for committing often.

When undo feels free and starting a cold session feels like "just read the repo," you've got the
safety net. Module 3 puts it to work on the lowest-risk possible target (documents, not code)
before Module 4 lets the AI edit your files directly.
