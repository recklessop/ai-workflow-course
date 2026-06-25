# Module 3: Version Control for Words, Not Just Code

> **The safest place to practice Git is on words, and it happens to be a genuinely useful skill on
> its own.** Branch an Architecture Decision Record (ADR), let the AI draft it, read the diff, merge
> it. Nothing breaks if it's wrong, so you build the muscle before the agent ever touches code.

---

## Prerequisites

- **Module 1:** you have the `tasks-app` project, an editor, and a terminal.
- **Module 2:** you can `init`, `commit`, read a `diff`, and `restore`. This module adds two new
  verbs to that vocabulary: `branch` and `merge`. They're introduced here, in the lowest-stakes
  setting possible (a markdown file), and picked up again for real code work in
  **Module 6 (Branches: Sandboxes for Experiments)**.

You're still working the way you did in Modules 1–2: **AI in a browser tab, copy-paste into the
file.** Editor-integrated AI is Module 4. That's deliberate; practicing branch/merge on documents
is exactly the low-risk on-ramp that makes the copy-paste friction tolerable one more time.

---

## Learning objectives

By the end of this module you can:

1. Explain why plain-text formats (markdown, AsciiDoc) version cleanly while `.docx`/`.pptx` version
   uselessly, and make the case to move a runbook or ADR out of Word.
2. Create a branch, do work on it, and merge it back. That's the full branch → diff → commit → merge
   loop, run on a document where a mistake costs nothing.
3. Have an AI draft a real engineering document (an ADR or a runbook) and review its work as a diff
   before accepting it.
4. Recognize that the wikis on most Git hosts are themselves Git repositories, so the docs you
   thought lived "in a web UI" were version-controlled all along.

---

## Key concepts

### The three seams apply to documents too

Module 1 named the three places the copy-paste loop breaks: more than one file, more than one day,
no undo. Documents have every one of those problems, and most teams feel them *worse* than they feel
them in code:

- **More than one document.** A runbook references an ADR that references a spec. Change the decision
  and three documents are now subtly out of sync, with no record of which changed when.
- **More than one day.** "Why did we decide to store state as JSON instead of SQLite?" The answer
  lived in a meeting, or a Slack thread, or someone's head. Six months later it's gone.
- **No undo.** Someone edits the runbook during an incident, gets it wrong, and there's no clean way
  back to the version that was correct an hour ago. `runbook-final-v2-ACTUAL-use-this.docx` is what
  "no undo" looks like when it metastasizes.

Git fixes all three for documents the same way it fixes them for code, but only *if* the documents
are in a format Git can actually work with. That "if" is the whole argument.

### Why plain text wins: the diff is line-based

Git's core operation is the line-based diff. It compares two snapshots and reports which **lines**
changed. Everything good about Git (readable history, reviewable changes, automatic merges) is
built on that one capability. So a format versions well in exact proportion to how well it maps onto
*lines of text*.

Markdown and AsciiDoc are just text. Change one sentence in a markdown runbook and `git diff` shows
you exactly that:

```diff
-Restart the worker with `systemctl restart tasks-worker`.
+Restart the worker with `systemctl restart tasks-worker`, then tail the log for 30s to confirm.
```

That is a perfect change record. A reviewer reads it in two seconds. Two people can edit different
sections and Git merges them automatically, because the changes touch different lines.

Now do the same edit in a `.docx`. A Word document isn't text; it's a zipped bundle of XML, styles,
and metadata. Git happily tracks it, but it can't diff it meaningfully. Ask for the diff and you get:

```
Binary files a/runbook.docx and b/runbook.docx differ
```

That's it. That's the entire change record: *something* changed. You can't see *what*, you can't
review it, and you can't merge two people's edits; Git will force you to pick one whole file and
throw the other away. The version history exists and is **completely useless**. `.pptx` is worse,
because slide decks are even more structure and even less text.

This is a real, defensible engineering argument, not a style preference:

> **Runbooks, ADRs, specs, and changelogs belong in markdown in the repo, not in Word on a shared
> drive.** The moment a document needs history, review, or more than one author, a binary format is
> actively costing you the thing version control exists to provide.

The honest counterpoint, where binary formats still earn their place, is in *Where it breaks*.

### The document types worth versioning

You don't need to convert everything. These are the high-value targets, all naturally plain text:

- **READMEs:** how to run the thing. Already markdown by convention; you saw `tasks-app/README.md`
  in Module 1.
- **ADRs (Architecture Decision Records):** short documents that capture *one* decision: the
  context, the choice, and the consequences. The point is to make the *reasoning* survive the
  meeting. An ADR lives next to the code, gets versioned with it, and answers "why is it like this?"
  long after everyone's forgotten.
- **Runbooks:** the step-by-step for an operational task (deploy, restore, rotate a key, respond to
  an alert). These get edited under pressure, which is exactly when you want clean history and undo.
- **Changelogs:** what changed in each release. A markdown `CHANGELOG.md` is the standard.
- **Specs / PRDs:** what you're going to build and why, before you build it.

For this audience the ADR is the easiest win: small, structured, high-value, and the kind of thing
that *never* gets written because it feels like overhead, right up until the AI drafts it for you in
ten seconds.

### Branch → diff → commit → merge (the new verbs)

Module 2 worked on a straight line of commits. A **branch** is a second line you can work on without
disturbing the first. The mental model: `main` is the version everyone trusts; a branch is a private
copy where you draft something, and **merge** folds your finished work back into `main`.

Creating a branch is one command, and `git branch` shows you which line you're on:

```console
$ git switch -c docs/adr-storage
Switched to a new branch 'docs/adr-storage'
$ git branch
* docs/adr-storage
  main
```

The `*` marks your current branch. From there, the loop for a document is the same handful of verbs
every time: **draft** the doc (with the AI's help), **stage** it, read the **diff**, **commit** it on
the branch, **switch** back to `main`, then **merge** to fold the finished work in and delete the
spent branch. You'll run that whole sequence by hand in the lab; here, just hold the shape.

Two new-command notes for this audience:

- **`git switch -c <name>`** creates and moves onto a branch. (Older docs and muscle memory use
  `git checkout -b <name>`; `switch` is the newer, clearer verb for the same thing. Either works.)
- **`git diff` shows nothing for a brand-new file** until Git is tracking it; new files are
  "untracked," and `git diff` only compares *tracked* changes. That's why the loop above does
  `git add` *then* `git diff --staged` (also spelled `--cached`): staging tells Git "track this," and
  `--staged` shows you what's staged. For a new file the diff is all-additions, which is fine; you're
  still reading every line before it lands.

Because this is one document on its own branch, the merge is trivial: nothing else touched `main`
while you worked, so Git **fast-forwards**; it just slides `main` up to your branch with no
conflict. That clean case is the whole reason we practice here first. What happens when two branches
edit the *same lines* (a merge conflict) is a real skill, and it gets its own treatment in
**Module 6**, on code, where the stakes make it worth the depth. Practice the happy path now; the
hard path is easier once the verbs are reflexes.

### The aha: your wiki was a Git repo all along

Most Git hosts (GitHub, GitLab, Gitea, and others) ship a **wiki** alongside each repository. It
looks like a web app: you click "New Page," type in a box, hit save. It feels like a different kind
of thing from your code.

It isn't. On essentially every one of these hosts, **the wiki is itself a Git repository**, a
separate repo, usually addressable as something like `your-project.wiki.git`, full of markdown files.
Every page is a `.md` file. Every "save" in the web UI is a commit. The web editor is just a
convenience layer over `git commit`.

The consequence: the documentation you've been editing in a browser textbox has had full version
history (diffs, blame, the works) the entire time. You can clone it, edit the markdown locally with
the same branch/diff/merge loop you're learning here, and push it back. (Cloning and pushing to a
remote repo is **Module 8** (remotes and hosting), so you can't do the clone in *this* lab yet. But
the realization changes how you see every wiki you'll ever touch: it's not a CMS, it's a repo
wearing a web UI.)

---

## The AI angle

Here's why this module is more than "learn Git on easy mode":

- **LLMs are native markdown writers.** Markdown is arguably the *most* fluent output format these
  models have; they were trained on oceans of it, and they reach for it by default. Asking an AI to
  "write an ADR for this decision" or "turn these rough notes into a runbook" plays directly to its
  strengths. The output is genuinely good and genuinely in the right format, with zero conversion.
- **"Draft it, branch it, diff it, merge it" works today.** You don't need new tools, a new model, or
  editor integration. The whole workflow (branch, paste the AI's draft into a `.md` file, read the
  diff, merge) runs on the browser chat you already have open. Most of the rest of this course is
  capability you have to build up to; this part you can put to work right now.
- **Reading the diff is how you review AI writing.** Same skill as reviewing AI code (Module 10), lower
  stakes. The AI will write an ADR that *sounds* authoritative and confidently states a rationale it
  invented. Reading the diff is how you catch "wait, that's not why we did this." The format makes the
  review possible; your judgment makes it correct.
- **It seeds a habit the whole course depends on.** Once "the AI drafts, I review the diff, I decide"
  is reflexive on documents, where a mistake costs nothing, you'll apply it without thinking when
  the AI starts editing code, opening PRs, and running unattended later on.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/03-version-control-for-words/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 3"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Git commands) plus a little markdown writing, on the `tasks-app` from
Modules 1–2. The AI stays in the **browser**; you copy its draft into the file yourself, exactly as
in Module 2.

In this lab you'll branch the repo, have the AI draft an **Architecture Decision Record**, review it
as a diff, and merge it into `main`. The document is real and the workflow is real; only the risk is
zero.

**You'll need:**

- Your `tasks-app` folder, already a Git repo with a clean working tree from Module 2
  (`git status` should say "nothing to commit, working tree clean").
- Git installed and your AI assistant open in a browser tab.
- The ADR template from this module's `lab/adr-template.md` (and `lab/runbook-template.md` if you
  want to do the variant at the end).

### Part A: Branch for the document

1. Confirm you're starting clean, then create a branch for the ADR:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   git status                       # want: "working tree clean"
   git switch -c docs/adr-storage   # new branch, named for what it's for
   git branch                       # the * shows you're on docs/adr-storage now
   ```

   You're now working on a copy. Nothing you do here touches `main` until you merge.

### Part B: Let the AI draft the ADR

2. Make a home for decision records:

   ```bash
   mkdir -p docs/adr
   ```

3. Open `adr-template.md` from this module's `lab/` folder in the course repo (wherever you downloaded
   it; it lives in the course repo, *not* inside `tasks-app`). In your browser chat, give the AI that
   template plus the context and ask for the draft:

   > *"Here's an ADR template (paste the contents of `adr-template.md`). Fill it out for this decision:
   > the `tasks-app` CLI stores its state in a plain `tasks.json` file next to the code. We chose JSON
   > over SQLite or a hosted database because the app is a single-user local tool and zero-setup
   > matters more than query power. Keep it concise. Output markdown."*

4. Now create the file and paste the draft in. In your editor, make a new file at this exact path
   inside `tasks-app`:

   ```
   docs/adr/0001-task-storage-format.md
   ```

   Paste the AI's markdown into it and save. (This is the copy-paste loop from Module 1, the last
   stretch before Module 4 removes it.) The file has to exist on disk before the next part can stage
   it.

### Part C: Review the diff before you accept it

5. A brand-new file is untracked, so `git diff` shows nothing yet. Stage it, then review:

   ```bash
   git status                       # the new file shows as "untracked"
   git add docs/adr/0001-task-storage-format.md
   git diff --staged                # every line of the new doc, as additions
   ```

   **Read it.** This is the point of the whole module: don't accept AI writing you haven't read. Check
   the *substance*, not just that it's well-formatted. Did it state a rationale you actually agree
   with, or did it invent a confident-sounding reason? If it's wrong, edit the file and `git add`
   again.

6. When it's right, commit it on the branch:

   ```bash
   git commit -m "Add ADR 0001: store tasks as JSON"
   git log --oneline                # your new checkpoint, on this branch
   ```

### Part D: Make a one-line edit and see the line-based diff

7. Edit one sentence in the ADR (tighten a line, fix a claim, whatever). Save, then:

   ```bash
   git diff
   ```

   Notice the diff shows **only the line you changed**, in context. That clean, surgical record is the
   thing a `.docx` can never give you. Commit it:

   ```bash
   git add docs/adr/0001-task-storage-format.md
   git commit -m "Tighten ADR 0001 rationale"
   ```

### Part E: Merge it into main

8. First, switch back to `main` and prove the document isn't there yet. You created the whole
   `docs/adr/` directory on the branch, so on `main` it doesn't exist:

   ```bash
   git switch main
   ls docs/adr/                     # error: "No such file or directory", only on the branch
   git log --oneline                # and your ADR commits aren't here either
   ```

   That's branch isolation: the work is real and committed, but completely invisible to `main` until
   you merge. Now fold it in and watch the file appear:

   ```bash
   git merge docs/adr-storage       # fast-forward, no conflict
   git log --oneline                # the ADR commits are on main now
   ls docs/adr/                     # and the file is here too
   ```

9. Clean up the branch. Its work now lives in `main`:

   ```bash
   git branch -d docs/adr-storage
   ```

You just ran the complete branch → draft → diff → commit → merge loop on a real document, with the AI
doing the writing and you doing the reviewing. That's the loop the rest of the course runs on.

### Optional: do it again as a runbook

Repeat the loop on a different branch (`git switch -c docs/runbook-restore`) using
`runbook-template.md` from this module's `lab/` folder: ask the AI to write a runbook for "restore the
tasks list after someone deletes `tasks.json` by accident," given that the app recreates an empty list
on next run. Same five parts. Doing it twice is what turns the commands into reflexes.

---

## Where it breaks

- **Line-based diffs punish reflowed paragraphs.** Git diffs *lines*. If you (or the AI) rewrap a
  paragraph so every line shifts, the diff shows the whole paragraph as changed even if you altered
  three words; the clean diff degrades toward `.docx`-style noise. The fix the technical-writing
  world uses is **semantic line breaks**: write one sentence (or one clause) per line, so edits stay
  local and diffs stay surgical. Worth knowing the AI will *not* do this by default; you can ask it
  to.
- **Plain text isn't free of binaries.** A markdown doc with screenshots still carries `.png` files,
  and Git diffs those as "binary files differ" just like a `.docx`. Git tracks and stores them fine;
  it just can't show you what changed inside them. Diagrams-as-code (text formats that render to
  pictures) sidestep this, but that's beyond this module.
- **Word and PowerPoint still exist for reasons.** A pixel-precise client deliverable, a slide deck
  with heavy layout, a document a non-technical stakeholder must edit in a tool they already know.
  These are real constraints. The argument isn't "markdown for everything." It's "anything that needs
  history, review, or multiple authors is paying a steep tax in a binary format." Pick the targets
  where that tax actually bites: runbooks, ADRs, specs, changelogs.
- **Merge conflicts are real; you just didn't hit one.** This lab fast-forwarded because nothing else
  touched `main`. The moment two branches edit the same lines, Git stops and asks *you* to resolve it.
  That's a genuine skill, deferred to **Module 6** on purpose so you learn it where the stakes make it
  matter.
- **The wiki-clone aha needs a remote.** You can *see* that a host's wiki is a Git repo now, but
  cloning it, editing locally, and pushing back requires remotes, which is **Module 8**. The realization is
  yours today; the round trip waits a few modules.
- **The AI writes confident fiction.** It will produce a fluent ADR with a rationale that sounds
  exactly like something a senior engineer wrote, and is sometimes simply made up. The format makes
  the document reviewable; it does not make the document *true*. Reading the diff is necessary, not
  sufficient. You still have to know whether the reasoning is right.

---

## Check for understanding

**You're done when:**

- Your `tasks-app` repo has an `docs/adr/0001-*.md` on `main`, authored by the AI and reviewed by you,
  arrived there via a branch and a merge.
- You created a branch, committed to it, merged it back, and deleted it; `git log --oneline` on
  `main` shows the ADR commits.
- You can explain, to a skeptical colleague, why the team's runbooks shouldn't be `.docx` files on a
  shared drive, using the line-based-diff argument, not just "markdown is nicer."
- You know that your Git host's wiki is itself a Git repo, and what that implies.

When branch/diff/commit/merge feels routine on a document, you're ready for **Module 4**, where the AI
finally comes out of the browser and starts editing your files directly, a step that's only safe
because you can now branch, diff, and revert exactly what it does.
