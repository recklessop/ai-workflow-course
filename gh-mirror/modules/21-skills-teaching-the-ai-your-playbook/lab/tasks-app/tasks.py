"""Core task logic for the demo app.

The same running example from Module 1 onward, carried forward with the `pending_count()` helper
that backs the `count` command. This is the codebase your "add a command" skill operates on.
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
        return len([t for t in self.tasks if not t.done])

    def render(self) -> str:
        if not self.tasks:
            return "(no tasks yet)"
        lines = []
        for i, task in enumerate(self.tasks):
            box = "[x]" if task.done else "[ ]"
            lines.append(f"{i}. {box} {task.title}")
        return "\n".join(lines)
