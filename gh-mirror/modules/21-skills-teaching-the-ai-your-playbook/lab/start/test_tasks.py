"""Test suite for the tasks-app. Run from this folder with:

    python3 -m unittest

Your "add a command" skill should ADD a test here for every new command. The point is to assert
intended behavior, not just that nothing crashed.
"""

import unittest

from tasks import TaskList


class TestTaskBasics(unittest.TestCase):
    def test_add_appends_a_task(self):
        tl = TaskList()
        tl.add("write the skill")
        self.assertEqual(len(tl.tasks), 1)
        self.assertEqual(tl.tasks[0].title, "write the skill")
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

    def test_pending_count_ignores_done(self):
        tl = TaskList()
        tl.add("a")
        tl.add("b")
        tl.complete(0)
        self.assertEqual(tl.pending_count(), 1)


if __name__ == "__main__":
    unittest.main()
