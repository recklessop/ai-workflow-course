# Module 11: Collaboration: Humans and Agents on One Repo

> **You now have every piece: issues, branches, PRs, review. This module wires them into one loop,
> and points out that half your "teammates" might not be human.** Once the loop runs the same way no
> matter who's pulling the work, an agent is just another contributor who needs a branch.

---

## Prerequisites

This is the synthesis module for Unit 2's collaboration arc. It assumes the whole chain up to here:

- **Module 2:** commits as checkpoints, and `git diff`/`git log` as the record everyone reads.
- **Module 6:** branches as isolated sandboxes; you make changes off `main`, not on it.
- **Module 7:** worktrees, so more than one branch (and more than one agent) can be live at once
  without stepping on each other.
- **Module 8:** a remote on a git host (GitHub the default; a self-hosted forge if you took that
  track), so there's a shared copy to collaborate around.
- **Module 9:** issues: the task layer that says *what* needs doing and *who* (human or agent) owns it.
- **Module 10:** pull/merge requests and the skill of reviewing a diff you didn't write.

Each of those taught one move. This module is the assembled motion. If you're missing one, the loop
still works, but a step will feel like a black box, so go back and fill it in.

---

## Learning objectives

By the end of this module you can:

1. Run the full collaboration loop end to end (issue → branch → implementation → PR → review →
   merge → issue auto-closed) and explain why each step exists.
2. Link a PR to an issue so the merge closes the issue automatically, and explain when that does and
   doesn't fire.
3. Decide correctly between a **branch** and a **fork** based on whether you have push access.
4. Reason about **who's allowed to push**: roles, protected branches, and why "never commit to
   `main`" stops being a personal habit and becomes an enforced rule.
5. Treat an agent as a contributor (give it a branch, route an issue to it, review its PR on the
   same gate you'd use for a human) and know where a human has to stay in the loop.

---

## Key concepts

### Two loops, not one

Module 2 gave you the **inner loop**: edit, `git diff`, commit, repeat. That loop lives on your disk
and is yours alone. It's how *you* (or your agent) make progress in a working session.

This module is the **outer loop**, the one the *team* sees:

```
issue  →  branch  →  implementation  →  pull request  →  review  →  merge  →  issue closed
 (M9)     (M6)        (inner loop, M2)      (M10)         (M10)              (this module)
```

Everything you learned was a single station on this track. The reason to assemble them now, rather
than keep treating issues, branches, and PRs as separate skills, is that the *handoffs between
stations* are where collaboration actually happens, and where it breaks. The issue says what to do.
The branch isolates the attempt. The PR makes the attempt reviewable. The review is the judgment.
The merge is the commitment. Closing the issue is the receipt. Skip a handoff and you get the
failure modes every team knows: work nobody asked for, changes that land straight on `main` with no
review, "done" issues for work that was never actually done.

The loop is worth internalizing as a loop because **it's the same loop regardless of who's doing the
work**, and increasingly some of the workers are agents. Hold that thought; it's the whole point of
the module, and we'll come back to it.

### The loop, step by step

**1. The issue (Module 9) is the contract.** Before any code, there's a statement of intent: a
title, a description of the desired behavior, maybe acceptance criteria. It has a number (`#42`) that
the rest of the loop will reference. The issue exists so that "what we're doing and why" lives
somewhere durable and shared, not in one person's head or one chat session that'll evaporate
(Module 1, Seam 2). Assign it to whoever's taking it: a person, or an agent.

**2. The branch (Module 6) is the workspace.** You never implement on `main`. You cut a branch
named for the work. Convention is something traceable like `42-clear-done-command` (the issue
number plus a slug). The name matters more than it looks: months later, `git branch` and the host's
branch list become a map of "what's in flight," and the issue number ties each branch back to its
contract.

```bash
git switch -c 42-clear-done-command   # branch off main and switch to it
# Switched to a new branch '42-clear-done-command'
```

**3. Implementation is the inner loop (Module 2).** This is where the actual editing happens:
you, or an agent, making commits on the branch. Nothing here is new; it's the edit/diff/commit
rhythm you already have. The branch keeps it isolated, so however bold the change, `main` is
untouched until the loop says otherwise.

```bash
git push -u origin 42-clear-done-command   # publish the branch so others (and the host) can see it
# branch '42-clear-done-command' set up to track 'origin/42-clear-done-command'.
```

**4. The pull request (Module 10) makes it reviewable.** Opening a PR says "this branch is ready
to be considered for `main`." It bundles the diff, a description, and a discussion thread into one
reviewable unit. Crucially, **this is where you link back to the issue** (next section) so the loop
can close itself.

**5. Review (Module 10) is the judgment gate.** Someone who isn't the author reads the diff for
correctness *and plausibility*, the skill Module 10 is built around. They approve, request changes,
or comment. For AI-generated diffs this gate is doing more work than it used to: the code compiles,
reads cleanly, and is still wrong in a way only review catches.

**6. Merge is the commitment.** Approved, the PR merges into `main`. Hosts offer a couple of merge
styles, a squash or a merge commit; your team picks one and the effect is the same: the branch's work
is now part of the shared trunk. (You'll also see a *rebase-merge* option; it rewrites history and is
out of scope here.) Delete the branch after; its job is done and its name lives on in the merge.

**7. The issue closes, ideally by itself.** If you linked the PR correctly, merging closes the
issue automatically. The receipt is written without anyone touching the issue. That's the satisfying
*click* of the whole loop landing, and it's the concrete thing the lab makes you feel.

### Linking the PR to the issue (the auto-close)

The mechanic that makes step 7 free: put a **closing keyword** in the PR description. Most hosts
(GitHub, GitLab, Gitea/Forgejo, Bitbucket) recognize a common set:

```
Closes #42
```

`Closes`, `Fixes`, and `Resolves` (and their variants `close/closed`, `fix/fixed`,
`resolve/resolved`) all work on the major hosts. When the PR merges **into the default branch**, the
host closes the referenced issue and cross-links the two so each shows the other. One line in the PR
body buys you a self-closing loop and a permanent trail from "why we did this" (issue) to "what we
did" (PR/diff) to "when it landed" (merge).

A plain mention without a keyword, just `#42`, *links* the two but does **not** close on merge.
That's useful too (for "related to" references), but know the difference: the keyword is load-bearing.

> **The trail is the point.** Six months later, someone (possibly an agent reading the repo as
> durable memory, Module 2) asks "why does `clear-done` exist?" The answer is one click away:
> issue → PR → diff → merge. You built that trail for free by linking one line.

### Branch vs. fork: it comes down to push access

There are two ways a contributor gets their work in front of the team, and the deciding question is
simple: **can you push to the repo?**

- **You have push (write) access → branch in the repo.** This is the normal case for a team working
  on a shared repo, and everything above assumes it. Your branch lives alongside everyone else's on
  the same remote; PRs go branch → `main` within one repo.
- **You don't have push access → fork, then PR from the fork.** This is the open-source contribution
  model and the "outside contributor" case. You clone the repo into your *own* copy (a fork), push
  branches there, and open a PR *across repos* from `your-fork:branch` into `upstream:main`. The
  maintainers review and merge; you never needed write access to their repo.

```bash
# Forked-contributor flow (no push access to upstream):
#   1. Fork upstream/repo  ->  you-now-own you/repo   (one click on the host)
#   2. git clone https://host/you/repo
#   3. git switch -c my-fix ; ...commit...
#   4. git push -u origin my-fix         # origin = your fork, which you CAN push to
#   5. Open a PR from you/repo:my-fix  ->  upstream/repo:main
```

For this audience, working mostly on repos you control, **branches are the default and forks are the
exception**: you reach for a fork when contributing to something you don't own. The relevance to AI
work: an agent you run on your own repo branches like any teammate. An agent contributing to a
project it doesn't own forks like any outside contributor. The rule doesn't change for machines.

### Who's allowed to push

"Never commit directly to `main`" started as a personal discipline. On a shared repo it becomes an
*enforced* rule, and that enforcement is the other half of collaboration nobody mentions until it
bites.

**Roles.** Hosts assign access in tiers, typically read (clone, comment), then write/develop (push
branches, open PRs), then maintain/admin (manage settings, force-merge, change protections). A
contributor only needs *write* to do the whole loop above; admin is for the people running the repo.
Give out the least that lets someone do their job, the same least-privilege instinct you already
have for production systems.

**Protected branches.** This is the enforcement mechanism. You mark `main` (and any other shared
branch) as protected, and the host then *refuses* direct pushes to it. The only way in is a PR. You
can layer rules on top:

- **Require a pull request:** no direct pushes, full stop. The loop is mandatory, not optional.
- **Require a review approval:** at least one non-author approval before merge is allowed.
- **Restrict who can merge:** only certain roles can click the button.

Turning these on converts "we agreed not to push to `main`" into "the server won't let you." For a
solo learner this can feel like bureaucracy, but it's exactly the guardrail that makes it safe to add
contributors you trust *less than fully*, including machine ones. (Required **status checks**,
"CI must pass before merge", are the same protected-branch feature, but they need CI to exist first;
that's Module 14. We'll come back and switch it on there.)

### The contributor who isn't human

Here's the synthesis the whole unit was building toward. Re-read the loop (issue, branch,
implementation, PR, review, merge) and notice that **nothing in it specifies that the contributor is
a person.** That's not an accident; it's the most useful property of the whole system right now.

- **An agent is a contributor with a branch.** You hand an agent an issue (Module 9 already framed
  assignees as a mix of humans and agents). It cuts a branch, implements, and opens a PR, exactly
  the loop above. A human reviews that PR on the same gate used for any teammate (Module 10). The
  agent never touches `main`; the protected-branch rules and the review gate apply to it identically.
  This is *why* the loop is worth assembling as a loop: it's the harness that lets you accept work
  from a contributor whose judgment you don't fully trust yet.

- **Two agents in parallel are just two contributors needing branches.** The moment you run more than
  one agent at once, you have the classic collaboration problem: two workers who must not edit the
  same files in the same working directory. That's not a new problem, and it already has an answer:
  **worktrees (Module 7).** Each agent gets its own working directory and its own branch; they work
  simultaneously, each opens its own PR, and you review and merge them independently. Worktrees
  earned their module precisely so this case would already be solved by the time you got here.

- **The merge stays human (for now).** The agent can do every step *up to* merge. The merge, the
  commitment to shared `main`, is where a human stays in the loop, because review is judgment and
  judgment is the thing you haven't delegated yet. Unit 5 is about carefully, conditionally moving
  that line; this module is where you should be able to *picture* an agent doing the first five steps
  while you do the sixth.

The reframe to carry forward: **collaboration tooling was never really about humans.** It's about
coordinating *contributors*: isolating their work, making it reviewable, controlling who can commit
it to the trunk. Those guarantees are exactly what you need to safely let an agent contribute, which
is why the team layer you just learned doubles as the agent-safety layer you'll lean on for the rest
of the course.

---

## The AI angle

A generic "intro to team git" lesson ends at "branch, PR, review, merge, congrats, you can work on a
team." This module's reason to exist is that **the team you're coordinating now includes agents, and
the loop is what makes that safe.**

- **The loop is the harness for untrusted contributors, and an agent is one.** Branch isolation,
  the PR boundary, mandatory review, protected `main`: every one of these was designed to let work
  flow from someone whose every change you don't personally vouch for. That's the exact profile of an
  agent. You don't need new tooling to put an agent to work; you need the tooling you just learned,
  pointed at a new kind of contributor.
- **Volume goes up; the gate has to hold.** A human contributor opens a PR a day. An agent can open
  five before lunch. The review gate (Module 10) and the protected-branch rules are what keep that
  volume from landing unreviewed on `main`. The faster your contributors, the more the gate earns its
  keep, the same lesson as Module 1, one layer up.
- **Parallel agents are a solved problem, on purpose.** Two agents at once is just two contributors
  needing isolation: worktrees (Module 7) and separate branches. You already have the answer; this
  module is where you see *why* you were given it.
- **The auto-closing trail is memory for the next session.** Issue → PR → diff → merge is exactly the
  durable, on-disk-and-on-host record a fresh agent reads to reconstruct "why does this exist?"
  (Module 2's durable-memory reframe, now spanning the whole loop). Linking the PR to the issue isn't
  bookkeeping; it's writing the project's memory in a form the next contributor, human or machine,
  can follow.

You're not learning collaboration *and then* learning to work with agents. They're the same skill.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/11-collaboration-humans-and-agents/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 11"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell plus your host's web UI for the issue, PR, review, and merge steps. From
Module 4 on you direct the AI to do the git work and verify the result; the only commands you type by
hand here are read-only checks like `git branch` and `git show`. You'll implement the feature with
Claude Code (sub your own agent) the way Module 4 taught: the agent edits the files directly, you
review the diff.

The goal is to run the **entire outer loop once**, on the `tasks-app`, and watch the issue close
itself on merge. One small feature, all seven stations.

**The feature:** add a `clear-done` command to the CLI that removes every completed task. It's a
deliberately small, two-file change (logic in `tasks.py`, wiring in `cli.py`), small enough that the
loop, not the code, is what you're practicing.

**You'll need:**

- Your `tasks-app` repo from earlier modules (`~/ai-workflow-course/tasks-app`), with a remote on your
  git host (Module 8) that supports issues and PRs.
- Push access to that repo (it's yours, so you have it).
- Claude Code (sub your own agent), your editor-integrated AI from Module 4.
- Your host's CLI (`gh` for GitHub, `glab` for GitLab, `tea` for Gitea/Forgejo). The web UI covers the
  whole human-driven loop (Parts A–D), so there the CLI is just convenience. Part E is the exception:
  for an *agent* to open the PR itself it has to reach the forge, which needs the CLI installed and
  authenticated, or you take the no-CLI fallback that section spells out.

Starter artifacts are in this module's `lab/`: `issue.md` (the issue to file) and `pr-body.md` (the
PR description, including the load-bearing closing keyword).

### Part A: Set the guardrail (one-time)

Before the loop, make `main` enforce what you've been doing by hand. In your host's web UI, open the
repo's branch-protection settings and protect `main` with **"require a pull request before merging."**

Now prove the rule bites. Working in `~/ai-workflow-course/tasks-app`, tell Claude Code to make a
throwaway edit on `main` and push it straight up:

> "On the `main` branch, append a comment line to `README.md`, commit it, and push directly to the
> remote. This is a deliberate test of branch protection."

Watch the push come back **rejected**: the host refuses a direct push to a protected branch. That
refusal is the whole point of Part A. Then have the agent undo the throwaway commit:

> "Good, the host rejected it. Drop that last commit and its changes so we're back to a clean `main`,
> then we'll do this the right way through a PR."

The agent reaches for `git reset --hard HEAD~1` here. That's a sharp, history-rewriting command from a
later module: it drops your most recent commit *and* its changes. It's safe only because that commit
was a throwaway to test the guardrail. Its full treatment and its real dangers are **Module 12**.

If the push went through instead of bouncing, protection isn't on; fix that before continuing. Feeling
the server say *no* is the point: "never commit to `main`" is now a rule, not a resolution.

### Part B: Issue → branch

1. **File the issue.** Create a new issue from `lab/issue.md` (title and body). Note its number; say
   it's `#42`. This is the contract.

2. **Branch for it**, naming the branch after the issue. Tell Claude Code to sync `main` and cut the
   branch:

   > "Sync `main` with the remote, then create and switch to a branch named `42-clear-done-command`
   > (use my issue number)."

   Verify it landed before moving on:

   ```bash
   git branch        # the new 42-clear-done-command branch, marked current with *
   git status        # "On branch 42-clear-done-command", working tree clean
   ```

   The branch-naming convention (issue number plus a short slug) is the thing to get right here, not
   the keystrokes.

### Part C: Implementation (with AI)

3. Point Claude Code at `~/ai-workflow-course/tasks-app` and ask for the feature:

   > "Add a `clear-done` command. In `tasks.py`, add a `TaskList` method that removes all completed
   > tasks. In `cli.py`, wire up a `clear-done` command that calls it, saves, and prints how many
   > were removed. Match the existing style."

4. **Review the diff before you trust it** (the Module 2 habit, the Module 10 skill):

   ```bash
   git diff
   ```

   Confirm it touched only `tasks.py` and `cli.py`, the logic lives in `tasks.py` (not crammed into
   the CLI), and it does what you asked. Run it:

   ```bash
   python3 cli.py add "keeper" ; python3 cli.py add "trash"
   python3 cli.py list                   # note the index shown next to "trash"
   python3 cli.py done <trash-index>     # use the index "list" just printed, NOT a fixed 1
   python3 cli.py clear-done             # expect it to remove the completed one
   python3 cli.py list                   # "keeper" remains, "trash" is gone
   ```

   Read the index off `list` rather than assuming it: `done` is positional, and your `tasks-app` has
   been carrying tasks since Module 1, so "trash" won't reliably land at index 1.

5. **Have the agent commit and push.** Tell Claude Code to stage just the two changed files, commit
   with a message that closes the issue, and publish the branch:

   > "Commit `tasks.py` and `cli.py` with a message like `Add clear-done command (closes #42)` (use my
   > issue number and the closing keyword), then push the branch to the remote."

   Verify before you trust it: the commit staged **only** those two files, and the subject carries the
   closing keyword.

   ```bash
   git show --stat HEAD     # only tasks.py and cli.py listed; subject ends "(closes #42)"
   ```

### Part D: PR → review → merge → auto-close

6. **Open the PR** from your branch into `main`, using `lab/pr-body.md` as the description. Make sure
   the body contains the closing line with **your** issue number:

   ```
   Closes #42
   ```

7. **Review it.** Open the PR's "Files changed" tab and read the diff *as a reviewer*, not as the
   author, the Module 10 move. For the full effect, pretend an agent wrote it (in a moment, one
   will): is the logic where it belongs? Any edge case missed (empty list, nothing done yet)?
   Approve it.

8. **Merge it.** Click merge (your protection rule required the PR and, if you added it, the
   approval). Delete the branch when prompted.

9. **Watch the issue close itself.** Open issue `#42`. It should now be **closed**, with a link to
   the PR that closed it. You didn't touch the issue; the merge did. That click is the whole loop
   landing.

   Now have Claude Code bring the merged work down and tidy up:

   > "Switch to `main`, pull the merged work, and delete the now-merged local branch
   > `42-clear-done-command`."

   Verify the branch is gone:

   ```bash
   git branch        # 42-clear-done-command no longer listed; you're on main
   ```

### Part E: Now make the contributor an agent

Run the loop one more time, but this time **let an agent be the contributor for steps 2–6.** File a
second issue (e.g. "Add a `pending` command that lists only incomplete tasks"; the `TaskList.pending()`
method already exists, so this is wiring only).

**First, a reality check the rest of the lab let you skip.** Two of those steps cross the forge
boundary: the agent has to *read* issue #43 from the forge and *open* a PR back into it. Your Module 4
editor agent only edits files and runs local commands, and `git push` publishes a branch, it does
**not** open a PR. The web UI you've been clicking can't be handed to the agent. So before you prompt,
give the agent a way to reach the forge. Pick one path:

- **Full agent-opens-PR path (host CLI required).** Install and authenticate your host's CLI (`gh`,
  `glab`, or `tea`) so the agent can run, e.g., `gh pr create` itself. For *this* step the CLI is a
  requirement, not the convenience it was in Parts A–D. Then prompt the agent:

  > "Take issue #43. Create a branch named `43-pending-command`, implement the feature, commit
  > referencing the issue with a closing keyword, push the branch, and open a PR into `main` whose
  > description closes #43."

- **No-CLI fallback (you open the PR).** Have the agent do everything local (branch, implement,
  commit, push) and *you* open the PR in the web UI, reusing `lab/pr-body.md` and keeping the
  `Closes #43` line. Prompt it the same way, but stop it at the push:

  > "Take issue #43. Create a branch named `43-pending-command`, implement the feature, commit
  > referencing the issue with a closing keyword, and push the branch. I'll open the PR."

  Wiring an agent *directly* into the forge, so it reads issues and opens PRs with no human hand-off
  and no CLI to shell out to, is what an MCP forge integration buys you in **Module 20**. Here you're
  feeling the exact seam that module closes.

Either way, let the agent drive to the open-PR state. Then **you** are the human at the gate: review
the diff, and merge (or request changes) yourself. You've just watched the exact loop run with a
non-human contributor, and felt precisely where you, the human, stayed in it. If you want the
parallel-agents case, file two issues and run two agents in separate worktrees (Module 7), each on its
own branch.

---

## Where it breaks

- **Auto-close only fires on merge to the *default* branch.** Closing keywords close the issue when
  the PR lands on `main` (or whatever your default is). Merge into a non-default branch and the issue
  stays open, by design. Keep the keyword in the *PR description* (or a commit message); a closing
  keyword buried in a mid-thread comment behaves differently across hosts.
- **The exact keyword set is host-specific.** `Closes/Fixes/Resolves` are the safe, widely-supported
  trio, but the full list and the cross-repo syntax (`owner/repo#42`, needed when a fork's PR closes
  an upstream issue) vary by host. When in doubt, mention-link and close the issue by hand; the trail
  still exists.
- **Auto-closed is not the same as actually done.** Merging closes the issue *mechanically*. It says
  nothing about whether the work was correct; that judgment was the review (Module 10), and if review
  was a rubber stamp, you just auto-closed an issue for broken work. The loop automates the
  bookkeeping, never the thinking.
- **Protected branches protect against accidents, not admins.** Most hosts let admins bypass
  protection (sometimes silently). And an account with push access, including a *bot* account you set
  up for an agent, is an attack surface and a blast radius: its token can push branches and, if
  over-permissioned, merge them. Scope machine accounts to the least they need; this is the front edge
  of a problem Unit 4 takes head-on.
- **Forks add real friction beyond the extra clone.** Keeping a fork in sync with a fast-moving
  upstream is ongoing work, and PRs *from* forks are deliberately limited by hosts (for example, they
  often can't access the upstream repo's CI secrets, relevant once you reach Module 14). For repos
  you own, prefer branches; reach for forks only when you genuinely lack push access.
- **The loop diagram is the happy path.** Real PRs get change requests, need updating when `main`
  moves underneath them, or hit a merge conflict (Module 6) when two contributors touched the same
  lines, exactly
  the parallel-agent scenario worktrees mitigate but don't eliminate. The stations are fixed; the
  number of trips around them isn't.
- **Squash-merge collapses authorship.** If your team squashes, the agent's (or your) individual
  commits become one commit on `main`, and the per-commit trail lives only on the now-deleted branch /
  closed PR. That's usually a fine trade for a clean history; just know the granular history moved
  from `main` to the PR record.

---

## Check for understanding

**You're done when:**

- You ran the full loop on `tasks-app` at least once and watched an issue close itself on merge,
  with `main` protected so the PR was mandatory, not optional.
- You can draw the seven-station loop (issue → branch → implementation → PR → review → merge → closed)
  from memory and say which earlier module owns each station.
- You can state the branch-vs-fork rule in one sentence (push access → branch; no push access → fork)
  and why an agent follows the same rule.
- You ran at least one trip around the loop with an **agent as the contributor** for the
  implement-and-open-PR steps, and can point to the exact step where you, the human, stayed in the
  loop (the merge).
- You can explain why the same tooling that coordinates human teammates is what makes accepting an
  agent's work safe.

When the loop feels like one motion rather than six separate tools, and when "give the agent a
branch and review its PR" feels obvious rather than novel, you're ready for Module 12, where we make
the *recovery* half of this safety net its own discipline: reverting a bad PR after it's already
merged.
