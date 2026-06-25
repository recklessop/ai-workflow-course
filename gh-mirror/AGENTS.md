# AGENTS.md: instructions for AI agents working in this repo

> This is the committed AI instructions file for *The Workflow* course. It exists for two reasons:
> it actually configures the agents that help author the course, **and** it is a live worked example
> of [Module 5: Commit the AI's Config, Not Just the Code](modules/05-commit-the-ai-config/). The
> filename is deliberately vendor-neutral: most agentic coding tools read a repo-level instructions
> file, and the principle outlives any one vendor's filename. If your tool looks for a different
> name, point it here.

## What this repo is

A course that teaches IT professionals the engineering toolchain *around* AI coding: version
control, collaboration, CI/CD, and the tools that extend AI into real systems. The repo is both the
course content and a dogfooded example of the practices it teaches.

- **Source of truth for structure:** `the-workflow-syllabus.md`. Don't re-derive decisions it
  settles; read it first.
- **Build-context for authoring:** `handoff.md`. The "how" of building, plus the owner's settled
  decisions.
- **Every module follows** `_TEMPLATE.md`. Don't invent a new shape per module.

## Core promises (do not violate)

- **Model-agnostic in principle; Claude Code as the concrete example.** The concepts and workflow
  never depend on one LLM or tool. Name the common agentic tools once, then use **Claude Code** as
  the worked example in commands and labs, e.g. `claude --version  # sub your own agent`. Keep the
  *concepts* vendor-neutral; use a concrete tool so steps aren't abstract. Examples must survive a
  model swap.
- **GitHub is the default, not the requirement.** Keep hosting content provider-neutral; name the
  alternatives and the self-host track. Do not reintroduce a single specific forge as *the* answer.
- **The dependency chain is load-bearing.** A module may assume only what precedes it. Never
  reference a tool before its introducing module. If you think something should move, **flag it**;
  don't silently reorder.
- **Honesty about limits.** Where a tool or analogy breaks, say so. Don't sand off the caveats.
- **Don't pad.** This audience reads fast and trusts the concrete over the exhaustive. Lead with the
  pain, show the command and the failure mode.

## What the course teaches about git (the reframe)

This is **not** a "memorize git commands" course. The reader should finish knowing git is
*critical*, understanding the *concepts* and the *basics*, and, above all, that they don't have to
memorize commands because **the AI drives git for them**. The analogy: learn arithmetic by hand,
then use a calculator.

- **Modules 1–3 teach the mechanics by hand, on purpose.** The AI is still in the browser; the
  learner types git to build intuition. Keep that.
- **Module 4 is the pivot.** It puts the AI in the editor/CLI. From there on the learner **directs
  the AI** to do the git work (commit, branch, merge, revert, decide what to commit) and **verifies**
  the result; they don't type the commands by hand, and modules must not tell them to.
- **Don't re-teach basics.** Once a concept is introduced, later modules build on it through the AI;
  they don't re-explain how to create a branch, etc.

## Lesson vs. lab (keep them separate)

- The **lesson / Key-concepts** section is **theory**. To show a command, show it *with example
  output* as illustration; never instruct the reader to *run* it there.
- **All hands-on execution lives in the lab.** The lesson must not duplicate commands the lab runs.

## Voice

Direct, concrete, rigorous. Reframe ops instincts the reader already has toward AI-assisted work.
No motivational filler. When in doubt, show the command and what goes wrong without it.

**No slop (hard rules).** Don't write like an AI.

- **No em-dash character anywhere.** Use a semicolon, a period, a comma, or restructure the
  sentence. This is absolute; self-check every edit by searching for that character and removing
  each one.
- **Banned words:** "prose" (say "writing"/"words"/"docs"), delve, leverage, utilize, foster,
  bolster, underscore, unveil, streamline, robust, comprehensive, pivotal, seamless, significantly,
  extremely, truly, unlock, "dive in".
- **Banned openers/transitions:** Furthermore, Moreover, That being said, In today's world,
  It's worth noting, When it comes to.
- No hollow "this is important" statements, no intensifier standing in for a number, no weasel
  hedges ("may potentially", "can help to"), no dramatic/teasing headings (a heading names its
  content). End claims on a concrete, checkable fact.

## Conventions for labs

- Labs run on the learner's **own machine, any OS**. Don't assume a sandbox, cloud account, or
  specific shell beyond what's stated.
- Lean on **Python or shell**, chosen per lab, kept minimal. State the language once per lab.
- Every module ends at a keyboard (a lab), not a quiz, and has a concrete "you're done when…" check.

## Working in this repo (dogfooding the course)

This repo is hosted on `git.jpaul.io`. Follow the same flow the course teaches:

- **Never commit directly to `main`.** Branch per module/change, open a PR, squash-merge. The PR is
  the review gate (Module 10) even for solo work; it exists for traceability.
- **Build in dependency-chain order.** Modules 1–2 are the locked exemplars; match their tone,
  depth, and lab style.
- **Verify before publishing volatile claims.** Anything about pricing, versions, or tool behavior
  (especially the Module 8 hosting comparison) must be checked at build time, not written from
  memory. Mark such claims with a "Verify-before-publish" note.

## Don't

- Duplicate or fork `the-workflow-syllabus.md`; edit it in place if structure changes.
- Reorder modules or break the dependency chain without flagging it.
- Pin to a specific LLM vendor or a specific tool's config filename.
- Write pricing/version claims from memory.
- Pad.
