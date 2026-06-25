# Module 16: Containers and Reproducible Environments

> **"Works on my machine" is a confession, not a defense.** A container ships the machine with the
> code, so your app, your CI, and your deploy target all run the exact same environment. It also
> gives you a throwaway box to run an agent you don't fully trust.

---

## Prerequisites

- **Module 1**: the `tasks-app` running on your machine, an editor, and a terminal.
- **Module 2**: version control. A Dockerfile is committed, diffable config like any other file;
  the environment becomes something you review in a PR, not something you reconstruct from memory.
- **Module 14**: Continuous Integration. CI already runs your checks on a clean machine. This
  module is what makes that clean machine *identical* to your laptop and to where you'll deploy.
- **Module 15**: security scanning and dependency hygiene. Important here as a boundary: a
  container faithfully reproduces your dependencies, including the vulnerable ones. Containers are
  **not** a substitute for the hygiene Module 15 taught; they're downstream of it.

You do **not** need Docker installed yet; that's the first step of the lab. This module looks
forward to Module 18 (deployment: a container is *what* you ship) and, lightly, to Units 4–5, where
that same throwaway box becomes the place you let an agent run.

---

## Learning objectives

By the end of this module you can:

1. Explain what a container actually is (image vs. container vs. registry) and what
   "reproducible" buys you that "it works for me" never could.
2. Write a Dockerfile for a real app, build an image, and run the app from inside the container.
3. Prove the image behaves identically in a clean container with nothing of yours on it.
4. Use a disposable container as a sandbox to run a command, or an agent, you don't fully trust.
5. State precisely where containers stop helping: not a security boundary by default, image bloat,
   and not a replacement for dependency hygiene.

---

## Key concepts

### "Works on my machine," diagnosed

Your code never runs alone. It runs on top of an implicit stack you mostly can't see: an OS and its
system libraries, a specific language runtime version, a set of installed packages, environment
variables, file paths, locale, a clock. When you say "it works on my machine," you're really saying
"it works on top of *that whole invisible stack*, which I happen to have, and which I've never
written down."

Hand the code to a colleague, a CI runner (Module 14), or a server, and the invisible stack is
different. The failures are maddeningly specific: a different Python patch version changes a default,
a system library is missing, an env var you set six months ago and forgot turns out to be required.
The bug isn't in the code. The bug is that the *environment* never traveled with it.

A container is the fix: it packages the code **and the invisible stack together** into one artifact
that runs the same everywhere. You stop shipping just the code and start shipping the machine.

### Image, container, registry, Dockerfile

Four words that get used loosely. Pin them down, because the rest of the module leans on the
distinction:

- **Image**: a built, read-only, layered filesystem snapshot: the language runtime, your code, its
  dependencies, all frozen together. The artifact. Analogous to a class.
- **Container**: a running (or stopped) instance of an image. You can start many from one image;
  each gets its own writable scratch layer on top. Analogous to an instance of that class.
- **Registry**: where images are stored and shared, the way a Git remote (Module 8) stores repos.
  You `push` an image to a registry and `pull` it elsewhere. (Most git hosts now bundle one.)
- **Dockerfile**: the plain-text recipe that *builds* an image. This is the part you version. It is
  the executable, reviewable specification of the environment, the same instinct as committing the
  AI's config in Module 5, applied to the whole machine.

### It is not a virtual machine

The ops reframe that matters: a container is **not** a VM. A VM virtualizes hardware and boots a
whole guest OS: its own kernel, gigabytes, slow to start. A container shares the **host's kernel**
and isolates only the process and its filesystem view. It's much closer to a souped-up `chroot`
or a BSD jail with packaging and distribution bolted on than to a hypervisor. That's why containers
start in milliseconds and weigh megabytes instead of gigabytes.

Hold onto "shares the host kernel." It's also exactly why a container is not a strong security
boundary by default (more in *Where it breaks*).

### The Dockerfile, line by line

Here's a Dockerfile for the `tasks-app`. The full version is in
[`lab/Dockerfile`](lab/Dockerfile); this is the shape:

```dockerfile
FROM python:3.12-slim          # base image: the invisible stack, made explicit and pinned
ENV PYTHONUNBUFFERED=1         # environment, frozen in; no more "did you set that var?"
WORKDIR /app                   # a fixed path that's the same on every machine
COPY tasks.py cli.py ./        # your code goes in
RUN useradd appuser && chown appuser /app   # don't run as root (hygiene, not a fence)
USER appuser
ENTRYPOINT ["python", "cli.py"]   # what runs when the container starts
CMD ["list"]                      # the default argument, overridable at run time
```

Each instruction adds a **layer**. Layers are cached and reused: change only `cli.py` and Docker
rebuilds from the `COPY` step down, reusing the base image and everything above. Order your
Dockerfile cheapest-to-most-volatile (base and dependencies first, your fast-changing code last) and
rebuilds stay fast. This is the same reason you install dependencies *before* copying source in a
real project, so a one-line code change doesn't reinstall the world.

### The levers that make it actually reproducible

"Containerized" and "reproducible" are not the same word. A container guarantees *the same image*
runs the same; it does not by itself guarantee that **rebuilding** gives you the same image. The
levers that close that gap:

- **Pin the base image.** `python:3.12-slim` is better than `python:latest`, but the `3.12-slim`
  tag still moves as it gets patched. For bit-for-bit reproducibility, pin the digest:
  `FROM python:3.12-slim@sha256:…`. Choose your point on the spectrum deliberately; a moving tag
  picks up security patches automatically; a pinned digest never changes under you. Both are valid;
  silence is not.
- **Pin your dependencies.** This is Module 15's lesson, and the container is where it bites. A
  Dockerfile that runs `pip install <pkg>` with no version reproduces *whatever was newest at build
  time*, which is not reproducible at all. Use a lockfile. The container is only as deterministic as
  what you install into it.
- **Use a `.dockerignore`.** See [`lab/dockerignore-starter`](lab/dockerignore-starter). What isn't
  copied into the build can't bloat the image or leak into it, the same instinct as `.gitignore`
  from Module 2.

### Why this snaps CI and deploy into one line

Module 14 sold CI as "a clean machine that runs your checks." The unsolved half was that the clean
machine still wasn't *your* machine: "passes locally, fails in CI" was a real, common, miserable
bug. Containers remove it. When CI builds and runs the same image you build and run locally, the
environment is identical by construction. "Works in CI but not locally" stops being possible because
there's only one environment now, not two that drift.

The same artifact carries forward: the image CI builds is the image Module 18 deploys. Build once,
run identically on laptop, pipeline, and production.

---

## The AI angle

Docker itself you may already know. What makes containers matter *more* in AI-assisted work:

- **AI writes code for an environment it can't see.** The model assumes packages are installed, a
  certain runtime version, paths that exist on *its* imagined machine. "Works on my machine"
  becomes "works on the machine the model pictured," and that machine is no one's. A Dockerfile
  forces the environment to be explicit, so the AI's assumptions either hold or fail loudly at build
  time instead of mysteriously at run time.
- **The environment becomes reviewable.** AI-suggested setup ("just run these eight commands") drifts
  and rots and lives in a chat log. A Dockerfile turns that into one committed, diffable file. When
  the AI changes how the environment is built, it arrives as a diff in a PR (Module 10), the same
  win as committing the AI's config in Module 5, extended to the whole machine.
- **A container is a sandbox for an agent you don't fully trust.** This is the forward-looking one.
  As you let AI do bolder things, run commands, install packages, execute its own code, and
  eventually (Units 4–5) operate as an agent, you want a blast radius. A throwaway container gives
  you one: mount only what it needs, drop the network if it doesn't need it, let the agent do its
  worst, then `docker rm` the whole thing. The host never saw it. This is the practical foundation
  for running less-trusted agents, and we'll build on it when MCP servers and skills (Unit 4) start
  executing third-party code.
- **But a container does not make AI code safe.** It reproduces whatever the AI wrote, including a
  hallucinated dependency (Module 15) or a hardcoded secret (Module 17), now faithfully baked into an
  image and shipped everywhere. Containers are a *reproducibility and blast-radius* tool, not a
  correctness or security tool. They sit alongside Module 15, not on top of it.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/16-containers-and-reproducible-environments/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 16"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** shell (Docker CLI) on the `tasks-app` from Module 1. You won't write Python; you'll
containerize and run the app you already have.

**You'll need:**

- The `tasks-app` folder from Module 1 (`tasks.py`, `cli.py`).
- A container engine. **Docker Desktop** (macOS/Windows) or **Docker Engine** (Linux) is the common
  choice; **Podman** works too and the commands below map 1:1 (`podman` for `docker`). Verify with
  `docker --version` (or `podman --version`). **The engine must be *running* before you build:**
  `docker --version` reports the client version even when the engine is stopped, so it's false
  reassurance; `docker build` then fails with "Cannot connect to the Docker daemon." On
  macOS/Windows start it first (launch Docker Desktop, or `podman machine start`); confirm the daemon
  is up with `docker info` (or `podman info`), which only succeeds when the engine is actually live.
- The starter files from this module's `lab/`: [`Dockerfile`](lab/Dockerfile) and
  [`dockerignore-starter`](lab/dockerignore-starter).
- Your coding agent (Claude Code is the worked example; sub your own).

### Part A: Build the image

1. Get the two starter files into your `tasks-app` folder. Direct your agent (Claude Code is the
   worked example; sub your own) to do the placement: *"Copy this module's lab/Dockerfile into
   `~/ai-workflow-course/tasks-app`, and create a file named exactly `.dockerignore` there from
   lab/dockerignore-starter."* Then read the Dockerfile top to bottom yourself before you build:
   every line is commented, and you want to know what you're about to run, not just that the file
   landed. The build is the lesson, so you run it by hand:

   ```bash
   cd ~/ai-workflow-course/tasks-app
   docker build -t tasks-app .
   ```

   The first build pulls the base image and runs each instruction as a layer. Watch the output: that
   is the invisible stack being made explicit.

### Part B: Run the app from inside the container

2. Run the CLI *inside* the container. The `--rm` flag deletes the container when it exits, so you
   don't pile up dead ones:

   ```bash
   docker run --rm tasks-app list                  # uses the CMD default -> python cli.py list
   docker run --rm tasks-app add "containerize it"  # override CMD with your own argument
   docker run --rm tasks-app list
   ```

   Notice the third command shows **no** "containerize it" task. That's not a bug; it's a lesson:
   each `--rm` run is a fresh container with a fresh writable layer, and `tasks.json` is written
   *inside* that layer, which is destroyed on exit. Containers reproduce the **environment**, not
   your **state**. (Persisting state means mounting a volume, a deliberate choice, covered when we
   deploy in Module 18.)

### Part C: Prove it's reproducible on a clean machine

3. The honest test of "works on my machine, solved" is: run it somewhere that has *nothing* of
   yours. The container already is that place; it has no access to your installed Python, your
   packages, or your paths. Confirm with the inverse experiment: run the **same base image** with
   *only* the engine and look for your app:

   ```bash
   docker run --rm python:3.12-slim python -c "import sys; print(sys.version)"
   ```

   That's a clean Python with none of your code. Now confirm CI-grade reproducibility: run the
   Module 14 test suite in a clean, throwaway container that mounts your code and runs it with the
   standard-library `unittest` runner: nothing to install, and no test tooling baked into your app
   image (that keeps it lean; see *Where it breaks*):

   ```bash
   docker run --rm -v "${PWD}:/app" -w /app python:3.12-slim \
     python -m unittest
   ```

   > **On Windows:** this step bind-mounts your code, so the host path matters. Run it from WSL (or
   > Git Bash), or from PowerShell; `${PWD}` resolves correctly in each. The other `docker run`
   > commands mount nothing of yours and are identical everywhere.

   > **On native Linux:** the container runs as root by default, and the bind mount maps that straight
   > onto your real project folder, so the `__pycache__` directories Python writes during the test
   > run land in your repo owned by `root:root`, and you can't delete them without `sudo rm -rf`.
   > Prevent it by telling Python not to write bytecode in the container: add
   > `-e PYTHONDONTWRITEBYTECODE=1` to the `docker run` line (with pytest you'd also pass
   > `pytest -p no:cacheprovider` to suppress `.pytest_cache`). A `.gitignore` won't help; it hides
   > the files from Git but they're still on disk and still sudo-only to remove. Avoid `--user
   > $(id -u):$(id -g)` here: it fixes ownership but breaks any in-container `pip install` into the
   > image's root-owned site-packages.

   This is, in miniature, exactly what containerized CI does. If it passes here, it passes the same
   way on any machine with the engine; your laptop's local Python version is now irrelevant.

### Part D: Use the container as a sandbox (the AI angle, hands-on)

4. Now use a disposable container as a blast-radius box for something you don't fully trust. Ask your
   agent (Claude Code is the worked example; sub your own) for a one-line shell command that
   "inspects the system," the kind of thing you'd hesitate to paste straight into your real terminal.
   Then run it where it can't touch your host: no network, read-only root filesystem, and nothing of
   yours mounted:

   ```bash
   docker run --rm --network none --read-only python:3.12-slim \
     sh -c "<the command the AI gave you>"
   ```

   `--network none` cuts it off from the internet; `--read-only` stops it writing to the container
   filesystem; `--rm` destroys the container after. Whatever the command does, it does it to a box
   that exists for one second and touches nothing you care about. **This is the pattern** for running
   less-trusted commands and, later, less-trusted agents: the foundation Units 4–5 build on. (Read
   *Where it breaks* before you trust it with something genuinely hostile.)

5. Commit your work. The Dockerfile and `.dockerignore` are environment-as-code, so version them
   like anything else. Direct your agent (Claude Code is the worked example; sub your own) to stage
   and commit them: *"Stage the Dockerfile and .dockerignore and commit them with a clear message
   about containerizing the tasks-app for a reproducible environment."*

   Then verify the result, because what got committed is the point. Have the agent show you the
   commit (`git show --stat HEAD`) and confirm it staged **only** those two files. `tasks.json`
   should be absent: your `.dockerignore` and `.gitignore` exclude it, and runtime state has no
   business in either the image or the repo. If the agent staged anything you didn't expect, that's
   the review gate (Module 10) doing its job before the environment-as-code ships.

---

## Where it breaks

Be honest about the limits; this audience will find them the hard way otherwise.

- **A container is not a security boundary by default.** It shares the host kernel and, out of the
  box, runs with more privilege than people assume. A process running as root inside a default
  container is root in a way that can reach the host through known escape paths, and `--privileged`
  or mounting the Docker socket throws the door wide open. The non-root `USER` in the lab Dockerfile
  is hygiene, not a fence. *Real* isolation needs more: rootless mode, user namespaces, dropped
  capabilities, seccomp/AppArmor profiles, and for genuinely hostile workloads a stronger sandbox
  with its own kernel (gVisor, Kata Containers, or a real VM). Treat the lab's `--network none
  --read-only` as raising the cost of mischief, not as a guarantee against a determined attacker.
- **Reproducible ≠ small.** A naive image can be hundreds of megabytes to multiple gigabytes:
  full base images, build toolchains left in the final layer, the `.git` directory copied in.
  Bloat is slow to pull, expensive to store, and a larger attack surface. The defenses: slim or
  distroless base images, multi-stage builds (build in a fat image, copy only the artifact into a
  thin one), and a real `.dockerignore`.
- **It does not replace dependency hygiene (Module 15).** A container reproduces your dependencies
  *perfectly*, including the vulnerable and the hallucinated ones. Pinning a base image with a known
  CVE just reproduces that CVE on every machine, reliably. Containers are downstream of Module 15,
  not a substitute: you still scan dependencies, and you scan the *image itself* (its base layers
  carry their own vulnerabilities).
- **Base images drift.** "Reproducible" has degrees. A moving tag like `3.12-slim` can build into a
  different image next week. You choose: pin the digest for true reproducibility, or track the tag to
  pick up patches automatically. Both are defensible; an unpinned `latest` is not.
- **It reproduces the environment, not the world.** Containers freeze the runtime and the
  dependencies. They do **not** freeze your database, external APIs, the wall clock, the network, or
  GPU drivers. "It builds reproducibly" is not "it behaves identically against live systems." Same
  family of honesty as Module 2: the tool captures exactly one slice of reality, and you have to know
  which slice.
- **The host abstraction is leaky off Linux.** On macOS and Windows the engine runs a hidden Linux
  VM, so containers there aren't quite native: bind-mount performance differs, file permissions and
  line endings can surprise you, and architecture (arm64 vs amd64) can bite when an image built on an
  Apple-silicon laptop lands on an x86 server. Build for the architecture you'll run on.

---

## Check for understanding

**You're done when:**

- `docker build -t tasks-app .` succeeds and `docker run --rm tasks-app list` prints the app's
  output; your app runs in an environment that has nothing of yours on it.
- You ran the Module 14 test suite inside a clean container and watched it pass without relying on
  your local Python.
- You ran a command you didn't fully trust inside a throwaway, network-less container and can explain
  why the host was safe, *and* can name one case where it wouldn't have been.
- You can state, without looking back: a container is not a VM, it's not a security boundary by
  default, and it doesn't replace dependency hygiene from Module 15.
- Your `Dockerfile` and `.dockerignore` are committed: the environment is now version-controlled,
  reviewable config.

When "works on my machine" stops being something you say and starts being something you build, you're
ready for Module 17, which handles the one thing you must *not* bake into that image: secrets.

---

## Verify-before-publish

Expansion-zone module: container tooling and base images move. Re-check at build/publish time:

- [ ] **Base image tag.** Confirm `python:3.12-slim` (in the README and `lab/Dockerfile`) is still a
      current, supported tag, and that it matches the version Module 14's CI pins. Bump both together
      if the course's baseline Python moves.
- [ ] **Engine commands and flags.** Verify `docker build`/`run`, `--rm`, `--network none`,
      `--read-only`, and the `-v`/`-w` flags behave as written on a current Docker/Podman release,
      and that the `podman`-for-`docker` 1:1 claim still holds.
- [ ] **Rootless / security defaults.** Container engines are steadily hardening defaults (rootless,
      user namespaces). Re-check that the "not a security boundary by default" framing and the named
      hardening tools (gVisor, Kata, seccomp/AppArmor) are still accurate and current.
- [ ] **Bundled registries.** The "most git hosts now bundle a registry" aside: confirm it's still
      true of the major hosts at publish time rather than from memory.
- [ ] **`useradd` on the base.** Confirm the Debian-slim base still ships `useradd` (it does today;
      a future minimal base might not), or switch to the engine's documented non-root pattern.
