# Module 23: Working with Existing Codebases

> **Every module so far quietly assumed you started the project. Most of your real work won't be
> like that.** This module is about pointing AI at a large codebase you *didn't* write, and making
> changes that don't break a system nobody fully understands.

---

## Prerequisites

This module needs only the **Module 4** tooling to *attempt*: an agentic, editor-integrated AI that
can read and edit your files. But it's placed at the back on purpose, because the basics are exactly
what make changing unfamiliar code survivable. Lean on:

- **Module 2: Version control as a safety net.** You're about to let an AI touch code you don't
  understand. The commit you can return to is the only reason that's not reckless.
- **Module 6: Branches.** Every change here happens on a branch, isolated from working code.
- **Module 10: Reviewing code you didn't write.** The core skill of this whole course, now aimed at
  a diff in a codebase you *also* didn't write. Double the unfamiliarity, double the discipline.
- **Module 12: Revert, reset, and recovery.** When a change in a system you don't understand goes
  wrong, recovery is how you get out clean.
- **Module 13: Testing.** The existing test suite is your contract for "did I break anything I
  can't see?"
- **Module 20: MCP servers.** Real, structured access to the code and the tools around it, instead
  of pasting fragments.
- **Module 21: Skills.** Where you codify the navigation and safe-change playbooks this module
  teaches, so you don't re-explain them every session.

---

## Learning objectives

By the end of this module you can:

1. Give an AI enough **factual, verifiable context** about a large repo to be useful in it, instead
   of letting it work from a few pasted fragments.
2. Have the AI **map and explain** an unfamiliar area (architecture, entry points, where things
   live) and verify that map against the actual files *before* anything is touched.
3. Scope a change down to the **smallest reviewable diff** that solves the problem, and refuse the
   sweeping rewrite the AI will happily offer.
4. Use **MCP (Module 20)** to give the AI real access to the code and surrounding tools, and
   **skills (Module 21)** to make your navigation and safe-change process repeatable.
5. Make one **small, scoped, tested, reviewable** change to a codebase you didn't write, and know
   why it's safe.

---

## Key concepts

### The greenfield assumption, and why it was a lie

Everything up to now used `tasks-app`: a tiny project you stood up, understood completely, and grew.
That made the lessons clean. It also made them unrepresentative. The dominant reality for an IT pro
is the opposite: a codebase that's **large, old, written by people who've left, and load-bearing for
something that matters.** You're not asked to build it. You're asked to change one thing in it
without breaking the other thousand things you've never read.

This is where AI is simultaneously most tempting and most dangerous. Tempting, because "just ask the
AI to figure it out" feels like exactly the help you need against 200,000 lines you don't know.
Dangerous, because the AI's two default failure modes get *worse* the bigger and less familiar the
codebase is:

- **It maps from vibes.** A file named `auth.py` becomes "the authentication module" in its mental
  model whether or not the real auth lives there. It confidently describes structure it inferred
  from names, not from reading. In a small repo you'd catch it. In a huge one you won't.
- **It rewrites instead of edits.** Ask for a small change and it hands you a "cleaned-up" version of
  the whole file (reformatted, renamed, restructured) burying your one-line fix in a 300-line diff
  nobody can review. In code you wrote, that's annoying. In code you didn't, it's how an invisible
  regression ships.

The entire job of this module is to deny the AI both of those defaults: **force it to map from the
real files, and force every change to stay small and reviewable.**

### The motion: orient, map, then change

Three phases, strictly in order. Skipping ahead is the mistake.

**1. Orient: establish ground truth before any opinion.** Before the AI gets to reason about the
codebase, give it facts it can't hallucinate: the actual file list, the real entry points, the
languages by volume, the build and test commands, the biggest files (often the spine of the system),
the recent commit history. This is mechanical and cheap; a script produces it (the lab's `orient.py`
does exactly this). It anchors everything that follows in reality. You're not asking the AI "what is
this project?" cold; you're handing it the facts and asking it to *interpret* them.

**2. Map: explain the area before touching it.** Now the AI builds a mental model, and the only
acceptable model is one **traced through real files with citations.** Don't accept "the request
flows through the controller layer." Demand: "trace one request from entry point to response, naming
each file it passes through." The deliverable is an architecture summary plus a "where things live"
table, and crucially a list of **open questions the code didn't answer.** A map with honest gaps is
trustworthy. A map with no gaps is fiction. This phase is **read-only**; nothing changes on disk.

**3. Change: the smallest scoped, tested, reviewable diff.** Only now do you edit. One change, one
branch (Module 6). Find the blast radius first, every caller of what you're touching, and if you
can't enumerate them, you're not ready. Make the minimal edit, add a test that fails without it,
run the *full* existing suite, and self-review the diff like it's someone else's PR (Module 10). No
drive-by reformatting. No "while I was in here." The diff a reviewer sees should be exactly the
change and nothing else.

### Context is the bottleneck, not intelligence

A frontier model is plenty smart enough to understand any one file in your repo. What it *can't* do
is hold all 200,000 lines in its head at once. The context window is finite, and stuffing it full of
irrelevant code makes the model worse, not better. So the skill here isn't "give the AI more." It's
**give the AI the right slice, and a way to fetch more on demand.**

That reframes the orientation pack: its job is to be a small, high-signal index that lets the AI
decide what to read next, not a dump of the whole tree. And it's exactly why the next two tools
matter so much in this module.

### Where MCP earns its place (Module 20)

Pasting files into a chat doesn't scale past a handful of them, and it makes the AI work blind
between pastes. **MCP (Module 20) gives the AI real, structured access to the codebase and the tools
around it** so it can navigate on its own instead of waiting for you to feed it fragments. The kinds
of access that turn a guessing model into a grounded one:

- **The filesystem and code search**, so it can grep for every caller of a function instead of
  assuming it found them all.
- **Language-server intelligence** (go-to-definition, find-references, type info) so "where is this
  used?" is answered by the toolchain, not by the model's guess.
- **The surrounding systems**: the issue tracker (Module 9), CI results (Module 14), the running
  app's logs, so the AI maps the code *and* the context it lives in.

The orientation pack is the cold-start. MCP is how the AI keeps the map accurate as it digs, by
pulling real answers from real tools instead of inferring them.

### Where skills earn their place (Module 21)

The orient/map/change motion is the same on every repo. That makes it a perfect candidate for a
**skill (Module 21)**: a committed, reusable playbook so you don't re-explain "map before you touch,
cite real files, keep the diff small" every single session. This module ships two starter skills in
`lab/skills/`:

- **`map-this-repo`**: the read-only navigation playbook: orient, find entry points, trace one path
  end to end, produce a cited architecture summary with honest open questions.
- **`safe-change`**: the safe-change playbook: branch first, find the blast radius, baseline the
  tests, make the minimal edit, cover it, self-review, and a set of **stop conditions** that tell the
  AI to escalate to a human instead of pushing on.

These are the structured big siblings of the committed config from Module 5: instead of "be careful
in unfamiliar code," they encode *exactly* what careful means, as steps the AI follows every time.

---

## The AI angle

Onboard a human to a legacy codebase and the advice is familiar: read the README, ask a senior dev.
What's specific here is that **the AI is both the thing reading the codebase and the thing most
likely to confidently misread it.** The bigger the repo, the wider that gap between "sounds
authoritative" and "is correct."

So the AI-specific discipline is verification, not exploration. The model is genuinely excellent at
the grunt work of orientation: reading a hundred files, summarizing structure, tracing a call path.
That's exactly the work that's tedious and slow for a human. But it will narrate a wrong map with
the same fluent confidence as a right one. Your job shifts from "explore the code" (let the AI do
that) to "make the AI prove its map against real files, and keep its changes small enough that a
wrong map can't do much damage." The whole earlier toolchain (version control, branches, review,
tests, recovery) is what turns "the AI might be wrong about this huge system" from a catastrophe
into a revertable diff.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** This lab is self-contained and does not depend
> on the earlier labs. Its files live in `modules/23-working-with-existing-codebases/lab/`. Copy them into a working folder
> and make a first commit so you start clean:
>
> ```bash
> cp -r ~/ai-workflow-course/modules/23-working-with-existing-codebases/lab ~/ai-workflow-course/23-working-with-existing-codebases-lab
> cd ~/ai-workflow-course/23-working-with-existing-codebases-lab && git init -b main && git add -A && git commit -m "start: module 23"
> ```
**Lab language:** shell + the provided Python script (`orient.py`); you run it, you don't write it.
This lab does **not** use `tasks-app`; the entire point is a codebase you *didn't* write.

**You'll need:**

- Git, Python 3.10+, and the agentic AI tool from Module 4. The lab uses Claude Code as the worked
  example (`claude --version  # sub your own agent`); the steps survive a tool swap.
- A real, small-to-medium open-source repo to clone. Pick something with **tests** and a clear
  build/test command, in a language you can at least read. Good traits: a few thousand lines, an
  obvious entry point, a documented install (`pip install -e .`, `npm install`, `go mod download`,
  …), and a test suite that **goes green on a clean clone after that documented install**. Confirm
  that before you rely on it as a baseline. (Avoid giant frameworks for a first run; you want a
  system you can't fully hold in your head, but whose test suite finishes in under a minute.)
  **First time? Pick a small Python repo**, so the Module 13 testing toolchain you already have
  transfers with the least friction.
- The starter files from this module's `lab/` folder: `orient.py` and `skills/`.

### Part A: Clone and orient

1. Clone your chosen repo and copy `orient.py` into its root:

   ```bash
   git clone <repo-url> unfamiliar-repo
   cd unfamiliar-repo
   # copy modules/23-working-with-existing-codebases/lab/orient.py into this folder
   python3 orient.py > ORIENT.md
   ```

2. Read `ORIENT.md` yourself first. In 30 seconds you should know the language, the likely entry
   point, the probable test command, and which files are biggest. These are **facts**; the AI can't
   argue with them. (Don't commit `ORIENT.md`; it's scratch context.)

### Part B: Map before you touch (read-only)

3. Start a fresh AI session, load the `map-this-repo` skill (`lab/skills/map-this-repo.md`) or paste
   it as instructions, and give it `ORIENT.md` as the opening context.

4. Ask it to produce the architecture summary: what the project does, a "where things live" table,
   the confirmed build/test command, and a traced path for one real operation end to end,
   **with every claim citing a real file.** Demand the list of open questions it couldn't resolve.

5. **Verify the map.** Open two or three files it cited and confirm they say what it claimed. This is
   the step everyone wants to skip and the one that catches the confident-but-wrong map. If a
   citation doesn't hold up, the map is suspect; push back and make it re-trace.

### Part C: One small, scoped, tested change

6. Pick a genuinely small change: a clearer error message, a fixed edge case, a tiny missing
   validation, a documented-but-unhandled input. Something a single function owns. Now load the
   `safe-change` skill (`lab/skills/safe-change.md`) and let Claude Code (sub your own agent) do the
   setup the skill assigns it. Tell it to install the project's dependencies the way the README says
   (typically `pip install -e .` for Python, `npm install` for JS/TS, `go mod download` for Go) and
   run the existing tests to establish a green baseline. **Your job is to verify the result**, not to
   type the commands. Confirm the suite is actually green, and apply the judgment the skill leaves to
   you: a fresh clone usually won't run green until its deps are installed, but if it still won't go
   green on a clean clone *after* a documented install, that's a setup problem rather than your
   baseline. Pick another repo before you change code on top of an environment you can't trust.

7. Direct the AI through the change with the `safe-change` skill loaded. Its first action is to
   create the branch (Step 1 of the skill), so you don't type `git switch` yourself; **verify** it
   did by running:

   ```bash
   git status        # confirm you're on e.g. scoped-change, not the default branch
   ```

   Then direct the rest: make it find the blast radius (every caller) before editing, keep the edit
   minimal, and add a test that fails without the change and passes with it. Have it run the **full**
   suite and confirm green.

8. **Review the diff like it's a stranger's PR (Module 10).** This part you do by hand; reviewing
   what the AI wrote is the skill that doesn't transfer to the AI:

   ```bash
   git diff
   ```

   Every changed line should be necessary and explainable. If the AI snuck in a reformat or a
   rename, tell it to revert that and keep only the scoped change. Once the diff is exactly the
   change and nothing more, instruct the AI to commit it, then verify the result with
   `git show` so the commit holds only what you approved.

9. Have the AI draft the PR description the `safe-change` skill asks for (what changed, why, the
   blast radius, how it was tested, and what it deliberately did *not* touch), then edit it into your
   own words before it goes up.

---

## Where it breaks

- **A confident map is still just a hypothesis.** The AI will produce a fluent, plausible
  architecture summary for a repo it half-read. Fluency is not correctness. The citation-checking in
  Part B isn't optional ceremony; it's the only thing standing between you and changing code based on
  a fiction. Verify at least a few claims by hand, every time.
- **The context window is a hard ceiling.** On a genuinely large monorepo, the AI cannot see everything,
  and it usually won't *tell* you what it didn't read. Its map is only as good as the slice it
  actually loaded. MCP-backed search and language-server tools (Module 20) shrink this problem by
  letting it fetch on demand, but they don't erase it; treat "I've reviewed the whole codebase" as
  a claim to distrust.
- **"Small change" can hide a big blast radius.** A one-line edit to a heavily-called function can
  ripple through code you never opened. The blast-radius search in the `safe-change` skill is the
  defense, but it's only as good as the AI's ability to find *every* caller: dynamic dispatch,
  reflection, config-driven wiring, and string-based lookups all defeat naive search. When in doubt,
  the tests are your backstop, which is why a repo *without* tests is genuinely dangerous to change
  this way.
- **The AI doesn't respect house style by default.** It writes in *its* idiom, not the repo's. In an
  existing codebase that's a tell that screams "an outsider touched this" and quietly degrades
  consistency. The committed instructions file (Module 5) and the `safe-change` skill's
  "match local conventions" rule help, but you'll still catch drift in review.
- **Some changes shouldn't be a small diff.** A genuine architectural problem won't be fixed by the
  smallest-possible edit, and forcing it to be makes things worse. This module's discipline is for
  the common case: a scoped change in a system you don't own. Recognizing when a change is actually
  a *project* (and escalating it as one) is its own judgment call the tooling won't make for you.

---

## Check for understanding

**You're done when:**

- You can hand an AI a factual orientation pack and get back an architecture summary whose citations
  you've **personally verified** against the real files, including the open questions it couldn't
  resolve.
- You've made one change to a codebase you didn't write that is on its own branch, covered by a test
  that fails without it, passing the full existing suite, and whose `git diff` is *exactly* the
  change with no drive-by edits.
- You can explain why the orient -> map -> change order is non-negotiable, and name the two AI
  failure modes (mapping from vibes, rewriting instead of editing) this module is built to deny.
- You can point to where MCP (Module 20) and skills (Module 21) make this repeatable rather than a
  one-off heroics session.

If your change is a clean, tested, reviewable one-liner in a system you couldn't have described an
hour ago, and you trust it, you've got the motion.

---

## Verify-before-publish

This is an expansion-zone module; the durable motion is stable, but the tooling around it moves.

- [ ] Confirm `orient.py` runs unchanged on current Python (3.10+) and a freshly cloned repo on
      macOS, Linux, and Windows (git-bash / PowerShell).
- [ ] Re-check the MCP capabilities cited (filesystem, code search, language-server intelligence,
      issue/CI/log access) against what's actually common in the current MCP ecosystem; the menu of
      available servers changes fast. Keep it described as capabilities, not specific products.
- [ ] Verify the cross-references still point to the right modules if any renumbering happened
      (4, 6, 9, 10, 12, 13, 20, 21).
- [ ] Re-confirm the `SIGNALS`/`TEST_HINTS` tables in `orient.py` still reflect common manifests and
      test runners; add any that have become standard, but keep it language-agnostic.
- [ ] Sanity-check the suggested "small-to-medium repo with a fast test suite" lab guidance still
      lands; recommend nothing by name that could rot.
