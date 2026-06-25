# Skill: Map this repo

A navigation playbook (a Module 21 skill) for orienting in a codebase you didn't write.
Point Claude Code (or sub your own agent) at this file as a skill, or paste it in as instructions. The goal is a
**read-only** mental model; no edits happen here.

## When to use
At the start of any session on an unfamiliar repo, before any change is discussed.

## Rules
- **Read only.** Do not edit, create, or delete files while mapping. No exceptions.
- **Cite real paths.** Every claim about the code must point to a file and, ideally, a line range.
  If you can't cite it, say "unverified" instead of guessing.
- **Breadth before depth.** Establish the whole shape before going deep on any one area.
- **No conclusions from file names alone.** A file called `auth.py` may not be where auth lives.

## Steps
1. Read the orientation pack (from `orient.py`), the README, and any `CONTRIBUTING`,
   `ARCHITECTURE`, or committed AI-instructions file. Treat these as claims to verify, not truth.
2. Identify the **entry points**: how does this thing start? (CLI `main`, web server, library
   exports.) Name the exact file(s).
3. Trace **one representative request/command end to end**, from entry point to where it does its
   real work and back. List the files it passes through, in order.
4. Produce an **architecture summary** (max ~1 page):
   - One paragraph: what this project does and how it's structured.
   - A "where things live" table: concern -> directory/file.
   - The build/test/run commands, confirmed against the README or CI config.
   - 3-5 things that surprised you or look risky to touch.
5. List **open questions** you could not resolve from the code. Do not paper over them.

## Output
A single Markdown summary. End with: "Verified against: <list of files actually read>."
