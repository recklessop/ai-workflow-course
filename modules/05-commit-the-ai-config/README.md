# Module 5: Commit the AI's Config, Not Just the Code

> **The instructions you give the model are as worth versioning as the code it writes.** Write your
> project's conventions down once, commit them, and every teammate (and every agent) inherits the
> same setup instead of each of you hand-tuning your own and quietly drifting apart.

---

## Prerequisites

- **Module 1**: you have the `tasks-app` project, an editor, and a terminal.
- **Module 2**: you can `commit`, read a `diff`, and treat commits as checkpoints. This module adds
  one more thing worth committing.
- **Module 4**: the AI now lives in your editor or CLI and reads your files directly. That's the
  whole reason a *committed* instructions file matters: an editor-integrated tool can pick it up
  automatically, where a browser chat never could.

---

## Learning objectives

By the end of this module you can:

1. Identify the repo-level instructions file your agentic tool reads, and explain what belongs in it.
2. Write an instructions file for a real project (conventions, build/test commands, coding
   standards, off-limits files, house style) that an AI will actually act on.
3. Commit that file so the configuration travels with the repo, not with one person's machine.
4. Demonstrate the AI obeying the committed instructions, and changing its behavior when you change
   the file.
5. Explain why committing the config makes AI behavior *reviewable*: a change to how the AI works
   arrives as a diff, like any other change.

---

## Key concepts

### The file your tool is already looking for

Open almost any agentic coding tool and, before it does anything, it scans the repo for a
**committed, repo-level instructions file**: a plain-text (usually markdown) file at the project
root that tells the AI how *this* project works. Different vendors look for different filenames, and
the names change; that's noise. The durable fact is the pattern: **your agentic tool reads a
committed instructions file from the repo, and you control what's in it.**

> Throughout this module we'll say "your agentic tool's committed instructions file" rather than name
> one. Find yours in your tool's docs (look for "project instructions," "rules," "context," or a
> repo-root config file). Some tools even read more than one filename; point them all at the same
> content if so. The principle outlives any one vendor's filename.

Without this file, you re-explain your project every session: "we use 4-space indent," "run the tests
with `python3 -m unittest` before you say you're done," "don't touch the generated `tasks.json`." You say it,
the AI complies, the session ends, the memory evaporates (Module 1's second seam), and tomorrow you
say it all again. The instructions file is where that knowledge stops being something you retype and
becomes something the project *carries*.

### What goes in it

An instructions file is not a prompt and it's not documentation for humans (that's the README). It's
a briefing for an agent that will edit this code. Keep it to what changes the AI's behavior:

- **Project conventions**: language version, layout, naming, the patterns this codebase actually
  uses. "Core logic lives in `tasks.py`; the CLI front end is `cli.py`; state persists to
  `tasks.json`."
- **Build and test commands**: the exact commands, copy-pasteable. "Run the app with
  `python3 cli.py <command>`. Run tests with `python3 -m unittest`. Don't claim a change works until
  the tests pass." This single line stops the AI from inventing a test runner you don't use.
- **Coding standards**: formatting, typing, error handling, the libraries you do and don't want.
  "Use the standard library only, no third-party packages. Type-hint public functions."
- **"Don't touch these files."** The off-limits list. Generated files, vendored code, secrets,
  anything the AI should read but never rewrite. "Never edit `tasks.json` by hand; it's generated."
- **House style**: the taste calls that otherwise come back wrong every time. "Keep functions
  small. Match the existing style; don't reformat files you're not changing. Prefer clarity over
  cleverness."

The test of a good line: would you otherwise have to say it again next session? If yes, it belongs in
the file. If the AI already gets it right without being told, leave it out; bloat dilutes the
signal (see *Where it breaks*).

### Why commit it instead of keeping it in your head (or your settings)

Most tools also let you set instructions *globally* (on your machine, for all projects). That's
useful for personal preferences, but it's the wrong home for project knowledge, because of where it
lives: on *your* laptop, invisible to everyone else.

Picture a two-person project with no committed instructions file. You've trained your local setup to
run `python3 -m unittest` and avoid `tasks.json`. Your teammate's setup hasn't, so their agent reformats whole files
and hand-edits the generated JSON. You're both "using AI on the same repo," but you're getting
different behavior, and neither of you can see the other's configuration. That's **drift**: the same
codebase, diverging because the rules live in two heads instead of one file.

Commit the file and that collapses. The configuration is now part of the repo. Clone the repo, get
the rules. A new teammate (or a brand-new agent that's never seen the project) is configured
correctly on the first run, because the setup travels *with the code* instead of with whoever set it
up. This is the same move as Module 2's "the repo is durable memory the AI can read," aimed one level
up: not just the code's history, but the instructions for working on it.

### Shared config vs. personal config

The instructions file is the main thing worth committing, but it's not the only AI config a tool drops
in a repo. Those files split cleanly into *shared* (belongs in the repo, so every collaborator and
every agent inherits it) and *personal* (your machine, your keys, your taste, kept out). Take Claude
Code as the concrete case (sub your own agent's filenames):

| File | Shared or personal |
| --- | --- |
| `CLAUDE.md` (the instructions file) | **Shared**: the whole point of this module |
| `.claude/settings.json` (project settings: permissions, hooks config) | **Shared**: the team runs the same setup |
| `.claude/settings.local.json` (your personal overrides) | **Personal**: gitignored for you |
| `.mcp.json` (the MCP servers the project uses) | **Shared if the project relies on them** |
| `.claude/commands/`, `.claude/agents/`, `.claude/hooks/` | **Shared if the project uses them** |

The principle is tool-agnostic. This very repo commits an `AGENTS.md` instead of a `CLAUDE.md` (same
job, vendor-neutral name) and keeps personal settings out. The line to hold: anything that defines
*how this project is worked on* is shared; anything that's your own machine or your secrets is not.
Rather than guess the split yourself, you can ask the agent which of its config files belong in the
repo. The lab does exactly that.

### AI behavior becomes reviewable

Here's the part that makes this more than a convenience. Once the instructions live in the repo, **a
change to how the AI works on this project is a change to a tracked file**, so it shows up exactly
like a code change. Tighten "keep functions small" into "no function over 30 lines" and `git diff`
reports it the same way it reports an edit to `tasks.py`:

```diff
 ## House style
-- Keep functions small and single-purpose.
+- No function over 30 lines; split anything longer.
```

That decision arrives as a *diff* you can read, question, and accept or reject. It's no longer an
invisible tweak in one person's settings that silently changes what the AI does for everyone. The way
your team works with AI becomes a reviewable artifact with a history: `git log` shows *why* a rule
exists and when it was added.

The full version of this lands in **Module 10**, where that diff becomes a pull request someone
actually reviews before it merges, and **Module 8**, where a shared remote means the file reaches the
whole team. You don't have those yet, so for now the payoff is local: the file is committed, the
behavior is recorded, and `git diff` already shows changes to it as plainly as changes to any code.
The habit starts now; the team-scale payoff arrives on schedule.

### This course commits its own

You don't have to take this on faith: this repo does exactly what the module teaches. At the root of
*The Workflow* is an `AGENTS.md` file, the committed instructions for the agents that help author the
course. (Claude Code reads `CLAUDE.md` by default; `AGENTS.md` is the same job under a vendor-neutral
name, and most tools can be pointed at it.) It states what the repo is, the core promises
(model-agnostic, GitHub-as-default-not-requirement, the load-bearing dependency chain), the voice, the
lab conventions, and a flat "Don't" list. Because it's committed, its history reads like a changelog
of how agents work here:

```text
$ git log --oneline AGENTS.md
4bd586b Tighten the no-slop voice rule; thin em-dashes
ced344d Add the git-reframe section (AI drives git from Module 4)
9e9bb51 Initial commit
```

That file is why every module in this course sounds like one course instead of twenty-seven
tutorials. It's the worked example for everything below.

### Where this is heading: Skills (Module 21)

A committed instructions file is the lightweight foundation. It says *how this project works* in
general: always-on context the AI reads every session. When you find yourself wanting to capture a
*specific repeatable procedure* ("here's exactly how we cut a release," "here's our playbook for
adding a new CLI command"), that's the structured big sibling: **Skills (Module 21)**. Same instinct
(write the knowledge down, commit it, let the AI execute it your way) but packaged as reusable
playbooks instead of a single always-on briefing. Start with the instructions file; graduate to
skills when a procedure earns its own page.

---

## The AI angle

This is the course thesis applied to your own configuration. **The model is the cheap, swappable
part; the setup you build around it is the durable artifact.** When you swap models next quarter (and
you will), your committed instructions file carries over unchanged. The new model reads the same
conventions, the same test command, the same don't-touch list, and behaves consistently on day one.
You configured the *project*, not the model.

Three things make this specifically an AI problem, not a generic config chore:

- **AI has no memory across sessions, but it reads files.** A committed instructions file is the
  cleanest way to give an ephemeral agent durable, project-specific context: written once, read
  every session, by every model.
- **AI is confidently inconsistent without a spec.** Unprompted, it'll pick a test runner, a
  formatting style, a place to put new code, and pick differently next time. The instructions file
  is how you make "the way we do it here" the default instead of a coin flip.
- **AI behavior is otherwise invisible.** A teammate's hand-tuned local rules silently change what
  the AI does. Committing the rules drags that into the open where it can be reviewed, which is the
  whole reason this audience trusts version control in the first place.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/05-commit-the-ai-config/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 5"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell + markdown, on the `tasks-app` project from Modules 1–2. You'll use your
editor-integrated AI (Module 4) for the part where the AI obeys the file.

**You'll need:**

- The `tasks-app` repo from Module 2 (already a Git repo with some history).
- Your agentic coding tool from Module 4, and knowledge of which filename it reads for repo-level
  instructions (check its docs; see the note in *Key concepts*).
- Optionally, a test command for the AI to honor; Python's built-in `python3 -m unittest` works with
  nothing to install (you'll write a real suite in Module 13; until then it simply reports no tests).

### Part A: Write the instructions file and let the AI commit the config

1. Look up the instructions filename your tool reads (Claude Code uses `CLAUDE.md`; sub your own).
   Open an AI session in the `tasks-app` repo and direct it to create that file from this module's
   starter, made true for the project:

   > *"Read `~/ai-workflow-course/modules/05-commit-the-ai-config/lab/instructions-file-starter.md`.
   > Create my tool's instructions file at the root of this repo seeded from it, and adjust every line
   > so it's accurate for this tasks-app. Don't commit yet; I want to review it first."*

   You're handing the AI the file creation and placement. You keep the judgment over *content*: a
   wrong instruction is worse than none.

2. Read what it produced, line by line. The starter is filled in for `tasks-app`, but confirm it
   matches reality. At minimum, check the test command is real (or have it drop the line if you don't
   have tests yet). Fix anything off before it gets committed.

3. Now ask the AI which config should travel with the repo, then let it stage and commit:

   > *"Which of the AI config files in this repo should be committed so a teammate gets the same setup,
   > and which are personal to my machine? Stage the shared ones and commit them with a clear message."*

   A good answer separates *shared* from *personal*. For Claude Code that means commit `CLAUDE.md` and
   `.claude/settings.json`; leave `.claude/settings.local.json` out (gitignored personal overrides);
   commit `.mcp.json` and anything under `.claude/commands/`, `.claude/agents/`, or `.claude/hooks/`
   *if the project uses them*. For a fresh `tasks-app` that's usually just the instructions file.
   Letting the agent stage and commit is the point: from here on you direct the git work and check the
   result.

4. Verify it landed the way you wanted:

   > *"Show me what you just committed."*

   Confirm the commit contains the instructions file and only the files you meant to share (no
   `settings.local.json`, no secrets). This commit is the point of the whole module: the configuration
   now travels with the repo.

### Part B: Watch the AI obey it

5. Start a **fresh** AI session in your editor (so it picks up the file cleanly) and give it a task
   that the instructions constrain. Pick a command your app doesn't have yet (so this is a real
   feature, not a re-add). For example:

   > *"Add a `search <term>` command that lists only the tasks whose title contains `term`. Then
   > confirm it works."*

6. Watch for the file taking effect. A correctly-configured agent should, without you saying any of
   it this time:
   - put the logic where your conventions said it goes (core in `tasks.py`, CLI wiring in `cli.py`);
   - **not** hand-edit `tasks.json` (you marked it off-limits);
   - use the standard library only (no surprise `pip install`);
   - run your stated test/run command before declaring success, instead of inventing one.

   You're checking that behavior you'd normally have to *dictate every session* now happens by
   default. That delta is the file working.

7. If it ignored a rule, that's signal too: tighten the wording, commit the change, and try again.
   Vague instructions get vague compliance; specific, imperative lines ("Never edit `tasks.json` by
   hand; it is generated") land far better than soft ones ("try to avoid editing generated files").

### Part C: Make a behavior change reviewable

8. Now change *how the AI works* and watch it show up as a diff. Direct the AI to add a house-style
   rule to the instructions file, say a hard line length:

   > *"Add this line to the instructions file under house style: `Keep functions under 20 lines; split
   > anything longer.` Don't commit yet; I'll review the diff first."*

9. Before anything gets committed, read the change exactly as a reviewer would. This is your
   verification step, so run it yourself:

   ```bash
   git diff
   ```

   That diff *is* the change to your AI workflow: readable, attributable, revertable. When it's right,
   direct the AI to record it:

   > *"Commit that with a message describing the rule."*

10. Confirm the history. Ask the AI to surface it (or read it yourself):

    > *"Show me the commit history of the instructions file."*

    Every line is a decision about how the AI behaves on this project, recorded rather than lost in
    someone's local settings. (In Module 8 this file reaches your whole team via a remote; in Module 10
    that diff becomes a PR someone reviews before it lands. The habit you just built is what those
    modules turn into a team workflow.)

---

## Where it breaks

Be honest about what a committed instructions file does and doesn't buy you:

- **It's guidance, not a guarantee.** The file biases the model strongly; it does not bind it. An AI
  can still ignore a line, especially a vague one, especially deep in a long session. The enforcement
  that *can't* be ignored (tests that fail the build, scans that block a merge) is **CI
  (Module 14)** and **security scanning (Module 15)**. The instructions file reduces how often the AI
  goes wrong; it doesn't replace the gates that catch it when it does.
- **Bloat kills it.** A 300-line instructions file is read the way *you* read a 300-line terms-of-
  service: not really. Every line you add dilutes the rest. Keep it to what actually changes behavior,
  and prune lines the model already honors without being told.
- **Stale instructions are worse than none.** A file that says "run the tests with `python3 -m
  unittest`" after you've switched to a different runner will actively misdirect the AI. The file is
  code-adjacent: it has to be maintained like code, and reviewed like code. That's exactly why
  committing it (so changes are
  visible) matters.
- **The team payoff isn't here yet.** On a solo local repo, the "no more drift between teammates"
  argument is theoretical: there's only you. The full value lands with a shared remote
  (**Module 8**) and review (**Module 10**). What you get *now* is the habit and the local history;
  don't oversell the team benefit until the team can actually pull the file.
- **It is not a security control.** Telling an agent "don't touch `secrets.env`" is a convention, not
  a permission boundary: a sufficiently confused or adversarial agent can still read or write it.
  Real isolation and least-privilege for agents come later (**Modules 16 and 22**). The instructions
  file expresses intent; it doesn't enforce it.

---

## Check for understanding

**You're done when:**

- Your `tasks-app` repo has a committed instructions file at the root, filled in to match the actual
  project, and `git log` shows the commit that added it.
- You've watched a fresh AI session honor a rule from the file (placing code where your conventions
  said, respecting the don't-touch list, or running your stated test command) *without you saying it
  that session*.
- You've changed a behavior rule, read the change with `git diff`, and committed it, so a change to
  how the AI works is now a reviewable diff with a history.
- You can explain, in one sentence, why committing the file beats each teammate hand-tuning their own
  setup: the configuration travels with the repo, so nobody drifts.

When the AI behaves like it already knows your project the moment you open it, and you didn't say a
word this session, the file is doing its job. Module 6 takes the safety net further: branches, so the
AI can try something wild in a sandbox you can throw away.
