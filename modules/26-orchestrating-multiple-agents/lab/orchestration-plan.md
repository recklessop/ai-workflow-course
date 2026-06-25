# Coordination plan: Module 26 lab

This is the artifact orchestration runs on. With one agent, the plan lived in your head. With a
fleet, it has to live here, because your head doesn't scale and it forgets (Module 2).

Fill the **Status** column as you go, and answer the questions at the bottom. The plan is the
deliverable, not the code.

---

## The fleet

| Issue | Branch | Worktree | Files owned | Depends on | Status |
|-------|--------|----------|-------------|------------|--------|
| #42 count | `feature/42-count` | `tasks-app-42-count` | `cli.py` (dispatch + new fn) | none | queued |
| #43 docs  | `feature/43-docs`  | `tasks-app-43-docs`  | `README.md`, `CHANGELOG.md` | none | queued |
| #44 clear | `feature/44-clear` | `tasks-app-44-clear` | `cli.py` (dispatch + new fn) | none | queued |

`main` is reserved as the integration point. No agent works in the main worktree.

---

## Part A: Predict the conflicts BEFORE you launch

Read the "Files owned" column. Which pairs are genuinely parallel, and which will collide at merge?
Write your prediction here, then watch it come true in Part C.

- Genuinely parallel (disjoint files, no shared interface): _______________________
- Will collide at merge (and on which file/line): _______________________________
- If you wanted to avoid the collision, what would you change? (serialize one? scope it to a
  different file?) _____________________________________________________________

---

## Part D: Score the orchestration honestly

- **Did parallel beat sequential?** Agent wall-clock (overlapping) + your serial review time +
  conflict resolution, vs. "I'd have done these three myself, in order."
  Answer: ______________________________________________________________________

- **Which split was worth it and which wasn't?**
  Answer: ______________________________________________________________________

- **Where was the bottleneck?** (Almost certainly your review queue, not the agents. Name it.)
  Answer: ______________________________________________________________________
