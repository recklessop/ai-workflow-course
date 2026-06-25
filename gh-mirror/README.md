# The Workflow
### The Toolchain Around AI Coding

A living course for IT professionals who are comfortable in an AI chat window and starting to build
real software with it, but who are still copy-pasting between the chat and their files. The goal is
to replace that loop with durable engineering workflows: version control, collaboration, CI/CD,
runners, and the tools that extend AI into real systems.

> **Thesis:** the model is the cheap, swappable part. The workflow around it is the skill that
> lasts. This course is deliberately model- and vendor-agnostic: whichever LLM you use, the
> scaffolding is the same.

This repo *is* the course, and it also dogfoods the course: it's version-controlled, it commits its
own AI instructions file ([`AGENTS.md`](AGENTS.md), the subject of Module 5), and each module is
built on a branch and merged through review, the same motion the modules teach.

---

## Read it as a book

The lessons render into the **[Wiki](https://github.com/recklessop/ai-workflow-course/wiki)** as a
navigable textbook (unit-by-unit sidebar, one page per module, prev/next links). The wiki is
generated from `modules/` and kept in sync automatically; it's build output, so read it there but
**edit the lessons here in `modules/`**. See [`tools/`](tools/) for the generator and the sync
workflows.

---

## Who this is for

IT professionals who are fluent in an AI chat window and comfortable with ops concepts. Not
beginners. If you already paste code between a chat tab and your editor and feel the friction, you
are the audience. You will not be taught what a variable is; you will be taught the engineering
scaffolding that makes AI-assisted work safe, shareable, and repeatable.

---

## How the course is built

It's a **dependency chain, not a topic list.** Every module assumes only what the previous ones
taught, and nothing references a tool before it's been introduced. The 27 modules group into five
units, plus a capstone finale.

| Unit | Modules | Theme |
|------|---------|-------|
| **1: Get out of the chat window** | 1–7 | The local foundation: version control, committing the AI's config, getting the AI editing real files safely. |
| **2: Make it shareable, reviewable, recoverable** | 8–12 | The team layer: hosting, issues, review, collaboration, recovery. |
| **3: Automate the checking and shipping** | 13–19 | The pipeline: tests, CI, security scanning, containers, secrets, delivery, runners. |
| **4: Extend the AI into your systems** | 20–23 | The frontier: MCP, skills, securing them, existing codebases. |
| **5: AI in the loop** | 24–27 | Agents inside the pipeline, from assistive to autonomous, plus the evals that make it trustworthy. |
| **Capstone** | finale | One real feature taken end to end. |

**Durable core vs. expansion zone.** Modules 1–14 are the stable foundation. From Module 15 onward
is the expansion zone, where a fast-moving space keeps handing us new lessons. Volatile material
lives toward the back so the front stays stable as the course grows.

See [`the-workflow-syllabus.md`](the-workflow-syllabus.md) for the full module-by-module plan and
the reasoning behind the sequencing.

---

## How git works in this course

You don't memorize git commands here. Modules 1–3 have you run the basics by hand so you build
intuition (the AI is still in a browser chat). Module 4 puts the AI in your editor/CLI, and from
there you **direct the AI to do the git work** (commit, branch, merge, revert) and verify the
result. Think arithmetic by hand first, then a calculator. You learn that git is critical and how it
works; the AI drives the keystrokes.

---

## Format and conventions

- **Written lessons + interactive labs.** Every module is a README you read *and* a lab you run at
  the keyboard. There are no quizzes; there's a "you're done when…" check.
- **Run labs on your own machine, any OS.** No sandbox or cloud account required. Where a lab needs
  code, it leans on **Python or shell**, picked per lab, kept as small as possible. The *concepts*
  are language-agnostic; the labs just need something concrete to run.
- **Claude Code as the worked example.** Commands and labs use Claude Code as the concrete agent
  (`claude --version  # sub your own agent`); the concepts stay model- and tool-agnostic.
- **GitHub is the default, not the requirement.** Hosting examples use GitHub because nearly
  everyone will encounter it, but the course is provider-neutral and includes an optional
  **self-hosted-forge track** for on-prem and air-gapped environments.
- **Self-checks only.** No grading, no certification; each module ends at a concrete done-criterion.

---

## Repo layout

```
ai-workflow-course/
  README.md                 # this file
  AGENTS.md                 # committed AI instructions; dogfoods Module 5 (vendor-neutral name)
  the-workflow-syllabus.md  # the full course plan (source of truth for structure)
  _TEMPLATE.md              # the shape every module follows
  modules/
    01-the-copy-paste-problem/
      README.md
      lab/
    02-version-control-as-a-safety-net/
      README.md
      lab/
    ...
  capstone/
    README.md
  assets/                   # diagrams, images
```

---

## Status

All 27 modules and the capstone are written and reviewed. The lessons render to the
[Wiki](https://github.com/recklessop/ai-workflow-course/wiki) as a textbook, kept in sync from
`modules/` by CI. Each lab is skip-friendly: copy that module's `lab/start/` snapshot into a
fresh `tasks-app`, commit, and run that lab without doing the earlier ones.
