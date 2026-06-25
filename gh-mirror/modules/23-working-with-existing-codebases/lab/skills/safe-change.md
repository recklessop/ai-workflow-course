# Skill: Safe scoped change

A safe-change playbook (a Module 21 skill) for modifying a codebase you don't fully understand.
Use it only **after** `map-this-repo` has produced an architecture summary. The whole bet of this
skill is: small, scoped, tested, reviewable, never a sweeping rewrite.

## When to use
When making a concrete change to an unfamiliar repo.

## Rules
- **One change, one branch.** Create a branch first (Module 6). Never work on the default branch.
- **Smallest diff that solves it.** Touch the fewest files possible. If the change wants to sprawl,
  stop and re-scope; sprawl in code you don't understand is how you break things invisibly.
- **No drive-by edits.** Do not reformat, rename, or "clean up" unrelated code. Those bury the real
  change and make the diff unreviewable (Module 10).
- **Match local conventions.** Mirror the surrounding code's style, naming, and patterns, not your
  own defaults.
- **Tests are the contract.** A change isn't done until it's covered (Module 13) and the existing
  suite still passes.

## Steps
1. **State the change in one sentence** and the acceptance criterion ("done when X").
2. **Find the blast radius first:** search for every caller/usage of what you're about to touch.
   List them. If you can't enumerate them, you're not ready to change it.
3. **Install the project's dependencies, then run the existing tests before touching anything**;
   establish a green baseline. Tell two failures apart: if the suite errors with missing imports,
   "no module named …", or "no tests ran," that's an **unconfigured environment**, not a baseline.
   Finish the documented install (and pick a different repo if it still won't go green on a clean
   clone). A genuine **pre-existing failure** (install succeeded, but a real test fails) is the other
   case: note it so it doesn't get blamed on you, and don't build on top of it.
4. **Make the minimal edit.** Keep it to the files identified in step 2.
5. **Add or extend a test** that fails without your change and passes with it.
6. **Run the full suite.** All green, including the baseline tests.
7. **Self-review the diff** as if reviewing someone else's PR (Module 10): is every changed line
   necessary and explained? Revert anything that isn't.
8. **Write the PR description:** what changed, why, blast radius, how it was tested, what you did
   NOT touch and why.

## Stop conditions (escalate to a human instead of pushing on)
- The change requires touching more than ~3 files or a "core" file from the architecture summary.
- You can't enumerate the callers of what you're changing.
- A test you don't understand starts failing.
- The fix needs a design decision the existing code doesn't settle.
