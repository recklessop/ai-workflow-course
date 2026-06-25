# Module 4: Getting the AI Out of the Browser

> **The copy-paste loop from Module 1 ends here.** You stop being the integration layer between a
> chat tab and your files; the AI reads the whole repo and edits the files directly, and you review
> what it did as a diff. This is the literal answer to Module 1, and it's safe *only* because of the
> net you built in Module 2.

---

## Prerequisites

- **Module 1**: you have the `tasks-app` project, an editor, and a terminal, and you've felt the
  three seams where copy-paste breaks. This module closes seam 1 (more than one file) for good.
- **Module 2**: this is the load-bearing prerequisite. You have a Git repo with commits, and you've
  personally watched `git diff` show you a change and `git restore` throw one away. **Do not do this
  module without that.** Letting an AI edit your real files directly is only sane because you can see
  and revert exactly what it did. The safety net comes first; the trapeze act comes second.
- **Module 3** is helpful but not required; you've already practiced the branch / diff / review /
  commit rhythm on low-stakes documents. Here you point that same rhythm at code, with the AI doing
  the editing.

---

## Learning objectives

By the end of this module you can:

1. Name the two categories of "AI out of the browser" tooling (editor-integrated assistants and
   agentic command-line tools) and choose between them on criteria that don't depend on a vendor.
2. Install, authenticate, and point one of them at a real repository, then confirm it can actually
   read the project.
3. Run the agentic edit → review → iterate loop: let the AI change real files, read the change as a
   `git diff`, and direct the AI to keep it (commit) or revert it.
4. Set the tool's permissions deliberately: what it may read, edit, and execute without asking.
5. Explain precisely why this is safe, in terms of Module 2's `restore`.

---

## Key concepts

### What "out of the browser" actually means

In the browser-chat loop, the AI is blindfolded and handcuffed. It can't see your files unless you
paste them in, and it can't change them; it can only hand you text to copy back. *You* are the
integration layer: you decide which files it sees, you apply its output, you are the one who notices
it forgot to update the second file. That's seam 1 from Module 1, and no smarter model fixes it,
because it isn't an intelligence problem, it's an *access* problem.

Getting the AI out of the browser means giving it two things it never had in the chat tab:

1. **Read access to the whole project**: it can open any file, search the repo, and see how the
   pieces fit, without you pasting anything.
2. **Write access to the files**: it edits `tasks.py` and `cli.py` directly, in place, instead of
   printing a new version for you to paste.

Everything in this module follows from those two capabilities. They're also exactly why Module 2 had
to come first: write access to your files is only acceptable when every edit is visible and
reversible.

### From here on, the AI drives git

Modules 1–3 had you type git by hand (`commit`, `branch`, `diff`, `restore`) on purpose. The AI
was stuck in the browser and couldn't touch your repo, so you built the muscle yourself. That was
learning arithmetic by hand before you're handed a calculator.

This module hands you the calculator. Once an agent runs inside your repo it can run commands too,
git included, so the work splits cleanly:

- **You describe the change** and **review the diff** it produces.
- **The AI edits the files and runs git**: it stages, commits, and reverts.
- **You verify the result**: the diff is what you asked for, the checkpoint landed, the tree is clean.

You don't stop understanding git; you stop typing it. The concepts from Modules 2–3 are exactly what
let you check the AI did the right thing. From this module on the course assumes this split: when a
step needs a commit or a revert, you tell the agent and verify its work instead of reaching for the
keyboard. The one thing that stays in your hands is reading the diff.

### The two categories

There are two shapes this tooling comes in. They overlap, and plenty of products do both, but the
distinction is real and worth understanding before you pick.

**Editor-integrated assistants.** These live *inside* a code editor (the graphical kind: VS Code and
its forks, the JetBrains IDEs, and others). They show up as a side panel you chat with, inline
suggestions as you type, and an "agent" or "edit" mode (the part that matters here) that proposes
changes across files, which you accept or reject in the editor's own diff view. The win is that the
review surface is right there: the editor highlights every changed line, and accepting a change is a
click. If you already work in a graphical editor, this is the lowest-friction on-ramp.

**Agentic command-line tools.** These run in your terminal as a standalone program you talk to in
plain language (Claude Code and Aider are two). You launch the tool *inside* your project directory,
and it reads files, runs commands, and edits files on its own, reporting back what it did. They tend
to be more autonomous, better at "go do this multi-step thing," and they're editor-independent, so
they work the same whether you use a graphical editor, a terminal editor, or none. The review surface
is `git diff` itself (Module 2), the same review surface you'll use for everything else in this
course.

| | Editor-integrated assistant | Agentic CLI tool |
|---|---|---|
| **Lives in** | Your graphical editor | Your terminal |
| **Review surface** | The editor's diff view (and `git diff`) | `git diff` |
| **Best at** | Tight inline edits, in-editor review | Multi-step, multi-file, autonomous work |
| **Tied to** | A specific editor | Nothing; works anywhere |
| **On-ramp if you…** | Already live in a graphical editor | Live in the terminal, or run agents headless later |

You do not have to choose forever, and you'll likely end up using both. Pick one to learn the loop
with. The rest of this course is written to work with either.

### How to choose (without crowning a winner)

This space moves fast and the "best" tool changes by the quarter, so evaluate on properties, not
brand:

- **Bring-your-own-model vs. locked model.** Some tools let you point at whichever model/provider you
  want; some bundle one. The course thesis applies directly (*the model is the swappable part*), so
  a tool that lets you swap models is hedging in your favor. (You may still pick a bundled one for
  other reasons; just know what you're trading.)
- **Reads a committed, repo-level instructions file.** You'll want this in Module 5. Most serious
  tools read a project-level instructions file from the repo root. A tool that supports this lets you
  version your AI's configuration like code.
- **Shows diffs before applying, and has an approval mode.** Non-negotiable. You need to see what it
  wants to change and control what it's allowed to do without asking (next section).
- **Works with your editor / OS / shell.** Obvious, but check. Agentic CLIs are the most portable.
- **Cost and where your code goes.** Read the tool's data policy. For work code, know whether your
  files are used for training and whether a self-hosted or local-model path exists (a real concern
  for this audience; it returns in later units).

Don't agonize. Any tool that shows diffs and has an approval mode is good enough to learn the loop.
The loop is the durable skill; the tool is swappable, same as the model.

**We'll use Claude Code as the worked example** from here on, so the commands below are concrete
instead of abstract. It's an agentic CLI; wherever you see `claude`, sub your own agent. The concepts
don't depend on it, same as the model.

### Wiring it up: from browser to repo

The exact clicks differ per tool and drift over time, so here is the shape every one of them
follows. Four steps connect any of them.

**1. Install it.** Editor-integrated assistants install from your editor's extension/plugin
marketplace: search, install, reload. Agentic CLIs install as a command-line program (commonly via a
package manager like `npm`/`pip`/`brew`, or a download) and then exist as a command you run, e.g.:

```bash
claude --version          # sub your agent if using something else
```

**2. Authenticate.** On first run the tool will send you through a sign-in, usually a browser-based
login that drops a token back onto your machine, or a paste-in API key from your provider account.
This is a one-time setup; the credential is stored locally for next time. If the tool lets you choose
a model/provider here, this is where the BYO-model choice from above gets made.

**3. Point it at the repo.** This is the step that has no equivalent in the browser, and it's the
whole point. The convention is **the current working directory is the project**:

```bash
cd ~/ai-workflow-course/tasks-app   # the repo from Modules 1–2
claude                              # launch it from inside the project
```

For an editor-integrated assistant, the equivalent is **open the project folder** (`code .` or
File → Open Folder), exactly as you did in Module 1; the assistant scopes itself to the folder
that's open. Either way, the tool now treats this directory as its world: it can see every file in
it without you pasting a thing.

**4. Confirm it can actually read the project.** Don't assume; verify, the same instinct you'd apply
to any new integration. The check is to ask a question only something that has read your files could
answer:

> *"What does this project do, which files is it split across, and what commands does the CLI
> support?"*

A connected tool answers from the actual files, naming `tasks.py` and `cli.py` and listing `add` /
`list` / `done`:

> *"It's a command-line to-do app. The logic lives in `tasks.py` (a `TaskList` class that persists to
> `tasks.json`), and `cli.py` is the front end that dispatches `add`, `list`, and `done`."*

If instead it asks you to paste code, or describes a generic to-do app it clearly invented, it is
**not** connected to the repo, and everything downstream assumes it can read.

Better still, point it at the *repo's* state, not just the files: *"run `git log`, `git status`, and
`git diff` and tell me where this project is."* An agentic tool runs those itself, so its first act
is reading the durable memory you built in Module 2: the "where were we?" reconstruction, now done
by the AI instead of pasted by you.

### Operating it: the edit → review → iterate loop

Connection is half the module. The other half is what you actually *do* once connected, and it
replaces the entire copy-paste loop with this:

1. **Describe the change** in plain language. Not "here's a file, rewrite it"; *"add a command that
   deletes a task by its index."* The tool decides which files that touches.
2. **The AI edits the files directly.** It opens what it needs, makes the changes in place, and tells
   you what it did. No copying, no pasting, no you-as-integration-layer. This is the moment seam 1
   dies: when the change spans `tasks.py` *and* `cli.py`, the tool edits both, because it can see
   both.
3. **Review the diff.** This is the load-bearing step and it stays in your hands, the Module 2 habit
   unchanged. The AI shows you what it changed: an agentic CLI runs `git diff`, an editor-integrated
   tool shows the same thing in its diff view. You read every line, across every file it touched.
   You're reviewing the AI's work, not trusting it. (The deep version of this skill, spotting the
   plausible-but-wrong change, is Module 10. Here, just build the reflex: *nothing gets committed
   unread.*)
4. **Keep it or revert it: the AI does the git, you verify.**
   - If it's right: tell the AI to commit the reviewed change with a clear message. It stages and
     commits; you confirm the checkpoint landed (`git log`). New checkpoint.
   - If it's *close*: tell the AI what to fix and loop back to step 2. It already has the context.
   - If it's wrong: tell the AI to throw away its uncommitted changes. It runs the restore; you
     verify `git diff` is empty and you're back at your last checkpoint, byte for byte. The mess is
     gone. Try a different prompt.

That fourth step is the entire reason this is safe, so let's be explicit about it.

### Why this is safe: the Module 2 hinge

Letting an AI write to your files directly *sounds* reckless, and in Module 1's world (no version
control, no checkpoints) it would be. The thing that makes it safe is not that the AI is careful.
It isn't, reliably. The thing that makes it safe is that **you committed first, so every edit it
makes is a visible, reversible delta from a known-good state.**

Concretely, the safety contract is:

- **Before you let it loose:** your work is committed and `git status` is clean. (You'll have the
  agent confirm this and commit anything outstanding; you verify it.) That's your restore point.
- **While it works:** every change is on disk, and `git diff` shows you all of it. Nothing is hidden.
- **If it goes wrong:** the agent runs `git restore`, discards every uncommitted edit it made, and
  you're back at the checkpoint with zero retyping. You verify the diff is empty. Module 2's "undo
  for the AI," now an undo the AI even performs for you.

This is the promise Module 2 made cashing out. Module 2 said *every later module asks you to let the
AI do something bolder, and you can say yes because you can always get back to a checkpoint.* This is
the first of those bolder things. The downside of any AI edit is now "throw away a few minutes and
re-prompt," never "lose work," and that asymmetry is what lets you move fast.

> **The one rule:** start from a clean commit. If `git status` shows uncommitted work before you turn
> the AI loose, you've blurred the line between *your* work and *its* work, and `git restore .` will
> throw away both. Commit your stuff first. Then the diff is purely the AI's, and restore is purely an
> undo of the AI.

### Permissions: what it may do without asking

Out of the browser, the AI can do more than edit files; an agentic tool can also *run commands*
(tests, linters, the app itself, git). That's powerful and worth controlling. Every serious tool has
an approval model, usually some version of:

- **Read-only / ask-first**: it proposes every edit and command and waits for your yes. Slowest,
  safest. Start here while you learn a tool's behavior.
- **Auto-edit, ask-to-run**: it edits files freely (you'll review the diff anyway) but asks before
  running commands. A good default once you trust the diff-review habit.
- **Full auto / "just go"**: it edits and runs without asking. Fast, and appropriate only when the
  blast radius is contained: a clean commit to restore to, and ideally an isolated branch (Module 6)
  or a sandbox (Module 16) for anything you don't fully trust.

The right setting is a function of your safety net, not your nerve. With a clean commit you can
afford a looser setting for edits, because the diff is reversible. Be more conservative about letting
it *run* commands unattended: a deleted file is restorable; a command that hits a real external
system may not be. Match the leash to what you can undo.

---

## The AI angle

This module *is* the AI angle of Unit 1; it's where the whole "get out of the chat window" premise
pays off. Map it straight back to Module 1's three seams:

- **Seam 1 (more than one file): solved here.** The tool reads the whole repo, so a change that
  spans `tasks.py` and `cli.py` gets made in both. You are no longer the integration layer holding
  two files in your head.
- **Seam 2 (more than one day): solved by Module 2, *used* here.** A fresh agentic session
  reconstructs "where were we?" by reading `git log` / `status` / `diff` itself, the durable-memory
  reframe from Module 2, now executed by the AI instead of pasted by you.
- **Seam 3 (no undo): solved by Module 2, *required* here.** Direct file edits would be reckless
  without `git restore`. The safety net isn't a nice-to-have for this module; it's the precondition.

The deeper point: notice that *none of this is model-specific.* You didn't get a smarter model. You
gave the same model **access** and wrapped it in **review and revert**. That's the course thesis in
miniature: the workflow around the model did the work, not the model. Swap the model underneath this
loop and the loop is unchanged.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/04-getting-the-ai-out-of-the-browser/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 4"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell + a small Python change *made by the AI, not by you*. You'll drive an agentic
tool; the tool writes the Python.

The goal: wire an agentic editor or CLI tool to the `tasks-app` repo, confirm it can read the
project, and make one **real, reviewed, multi-file** change with it: the exact change that broke the
copy-paste loop back in Module 1, now done right.

**You'll need:**

- The `tasks-app` repo from Modules 1–2, as a Git repo with at least one commit.
- One AI-out-of-the-browser tool. We'll use **Claude Code** as the example; sub your own agent (an
  editor-integrated assistant or another agentic CLI). Use the "How to choose" criteria above; any
  tool that shows diffs and has an approval mode is fine.
- Your model/provider credentials for that tool.
- The verify script in this module's `lab/verify.sh`. **Convention for every lab script from here on:**
  the course's scripts live under `~/ai-workflow-course/modules/NN/lab/`, but your `tasks-app` is a
  separate folder (Module 1), so when a step runs one, **copy the script into `tasks-app` first, then
  run it by name**. (Paths below assume the course unzipped to `~/ai-workflow-course/`; adjust if you
  put it elsewhere.)

### Part A: Wire it up and confirm it can read

1. Install the tool and authenticate it (steps 1–2 in "Wiring it up").

2. Point it at the repo (step 3): `cd ~/ai-workflow-course/tasks-app` and launch `claude` from there,
   **or** open that folder in your editor and open the assistant's agent panel.

3. **Confirm read access** (step 4). Ask it the read-check question from "Wiring it up." You're
   connected only if it answers from the real files; if it asks you to paste code, fix the wiring
   before continuing.

### Part B: Start from a clean checkpoint

4. This is the one rule: start clean, so the AI's change is the *only* thing in the next diff. **Tell
   the agent to set the checkpoint**, then verify it yourself. Ask:

   > *"Check `git status`. If anything's uncommitted, commit it with a clear message so we start from
   > a clean tree."*

   Then confirm with your own eyes:

   ```bash
   git status        # you check: "nothing to commit, working tree clean"
   ```

   Now you have a known-good restore point, and anything that appears in `git diff` next is purely
   the AI's. (Notice you directed the commit and verified the result; you didn't type it. That's the
   split for every git step from here on.)

### Part C: Make a real multi-file change

5. Ask the tool (in plain language, letting *it* decide which files to touch) for the change that
   needs both files:

   > *"Add a `delete <index>` command to the task app that removes the task at the given index. Put
   > the removal logic in the TaskList class in `tasks.py` and wire the command up in `cli.py`. Match
   > the existing code style and update the usage string."*

   Let it edit the files directly. Do **not** copy anything by hand; if you find yourself pasting,
   the tool isn't actually wired to the repo (back to Part A).

6. **Review the diff before you trust a line of it:**

   ```bash
   git diff
   ```

   Confirm with your own eyes: a new method on `TaskList` in `tasks.py`, a new `delete` branch in
   `cli.py`'s command dispatch, the usage string updated, and **nothing touched that shouldn't be.**
   This is the review reflex. Two files changed, and you didn't merge them by hand. That's seam 1,
   gone.

7. **Verify it runs.** Use the provided script, which exercises the new command end to end across
   both files. Copy it into `tasks-app` first (see *You'll need*), then run it from there:

   ```bash
   cp ~/ai-workflow-course/modules/04-getting-the-ai-out-of-the-browser/lab/verify.sh .
   bash verify.sh
   ```

   It should add tasks, delete one by index, and confirm the right task remains. If it fails, don't
   hand-fix it; tell the AI what broke and let it iterate (step 4 of the loop), then re-run.

8. **Commit the reviewed change: tell the agent, then verify.** It passed your own eyes and it
   passes the check, so lock it in. Ask the agent:

   > *"Commit this with the message 'Add delete command (made via editor/CLI agent)'."*

   It stages and commits. You verify the checkpoint landed:

   ```bash
   git log --oneline   # your new commit is on top
   ```

   You just shipped a reviewed, multi-file change an AI made by editing your files directly, and you
   never typed the commit. This commit is now the clean state the AI's `git restore` falls back to in
   the next part.

### Part D: Practice the revert (do this even though it works)

9. You only trust an undo you've used. Your tree is clean (you just committed in Part C, exactly the
   safe setup the one rule demands). Prove the net is under you. Ask the tool for a deliberately
   throwaway change:

   > *"Rename every variable in `tasks.py` to single letters."*

   Let it apply it, glance at `git diff` to see the damage, then **tell the agent to undo it**:

   > *"Throw away everything you just did and get us back to the last commit."*

   It runs the restore. Now you verify the rescue:

   ```bash
   git diff           # empty: the AI's mess is gone, byte for byte
   bash verify.sh     # still passes: you're back at your good state (you copied it in at step 7)
   ```

   That's the Module 2 safety net catching a Module 4 mistake, and the AI even performed the undo on
   your word. Internalize how cheap that was.

### Part E: Confirm you're back at your good state

10. Nothing left to commit: the `delete` feature went in back in Part C, and Part D's throwaway is
    already gone. Confirm the reviewed multi-file commit is your latest and the tree is clean:

    ```bash
    git log --oneline   # "Add delete command…" is the latest commit
    git status          # clean: the throwaway left no trace
    ```

    That's the whole loop closed: a reviewed, multi-file change the AI made across both files is
    committed, and the mess you made on purpose vanished without touching it.

---

## Where it breaks

Be honest about the limits of working this way:

- **Access is not judgment.** The AI reading your whole repo makes it *informed*, not *correct*. It
  will still make confident, plausible, wrong changes, now across multiple files at once, which is a
  bigger mess to read. The diff review in step 3 of the loop is not optional, and the deep version of
  that skill is a whole module of its own (Module 10). The tool removed the copy-paste; it did not
  remove the reviewing.
- **`git restore .` only saves you if you committed first.** This is the one rule for a reason. If
  you let the AI loose on a dirty tree, restore can't tell your work from its work and throws away
  both. The discipline that makes this module safe is *commit before you turn it loose*, the same
  "commit often" lesson from Module 2, now with teeth.
- **It can do more than edit: watch what it runs.** An agentic tool that can run commands can do
  things `git restore` cannot undo: delete files outside the repo, hit a network service, mutate a
  database. Restore covers *versioned files only* (Module 2's honest limit, still true). Keep the
  run-commands leash tighter than the edit-files leash until you've built the heavier isolation later
  (branches in Module 6, containers in Module 16).
- **Big autonomous changes outrun your review.** A tool set to "just go" can produce a 12-file diff
  faster than you can read it, and an unread diff is just copy-paste with extra steps. Keep changes
  small enough to actually review. Scoping work into small, reviewable pieces is a skill the rest of
  the course leans on hard.
- **The wiring drifts.** Install steps, auth flows, approval-mode names, and model pickers change
  between tool versions. The four-step *shape* (install → authenticate → point at repo → confirm it
  reads) is stable; the exact clicks are not. When in doubt, the "confirm it can read" test tells you
  truthfully whether you're connected.

---

## Check for understanding

**You're done when:**

- An agentic editor or CLI tool is wired to your `tasks-app` repo and correctly answers "what does
  this project do and which files is it in?" from the actual files, no pasting.
- You have a committed `delete` command that you watched the AI write across **both** `tasks.py` and
  `cli.py`, that you reviewed with `git diff` before committing, and that `bash verify.sh` passes
  (after copying `verify.sh` into `tasks-app`).
- You have, on purpose, let the AI make a change and then erased it with `git restore .`, watching
  `git diff` go empty.
- You can explain, in one sentence, why letting an AI edit your files directly is safe, and your
  sentence mentions the clean commit you start from and the `restore` you can fall back to.

When making a multi-file change feels like "describe it, read the diff, keep it or restore it," and
the browser copy-paste loop feels like a thing you used to do, you've got it. Module 5 takes the next
step: now that the AI is operating *in* your repo, you commit its *configuration* into the repo too,
so the setup you just did becomes a durable, shared, reviewable artifact instead of something every
teammate re-tunes by hand.

---

## Verify-before-publish

This is durable-core, but the wiring instructions touch tool surfaces that drift. Re-check at build
time:

- [ ] The two categories (editor-integrated assistants; agentic CLI tools) still describe the market,
      and no single tool has become so dominant that "agnostic" reads as evasive; if so, name it as
      *the common default* the way the syllabus treats GitHub in Module 8, without crowning it.
- [ ] The four-step wiring shape (install → authenticate → point at repo → confirm it reads) still
      matches how current tools onboard; update the install-command examples if package-manager
      conventions have shifted.
- [ ] The approval/permission model still maps to roughly read-only / auto-edit / full-auto across
      current tools; update the labels if the common terminology has moved.
- [ ] `lab/verify.sh` still passes against the Module 1 `tasks-app` after an AI implements `delete`.
