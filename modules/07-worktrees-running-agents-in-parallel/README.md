# Module 7: Worktrees for Running Agents in Parallel

> **A branch lets one agent try something risky. A worktree lets two agents try two things at the
> same wall-clock time, in separate folders, on separate branches, without touching each other's
> files.** This is the move that turns "I run an agent" into "I run agents."

---

## Prerequisites

- **Module 1: the `tasks-app`.** The running example continues here.
- **Module 2: Version control.** The `tasks-app` is already a Git repo with commits, and you read
  a project's state from `git status` / `git diff` / `git log`. Each worktree has its own answer to
  those, which is the whole point.
- **Module 4: Getting the AI out of the browser.** The agents in this module edit real files in a
  folder. You'll point an editor-integrated AI session at each worktree directory.
- **Module 6: Branches.** You can create a branch, switch to it, merge it back, and resolve a
  conflict. A worktree is the physical counterpart to the logical isolation a branch already gives
  you, so this module makes no sense without it.

If you parachuted in: you minimally need a Git repo with at least one commit and a working
understanding of branches.

---

## Learning objectives

By the end of this module you can:

1. Explain why a single working directory is the bottleneck the moment you want two agents running
   at once, and why branches alone don't fix it.
2. Create, list, and remove linked worktrees (`git worktree add` / `list` / `remove`), each on its
   own branch.
3. Run two independent AI edit sessions on the same project simultaneously without them colliding on
   files, branches, or app state.
4. Merge parallel work back to `main` and clean up worktrees without leaving stale state behind.
5. State precisely what worktrees share (history/objects) and what they don't (working files,
   uncommitted changes, checked-out branch), and where that bites.

---

## Key concepts

### Where branches alone run out

Module 6 gave you branches: spin one up, let the agent do something wild, keep it or throw it away
with zero risk to `main`. That's logical isolation: two lines of history that don't affect each
other.

But there's a physical fact branches don't change: **a repo has exactly one working directory, and
only one branch can be checked out in it at a time.** The files on disk are *the* files. When you
`git switch other-branch`, Git rewrites those same files in place to match the other branch. There's
one floor, and switching branches yanks it out and lays a different one down.

That's fine when *you* are the only one standing on the floor. It falls apart the instant you want
two things happening at once. Watch it break:

```bash
# Agent A added a `wipe` command and committed it on its own branch:
git switch -c feature/wipe
# ...agent A edits the usage line in cli.py to add `wipe`...
git commit -am "Add wipe command"

# You start Agent B on a fresh branch off main; it begins editing the SAME
# usage line to add `remaining`, and hasn't committed:
git switch main
git switch -c feature/remaining
# ...agent B edits cli.py, hasn't committed...

# You try to hop the working directory back to Agent A's branch to check on it:
git switch feature/wipe
# error: Your local changes to the following files would be overwritten by checkout:
#   cli.py
# Please commit your changes or stash them before you switch branches.
```

Git stops you, and correctly so. Switching to `feature/wipe` would overwrite Agent B's uncommitted edits
to `cli.py` with Agent A's committed version of those same lines, so Git refuses rather than silently
destroy the work. But now you're stuck choosing between bad options:

- **Commit half-finished work** just to get it out of the way (pollutes history, and Agent B's
  `remaining` command isn't done).
- **Stash it** (now Agent B's context lives in a stash you have to remember to pop, and Agent B, a
  long-running session that thinks its files are right there, is now editing files that silently
  changed under it).
- **Run both agents on the same branch in the same folder**, and watch them overwrite each other's
  edits, because they're both writing the same `cli.py` with no idea the other exists.

The branch was never the problem. The single working directory is. You need two floors.

### What a worktree is

`git worktree` gives you exactly that: **additional working directories attached to the same
repository, each with its own checked-out branch.** One repo, many checkouts.

```bash
$ cd ~/ai-workflow-course/tasks-app          # your existing repo from Module 2
$ git worktree add ../tasks-app-remaining -b feature/remaining
Preparing worktree (new branch 'feature/remaining')
HEAD is now at a1b2c3d Add done command
```

That command creates a brand-new folder, `~/ai-workflow-course/tasks-app-remaining`, containing a full
checkout of your project on a new branch `feature/remaining`. Your original folder is untouched,
still on its own branch. You now have two real directories you can `cd` into, edit, and run
independently:

```
~/ai-workflow-course/
  tasks-app/             ← the "main" worktree, on (say) main
  tasks-app-remaining/   ← a "linked" worktree, on feature/remaining
```

Both are backed by **one** repository. There is a single `.git`: a single object store, a single
history, a single set of branches and tags. The linked worktree doesn't get its own copy of the
history; it gets its own copy of the *files*, and a pointer back to the shared `.git`. (If you peek,
the linked worktree has a tiny `.git` *file*, not a directory; it just points at the real one in
the main worktree.)

This is the distinction that makes the whole thing click:

> **A clone copies the history. A worktree copies the working files and shares the history.**

A clone is a second repository: separate objects, separate `.git`, you sync between them with
pull/push (Module 8). A worktree is one repository checked out in two places. A commit you make in
one worktree is instantly an object in the shared store. No pushing, no pulling; it's just *there*,
because there's only one store.

### The mental model: one history, many present moments

Think of the shared object store as the project's single, settled past: every commit, on every
branch, in one place. Each worktree is a different *present moment* checked out of that past: this
folder is "the project as of `feature/remaining`," that folder is "the project as of `main`." They all
write to the same past (commits go to the shared store), but each lives in its own present (its own
files on disk).

That's why worktrees are the natural payoff of branches. A branch is a *logical* "what if." A
worktree makes that "what if" a *place you can stand*: a folder you can open, run, and point an
agent at, while every other "what if" stays open in its own folder at the same time.

### The core commands

```bash
git worktree add <path> -b <new-branch>   # new folder + new branch, checked out there
git worktree add <path> <existing-branch> # new folder, checks out an existing branch
git worktree list                         # every worktree, its path, and its branch
git worktree remove <path>                # delete a worktree (must be clean, or use --force)
git worktree prune                        # forget worktrees whose folders were deleted by hand
```

`git worktree list` is your map:

```bash
$ git worktree list
~/ai-workflow-course/tasks-app             a1b2c3d [main]
~/ai-workflow-course/tasks-app-remaining   d4e5f6a [feature/remaining]
~/ai-workflow-course/tasks-app-wipe        7g8h9i0 [feature/wipe]
```

Three folders, one repo, three branches checked out simultaneously. No stashing, no switching, no
collisions.

### How this maps onto running multiple agents

Here's the payoff the module exists for. An AI agent isn't a quick command; it's a **long-running
session that holds a working directory and usually a running process** (your app, your test runner,
a watcher). Two such sessions in one folder is a guaranteed mess:

- They edit the same files; their changes interleave and clobber each other.
- One commits or switches branches and the floor moves under the other.
- Their app runs and test runs share state and step on each other's output.

Give each agent its own worktree and every one of those collisions disappears *by construction*:

- **Separate folders** → separate files. Agent A literally cannot touch Agent B's `cli.py`; it's a
  different file on disk.
- **Separate branches** → separate history lines. Neither can move the other's branch.
- **Shared object store** → when both finish, merging their work back together is trivial; it's all
  already in one repo. No syncing between copies.

So "run two agents at once" stops being a coordination nightmare and becomes "open two folders."
That's the local foundation; **doing this at scale (many agents, split work, kept reviewable) is
Module 26 (Orchestrating Multiple Agents).** Worktrees are the primitive that module is built on.
Learn the primitive here on two; the orchestration comes later.

---

## The AI angle

Worktrees look like a niche convenience: a way to dodge `git stash` when you switch branches. For
AI-assisted work they're closer to essential, for a reason specific to how agents behave:

- **An agent assumes its working directory is stable.** It reads files, reasons about them, and
  writes them back over a session that can run for many minutes. If a *second* agent (or you,
  switching branches) rewrites those files underneath it, the first agent is now operating on a
  reality that silently changed. That's the worst kind of bug, because nothing errors; the work just
  comes out wrong. A worktree pins each agent to a directory nobody else will touch.
- **Parallelism is the whole point of cheap agents.** The model is fast and you can run several at
  once: a feature here, a bugfix there, a doc update in a third. The constraint was never the
  model; it was that they'd trip over one repo. Worktrees remove the constraint.
- **Each worktree is its own durable memory (Module 2).** A fresh agent dropped into
  `tasks-app-remaining` reads `git status` / `git diff` / `git log` and gets *that branch's* ground
  truth, not a blur of three agents' half-finished work. Per-agent isolation makes per-agent
  "where were we?" actually answerable.
- **It keeps parallel AI output reviewable.** Each agent's work lands as its own branch with its own
  clean history, instead of a tangle of interleaved edits on one branch that no human could ever
  review. That reviewability is what later lets agents run with less supervision (Unit 5).

You don't reach for worktrees because you read about them. You reach for them the first time you try
to run two agents and watch them overwrite each other's work.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/07-worktrees-running-agents-in-parallel/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 7"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Git commands), plus two AI edit sessions on the `tasks-app`.

In this lab you'll run **two AI sessions at the same time** on the same project (one adding a
`wipe` command, one adding a `remaining` command), each in its own worktree, and watch them *not*
collide. Then you'll merge both back and clean up. (We use two commands your carried-forward
`tasks-app` doesn't have yet, so neither agent re-adds something that already exists: the lesson is
the parallel isolation, not the commands.)

**You'll need:**

- The `tasks-app` Git repo from Module 2 (initialized, with a few commits). If you skipped ahead,
  run `git init -b main` and make one commit first; the `-b main` matches Module 2, so the
  `git switch main` steps below resolve.
- Git 2.5 or newer (worktrees landed in 2.5; any modern Git is fine, run `git --version` to check).
- **Two** editor-integrated AI sessions you can run at once (Module 4): two editor windows, or two
  terminal AI sessions. If you only have a browser chat, you can still do the lab; just treat each
  worktree folder as a separate copy-paste context.
- The starter scripts and prompts in this module's `lab/` folder, at
  `~/ai-workflow-course/modules/07-worktrees-running-agents-in-parallel/lab/`. As established in
  Module 4, the course's lab scripts live in the course repo while `tasks-app` is a separate folder.
  Here the worktree git is the **AI's** job (the Module 4 pivot): you direct the coordinating session
  to run the `git worktree` commands, or hand it `setup-worktrees.sh` / `cleanup-worktrees.sh` to
  run, and you verify the result. You don't type the git by hand.

### Part A: Feel the collision (1 minute)

Before fixing it, reproduce the bottleneck from "Where branches alone run out." The wall only appears
when both branches touch the **same line** of `cli.py` (one committed, one not), so we make each
branch edit the usage line. (The `sed … > tmp && mv` is just a portable, copy-pasteable stand-in for
the edit an agent would make.) In your `tasks-app`:

```bash
cd ~/ai-workflow-course/tasks-app

# Agent A's branch: add `wipe` to the usage line and commit it.
git switch -c feature/wipe
sed 's/done <index>/done <index> | wipe/' cli.py > cli.tmp && mv cli.tmp cli.py
git commit -am "Add wipe command (demo)"

# Agent B's branch, off main: start adding `remaining` to the SAME line; leave it uncommitted.
git switch main
git switch -c feature/remaining
sed 's/done <index>/done <index> | remaining/' cli.py > cli.tmp && mv cli.tmp cli.py

# Try to hop the working directory back to Agent A's branch:
git switch feature/wipe
# error: Your local changes to the following files would be overwritten by checkout:
#   cli.py
# Please commit your changes or stash them before you switch branches.
```

(The `sed` matches `done <index>`, which is still in your usage line no matter how many commands
you've added since Module 1, and inserts a new one right after it, so both branches edit the same
line.) Git refuses: moving the one working directory to `feature/wipe` would overwrite Agent B's
uncommitted edit with `feature/wipe`'s committed version of that line. *That* is the wall: one
directory can't hold two agents' in-progress work at once. These two branches existed only to feel
the collision, so clean them up before continuing:

```bash
git restore cli.py                              # drop Agent B's uncommitted edit
git switch main
git branch -D feature/wipe feature/remaining    # throw away the demo branches
```

### Part B: Create two worktrees

An agent that lives *inside* a worktree can't create its own worktree, so the **coordinating
session** (the AI you already have pointed at `tasks-app` from Module 4) sets them up. That's Claude
Code in this example; sub your own agent. Tell it:

> *"From the `tasks-app` repo, create two linked worktrees as siblings of this folder: one at
> `../tasks-app-wipe` on a new branch `feature/wipe`, and one at `../tasks-app-remaining` on a new
> branch `feature/remaining`. Then show me `git worktree list`."*

It runs the `git worktree add` calls for you. (If you'd rather it run a script than type the commands,
hand it `lab/setup-worktrees.sh`, which does exactly this.) Then **verify** by hand:

```bash
cd ~/ai-workflow-course/tasks-app
git worktree list      # should show main + feature/wipe + feature/remaining
```

Three folders backed by one repo, and you didn't type a git command. You directed, the agent did the
git, you confirmed.

### Part C: Run two AI sessions in parallel

This is the part to actually *do simultaneously*, not one then the other.

1. Open `~/ai-workflow-course/tasks-app-wipe` in one editor/AI session. Give it the prompt in
   `lab/agent-a-prompt.md`: *add a `wipe` command that removes all tasks.*
2. Open `~/ai-workflow-course/tasks-app-remaining` in a **second** editor/AI session. Give it the prompt
   in `lab/agent-b-prompt.md`: *add a `remaining` command that prints the number of pending tasks.*
3. Let both work at the same time. While they run, prove the isolation from a third terminal, but
   use commands that **already exist**. (`wipe` and `remaining` don't yet; the agents are still
   writing them.) Give each worktree its own task and list it:

   ```bash
   cd ~/ai-workflow-course/tasks-app-wipe && python3 cli.py add "from worktree A" && python3 cli.py list
   cd ~/ai-workflow-course/tasks-app-remaining && python3 cli.py add "from worktree B" && python3 cli.py list
   ```

   Each `list` shows only its own task: worktree A never sees "from worktree B" and vice versa. Each
   worktree has its **own** `tasks.json` (gitignored runtime state, not shared history), so the two
   running apps don't even share data. Separate files, separate state, while both agents work.

4. Review each agent's diff, then have **that worktree's own session** commit its work on its branch.
   In the `tasks-app-wipe` session, read the diff and tell the agent:

   > *"The diff looks right. Commit this on the branch with the message 'Add wipe command'."*

   Do the same in the `tasks-app-remaining` session (message 'Add remaining command'). Each agent
   stages and commits its own work; you verify each landed and left a clean tree:

   ```bash
   cd ~/ai-workflow-course/tasks-app-wipe && git status && git log --oneline -1
   cd ~/ai-workflow-course/tasks-app-remaining && git status && git log --oneline -1
   ```

   Two agents, two commits, two branches, and neither ever saw the other's files.

5. *Now* the new commands exist: run each in its own worktree to watch it work:

   ```bash
   cd ~/ai-workflow-course/tasks-app-wipe && python3 cli.py wipe        # agent A's new command
   cd ~/ai-workflow-course/tasks-app-remaining && python3 cli.py remaining   # agent B's new command
   ```

   `remaining` counts a single pending task, the one you added to worktree B in step 3, because B's
   `tasks.json` is the only state it can see.

### Part D: Merge back and clean up

Both feature branches need to come home to `main`. Back in the **coordinating session** (the one on
`tasks-app`), direct the merges:

> *"On the `tasks-app` repo: switch to `main`, then merge `feature/wipe` and `feature/remaining` into
> it."*

Both commits are already in the shared object store, so there's nothing to fetch; the merges are
local and instant. The second merge **may** hit a small conflict in `cli.py` if both agents added
their `elif` branch in the same spot. That's expected, and it's a *merge-time* event, not a
parallel-work collision. When it happens, direct the agent to resolve it with the same conflict skill
from Module 6:

> *"`cli.py` has a merge conflict. I want the final file to keep BOTH the `wipe` and `remaining`
> commands. Resolve it and complete the merge."*

Then **verify** the result before you trust it, the same way you did in Module 6:

```bash
cd ~/ai-workflow-course/tasks-app
git diff                 # no conflict markers remain
python3 cli.py list       # the app still runs
python3 cli.py wipe       # both new commands work
python3 cli.py remaining
```

Now tear down the worktrees. Direct the coordinating session:

> *"Remove the `tasks-app-wipe` and `tasks-app-remaining` worktrees and prune any stale records."*

It runs `git worktree remove` on both folders and `git worktree prune`. (Hand it
`lab/cleanup-worktrees.sh` if you'd rather it run the script.) The branches are already merged into
`main`, so the work is safe. **Verify** only the main worktree is left:

```bash
git worktree list        # only the main worktree remains
```

---

## Where it breaks

Worktrees are sharp tools. The honest caveats:

- **You cannot check out the same branch in two worktrees.** Git refuses
  (`fatal: 'main' is already checked out at ...`). This is a feature, not a bug; it's exactly what
  stops two agents from writing the same branch, but it surprises people. One branch, one worktree.
- **Uncommitted work is *not* shared.** Only commits go to the shared store. The edits sitting
  modified-but-uncommitted in `tasks-app-remaining` exist *only* in that folder. If you
  `git worktree remove` a dirty worktree, Git refuses unless you pass `--force`, and `--force`
  throws that uncommitted work away for good. Commit before you remove.
- **Cleanup is a two-part chore.** Deleting a worktree folder with `rm -rf` does *not* tell Git it's
  gone; you'll have a stale entry in `git worktree list` forever until you run `git worktree prune`.
  Prefer `git worktree remove <path>`, which does both. (The cleanup script does this for you.)
- **One shared object store means one shared fate.** All worktrees depend on the main repo's `.git`.
  Delete or move the main worktree and every linked worktree breaks; they're pointing at a `.git`
  that isn't there anymore. Worktrees are *not* independent backups; they're one repository. (The
  backup story is still Module 8: get the history off this one machine.)
- **Worktrees don't prevent merge conflicts; they defer them.** Two agents editing the same lines
  will still conflict *when you merge*. What worktrees buy you is that the conflict happens once, on
  your terms, in one calm step (Module 6), instead of two live agents corrupting each other's files
  in real time. Isolation during work; resolution after.
- **Each worktree is a full set of working files.** Cheaper than a clone (the history is shared), but
  not free: a worktree per agent means a working tree per agent on disk, plus whatever each agent's
  running process consumes. Fine for two; something to plan for when Module 26 takes this to many.
- **Tooling that hardcodes the repo root can get confused.** Anything keyed to an absolute path, a
  per-checkout cache, or "the one working directory" may need per-worktree setup. The committed AI
  config from Module 5 travels with each worktree (it's a tracked file), which is exactly why
  committing it pays off here: every agent in every worktree inherits the same instructions.

---

## Check for understanding

**You're done when:**

- `git worktree list` showed three entries at once, and you ran the `tasks-app` from two different
  worktree folders, adding a different task in each and watching each keep its own `tasks.json`.
- You ran two AI sessions in parallel, each in its own worktree on its own branch, and confirmed
  neither touched the other's files (different folders, different `tasks.json`, different branch).
- You merged both feature branches back into `main` (resolving a conflict if one appeared) and the
  app has both new commands.
- You cleaned up so that `git worktree list` shows only the main worktree and the stray folders are
  gone, with no stale entries left behind.
- You can state, without looking, what a worktree shares with the repo (history, objects, branches,
  tags) and what it keeps to itself (working files, uncommitted changes, its one checked-out branch).

When "run two agents at once" feels like "open two folders" instead of "orchestrate a stash dance,"
you've got it. This is the primitive Module 26 scales up; for now, two is plenty.
