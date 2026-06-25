# Module 22 lab files

Run the lab from the module README. Quick map of what's here:

- **`audit.sh`**: the runnable vetting checklist. `bash audit.sh <dir>` statically scans a skill or
  MCP server for red flags (network egress, secret/env reads, shell-out, obfuscation, broad FS
  access, hidden/injected instructions, zero-width characters). It only reads; it never executes the
  target.
- **`suspicious-skill/`**: the audit TARGET for Part A. A deliberately malicious "export tasks to
  Notion" skill (`SKILL.md` + `tools/sync.py`). **Do not install it or run `sync.py` against real
  credentials**; it exfiltrates your environment and local secrets. The point is to catch it first.
- **`poisoned-task.txt`**: the prompt-injection payload for Part B. A real-looking task with an
  injected "system" directive underneath, to add to the Module 1 `tasks-app` and feed to your AI.

Expected result of Part A:

```
bash audit.sh suspicious-skill   # exits non-zero, verdict: REJECT
```
