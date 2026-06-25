# Module 18: Continuous Delivery and Deployment

> **Merged isn't running.** This module closes the last gap in the pipeline: getting approved code
> from `main` to something actually serving traffic, automatically, with a way back when it's wrong.

---

## Prerequisites

- **Module 10: Reviewing Code You Didn't Write.** The PR review gate. Auto-deploy is only safe
  because a human (or an agent under supervision) signed off on the diff first.
- **Module 14: Continuous Integration.** You already have a pipeline that lints, builds, and tests
  on every push. CD is not a new system; it's **more stages on that same pipeline**, after the
  checks pass.
- **Module 15: Security Scanning.** Dependency, secret, and static-analysis gates on the same
  pushes. These are part of what makes shipping without a human in the loop survivable.
- **Module 16: Containers and Reproducible Environments.** The container image is *what you ship*.
  CD takes that image and runs it somewhere. This module assumes you can already build and tag an
  image of the `tasks-app`.
- **Module 17: Secrets, Config, and Environments.** A running service needs configuration and
  secrets at runtime, *what it needs to run*. CD wires those into the deploy step instead of baking
  them into the image.

If you've done 14–17, you have all the parts. This module is the assembly.

---

## Learning objectives

By the end of this module you can:

1. State the precise difference between continuous **delivery** and continuous **deployment**, and
   decide which one a given project should use.
2. Extend your CI pipeline with build-and-publish stages that turn a merge into a versioned,
   deployable artifact.
3. Wire a deploy step that takes that artifact, injects runtime config/secrets, and brings up the
   new version, provider-neutrally.
4. Add a health check and an automatic **rollback** so a bad deploy reverts itself instead of
   staying down.
5. Reason about the deploy gate the way this audience already reasons about change windows: what's
   automated, what's manual, and where the stop button is.

---

## Key concepts

### The gap nobody automated yet

Walk the pipeline you've built so far. A change gets proposed (Module 9), implemented on a branch
(Module 6), reviewed as a PR (Module 10), checked by CI (Module 14), scanned for vulnerabilities
(Module 15). It merges. `main` is now correct, tested, and clean.

And then nothing happens. The code that's "done" is sitting in a Git history. The thing your users
touch is still running last week's version. Somebody (usually you, usually at 6pm) has to SSH in,
pull, build, restart, and pray. That manual last mile is where most outages are actually born:
inconsistent steps, a forgotten config flag, a half-restarted service, "wait, which version is in
prod right now?"

CI answered *"is this change good?"* CD answers the next question: ***"now get the good change
running, the same way every time."*** It's the same instinct that made CI worth it, the one that
replaces an error-prone manual ritual with an automated, repeatable one, now pointed at the last
step.

### Delivery vs. deployment: the distinction that matters

These two terms get used interchangeably and they are not the same thing. The difference is exactly
one decision: **who pushes the button to prod.**

- **Continuous Delivery:** every merge to `main` automatically produces a **deployable artifact**
  (a built, tagged, tested container image, sitting in a registry) and deploys it as far as a
  staging/pre-prod environment. Production deploy is **one click by a human**. The pipeline
  guarantees the artifact is *ready to ship at any moment*; a person decides *when*.

- **Continuous Deployment:** same pipeline, but there's **no button**. If it passes every gate, it
  goes all the way to production automatically. Merge is the last human action.

```
                 merge to main
                      │
        ┌─────────────┴──────────────┐
   CONTINUOUS DELIVERY          CONTINUOUS DEPLOYMENT
        │                            │
   build + test + scan          build + test + scan
        │                            │
   publish artifact             publish artifact
        │                            │
   deploy to staging            deploy to staging
        │                            │
   [human clicks "ship"] ──►    deploy to prod  (automatic)
        │                            │
   deploy to prod                  done
```

Both are "CD." When someone says "we do CD," ask which one; the operational risk is completely
different. Continuous deployment is not the more advanced/better option you graduate to; it's a
different risk posture that's appropriate for some systems and reckless for others. A blog,
internal dashboard, or stateless web service with good tests is a fine candidate. A billing engine,
a database migration, or anything with a regulatory change-control requirement usually is not, and
"a human clicks deploy" is a perfectly mature answer there, not a failure to automate.

The honest default for most teams adopting this: **start with continuous *delivery*.** Get the
artifact and the deploy step fully automated and trustworthy, keep the human on the prod button, and
remove that button only once you trust the gates more than you trust the click.

### The artifact is the unit of deploy

Here's the discipline that makes CD reliable, and it comes straight from Module 16: **you deploy a
built image, not a Git ref.** "Deploy `main`" is ambiguous; it means "go to the prod box, pull,
and rebuild," and that rebuild can pull a different base image or dependency version than CI tested.
"Deploy `tasks-app:9f3a2c1`" is not ambiguous. It's the exact bytes CI built and tested.

So the build-and-publish stage does this once, centrally:

1. Build the image from the merged code.
2. Tag it with something **immutable and traceable**: the Git commit SHA is the standard choice
   (`tasks-app:9f3a2c1`). Optionally also a moving tag like `:latest` or `:staging` for convenience,
   but the SHA tag is the one you trust.
3. Push it to a container registry, the durable home for images the same way a Git remote
   (Module 8) is the durable home for commits.

Every later deploy (to staging, to prod, a rollback) just says "run *this* tag." Build once, run
the identical artifact everywhere. That single property is what kills "works on my machine" at the
deploy layer.

### The deploy step, provider-neutrally

The shape of a deploy is the same everywhere, whatever the target (a cloud platform, a Kubernetes
cluster, a single VM, a PaaS):

1. **Pull** the specific image tag onto the target.
2. **Inject runtime config and secrets** (Module 17): environment variables, mounted secret files,
   a secrets-manager lookup. Never baked into the image; supplied at run time so the *same* image
   runs in staging and prod with different config.
3. **Start the new version** alongside or in place of the old one.
4. **Health-check** it before sending real traffic.
5. **Cut over** if healthy; **roll back** if not.

This module is deliberately provider-agnostic on *where*, the same way Module 8 stayed neutral on
hosts. The mechanics differ (a `kubectl` apply, a platform CLI, a `docker run`, a `compose up`), but
the five steps don't. The lab does the simplest possible real version: a local container run. The
logic is identical at scale.

### Health checks and rollback: the part beginners skip

A deploy that can't tell whether it worked isn't a deploy, it's a gamble. The single most important
thing CD adds over "SSH in and restart" is that **the pipeline verifies the new version is alive
before trusting it, and reverses itself when it isn't.**

A health check is a cheap, honest signal that the new version is actually serving: typically an
endpoint like `/health` that returns `200` only when the app has started clean. The deploy step
hits it after starting the new version and **waits for green before cutting over.**

Rollback is the other half. If the health check fails, the deploy stops the broken new version and
brings the **previous known-good image tag** back up. Because you deploy immutable tags, rollback is
trivial: you still have `tasks-app:<previous-sha>`, so "go back" is just "run the old tag again."
No rebuild, no git revert race, no scramble. (Reverting the *source* is still Module 12's job for the
code; rollback here is about the *running artifact*.) The strategies have names you'll meet:
blue-green (run old and new side by side, flip a switch) and canary (send 5% of traffic to new,
watch, ramp). They're all variations on "keep the old one ready until the new one proves itself."

> **Reframe for the ops reader:** you already know this instinct. It's the deployment equivalent of
> a maintenance window with a back-out plan, except the back-out plan is automated, tested on every
> single deploy, and takes seconds instead of a panicked hour. CD doesn't remove the discipline you
> already have; it encodes it so it runs every time instead of only when someone remembers.

---

## The AI angle

CI existed long before AI, and so did CD. What changed is the **rate**, and rate is everything for
the merged-to-prod gate.

AI writes and ships changes dramatically faster. More PRs open, more merge, and they merge sooner.
That's the upside, and it means the volume of code flowing toward production goes *up*, while the
human attention available to babysit each deploy stays flat. The gap between "merged" and "in prod"
stops being a quiet formality and becomes the place where that speed either pays off or hurts you.

Two consequences follow, and they pull in opposite directions:

- **Automating the deploy matters more.** If a human has to hand-deploy every AI-generated change,
  the manual last mile becomes the bottleneck that eats all the speed AI just gave you. CD is what
  lets the throughput actually reach users.
- **The gate matters more.** Faster shipping of code that *looks right* (the recurring AI failure
  mode from Modules 1 and 14) means a bad change reaches prod faster too, unless something catches
  it. This is the crucial point: **continuous deployment is only survivable because of the gates in
  front of it.** Review (Module 10), CI tests (Module 14), and security scanning (Module 15) are not
  bureaucracy you tolerate. They are the *entire reason* you're allowed to remove the human from the
  deploy button. Take auto-deploy without those gates and you've built a machine that ships AI
  mistakes to production at full speed.

So the AI-era posture is specific: **strengthen the early gates, then automate the late ones.** The
more you trust review + CI + scanning, the further right you can safely push automation, up to and
including no human on the prod button. The strength of the gates is the dial that decides whether
continuous *deployment* is responsible or reckless for a given repo. And when an agent itself is the
one merging (Unit 5), this stops being theoretical: the deploy gate is the last thing standing
between an autonomous contributor and your users.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** This lab is self-contained and does not depend
> on the earlier labs. Its files live in `modules/18-continuous-delivery-and-deployment/lab/`. Copy them into a working folder
> and make a first commit so you start clean:
>
> ```bash
> cp -r ~/ai-workflow-course/modules/18-continuous-delivery-and-deployment/lab ~/ai-workflow-course/18-continuous-delivery-and-deployment-lab
> cd ~/ai-workflow-course/18-continuous-delivery-and-deployment-lab && git init -b main && git add -A && git commit -m "start: module 18"
> ```
**Lab language:** shell, driving the container tooling from Module 16. You'll extend the `tasks-app`
into a tiny running service, then build a deploy script that ships it locally with a health check and
automatic rollback, the whole CD motion simulated on your own machine.

This lab simulates deployment with a **local container run** so it works on any machine with no cloud
account. The five deploy steps are real; only the *target* is your laptop instead of a server.

**You'll need:**

- A container runtime from Module 16: Docker or Podman. (Commands below use `docker`; if you run
  Podman, `alias docker=podman` or substitute.) As in Module 16, the engine must be **running**
  before you build or deploy. On macOS/Windows start Docker Desktop (or `podman machine start`);
  `docker --version` succeeds even when the engine is stopped, so confirm it's live with
  `docker info` first, or `deploy.sh`'s build step fails with "Cannot connect to the Docker daemon."
- The `tasks-app` from Modules 1–2, now a Git repo.
- `curl` (for the health check) and a bash-capable shell. On Windows, use WSL or Git Bash.
- Claude Code (sub your own agent), editor-integrated as of Module 4. From here you **direct it** to
  do the setup, commit, build, and deploy work, then you **verify** the result; you don't type those
  commands by hand.

Starter files are in this module's `lab/` folder:

- `serve.py`: turns the `tasks-app` into a minimal HTTP service with a `/health` endpoint, using
  only the Python standard library (no dependencies). This is the long-running thing CD deploys.
- `Dockerfile`: the Module 16 container image, adjusted to run the service.
- `deploy.sh`: the deploy step: build, tag, run, health-check, cut over or roll back.
- `cd-starter.yml`: the CD pipeline stages, written as GitHub Actions and extending the Module 14
  CI file. GitLab/other-forge notes are in the comments.

### Part A: Make something worth deploying

A CLI that exits immediately is awkward to "deploy." Give the app a long-running face.

1. Direct Claude Code to bring the starter files into your `tasks-app` folder next to `tasks.py` and
   `cli.py`: *"Copy `serve.py`, `Dockerfile`, and `deploy.sh` from this module's `lab/` into the
   tasks-app folder."* Then **read `serve.py` yourself**; it's ~40 lines wrapping the `TaskList` you
   already have in a stdlib HTTP server with two routes, `/health` and `/tasks`. Verify the three
   files landed next to `tasks.py`/`cli.py`.

2. Run the service locally first, no container, to see it work:

   ```bash
   python3 serve.py        # serves on http://localhost:8000
   ```

   In another terminal:

   ```bash
   curl localhost:8000/health     # {"status": "ok", "version": "dev"}
   curl localhost:8000/tasks      # your tasks as JSON
   ```

   Stop it with Ctrl-C. Now have Claude Code commit the new files: *"Stage and commit the HTTP
   service and Dockerfile with a clear message."* **Verify** the commit before moving on: read the
   diff it staged and confirm no secret, state file, or junk got swept in (it should be just
   `serve.py`, `Dockerfile`, and `deploy.sh`).

### Part B: Build and tag the artifact

3. Have Claude Code build the image and tag it with the current commit SHA, the immutable, traceable
   tag: *"Build the container image and tag it with the short commit SHA and also `:latest`."*
   Getting the SHA is git work the agent drives. **Verify** the result yourself:

   ```bash
   docker images tasks-app        # both tags point at one image; note the SHA
   ```

   That `:<sha>` tag is the unit of deploy. Everything downstream refers to *this exact image*.

### Part C: Deploy it (with a net)

4. **Read `lab/deploy.sh` yourself** before running it. It does the five steps: stops any running
   `tasks-app` container, starts the new image with runtime config injected as env vars (Module 17,
   note the `APP_VERSION` and the *absence* of any secret baked into the image), polls `/health`
   until green, and on failure rolls back to the previous tag it recorded.

   Now direct Claude Code to run the deploy against the SHA you just built: *"Run `deploy.sh` for the
   current commit SHA and report whether it came up healthy."* The agent makes the script executable
   and runs it. **Verify** the deploy yourself:

   ```bash
   curl localhost:8000/health     # now reports the SHA you deployed
   ```

   Ask the agent to commit a trivial change and deploy again, then read back what it recorded as the
   rollback target. You now have continuous *delivery* in miniature: one command turns a commit into
   a running, version-tagged service.

### Part D: Break a deploy and watch it roll back

5. Now prove the net works. The service honors a `BREAK=1` env var that makes `/health` return
   `500`, a stand-in for "this build starts but is actually broken." First have the agent deploy a
   healthy version so there's a known-good to fall back to, then trigger the broken one yourself so
   you watch it happen:

   ```bash
   ./deploy.sh                    # healthy baseline (defaults to the current commit SHA)
   BREAK=1 ./deploy.sh            # same image, but the new instance fails its health check
   ```

   The script starts the "new" version, the health check fails, and it **automatically stops the
   broken instance and brings the previous good one back up.** Confirm you're still serving:

   ```bash
   curl localhost:8000/health     # ok, the bad deploy reverted itself
   ```

   That automatic reversal, not the build and not the run, is the part that makes auto-deploy
   something you can sleep through.

### Part E: Wire it into the pipeline (read + reason)

6. Open `lab/cd-starter.yml` and compare it to the Module 14 `ci-starter.yml`. It's the **same
   pipeline with stages appended**: the lint/test/scan gates run first (unchanged), and only `on:
   push` to `main` (a merge) do the build-publish-deploy stages run. Trace the `needs:`/dependency
   chain that makes deploy run *only after* the checks pass.

7. Find the one line that is the delivery-vs-deployment switch: the deploy-to-prod step gated behind
   a manual approval (`environment:` with a required reviewer, commented in the file). Decide, for
   the `tasks-app`, which side you'd choose and why, and ask Claude Code to make the case for the
   *other* choice. The goal isn't a "right" answer; it's being able to articulate the risk posture
   either way.

> **A note on running the full pipeline:** actually executing `cd-starter.yml` end to end needs a
> forge with a container registry and a deploy target wired up; that's environment-specific and
> partly Module 19's territory (the runners and compute underneath). Parts A–D give you the deploy
> *logic* runnable today on your own machine; the YAML shows how it slots into the automated
> pipeline you already started in Module 14.

---

## Where it breaks

Be honest about the edges: this is where teams get burned.

- **The deploy is only as safe as the gates in front of it.** Continuous deployment with weak tests
  and no review isn't "moving fast," it's an automated mistake-shipping machine. If you haven't done
  the Module 10/14/15 work, do *delivery* (human on the button), not *deployment*. Auto-deploy is a
  reward you earn by trusting your gates, not a default you turn on.
- **Health checks lie.** A `200` from `/health` means "the process started," not "the feature
  works." A shallow health check passes while the app returns garbage to users. Make the check
  meaningful (does it reach its database? can it serve a real request?) and lean on canary/gradual
  rollout for anything important, but know that no health check replaces real tests and real
  monitoring.
- **Rollback isn't free, and some things don't roll back.** Reverting the *running image* is cheap.
  Reverting a **database migration**, a sent email, a charged credit card, or a published message is
  not. Those are forward-only. The cleaner the separation between code deploys and irreversible
  state changes, the more rollback actually saves you. Don't assume "we can always roll back" covers
  data.
- **This lab simulates the target.** A local `docker run` is the deploy logic, not the deploy
  reality. Real targets add networking, DNS cutover, load balancers, zero-downtime orchestration,
  and multiple instances. The five steps hold; the operational surface around them is larger. The
  *compute* that runs all of this (and why you might run your own) is Module 19.
- **"Build once" only holds if you actually do.** The instant someone rebuilds on the prod box "just
  to be sure," you've lost the guarantee that prod runs what CI tested. Deploy the artifact CI built.
  No rebuilds downstream.

---

## Check for understanding

**You're done when:**

- You can state the difference between continuous delivery and continuous deployment in one sentence
  (*who clicks the prod button*) and say which one `tasks-app` should use and why.
- `./deploy.sh` builds, tags by commit SHA, runs the container, and reports a healthy deploy you can
  `curl`.
- You have **watched a bad deploy roll itself back** to the previous good version, and the service
  stayed up.
- You can point at the line in `cd-starter.yml` that turns delivery into deployment, and explain what
  gates have to be trustworthy before you'd flip it.

When a deploy is one command, a bad one reverts itself, and you can argue the delivery-vs-deployment
call for a given repo, you've closed the merged-to-running gap. Module 19 goes underneath all of
this: the runners and compute actually executing your CI/CD, and why you'd own them.

---

## Verify-before-publish

This is expansion-zone material (Module 15+); some specifics drift. Re-check at build/publish time:

- [ ] **Action/runner versions** in `cd-starter.yml` (`actions/checkout`, `actions/setup-python`,
      any build/login/push actions); pin to current major versions and confirm they still exist.
- [ ] **Registry login + push syntax:** the standard build-and-push action names and auth flow
      change; verify against current forge docs rather than the comments here.
- [ ] **Manual-approval mechanism:** the way a forge gates a job behind human approval
      (GitHub `environment` protection rules, GitLab `when: manual`, others) shifts in naming/UI.
      Confirm the delivery-vs-deployment switch still maps to the current feature.
- [ ] **Container runtime commands:** confirm `docker`/`podman` flags used in `deploy.sh`
      (`run`, `--health-*`, `inspect`) match current CLI behavior.
- [ ] **Cross-references** to Modules 16, 17, and 19 still match those modules' final content.
