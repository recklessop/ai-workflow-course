"""Candidate output: the CURRENT model/prompt.

This is what your agent produced for the task "implement pending_count() so it
returns the number of tasks that are not done." It's correct. Replace this whole
directory with your own agent's real output when you run the lab for real.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    done: bool = False


@dataclass
class TaskList:
    tasks: list[Task] = field(default_factory=list)

    def add(self, title: str) -> Task:
        task = Task(title=title)
        self.tasks.append(task)
        return task

    def complete(self, index: int) -> None:
        self.tasks[index].done = True

    def pending(self) -> list[Task]:
        return [t for t in self.tasks if not t.done]

    def pending_count(self) -> int:
        # Correct: count only the tasks that aren't done.
        return len(self.pending())

    def render(self) -> str:
        if not self.tasks:
            return "(no tasks yet)"
        lines = []
        for i, task in enumerate(self.tasks):
            box = "[x]" if task.done else "[ ]"
            lines.append(f"{i}. {box} {task.title}")
        return "\n".join(lines)
