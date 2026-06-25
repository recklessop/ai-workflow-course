# Reviewing an AI-generated diff: working checklist

Keep this open while you read a diff the AI produced. The point is not to re-read the whole
file; it's to interrogate **the change** against the prompt you gave. Work top to bottom.

## 0. Frame the review

- [ ] **What did I actually ask for?** Write the request in one sentence. Every changed line
      should trace back to it.
- [ ] **Read the diff, not the summary.** Ignore the AI's account of what it did; the diff is the
      only ground truth. (`git diff main..<branch>`)

## 1. Scope: did it change only what was asked?

- [ ] Every hunk maps to the request. Anything outside it is **scope creep** until proven
      otherwise.
- [ ] No unrelated files touched (formatting churn, import reshuffles, version bumps).
- [ ] No "while I was here" refactors of code the request never mentioned.

## 2. Deletions: what did it take away?

- [ ] Read every `-` line. Deletions are higher-risk than additions and skim right past you.
- [ ] **Edge-case handling still there?** Bounds checks, `None`/empty guards, `try/except`,
      validation, error returns; confirm none were dropped or weakened.
- [ ] An error that used to be raised/logged isn't now silently swallowed (`except: pass`).

## 3. Plausibility: does it only *look* right?

- [ ] **Invented APIs.** Every function, method, kwarg, attribute, import, env var, CLI flag,
      config key, and endpoint actually exists. Confidence is not evidence; verify the
      unfamiliar ones against real docs/source.
- [ ] **Invented behavior.** It isn't relying on a flag/option that doesn't do what the name
      suggests (e.g. assuming `list.pop` takes a default like `dict.pop`).
- [ ] **Off-by-one / boundary logic.** Indexing, ranges, slicing, loop bounds, 0- vs 1-based.
- [ ] **Inverted or weakened conditions.** `if not x` vs `if x`, `<` vs `<=`, `and` vs `or`,
      a filter quietly dropped from a comprehension.

## 4. Behavior change: would the happy path hide it?

- [ ] Does any existing command/function behave differently now? Trace one real call through.
- [ ] **Run the failure case, not the success case.** The trap usually survives the happy
      path. Feed it bad input, an empty list, a missing file, a duplicate.
- [ ] Return values / exit codes unchanged where callers depend on them.

## 5. Decide

- [ ] I can explain, in my own words, what every hunk does and why it's correct.
- [ ] If I can't, I **request changes**; the burden of proof is on the diff, not on me.

> Rule of thumb: a diff is guilty until proven correct. "It runs" is the weakest possible
> evidence; "I read every `-` line and ran the failure case" is the bar.
