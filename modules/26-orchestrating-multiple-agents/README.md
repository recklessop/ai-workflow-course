# Module 26: Orchestrating Multiple Agents

> **One agent on its own branch was the experiment. Several agents at once, on their own branches,
> integrated back through review: that's the payoff.** This module turns worktrees from a one-off
> convenience into an operating model, and it introduces the bottleneck that replaces compute. That
> bottleneck is your own attention.

---

## Prerequisites

- **Modules 2, 5, 6.** Durable memory per worktree, the committed AI config every agent inherits,
  and conflict resolution for the inevitable merge.
- **Module 7, Worktrees.** The primitive everything here rests on. One repo, many working directories, each on
  its own branch, each safe for an agent to edit without touching the others. Module 7 proved this on
  *two* agents and told you the scale-up lived here. This is here. If `git worktree add` /
  `list` / `remove` aren't muscle memory yet, go back; everything below is that, multiplied.
- **Module 8, Remotes.** The PRs in this lab live on a forge. (A local-only fallback is given.)
- **Module 9, Issues.** The unit of work you split across agents. A clean fan-out is a set of clean
  issues.
- **Module 10, Reviewing code you didn't write.** The skill that becomes the bottleneck. N agents
  produce N diffs; one human reviews them one at a time.
- **Module 11, Collaboration: humans and agents on one repo.** The issue → branch →
  implementation → PR → review → merge → close loop. Orchestration is that loop run N times in
  parallel and fanned back into one `main`. Parallel agents are just contributors who happen to
  share a clock.
- **Module 14, Continuous integration.** The automated gate every parallel branch passes through
  before it's yours to review. With many agents, CI stops being a nicety and becomes the only thing
  keeping the merge queue honest.
- **Module 25, Autonomous agents.** You can hand an agent an issue and get a reviewable PR back,
  supervised. This module runs *several* of those at once. If you can't trust one unattended agent,
  you have no business running five.

If you parachuted in: you minimally need worktrees, the PR loop, and one agent you'd let run on its
own. This module is about coordinating many of those, not about any one of them.

---

## Learning objectives

By the end of this module you can:

1. Decompose a chunk of work into units that are *actually* parallelizable, and recognize the ones
   that only look parallelizable because they share an interface.
2. Fan work out across several agents, each isolated in its own worktree on its own branch tied to
   its own issue, using a coordination plan instead of luck.
3. Fan the results back in through PRs, CI, and review without producing a tangle no human could read.
4. Sequence merges and resolve agent-vs-agent conflicts deliberately, instead of letting the merge
   order be whoever-finished-first.
5. Judge honestly whether parallelizing a given task was worth it, including when the coordination
   and review overhead ate the speedup.

---

## Key concepts

### The shift: from "an agent" to "a fleet"

Module 25 got you to a real milestone: hand an agent an issue, walk away, come back to a PR that
passed CI. The supervision was structural: the agent couldn't merge anything; it could only *propose*
a reviewable change. That's one agent.

What that milestone doesn't tell you is how quickly you want a second one. The agent is
cheap and it works in wall-clock minutes, so the instant you have one job running you notice three
*other* jobs sitting idle. The model isn't the constraint; it never was. The constraint was that
all those jobs wanted the same repo, the same files, the same checked-out branch. Module 7 removed
exactly that constraint for two agents. Orchestration is what you do when "two" becomes "however many
the work splits into."

And here's the reframe that organizes the whole module:

> **Running multiple agents is not a parallel-programming problem. It's a project-management problem
> that happens to have agents as the workers.** The hard parts (splitting work so it doesn't
> overlap, coordinating who owns what, integrating the results, reviewing it all) are the same hard
> parts a tech lead has always had. The agents just make the *doing* fast enough that the
> *coordinating* becomes the whole job.

Everything below is one of those four management problems: **split, isolate, coordinate, integrate.**

### Problem 1: Splitting work cleanly (the part everyone gets wrong)

The common failure mode is to look at a pile of work, declare "I'll run five agents on this," and
fan it out by gut. It feels like a 5× speedup. It usually isn't, because **most work isn't as
independent as it looks**, and the dependencies you ignored at split-time come back as merge
conflicts at integrate-time, with interest.

The unit of split is the **issue** (Module 9). A good fan-out is a set of issues where each one:

- **Touches a disjoint set of files.** Two agents editing the same file will conflict at merge. Two
  agents editing *different* files won't. This is the single biggest predictor of a clean fan-in.
- **Doesn't change a shared interface.** This is the subtle one. Two agents can edit two different
  files and *still* collide if both depend on the signature of a third thing. If agent A adds a
  `due_date` field to the `Task` dataclass and agent B adds a `priority` field to the *same*
  dataclass, they're editing the same file *and* the same contract; that's not two jobs, it's one
  job pretending to be two.
- **Has its own acceptance criteria.** Each agent must be able to know it's done without asking what
  the others did. If "done" for agent A depends on agent B's output, they're sequential, not
  parallel; run them in order, not at once.

The honest heuristic:

> **Parallelize across the seams of your codebase, not across its joints.** Independent features in
> separate files parallelize beautifully. Anything that touches a shared type, a shared config, a
> shared route table, or a shared schema is a *joint*; serialize it. One agent owns the joint; the
> others build off it once it's merged.

A concrete tell: if you can't write the N issues such that each one's "files touched" list barely
overlaps the others', you don't have N parallel jobs. You have one job and a wish.

### Problem 2: Isolation at scale

This is the part Module 7 already solved; orchestration just adds discipline and naming.

Each agent gets **its own worktree on its own branch tied to its own issue.** The convention that
keeps a fleet legible:

```
~/ai-workflow-course/
  tasks-app/            ← main worktree, on main (the integration point; no agent works here)
  tasks-app-42-count/   ← worktree for issue #42, branch feature/42-count, agent A
  tasks-app-43-docs/    ← worktree for issue #43, branch feature/43-docs,  agent B
  tasks-app-44-clear/   ← worktree for issue #44, branch feature/44-clear, agent C
```

The branch name carries the issue number (`feature/42-count`), the folder name mirrors the branch,
and **`main` is sacred**: it's the integration point, not a workspace. No agent runs in the main
worktree; that's where *you* merge their work after review. Keeping `main` out of the rotation is
what lets you always answer "what's the known-good state?" with one `cd`.

Worktrees give you file isolation for free (Module 7): agent A literally cannot write agent B's
files, because they're different files on disk. But "files on disk" is not the only shared resource,
and this is where scale bites in ways two-agents didn't:

- **Runtime state.** The per-worktree `tasks.json` is isolated (it's gitignored runtime state, one
  per folder). Good.
- **Ports, databases, external services.** *Not* isolated. If three agents each start the app and it
  binds the same port, or they all hammer one shared dev database or one API key's rate limit, the
  isolation that holds for files evaporates for shared infrastructure. Worktrees isolate the *repo*,
  not the *world*. (Containers, Module 16, are how you isolate the world; worth reaching for once a
  fleet shares more than a filesystem.)
- **Disk and compute.** Each worktree is a full set of working files plus whatever each agent's
  process consumes. Two is free-ish. Ten is a resource plan.

### Problem 3: Coordination, the plan is the artifact

With one agent, the coordination lived in your head. With a fleet, it has to live in a file, for the
same reason every other piece of project memory does (Module 2): your head doesn't scale and it
forgets.

The artifact is a **coordination plan**, a flat table of who owns what. There's a starter in
`lab/orchestration-plan.md`; the shape is just:

| Issue | Branch | Worktree | Files owned | Depends on | Status |
|-------|--------|----------|-------------|------------|--------|
| #42 count | `feature/42-count` | `tasks-app-42-count` | `cli.py` (dispatch + new fn) | none | running |
| #43 docs | `feature/43-docs` | `tasks-app-43-docs` | `README.md`, `CHANGELOG.md` | none | running |
| #44 clear | `feature/44-clear` | `tasks-app-44-clear` | `cli.py` (dispatch + new fn) | none | queued |

Reading that table tells you everything orchestration needs to know *before* you launch anything:

- **#42 and #43 are genuinely parallel:** disjoint files, no shared interface. Run them at once.
- **#44 conflicts with #42:** both own `cli.py`'s dispatch. The table makes the collision visible at
  plan-time, when it's free to fix, instead of merge-time, when it costs a conflict. Your options:
  serialize them (run #44 after #42 merges), or split the seam better (one owns dispatch, the other
  is told exactly where to add its branch, though shared files resist this).

The "Depends on" column is the parallelism killer in disguise. Any non-empty cell means *not now*.

**Two ways to drive the fan-out.** The plan can be executed by *you* (you open the worktrees, launch
each agent, track the table by hand) or by an **orchestrator agent** that reads the plan and spawns a
sub-agent per row. Tooling for the latter is real and moving fast; some agentic tools can launch and
manage parallel sub-agents or background sessions directly. It's powerful and it adds a layer: an
orchestrator that mis-splits the work fans out *bad* splits faster than you could by hand. Whether you
drive it or an agent does, **the plan is the contract**, and a human owns the plan.

### Problem 4: Integration, keeping the fan-in reviewable

This is where multi-agent work lives or dies, and it's the reason this module is paired with review
(Module 10) in the syllabus.

The anti-pattern is to let agents merge into each other, or all pile onto one branch, producing an
interleaved history no human can read line by line. That defeats the entire point: the output stops
being reviewable, and unreviewable AI output is exactly what Unit 5 exists to prevent.

The pattern is **fan-out, then fan-in through the front door, one branch at a time:**

1. Each agent's work lands as **its own branch → its own PR.** One agent, one diff, one issue, one
   review. The PR is the unit of reviewability (Module 10), and it stays that way no matter how many
   agents ran.
2. **CI runs on every PR** (Module 14). With a fleet, this is non-negotiable: it's the automated
   first pass that lets you spend your scarce review attention only on PRs that already build and pass
   tests. CI reviews *all* of them in parallel for free; you review the survivors.
3. **You merge them into `main` in a deliberate order**, not finish-order. Merge the foundational one
   first (the agent that touched the joint), then merge the others on top so any conflict
   surfaces against settled code. Each merge is a small, calm, Module-6 conflict resolution, on your
   terms, once, instead of two live agents corrupting each other in real time.
4. **An assistive reviewer (Module 24) can take the first pass** on each PR: comment on the obvious
   stuff so your human attention lands on the judgment calls. But a human still owns the merge, the
   same as always.

The shape to hold in your head: **agents fan out wide, work fans back in narrow**, through PRs,
through CI, through one reviewer, into one `main`. Wide at the edges, single-file in the middle. That
funnel is what keeps "five agents ran" from becoming "five times the mess."

### The thing that actually limits you

Notice what got expensive. The model is cheap and parallel. The worktrees are cheap. CI is cheap and
parallel. The two things that *don't* parallelize are **splitting the work** (one brain deciding the
seams) and **reviewing the results** (one brain reading the diffs). Add agents and those two stay
exactly as serial as they were.

> **Compute stopped being the bottleneck the moment agents got cheap. Your attention is the new
> bottleneck, and it doesn't fan out.** Orchestration is the discipline of spending that attention on
> the two things only you can do (split and review) and letting the agents have everything in between.

The skill of this module is not "launch many agents"; any tool can do that. It's keeping the fan-in
narrow enough that one human can still stand at the funnel.

---

## The AI angle

A generic devops course has no reason to teach this, because human contributors don't spawn on
demand. You hire them slowly, they self-coordinate in standups, and you'd never have five of them
start the same morning on one small repo. Agents break all three assumptions: they spawn instantly,
they coordinate only as well as you instrument them to, and "five at once on a small repo" is Tuesday.

That changes the calculus specifically:

- **The cost of a bad split is now paid at agent speed.** A human who picks up an ambiguous,
  overlapping task will *ask you* before they collide with a teammate. Agents don't hesitate; they
  confidently barrel into the overlap and you discover it at merge. The coordination plan isn't
  bureaucracy; it's the question the agents won't think to ask.
- **Parallelism is the entire economic case for cheap agents, and it's a trap if the work isn't
  parallel.** The temptation to fan out is strongest exactly when you're most rushed, which is exactly
  when you're least careful about the seams. Fanning out non-parallel work doesn't speed it up; it
  converts a clean sequential job into a conflicted parallel one and *adds* the merge tax.
- **Review is the wall everything rests on, and agents push on it hardest.** One agent makes you review one
  diff. Five agents make you review five, and they all finished while you were reviewing the first.
  This is the concrete reason the whole back half of this course (review, CI, security gates) had to
  exist *before* this module: those gates are the only things that let one human stay in the loop on
  output produced faster than one human can read.
- **The reviewability you protected in Module 7 is what makes scale survivable.** Per-agent worktrees
  meant per-agent branches meant per-agent clean history. At fleet scale, that's the difference
  between "five PRs I can review in turn" and "one branch with five agents' edits braided together
  that I have to archaeology my way through." You bought reviewability cheap back then; here's where
  it pays the rent.

You don't reach for orchestration because running many agents is cool. You reach for it the first
time you fan out by gut, hit four merge conflicts and two redundant PRs, and realize the speedup was
imaginary, and that the fix was a ten-minute coordination plan you skipped.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/26-orchestrating-multiple-agents/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 26"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Git + a couple of helper scripts) driving multiple AI edit sessions on the
`tasks-app`, integrated through PRs.

You'll fan three agents out across the `tasks-app`: two with genuinely independent work, one
deliberately set to collide; then fan their work back in through PRs and review. The goal is not
just "it worked." The goal is to **feel the coordination and review cost in your own hands**: the
clean merge, the conflict you could have predicted from the plan, and the moment review becomes the
thing you're waiting on.

**You'll need:**

- The `tasks-app` repo from Module 2, pushed to a remote forge (Module 8), so you can open real PRs.
  **No remote?** Do the whole lab locally: replace "open a PR" with "merge into a local `integration`
  branch and review the diff there." You lose the forge UI, not the lesson.
- Worktrees working (Module 7): `git --version` ≥ 2.5.
- **Three** AI edit sessions you can run at once (Module 4): three editor windows, three terminal
  agent sessions, or one orchestrator driving three sub-agents if your tool supports it (Claude Code
  is the worked example here; sub your own agent). Browser-only still works; treat each worktree as a
  separate copy-paste context, but you'll feel the coordination cost more sharply, which is the lesson.
- The starter files in this module's `lab/` folder, at
  `~/ai-workflow-course/modules/26-orchestrating-multiple-agents/lab/`: `orchestration-plan.md`,
  `fan-out.sh`, `status.sh`, `cleanup.sh`, and three prompts under `lab/agent-prompts/`. As
  established back in Module 4, the course's lab scripts live in the course repo while `tasks-app` is a
  separate folder. Here the worktree git is the **AI's** job (the Module 4 pivot): you direct a
  coordinating session to create and tear down the worktrees and you verify the result, with the
  scripts as the tool-agnostic fallback if you'd rather hand the agent a script to run than have it
  type the commands. `status.sh` stays a read-only dashboard you run yourself.

### Part A: Plan the split before you launch anything (this is the lab)

1. Open `lab/orchestration-plan.md`. It's pre-filled with three issues against `tasks-app`:

   - **#42 `count`:** add a `count` command to `cli.py` that prints the number of pending tasks.
   - **#43 `docs`:** document the existing commands in `README.md` and start a `CHANGELOG.md`.
   - **#44 `clear`:** add a `clear` command to `cli.py` that removes all tasks.

2. Before doing anything, **read the "Files owned" column and predict the conflicts.** Write your
   prediction at the bottom of the plan. You should be able to see, on paper, that **#42 and #43 are
   clean** (disjoint files: `cli.py` vs. docs) and that **#44 collides with #42** (both own `cli.py`'s
   dispatch chain). That prediction is the entire skill of Problem 1; make it now, then watch it come
   true at merge.

   (If you have real issues on your forge from Module 9, create #42/#43/#44 there and let the branch
   names reference them. If not, the numbers are just labels; the lesson is identical.)

### Part B: Fan out

3. Create a worktree per issue. An agent that lives inside a worktree can't create its own worktree,
   so direct your **coordinating session** (the AI already pointed at `tasks-app` from Module 4,
   Claude Code in this example; sub your own agent) to set them up from the plan:

   > *"From the `tasks-app` repo, create one linked worktree per row in `orchestration-plan.md`, each
   > as a sibling folder on its issue-named branch: `../tasks-app-42-count` on `feature/42-count`,
   > `../tasks-app-43-docs` on `feature/43-docs`, and `../tasks-app-44-clear` on `feature/44-clear`.
   > Leave `main` untouched. Then show me `git worktree list`."*

   That's three `git worktree add` calls and a `git worktree list`, run for you. (Prefer a script?
   Hand the agent `fan-out.sh` from this module's `lab/` and have it run that instead; same result,
   tool-agnostic.) Then **verify** by hand:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   git worktree list      # main + the three feature/ worktrees
   ```

   Four folders, one repo, `main` untouched and reserved for integration. You directed, the agent did
   the git, you confirmed.

4. Launch the three agents **at the same time**, each pointed at its own worktree and given its own
   prompt:

   - `tasks-app-42-count` ← `lab/agent-prompts/agent-42-count.md`
   - `tasks-app-43-docs`  ← `lab/agent-prompts/agent-43-docs.md`
   - `tasks-app-44-clear` ← `lab/agent-prompts/agent-44-clear.md`

   While they run, watch the fleet. Copy the read-only dashboard into `tasks-app` and run it from a
   fourth terminal:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   cp ~/ai-workflow-course/modules/26-orchestrating-multiple-agents/lab/status.sh .
   bash status.sh
   ```

   It prints each worktree, its branch, and how many commits/changes are in flight: your fleet
   dashboard. Update the **Status** column in the plan as each finishes.

5. Have each agent commit and push its own work. Each prompt already ends by telling its agent to
   commit the change on its branch and push it; to trigger it explicitly, tell each session: *"Commit
   your work on this branch with a message that references the issue, then push the branch."* Each
   agent owns its own commit and push, so three branches advance in parallel with no git typed by you.
   Then **verify** the fleet landed:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   bash status.sh      # each branch should show commits ahead of main and DIRTY? = no
   ```

   (No remote? Drop the push; the branches still exist locally and you'll integrate them in Part C.)

### Part C: Fan in through the funnel

6. Open **one PR per branch** on your forge (Module 11), each linked to its issue. You now have three
   PRs in flight. Let CI run on each (Module 14); notice it reviews all three in parallel, for free,
   while you've reviewed zero.

7. **Review them one at a time** (Module 10). This is the moment to feel the bottleneck: three agents
   finished in parallel, and you are reading their diffs in series. Time yourself if you want the
   point to land.

8. **Merge in deliberate order, not finish order.** The order is *your* call, the part only you can
   make: merge the two clean, independent branches first, then the one you flagged as a collision, so
   the conflict surfaces against settled code. Direct your coordinating session (in the `tasks-app`
   main worktree) to do the merges in exactly that order, and to stop on the first conflict instead of
   resolving it:

   > *"On `main` in `tasks-app`, merge `feature/42-count`, then `feature/43-docs`, then
   > `feature/44-clear`, in that order. After each, tell me whether it merged cleanly or conflicted.
   > If one conflicts, stop and show me the conflict; don't resolve it yet."*

   The first two land clean (disjoint files). The third stops on a conflict:

   ```text
   CONFLICT (content): Merge conflict in cli.py
   Automatic merge failed; fix conflicts and then commit the result.
   ```

   There it is: the conflict you predicted in Part A, exactly where the plan said it would be: both
   #42 and #44 added an `elif` to the same dispatch chain. Read the conflict yourself before you let
   the agent touch it; seeing it land where you called it is the whole point of the prediction you
   wrote in Part A. Then direct the agent to resolve it the Module 6 way (*keep both the `count` and
   `clear` branches, then stage and commit the merge*), then **verify** the result by hand:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   python3 cli.py list && python3 cli.py count && python3 cli.py clear   # all three features live
   ```

   If any of those three commands fails, the resolution was wrong. That's why you verify the result
   instead of trusting the merge.

9. Close the issues (Module 11 closes them automatically if the PRs referenced them). Then tear the
   fleet down: direct your coordinating session to *remove the three worktrees now that their work is
   merged, then prune and show `git worktree list`*. (Prefer a script? Hand it `cleanup.sh` from this
   module's `lab/`.) Either way it refuses to remove a worktree that still has uncommitted work
   (Git's safety), so commit or merge anything stray first. Verify only `main` remains:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   git worktree list      # just main
   ```

### Part D: Score the orchestration honestly

10. Answer these in the plan file, for real:

    - **Did parallel beat sequential here?** Add up agent wall-clock (mostly overlapping) *plus* your
      serial review time *plus* the conflict resolution. Compare to "I'd have done these three myself,
      in order." Be honest about whether the fan-out actually won.
    - **Which split was worth it and which wasn't?** #42+#43 were genuinely parallel. #44 fought #42
      the whole way. What would you have done differently: serialized #44, or scoped it to a
      different file?
    - **Where was the bottleneck?** It was almost certainly your review queue, not the agents. Name it.

That reflection is the deliverable. Anyone can launch three agents; the skill is knowing when the
fourth one makes things slower.

---

## Where it breaks

The honest caveats, and at fleet scale they bite harder than anywhere else in the course:

- **Coordination overhead can exceed the speedup.** There's an Amdahl's-law reality here: the serial
  parts (splitting the work, resolving conflicts, reviewing every PR) don't shrink when you add
  agents, so past a small number the coordination cost grows faster than the parallel gain. Three
  well-scoped agents routinely beat one. Eight overlapping agents routinely *lose* to one. The number
  isn't "as many as the tool allows"; it's "as many as the work genuinely splits into and you can
  still review."
- **The temptation to fan out work that isn't parallelizable is the central failure mode.** It feels
  like a speedup and registers as one right up until integration, when the dependencies you waved away
  arrive as conflicts. Fanning out a non-parallel job is strictly worse than doing it sequentially:
  same work, plus a merge tax, plus N reviews instead of one. When in doubt, run it as one agent.
- **Merge conflicts between agents are a *when*, not an *if*, on any shared file.** Worktrees defer
  conflicts to merge-time (Module 7); they don't prevent them. Two agents on the same dispatch chain,
  the same config, the same schema *will* collide. The plan's job is to make that collision a
  conscious choice (serialize, or accept one merge conflict), not a surprise.
- **Review becomes the bottleneck, and it's a human one.** This is the wall every honest practitioner
  hits. You can generate diffs faster than you can responsibly read them, and merging unread AI diffs
  to clear the queue is how a fleet quietly ships bugs at scale. Assistive review (Module 24) and CI
  (Module 14) raise the ceiling; they don't remove it. If your review queue is permanently growing,
  you have too many agents, not too few reviewers.
- **Shared infrastructure isn't isolated by worktrees.** Files are isolated; ports, databases, API
  keys, rate limits, and external services are not. A fleet that shares a backing service can corrupt
  shared state or exhaust a quota in ways no amount of branch isolation prevents. That's a
  containers/secrets problem (Modules 16–17), not a Git one.
- **An orchestrator agent is another agent that can be wrong, faster.** Letting an agent split the
  work and spawn the sub-agents is powerful and convenient, and it removes the one human checkpoint
  (the plan) that catches a bad split before it's executed N times. If you delegate the orchestration,
  keep the *plan* human-owned: review the split before the fan-out, not the wreckage after.
- **Disk, processes, and cost scale linearly with the fleet.** Every worktree is a full working tree;
  every agent is a running process and a stream of (metered) model calls. "Run more agents" is not
  free even when each one is cheap. Budget the fleet like you'd budget any pool of workers.

---

## Check for understanding

**You're done when:**

- You wrote a coordination plan that named, *before launching*, which agents were genuinely parallel
  and which would collide, and the merge proved your prediction right.
- You ran three agents at once, each isolated in its own worktree on its own issue-named branch, with
  `main` reserved as the integration point and never worked in directly.
- Each agent's work came back as its own PR, passed CI, got reviewed one at a time, and merged into
  `main` in a deliberate order, including resolving the agent-vs-agent conflict you'd predicted.
- You can state, without looking, the two things that *don't* parallelize when you add agents
  (splitting the work, reviewing the results) and therefore where your real bottleneck lives.
- You can give an honest answer to "was the fan-out worth it?" for your lab, including the case where
  it wasn't.

When you instinctively reach for a coordination plan before fanning out, and instinctively cap the
fleet at what you can still review, you've got it. That review-as-bottleneck instinct is exactly what
Module 27 makes systematic: if your attention can't scale to judge every agent by hand, **evals** are
how you judge them at scale instead.

---

## Verify-before-publish

This is expansion-zone material; multi-agent tooling is some of the fastest-moving in the course.
Re-check at build/publish time:

- [ ] **Parallel-agent / sub-agent features in agentic tools.** Whether and how current tools launch
      and manage parallel sessions, background agents, or orchestrator-and-sub-agent patterns; names,
      limits, and defaults drift fast. Keep the writing describing the *capability* generically; don't
      pin a vendor's feature name.
- [ ] **Native worktree management in agentic tools.** Some tools now create/manage worktrees per
      session automatically. If that's mainstream at publish time, note it so learners aren't doing by
      hand what their tool does for them, but keep the manual `git worktree` path as the
      tool-agnostic foundation.
- [ ] **Forge merge-queue / parallel-CI features.** Merge queues and parallel CI for many concurrent
      PRs are evolving on the major forges. If the forge automates ordered, conflict-checked merging,
      reference it as an aid to the fan-in, without making it a requirement.
- [ ] **The "how many agents is too many" framing.** Stays a judgment call, not a number. Verify the
      Amdahl framing still reads as honest against whatever the tooling makes easy that quarter, and
      resist any vendor claim that orchestration removes the review bottleneck; it doesn't.
- [ ] **Cross-references** to Modules 24 (assistive review) and 27 (evals) still match their final
      titles and framing.
