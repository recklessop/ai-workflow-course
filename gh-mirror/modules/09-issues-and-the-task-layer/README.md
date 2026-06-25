# Module 9: Issues and the Task Layer

> **An issue is how you hand a piece of work to someone else, and "someone else" is now a mix of
> humans and agents.** A well-formed issue is the one interface that works for both, which makes
> writing them more valuable than they used to be.

---

## Prerequisites

- **Module 1**: the `tasks-app` project. The lab writes issues against it.
- **Module 2**: the repo-as-durable-memory reframe. Issues are the team-scale version of the same
  idea: shared memory for the work that *hasn't happened yet*.
- **Module 5**: you committed your AI instructions file. That file plus a good issue is what gives
  an agent enough context to attempt a task; this module puts that pairing to work.
- **Module 8**: you have a repo on a remote forge (GitHub or any alternative). Issues live on the
  forge, alongside the code, so this module needs the remote you set up there. Everything here is
  provider-neutral: issues exist on every forge.

You do **not** yet need pull requests (Module 10) or the full collaboration loop (Module 11). This
module produces the *input* to that loop. We'll point forward to it, not teach it here.

---

## Learning objectives

By the end of this module you can:

1. Write a well-formed issue (title, context, acceptance criteria, scope) that a human *or* an
   agent can pick up and act on without a follow-up conversation.
2. Use labels and assignment to route, prioritize, and find work across a backlog.
3. Decide which work to route to a human and which to hand to an agent, and articulate the heuristic
   behind that call.
4. Use issues as durable, shared task memory: the part of the project's state that lives outside
   the code.

---

## Key concepts

### What an issue actually is (for this audience)

An issue is **a written, addressable unit of work that lives next to the code instead of in
someone's head, a Slack thread, or a chat tab.** The project-management vocabulary around it varies;
that core doesn't. It has a title, a body, and metadata (labels, an assignee, a status). It gets a stable number. You
can link to it, search it, and close it.

You already know this shape; it's a ticket. Jira, Linear, ServiceNow, a help-desk queue: same idea.
What matters for this course is that **every git forge has issues built in**, sitting in the same
place as the repo. GitHub Issues, GitLab Issues, Gitea/Forgejo Issues, Bitbucket, Azure Boards:
the feature set varies, the concept does not. Because they're attached to the repo, an issue can
reference a commit, a file, or a line, and the work that resolves it can reference the issue back.
That tight coupling is the whole point: the *description* of the work and the *code* that does it
live one click apart.

### Reframe: issues are shared task memory

Module 2 reframed the repo as **durable memory the AI can read**: a fresh session reconstructs
"where were we?" from `git log`, `git status`, and `git diff`. But notice what git can only ever
tell you: what *happened*. Settled history and in-flight edits. It is silent on the work that
*hasn't started yet*: the bug someone reported, the feature you promised, the cleanup you keep
deferring.

That forward-looking state has to live somewhere durable too, or it lives in memory and evaporates
exactly like a closed chat tab. Issues are where it lives. So the project actually has two memories,
and they divide the timeline cleanly:

| Layer | Answers | Lives in |
|-------|---------|----------|
| The repo (Module 2) | "What happened / what's in flight right now?" | commits, working tree |
| The issue tracker (this module) | "What still needs to happen, and who has it?" | issues, labels, assignees |

A teammate joining tomorrow, or an agent that has never seen the project, reads the repo to learn
the code and reads the open issues to learn the *work*. Both are ground truth you can hand to a
human or a machine. Neither depends on anyone remembering anything.

### Anatomy of a well-formed issue

Most issues are written badly because they're written for the author, who already has all the
context. A good issue is written for **a stranger**, because increasingly the thing that picks it
up *is* one: a teammate you've never met, future-you who's forgotten, or an agent with no memory at
all. Four parts carry the weight:

1. **Title**: a specific, scannable summary. Someone reading a list of forty titles should know
   what each one is. `done command crashes on a bad index` beats `bug in cli`.
2. **Context / problem**: what's wrong or missing, and *why it matters*. Include how to reproduce a
   bug (the exact command and what happened), or the motivation for a feature. This is the part a
   vague issue skips and then nobody can act on it.
3. **Acceptance criteria**: the checklist that defines *done*. Concrete, verifiable statements:
   "`done 99` prints an error and exits non-zero instead of a traceback." This is the single most
   valuable part of the issue, for reasons the AI angle makes sharp.
4. **Scope / out of scope**: what this issue does *not* cover, so the work doesn't sprawl. "Not
   changing the storage format" keeps a one-line fix from becoming a refactor.

A proposed approach is optional and often helpful, but keep it as a suggestion, not a spec; the
person or agent doing the work may know a better one.

Compare. A bad issue:

> **Title:** fix the done thing
> the done command is broken, please fix

Nobody, human or agent, can act on that without coming back to ask you three questions. A
well-formed version of the same bug:

> **Title:** `done` command crashes on an out-of-range or non-integer index
>
> **Context:** `python3 cli.py done 99` on a list with 3 tasks raises an uncaught `IndexError` and
> dumps a traceback. `python3 cli.py done abc` raises `ValueError`. Either way the user sees a stack
> trace instead of a helpful message.
>
> **Acceptance criteria:**
> - `done <index>` with an out-of-range index prints a clear error (e.g. `no task at index 99`) and
>   exits non-zero.
> - `done <non-integer>` prints a clear error and exits non-zero.
> - A valid `done <index>` still works exactly as before.
>
> **Out of scope:** changing how tasks are stored or numbered.

That second version is pickup-ready. It is also, not coincidentally, the format an agent needs.

### Labels: the cross-cutting axes

A title says what one issue is. **Labels** are how you slice the whole backlog. Keep the taxonomy
small and orthogonal, a handful of axes, not forty decorative tags:

- **Type**: `bug`, `feature`, `chore`/`docs`. What kind of work.
- **Priority**: `p1`/`p2`/`p3` or `high`/`med`/`low`. How much it matters.
- **Area**: `cli`, `storage`, `docs`. Which part of the system, for routing to whoever (or whatever)
  owns it.
- **Readiness**: a single label like `ready` meaning "well-formed enough to start." This one matters
  most in the AI era: it's the signal that an issue has clear acceptance criteria and can be handed
  off, to a person *or* an agent, without more discussion.

Resist label sprawl. If a label never changes how you filter or who picks up the work, delete it.
Five well-chosen labels beat thirty that no one trusts.

### Assignment: routing the work to one owner

Labels describe; **assignment routes.** Assigning an issue puts one name on it: the owner, the
person (or agent) the rest of the team can assume is handling it. The discipline that matters is
*one* owner; an issue assigned to three people is assigned to no one. Unassigned-but-`ready` is a
fine state too; it means "available, anyone can grab this."

This is the mechanic that turns a pile of issues into coordinated work, and it leads straight to the
point this module turns on.

### The roster is mixed now: humans and agents

Here's the shift. The list of things you can assign an issue to used to be "the people on the team."
It increasingly includes **agents**. An issue can be routed to a person, or handed to an
issue-to-PR agent that reads the issue, makes the change on a branch, and opens it up for review.
(That agent is its own module, **Module 25**, and we are not building it here. The point now is
only that it's a possible *assignee*, which changes how you write the issue.)

The exact mechanism varies and is still settling across forges: some let you assign an agent like a
user, some trigger it with a label, some kick it off from a comment or an external runner. Don't
anchor on the plumbing. Anchor on this: **the well-formed issue is the one interface that works for
every assignee on the roster.** A human and an agent need the same things from an issue: a clear
title, real context, and acceptance criteria that define done. Write it well and you've written it
for both.

### Which work goes to a human, which to an agent

So how do you decide? A useful heuristic, which is really a property of the *issue*, not the model:

**Hand it to an agent when the issue is well-scoped, has concrete acceptance criteria, and follows
a pattern already in the codebase.** An `undone <index>` command, the inverse of `done`, is a
strong candidate: it mirrors the existing command almost exactly, "clear the done flag" is
unambiguous, and a human can verify the result in seconds. The bug above is another: contained,
reproducible, testable.

**Keep it with a human when the issue carries genuine ambiguity, design judgment, or cross-cutting
risk.** "Add due dates" sounds small but isn't: what date format does the user type? Does the list
re-sort by date? How are overdue tasks shown, and in whose timezone? Those are product decisions an
agent will *answer confidently and probably wrongly*, because nothing in the issue tells it the
right call. A human resolves the ambiguity first (often by splitting it into clear sub-issues, at
which point the pieces may become agent-ready).

Notice the heuristic doesn't ask how smart the model is. It asks how well-specified the *work* is.
A vague issue degrades gracefully with a human, who asks you a question, and catastrophically with
an agent, which guesses and produces a confident, plausible, wrong PR. Routing is mostly about
matching the clarity of the issue to the autonomy of the assignee.

### Where this is heading

This module produces the input to a loop you'll complete later. An issue is the start; the rest is:

- An assignee (human or agent) takes the issue, branches (Module 6), does the work, and opens it for
  review as a pull request (**Module 10**), which gets merged and **closes the issue**; the full
  coordination loop is **Module 11**.
- Agents can also work the *intake* side: triaging, labeling, and routing incoming issues with a
  human still deciding (**Module 24**), or taking an assigned issue all the way to a PR (**Module
  25**).

You don't need any of that yet. You need issues good enough to feed it. That's this module.

---

## The AI angle

The issue tracker itself isn't new. What's changed is that **the issue is now an agent's task
specification**, and that raises the stakes on writing it well in three concrete ways:

- **Acceptance criteria are the agent's definition of done.** A human reads fuzzy criteria and fills
  the gaps with judgment. An agent reads them literally and stops when they're satisfied, so vague
  criteria produce work that's technically complete and actually wrong. The same criteria also become
  the basis for the test you'll write (Module 13) and the thing you check in review (Module 10). One
  well-written checklist pays out three times.
- **A bad issue fails an agent harder than a human.** The failure modes aren't symmetric. Hand a
  person an underspecified ticket and you get a question; hand an agent the same ticket and you get a
  confident, plausible, wrong PR that costs more to review than the work would have taken. The cheap
  insurance is the clarity you put in *before* assigning.
- **Your committed config plus the issue is the whole brief.** Module 5's instructions file carries
  the standing context: conventions, build and test commands, what not to touch. The issue carries
  the specific task. Together they're enough for an agent to attempt the work with no live
  conversation at all. That's the pairing that makes routing-to-an-agent viable, and it's why both
  artifacts have to be good.

The reframe: writing a clear issue used to be a courtesy to your teammates. Now it's the difference
between an agent that ships the right change and one that wastes a review cycle. The skill got more
valuable, not less.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/09-issues-and-the-task-layer/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 9"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** Markdown + shell, against the `tasks-app` repo you pushed to a forge in Module 8.

You'll draft issues as Markdown locally (so you can version and reuse the format), then have your
agent create them on the forge and route them yourself. Drafting first keeps the *thinking*, the
part that matters, separate from the mechanical step of turning a draft into a forge issue.

**You'll need:**

- Your `tasks-app` repo on a forge (Module 8), with its issue tracker enabled. Most forges turn
  issues on by default, but not all of them do, consistent with the "the feature set varies" caveat
  above. Bitbucket Cloud's tracker is off until you enable it, Azure DevOps uses Boards/Work Items
  rather than an Issues tab, and SourceHut uses a separately provisioned `todo.sr.ht` tracker. If you
  took the forge-agnostic path, confirm yours has issues available before Part C.
- The starter files in this module's `lab/` folder:
  - `issue-template.md`: the well-formed-issue skeleton to copy for each issue.
  - `example-issues.md`: three worked issues for `tasks-app`, as a reference/answer key.
- Claude Code (or your own CLI/in-editor agent from Module 4), pointed at the `tasks-app` repo. It
  can read the code directly to ground each issue's context, and create the issues on your forge once
  you've drafted them.

### Part A: Find the work

Look at the `tasks-app` and find three real pieces of work. The app is deliberately thin, so there's
plenty it still can't do. Because it's carried forward across modules, skip anything you may have
already built (a `delete` command, task priorities) and pick work that's genuinely still missing.
Good candidates:

1. **A bug**: `python3 cli.py done 99` (an out-of-range index) and `python3 cli.py done abc` (a
   non-integer) both crash with an uncaught traceback. Run them and watch.
2. **A small, patterned feature**: an `undone <index>` command that clears a task's done flag,
   mirroring the existing `done` command (it's the inverse).
3. **A judgment-heavy feature**: due dates on tasks (date format? sorting? overdue display?
   storage?).

### Part B: Draft three well-formed issues

For each, copy `lab/issue-template.md` to its own file (say `issue-bug.md`, `issue-undone.md`,
`issue-due-dates.md`) and fill every section: title, context (with repro steps for the bug),
acceptance criteria, and out-of-scope. Write them for a stranger.

This is a good place to *use* the AI: point Claude Code at `tasks-app` and ask it to draft acceptance
criteria against the actual code, then **edit them down**. The model tends to over-produce, and
tightening its draft is exactly the skill. Check your drafts against `lab/example-issues.md` only
after you've written your own.

### Part C: Create, label, and route

You've done the thinking; turning three Markdown drafts into real issues with labels is mechanical
forge work, so hand it to the agent and verify the result. From the repo, ask Claude Code (or your
own agent) to do it, for example: *"Create three issues on the forge from `issue-bug.md`,
`issue-undone.md`, and `issue-due-dates.md`. For each, set a type label (`bug`/`feature`), a
priority, and a `ready` label only where the acceptance criteria are solid enough to start."* The
agent uses the forge's CLI or API (`gh issue create` on GitHub, the equivalent elsewhere) to create
and label them.

Then **verify** on the forge: open the issue list, confirm all three exist, check the bodies match
your drafts, and check the labels are right. This is the Module 4 pattern. You direct, the agent does
the mechanical work, you confirm it landed.

**Routing is your call, not the agent's.** This is the module's core exercise:

- Assign the **judgment-heavy feature (due dates) to a human**, yourself. It has unresolved design
  questions; it is not agent-ready as written.
- Earmark the **bug** and the **`undone` feature for an agent.** They're well-scoped, patterned, and
  easy to verify. Use whatever your forge offers: an actual agent assignee, an `agent-ready` label,
  or a note in the issue saying "suitable for an issue-to-PR agent (Module 25)." The mechanism
  doesn't matter yet; the *decision* does.

Write one sentence in each issue, or a scratch note, explaining **why** it went where it went, in
terms of the issue's clarity rather than the model's smarts. That sentence is the routing skill.

### Part D: Read the backlog cold

Open your forge's issue list and filter by your `ready` label. You should be looking at exactly the
work that's pickable right now, by anyone or anything. That filtered view is the shared task memory
from the reframe: the thing a new teammate or a fresh agent reads to learn the work, with no one
explaining anything.

---

## Where it breaks

The honest caveats: issues are not the repo, and they don't behave like it:

- **Issues lie when they go stale; git doesn't.** The repo is ground truth by construction; it *is*
  the code. An issue is a *claim* about work, and a claim rots. A backlog full of issues that were
  fixed months ago, or describe a version of the app that no longer exists, is worse than no backlog,
  because people (and agents) trust it. Closing issues is as much a discipline as opening them.
- **Acceptance criteria can't capture genuine ambiguity.** The whole "agent-ready vs. human" split
  assumes you *can* write clear criteria. For real design problems you can't yet; that's not a
  writing failure, it's the nature of the work. Forcing crisp criteria onto an open question just
  hides the question. Those issues stay with a human until the ambiguity is resolved.
- **Routing to an agent is delegation, not abdication.** Handing an issue to an agent doesn't mean
  the change ships unseen. Everything it produces still lands as a reviewable pull request behind the
  review and CI gates you'll build in later modules (10, 14). "Assign to agent" means "an agent does
  the first pass," not "an agent merges to `main`." If your mental model is the latter, fix it before
  Unit 5.
- **Label and assignment models differ across forges.** There's no cross-forge standard. Some allow
  multiple assignees, some one; label and permission systems vary; "assign an issue to an agent" is
  an emerging capability implemented differently everywhere it exists at all. Keep your taxonomy
  small and portable so it survives a forge change; don't build a workflow that depends on one
  vendor's exact issue fields.
- **Over-tooling a tiny project is its own failure.** A solo throwaway script does not need a labeled,
  prioritized backlog. Issues pay off when work is shared: across people, across agents, or across
  enough time that you'd otherwise forget. Below that threshold, a TODO comment is fine.

---

## Check for understanding

**You're done when:**

- You have **three well-formed issues** on your forge for `tasks-app`, each with a title, context,
  and concrete acceptance criteria, not a one-line "fix the thing."
- Each issue carries a small, sensible label set, and at least one is marked `ready`.
- At least one issue is **routed to a human** and at least one is **earmarked for an agent**, and you
  can state the routing reason in terms of the issue's clarity and scope, not the model's
  intelligence.
- You can explain why issues are *shared task memory* and how that complements (rather than
  duplicates) the repo-as-memory idea from Module 2.

When a stranger could pick up any of your `ready` issues and start without asking you a single
question, you've written them well, and that's exactly what Module 10 (reviewing the resulting
change) and Module 11 (closing the loop) are about to build on.

---

## Verify-before-publish

Mostly durable (issues are a stable concept on every forge), but one part of this module sits on
moving ground:

- [ ] **Agent-as-assignee mechanics.** How you route an issue to an agent (native agent assignee,
  trigger label, comment command, external runner) is still settling and differs per forge. Re-check
  that the lab's "earmark for an agent" step still matches what at least one mainstream forge
  actually offers, and keep the wording mechanism-agnostic if it's still in flux.
- [ ] **Forge issue terminology and label/assignee limits** (single vs. multiple assignees, built-in
  vs. custom labels). Confirm the neutral descriptions still hold across the forges named in
  Module 8.
