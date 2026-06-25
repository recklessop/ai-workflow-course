# Module 17: Secrets, Config, and Environments

> **Ask an AI to "connect to the API" and it will paste your secret key straight into a source
> file, the one place it must never go.** This module gives you the standard, boring, correct
> place to put secrets and per-environment config instead, and a reflex for catching the AI when
> it does the wrong thing.

---

## Prerequisites

- **Module 2: Version Control as a Safety Net.** You need `.gitignore` and the habit of reading
  `git diff` before you commit. Both matter here.
- **Module 12: Revert, Reset, and Recovery.** You learned that Git history is forever and that
  secrets *don't belong in it*; this module is the practical follow-through on that promise.
- **Module 15: Security Scanning for AI-Generated Code.** Secret scanning is the automated gate
  that catches a hardcoded key after the fact. This module is the *prevention* that means the gate
  rarely has to fire.
- **Module 16: Containers and Reproducible Environments.** A container is a sealed box; config and
  secrets are how you pass the outside world *into* it at run time. That handoff is environment
  variables, which is exactly what this module is about.

You can attempt the lab with only Modules 1–2, but the *why* leans on 12, 15, and 16.

---

## Learning objectives

By the end of this module you can:

1. Explain why a secret in source code is a different and worse problem than a bug, and why Git
   makes it permanent.
2. Move a secret out of code and into the **environment** (an environment variable or a gitignored
   `.env` file), and have the app read it back at run time.
3. Keep config you *can* commit (a committed template) separate from secrets you *can't* (the real
   `.env`), so a teammate or a fresh AI session knows exactly what to supply.
4. Apply the 12-factor rule (*config lives in the environment, not the build*) to run one codebase
   unchanged across dev, staging, and prod.
5. Describe what a secrets manager buys you over `.env` files, in vendor-neutral terms, and know
   when you've outgrown a file on disk.

---

## Key concepts

### A secret in source is not a bug, it's a leak

A bug is a wrong behavior you can fix and move on from. A hardcoded secret is different: the moment
it's written to a file in a repo, you've started a countdown. Commit it and it's in your history
**forever**. Module 12 was blunt about this: `git revert` writes a *new* commit undoing the change,
but the old commit, with the key in plain text, is still right there in the log for anyone who
clones the repo. Push it (Module 8) and it's now on a server, in every teammate's clone, and in
every backup. "Delete the line and commit again" does nothing; the secret is in the snapshot, not
the current file.

So the only real fix after a leak is **rotation**: revoke the exposed key at the provider and issue
a new one, treating the old one as compromised. That's expensive and easy to forget, which is why
the whole discipline is built around one rule: *never write the secret to a tracked file in the
first place.* Prevention is the only cheap fix.

What counts as a secret: API keys and tokens, database passwords and connection strings, private
keys and certificates, signing/encryption keys, OAuth client secrets, webhook signing secrets. The
test is simple. *If this string leaked, would someone have to scramble?* If yes, it's a secret and
it does not go in code.

### Config vs. secrets vs. code

Three things often get jumbled into source files. Pulling them apart is the mental model for the
rest of this module:

| Kind | Example | Where it lives | Goes in Git? |
|------|---------|----------------|--------------|
| **Code** | The logic of your app | Source files | **Yes**, that's the point |
| **Config** | Which backend URL, log level, feature flags, timeouts | The environment (often a `.env` *template* you commit + real values you don't) | The *template* yes, the *values* it depends |
| **Secrets** | API keys, passwords, tokens | The environment, sourced from a secret store in real deployments | **Never** |

The dividing line that matters: **config and secrets are things that change between *where* the app
runs, not *what* the app does.** Your dev laptop, the staging server, and production all run the
same code; they differ only in config (different URLs) and secrets (different keys). That
observation is what the 12-factor rule below is built on.

### The environment: where config and secrets actually go

An **environment variable** is a named value the operating system hands to a process when it
starts. Every OS has them; your shell is full of them right now (`PATH`, `HOME`). They're the
universal, language-agnostic channel for passing config *into* a program without putting it *in* the
program.

Set one for a single command:

```bash
# macOS / Linux
TASKS_API_KEY="sk-live-..." python3 sync.py

# Windows PowerShell
$env:TASKS_API_KEY="sk-live-..."; python3 sync.py
```

Read it back in code, and **fail loudly if it's missing**, because a silent empty string is worse
than a crash:

```python
import os

api_key = os.environ.get("TASKS_API_KEY")
if not api_key:
    raise SystemExit("TASKS_API_KEY is not set. Copy .env.example to .env and fill it in.")
```

That's the pattern. The secret never appears in the file; the file only *asks the environment* for
it. Anyone reading the source learns *that a key is needed* but not *what the key is*, which is
exactly the property you want.

### `.env` files: the developer-friendly middle ground

Typing `TASKS_API_KEY=...` before every command gets old, and exported shell variables vanish when
you close the terminal. The conventional fix is a **`.env` file**: a flat list of `KEY=value`
lines, sitting in your project, that gets loaded into the environment when the app starts:

```
APP_ENV=dev
TASKS_API_KEY=sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c
```

Two non-negotiable rules come with it:

1. **The real `.env` is gitignored. Always.** Add `.env` to your `.gitignore` (Module 2) *before*
   you create the file, so there's never a window where it could be committed. This is the single
   most important line in this module:

   ```gitignore
   # secrets and local config, never commit
   .env
   .env.*
   !.env.example
   ```

   That last two lines say: ignore `.env` and any `.env.something`, **but** keep tracking
   `.env.example` (the `!` un-ignores it). More on that next.

2. **Commit a template, not the secrets.** A `.env.example` (or `.env.template`) lists every
   variable the app needs with **placeholder** values and no real secrets. *This* file you commit.
   It's the documentation that tells a teammate (or the next AI session reading the repo as memory,
   Module 2) exactly what to supply:

   ```
   # .env.example  (committed)
   APP_ENV=dev
   TASKS_API_KEY=replace-me
   ```

Loading a `.env` is usually one line via a small library (every major language has one). You can
also load it with a few lines of your own code and zero dependencies; the lab shows the
dependency-free version so it runs anywhere with just the language installed.

> **Naming, not values, is the contract.** Standardize the variable *names* across the team and
> commit them in the template. The values are local and secret; the names are shared and public.
> When the AI writes `os.environ["TASKS_API_KEY"]`, it should match what's in `.env.example`
> exactly; a mismatch is the most common "works on my machine" failure in this whole area.

### 12-factor: config in the environment, one build everywhere

The principle behind all of this comes from the [12-factor app](https://12factor.net) guidelines,
and factor III states it plainly: **store config in the environment.** The payoff for this audience:

> You build the artifact **once** and run the *same* artifact in every environment. Nothing about
> dev, staging, or prod is baked into the code or the container image; the differences are injected
> at run time as environment variables.

This is why it pairs so tightly with containers (Module 16). A container image is your immutable,
built-once artifact. You don't build a "staging image" and a "prod image"; you build *one* image
and start it with different environment variables:

```bash
docker run -e APP_ENV=staging -e TASKS_API_KEY="$STAGING_KEY" tasks-app
docker run -e APP_ENV=prod    -e TASKS_API_KEY="$PROD_KEY"    tasks-app
```

Same image, different environment. That's what makes the delivery pipeline in Module 18 sane:
promote one artifact through environments instead of rebuilding per stage.

### Per-environment config: dev, staging, prod

"Environments" here means the distinct places your code runs, each with its own config and its own
secrets. The standard three:

- **dev**: your machine. A dev backend, a dev key with low privileges, verbose logging.
- **staging**: a production-like rehearsal. Separate backend, separate key, real-ish data.
- **prod**: the real thing. Real users, the powerful key, conservative settings.

The rule that catches people: **each environment gets its own secrets, and they never mix.** A dev
key must not be able to touch prod data, and a prod key must never sit in a developer's `.env`. The
clean pattern is one variable that *names* the environment (`APP_ENV`), which the code uses to pick
the right URLs and behavior, plus per-environment secret *values* supplied separately:

```python
import os

ENVIRONMENTS = {
    "dev":     "https://api.dev.example-tasks.com/v1",
    "staging": "https://api.staging.example-tasks.com/v1",
    "prod":    "https://api.example-tasks.com/v1",
}

app_env = os.environ.get("APP_ENV", "dev")
backend_url = ENVIRONMENTS[app_env]   # config selected by environment, not hardcoded
```

The *non-secret* per-environment config (which URL goes with which env) is fine to keep in code
like this; it's not sensitive and it's the same everywhere the code runs. Only the *secret values*
and the *choice of which environment this process is* come from outside.

### Secret stores: when a file on disk isn't enough

A gitignored `.env` is the right tool on your laptop. It does not scale to a running fleet, for
reasons that show up fast in real operations:

- A plaintext file on a server is readable by anything that compromises that box.
- You can't **rotate** a key across fifty machines by editing fifty files.
- You get no **audit trail**: no record of who read which secret when.
- There's no **access control**: "this service can read the DB password but not the signing key."

A **secret manager** (also called a secrets store or vault, categorically) solves these. It's a
dedicated service that stores secrets encrypted at rest, hands them out only to authenticated
callers, logs every access, and supports rotation and fine-grained access policies. At run time your
app (or the platform it runs on) fetches the secret from the manager into memory instead of reading
a file. The categories you'll encounter:

- **Cloud-provider managers**: every major cloud has one, tightly integrated with that cloud's
  identity system.
- **Standalone / self-hostable vaults**: dedicated secret-management products you run yourself, a
  good fit for the on-prem and air-gapped scenarios this audience often lives in (the same
  self-host instinct from Module 8).
- **Platform-native secrets**: your container orchestrator and your CI/CD system both have a
  built-in concept of "secrets" you can inject as environment variables, which is how secrets reach
  a pipeline (Module 14) or a deployment (Module 18) without ever touching the repo.

You don't need a manager for the lab or for a solo project. You need it the moment a secret has to
be available to *more than one machine you don't personally babysit*. The mental upgrade is the same
either way: **the app reads its secret from the environment; what populates the environment grows
up from a file to a service.** Your code doesn't change, which is the point of reading from the
environment all along.

---

## The AI angle

This module exists because of one specific, recurring AI failure mode: **AI loves to hardcode
secrets.** Ask any coding assistant to "add authentication," "connect to the database," or "call
the API," and a large fraction of the time it will write the key, token, or password directly into
the source file, often with a comment like `# your API key here`. It does this because its training
data is full of tutorials and quick examples that do exactly that, and because a literal value is
the path of least resistance to working code. The code *runs*, the demo *works*, and a leak is now
one `git commit` away.

This is the textbook case of the recurring course theme: **AI output that looks right and runs is
not the same as output that's safe.** A human who knows better still has to catch it, because the
model will keep offering it. Concretely:

- **Make "where did the secret go?" a review reflex.** Every time the AI touches auth, config, or a
  network call, read the `git diff` (Module 2) and grep the change for anything that looks like a
  key before you commit. The diff is where you catch it cheaply, *before* it's in history.
- **Tell the AI the pattern up front.** Put the rule in your committed instructions file (Module 5):
  *"Never hardcode secrets. Read all keys and config from environment variables; add new ones to
  `.env.example`."* A model given that house rule will usually write the `os.environ` version on the
  first try. This is the prevention-by-config payoff Module 5 promised.
- **Let the AI do the refactor; it's good at it.** The same model that hardcodes a key on the way
  in is good at pulling it back out when you ask: "move every hardcoded secret and
  environment-specific value into environment variables, fail loudly if they're missing, and update
  `.env.example`." That's exactly the lab.
- **Secret scanning is the backstop, not the plan (Module 15).** A scanner in CI catches the key
  you missed, but by then it may already be in a commit. Treat a scanner hit as a *rotation event*,
  not a code-review comment. The goal of this module is that the scanner stays quiet because the
  secret never reached the repo.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** This lab is self-contained and does not depend
> on the earlier labs. Its files live in `modules/17-secrets-config-and-environments/lab/`. Copy them into a working folder
> and make a first commit so you start clean:
>
> ```bash
> cp -r ~/ai-workflow-course/modules/17-secrets-config-and-environments/lab ~/ai-workflow-course/17-secrets-config-and-environments-lab
> cd ~/ai-workflow-course/17-secrets-config-and-environments-lab && git init -b main && git add -A && git commit -m "start: module 17"
> ```
**Lab language:** Python + shell, on a new `sync` feature for the `tasks-app` from Module 1.

You'll take a file that hardcodes a secret (the exact thing an AI hands you) and refactor it so the
secret lives in the environment and the real values never enter Git. As in every module past
Module 4, you direct the agent to do the git and setup work and then verify the result; you don't
type the commands by hand. Then you'll make it select config per environment.

**You'll need:**

- The `tasks-app` folder from Modules 1–2 (a Git repo with a `.gitignore`).
- Python 3.10+ and a terminal.
- The starter files in this module's `lab/starter/`: `sync.py` (the before) and `.env.example`.
- Claude Code in your terminal (`claude --version` to confirm it's installed; sub your own agent).

### Part A: See the smell

1. Copy `lab/starter/sync.py` and `lab/starter/.env.example` into your `tasks-app` folder, then run
   the before-picture:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   python3 sync.py
   ```

   It prints a simulated request, including `Authorization: Bearer sk-live-...`. Open `sync.py` and
   find the two hardcoded lines: `API_KEY` and `BACKEND_URL`. **This is the AI default.** Picture
   this getting committed and pushed: the key is now in history forever (Module 12) and a secret
   scanner (Module 15) would light up, if you were lucky enough to have one.

### Part B: Gitignore the secret *first*

2. Before any real secret exists, close the door. Tell Claude Code (sub your own agent) to set up
   the ignore rules:

   > *"Add rules to `.gitignore` that ignore `.env` and any `.env.*` file but keep tracking
   > `.env.example`, then create a real `.env` with `APP_ENV=dev` and a throwaway
   > `TASKS_API_KEY=sk-live-test-0000`. Explain the `!.env.example` negation line."*

   The agent edits `.gitignore` and writes the file; you supplied the *ordering* that matters
   (ignore the secret before the secret exists). The rules should land like this:

   ```gitignore
   # secrets and local config, never commit
   .env
   .env.*
   !.env.example
   ```

3. Now **verify** the door actually closed. Read `git status` yourself:

   ```bash
   git status        # .env must NOT appear; .env.example and your .gitignore change SHOULD
   ```

   If `.env` shows up in `git status`, the ignore rule is wrong; have the agent fix it before going
   further. This verification is the step that prevents the leak.

### Part C: Refactor the secret into the environment

4. Now move the secret and the environment-specific URL out of the code. Ask Claude Code (sub your
   own agent):

   > *"Refactor `sync.py` so it reads `TASKS_API_KEY` and `APP_ENV` from environment variables
   > instead of hardcoding them. Pick the backend URL from `APP_ENV` (dev/staging/prod). Fail loudly
   > with a clear message if `TASKS_API_KEY` is missing. Don't add any third-party dependency; load
   > the `.env` file with a few lines of plain Python, and make sure the loader does **not**
   > overwrite a variable that's already set in the environment, so a value passed on the command
   > line still wins."*

   You're looking for a result shaped like this (read the diff before you accept it):

   ```python
   import os
   from pathlib import Path

   def load_dotenv(path: Path) -> None:
       """Minimal .env loader, no dependency. Real projects use a library for this."""
       if not path.exists():
           return
       for line in path.read_text().splitlines():
           line = line.strip()
           if not line or line.startswith("#") or "=" not in line:
               continue
           key, _, value = line.partition("=")
           os.environ.setdefault(key.strip(), value.strip())

   load_dotenv(Path(__file__).parent / ".env")

   ENVIRONMENTS = {
       "dev":     "https://api.dev.example-tasks.com/v1",
       "staging": "https://api.staging.example-tasks.com/v1",
       "prod":    "https://api.example-tasks.com/v1",
   }

   app_env = os.environ.get("APP_ENV", "dev")
   api_key = os.environ.get("TASKS_API_KEY")
   if not api_key:
       raise SystemExit("TASKS_API_KEY is not set. Copy .env.example to .env and fill it in.")
   backend_url = ENVIRONMENTS[app_env]
   ```

   Confirm there is **no literal key left anywhere** in `sync.py`:

   ```bash
   grep -n "sk-live" sync.py     # should print nothing
   ```

   **Why `setdefault` and not plain assignment?** The loader uses `os.environ.setdefault(key, value)`,
   which sets a variable *only if it isn't already set*. That precedence is load-bearing: a value the
   environment already supplies (like an `APP_ENV` you pass on the command line) wins over the
   `.env` file. A loader that writes `os.environ[key] = value` instead **clobbers** anything already
   there, so the file silently overrides your command line and Part D's override demo does nothing.
   This matches the real-world dotenv default (`override=False`): the file fills in gaps, it doesn't
   stomp on what's already in the environment. If the AI hands you plain assignment, that's the
   correction to make.

### Part D: Run it from the environment

5. Run it reading from your `.env`:

   ```bash
   python3 sync.py                # loads .env -> dev URL, key from the file
   ```

6. Now prove the 12-factor point: **same code, different environment, no edit.** Override at the
   command line to act like staging, then prod:

   ```bash
   # macOS / Linux
   APP_ENV=staging python3 sync.py
   APP_ENV=prod    TASKS_API_KEY="sk-live-prod-key" python3 sync.py
   ```

   ```powershell
   # Windows PowerShell
   $env:APP_ENV="staging"; python3 sync.py
   ```

   Watch the backend URL change with `APP_ENV` while the source never does. That's config in the
   environment. **If the URL *doesn't* change, your loader is clobbering variables that were already
   set:** it's using `os.environ[key] = value` where it needs `os.environ.setdefault(...)` (see
   Part C). Fix the loader so the command line wins, and the override takes effect.

### Part E: Commit, and verify the secret didn't tag along

7. Have the agent commit the refactor, then **read the diff yourself before you accept it** (the
   review reflex from the AI angle). Tell Claude Code (sub your own agent):

   > *"Stage and commit the refactor with a message like 'Read secrets and per-env config from the
   > environment, not source'. Include the refactored `sync.py`, the `.gitignore` change, and
   > `.env.example`; do NOT stage the real `.env`."*

   Now verify the agent staged the right things. Read the staged diff and the status yourself:

   ```bash
   git diff --cached            # the refactored sync.py + .gitignore + .env.example
   git status                   # clean; .env remains untracked
   ```

   The diff must contain the *template* and the *code that reads the environment*, and **not** the
   real key or your `.env`. If the real `.env` slipped into the commit, that's a leak in the making;
   have the agent unstage it and recommit before you move on.

You've now done the exact refactor that turns the AI's default mistake into the correct pattern, and
left behind a `.env.example` so the next person (or agent) knows what to supply.

---

## Where it breaks

- **`.env` is not encryption.** A `.env` file is plaintext on disk. Gitignoring it keeps it out of
  *Git*, not out of reach of anything with access to your machine. It's the right tool for local
  dev and the wrong tool for a shared server, which is where a secret manager earns its place.
- **Environment variables leak in their own ways.** They can show up in process listings, crash
  dumps, log lines that print the whole environment, and child processes that inherit them. Reading
  from the environment is far better than hardcoding, but it's not a force field: don't log the
  environment, and scrub secrets from error reports.
- **A committed template can still leak by accident.** The scheme only holds if `.env.example`
  stays free of real values. It's easy to "just fill it in to test" and commit it. Keep the
  placeholder discipline, and lean on the Module 15 scanner as the backstop for the day you slip.
- **The damage may already be done.** If a secret was *ever* committed, even in a commit you later
  reverted, assume it's compromised and **rotate it**. Removing it from current files does not
  remove it from history. Scrubbing history is possible but disruptive (and Module 12 warned you
  about rewriting shared history); rotation is the reliable fix.
- **Managed secrets aren't automatically safe.** A secret manager with over-broad access policies,
  or one whose secrets you copy into a `.env` "just for now," gives back everything it was supposed
  to protect. The tool only helps if least-privilege access and rotation are actually configured.

---

## Check for understanding

**You're done when:**

- `sync.py` runs entirely from the environment, and `grep "sk-live" sync.py` prints nothing.
- A real `.env` exists, contains your secret, and does **not** appear in `git status`, while
  `.env.example` is tracked.
- `APP_ENV=staging python3 sync.py` and the default run hit different backend URLs with **zero**
  source edits between them.
- You can state, in one sentence, why deleting a committed secret and re-committing does not fix the
  leak, and what the actual fix is (rotation).
- You've added a "never hardcode secrets; read from the environment" rule to your committed
  instructions file (Module 5), so the AI stops reintroducing the problem.

When the AI hands you a hardcoded key and your first instinct is "that goes in the environment, and
the diff has to prove it didn't reach Git," the reflex is installed. Module 18 takes this artifact
(built once, configured per environment) and ships it.

---

## Verify-before-publish

This is an expansion-zone module; the durable concepts (env vars, `.env`, 12-factor, the
config/secret/code split) are stable, but anything naming a specific product drifts. Before
publishing:

- [ ] **Keep secret-manager references categorical.** The text deliberately names *categories*
      (cloud-provider managers, standalone/self-hostable vaults, platform-native secrets), not
      products. If you add specific product names, re-verify each still exists, is current, and
      isn't pinned as *the* answer (vendor-neutral rule, AGENTS.md).
- [ ] **Re-check the 12-factor reference.** Confirm the [12factor.net](https://12factor.net) link
      resolves and that "factor III, config" is still phrased as "store config in the environment."
- [ ] **Re-verify `.gitignore` negation behavior.** Confirm `!.env.example` still un-ignores the
      template under the `.env.*` rule with a current Git, and that `git status` behaves as the lab
      claims.
- [ ] **Re-verify the Windows PowerShell syntax** (`$env:VAR="..."`) and the inline
      `VAR=value command` syntax for macOS/Linux against current shells.
- [ ] **Confirm dependency-free `.env` loading still reads correctly** under the current Python
      version, so the lab runs with no `pip install`.
- [ ] **Confirm cross-references** to Modules 2, 5, 8, 12, 14, 15, 16, and 18 still match those
      modules' final numbering and titles.
