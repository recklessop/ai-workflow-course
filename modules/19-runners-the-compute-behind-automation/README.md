# Module 19: Runners, the Compute Behind the Automation

> **Every green check in the last five modules ran on someone else's computer. This module is where
> you find out whose, and decide whether it should be yours.** Owning the runner is what turns "I
> use a CI pipeline" into "I own the pipeline, end to end."

---

## Prerequisites

- **Module 8: Remotes and Hosting.** You push to a forge, and you met the self-host track
  (Forgejo, Gitea, GitLab CE, and others). Self-hosted runners are the compute half of that same
  "own your own infrastructure" decision.
- **Module 14: Continuous Integration.** You have a CI workflow that lints and tests `tasks-app`
  on every push. Module 14 mentioned, in passing, that the job runs on "a fresh, throwaway Linux
  machine the forge spins up." This module is the full accounting of that machine.
- **Module 18: Continuous Delivery and Deployment.** The deploy jobs you automated there run on
  the same compute. Once you self-host, deploy steps get direct line-of-sight to your private
  infrastructure: a feature and a footgun, both covered here.
- Helpful but not required: **Module 16: Containers**, since most runners execute jobs in
  containers and ephemeral runners lean on them.

You don't need to have read Module 18 in full. If you only have CI from Module 14, everything here
still lands. CD just gives you a second, higher-stakes reason to care where jobs run.

---

## Learning objectives

By the end of this module you can:

1. Explain what a runner *is*, the actual process and machine that executes your pipeline steps,
   and tell, for any job, whether it ran on hosted or self-hosted compute.
2. Make a reasoned hosted-vs-self-hosted decision for a given pipeline, on the five axes that
   actually move the needle: cost, data control, network reach, hardware, and air-gap/compliance.
3. Register a self-hosted runner against your forge and run the `tasks-app` CI job on it.
4. State, without flinching, the central security tradeoff: a self-hosted runner executes arbitrary
   code, is non-ephemeral by default, and can be a backdoor into your network. Name the
   mitigations that make it survivable.

---

## Key concepts

### A runner is just a computer that does what the YAML says

A runner is **a process, on some machine, that checks out your code and executes the steps in your
pipeline**, nothing more exotic than that. When your Module 14 workflow says "set up
Python, install pytest, run the tests," *something physical* has to do that: pull the repo onto a
disk, run `pip install`, run `pytest`, report pass or fail back to the forge. That something is the
runner.

The loop every runner runs, regardless of forge:

1. **Register** with the forge once, using a registration token, so the forge knows it exists.
2. **Poll** the forge: "got any jobs for me?"
3. When a job matches, **pull the code and the job definition**, then execute each step in order.
4. **Stream logs and the final status** (pass/fail) back to the forge.
5. Go to 2.

That's the whole machine. Everything else (hosted vs. self-hosted, ephemeral vs. persistent,
containerized vs. bare metal) is a variation on *which computer runs that loop and who owns it.*

### Hosted runners: you've been renting

Up to now, every job ran on a **hosted runner**: a machine the forge owns, spins up on demand, and
bills you for. This is the default and, for most work, the right default. What you're actually
getting:

- **A fresh, throwaway machine per job.** This is the property Module 14 leaned on: "works on my
  machine" can't hide, because the machine has *nothing of yours on it.* The job starts from a clean
  image and the machine is destroyed afterward. Clean room, every time.
- **No ops burden.** You don't patch it, scale it, or keep it online. It exists for the length of
  your job and then it's gone.
- **Metered billing.** You pay in **runner-minutes**: wall-clock time your jobs spend executing,
  usually with a free monthly allotment and then per-minute pricing above it. Different machine
  sizes (more CPU/RAM, GPUs) bill at higher multipliers.

For a small Python test suite, hosted is perfect. The job is short, needs nothing private, and the
clean-room property is pure upside. You will keep using hosted runners for most of what you do.

### Self-hosted runners: you own the computer

A **self-hosted runner** runs that exact same loop (register, poll, execute, report) but on a
machine *you* own: a spare server, a VM in your own cloud account, a box in your homelab, a beefy
workstation under a desk. You install the forge's runner agent, register it with a token, and it
starts pulling jobs. To the pipeline author, almost nothing changes; the workflow just targets your
runner instead of a hosted one (the targeting mechanic is below).

This is the compute analogue of the Module 8 decision. There, you chose between pushing your repo to
a hosted forge versus self-hosting one. Here, you choose between renting compute to run your
pipeline versus owning it. Same instinct, applied one layer down.

### Why you'd run your own: the five real reasons

Don't self-host for the vibe of it. Self-host when one of these actually applies:

1. **Cost at volume.** Runner-minutes are cheap until they aren't. A heavy pipeline (large test
   matrices, container builds, long integration suites, or the AI eval/agent jobs from Unit 5 that
   call models on every run) can run the meter hard. If you already own idle hardware, a self-hosted
   runner turns "per-minute forever" into "electricity you're already paying for." (Verify the
   crossover with real numbers; see the checklist at the end.)

2. **Data control.** Hosted runners execute your code, with your secrets, on infrastructure you
   don't own. For a lot of work that's fine. For regulated data, customer data under contract, or a
   shop with a "source never leaves our perimeter" rule, it isn't. A self-hosted runner keeps the
   checkout, the build, and the secrets on hardware you control.

3. **Network access to private systems.** This is the one IT pros hit first and hardest. Your CD job
   (Module 18) needs to deploy to a server on your private network. Your tests need a database that
   lives on an internal VLAN. A hosted runner sits on the public internet and cannot reach any of
   that without you punching holes in your firewall. A self-hosted runner placed *inside* your
   network already has line-of-sight, with no inbound holes and no VPN gymnastics. (This is also
   exactly why it's a security problem; hold that thought.)

4. **Custom or specialized hardware.** GPUs for ML work, a specific CPU architecture, more RAM than
   any hosted tier offers, a hardware security module, a USB device for hardware-in-the-loop tests.
   If your job needs hardware the forge doesn't rent, you bring your own.

5. **Air-gapped or fully on-prem operation.** A self-hosted forge (Module 8) on an isolated network
   has nowhere to send jobs *except* a self-hosted runner on that same network. There is no hosted
   option in an air gap. If your whole stack lives behind a wall, the runner lives there too.

If none of these apply, stay on hosted. "I want to" is not on the list.

### The mechanic: register, target, run

The shape is the same on every forge; only the command names and config filenames differ. Three
moving parts, vendor-neutral.

A **registration token** ties a runner to a forge. It's generated in the forge's settings, under its
"Runners" or "CI/CD" section, at the repo, org, or instance level. It's short-lived and proves the
runner is allowed to attach here. Because it lives behind the forge's web UI, this is the one part of
standing up a runner that stays a human-in-the-browser step.

A **register/config command** turns that token into a running agent. The agent and its flags vary by
forge: GitHub-style Actions uses a `config` script then a `run` script (or a service); GitLab uses
`gitlab-runner register`; Forgejo/Gitea use `act_runner register` then `act_runner daemon`. Every one
does the same two things, though: write a small local identity file, then start the poll loop. A
successful registration confirms the runner and it shows up online in the forge. What that looks like:

```text
$ act_runner register --instance https://git.example.com --token *** --labels self-hosted,linux
INFO Runner registered successfully.
INFO Runner self-hosted is now online.
```

The flags drift between releases, so they're something to look up against current runner docs rather
than memorize (see the checklist).

A **label** is how a workflow picks a runner. A runner advertises labels (`self-hosted`, `linux`,
`gpu`, `internal-net`); a job selects them with `runs-on:` in Actions-style YAML, or `tags:` in
GitLab. So moving a job from hosted to your own runner is one line:

```yaml
# before, hosted:
runs-on: ubuntu-latest
# after, your runner, selected by label:
runs-on: [self-hosted, linux, internal-net]
```

That one line is the whole "I now own this pipeline" switch. Everything else in your Module 14
workflow stays identical, because the runner runs the same loop either way.

### Ephemeral vs. persistent: the property that matters most

A hosted runner is **ephemeral**: fresh machine per job, destroyed after. A self-hosted runner is
**persistent by default**: the same machine, with the same disk, runs job after job. That difference
is the source of nearly every self-hosted runner security incident, so it gets its own section below;
flag it now. The clean-room guarantee you got for free with hosted runners is something you have to
*rebuild on purpose* when you self-host.

---

## The AI angle

Two things make runners specifically an AI-era topic, not a generic ops footnote.

**1. AI pipelines are compute-hungry, and that changes the cost math.** Unit 5 puts agents *inside*
the pipeline: jobs that call a model to review a PR, triage an issue, or attempt a fix on a failing
build. Module 25 takes this further, into agents running as **triggered or scheduled runner jobs**, kicked
off on a cron or by an event rather than a human push. Those jobs run longer and fire more often than
a lint-and-test pass, and every one of them consumes runner-minutes. The "rent vs. own compute"
decision you're learning here is the one that keeps an AI-heavy pipeline from quietly becoming your
biggest line item. When you reach Module 25 and stand up an agent that runs unattended on a schedule,
*this* is the machine it runs on.

**2. The agent needs hands, and the self-hosted runner is the hands.** A self-hosted runner inside
your network is the most direct way to give an automated agent real reach: deploy access, internal
databases, private services. That's the payoff and the peril in one sentence. The same property that
makes a self-hosted runner useful for an unattended agent (it can touch your real systems) is exactly
what makes it dangerous when the code it runs isn't yours. Which brings us to the part you cannot skip.

**3. AI writes the CI config too.** Ask an agent to "set up CI" and it will happily emit
`runs-on: self-hosted` or wire a deploy step, because it's pattern-matching on examples that did. AI
also opens PRs (Module 11), and a pull request, from a human or an agent, is *untrusted code that
your pipeline may execute.* You review the *code* in a PR (Module 10); you also have to review what
your pipeline *does with that PR's code* before it runs on hardware that can reach your network. The
review reflex from Module 10 has to extend to the workflow files, not just the application code.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** This lab is self-contained and does not depend
> on the earlier labs. Its files live in `modules/19-runners-the-compute-behind-automation/lab/`. Copy them into a working folder
> and make a first commit so you start clean:
>
> ```bash
> cp -r ~/ai-workflow-course/modules/19-runners-the-compute-behind-automation/lab ~/ai-workflow-course/19-runners-the-compute-behind-automation-lab
> cd ~/ai-workflow-course/19-runners-the-compute-behind-automation-lab && git init -b main && git add -A && git commit -m "start: module 19"
> ```
**Lab language:** shell, plus a one-line edit to the YAML workflow from Module 14. Runs on your own
machine and your own forge, with no hosted account required for the core of it.

This lab has two tracks. **Track A** is mandatory and works for everyone: find out exactly where your
jobs run today and walk the security tradeoffs concretely. **Track B** is the real thing: register a
self-hosted runner and run `tasks-app` CI on it. Do Track A always; do Track B if you have a forge you
can attach a runner to (a self-hosted forge from Module 8 is ideal; a hosted account where you control
a repo also works). If a real runner is too heavy right now, Track A alone satisfies the module.

**You'll need:**

- Your `tasks-app` repo with the Module 14 CI workflow in it.
- The two starter files in this module's `lab/` folder:
  - `whoami-runner.yml`, a tiny workflow that reports *where it ran*.
  - `inspect-runner.sh`, a script you run on a candidate runner machine to see what an attacker
    would see if they got code execution on it.
- For Track B: a forge you can register a runner against, and a spare machine or VM to be the runner
  (your laptop is fine for a one-off; don't leave it registered).
- Claude Code (sub your own agent).

### Track A: Find out whose computer you've been using (everyone)

1. **Make the invisible visible.** Direct Claude Code (sub your own agent) to place
   `lab/whoami-runner.yml` in the same workflow directory your Module 14 `ci.yml` lives in, then
   commit and push it. State the goal, not the path: *"Drop this whoami-runner workflow into the right
   workflows directory for this forge, commit it, and push."* The agent resolves the directory for an
   Actions-style forge (`.github/`/`.forgejo/`/`.gitea/` under `workflows/`). **You verify:** the run
   shows up on the forge. It runs the same lint-and-test as Module 14, then prints the runner's
   hostname, OS, user, whether it looks ephemeral, and whether it can reach the public internet. The
   receipt step carries `if: always()` so it still prints even when lint or test fail; a diagnostic
   shouldn't disappear on a red build (the job still reports red). On GitLab CI the same idea is
   `when: always` on the job.

2. **Read the receipt.** Open the job logs on your forge and read the `Where did this run?` step.
   You're now able to answer, for a real job, the question this module opened with: *whose computer
   was that?* On a hosted runner you'll see a generic cloud hostname and a throwaway user. Note it,
   because you'll compare against your own runner in Track B.

3. **See what code execution would expose.** On the machine you'd *consider* using as a self-hosted
   runner (your laptop is fine for the exercise), run:

   ```bash
   bash lab/inspect-runner.sh
   ```

   It inventories what a job (*any* job, including one from a pull request) could see if it ran
   here: environment secrets, cloud credential files, SSH keys, Docker socket access, and which
   private hosts on your network are reachable. This is not hypothetical. A workflow step is a shell
   command; whatever the script can see, a malicious workflow step can see too.

4. **Walk the tradeoff with Claude Code (sub your own agent), grounded in that output.** Paste the
   `inspect-runner.sh` output into the agent and ask: *"If this machine were a self-hosted CI runner
   and someone opened a pull request with a malicious workflow step, what could they reach or steal?
   Rank it worst-first."* Read the answer against your real output. This is the honest version of "why
   you'd run your own": the network reach that makes a self-hosted runner *useful* is the exact same
   reach that makes a compromised one *catastrophic.*

### Track B: Own the pipeline (if you can attach a runner)

5. **Get a registration token.** In your forge's settings, find the Runners / CI/CD section and
   generate a runner registration token (repo-level is the tightest scope, so start there).

6. **Register the runner.** Hand this to Claude Code (sub your own agent) on your runner machine:
   *"Look up the current runner-agent docs for my forge, then download the agent, register it against
   my forge URL with this token, label it `self-hosted`, and start it polling."* The commands are
   forge-specific and drift between releases, which is exactly why you let the agent fetch the current
   docs instead of running a half-remembered command. **You verify:** the runner shows as **online**
   in the forge's Runners list.

7. **Aim CI at your runner, the one-line switch.** Tell Claude Code (sub your own agent): *"Change
   the `runs-on:` (or `tags:`) line in the `tasks-app` CI workflow to target my `self-hosted` runner
   instead of the hosted image, then commit and push."* That's the before/after edit from Key
   concepts. **You verify:** from the job log, the run executed on your own runner.

8. **Watch your own machine do the work.** Open the job logs. The lint-and-test pass from Module 14
   now runs on hardware you own. Re-run the `whoami-runner.yml` workflow too and compare its output to
   step 2: your hostname, your user, and, critically, note that it is **not** a fresh throwaway
   machine. Run it twice and look for leftovers (a `pip` cache, files from the previous run). That
   persistence is the thing to respect.

9. **Clean up.** Have Claude Code (sub your own agent) stop and unregister the runner agent on your
   machine. Then **remove the runner** from the forge's Runners list yourself; that side is a forge-UI
   step. **You verify:** the runner disappears from the list. A registered-but-forgotten runner is a
   standing liability, exactly the kind of stale backdoor the security section warns about.

---

## Where it breaks

This is the section that earns the module. Self-hosted runners are the single sharpest-edged tool in
this course. Be honest about all of it.

- **A runner executes arbitrary code; that's its entire job.** A "workflow step" is just a shell
  command someone put in a file in the repo. The runner runs it, faithfully, with whatever access
  that machine has. There is no sandbox unless you build one.

- **Pull requests are untrusted code, and this is the headline risk.** On a public repository, *anyone
  can fork it, edit the workflow, and open a PR*, and on a misconfigured setup, your self-hosted
  runner will dutifully execute their workflow on your hardware, inside your network. This is not
  theoretical: in 2025, real attacks used exactly this path. A malicious fork PR pulled a reverse
  shell onto a self-hosted runner and used the available token to push malicious code back to the
  origin repo. The blunt, widely-repeated guidance: **do not attach self-hosted runners to public
  repositories.** If you must, require manual approval before workflows from forks/first-time
  contributors run, and never give those jobs your real secrets.

- **Persistent runners accumulate compromise.** Because the default self-hosted runner is *not*
  ephemeral, anything a job leaves behind (a cached credential, a background process, a tampered
  tool on `PATH`) survives into the next job. A single compromised run can become a permanent
  implant. The fix is **ephemeral runners**: tear the environment down and rebuild it after every
  job (typically by running each job in a fresh container or a disposable VM). This is more setup, and
  it's the price of getting back the clean-room property hosted runners gave you for free.

- **Network reach cuts both ways.** The reason you self-host, line-of-sight to internal systems, is
  also why a compromised runner is a pivot point into your network. Put runners on an isolated
  segment with only the egress they actually need, run them as a dedicated low-privilege user (never
  root, never your own login), and scope their secrets to the minimum. Treat the runner as
  semi-trusted at best.

- **"Free" compute isn't free.** You trade per-minute billing for ops work: patching the OS, keeping
  the agent online and version-matched to the forge (a runner much older than the server can
  fail jobs in subtle ways), scaling under load, and securing all of the above. For a busy pipeline
  on idle hardware that math wins. For an occasional test run, the hosted clean room is cheaper once
  you count your own time.

- **Autoscaling is a real project, not a checkbox.** Matching a fleet of runners to bursty demand,
  spinning ephemeral runners up and down on a queue, is its own piece of infrastructure. Don't
  assume one box; don't assume it's trivial to make it many.

---

## Check for understanding

**You're done when:**

- You can look at any pipeline run and state whether it executed on hosted or self-hosted compute,
  and back it up from the job's own output (you ran `whoami-runner.yml` and read the receipt).
- You can give the five reasons to self-host and honestly say which, if any, apply to your situation,
  instead of self-hosting by default.
- (Track B) You ran `tasks-app` CI on a runner you own, by changing a single targeting line, and you
  saw firsthand that it is not a throwaway machine.
- You can explain, to a skeptical colleague, the central tradeoff in one breath: a self-hosted runner
  executes arbitrary code on your hardware with reach into your network, is persistent by default, and
  must never be casually attached to a public repo. You can name ephemeral runners, network
  isolation, and least-privilege as the mitigations.

When "where does this run, and what can it touch?" is a question you ask reflexively about every job,
and especially every job triggered by a PR or, soon, by an agent, you own the pipeline end to end.
Module 25 will put autonomous agents on exactly this compute; you now know what they're standing on.

---

## Verify-before-publish

This is an expansion-zone module and the runner ecosystem moves. Re-check at build/publish time:

- [ ] **Runner agent commands and config filenames** for each forge named (the GitHub-style
      `config`/`run` scripts, `gitlab-runner register`, `act_runner register`/`daemon`). Flags and
      script names drift between releases; confirm against current official runner docs, don't pin
      from memory.
- [ ] **Hosted runner pricing and free-minute allotments**, and the machine-size multipliers, for any
      forge a reader is likely to use. These change and vary by plan; state them as "check current
      pricing" rather than a hard number, and re-verify the cost-crossover framing.
- [ ] **Fork-PR / untrusted-workflow defaults**: whether the major forges run fork PRs on
      self-hosted runners by default or require approval, and the exact setting names. The security
      guidance here depends on current defaults; confirm them.
- [ ] **Ephemeral-runner mechanics**: the current supported way to run jobs ephemerally
      (per-job containers, disposable VMs, the `--ephemeral`-style flags) on each forge.
- [ ] **The 2025 attack reference**: keep it accurate and current; if newer, clearer public
      incidents exist at publish time, cite the most representative one rather than an aging example.
- [ ] **Runner-to-server version-compatibility guidance**: confirm the "keep the agent version
      matched to the forge" caveat still reflects current behavior.
