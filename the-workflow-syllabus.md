# The Workflow
### The Toolchain Around AI Coding

A living course for IT professionals who are comfortable in an AI chat window and starting to
build real software with it, but are still copy-pasting between the chat and their files. The
goal is to replace that loop with durable engineering workflows: version control, collaboration,
CI/CD, runners, and the tools that extend AI into real systems.

**Thesis:** the model is the cheap, swappable part. The workflow around it is the skill that lasts.
The course is **model-agnostic in principle**: the concepts and workflow don't depend on one LLM,
and the examples must survive a model swap. To keep steps concrete instead of abstract, the labs
use **Claude Code** as the worked example (`claude --version  # sub your own agent`).

---

## How this syllabus is built

It's a dependency chain, not a topic list. Every module assumes only what the previous ones
taught, and nothing references a tool before it's been introduced. The 27 modules group into
five units:

- **Unit 1 (1–7): Get out of the chat window.** The local foundation: version control, committing
  the AI's config, and getting the AI editing real files safely.
- **Unit 2 (8–12): Make it shareable, reviewable, recoverable.** The team layer: hosting, issues,
  review, collaboration, and recovery.
- **Unit 3 (13–19): Automate the checking and shipping.** The pipeline: tests, CI, security
  scanning, containers, secrets, delivery, and the compute behind it.
- **Unit 4 (20–23): Extend the AI into your systems.** The frontier: MCP, skills, securing them,
  and working with existing codebases.
- **Unit 5 (24–27): AI in the loop.** Agents operating inside the pipeline, from assistive to
  autonomous, plus the evals that make that trustworthy.
- **Capstone** ties the whole motion together on one real feature.

**Durable core vs. expansion zone.** Modules 1–14 are the stable foundation: version control,
review, testing, and CI aren't going anywhere and should rarely change. From Module 15 onward
(security scanning, the extend-the-AI unit, and all of Unit 5) is the expansion zone, where a
fast-moving space will keep handing you new lessons. Keeping the volatile material toward the back
lets the front stay stable as the course grows.

**The backup-and-recovery thread.** Version control as backup and recovery is woven across
Module 8 (remotes give you the offsite, distributed copy, the *backup* half) and Module 12
(commits give you point-in-time restore, the *recovery* half), with an honest accounting of where
the analogy holds and where it breaks.

---

## How git is taught (the reframe)

This is **not** a "memorize git commands" course. The reader should finish knowing git is critical,
understanding the concepts and the basics, and, above all, knowing they don't have to memorize
commands because **the AI drives git for them**. The working analogy: learn arithmetic by hand,
then use a calculator.

- **Modules 1–3 teach the mechanics by hand, on purpose.** The AI is still in a browser chat; the
  learner types git so the concepts land. Module 3 is where `branch` and `merge` first appear,
  practiced on a markdown doc where a mistake costs nothing.
- **Module 4 is the pivot.** It puts the AI in the editor or CLI. From there on the learner
  **directs the AI** to do the git work (commit, branch, merge, revert, decide what to stage) and
  **verifies** the result. Later modules don't tell the reader to type the commands themselves and
  don't re-teach the verbs.
- **Lesson vs. lab.** The lesson (Key concepts) is theory; commands appear with example output as
  illustration, never as "run this." All hands-on execution lives in the lab.

---

## Lab format

- **Self-contained, skip-friendly labs.** Each lab carries a `lab/start/` canonical snapshot and a
  "Starting point (skip-friendly)" preamble, so a learner can copy that snapshot and start any
  module without doing the prior labs first.
- Labs run on the learner's **own machine, any OS**: no sandbox, no cloud account. Where a lab needs
  code, it leans on Python or shell, picked per lab, kept minimal.
- Every module ends at a keyboard (a lab), not a quiz, with a concrete "you're done when…" check.

---

## Unit 1. Get out of the chat window

### Module 1. The Copy-Paste Problem
Orientation, not content. Diagnose the current state honestly: why pasting between a chat tab and a
file falls apart the moment a project has more than one file or more than one day of history.
Establish the course thesis and get everyone set up with a real local project, an editor, and a
terminal.

### Module 2. Version Control as a Safety Net
Git fundamentals framed for this audience as *undo for the AI*: `init`, `commit`, `diff`, `log`,
`restore`. The reframe that lands: commits are checkpoints you can always return to when the AI
confidently makes a mess, which is what makes everything riskier in later modules safe to attempt.

A second reframe that matters just as much: the repo is *durable memory the AI can read*. An AI
session is ephemeral (disconnect and the agent's working context is gone), but the changes on disk
aren't. A fresh session can answer "where were we?" entirely from ground truth by reading git:
`git status` shows what's changed but uncommitted (including new untracked files), `git diff` shows
the actual line-level edits, `git log` shows what's already committed and settled, and
`git log main..HEAD` plus the ahead/behind report in `git status` show how the branch compares to
`main` and to the remote, covering the untracked, uncommitted, and not-yet-pushed states in one
pass. The one limit to teach honestly: git only sees what was *written to disk*; anything the agent
only reasoned about in context but never wrote is gone with the session. That's also the practical
argument for committing often: the more granular the history, the cleaner the reconstruction.

### Module 3. Version Control for Words, Not Just Code
The lowest-stakes place to practice Git, and a genuinely useful skill on its own. **This is where
`branch` and `merge` first land**, practiced on a markdown doc where a mistake costs nothing, so
the verbs are already familiar before the agent ever touches code. Editing a doc with AI and
committing it carries almost no risk, which makes it the right first home for the full
branch / diff / commit / merge loop. Covers why plain text wins:
Git diffs are line-based, which is exactly why markdown and AsciiDoc version beautifully while
`.docx` and `.pptx` version terribly (Git tracks them, but the diff is useless binary noise and
merges are impossible). A real argument for moving runbooks, ADRs, and specs out of Word and into
markdown. Doc types covered: READMEs, architecture decision records, runbooks, changelogs, specs/PRDs.
The "aha": the wikis on most git hosts (GitHub, GitLab, Gitea, and others) are themselves just Git
repos, so your wiki was version-controlled all along. AI angle: LLMs are native markdown writers, so
"draft the ADR, branch it, review the diff, merge it" is adoptable tomorrow.

### Module 4. Getting the AI Out of the Browser
The literal answer to Module 1: agentic, editor-integrated AI tools that operate on your files
directly. Worked example: Claude Code; the criteria for choosing a tool stay vendor-neutral. This
works *because* of Module 2: you let the AI edit real files only because you can now see and revert
exactly what it did. **This module is the pivot in how git is taught.** From here on, the learner
directs the agent to run git (commit, branch, merge, revert) and verifies the result, instead of
typing the commands by hand.

### Module 5. Commit the AI's Config, Not Just the Code
The instructions you give the model are as worth versioning as the code it writes, and the thesis
holds here too: the model is swappable, but *your* setup for it is a durable artifact. Most agentic
coding tools read a committed, repo-level config or instructions file: project conventions, build
and test commands, coding standards, "don't touch these files," and house style. The principle is
tool-agnostic; the worked example uses Claude Code's `CLAUDE.md` so the steps are concrete, and the
filename convention is called out as a stand-in for whatever your tool reads. The motion itself is
now agent-driven: the learner directs the agent to **identify which config files belong in version
control**, stage them, and commit them. Checking the config into the repo means every teammate
(and every automated agent that later operates on the repo) inherits the same setup instead of each
person hand-tuning their own and quietly drifting apart. It also makes AI behavior *reviewable*: a
change to how the AI works on this project arrives as a diff in a PR, like any other change. (Its
full payoff lands once you have a shared remote in Module 8, but the habit starts now.) This is the
lightweight foundation that Module 21, Skills, later builds into structured, reusable playbooks.

### Module 6. Branches: Sandboxes for AI Experiments
**Not** a re-teach of branch verbs (Module 3 already first-taught `branch` and `merge` on docs).
Module 6 is about **directing the agent to run a risky experiment on a branch**: spin up a branch,
have the agent try something bold on real code, then decide as one call to keep it (merge) or throw
it away (delete the branch) with zero trace on `main`. The learner directs and verifies; the agent
runs the git. Conflicts are covered as something to *recognize and verify*, including the case where
the agent resolved one silently and you never saw a marker.

### Module 7. Worktrees: Running Agents in Parallel
Multiple working directories from one repo, genuinely powerful once you're running more than one
AI session at a time and don't want them stepping on each other. The natural payoff of understanding
branches.

---

## Unit 2. Make it shareable, reviewable, recoverable

### Module 8. Remotes and Hosting: GitHub, the Alternatives, and Owning Your Repo
Push, pull, and remotes: the mechanic that gets your history off your laptop and somewhere durable.
A remote is just a remote, so this stays deliberately provider-neutral. GitHub is the titan and the
default nearly everyone will encounter (the largest by far, and the one most AI tooling integrates
with first), but it is one option among many. Hosted alternatives worth naming include GitLab,
Bitbucket, Azure DevOps, Codeberg, and SourceHut. For teams that want control, on-prem, or
air-gapped operation (a real concern for this audience), you can self-host an open-source forge
instead: Forgejo, Gitea, GitLab CE, Gogs, and OneDev are all viable. (GitLab notably spans both
camps: hosted SaaS and a self-hostable Community Edition.) **Planned artifact:** a side-by-side
comparison (hosted vs. self-hosted, pricing, built-in CI/CD, AI-tooling integration, and ease of
operation) to be built and verified when we develop this module, rather than baking in claims that
age. **Backup thesis, part one:** a single local repo is *not* a backup; it's one disk away from
total loss. Pushing to a remote gives you an offsite copy, and because every clone carries the full
history, a working team accidentally implements something close to the 3-2-1 rule just by working
normally. The *recovery* power comes from commits; the *backup* power comes from remotes and
distribution.

### Module 9. Issues and the Task Layer
The "sharing dev tasks with others" layer. Issues describe the work; assignment routes it. The twist
that keeps it on-thesis: your assignees are increasingly a mix of humans and agents; an issue can
go to a person *or* be handed to an issue-to-PR agent. Sets up the coordination loop completed in
Module 11.

### Module 10. Reviewing Code You Didn't Write
Pull/merge requests as a review gate, and the genuinely new skill of evaluating a diff the AI
produced, reviewing for plausibility traps, not just correctness. One of the most important and
least-taught skills in the whole space.

### Module 11. Collaboration: Humans and Agents on One Repo
The full coordination loop now that issues (Module 9) and PRs (Module 10) both exist: issue → branch
→ implementation → PR → review → merge → issue closed. Contributors, forks vs. branches, and who's
allowed to push. The current-feeling angle: some of those "contributors" aren't human: a PR opened
by an agent and reviewed by a human, or two agents in parallel who are just two contributors needing
branches (which is why worktrees earned Module 7).

### Module 12. When It Goes Wrong: Revert, Reset, and Recovery
Recovery as its own discipline, placed here because "revert a bad PR" only makes sense once PRs
exist. `revert` cleanly undoes a change by writing a new commit (safe on shared history); `reset`
rewrites history (dangerous once others have pulled); the reflog recovers work you thought you'd
destroyed; tags and releases act as named recovery points. Reverting a bad merge is the headline
example. **Backup thesis, part two, and its limits:** Git gives excellent point-in-time logical
recovery for *versioned text*, but it is not backup for your database, your secrets (which shouldn't
be there anyway; Module 17), your uncommitted changes, or large binaries. Teaching where the
analogy breaks is what earns this audience's trust.

---

## Unit 3. Automate the checking and shipping

### Module 13. Testing in the AI Era
What a test is, why AI output specifically needs verification, and the happy fact that AI is
excellent at writing tests once you know how to direct it. Tests are the content that the next
module automates.

### Module 14. Continuous Integration
Automated checks (lint, build, test) running on every push. The pitch writes itself: AI generates
code that *looks* right, and CI is the tireless reviewer that catches when it isn't.

### Module 15. Security Scanning for AI-Generated Code
AI introduces failure modes a build check won't catch: vulnerable dependencies, hardcoded secrets,
and hallucinated packages that don't exist (a real supply-chain risk; attackers register the
plausible-but-fake package names LLMs invent). Covers dependency/SCA scanning, secret scanning, and
static analysis (SAST) as automated gates in the pipeline. Sequenced after CI because it's another
gate on the same pushes, and after the secrets problem is on the table.

### Module 16. Containers and Reproducible Environments
Docker and "works on my machine," solved: reproducibility so your code, your CI, and eventually
your deployments run identically. Also the foundation for safely sandboxing agents you don't fully
trust on your host.

### Module 17. Secrets, Config, and Environments
Managing secrets and configuration across environments. Earns its own module partly because AI loves
to hardcode an API key straight into a file, a concrete, recurring, AI-specific failure to defend
against.

### Module 18. Continuous Delivery and Deployment
Getting merged code to something running, automatically. Builds on containers (what you ship) and
secrets (what it needs to run).

### Module 19. Runners: The Compute Behind the Automation
What's actually executing all this CI/CD: hosted vs. self-hosted runners, and why you'd run your
own. The IT-pro payoff: you've been using someone else's compute; now you own the pipeline end to
end.

---

## Unit 4. Extend the AI into your systems

### Module 20. MCP Servers: Giving the AI Hands
The Model Context Protocol: connecting the AI to your real tools, data, and systems instead of it
working blind. Model-agnostic by design (it's a protocol, not a vendor feature), which reinforces
the whole course thesis.

### Module 21. Skills: Teaching the AI Your Playbook
Codifying repeatable workflows so the AI performs them your way, consistently, without re-explaining
every time. Turns one-off prompting into durable, reusable capability; and, fittingly, the skills
themselves live in version control. The structured big sibling of the committed config from Module 5.

### Module 22. Securing Third-Party MCP Servers and Skills
Module 15 scans the code the AI *writes*; this secures the AI *as an actor* in your environment.
Unit 4 just gave the model hands (MCP servers and skills), and installing a third-party MCP server
or skill is installing untrusted code that runs with access to your systems and data. Covers the new
attack surface: prompt injection (malicious instructions smuggled in through content the AI reads),
tool and agent abuse, over-broad permissions, and the MCP-and-skills supply chain: vetting, version
pinning, and least-privilege for anything you connect. The defense belongs here because Unit 4's own
content is what creates the risk; sequenced immediately after Skills so the danger and its mitigation
sit together.

### Module 23. Working with Existing Codebases
Everything so far has quietly assumed a greenfield project: you starting or growing something. The
harder, more common reality for IT pros is pointing AI at a large codebase you *didn't* write:
unfamiliar code, no mental model of it, and changes that have to be safe in a system nobody fully
understands. This module is about giving the AI enough context to be useful there: orienting it
across a big repo, having it map and explain unfamiliar areas before touching them, and making
small, well-scoped, reviewable changes rather than sweeping rewrites. It uses the full
extend-the-AI toolkit: MCP (Module 20) for real access to the code and surrounding tools, and skills
(Module 21) to codify navigation and safe-change playbooks. Placed deliberately late: it needs only
the Module 4 tooling to attempt, but the basics (version control, review, testing, recovery) are
exactly what make changing code you don't understand survivable, so it comes after them by design.

---

## Unit 5. AI in the Loop: Agents Inside Your Pipeline

Units 2–4 built the machinery (issues, PRs, CI, runners) and gave the AI hands. Unit 5 puts the AI
*inside* that machinery, escalating from the AI assisting you to the AI acting on its own under
supervision. The honest through-line: an agent can operate unattended only because the review, CI,
and recovery muscles from earlier units are there to catch it.

### Module 24. Assistive Agents: AI Review and Issue Triage
The AI helps, a human still decides. AI reviewers that comment on PRs (Module 10), and agents that
triage, label, and route incoming issues (Module 9). Low-risk because nothing merges or ships
without a person; the on-ramp to trusting agents in the loop at all.

### Module 25. Autonomous Agents: Issue-to-PR and Self-Healing CI
The AI acts, supervised. Agents that take an assigned issue and open a PR, agents that respond to a
failing pipeline by proposing a fix, and agents running as triggered or scheduled runner jobs
(Module 19). Everything they produce still lands as a reviewable PR behind CI and security gates; the
supervision is structural, not a matter of watching them work.

### Module 26. Orchestrating Multiple Agents
More than one agent working at once without stepping on each other, the payoff of worktrees
(Module 7) at full scale. Coordination, isolation, splitting work cleanly, and keeping parallel
output reviewable instead of a tangled mess.

### Module 27. Evals: Trusting an Agent That Acts Without You
The question Unit 5 forces: how do you know an unattended agent is doing good work? Evals as the
answer: measuring agent output systematically, setting guardrails, and deciding what an agent is
allowed to do without a human in the loop. The model-agnostic close to the whole course: evals are
how you judge any model or agent, so when you swap the model (which you will), your evals are what
tell you whether the swap was safe.

---

## Capstone: The Full Loop
One feature taken end to end: prompt → branch → AI implementation → tests → PR → CI → security scan →
review → merge → containerized deploy, with the committed AI config from Module 5 already in place
from the first commit. **Every step is agent-driven**: the agent creates the branch, writes the
code and tests, makes the commits, opens the PR, responds to CI and security findings, and runs the
deploy. The learner *directs* (states intent, sets guardrails, decides what merges) and *verifies*
(reads the diff, reads the CI output, confirms the deployed behavior). Everything clicks into a
single motion, and learners walk away with a workflow rather than a pile of tips. Stretch variant:
run the same feature the Unit 5 way (an assistive agent reviewing, an issue-to-PR agent doing the
first pass) so the workflow visibly starts running itself.

---

## Notes for the course owner

- **One sequencing decision to make:** Modules 20–21 (MCP, skills) are somewhat orthogonal to the
  deploy pipeline and could move much earlier (right after the AI-out-of-the-browser module) if
  you'd rather front-load "extend the AI's reach" over "ship safely." They sit at the back here so
  later units can build on them, but your audience's priorities might pull the other way.
- **Working with Existing Codebases (Module 23)** strictly needs only the Module 4 tooling and could
  move much earlier; it's placed late on purpose so the basics come first.
- **The capstone is a 28th unit by design** (27 teaching modules + finale). If you'd rather it count
  as a numbered module, the easiest merge is folding Issues (Module 9) into Collaboration (Module 11).
- **Expansion candidates** for future modules, all back-of-course: observability, cost/usage
  management, prompt-as-code, and dependency/license compliance. (Agent orchestration and evals
  graduated into Unit 5.)
- **Recommended future Unit 6: Adoption, Governance, and Scale.** Sits above Unit 5: agent
  permissions and least privilege, data governance and local/self-hosted models (the model-layer
  parallel to self-hosting a git forge), IP and licensing of AI-generated output, audit trails, and
  cost management. It's the unit that most differentiates a course aimed at IT professionals; parked
  here until you're ready to build it.
