# Module 20: MCP Servers, Giving the AI Hands

> **Until now the AI could read and write files in your repo and nothing else. MCP lets it reach
> your real tools, data, and systems (your task tracker, your database, your docs, your APIs)
> through a standard interface instead of working blind.** And because MCP is an open protocol, not
> a vendor feature, the connections you build outlive whichever model you're running.

---

## Prerequisites

- **Module 1** gave you the `tasks-app` running example, an editor, and a terminal. The lab gives
  the AI hands on this exact app.
- **Module 2** taught you to read a project's state from Git and trust `git restore` to undo a mess.
  That safety net matters more here than anywhere so far: you're about to let the AI *act on real
  systems*, not just edit files.
- **Module 4** put the AI in your editor or CLI (an "agentic tool"), editing files directly. That
  same tool is the **MCP client** in this module; MCP is how you extend what it can reach.
- **Module 5** had you commit the AI's config to the repo. MCP server configuration is more config
  worth committing, and the same "make it travel with the repo" instinct applies.

Helpful but not required: **Module 16** (containers) and **Module 17** (secrets) get referenced when
we talk about *where* a server runs and *what it's allowed to touch*. You can read this module
without them.

This is the opener of **Unit 4: Extend the AI into your systems.** Units 1–3 got the AI safely
editing your code and shipping it. Unit 4 is about giving it reach beyond the repo.

---

## Learning objectives

By the end of this module you can:

1. Explain the MCP client/server model: what a server exposes (tools, resources, prompts), what the
   client (your agentic tool) does, and why "it's a protocol, not a vendor feature" is what makes
   your work survive a model swap.
2. Connect an MCP server to your agentic tool and confirm the AI can call its tools, using either an
   existing reference server (the optional Part A warm-up) or the one you build in Part B/C.
3. Build a tiny MCP server in Python that exposes one real capability over the `tasks-app`, and wire
   it into your tool.
4. Watch the AI *use* that server (read and change real state through a tool call) and verify the
   effect outside the chat.
5. State precisely what MCP does and doesn't give you, including the one caveat this module
   deliberately defers: **installing an MCP server is installing code that runs with access to your
   systems** (handled in Module 22).

---

## Key concepts

### The wall the AI keeps hitting

Everything so far has given the AI exactly one kind of reach: **files in your repo.** Module 4 let
it read and write `cli.py`; Module 2 let it read your Git history. That's a lot, but watch where it
stops.

Ask your agentic tool, *"how many tasks are in my list and which are done?"* and it can answer,
because the data happens to live in a file it can read. Now ask it something one inch further out:

- *"How many active users signed up this week?"* The answer is in a database it can't query.
- *"Is this docs page out of date versus the changelog?"* The docs live in a system it can't read.
- *"File a ticket for this bug."* The tracker is an API it can't call.

The AI's response to all three is some flavour of *"I can't access that, but here's a script you
could run,"* and you're back in the copy-paste loop from Module 1, just one level up. The model is
plenty smart enough to do the work. It's **blind and handless** beyond your files. It can reason
about your systems; it can't *touch* them.

You could solve this the bad way: paste a database dump into the chat, copy the AI's SQL out and run
it yourself, paste the results back. That's Module 1's seam all over again: you as the integration
layer, manually shuttling data between the AI and the real system. MCP exists to delete that loop.

### What MCP is

The **Model Context Protocol (MCP)** is an open standard for connecting AI applications to external
tools and data through a uniform interface. Two roles:

- An **MCP server** exposes capabilities: "here are the things I can do and the data I can provide."
- An **MCP client** (embedded in your agentic tool) discovers those capabilities and calls them on
  the AI's behalf.

That's the entire shape: **servers offer, clients call.** Your editor-integrated AI tool is the
client. A small program you (or someone else) writes is the server. When the AI decides it needs to
add a task, the client calls the server's `add_task` tool, the server does the work against the real
system, and the result comes back into the AI's context. No pasting, no scripts you run by hand.

If you've ever written or consumed an HTTP API, the instinct transfers cleanly: a server advertises
a set of operations; a client calls them with arguments and gets structured results back. The
difference is what it's *for*: MCP is shaped specifically so an AI can **discover** what's available
at runtime (names, descriptions, argument schemas) and decide which call to make, rather than a human
reading docs and hardcoding the call.

### Why "a protocol, not a vendor feature" changes everything

This is the course thesis showing up in the architecture itself. MCP is a **standard**, like HTTP or
SQL, not a button inside one company's product. The consequences are exactly the ones this course
keeps promising:

- **Write a server once; every compliant client can use it.** The `tasks` server you'll build in the
  lab works with any agentic tool that speaks MCP, today's and next year's. You are not building for
  a vendor; you're building for the protocol.
- **Swap the model underneath and your servers don't care.** The server exposes `add_task`; it has
  no idea which model is on the other end of the client. Change models, which you will, and every
  connection you built keeps working. That's the durable-skill payoff Module 1 promised, made real.
- **The catalogue grows on its own.** Because it's a shared standard, there's a large and growing
  set of servers other people already wrote: databases, cloud providers, ticket trackers, docs,
  browsers, your own internal tools. Connecting one is usually configuration, not coding.

MCP originated with one vendor and was released as an open spec; it's since been adopted across major
AI tooling regardless of who makes the model. We name no vendor on purpose: the skill is "wire a
server to a client," and it's the same skill everywhere.

### What a server actually exposes: tools, resources, prompts

An MCP server can offer three kinds of things. You'll mostly care about the first:

- **Tools** are *actions the AI can take.* A tool is a named function with typed arguments and a
  description: `add_task(title)`, `run_query(sql)`, `create_issue(title, body)`. The AI reads the
  description, decides to call it, supplies the arguments, and gets a result. This is the "hands"
  half of the module title; tools are how the AI *does* things. (Tools can have side effects: they
  write to your database, hit your API, change real state. That power is exactly why Module 22
  exists.)
- **Resources** are *data the AI can read.* Read-only context the server makes available: a file, a
  database record, a docs page, the contents of a config. Where tools *do*, resources *inform*:
  they're how the AI gets eyes on a system, the parallel to "durable memory it can read" from
  Module 2, extended past your repo.
- **Prompts** are *reusable prompt templates the server offers* for common operations against it (e.g.
  "summarize this incident from these logs"). Useful, but the least-used of the three; don't worry
  about them while you're learning.

For the lab you'll build **tools**, because tools are where MCP earns the module title. One function,
one decorator, and the AI has a new verb.

### How the client and server talk: transports

The client has to launch or reach the server and exchange messages with it. Two shapes dominate, and
the distinction is practical:

- **stdio (local).** The client launches the server as a subprocess on your machine and talks to it
  over standard input/output, the same pipes a normal command-line program uses. This is the right
  default for anything local: your `tasks` server, a server that reads your filesystem, one that
  drives a local tool. No network, no ports, no auth to set up. **This is what the lab uses.**
- **HTTP-based (remote).** For a server running somewhere else (a shared internal service, a
  vendor's hosted server), the client reaches it over HTTP. This is where authentication and network
  access enter the picture, and where the security stakes climb.

You don't pick the transport at random; it follows from where the server runs. Local tool over a
real system on your box → stdio. Shared or third-party service → HTTP. (The exact name of the HTTP
transport in the spec has changed more than once (see *Verify-before-publish*), but the local-vs-
remote split is the durable idea.)

### Configuring a server: where the wiring lives

To connect a server, you tell your agentic tool how to start it (for stdio) or reach it (for HTTP).
Most tools read this from a small JSON config. The *de facto* common shape for a local server looks
like this:

```json
{
  "mcpServers": {
    "tasks": {
      "command": "python",
      "args": ["/home/you/ai-workflow-course/tasks-app/tasks_mcp_server.py"]
    }
  }
}
```

Read it plainly: *"there's a server called `tasks`; to start it, run `python <that file>` and talk to
it over stdio."* That's the whole contract for a local server.

Two notes, both flowing from the course's core promises:

- **The filename and location of this config are tool-specific, and we won't pin them.** Some tools
  keep it in a project file, some in a user-level file, some let you add servers from a UI. The
  `mcpServers` *shape* above is widely shared, but check your tool's docs for where it reads it. The
  principle ("a server is a name plus how to launch or reach it") outlives any one tool's filename,
  exactly like the committed-instructions file in Module 5.
- **This config is worth committing, with care.** A project-level MCP config means every teammate
  and every agent that opens the repo gets the same tools wired up, which is the Module 5 instinct
  applied one level out. But MCP config often points at paths or, for HTTP servers, endpoints and
  credentials, and **credentials never go in the repo** (that's Module 17, and it's a hard rule).
  Commit the wiring; keep the secrets in the environment.

### Where this is in the repo's reach, and where it's heading

Stack the units up and the picture is clear. Module 4 put the AI in your editor. This module gives
that same AI hands beyond the repo. The next three modules build directly on it:

- **Module 21 (Skills)** teaches the AI *playbooks*, repeatable procedures it runs your way. Skills
  and MCP compose: MCP gives the AI the tools; a skill tells it *how and when* to use them.
- **Module 22 (Securing third-party MCP servers and skills)** handles the danger this module is
  deliberately deferring (see *Where it breaks*). Read it before you install anything you didn't
  write.
- **Module 23 (Working with existing codebases)** leans on MCP to give the AI real access to a large
  repo and the systems around it, so it can orient before it changes anything.

---

## The AI angle

Most integration work wires systems together for *programs* to use: fixed clients calling fixed
endpoints. MCP is shaped for a different consumer: **an AI that decides at runtime what it needs.**
That changes what matters about the integration.

- **Discovery, not hardcoding.** A traditional client is written against specific API calls by a
  human. An MCP client hands the AI a *menu* (tool names, descriptions, argument schemas) and the
  AI picks. Which means the **description you write for a tool is part of the interface**: it's how
  the model knows when to reach for `add_task` versus `list_tasks`. A vague docstring is a vague tool.
  (You'll feel this in the lab: the docstrings on the server functions are not decoration; they're
  what the AI reads.)
- **It closes Module 1's loop at the systems layer.** The original copy-paste pain was shuttling code
  between a chat and a file. The same pain reappears one level out: shuttling *data* between the AI
  and your database, your tracker, your docs. MCP is the editor-integration moment for systems: the
  AI reaches them directly instead of you being the integration layer.
- **It's the model-agnostic bet made concrete.** Every other module argues the workflow outlasts the
  model. MCP *is* that argument in protocol form: the server you write is bound to a standard, not a
  model. Swap the model and your hands stay attached.
- **The reach is the risk.** The very thing that makes MCP powerful, real access to real systems,
  is why it needs its own security module. An AI with hands can do real damage as easily as real
  work. That's not a reason to avoid it; it's the reason Module 22 comes right after.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/20-mcp-servers-giving-the-ai-hands/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 20"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** Python (a ~15-line MCP server) plus your agentic tool's config. Runs on your own
machine, any OS.

You'll do two things: **connect an existing MCP server** to confirm the client/server wiring works
at all, then **build your own tiny server** over the `tasks-app` and watch the AI use it. The second
is where the idea sticks.

**You'll need:**

- The `tasks-app` from Module 1/2 (a folder with `tasks.py`, `cli.py`, and ideally a Git repo so you
  can see and undo what the AI does, per Module 2).
- Your agentic coding tool from Module 4, which is the **MCP client**. Find, in its docs, *where it
  reads MCP server configuration* and *how it shows that a server is connected* (often a list of
  connected servers or available tools).
- Python 3.10+ and the official MCP Python SDK, installed into a virtual environment. Read the
  **Python packages and which `python`** note just below before you have the agent set this up.
- The starter files in this module's `lab/` folder: `tasks_mcp_server.py` and
  `mcp-config-example.json`.
- **Only for the optional Part A warm-up:** the reference server your tool points you at typically
  runs via `npx` (needs Node) or `uvx` (needs uv); install whichever its documented `command`
  needs. Part B/C need only the Python SDK above, so you can skip this.

> **Python packages and which `python`.** This lab's one dependency is the MCP SDK, and *how* it
> gets installed decides whether the server ever connects. Two things bite people, and one is the
> reason you point the agent at the work and then check the result yourself:
>
> - **PEP 668 ("externally-managed-environment").** On modern Debian/Ubuntu and Homebrew Python, a
>   global `pip install` is refused on purpose. The clean fix is a virtual environment per project.
>   Direct Claude Code (or sub your own agent) to set it up:
>
>   > *"In `~/ai-workflow-course/tasks-app`, create a `.venv` virtual environment, install `mcp[cli]`
>   > into it, then tell me the absolute path to that venv's python interpreter."*
>
>   It will run the equivalent of `python3 -m venv .venv` and `.venv/bin/python -m pip install
>   "mcp[cli]"`, and report a path like `/home/you/ai-workflow-course/tasks-app/.venv/bin/python`.
>   (If you'd rather not use a venv, the agent can fall back to `pipx` or
>   `pip install --break-system-packages`; a venv is the clean default and keeps this dependency out
>   of your system Python.)
> - **The install interpreter must match the config's launch command.** This is the load-bearing
>   gotcha of the whole lab, so understand it even though the agent does the typing. Your MCP client
>   starts the server by running the `"command"` in its config, *not* from your activated shell, so
>   activating a venv does nothing to help the client find the SDK. The config's `"command"` must be
>   the venv's **absolute** python path (the one the agent just reported, e.g.
>   `/home/you/ai-workflow-course/tasks-app/.venv/bin/python`, or `...\.venv\Scripts\python.exe` on
>   Windows). If they don't match, the server dies on `import mcp` and your tool just says "not
>   connected" with no obvious reason: the exact failure this lab is about avoiding.
>
> Before wiring anything, confirm the SDK is reachable from the *same* interpreter the config will
> launch. Run this one-line check yourself against the path the agent reported:
>
> ```bash
> /home/you/ai-workflow-course/tasks-app/.venv/bin/python -c "import mcp; print('mcp ok')"
> ```

### Part A: Connect an existing server (optional warm-up, ~10 min)

This part is **optional**: it proves the plumbing works by connecting a server someone else already
wrote, but it's a warm-up. Parts B/C carry the real lesson on the Python SDK you already installed.
The catch is the runtime: most **reference servers** (filesystem, fetch, git, and
more) are distributed for `npx` (Node) or `uvx` (uv), *not* Python, so this warm-up needs whichever
runtime its documented command uses. If you don't already have Node or uv and don't want to install
one for a 10-minute warm-up, **skip straight to Part B**; you lose nothing the rest of the lab needs.

To do it: pick a simple, read-only reference server your tool's docs point you at (a "filesystem" or
"fetch" server is a good first choice), and install the runtime its command needs (Node for `npx`, uv
for `uvx`).

1. Add the server to your tool's MCP config, following the tool's docs. Most reference servers are
   launched the same stdio way as the JSON shape shown in *Key concepts*: a `command` (e.g. `npx` or
   `uvx`) and `args`.
2. Restart or reload your agentic tool so it picks up the config. Confirm it reports the server as
   **connected** and lists its tools.
3. Ask the AI to do something only that server enables. For example, with a fetch server, *"fetch
   example.com and summarize it"*; with a filesystem server scoped to a folder, *"list the files in
   that folder."* Watch the AI **call a tool** rather than tell you it can't.

That's the entire client/server loop, end to end, with zero code you wrote. Now make your own.

> **Stop before you install anything you don't fully trust.** A reference server from the protocol's
> own maintainers is a reasonable warm-up. A random server off the internet is untrusted code that
> will run with your permissions; vetting that is **Module 22's** job, and it's not optional. For
> now, stick to first-party reference servers or the one you write next.

### Part B: Build a one-tool server over the tasks-app

1. Have Claude Code (or sub your own agent) copy this module's `lab/tasks_mcp_server.py` into your
   `tasks-app` folder, next to `tasks.py` and `cli.py`, and confirm it landed there:

   > *"Copy the starter file at `modules/20-mcp-servers-giving-the-ai-hands/lab/tasks_mcp_server.py`
   > into `~/ai-workflow-course/tasks-app/`, next to `tasks.py` and `cli.py`, then show me the
   > contents so I can read it."*

   Then open the copied file yourself and read it. (It reuses `tasks.py` and shares the same
   `tasks.json`, so anything it changes shows up in `python3 cli.py list`.) The whole server is two
   tools:

   ```python
   @mcp.tool()
   def list_tasks() -> str:
       """List every task in the tasks-app, with its index and whether it's done."""
       return _load().render()

   @mcp.tool()
   def add_task(title: str) -> str:
       """Add a new task to the tasks-app. `title` is the text of the task to add."""
       tlist = _load()
       tlist.add(title)
       _save(tlist)
       return f"added: {title}"
   ```

   That's it: a tool is a normal function plus the docstring the AI reads to decide when to use it.

2. Sanity-check that it starts (optional, but it's a useful feel for what stdio does). Ask the agent
   to run the server with the venv python and report what happens:

   > *"Run `~/ai-workflow-course/tasks-app/.venv/bin/python tasks_mcp_server.py` from inside
   > `tasks-app` and tell me what it does, then stop it."*

   It looks like it's hanging. It isn't: a stdio server waits for a client on its stdin/stdout, so
   there's nothing to print and no prompt to return to until a client connects. That waiting *is*
   the correct behavior. You don't run it by hand for real; the client launches it.

### Part C: Wire it into your agentic tool

3. Have the agent write the `tasks` config entry. It already knows both absolute paths (the venv
   python it just reported and the server file it just copied), so let it fill them in. Point it at
   wherever your tool reads MCP config, using `lab/mcp-config-example.json` as the shape:

   > *"Add a `tasks` MCP server entry to <my tool's MCP config file>, using the shape in
   > `lab/mcp-config-example.json`. Set `command` to the absolute venv python path you reported and
   > `args` to the absolute path of the copied `tasks_mcp_server.py`. Do not use a bare `python`."*

   The entry it writes should look like this, with real absolute paths swapped in for the
   placeholders:

   ```json
   "tasks": {
     "command": "/home/you/ai-workflow-course/tasks-app/.venv/bin/python",
     "args": ["/home/you/ai-workflow-course/tasks-app/tasks_mcp_server.py"]
   }
   ```

   (On Windows the venv python is `...\.venv\Scripts\python.exe`.) *Where* the config file lives is
   tool-specific; if your tool adds servers from a UI or your agent can't reach its config, edit the
   entry by hand as the fallback. Either way, a bare `"command": "python"` is the single most common
   reason the server "won't connect": the client launches whatever `python` is on *its* PATH, which
   is usually not the interpreter that has the SDK. That's why the `"command"` must be the absolute
   venv path.

4. Reload your agentic tool and verify it shows the `tasks` server **connected**, with `list_tasks`
   and `add_task` among its available tools. If it doesn't connect, the usual culprits are a wrong
   path, the wrong `python`, or the SDK not installed for that interpreter. Re-run the
   `... .venv/bin/python -c "import mcp"` check from the note above against the *exact* path in
   `"command"`, then check the tool's MCP logs.

### Part D: Watch the AI use its new hands

5. In the AI chat, **don't** mention files or `tasks.json`. Ask in terms of the *system*:

   > *"What's on my task list right now?"*

   The AI should call `list_tasks` and answer from the live result, not from reading a file and not
   from memory. Many tools show the tool call inline ("called `tasks.list_tasks`"); watch for it.

6. Now have it act:

   > *"Add a task: review the Module 20 lab."*

   It should call `add_task("review the Module 20 lab")`. Then **verify the effect outside the AI**.
   This is the part that matters: the change is real, and the proof lives outside the chat. Check it
   the way you'd verify any runtime effect, by reading the *state*, not the repo:

   ```bash
   python3 cli.py list   # the new task is there, because the server wrote the same tasks.json
   cat tasks.json       # the raw state the server changed, end to end
   ```

   The AI just changed real state in a real system through a tool call. Notice what you did *not*
   reach for: `git diff`. `tasks.json` is deliberately gitignored (Module 2's `.gitignore` treats it
   as generated runtime state, not source), so `git diff` stays empty here, and that's correct, not a
   bug. The proof the task list changed is the live state (`python3 cli.py list` / `cat tasks.json`),
   not version control; runtime data the app owns is exactly the kind of thing you keep *out* of
   history. No copy-paste, no script you ran by hand, no pasting `tasks.json` into a chat. That's
   "hands."

7. (Optional, to feel the discovery point.) Edit the docstring on `add_task` to be vague; change it
   to just `"""Adds something."""`, reload, and try the same request. Notice the AI gets *less*
   reliable about choosing the tool. The description is part of the interface; the model reads it to
   decide. Restore the good docstring.

---

## Where it breaks

The caveats, and one of them is large enough that it gets its own module.

- **Installing an MCP server is installing code that runs with your access, and this module does not
  secure it.** A server you connect runs on your machine (stdio) or is trusted by your client (HTTP),
  with whatever permissions you give it: your files, your network, your credentials. A malicious or
  compromised server is malware with an AI driving it, and a server's tool descriptions can even
  carry instructions that try to steer the model (prompt injection). **This module deliberately
  stops here.** The attack surface (vetting servers, pinning versions, least-privilege, prompt
  injection) is **Module 22 (Securing Third-Party MCP Servers and Skills)**, and you should treat
  it as required reading before connecting anything you didn't write. In this module: only first-
  party reference servers and the one you build yourself.
- **A tool with side effects can do real damage as easily as real work.** Your `add_task` writes to
  real state. A `run_query` or `delete_user` tool does too. An AI that confidently calls the wrong
  tool with the wrong arguments isn't a typo in a file you can `git restore`; it might be a row
  deleted from a database Git never backed up (Module 12's limit). Keep destructive tools behind
  confirmation, scope them narrowly, and lean on the safety net: do this against test data first.
- **The AI still has to *choose* the tool correctly.** MCP gives the model hands; it doesn't give it
  judgment. It can call the wrong tool, pass bad arguments, or ignore a perfectly good tool and
  hallucinate an answer instead. Good tool names and descriptions reduce this a lot (Part D step 7);
  they don't eliminate it.
- **More servers, more tools, more noise.** Every connected tool is something the model has to
  consider on every turn. Wire up thirty tools and you dilute the model's attention and slow it down.
  Connect what a task needs; disconnect what it doesn't. (This is the MCP echo of Module 5's "bloat
  kills it.")
- **The spec and SDKs move fast.** This is expansion-zone material. Transport names, SDK APIs, and
  config conventions have all churned and will again. The *client/server, servers-offer-clients-call*
  model is durable; specific commands and field names are not, so verify them at build time.
- **stdio servers are local-only by nature.** The lab's server runs on your machine for you. Sharing
  a server with a team, or reaching one that needs to run elsewhere, means the HTTP transport, which
  drags in auth, network access, and the containerization story from Module 16. Don't reach for that
  until you need it.

---

## Check for understanding

**You're done when:**

- (Optional, Part A) If you ran the warm-up, you connected an **existing** reference MCP server to
  your agentic tool and watched the AI call one of its tools. Skipping it costs nothing; Part C
  connects the server you build and shows the same tool call.
- You built `tasks_mcp_server.py`, wired it into your tool, and saw the `tasks` server report as
  connected with `list_tasks` and `add_task` available.
- You asked the AI a question and it answered by **calling a tool** against the live system, and you
  asked it to add a task and then **verified the change outside the AI** by reading the runtime state
  (`python3 cli.py list` / `cat tasks.json`), not `git diff`, because `tasks.json` is deliberately
  gitignored (Module 2).
- You can explain the client/server model in one breath (*servers expose tools/resources/prompts;
  the client (your agentic tool) discovers and calls them on the AI's behalf*) and why "it's a
  protocol, not a vendor feature" means your server survives a model swap.
- You can state the one caveat this module defers: connecting an MCP server is running code with
  access to your systems, and **Module 22** is where that risk gets handled.

When "the AI can't reach that system" stops being a wall and becomes "so I'll give it a tool," you've
got it. Module 21 takes the next step: teaching the AI the *playbook* for using these hands well.

---

## Verify-before-publish

MCP is moving fast; re-check these at build/publish time rather than trusting this draft:

- [ ] **Python SDK install + API.** Confirm `pip install "mcp[cli]"` is still the package, and that
      `from mcp.server.fastmcp import FastMCP`, the `@mcp.tool()` decorator, and `mcp.run()` are
      still the current FastMCP surface. Run `tasks_mcp_server.py` end to end against a real client.
- [ ] **Transport naming.** The HTTP transport has been renamed in the spec before (an SSE-based
      transport gave way to a "streamable HTTP" one). Verify the current name and any deprecation
      before describing remote transports.
- [ ] **The `mcpServers` config shape.** Confirm it's still the widely-shared convention for stdio
      servers, and that the `command`/`args` fields are current. Keep the lesson tool-agnostic about
      *where* the config file lives.
- [ ] **Reference servers (optional Part A).** Verify which first-party reference servers exist and
      how they're launched today; the catalogue and launch commands change. Don't name a specific
      server that may have moved or been retired without checking. Confirm the named runtimes (`npx`
      via Node, `uvx` via uv) are still how the common reference servers are distributed.
- [ ] **Adoption framing.** Re-confirm the "open standard, adopted across vendors regardless of
      model" claim is still accurate and still vendor-neutral; update if the ecosystem has shifted.
