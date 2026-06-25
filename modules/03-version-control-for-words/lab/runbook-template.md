<!--
  Runbook template: the step-by-step for one operational task.

  A runbook is read under pressure, often by someone who is not the person who wrote it and not at
  their best (it's 3 a.m., something is on fire). Optimize for "follow it exactly, no thinking
  required." Concrete commands, expected output, and what to do when a step fails.

  In the Module 3 lab (optional variant) you hand this to the AI to draft a runbook, then review the
  draft as a diff before merging. Write one command/step per line so git diffs stay clean.

  Delete these HTML comments when you write the real runbook.
-->

# Runbook: <task name>

- **Purpose:** <one sentence: what this runbook gets you out of>
- **When to run:** <the trigger, e.g. the alert, the symptom, or the request>
- **Owner:** <team or role responsible>
- **Last verified:** YYYY-MM-DD

## Before you start

<!-- Access, tools, or context the operator needs in hand before step 1. -->

- <prerequisite>

## Steps

<!-- Numbered, concrete, copy-pasteable. After a command, say what success looks like so the operator
     knows whether to continue. -->

1. <action>

   ```bash
   <command>
   ```

   Expected: <what you should see>

2. <action>

## Verify

<!-- How to confirm the task actually worked, not just that the commands ran without error. -->

- <check>

## If it goes wrong

<!-- The two or three most likely failure modes and what to do about each. Where to escalate. -->

- **<symptom>** → <what to do>
