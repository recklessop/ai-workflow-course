# Module 8: Remotes and Hosting (GitHub, the Alternatives, and Owning Your Repo)

> **One repo on one laptop is one spilled coffee away from gone.** A remote gets your history
> off your machine and somewhere durable. And because every clone carries the full history, a
> working team backs itself up just by working.

---

## Prerequisites

- **Module 2**: you have a Git repo (`tasks-app`) with real commits, and you understand commits as
  checkpoints and the repo as durable memory. This module gets that history *off the one disk it
  lives on*.
- **Module 5**: you committed your agentic tool's instructions file into the repo. A remote is what
  finally makes that config *shared*: push it once and every teammate (and every agent) pulls the
  same setup.
- **Module 6**: you can work on branches. Pushing is per-branch, so knowing what a branch is matters
  here.

Helpful but not required: **Module 7** (worktrees). Everything below works the same whether you have
one working directory or several.

---

## Learning objectives

By the end of this module you can:

1. Explain what a remote *is* (a named pointer to another copy of the same repo) and why "it's just
   another copy" is the whole reason hosting is provider-neutral.
2. Add a remote, push your history to it, and pull changes back, on any forge, with the same commands.
3. Recover from the three failure modes that bite everyone on first push: authentication, a
   non-empty remote, and a branch-name mismatch.
4. Choose a host deliberately, hosted vs. self-hosted, using a current, dated comparison instead of
   defaulting to GitHub by reflex.
5. State precisely where "pushing to a remote" is and isn't a backup, and how a normal team workflow
   accidentally satisfies most of the 3-2-1 rule.

---

## Key concepts

### A remote is just another copy

A **remote** is a named reference to *another copy of this same repository*, usually somewhere you
can reach over the network. That's it. `origin` is not a
GitHub concept, a GitLab concept, or a Gitea concept. It's a Git concept, and the copy it points at
is a full, equal Git repo that happens to live on a server.

This is the fact the entire rest of the module rests on: **because a remote is just
another copy, the commands you use to talk to it are identical no matter who hosts it.** `git push`
to GitHub is byte-for-byte the same operation as `git push` to a **forge** (a Git hosting platform
like GitHub, GitLab, Gitea, or Forgejo) you run yourself in a locked-down rack. The provider is
a logistics decision (uptime, price, who can see it, where the servers sit), not a Git decision. We
lean on GitHub as the worked example below *only* because it's
the one you're most likely to hit first, not because the mechanics change anywhere else.

The local-to-remote vocabulary is small:

```bash
git remote add origin <URL>   # register a remote named "origin" at this URL (once per repo)
git remote -v                 # list remotes and their URLs
git push -u origin main       # send your "main" branch up; -u links local main to origin/main
git push                      # after the first -u push, this is all you need
git pull                      # fetch the remote's changes AND merge them into your branch
git fetch                     # fetch the remote's changes WITHOUT merging (look before you leap)
git clone <URL>               # make a brand-new local copy from a remote (history and all)
```

`origin` is just the conventional name for "the place I push to." You can have more than one remote
(a personal fork *and* the team's repo, say), and they can live on different hosts entirely: one on
a SaaS forge, one on a box in your closet. Git doesn't care.

### Getting a remote: you create the empty repo first

The one piece the commands above assume is that a remote repo *exists* to push into. On every host
the shape is the same:

1. In the host's web UI (or its CLI/API), create a **new, empty** repository. Give it a name; do
   **not** let it add a README, license, or `.gitignore`; you want it empty so your local history
   is the first thing in it.
2. Copy the URL it gives you. You'll see two flavours:
   - **HTTPS**: `https://host/you/tasks-app.git`. Authenticates with a username + a personal access
     token (not your account password; password auth over Git is gone on essentially every modern
     host).
   - **SSH**: `git@host:you/tasks-app.git`. Authenticates with an SSH key you've added to your
     account. More setup once, less friction forever.
3. Register the remote on the local side and push the history up. The shape of that exchange, with a
   first push to an empty remote, looks like this:

   ```console
   $ git remote add origin <URL-you-copied>
   $ git push -u origin main
   Enumerating objects: 24, done.
   ...
   To github.com:you/tasks-app.git
    * [new branch]      main -> main
   branch 'main' set up to track 'origin/main'.
   ```

   In the lab you direct your agent to run that and then verify the result; here we're just reading
   what it does.

That `-u` (short for `--set-upstream`) is worth understanding, not just copying: it records that your
local `main` *tracks* `origin/main`. After it, `git status` will tell you things like "your branch is
ahead of origin/main by 2 commits", the ahead/behind report you met in Module 2, now meaningful
because there's finally a remote to be ahead *of*. And `git push` / `git pull` with no arguments know
where to go.

### The three failure modes of a first push

Everyone hits at least one of these. Recognizing them by their error text saves an afternoon.

**1. Authentication fails.** You push and get `Authentication failed`, `Permission denied
(publickey)`, or a `403`. Two different causes hide behind that wall, and they have different fixes.
The common one is *no usable credential at all*: you tried an account password (dead on every modern
host) or never set up a token / SSH key. The sneakier one is a credential that *exists but lacks the
right scope*: a token authenticates fine and then the push is refused with `403` because the token was
never granted write access to repositories. They look alike but you fix them differently. One needs a
credential created; the other needs you to *edit the existing token's scopes* (don't regenerate it).
For the no-credential case: for HTTPS, generate a personal access token in the host's settings and use
it as your password when prompted; for SSH, generate a key (`ssh-keygen`) and paste the public half
into the host's SSH-keys settings. This is host-specific UI but the *concept* is identical everywhere,
and the callout below walks the shape of getting one.

> ### Getting a credential (the shape)
>
> The exact menu names and scope labels drift per host, so treat these as the *shape*, not gospel
> (**Verify-before-publish** the specific UI wording for your forge):
>
> - **Scope is the gotcha; check it first.** In the host's **Settings → developer / access tokens →
>   create token**, you must grant the token write access to repositories: usually a scope literally
>   named `repo`, or a "read **and write**" toggle on the repositories resource. A token created
>   *without* it authenticates and then `403`s on push; it looks like an auth failure, but the fix is
>   to **edit the token's scopes**, not to delete and recreate it.
> - **The token is shown once.** Hosts reveal the value a single time at creation. Copy it the moment
>   it appears; if you lose it you create a new one rather than recover the old.
> - **Pasting it is invisible, and only happens once.** When Git prompts for your "password," paste
>   the token; most terminals show *nothing* as you paste a secret, which is normal, not a failure.
>   A **credential helper** (`git config --global credential.helper …`, e.g. `store`, `cache`, or your
>   OS keychain) remembers it after the first success so you aren't pasting it on every push.
> - **SSH is the alternative.** A key you've added to the host skips passwords entirely: more setup
>   once, no token to scope or cache afterward.

**2. The remote isn't empty (non-fast-forward).** You let the host create the repo *with* a README,
then push, and get `! [rejected] ... (fetch first)` or `non-fast-forward`. The remote has a commit
your local history doesn't, so Git refuses to overwrite it. The simple fix is to **recreate the remote
empty** and push again. (The alternative you'll see online is `git pull --rebase origin main` then
push: it replays your commits on top of the remote's, but `rebase` is an advanced, history-rewriting
operation this course doesn't teach as a step here, so prefer the empty-remote fix for now. And note
that plain `git pull` won't rescue you against an auto-README remote; it refuses to merge unrelated
histories.) This is the same "someone else pushed before me" situation you'll hit constantly once
you're collaborating (Module 11), except here the "someone else" was the host's auto-generated README.

**3. Branch-name mismatch.** Your local default branch is `master` but the host expects `main` (or
vice versa). `git push -u origin main` then errors with `src refspec main does not match any`. Fix:
check what you actually have with `git branch`, and either push the branch you have
(`git push -u origin master`) or rename it first (`git branch -m main`). If you initialized with
`git init -b main` back in Module 2, you're already on `main` and this one won't bite you here. But
it's the classic wall for any repo that started life on `master`, so it's worth recognizing.

### Pull, fetch, and the everyday loop

Once the remote exists, day-to-day work adds two moves to the Module 2 loop:

- **`git pull`** before you start, to get whatever the remote gained since you last looked. It's a
  `fetch` (download) plus a merge into your current branch in one step.
- **`git push`** after you've committed, to send your new checkpoints up.

When you want to *see* what the remote has before you let it touch your working files, use
**`git fetch`** instead: it downloads the remote's commits into `origin/main` but leaves your branch
untouched, so you can `git log main..origin/main` to read exactly what's incoming before merging.
That "look before you leap" habit matters more the moment other contributors (human or agent) are
pushing to the same place.

### Choosing a host: the comparison

GitHub dominates. It is by a wide margin the largest forge, it's where most open source lives, and
it's the one AI tooling integrates with *first*: when a new coding agent or MCP server ships, GitHub
support is usually in the first release and everything else trails. That makes it the sane default for
most people, and it's why this module uses it as the worked example. But "default" is not "only," and
for a team with on-prem, air-gapped, or data-control requirements (a real and common constraint for
this audience) it may be the wrong default. The genuine choice is between **hosted** (someone runs
the forge; you just use it) and **self-hosted** (you run the forge on your own infrastructure).

> ### Hosting comparison (as of 2026-06-22)
>
> Pricing and feature claims drift fast. Everything in these two tables was checked on the date above
> and must be re-verified before you rely on it; see the **Verify-before-publish** checklist at the
> end. List prices are per-user/month at the entry paid tier, billed annually, in USD; promotional
> and volume discounts are common and not shown.

**Hosted forges (someone else runs it):**

| Platform | Pricing (entry → paid) | Built-in CI/CD | AI-tooling integration | Ease of operation |
|---|---|---|---|---|
| **GitHub** | Free; Team ~$4/user; Enterprise ~$21/user | GitHub Actions, built in (Free tier includes a monthly minutes allowance for private repos; unlimited for public) | **Deepest.** Most agents, MCP servers, and AI reviewers target GitHub first | Zero ops, pure SaaS |
| **GitLab** (SaaS) | Free (capped users/namespace, small CI allowance); Premium ~$29/user; Ultimate ~$99/user | GitLab CI/CD, among the most mature, deeply integrated pipelines | Strong; first-party AI assistant plus growing agent support | Zero ops as SaaS; also self-hostable (see below) |
| **Bitbucket** (Atlassian) | Free (≤5 users); Standard ~$3.65/user; Premium ~$7.25/user | Pipelines, built in (small free monthly build-minute allowance) | Growing; tightest value is deep Jira/Atlassian tie-in | Zero ops as SaaS; Data Center edition self-hostable (enterprise pricing) |
| **Azure DevOps** | First 5 users free; Basic ~$6/user beyond; pipelines ~$40/parallel job after a free job | Azure Pipelines, built in (one free parallel job + monthly minutes) | Good within the Microsoft ecosystem; Copilot integration | Zero ops as SaaS; Azure DevOps Server self-hostable |
| **Codeberg** | Free (FOSS projects only; soft repo/storage caps) | Forgejo Actions (it runs Forgejo) | Via API/MCP; not a first-tier agent target | Zero ops; nonprofit-run, no commercial/closed-source hosting |
| **SourceHut** | Paid to host: ~$5 / $10 / $15 (all tiers buy the *same* service, "pay what's fair"); reduced ~$2 rate / financial aid if the full price is a hardship; free to *contribute* | builds.sr.ht, built in | Minimal first-class AI tooling; reachable via API | Zero ops as SaaS; fully self-hostable (it's open source) |

**Self-hostable open-source forges (you run it):**

| Forge | License / cost | Built-in CI/CD | AI-tooling integration | Ease of operation |
|---|---|---|---|---|
| **Forgejo** | Free, open source (you pay infra + ops) | Forgejo Actions, runs GitHub-Actions-compatible workflow YAML | Full REST API; community MCP servers; agents work over git + API | **Easiest.** Single Go binary, runs on a tiny VPS (~256 MB RAM). Community/nonprofit governed |
| **Gitea** | Free, open source | Gitea Actions (GitHub-Actions-compatible YAML) | Full REST API; community MCP servers | Single Go binary, same light footprint as Forgejo; company-backed |
| **GitLab CE** | Free, open source | Full GitLab CI/CD + container registry + more, in one install | Same first-party AI direction as GitLab SaaS, self-hosted | **Heaviest.** Wants ~8 GB+ RAM (Postgres/Redis/Sidekiq/Gitaly); upgrades can't skip versions |
| **Gogs** | Free, open source | None built in | API only | Lightest of all; single binary, runs on a Raspberry Pi. Slower development; no CI |
| **OneDev** | Free, open source | Built-in CI/CD configured in the **UI** (little/no YAML) + Kanban + packages | API; less common as an agent target | Single deployment; all-in-one but a smaller ecosystem |

Two things to read out of those tables rather than memorize the numbers:

- **GitLab spans both camps.** It's a hosted SaaS *and* a self-hostable Community Edition from the
  same project; useful if you want SaaS now and the *option* to bring it in-house later without
  changing tools.
- **"Self-hosted" trades a per-user bill for an ops bill.** The license is free; your cost is the
  server, the upgrades, the backups, and the on-call. Forgejo/Gitea make that bill small (a single
  binary on a cheap box). GitLab CE makes it real (a stack to feed and water). That trade is the
  whole decision.

### The self-hosted-forge track (optional)

If you're in the air-gapped/on-prem audience, you can run this module's lab against a forge you stand
up yourself instead of a SaaS account. The teaching point is precisely that **nothing changes**: you
create an empty repo on your forge, copy its URL, `git remote add origin <URL>`, and `git push`. The
lab below flags exactly where the only difference is (the URL and how you authenticate to your own
box). Standing the forge up is its own exercise; Forgejo or Gitea is a single binary and the fastest
path; the *git* half is identical to the hosted track.

### Backup thesis, part one: distribution is the backup

Module 2 left you with a sharp limitation: everything lived on one disk. Drop the laptop in a lake and
the repo, history and all, is gone. A single local repo gives you *recovery* (move between
checkpoints) but not *backup* (a copy that survives the disk dying).

Pushing to a remote is what closes that gap, and Git's design makes the win bigger than it looks.
Recall the standard **3-2-1 backup rule**: keep **3** copies of your data, on **2** different media,
with **1** offsite. Now look at what a normal team doing normal work ends up with, without anyone
"doing backups":

- Your laptop has a full copy: **complete history**, not just current files.
- The remote has a full copy: **offsite**, on someone else's hardware (or your other box).
- Every teammate who has cloned the repo has *another* full copy, each with the entire history,
  because **clone copies everything**, not a snapshot.

A four-person team that pushes to one remote is sitting on five-plus complete, independent copies of
the entire project history across multiple locations and machines. They didn't run a backup tool.
They just worked. That's the point of a *distributed* version control system: distribution
*is* the redundancy. The 3-2-1 rule, which most ops shops fight to satisfy deliberately, falls out of
a forge and a working team almost for free.

Be precise about the division of labor, because the course is honest about where analogies stop:

- **Recovery power comes from commits (Module 2, and Module 12 for the harder cases).** That's your
  point-in-time restore: go back to any checkpoint.
- **Backup power comes from remotes and distribution (this module).** That's your offsite,
  redundant, survives-the-disk copy.

You need both. Commits without a remote survive a mistake but not a dead drive. A remote without good
commits survives a dead drive but gives you a junk drawer to restore from. Module 12 picks up the
*recovery* half in full and is just as honest about what Git is **not** a backup for: your database,
your secrets, your uncommitted work, your large binaries. We'll hold that thought there.

---

## The AI angle

A remote isn't only about durability. It's what the AI parts of this course run on.

- **Most AI tooling integrates with the forge first, not your laptop.** AI reviewers, issue-to-PR
  agents, and the CI that catches code which merely *looks* right (Modules 10, 14, and Unit 5) all
  operate on the *remote* repo through its API and web UI. Until your history is pushed, none of that
  machinery has anything to act on. A remote is the precondition for every agent-in-the-loop module
  that follows.
- **GitHub's "integrates first" status is a real, current bias; name it, then decide.** Because the
  largest forge is where AI tooling lands first, picking a less-common host or self-hosting can mean
  thinner first-class agent support and more wiring-it-yourself over the API. That's a legitimate cost
  to weigh against control and data-residency; *not* a reason to abandon the choice. The git
  mechanics are identical everywhere; it's the AI ecosystem maturity that varies, and that gap is the
  thing to check (it narrows constantly).
- **The committed AI config from Module 5 only pays off once it's pushed.** Locally, your agent's
  instructions file just configures *your* agent. Pushed to the remote, it configures *everyone's*:
  every teammate who clones, and every automated agent that later operates on the repo, inherits the
  same conventions instead of each drifting into a private setup. The remote is what turns "my AI
  config" into "the project's AI config."
- **A remote is an agent's recovery insurance.** When you hand an agent a branch and let it run
  (Module 6, and Unit 5 at full autonomy), a pushed branch means its work survives a crashed session,
  a wiped worktree, or a machine that dies mid-run. Push early; an agent's output that only exists in
  one uncommitted, unpushed working directory is the most fragile state in this whole course.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/08-remotes-and-hosting/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 8"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Git commands), plus one short provided shell script. Runs on macOS, Linux,
WSL, or Git Bash on Windows. Continues the `tasks-app` repo from Module 2.

**You'll need:**

- Your `tasks-app` Git repo from Module 2 (with several commits and a `.gitignore`).
- An account on a Git host. **Hosted track:** GitHub is the worked default, but GitLab, Bitbucket,
  Codeberg, or any forge works with the identical commands. **Self-hosted track:** a Forgejo/Gitea
  (or other) instance you can reach, and an account on it.
- The ability to authenticate to that host: a personal access token (for HTTPS) or an SSH key added
  to your account. This is the one part you set up by hand in the host's web UI, since it's account
  security, not git. Do it first; failure mode #1 above is the most common first-push wall.
- Claude Code (or sub your own agent) in your terminal, set up as in Module 4. In this lab you
  *direct the agent* to do the git work (add the remote, push, clone, fetch, pull) and you verify
  each result yourself. You don't type the git commands by hand.

### Set up GitHub authentication (do this first)

This is the one part you do by hand in the web UI, and it's failure mode #1 above: the single most
common first-push wall. Set it up *before* Part A so the push just works. You have two paths; do
**one**. This lab walks the **PAT / HTTPS** path step by step on GitHub as the worked example,
because it's all in the browser and needs no command-line setup. SSH is the optional alternative,
linked below.

> **Other host?** These are GitHub's exact menu paths as the worked example. On GitLab, Bitbucket,
> Codeberg, or your own Forgejo/Gitea the *shape* is identical (see the "Getting a credential" callout
> in the lesson) but the menu names drift; find your host's "access tokens" or "SSH keys" settings.

**Path 1: Personal access token (PAT) over HTTPS.** Generate a token in GitHub's web UI, then paste
it once when Git asks for a password.

1. On GitHub, go to your avatar (top right) → **Settings** → **Developer settings** (bottom of the
   left sidebar) → **Personal access tokens**. GitHub offers two token types:

   - **Fine-grained tokens** (recommended): scoped to a single repository, with explicit permissions.
     This lab uses fine-grained.
   - **Tokens (classic)**: older, broader; access is controlled by a coarse `repo` scope that grants
     all your repos at once.

   Pick **Fine-grained tokens** → **Generate new token**.

2. Fill in the token:

   - **Token name:** anything memorable, e.g. `tasks-app-push`.
   - **Expiration:** pick a real expiry (30 to 90 days is fine for the lab). Tokens expire by design;
     that's a rotation cost you accept for the convenience.
   - **Repository access:** choose **Only select repositories** and select your `tasks-app` repo. If
     you haven't created the empty remote yet (Part A step 1), come back and select it after, or
     create the repo first and then make the token. The token only needs to *reach* a repo that
     exists.
   - **Permissions → Repository permissions → Contents:** set it to **Read and write**. This is the
     write scope, and it is *the* gotcha: a token without it authenticates fine and then `403`s on
     push (failure mode #1's scope trap). GitHub auto-adds **Metadata: Read** when you do this; leave
     it.

3. Click **Generate token** and **copy the value immediately.** GitHub shows it exactly once. If you
   lose it, you generate a new one rather than recover the old.

4. At the first push (Part A step 2), Git prompts for a **username** and **password**:

   - **Username:** your GitHub username.
   - **Password:** paste the **token** (not your GitHub account password; password auth over HTTPS
     was removed years ago). Most terminals show *nothing* while you paste a secret; that's normal,
     not a hang. Press Enter.

   A **credential helper** caches it after the first success (`git config --global credential.helper`,
   set to `osxkeychain` on macOS, `manager` on Windows, or `store`/`cache` on Linux), so you paste the
   token *once*, not on every push.

   > **Verify-before-publish:** GitHub's menu wording, token-type names, and the **Contents: Read and
   > write** permission label drift. Re-confirm the path **Settings → Developer settings → Personal
   > access tokens → Fine-grained tokens** and the Contents scope before relying on these exact names.

**Path 2: SSH key (optional alternative).** A key you add to your account skips passwords entirely.
It's more upfront setup (generate a keypair, load the ssh-agent, paste the *public* key into GitHub),
but then there's no token to scope, expire, or cache. Follow GitHub's official docs, in order:

- [Generating a new SSH key and adding it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [Adding a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
- [Testing your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection)

If you go SSH, use the **SSH** URL (`git@github.com:…`) when you create the remote in Part A, not the
HTTPS one.

**Which should you pick?**

| | **PAT / HTTPS** | **SSH key** |
|---|---|---|
| **Setup** | Fast, all in the web UI; nothing to install | More upfront: keygen, ssh-agent, add the public key |
| **After setup** | Credential helper caches the token; otherwise re-paste | No prompts ever; nothing to cache |
| **Network** | Port 443; sails through corporate proxies/firewalls | Port 22; sometimes blocked on locked-down networks |
| **Maintenance** | Expires; needs rotation; the write-scope `403` trap; shown once | No expiry by default; no scope to misconfigure |
| **Risk to manage** | A leaked token until it expires/is revoked | A private key + passphrase on your disk |

Short version: **PAT** is the faster start and the friendlier path behind a corporate firewall;
**SSH** is the lower-friction *long-term* setup once you're past the initial keygen. Either one
satisfies the lab. If you're unsure, do the PAT.

### Part A: Create the empty remote and push

1. On your host's web UI, create a **new, empty** repository named `tasks-app`. Do **not** add a
   README, license, or `.gitignore`; leave it empty so your local history goes in clean. Copy the URL
   it shows you (HTTPS or SSH).

   > **Self-hosted track:** identical step, on your own forge's UI. The only thing that differs from
   > the hosted track is the URL (your forge's hostname) and how you authenticate to your box.
   > Everything from here on is the same commands.

2. From `~/ai-workflow-course/tasks-app`, tell your agent what you want and let it run the git. A
   prompt like:

   > "Add a remote named `origin` at <URL> and push `main` up with upstream tracking."

   Then verify it did exactly that, with your own eyes:

   ```bash
   git remote -v                 # origin should show, for both fetch and push
   ```

   Confirm `origin` points at your URL, and that the push reported `branch 'main' set up to track
   'origin/main'`. If the push errored, match the error to the three failure modes above before you
   re-prompt: `Authentication failed` / `Permission denied` → token or SSH key (#1); `non-fast-forward`
   / `fetch first` → the remote wasn't empty (#2); `src refspec main does not match` → branch-name
   mismatch, check `git branch` (#3). Tell the agent the fix and have it push again.

3. Confirm the offsite copy exists: refresh the host's web page for the repo. Your files and your full
   commit history from Module 2 are now sitting on hardware that is not your laptop. **That is the
   backup half the course promised.**

### Part B: Prove distribution is redundancy

You're going to demonstrate the 3-2-1 claim with your own eyes: that a clone is a *complete,
independent* copy, history and all, not a snapshot.

4. Direct your agent to make a change and ship it in one go:

   > "Add a `version` command that prints the app version, commit it, and push to origin."

   Then verify: `git log --oneline -1` shows the new commit, and `git status` reports your branch is
   up to date with `origin/main` (nothing left stranded to push).

5. Have your agent clone the remote into a *separate* directory, as if you were a teammate on a fresh
   machine:

   > "Clone <URL> into `~/ai-workflow-course/tasks-app-teammate`."

   Now inspect the clone yourself. This is the see-it-with-your-own-eyes step, so you run the look:

   ```bash
   git -C ~/ai-workflow-course/tasks-app-teammate log --oneline   # the ENTIRE history is here
   ```

   Every commit, not just the latest. Compare the commit count to your original repo
   (`git log --oneline | wc -l` in each). They match. The clone didn't get "the current files"; it
   got the whole project's memory. That's the property that makes a working team into an accidental
   backup system.

6. Run the provided check from this module's `lab/` to make the point mechanically:

   ```bash
   # from your original repo:
   bash ~/ai-workflow-course/tasks-app/verify-backup.sh   # (copied from lab/verify-backup.sh)
   ```

   The script confirms (a) you have a remote configured, (b) your local branch is fully pushed
   (nothing stranded only on your disk), and (c) a fresh clone of the remote carries the exact same
   commit count as your local repo, i.e. the offsite copy is complete, not partial. Read its output;
   the green line is your evidence that the backup is real.

   > On the **HTTPS + token** path with a *private* repo, the clone check (c) needs your credential
   > helper to have cached the token from your earlier push; otherwise it can't authenticate to clone.
   > The script won't hang waiting for a prompt (it disables interactive credential prompts); it just
   > reports a `NOTE` that it couldn't clone, and the push checks above still stand. SSH and public
   > repos clone with no credential at all.

### Part C: The everyday loop

7. From the *teammate* clone, direct your agent to make and ship a change:

   > "In `~/ai-workflow-course/tasks-app-teammate`, note the remote in the README, commit, and push."

8. Back in your *original* repo, get the teammate's commit, but look before you leap. First have the
   agent fetch without merging:

   > "In `~/ai-workflow-course/tasks-app`, fetch from origin but don't merge yet."

   Then read exactly what's incoming yourself, before anything touches your files. This inspection is
   the habit, so you run it:

   ```bash
   git -C ~/ai-workflow-course/tasks-app log main..origin/main   # SEE what's incoming
   ```

   Once you've seen what's coming, tell the agent to take it:

   > "Now pull origin/main into main."

   Verify with `git -C ~/ai-workflow-course/tasks-app log --oneline` that the teammate's commit
   landed. That fetch-then-look-then-pull rhythm is the habit to keep: you saw what was coming before
   you let it touch your files. You've now pushed *and* pulled across two independent copies through
   one remote, the complete remotes mechanic.

### Part D (optional): A second remote

9. Direct your agent to add a *second* remote (a personal fork on another host, or even a bare repo on
   a USB drive or a box on your LAN) and push to it too:

   > "Add a remote named `backup` at <SECOND-URL> and push `main` to it."

   Then verify with `git remote -v`: two remotes now, `origin` and `backup`. You now literally have
   the 3-2-1 rule satisfied across your laptop, `origin`, and `backup`: three copies, more than one
   location. Nothing about Git stopped you from pointing at as many copies as you want.

---

## Where it breaks

The honest limits; the backup analogy especially needs them.

- **A remote backs up what you *pushed*, nothing else.** Uncommitted edits, untracked files, and
  anything `.gitignore` excludes (like `tasks.json` runtime state) never leave your laptop. "I pushed"
  is not "everything is safe"; it's "every *committed and pushed* change is safe." The defense is the
  Module 2 habit: commit often, and now, push often too.
- **Git is not a backup for non-Git things.** Your database, your secrets (which shouldn't be in the
  repo anyway, see Module 17), large binaries, and build artifacts are not covered by pushing code. The
  3-2-1-by-accident win applies to your *versioned source*, full stop. Module 12 is blunt about this.
- **One remote is one vendor.** Distribution across a team is great redundancy against *disk* failure;
  it's weaker against *account* failure. If your whole team only ever pushes to one host and that
  account is suspended, locked, or the provider has an outage, your offsite copy is temporarily out of
  reach (your local clones are fine). Part D's second remote, or a periodic clone to storage you
  control, is the answer for anyone who needs it. It's also the on-ramp to the self-hosting argument.
- **"GitHub integrates first" is true today and a moving target.** Don't treat the AI-ecosystem gap
  between hosts as permanent; it's exactly the kind of claim that ages. Re-check it for your tooling
  before you let it decide your host.
- **The comparison tables are a snapshot, not a fact of nature.** Every price and tier above was true
  on 2026-06-22 and will drift. Use them to learn the *dimensions* that matter (per-user cost vs. ops
  cost, built-in CI or not, footprint, AI-ecosystem maturity), then check current numbers yourself.

---

## Check for understanding

**You're done when:**

- Your `tasks-app` exists on a remote, and `git remote -v` plus the host's web UI both confirm it.
- You have pushed at least one commit and pulled at least one commit back, across two copies of the
  repo through one remote.
- `verify-backup.sh` reports a clean, fully-pushed state and a clone whose commit count matches your
  local repo's: you've *seen* that the offsite copy is complete.
- You can explain, in your own words, why a four-person team pushing to one remote roughly satisfies
  3-2-1 without running a backup tool, and name two things that win does *not* cover.
- You can state why the choice of host is a logistics decision, not a Git one, and name at least one
  hosted alternative to GitHub and one self-hostable forge.

When pushing feels like the natural end of "commit" and you trust that your history is no longer
trapped on one disk, you have the *backup* half of the backup-and-recovery thread. Module 9 starts
using the remote for more than storage (issues, the task layer where humans and agents pick up
work), and Module 12 returns to finish the *recovery* half.

---

## Verify-before-publish

This module makes dated pricing and feature claims that drift. Re-check each before relying on the
tables, and update the "as of" date when you do.

- [ ] **GitHub** tiers and prices: Free / Team / Enterprise per-user/month, and the Free-tier CI
      minutes allowance for private repos.
- [ ] **GitLab** tiers: Free (user/namespace caps, CI allowance), Premium, Ultimate per-user/month,
      and the SaaS-vs-self-managed price split.
- [ ] **Bitbucket** tiers: Free user cap, Standard (~$3.65), Premium (~$7.25) per-user/month, and
      free build-minute allowance. (Reconciled against Atlassian's own pricing page on 2026-06-22;
      stale third-party listings still quote ~$2/$5; trust Atlassian's page, and re-confirm.)
- [ ] **Azure DevOps**: free-user count, Basic per-user/month, and the per-parallel-job pipeline
      price plus free job/minutes.
- [ ] **Codeberg**: that it remains FOSS-only and free, and its current soft repo/storage caps.
- [ ] **SourceHut** paid-to-host tiers ($5/$10/$15): the 2026 prices are now *in effect* for new
      accounts (confirmed 2026-06-22), so they're no longer "proposed." Note all tiers buy the same
      service ("pay what's fair"), with a reduced rate (~the earlier minimum) and financial aid for
      hardship; re-confirm before relying on it.
- [ ] **Self-hosted forges**: that Forgejo/Gitea still ship GitHub-Actions-compatible CI, GitLab CE's
      current minimum resource footprint, and whether OneDev/Gogs CI status has changed.
- [ ] **"GitHub integrates first" / AI-ecosystem maturity**: re-assess which forges are first-tier
      agent and MCP targets; this gap narrows fast.
- [ ] **Self-host/hosted spans**: confirm GitLab still offers CE self-host, and Bitbucket/Azure DevOps
      still offer their self-hostable editions, before describing either as spanning both camps.
- [ ] **Credential/token UI**: the "Getting a credential" callout names menu paths and the
      write-scope label (`repo` / "read and write") generically; confirm the current wording and
      scope name on the default-example host before publishing.
- [ ] **GitHub PAT walkthrough** (lab "Set up GitHub authentication"): confirm the menu path
      **Settings → Developer settings → Personal access tokens → Fine-grained tokens**, the two token
      types (**fine-grained** vs **classic**/`repo`), and that the write scope is **Repository
      permissions → Contents: Read and write** (with **Metadata: Read** auto-added). These are
      volatile GitHub UI labels; also re-confirm the three linked SSH docs URLs still resolve.
- [ ] Update the comparison's **"as of" date** to the build date.
