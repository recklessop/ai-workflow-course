"""The eval set for the tasks-app `pending_count` agent task.

An *eval set* is a list of CASES. Each case is three things:

  - a name (so the scorecard is readable),
  - an input (here: the state a TaskList is in), and
  - the expected result (here: how many tasks should count as pending).

The grading lives in run_eval.py; this file is just data. Keeping the cases
separate from any model, prompt, or runner is the whole point; the same eval
set judges *any* candidate you point it at, which is what makes it useful when
you swap the model out from under it.

The task we're evaluating: an agent was asked to implement
`TaskList.pending_count()` so it returns the number of tasks that are NOT done.
That sounds trivial. The discriminating cases below are the ones a
"looks-right" implementation quietly fails.
"""

# Each case: (name, [(title, done), ...], expected_pending_count)
CASES = [
    ("empty list has zero pending", [], 0),
    ("one open task counts as one", [("write tests", False)], 1),
    (
        "three open tasks count as three",
        [("a", False), ("b", False), ("c", False)],
        3,
    ),
    # The discriminating case. A candidate that returns len(tasks) passes
    # everything above and fails right here. This is the eval earning its keep.
    (
        "completed tasks are NOT pending",
        [("done thing", True), ("open thing", False), ("also done", True)],
        1,
    ),
    ("all done means zero pending", [("x", True), ("y", True)], 0),
]
