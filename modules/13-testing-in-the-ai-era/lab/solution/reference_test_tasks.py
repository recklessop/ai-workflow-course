"""Reference test suite for the Module 13 lab. Peek only after you've tried it yourself.

Named `reference_test_tasks.py` (not `test_*.py`) on purpose, so `python3 -m unittest discover`
does NOT pick it up automatically. To run it, copy it next to your working `tasks.py` (e.g.
`~/ai-workflow-course/work/tasks-app/`) and run, from that directory:

    python3 -m unittest reference_test_tasks

It assumes `tasks.py` is importable, which is why you run it from the tasks-app directory.

The point of this file is to show the difference between a test that asserts CURRENT BEHAVIOR
(a tautology that passes against the bug) and a test that encodes INTENT (and fails until the
bug is fixed).
"""

import unittest

from tasks import TaskList


class TestTaskBasics(unittest.TestCase):
    def test_add_appends_a_task(self):
        tl = TaskList()
        tl.add("write the tests")
        self.assertEqual(len(tl.tasks), 1)
        self.assertEqual(tl.tasks[0].title, "write the tests")
        self.assertFalse(tl.tasks[0].done)

    def test_complete_marks_done(self):
        tl = TaskList()
        tl.add("a")
        tl.complete(0)
        self.assertTrue(tl.tasks[0].done)

    def test_pending_excludes_completed(self):
        tl = TaskList()
        tl.add("a")
        tl.add("b")
        tl.complete(0)
        self.assertEqual([t.title for t in tl.pending()], ["b"])


class TestPendingCount(unittest.TestCase):
    def test_count_with_nothing_done_is_a_tautology(self):
        # This passes even with the bug, because when nothing is completed
        # "total" and "pending" are the same number. It proves almost nothing.
        tl = TaskList()
        tl.add("a")
        tl.add("b")
        self.assertEqual(tl.pending_count(), 2)

    def test_count_reflects_intent_after_completing_one(self):
        # This encodes what `count` is FOR: how many tasks are still pending.
        # It FAILS against the planted bug (pending_count returns len(self.tasks)),
        # and passes once pending_count returns len(self.pending()).
        tl = TaskList()
        tl.add("a")
        tl.add("b")
        tl.complete(0)
        self.assertEqual(tl.pending_count(), 1)

    def test_count_of_all_done_is_zero(self):
        tl = TaskList()
        tl.add("a")
        tl.complete(0)
        self.assertEqual(tl.pending_count(), 0)


# The fix, for reference:
#
#     def pending_count(self) -> int:
#         return len(self.pending())


if __name__ == "__main__":
    unittest.main()
