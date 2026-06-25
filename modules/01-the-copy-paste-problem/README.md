# Module 1: The Copy-Paste Problem

> **You can already get an AI to write good code. The thing that's failing you is everything around
> the code.** This module names that gap honestly and gets your workspace ready to close it.

---

## Prerequisites

None. This is the orientation module. You need to be comfortable using an AI chat assistant and have
a machine you can install software on. That's the whole entry requirement.

If you've never opened a terminal, this course will stretch you, but it won't lose you: every
command is shown and explained.

---

## Learning objectives

By the end of this module you can:

1. Articulate *why* the chat-to-file copy-paste loop fails: not vaguely, but at the three specific
   seams where it breaks.
2. State the course thesis and explain what "the workflow is the durable skill" means for your own
   work.
3. Stand up a real local project: a project folder, a code editor, and a working terminal.
4. Reproduce the copy-paste failure on purpose, so you recognize it instantly when it bites you for
   real.

---

## Key concepts

### The loop you're in right now

Here is the workflow almost everyone starts with, and it genuinely works for a while:

1. Describe what you want in a chat window.
2. The AI produces code.
3. You copy it.
4. You paste it into a file in your editor.
5. You run it.
6. Something's off, so you copy the error *back* into the chat.
7. Go to 2.

For a single file you're poking at for an afternoon, this is fine. The friction is low and the
results are real. The problem isn't that this loop is *bad*. It's that the loop **doesn't scale along
the two axes every real project grows on: more than one file, and more than one day.**

### Seam 1: More than one file

The moment your project is two files instead of one, the chat window loses the thread. You paste in
`cli.py`, ask for a change, and the AI confidently edits it. But the change actually needed to touch
`tasks.py` too, which it can't see because you only pasted one file. Or it *can* see it because you
pasted both, but now its reply rewrites both files and you're hand-merging two blobs of text back
into two real files, hoping you didn't drop a function in the shuffle.

You become the integration layer. Every change is a manual diff you perform in your head, between
what's in the chat and what's on disk. That's slow, and worse, it's *error-prone in a way you can't
see*: there's no record of what actually changed.

### Seam 2: More than one day

Close the chat tab, come back tomorrow, and the AI's entire working memory is gone. It doesn't know
what you decided yesterday, which approach you rejected, or why that one function looks weird (you
had a reason). The context that lived in the conversation evaporated when the session ended.

So you re-explain. You re-paste. You reconstruct yesterday from memory, and your memory is worse
than you think. The project's real state lives on your disk, but the chat has no way to read your
disk, so every session starts cold.

### Seam 3: No undo, no record, no safety

This is the quiet one, and it's the most dangerous. The AI confidently makes a mess. It deletes a
function you needed, "refactors" something into a subtly broken state, rewrites a file you'd carefully
tuned. What's your recovery plan?

Right now it's probably: *Ctrl-Z until it looks right*, or *paste the old version back from the chat
history if I can find it*, or, too often, *retype it from memory*. There is no checkpoint you can
return to and no record of what changed between "working" and "broken." You're doing high-wire work
with no net, and the AI makes it *easier* to do a lot of risky changes fast. So you fall more often.

### The reframe

Notice what all three seams have in common: **none of them are about the AI's intelligence.** A
smarter model writes better code, but it doesn't give you a record of changes, a way to undo a mess,
or a memory that survives a closed tab. Those come from the *engineering scaffolding around* the
model: version control, a real editor integration, hosting, review, automation.

That scaffolding is what this course teaches. And here's why it's worth your time specifically now:

> **The model is the cheap, swappable part. The workflow around it is the skill that lasts.**

Models change every few months. The one you're using today will be replaced, probably by something
cheaper and better, and when that happens your prompts mostly carry over and your habits fully
carry over. The version-control discipline, the review reflex, the CI pipeline, the way you give an
agent a branch instead of your whole repo: *none of that depends on which model you run.* You learn
it once and it pays out across every model you'll ever use. That's why this course is deliberately
model- and vendor-agnostic. We're teaching the part that doesn't expire.

---

## The AI angle

A generic "intro to developer tools" course would teach the same git, the same editors, the same
CI. What makes this one different is that **AI changes the cost-benefit of every tool in it**, and
usually makes the tool *more* valuable, not less:

- AI makes changes **faster and more confidently**, including the wrong ones. That raises the value
  of an undo you can trust (Module 2) and a review gate (Module 10).
- AI **can't remember** across sessions, but your repo can. Version control becomes durable memory
  the AI reads back (Module 2).
- AI generates code that **looks right** and passes a human skim. That's exactly what automated
  testing and CI exist to catch (Modules 13–14).
- AI itself can become a **teammate inside the workflow**, opening PRs, triaging issues, fixing
  failing builds, but only safely once the scaffolding is there to catch it (Unit 5).

You don't adopt this toolchain *despite* using AI. You adopt it *because* you're using AI. The pain
you already feel is the curriculum.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/01-the-copy-paste-problem/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 1"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell + a tiny bit of Python (just enough to have something real to run). You will
not write Python; you'll run a small app we provide.

The goal of this lab is twofold: get your workspace stood up, and **feel the copy-paste problem on
purpose** so you recognize it later.

**You'll need:**

- A terminal (Terminal on macOS/Linux, or Windows Terminal / PowerShell on Windows).
- A code editor. Any will do; a graphical editor like VS Code is the easiest starting point because
  later modules build on editor-integrated AI tools.
- Python 3.10 or newer (`python --version` or `python3 --version` to check).
- Your usual AI chat assistant, open in a browser tab.

> **One command name, the whole course through:** the labs are written with `python3`, the command
> name current macOS and default Debian/Ubuntu actually ship (they install Python only as `python3`,
> with no bare `python` on PATH). Run `python3 --version`; if it prints a 3.10+ version, use `python3`
> in *every* lab from here on. If `python3` is "command not found" but `python --version` shows a
> 3.10+ version (older or some Windows setups), read every `python3` in the labs as `python` instead.
> Where a lab runs `pip`, use whichever pairs with your Python (`pip3` commonly goes with `python3`).
> This note holds course-wide; we won't repeat it.

### Get the course materials

Everything you'll run in this course lives in one repo. Grab it once, up front; no tools required
beyond a web browser:

1. Open the course's home page, **`https://github.com/recklessop/ai-workflow-course`**, and use its
   **Download ZIP** (archive) link.
2. Unzip it under your home directory so the course's `modules/` folder lands at
   `~/ai-workflow-course/modules/`. (Rename the unzipped folder to `ai-workflow-course` if your download
   named it something else.)

You now have every module's files locally, including this one's under
`modules/01-the-copy-paste-problem/`.

> *A cleaner, **updatable** way to get the repo, `git clone`, arrives in **Module 8**, once you've
> learned Git (Module 2). A one-time ZIP is all you need today; don't reach for `clone` yet.*

### Part A: Stand up the project

1. Make a working directory and copy in the starter app from this module's `lab/starter/` folder:

   ```bash
   mkdir -p ~/ai-workflow-course/tasks-app
   cd ~/ai-workflow-course/tasks-app
   # copy the three files from modules/01-the-copy-paste-problem/lab/starter/ into here:
   #   tasks.py  cli.py  README.md
   ```

   (Copy them however you like; drag-and-drop in your editor's file explorer is fine.)

   > **On Windows:** these labs' shell snippets are written for bash; run them from **Git Bash** or
   > **WSL** and they work as-is. In native PowerShell a few POSIX-only commands differ; here, `mkdir
   > -p` becomes `New-Item -ItemType Directory -Force`.

2. Open the folder in your editor (`code .` if you're using VS Code, or File → Open Folder).

3. Run it in your terminal to confirm it works:

   ```bash
   python3 cli.py add "finish module 1"
   python3 cli.py list
   ```

   You should see your task listed. **This is your "real local project, an editor, and a terminal."**
   That's the Module 1 setup goal, complete.

### Part B: Feel the seams

Now reproduce each failure deliberately. Keep the AI strictly in the **browser chat**; no
editor-integrated tools yet (those arrive in Module 4). This is the "before" picture on purpose.

1. **Seam 1 (multiple files).** First mark a task done so there's something to hide. Run `python3
   cli.py done 0`, then `python3 cli.py list` shows it as `[x]`. Now paste *only* `cli.py` into your
   chat and ask: *"Make the `list` command hide tasks that are already done."* Apply whatever it
   gives you and run `python3 cli.py list`. The clean version of this change lives in `tasks.py`, the
   file you *didn't* paste: open it and you'll see `render()` already owns the `[x]`/`[ ]`
   box-and-index formatting, and a `pending()` helper already returns exactly the not-done tasks. But
   the chat never saw that file, so it had to do one of two things. Either it guessed at methods it
   couldn't see (and `python3 cli.py list` errors out), or it reached into the raw task list and
   *re-created* that box-and-index formatting inside `cli.py`, duplicating logic that already existed
   one file over. Either way, *you* had to be the one who knew the change really belonged in the
   other file.

2. **Seam 2 (across time).** Close the chat tab. Open a new one. Ask it to *"continue where we left
   off."* Watch it have no idea what you were doing. The project's real state is sitting right there
   on your disk, and the chat can't read a byte of it.

3. **Seam 3 (no undo).** Paste a file into the chat and ask it to *"refactor this to be cleaner,"*
   then paste the result back over your file without reading it closely. Now try to get back to the
   exact version you had five minutes ago. Notice that your only recovery options are editor undo
   (fragile, gone once you close the file) and the chat history (if you can find the right message).
   There is no checkpoint.

You just manually reproduced the three problems the rest of Unit 1 removes. Hold onto that feeling;
it's the motivation for everything that follows.

---

## Where it breaks

Be honest about the limits of this module's claims:

- **Copy-paste isn't *wrong*, it's *unscalable*.** For a one-file throwaway script, the loop is
  genuinely the fastest path. Don't over-engineer a five-line utility. The toolchain earns its keep
  as soon as a project has a second file or a second day, which is most of them, but not all.
- **Tools don't fix judgment.** Version control will let you undo a bad AI change instantly; it won't
  tell you the change was bad. That skill, reviewing AI output, is its own module (10), and no
  amount of scaffolding replaces it.
- **This module doesn't make you faster yet.** Setup rarely does. The payoff compounds over the next
  six modules. If it feels like overhead right now, that's expected.

---

## Check for understanding

**You're done when:**

- You can run `python3 cli.py list` in your terminal and see output; your project, editor, and
  terminal are working together.
- You can name the three seams where copy-paste breaks (more than one file, more than one day, no
  undo) without looking back at the lesson.
- You can state the thesis in your own words: the model is swappable; the workflow is the durable
  skill.

If all three are true, you're ready for Module 2, where we install the safety net that makes the
rest of the course safe to attempt.

---

## Verify-before-publish

- [ ] Confirm the **Download ZIP** URL (`https://github.com/recklessop/ai-workflow-course`) points at
      the published course host before shipping.
