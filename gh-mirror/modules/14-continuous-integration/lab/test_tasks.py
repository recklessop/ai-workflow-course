"""Tests for the tasks-app core logic: the kind of suite Module 13 has you write.

Reproduced here so this module's lab is self-contained: if you already wrote tests in Module 13,
use those instead. Standard-library `unittest`, exactly like Module 13, nothing to install.
Run locally with `python3 -m unittest` from the project folder. CI runs exactly this.
"""

import unittest

from tasks import TaskList


class TestTaskList(unittest.TestCase):
    def test_add_appends_a_task(self):
        tl = TaskList()
        tl.add("write the CI lesson")
        self.assertEqual(len(tl.tasks), 1)
        self.assertEqual(tl.tasks[0].title, "write the CI lesson")
        self.assertFalse(tl.tasks[0].done)

    def test_complete_marks_a_task_done(self):
        tl = TaskList()
        tl.add("ship it")
        tl.complete(0)
        self.assertTrue(tl.tasks[0].done)

    def test_pending_excludes_completed_tasks(self):
        tl = TaskList()
        tl.add("a")
        tl.add("b")
        tl.complete(0)
        pending = tl.pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].title, "b")

    def test_render_is_friendly_when_empty(self):
        self.assertEqual(TaskList().render(), "(no tasks yet)")


if __name__ == "__main__":
    unittest.main()
