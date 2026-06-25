# Module 13: Testing in the AI Era

> **AI writes code that looks right and passes a human skim. That's exactly the code that needs a
> test.** The same AI that produces the risk is excellent at writing the tests that catch it, once
> you know how to direct it.

---

## Prerequisites

- **Module 1**: the `tasks-app` running example you'll be testing, and a working Python + terminal.
- **Module 2**: commits as checkpoints and reading `git diff`. Tests and a clean commit history are
  the two halves of "I can trust this change."
- **Module 10**: reviewing a diff the AI produced for *plausibility traps*, not just correctness.
  This module is the automated, repeatable version of that same instinct: a test reviews the code for
  you, the same way, every time.

You can parachute in here with only Modules 1–2 if you must. You'll have the app and version control,
which is enough to do the lab. But the payoff lands hardest if you've already felt the review problem
from Module 10, because a test is how you stop reviewing the same thing by hand forever.

This is the last module before **Module 14 (Continuous Integration)**. The tests you write here are
the exact thing CI will run automatically on every push, so leaving here with a real test file is the
setup for the next module.

---

## Learning objectives

By the end of this module you can:

1. Say what a test actually *is*: a small program that runs your code and asserts what should be
   true, and run one with Python's built-in `unittest`, no installs.
2. Explain why AI-generated code specifically needs automated verification, beyond a careful read.
3. Direct an AI to write *meaningful* tests for code, and recognize the trap where it writes tests
   that merely re-state current behavior instead of encoding intent.
4. Use a test to expose a real bug in code that looked correct, then fix the code (not the test) and
   watch the suite go green.
5. Leave with a runnable test file that Module 14 can wire into CI unchanged.

---

## Key concepts

### What a test actually is

Strip away the frameworks and a test is the least mysterious thing in this course: **a small program
that runs a piece of your code and asserts that the result is what it should be.** If the assertion
holds, the test passes silently. If it doesn't, the test fails loudly and tells you exactly which
expectation broke.

You've already been testing, by hand. Every time you ran `python3 cli.py list` and eyeballed the
output, you ran a manual test: *do something, check the result looks right.* The problem with the
manual version is the same problem copy-paste had in Module 1: it doesn't scale across files or
across time. You can't re-run "eyeball every command" on every change, so you don't, so regressions
slip in. An automated test is that same check, written down once and run forever for free.

Python ships a test framework in the standard library, `unittest`, so there is nothing to install.
A test is a method whose name starts with `test_`, living in a class that subclasses
`unittest.TestCase`, using assertion methods to state expectations:

```python
import unittest
from tasks import TaskList

class TestTaskList(unittest.TestCase):
    def test_add_appends_a_task(self):
        tl = TaskList()
        tl.add("write the tests")
        self.assertEqual(len(tl.tasks), 1)        # expectation, stated as code
        self.assertEqual(tl.tasks[0].title, "write the tests")
```

The whole suite runs from the project folder with a single command: `python3 -m unittest`
auto-discovers files named `test_*.py`, and `-v` prints each test name and its result. A verbose run
looks like:

```text
$ python3 -m unittest -v
test_add_appends_a_task (test_tasks.TestTaskList) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

A passing run ends in `OK`. A failing one ends in `FAILED (failures=1)` and shows the line, the
expected value, and the actual value. That diff between *expected* and *actual* is the entire value
of the thing.

> A note on `unittest` vs `pytest`. The wider Python world mostly uses `pytest`, which is terser
> (plain `assert`, no class boilerplate) and nicer to use, but it's a third-party install. We use
> `unittest` here so the lab runs on a clean machine with zero dependencies and the test file is
> something you can drop into CI in Module 14 without a `pip install` step first. Everything you learn
> transfers directly; if your team standardizes on `pytest` later, the *thinking* is identical and the
> mechanical translation is an afternoon.

### Why AI output specifically needs verification

Here's the failure mode that makes this module non-optional. AI-generated code has a property normal
buggy code doesn't: **it is optimized to look correct.** The model produces code that reads
plausibly, uses the right function names, follows the conventions it saw in your file, and passes a
human skim, because "looks like correct code" is close to what it was trained to produce. Correct
*behavior* is a separate thing the model is often right about and sometimes confidently wrong about,
and the surface gives you almost no signal about which.

This is the exact trap from Module 10's review skill, sharpened. When you review human code, sloppy
code looks sloppy (odd naming, weird structure, obvious gaps), and the look is a useful tripwire.
AI code removes that tripwire. The buggy version and the correct version look equally clean. You can
read a wrong implementation three times and approve it, because nothing about it *looks* wrong.

A test doesn't read the code. It *runs* the code and checks the result. It is immune to plausibility.
That immunity is precisely what AI-assisted work needs more of, because the one signal you used to
rely on, "does this look right?", has been actively defeated.

### AI is excellent at writing tests

Writing tests is the chore that keeps most people from having a real suite: it's tedious, it's not
the feature, it's easy to skip. AI removes that excuse almost entirely. Describe the code and the behavior you care about, and a competent model will
produce a solid first draft of a test suite faster than you could write the boilerplate: it knows
`unittest`, it'll cover the obvious cases, set up fixtures, and name the tests sensibly.

The economics change. The thing that was too tedious to do consistently is now cheap. The remaining
skill isn't *writing* tests, it's *directing* the AI to write the right ones, and knowing how to
tell a good test from a worthless one. Which brings us to the trap.

### The trap: tests that assert current behavior instead of intent

Ask an AI to "write tests for this function" with no further direction and you will often get tests
that are subtly worthless, in a specific way: **they assert whatever the code currently does, rather
than what the code is supposed to do.** The model reads the implementation, sees that it returns `5`
for some input, and writes `assertEqual(result, 5)`. The test passes. It will keep passing. It is a
tautology; it tests that the code does what the code does.

This is catastrophic in the AI era, because if the code the AI wrote is *wrong*, an AI test that was
written *from that same code* will faithfully assert the wrong answer and lock the bug in. You now
have a green checkmark certifying a bug. That's worse than no test: it's false confidence with a
paper trail.

The fix is a discipline, and it's the whole craft of testing in one sentence:

> **A test must encode intent (what the code is *for*) derived from the spec, not from the
> implementation.**

Concretely, that changes how you direct the AI. Don't say "write tests for `pending_count`." Say
*what it should do* and let the test be written against that:

- Weak (invites tautology): *"Write unit tests for the `pending_count` method."*
- Strong (encodes intent): *"`pending_count` should return the number of tasks that are still
  pending, not completed. Write `unittest` tests for that behavior: empty list returns 0; tasks
  added but none done returns the full count; after completing some, returns only the still-pending
  count; all done returns 0. Derive the expected values from that description, not from the current
  implementation."*

The second prompt does something the first can't: it describes a case (*after completing some*)
where a buggy implementation and a correct one give *different* answers. A tautological test only
ever exercises the case where they happen to agree. **The intent test is the one that can fail, and a
test that can't fail isn't testing anything.** Your job when reviewing AI-written tests is to ask of
each one: *if the code were wrong, would this test notice?* If the answer is no, the test is worthless.

This is also why you write the test against the *spec*, even when the AI wrote both the code and the
tests. If you let the same source produce both, they agree by construction and verify nothing. The
intent has to come from you.

### Tests are the content the next module automates

One more framing before the lab. A test file just sitting in your repo is useful when you remember to
run it; like the manual eyeball check, you eventually won't. The full payoff comes in
**Module 14**, where Continuous Integration runs this exact `python3 -m unittest` command
automatically on every push, so a regression can't reach `main` without something going red first.

That's why this module comes immediately before CI: **tests are the content CI runs.** You can't
automate a check you don't have. So the deliverable here isn't just "I understand testing"; it's a
real, committed `test_tasks.py` that the next module will pick up and run for you forever. Leave this
module with that file and Module 14 is half-built already.

---

## The AI angle

Generic testing courses teach assertions and frameworks. What's specific to AI-assisted work is the
*two-sided* relationship between AI and tests, and you have to hold both sides at once:

- **AI is the reason you need tests more.** It produces plausible-looking code at high volume, and
  plausibility is exactly the signal a human review leans on and exactly the signal AI defeats. Tests
  verify behavior, which is the thing the surface no longer tells you.
- **AI is also what makes a real test suite finally affordable.** The boilerplate that used to make
  testing a discipline you skipped is now nearly free to generate. The barrier moves from "writing
  tests is tedious" to "directing and judging tests is a skill," a much better place for the barrier
  to be.
- **The danger is letting the same AI close the loop on itself.** AI writes the code, then AI writes
  tests *from that code*, the tests pass, and you've certified a bug. The discipline that breaks the
  loop is human-supplied intent: you state what the code is *for*, and the test is written against
  that, so the test can disagree with the code. A test that can't disagree with the code is theater.

The reflex to build: when an AI hands you code *and* tests, review the tests first, and review them by
asking "would this fail if the code were wrong?", not "do these pass?" Passing is the easy part.
Passing for the right reason is the skill.

---

## Hands-on lab


> **Starting point (this lab is skip-friendly).** You do not need to have done the earlier labs.
> To begin from a clean, known state, copy this module's snapshot into a fresh `tasks-app` and
> make the first commit:
>
> ```bash
> mkdir -p ~/ai-workflow-course/tasks-app
> cp -r ~/ai-workflow-course/modules/13-testing-in-the-ai-era/lab/start/. ~/ai-workflow-course/tasks-app/
> cd ~/ai-workflow-course/tasks-app && git init -b main && git add -A && git commit -m "start: module 13"
> ```
>
> Already carrying your `tasks-app` from earlier modules? Keep using it and ignore this box.
**Lab language:** Python (standard-library `unittest`), with a couple of shell commands to run the
suite. Nothing to install.

In this lab you'll direct an AI to write meaningful tests for the `tasks-app`, run them, and use them
to catch a bug that has been sitting in the code looking perfectly fine.

**You'll need:**

- Python 3.10+ and a terminal.
- The lab copy of the app at
  `~/ai-workflow-course/modules/13-testing-in-the-ai-era/lab/tasks-app/` (`tasks.py`, `cli.py`).
  It's the Module 1/2 app plus a `count` command, and a planted bug. Have Claude Code copy it to a
  working directory (`~/ai-workflow-course/work/tasks-app/`) and confirm both files landed; or use
  your own `tasks-app` if it has a `count` command (see note in step 6).
- Claude Code running in your editor or terminal (Module 4), with file access to the working copy.
  Sub your own agent if you prefer (`claude --version  # sub your own agent`).
- Git initialized in your working copy (Module 2), so the agent can commit the test file at the end.

### Part A: Write and run a first test by hand

Do this once yourself so the tool isn't magic. From inside your working copy of the app:

1. Create `test_tasks.py` next to `tasks.py` with one real test:

   ```python
   import unittest
   from tasks import TaskList

   class TestTaskList(unittest.TestCase):
       def test_add_then_complete_marks_done(self):
           tl = TaskList()
           tl.add("a")
           tl.complete(0)
           self.assertTrue(tl.tasks[0].done)

   if __name__ == "__main__":
       unittest.main()
   ```

2. Run it:

   ```bash
   python3 -m unittest -v
   ```

   You should see one test, and `OK`. That's the entire mechanism. Everything else is more of these.

### Part B: Direct the AI to write tests that encode intent

3. Now hand Claude Code the job, but direct it properly. Point it at `tasks.py` with a prompt that
   supplies **intent**, not just "write tests." Something like:

   > "Look at `tasks.py`. Write a `unittest` test suite in `test_tasks.py` covering `add`,
   > `complete`, `pending`, and `pending_count`. For `pending_count`, the intended behavior is: it
   > returns the number of tasks that are *not done*. Cover these cases and derive the expected
   > numbers from that description, not from the current code: (a) empty list → 0; (b) two added,
   > none completed → 2; (c) two added, one completed → 1; (d) one added then completed → 0."

   Note what you did: you described a case (*one completed*) where a correct `pending_count` and a
   wrong one give different answers. That's the case that can catch a bug.

4. Claude Code writes `test_tasks.py` next to `tasks.py`. **Review it before running it**; this is
   the Module 10 skill applied to tests. For each test ask: *if `pending_count` were wrong, would this
   one notice?* A test that only ever adds tasks (never completes one) would pass no matter what
   `pending_count` returns, because with nothing done, total and pending are the same number. That
   test is a tautology; the "one completed" test is the one with teeth.

### Part C: Catch the bug

5. Run the suite:

   ```bash
   python3 -m unittest -v
   ```

   At least one `pending_count` test should **FAIL**, with something like
   `AssertionError: 2 != 1`. Read it: after completing one of two tasks, the intended answer is 1,
   but the code returned 2. Open `tasks.py` and look at `pending_count`:

   ```python
   def pending_count(self) -> int:
       return len(self.tasks)        # counts ALL tasks, not just pending ones
   ```

   There's the bug. It "worked" in every quick manual check because nobody ran `count` *after*
   completing a task, the one case where total and pending diverge. It passes a human skim. It does
   not pass a test that encodes intent.

6. **Fix the code, not the test.** The test is correct; the code is wrong. Change it to honor the
   intent (and reuse the method that already does it right):

   ```python
   def pending_count(self) -> int:
       return len(self.pending())
   ```

   Re-run `python3 -m unittest -v`; green. Confirm the app agrees:
   `python3 cli.py add a && python3 cli.py add b && python3 cli.py done 0 && python3 cli.py count`
   should report **1 task(s) pending**.

   > Using your own app from earlier modules instead? If your `count` command was already correct,
   > don't skip the lesson; *plant* the bug to feel it: temporarily change your pending-count logic
   > to `len(self.tasks)`, confirm an intent-encoding test goes red, then fix it. The muscle is
   > "write the test that would have caught this," and you build it by watching it catch something.

7. Commit the test file. This is the artifact Module 14 will automate. Tell Claude Code to stage
   `tasks.py` and `test_tasks.py` and commit them with a message describing the test addition and the
   `pending_count` fix. Before it commits, check the staged diff and the message yourself; you're
   verifying it staged exactly those two files and landed a commit equivalent to:

   ```text
   Add tests for TaskList; fix pending_count to count only pending
   ```

A reference suite (including the tautology-vs-intent contrast spelled out) is in
`~/ai-workflow-course/modules/13-testing-in-the-ai-era/lab/solution/reference_test_tasks.py`. Compare
against it *after* you've written your own.

---

## Where it breaks

The honest limits, because a green suite invites overconfidence:

- **Passing tests prove presence, not absence.** A green run means the behaviors you *wrote tests
  for* work. It says nothing about the behaviors you didn't think to test, which, with AI-written
  code, includes the edge cases the model also didn't think about. Tests narrow risk; they don't
  eliminate it. "All tests pass" is not "the code is correct."
- **Tests written from the implementation are worse than no tests.** A suite that locks in current
  behavior gives you false confidence with a paper trail, the worst combination. The whole module
  hinges on intent coming from *you*, not from the code the AI just wrote. If you ever let the same
  AI write both code and tests with no spec from you, assume the tests verify nothing until you've
  checked each one against intent.
- **Coverage is a trap metric.** It's easy to ask the AI for "100% coverage" and get a suite that
  executes every line while asserting almost nothing meaningful. A line being *run* by a test is not
  the same as its behavior being *checked*. Chase "would this fail if the code were wrong?", never a
  coverage percentage.
- **Not everything is a unit test.** The `tasks-app` is pure logic, which is the easy case. Code that
  hits a database, a network, the filesystem, or an external service needs more setup (fixtures,
  fakes, integration tests) than this module covers. The thinking transfers; the mechanics get
  heavier, and that's out of scope here.
- **A test suite is code too, and the AI wrote it.** Tests can have bugs, including the silent kind
  that always pass. Reviewing tests is as real a task as reviewing code, which is exactly why Part B
  has you read them before trusting them.

---

## Check for understanding

**You're done when:**

- You can run `python3 -m unittest -v` in your `tasks-app` and see your own tests pass.
- You watched an intent-encoding test **fail**, traced it to the real `pending_count` bug, fixed the
  *code*, and watched it pass.
- You can articulate, in your own words, the difference between a test that asserts current behavior
  (a tautology that can't fail) and one that encodes intent (one that can), and why the second is
  the only kind worth having for AI-written code.
- You have a committed `test_tasks.py` in the repo, ready for Module 14 to run automatically on every
  push.

If a test that can't possibly fail now reads to you as obviously useless, you've got the core idea,
and you're ready for **Module 14**, where these tests stop depending on you remembering to run them.
