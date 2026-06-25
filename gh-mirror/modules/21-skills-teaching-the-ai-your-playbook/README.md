# Module 21: Skills: Teaching the AI Your Playbook

> **Stop re-explaining your own procedures.** A skill is a repeatable workflow written down once,
> committed, and invoked on demand, so the AI does the thing *your* way, the same way, every time,
> without you narrating the steps again.

---

## Prerequisites

- **Module 2:** you commit, read diffs, and treat the repo as durable memory. Skills live in that
  repo and are versioned exactly like code.
- **Module 3:** markdown-as-versioned-text, and the `CHANGELOG.md` convention this module's lab
  writes to.
- **Module 4:** the AI lives in your editor/CLI and reads your files directly. A skill is a file it
  loads; a browser chat can't pick one up automatically.
- **Module 5, the one this builds on directly.** You committed an always-on instructions file that
  tells the AI how the project works in general. This module is its **structured big sibling**: the
  same write-it-down-and-commit instinct, but for *specific repeatable procedures* invoked on demand.
- **Module 13:** what a real test is (and why "it didn't crash" isn't one). The lab's procedure
  includes writing one.
- *Helpful, not required:* **Module 20 (MCP).** A skill's steps can call the real tools an MCP
  server exposes, which is where a playbook reaches beyond editing files into live systems.

---

## Learning objectives

By the end of this module you can:

1. Explain the difference between an **always-on instructions file (Module 5)** and a **skill**, and
   say when each is the right tool.
2. Write a skill: a structured, named, invokable playbook for a recurring task, in your tool's
   format-agnostic essentials (when-to-use, inputs, ordered steps, done-criteria).
3. Have the AI **execute** a skill end to end and verify it followed every step.
4. Keep skills in version control so a procedure is shareable, reviewable, and recoverable like any
   other artifact.
5. Recognize when a one-off prompt has earned promotion into a durable skill, and when it hasn't.

---

## Key concepts

### The pain: you keep narrating the same procedure

You've written the Module 5 instructions file, and it's working. The AI knows your layout, your test
command, your off-limits files. But there's a class of knowledge it doesn't cover: **multi-step
procedures you run again and again.**

"Add a new CLI command" is the canonical example. Done properly it's never one edit. It's: put the
logic in the right file, wire the CLI, write a test that actually checks the behavior, run the tests,
smoke-test the command, add a changelog line, commit it as one clean change. The AI can do every step.
But left to a bare prompt (*"add a `clear` command"*) it'll usually give you the code and forget the
test, or skip the changelog, or commit `tasks.json` along for the ride. So you spell out the seven
steps. It works. Next week you add another command and **you spell out the same seven steps again.**

That re-narration is the exact pain Module 1 named, one level up: not re-explaining the *project* each
session, but re-explaining the *procedure* each time you run it. A skill is where that procedure stops
being something you retype and becomes something the repo carries.

### What a skill is

A **skill** is a named, structured, invokable set of instructions for one repeatable procedure,
stored as a file in the repo and loaded **on demand** when that procedure is the task at hand.

Strip the vendor branding and every skill has the same four parts:

- **A name and a "when to use it."** So both you and the AI know which playbook applies and, just as
  importantly, when it *doesn't*.
- **Inputs.** The few things the procedure needs to be told (here: the command name and what it does).
- **Ordered steps.** The actual procedure: the commands, the files, the checks, in sequence, with the
  non-negotiables marked ("run the tests before claiming success," "don't stage `tasks.json`").
- **Done-criteria.** How the AI (and you) know it's actually finished, not just "produced something."

That's it. A skill is a checklist precise enough that an agent can execute it and you can verify it
did.

### Skill vs. the Module 5 instructions file

This is the distinction to lock in, because the two are siblings and easy to conflate:

| | **Committed instructions file (Module 5)** | **Skill (this module)** |
|---|---|---|
| Scope | How the project works, *in general* | How to do *one specific procedure* |
| When it loads | **Always on**: read every session | **On demand**: invoked when relevant |
| Shape | Ambient briefing: conventions, commands, don't-touch list | A playbook: when-to-use, inputs, ordered steps, done-criteria |
| Analogy | The standing house rules posted on the wall | A labeled recipe card you pull out when you cook that dish |

They're complementary. The instructions file is the right home for facts true *all the time* ("tests
run with `python3 -m unittest`"). A skill is the right home for a procedure you run *sometimes* ("here
is exactly how we add a command"). Module 5 even told you this was coming: start with the always-on
file; graduate a procedure into a skill when it earns its own page.

### Why "on demand" is the whole point

Module 5 warned that **bloat kills an instructions file**: a 300-line always-on briefing gets read
the way you read a terms-of-service. So you *can't* solve the re-narration problem by stuffing every
procedure into the always-on file; you'd drown the signal that makes it work.

A skill solves that. Because a skill loads only when its procedure is the task, you can write
it in full detail, every step and every guardrail, without taxing every unrelated session. Ten skills
cost the AI nothing on a session that invokes none of them. This is **progressive disclosure**: keep
the always-on context lean, and pull in the deep procedure exactly when it's needed. It's the same
reason you don't tape every recipe you own to the kitchen wall.

### Skills live in version control

This is what makes a skill more than a snippet in a notes app, and it's why this module sits where it
does in the course. A skill is a file in the repo, so everything you already learned about versioned
text applies to it directly:

- **Recoverable and historied (Module 2).** A skill has a `git log`. You can see when a step was added
  and why, and `git restore` a botched edit. The procedure is a checkpoint like any other.
- **Shareable (Modules 8 & 11).** Push the repo and the whole team, plus every agent that later
  operates on it, inherits the same playbook. Nobody runs their own private version of "how we add a
  command." It's the Module 5 anti-drift argument, applied to procedures.
- **Reviewable (Module 10).** Changing how the AI performs a procedure arrives as a **diff in a PR**.
  Tightening "add a test" into "add a test that asserts the end state, not just no-crash" is a
  reviewable change to your team's workflow, not an invisible tweak in one person's setup.

A prompt you keep in your head dies with the session. A skill in the repo is durable, shared
capability. That's the upgrade: from one-off prompting to a versioned, reviewable asset.

### Naming the pattern, not the vendor

"Skills" is one name for this. Tools also call them custom commands, slash commands, recipes, prompts,
playbooks, or modes, and they load them differently: some auto-discover a dedicated folder, some need
you to point at a file, some let your always-on instructions file say *"when asked to add a command,
follow `add-command.md`."* **The durable pattern is the same in all of them: a named, invokable file
of structured steps for a repeatable procedure, kept in the repo.** Learn the pattern; map it onto
whatever your tool calls it. As with everything in this course, the model and the tool are swappable;
the playbook you wrote is the part that lasts.

### Skills compose with your tools

A skill's steps aren't limited to editing files. They can drive the test runner, the CLI, Git, and,
once you have **Module 20's MCP** servers wired up, the real systems behind them (open the issue, hit
the staging API, query the database). A skill is where you encode *"use these hands, in this order, to
get this outcome."* The deeper your toolchain, the more a written playbook is worth, because there
are more steps to get wrong, and more value in getting them right every time.

---

## The AI angle

On paper this is just "write a runbook." The AI-specific twist is what changes the stakes:

- **The AI will execute the playbook, not just read it.** A runbook for a human is a reminder; a skill
  for an agent is something it *performs*. The precision pays off immediately: vague step, vague
  result; imperative step ("run `python3 -m unittest`; do not claim success until it's green"), reliable
  result.
- **The AI is confidently incomplete without one.** Asked to "add a command," it'll happily stop at
  the code and skip the test, the changelog, the clean commit, and sound finished doing it. The skill
  is how you make *complete* the default instead of a thing you have to keep catching.
- **The skill outlives the model.** Swap models next quarter and the playbook carries over unchanged.
  You encoded the *procedure*, not the prompt that happened to coax it out of this month's model. The
  workflow is the durable skill; the model is the swappable part; here, literally.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/21-skills-teaching-the-ai-your-playbook/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 21"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** markdown (the skill file) plus shell and Python (the `tasks-app`). You'll write a
skill, then have your editor-integrated AI (Module 4) execute it.

You'll write a skill for the procedure from *Key concepts*, **add a new `tasks-app` command, end to
end: code + test + changelog + clean commit**, and then watch the AI run it on a command it's never
seen, producing all four parts without you listing the steps.

**You'll need:**

- Your agentic coding tool from Module 4, and knowledge of how it loads a procedure (a skills/commands
  folder it auto-discovers, or simply pointing it at a file by name; check its docs).
- A Python 3.10+ `tasks-app`. Use the snapshot in this module's `lab/tasks-app/` (it has `add`,
  `list`, `done`, `count`, a `test_tasks.py`, and a `CHANGELOG.md`), or carry forward your own from
  earlier modules. It should already be a Git repo from earlier modules; if you're starting fresh,
  ask Claude Code (`claude` in the project; sub your own agent) to initialize it and commit a
  baseline, then confirm with `git log` that the first commit landed.

### Part A: Install the skill

1. Copy this module's starter skill, `lab/add-command-skill.md`, into your `tasks-app` repo wherever
   your tool expects procedures. If your tool auto-discovers a folder, put it there under a clear name
   (e.g. `add-command.md`). If it doesn't, just drop it at the repo root and invoke it by name.

   ```bash
   cd ~/ai-workflow-course/tasks-app
   cp ~/ai-workflow-course/modules/21-skills-teaching-the-ai-your-playbook/lab/add-command-skill.md add-command.md
   ```

2. Read it. The whole file is short on purpose: when-to-use, inputs, seven ordered steps, and
   done-criteria. Confirm every project fact in it matches *your* app (test command, file names, the
   off-limits `tasks.json`). A skill with wrong facts misdirects the AI worse than no skill.

3. **Commit it.** This is the point: the procedure now lives in version control. Ask Claude Code
   (sub your own agent) to commit the new skill file with a message like "Add skill: add a tasks-app
   command end to end," then verify it landed:

   ```bash
   git log --oneline -1   # the skill commit, by name
   ```

### Part B: Invoke it

4. Start a **fresh** AI session in your editor and invoke the skill the way your tool does it: its
   slash command / skill name, or plainly: *"Follow `add-command.md` to add a `clear` command that
   removes all tasks."* Crucially, **don't list the steps yourself.** The skill is supposed to supply
   them.

5. Watch it perform the procedure. A correctly-followed skill will, without you saying any of it:
   - add `clear()` to `tasks.py` and wire a `clear` branch into `cli.py` (logic in the right file);
   - add a real test to `test_tasks.py` that asserts the list is empty afterward (not just "no crash");
   - run `python3 -m unittest` and show it green;
   - smoke-test `python3 cli.py clear` and show the output;
   - add a `CHANGELOG.md` line;
   - stage code + test + changelog into one commit, **without** `tasks.json`.

### Part C: Verify it followed the playbook

6. Don't take the AI's word for it. Check against the skill's own done-criteria:

   ```bash
   python3 -m unittest          # green, and a clear-related test is present
   python3 cli.py add "x" && python3 cli.py clear && python3 cli.py list   # -> (no tasks yet)
   git show --stat HEAD        # one commit: tasks.py, cli.py, test_tasks.py, CHANGELOG.md; no tasks.json
   ```

   If a step was skipped, that's the lab working: it shows you exactly where your wording was too soft.
   Tighten that line, have Claude Code (sub your own agent) commit the skill edit while you verify the
   diff, and run it again on a second command (`high <index>` to flag a task, say). **A skill you
   improve once and reuse forever is the deliverable**, not the one `clear` command.

### Part D: See it as a reviewable, reusable asset

7. Look at what you built:

   ```bash
   git log --oneline add-command.md   # the procedure's own history
   git log -p -- add-command.md        # full patch history: the file's creation, plus the Part C tighten if you made one
   ```

   (`git log -p` surfaces the skill's own patches no matter what you committed *after* tightening it,
   unlike `git diff HEAD~1`, which would be empty here because the most recent commit added the second
   *command*, not a change to the skill.) Each entry in that history *is* a change to how your team adds
   commands: readable, attributable, revertable. In a
   team repo (Modules 8, 11) it reaches everyone on `git pull`; behind review (Module 10) it lands as a
   PR someone approves. You've turned a procedure you used to narrate into a versioned capability.

---

## Where it breaks

- **A skill is guidance, not enforcement; same caveat as Module 5.** It strongly biases the AI; it
  doesn't bind it. The agent can still skip a step, especially a soft one, especially late in a long
  session. The steps that *can't* be skipped are the ones backed by **CI (Module 14)**: the test the
  skill tells it to write only gates anything once a pipeline runs it on every push. Write the
  done-criteria as hard checks, and let CI be the backstop.
- **Skills rot.** A playbook that says "tests run with X" after you've moved to Y will confidently
  march the AI off a cliff. Skills are code-adjacent: review them, update them, delete the ones you no
  longer run. Committing them (so changes are visible) is what makes that maintainable.
- **Don't skillify everything.** A skill earns its place when a procedure is *repeated*, *multi-step*,
  and *gets done wrong without one*. A one-off task doesn't need a playbook, and a pile of near-duplicate
  skills is its own kind of bloat: now you're maintaining ten files and the AI has to pick the right
  one. Promote a prompt to a skill the third time you've typed it, not the first.
- **Overlap with the always-on file causes drift.** If a fact lives in both your Module 5 instructions
  file *and* a skill, you'll eventually update one and not the other. Keep general facts in the
  always-on file and *reference* them from skills; don't duplicate them.
- **A skill is not a security boundary.** "Don't stage `tasks.json`" is a convention, not a permission.
  An installed third-party skill is untrusted code that runs against your repo; vetting, permissions,
  and prompt-injection defense are **Module 22's** job, immediately next, for exactly this reason.

---

## Check for understanding

**You're done when:**

- Your `tasks-app` repo has a committed skill file for "add a command," with `git log` showing the
  commit that added it.
- You've invoked that skill and watched a fresh AI session produce **all four** parts (code, a real
  test, a changelog entry, and one clean commit) *without you listing the steps that session*.
- You've verified it against the skill's done-criteria (tests green, command works, the commit
  contains the right files and not `tasks.json`) rather than trusting the AI's summary.
- You can state, in one sentence, when to put knowledge in the always-on instructions file (Module 5)
  versus a skill: general facts go in the file that's always read; a specific repeatable procedure goes
  in a playbook invoked on demand.

When adding the *next* command is "invoke the skill" instead of "re-explain the seven steps," the
playbook is doing its job. Module 22 comes next, and not by accident: Unit 4 just gave the AI hands,
MCP servers and skills, and the very next thing is securing them, because an installed skill or
server is untrusted code running in your environment.

---

## Verify-before-publish

This is expansion-zone material; the *concept* is durable but tool specifics drift. Re-check at build
time:

- [ ] **Skill terminology and mechanics.** Confirm how mainstream agentic tools name and load skills
      (skills / custom commands / slash commands / recipes / prompts), whether they auto-discover a
      folder or need an explicit pointer, and any required file format/frontmatter, without pinning
      the lesson to one vendor. Update the "Naming the pattern" paragraph if the common vocabulary has
      shifted.
- [ ] **No vendor leaked in.** Verify the module still names the *pattern*, not one implementation, and
      that the example skill format stays generic (when-to-use / inputs / steps / done-criteria).
- [ ] **Dependency chain intact.** Confirm Module 20 (MCP) and Module 22 (securing servers/skills) are
      still numbered as referenced, and that nothing here leans on a tool introduced after Module 20.
- [ ] **Lab still runs.** `python3 -m unittest` is green in `lab/tasks-app/`, and the `clear`-command
      walkthrough still matches the starter files (`add`/`list`/`done`/`count`, `test_tasks.py`,
      `CHANGELOG.md`).
