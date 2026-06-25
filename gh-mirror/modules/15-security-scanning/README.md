# Module 15: Security Scanning for AI-Generated Code

> **Your build is green, your tests pass, and the AI just imported a package that doesn't exist,
> or one an attacker registered last week using exactly the name LLMs like to invent.** CI proves
> the code *runs*; it says nothing about whether it's *safe*. This module adds the gates that catch
> what a build check structurally can't.

---

## Prerequisites

- **Module 1: the `tasks-app`.** The running example. We'll let the AI bolt a "cloud sync" feature
  onto it and watch it introduce all three failure modes at once.
- **Module 2: Version Control as a Safety Net.** Scanners flag findings in a diff; you'll commit,
  re-scan, and confirm a gate goes red then green. Secret scanning in particular cares about *history*,
  not just the working tree; that only makes sense once you think in commits.
- **Module 14: Continuous Integration.** You have a pipeline that runs lint, build, and tests on
  every push. Security scanning is *more gates on that same pipeline*, so you need somewhere to bolt
  them on.

Helpful but not required: **Module 8 (remotes/hosting)** gives you host-native scanning (Dependabot-style
alerts, push protection) that lives on the remote; **Module 10 (reviewing code you didn't write)** frames
scanners as the automated half of that review. Secrets get a full treatment of their own in
**Module 17**; this module's job is to *catch* them, not to manage them.

---

## Learning objectives

By the end of this module you can:

1. Name the three classes of risk AI introduces that a build-and-test pipeline will happily pass:
   vulnerable dependencies, hardcoded secrets, and hallucinated/typosquatted packages.
2. Explain **slopsquatting** and why AI-suggested dependencies are a live supply-chain attack vector,
   not a hypothetical one.
3. Run the three automated gates locally and read their output for real signal vs. noise:
   **SCA (dependency scanning)**, **secret scanning**, and **SAST (static analysis)**.
4. Wire those gates into the Module 14 pipeline so a planted secret or a fake dependency turns the
   build red *before* it merges.
5. Reason about each gate's limits: false positives, the secret that's already leaked, and what
   "no findings" does and doesn't prove.

---

## Key concepts

### Why CI passing is not the same as safe

Module 14's pipeline answers one question: *does this code build, lint clean, and pass its tests?*
That's a question about **behavior the tests exercise.** None of the following change the answer:

- A dependency three levels down has a known remote-code-execution CVE. The code still imports it,
  still runs, tests still pass. Green.
- An API key is hardcoded in a source file. It's a perfectly valid string literal. Lint is happy,
  tests are happy. Green.
- The AI used a SQL query built by string concatenation. The happy-path test passes a normal title;
  the injection case is never exercised. Green.

CI is a *functional* gate. Security scanning is a *non-functional* gate that asks a different
question (*is this code safe to ship?*), and it asks it the only way that scales: automatically, on
every push, with no human remembering to look. You are adding three checkers that each know a class
of problem your tests structurally cannot see.

The reframe for this audience: you already gate merges on "tests pass." You're now adding "no known
vulns, no secrets, no obvious injection" to the same gate. It's the same instinct, *don't let bad
things through automatically*, pointed at a different failure mode.

### The three gates

| Gate | Catches | Category of tool |
|------|---------|------------------|
| **SCA** (Software Composition Analysis) | Known-vulnerable, abandoned, or **non-existent** dependencies | Dependency/vulnerability scanners |
| **Secret scanning** | Credentials committed into source or git history | Entropy + pattern matchers over files and commits |
| **SAST** (Static Application Security Testing) | Insecure code *you wrote*: injection, weak crypto, unsafe deserialization | Static analyzers / linters with a security ruleset |

SCA and SAST split the world cleanly: **SCA scans the code you didn't write (your dependencies);
SAST scans the code you did.** Secret scanning cuts across both: a leaked key is neither a
dependency nor a logic bug, it's a string that should never have been committed.

### Gate 1 (SCA): scanning the code you didn't write

Modern software is mostly other people's code. A ten-line script can pull in a hundred transitive
dependencies, any of which can have a published vulnerability. SCA tools resolve your full dependency
tree and check every package and version against a vulnerability database (CVE feeds, the OSV
database, language-ecosystem advisory databases). Output is a list of "package X version Y has
advisory Z, fixed in version W."

This is well-trodden DevOps. What's *new* with AI is the failure mode at the bottom of the table:
the dependency that **doesn't exist at all.**

#### Slopsquatting: the AI supply-chain attack

LLMs generate plausible text, and a package name is plausible text. Ask for code that talks to a
service and the model will `import` or list a dependency that *sounds* exactly right
(`requests-oauth`, `python-jsonlogger2`, `task-store-client`) but was never published. This isn't
rare; studies of AI-generated code find a meaningful fraction of suggested packages are
hallucinations, and crucially, **the model hallucinates the same plausible names repeatedly.**

Attackers noticed. The attack, nicknamed **slopsquatting** (typosquatting, but aimed at LLM "slop"
rather than human typos), is:

1. Watch what package names LLMs commonly invent.
2. Register those exact names on the public package index, with malware inside.
3. Wait. The next developer who pastes AI output and runs `pip install -r requirements.txt`
   (or `npm install`) pulls your payload, which now runs with that developer's privileges, in their
   dev environment or, worse, in CI.

The defense has two layers, and SCA is where they live:

- **The package doesn't exist (yet).** The install or the resolver fails outright with "no matching
  distribution." Annoying, but *safe*: a name that 404s can't hurt you. The danger is treating that
  as a mere typo and "fixing" it by finding the closest real name without checking it.
- **The package exists but you didn't vet it.** This is the live wire. SCA flags newly-published,
  low-download, or known-malicious packages; combined with the discipline of *never installing a
  dependency the AI suggested without confirming it's the real, intended project*, it closes the gap.

The habit to build: **a dependency the AI added is an untrusted claim until you verify the package is
real, is the one you meant, and is widely used.** Treat the requirements file the AI hands you the
same way you'd treat a stranger handing you a USB stick.

### Gate 2 (secret scanning)

AI loves to hardcode credentials. Ask for code that calls an authenticated API and a model will
write `API_KEY = "sk-live-..."` straight into the source, because that makes the example
*work*, and "make it work" is what it optimizes for. It has no instinct that the key is sensitive.

Secret scanners catch this by scanning files (and crucially, **git history**) for two signals:

- **Known patterns**: provider key formats (cloud access keys, tokens with recognizable prefixes,
  private-key PEM headers, connection strings).
- **High entropy**: random-looking strings that statistically resemble a generated credential even
  when they match no known pattern.

The non-obvious part for this audience: **a secret committed once is leaked forever.** Deleting it in
a later commit doesn't help; it's still sitting in history, and anyone with the repo can
`git log -p` their way to it. So secret scanning runs over *history*, not just the current files, and
a true hit means two jobs, not one: (1) get it out of the code, and (2) **rotate the credential**,
because you must assume it's compromised. Scrubbing history is harder than it looks and is a
recovery-grade operation (Module 12 territory). The cheap win is catching it *before* it's ever
pushed, which is exactly why this gate belongs in the pipeline and, ideally, in a pre-commit hook.

This module catches the secret. *Managing* secrets properly (env vars, secret stores, per-environment
config so the AI never has a key to hardcode in the first place) is **Module 17**. Gate 2 is the
tripwire that proves you need it.

### Gate 3 (SAST): scanning the code you did write

SAST analyzes *your* source for insecure patterns without running it: SQL built by string
concatenation, shell commands assembled from user input, weak or misused crypto, unsafe
deserialization, paths built from untrusted input. It's a linter (Module 14) with a security
ruleset; same machinery, different question.

Why it earns a place specifically for AI code: a model reproduces the patterns it was trained on, and
the internet is full of insecure examples. It will write the string-concatenated SQL query because a
million tutorials did. It looks idiomatic, it passes the happy-path test, and it's a vulnerability.
SAST flags the *shape* of the bug regardless of whether any test happens to trigger it.

SAST is also the noisiest of the three. Expect false positives, expect to tune the ruleset, and
expect to mark some findings "won't fix" with a reason. That's normal and it's why SAST is introduced
*after* the two higher-signal gates: it's the most valuable to tune and the easiest to turn into
ignored red noise if you don't.

### Where the gates run

You want these in more than one place, cheapest-and-earliest first:

- **Local / pre-commit**: fastest feedback, and the only place that stops a secret *before* it
  enters history. A pre-commit hook running secret scanning is the single highest-value placement.
- **CI (the Module 14 pipeline)**: the enforcement gate. Local hooks can be skipped; the pipeline
  can't be, if you require it to pass before merge. This is where "the build goes red" actually
  blocks a merge.
- **Host-native, on the remote**: most git hosts (Module 8) offer some of this for free:
  dependency alerts that watch your manifest against advisory feeds and open issues/PRs when a new
  CVE drops, and push protection that rejects a commit containing a recognized secret at the server.
  Turn these on; they cover the long tail (a CVE published *after* you merged) that a one-shot CI run
  never will.

The same scanner can run in all three. The lab uses one script you can run by hand *and* call from
CI, so there's one source of truth for "what counts as a finding."

---

## The AI angle

These three gates exist in any DevSecOps practice. What makes them matter here is that
AI-assisted coding doesn't just fail to prevent these problems; it actively manufactures all three,
and does it in the exact form that slips past a human skim and a green build:

- **It invents dependencies.** Hallucinated package names are a failure mode unique to generated
  code, and slopsquatting turns that failure into an externally-exploitable supply-chain attack. No
  human typing dependencies by hand produces this risk at the same rate.
- **It hardcodes secrets** because hardcoding makes the example run, and running is what the model is
  rewarded for. The instinct that "this string is dangerous" is exactly the instinct it lacks.
- **It reproduces insecure idioms** by default, because plausible-looking code is the
  whole game, and insecure code is plausible by default: it's all over the training data.

And the volume multiplies all of it. You're merging more code, faster, with less of it read
line-by-line, precisely because the AI made generation cheap. The one defense that scales with that
volume is the one that doesn't depend on a human remembering to look. That's these gates. You don't
add them *despite* using AI; using AI is what moves them from "nice to have" to "required."

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** This lab is self-contained and does not depend
> on the earlier labs. Its files live in `modules/15-security-scanning/lab/`. Copy them into a working folder
> and make a first commit so you start clean:
>
> ```bash
> cp -r ~/ai-workflow-course/modules/15-security-scanning/lab ~/ai-workflow-course/15-security-scanning-lab
> cd ~/ai-workflow-course/15-security-scanning-lab && git init -b main && git add -A && git commit -m "start: module 15"
> ```
**Lab language:** shell, driving Python tooling, on the `tasks-app` from Module 1. You'll install two
scanners (both pip-installable, cross-platform), let the AI introduce all three problems, catch them,
and wire the catch into your pipeline.

> **Windows note:** the scanner *commands* are identical everywhere. The wrapper script
> `lab/security-scan.sh` is bash; run it from Git Bash or WSL, or just run the three commands it
> contains directly in PowerShell. Nothing in the lab needs a specific shell beyond that.

**You'll need:**

- The `tasks-app` repo at `~/ai-workflow-course/tasks-app` under version control from Module 2, and
  your CI pipeline from Module 14.
- Python 3.10+ and `pip`.
- Two scanners installed into your environment. Direct your agent (Claude Code is the worked example;
  sub your own) to install them: *"Install the pip-audit and detect-secrets scanners into this
  project's environment; if pip refuses with an externally-managed-environment error, make a venv
  first and install into that."* The command it runs is `pip install pip-audit detect-secrets`.
  Verify both landed (`pip-audit --version`, `detect-secrets --version`) before you go on.

  > **If `pip install` is refused** with "externally-managed-environment" (PEP 668, common on recent
  > Debian/Ubuntu and Homebrew Python), the scanners install into a per-project virtual environment
  > instead: `python3 -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`),
  > then re-run the install. (`pipx` or `pip install --break-system-packages` also work; a venv is the
  > clean default.) Point your agent at this note if it gets stuck.

  These are concrete, currently-maintained examples of the **SCA** and **secret-scanning**
  categories, not the only choices (see *Where it breaks* and *Verify-before-publish*). The lab
  teaches the moves; the moves transfer to any tool in the category.

- Your coding agent (Claude Code is the worked example; sub your own).

### Part A: Let the AI introduce the problems

Direct your agent (Claude Code is the worked example; sub your own) to place this module's starter
files: *"Copy `~/ai-workflow-course/modules/15-security-scanning/lab/config.py` and
`~/ai-workflow-course/modules/15-security-scanning/lab/requirements.txt` into
`~/ai-workflow-course/tasks-app`."* They're a realistic snapshot of what an AI hands you when you ask
the `tasks-app` to "sync tasks to a cloud service":

- `config.py` → a new module the AI "wrote," complete with a **hardcoded API key**.
- `requirements.txt` → the dependencies the AI "suggested," containing a **vulnerable real
  package**, a **typosquatted** name, and a **hallucinated** name that doesn't exist.

Now open both and read them yourself. They look completely normal, and that's the point: nothing here
would fail a lint or a test. Reading what the agent dropped in, instead of trusting that it landed,
is the move the whole module trains.

If you'd rather generate them instead, tell your agent: *"Add a module to tasks-app that syncs tasks
to a cloud API, and give me a requirements.txt for it."* You'll very likely get a hardcoded key and
at least one questionable dependency for free. Use the provided files if you want the lab to be
reproducible.

### Part B (Gate 1): SCA, and meeting a hallucinated package

From the repo, try to resolve the AI's dependencies. Running the scanner is the lesson, so you run it
by hand:

```bash
cd ~/ai-workflow-course/tasks-app
pip-audit -r requirements.txt
```

It fails before it can audit anything: the resolver can't find one or more packages. **That's
slopsquatting's first tripwire.** Read the error; it names the package it couldn't resolve. Now make
the call this module is really about, and make it *yourself*; this is the human-in-the-loop judgment
no tool and no agent should make for you: *is this a typo I should "fix," or a name that should not
exist?* Do **not** let the agent (or your own reflex) swap in the nearest real name; that reflex is
exactly what the attack relies on. Confirm against the real project's home page which dependency was
actually intended.

Once you've decided, hand the mechanical edit to your agent: *"In requirements.txt, comment out the
two unresolvable lines, `reqeusts==2.31.0` and `task-cloud-sync-client==1.4.2`, and leave the rest."*
Then re-run the scanner yourself:

```bash
pip-audit -r requirements.txt
```

This time it resolves and reports a known vulnerability with an advisory ID and a fixed version. You
decide the advisory applies and the fix is safe, then direct your agent to apply it: *"Bump requests
to the fixed version the advisory names in requirements.txt."* Run `pip-audit` once more until it's
clean. You've now exercised both halves of SCA: the package that *shouldn't exist*, and the package
that exists but *shouldn't be at that version*.

### Part C (Gate 2): secret scanning

Scan for the hardcoded key yourself:

```bash
detect-secrets scan config.py
```

The JSON output lists a detected secret with its file, line, and detector type. That's your tripwire
firing on the AI's hardcoded key.

Now do it right. Direct your agent to apply the fix: *"In config.py, remove the hardcoded
SYNC_API_KEY literal and read it from os.environ instead."* (The file carries the fixed version at
the bottom, commented out, so you can confirm the agent matched it.) Re-scan yourself and confirm the
finding is gone. And say the quiet part out loud: **if that key had been real and ever pushed,
removing it now is not enough; you'd have to rotate it,** because it's in history. (Proper secret
management is Module 17; this is just the catch.)

> **Stretch (Gate 3, SAST):** install a static analyzer for your language (for Python,
> `pip install bandit`, then `bandit -r .`) and watch it flag insecure *code you wrote*: here, the
> MD5-based request signing in `config.py` (weak crypto, CWE-327). Now note what it does **not**
> flag: the hardcoded `SYNC_API_KEY`. Bandit's hardcoded-credential checks (B105–107) key on
> *password-named* identifiers (`password`, `secret`, `token`), so a key named `SYNC_API_KEY` slips
> right past them. Catching that string is a secret scanner's job (Gate 2), not SAST's. Same file,
> two distinct flaws, caught by two different gates with two different blind spots, which is exactly
> why you run all three rather than trusting one. And note how much noisier SAST is than the first
> two gates: that noise is why it's the one you tune.

### Part D: Wire the gates into CI

A scan you have to remember to run is a scan you'll skip. Move it into the Module 14 pipeline so it
runs on every push and blocks the merge.

1. Have your agent place the gate script and make it runnable: *"Copy
   `~/ai-workflow-course/modules/15-security-scanning/lab/security-scan.sh` into
   `~/ai-workflow-course/tasks-app` and make it executable."* The script runs the SCA and secret-scan
   gates and **exits non-zero on any finding**, which is what makes CI go red. Verify the copy landed
   and is executable (`ls -l security-scan.sh` shows the `x` bit) before you trust it.

   Before you run it, the starter files have to be **staged** so the secret gate can see them. Direct
   your agent to stage them, *"Stage config.py and requirements.txt,"* then confirm with `git status`
   that both show as staged.

   That staging step is not a footnote. `detect-secrets scan` with no path argument scans the files
   Git *tracks*; an *untracked* `config.py` is invisible to it, so the gate would report "no secrets"
   on a file that's full of them (a silent false pass, the worst kind). Staging puts the file in
   front of the scanner. It's the same reason the explicit `detect-secrets scan config.py` in
   Part C worked, and the same reason "secrets live in history": the moment Git knows about a file,
   so does the gate. Verifying with `git status` that the files are actually staged is the point, so
   don't skip it.

   To watch the gate catch both planted problems at once, you need the original booby-trapped files
   back (you fixed them in Parts B and C). Direct your agent: *"Re-copy config.py and requirements.txt
   from `~/ai-workflow-course/modules/15-security-scanning/lab/` into the repo, overwriting my fixes,
   and stage them again."* Then run the gate yourself:

   ```bash
   ./security-scan.sh
   ```

   It should **fail on both gates** (the SCA gate on the unresolvable/vulnerable dependencies and
   the secret gate on the hardcoded key), and you should be able to point at which finding caused
   each non-zero exit. Direct your agent to re-apply your Part B/C fixes and re-stage, run the gate
   once more yourself, and it should pass.

2. Merge the security steps into your pipeline. `lab/ci-security.yml` shows the gate as a
   self-contained, provider-neutral job: check out, set up Python, install the scanners, run the
   script. But the `check` job you built in Module 14 *already* checks out the code and sets up
   Python, so you don't want a second job duplicating that work. You want its two **new** steps,
   **install the scanners** and **run the gate**, added to the steps you already have. (Checkout and
   Python are in the snippet only so it reads as a complete example; the agent should skip them when
   it merges.)

   This is a careful edit to an indentation-sensitive file, so direct your agent and then check its
   work against the spec below: *"In my CI workflow, append two steps to the existing `check` job
   after the Test step: one that installs the pip-audit and detect-secrets scanners, and one that
   runs `./security-scan.sh` (chmod it first). Don't add a second job, and don't touch the checkout
   or Python steps."*

   Here is exactly what the result should look like. **Before**: the tail of your Module 14 `check`
   job (GitHub Actions flavor, matching `ci-starter.yml`; on GitLab the same two steps drop into the
   job's `script:`):

   ```yaml
   jobs:
     check:
       runs-on: ubuntu-latest
       steps:
         - name: Check out the code
           uses: actions/checkout@v7
         - name: Set up Python
           uses: actions/setup-python@v6
           with:
             python-version: "3.12"
         - name: Install tools
           run: pip install ruff
         - name: Lint
           run: ruff check .
         - name: Test
           run: python -m unittest
   ```

   **After**: the same job with the two security steps appended; nothing else changes:

   ```diff
          - name: Lint
            run: ruff check .
          - name: Test
            run: python -m unittest
   +      - name: Install scanners
   +        run: pip install pip-audit detect-secrets
   +      - name: Run the security gate
   +        run: |
   +          chmod +x security-scan.sh
   +          ./security-scan.sh
   ```

   > **YAML is indentation-sensitive, so verify the agent matched the existing steps' indentation
   > exactly.** Each new `- name:` should line up in the *same column* as the steps above it, and the
   > keys under it (`run:`) sit one level deeper. A step placed even one space off will silently
   > attach to the wrong block or fail to parse, and the whole workflow breaks. If you'd rather keep
   > the gate as its own job (some teams prefer the isolation), have the agent copy `ci-security.yml`
   > in whole as a second job under `jobs:` in the same workflow file instead; that is exactly why it
   > carries its own checkout and Python steps. The *shape* (install tools, run the gate, fail on
   > findings) is identical everywhere.

3. Now prove the gate works on a live push, and notice the angle: the AI itself commits the mistake,
   and the gate catches it. Direct your agent to plant and ship the regression: *"Re-add the
   hardcoded SYNC_API_KEY to config.py, then commit and push it."* Watch the pipeline go **red** on
   the security step even though lint, build, and tests are still green: your own agent's change,
   blocked by your own gate. Then direct it to undo and push again, *"Remove the hardcoded key again
   and push,"* and watch the pipeline go green. The agent does the git; you verify each result on the
   pipeline.

---

### Gate 0: your hosted forge

Most hosted forges run their own secret scanner on every push and reject the push if it finds a
recognized key pattern (GitHub calls this *push protection*; GitLab and others have equivalents).
That happens **before** any CI you wrote runs, so it is effectively *Gate 0* in this module. The
planted `SYNC_API_KEY` in `lab/config.py` uses a generic high-entropy value (not an issuer
pattern) so the lab can ship; in your real repo, treat your forge's push protection as the
earliest gate and never paper over a bypass.

## Where it breaks

The honest limits (these gates are necessary, not sufficient):

- **A clean scan is not a safe codebase.** Scanners find *known* vulns and *recognizable* patterns. A
  novel logic flaw, a business-logic auth bypass, or a brand-new zero-day in a dependency all pass
  clean. "No findings" means "none of the things these tools know about," not "secure." Human review
  (Module 10) and SAST tuning still matter.
- **The secret that already leaked.** Catching a secret in CI is great; if it was pushed last month,
  the gate is closing the barn door. The credential must be assumed compromised and **rotated**, and
  scrubbing it from history is a separate, harder, recovery-grade job. Prevention (Module 17) beats
  detection here.
- **False positives are real and they erode trust.** SAST especially will flag things that aren't
  exploitable in your context. If every push has noise, people start ignoring red, the worst
  outcome. Budget time to tune rulesets and triage findings, or the gate becomes decoration.
- **SCA depends on a manifest it can read.** If dependencies aren't declared in a file the scanner
  understands (a pinned requirements/lock file, a package manifest), it can't see them. Vendored code,
  dynamically downloaded packages, and "just `pip install` whatever" workflows are blind spots.
- **A 404 today can be malware tomorrow.** A hallucinated name that doesn't resolve now is safe *now*;
  nothing stops an attacker registering it next week. The durable defense isn't "the scan was clean,"
  it's the *habit* of never adding an AI-suggested dependency without verifying it's the real,
  intended, widely-used project.
- **Scanners scan; they don't decide.** A finding is information, not a verdict. Whether a given
  advisory actually affects you (is the vulnerable code path even reachable?) is a judgment call the
  tool can't make. The gate's job is to put the question in front of a human, not to answer it.

---

## Check for understanding

**You're done when:**

- You can state, without looking back, the three classes of risk AI introduces that a green build
  won't catch, and which gate catches each.
- You can explain slopsquatting to a colleague in two sentences, including *why* registering a
  hallucinated name works as an attack.
- Running `./security-scan.sh` on the unmodified starter files **fails**, and on your fixed files
  **passes**, and you understand which finding each exit reflects.
- You've pushed a commit with a planted secret and watched your CI pipeline go red on the security
  step while lint/build/test stayed green, then watched it go green after the fix.
- You can say what a *clean* scan does and doesn't prove.

When a failing security gate feels like the pipeline doing its job, not an obstacle, you're ready
for Module 16, where containers make the environment your code (and these scanners) run in
reproducible.

---

## Verify-before-publish

> **Expansion-zone module: these facts move fast.** Re-check at build/publish time; don't ship the
> claims above from memory.

- [ ] **Pinned CI action versions.** The `ci-security.yml` snippet (and the Part D before/after diff)
      pin `actions/checkout` and `actions/setup-python` to major versions (`@v7`/`@v6` at build time).
      Pinned majors age; confirm they're current and not deprecated against the host's docs, the same
      check the Module 14 and Module 18 CI/CD checklists carry.
- [ ] **Scanner names and install methods.** Confirm `pip-audit`, `detect-secrets`, and `bandit` are
      still maintained and still install as shown. If any has stalled, swap in a current equivalent
      from the *same category* and keep the writing category-first, not tool-first.
- [ ] **Category roster.** Verify the named alternatives still exist and are reasonable to recommend:
      SCA (Trivy, Grype, OWASP Dependency-Check, Snyk, Safety, language-native `npm audit` etc.);
      secret scanning (gitleaks, trufflehog, git-secrets, detect-secrets); SAST (Semgrep, CodeQL,
      SonarQube, Bandit, language-native security linters). Add/remove as the landscape shifts.
- [ ] **Host-native features.** The major hosts' free offerings (dependency alerts, automated
      fix PRs, secret push-protection) change names and availability. Confirm what's actually free vs.
      paid at publish time rather than naming a specific product tier.
- [ ] **Slopsquatting framing.** Re-check the current research on AI package-hallucination rates and
      any newly-reported real-world slopsquatting incidents. Keep the figure qualitative
      ("a meaningful fraction") unless you can cite a current, specific source.
- [ ] **The planted vulnerable dependency in `lab/requirements.txt`.** Confirm the pinned version
      *still* trips an advisory in the scanner (advisory databases get reorganized and old entries
      occasionally change shape). Re-pin to a currently-flagged version if needed so Part B actually
      fires.
- [ ] **The hallucinated/typosquatted names in `lab/requirements.txt`.** Confirm they still do **not**
      resolve on the public index (someone may have since registered one, which would, ironically,
      make the slopsquatting point for you, but breaks the lab's "resolution fails" step). Swap for a
      currently-nonexistent plausible name if so.
