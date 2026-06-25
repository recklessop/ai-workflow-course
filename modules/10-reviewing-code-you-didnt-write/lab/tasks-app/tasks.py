"""Core task logic for the demo app.

Same running example as Modules 1 and 2, with one addition: `complete` now validates the
index and raises a clear error for a bad one. That explicit edge-case handling is here on
purpose; it's the kind of thing an AI "refactor" likes to quietly remove. This is the
known-good base you'll review an AI change against in Module 10.
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
        if not 0 <= index < len(self.tasks):
            raise IndexError(f"no task at index {index}")
        self.tasks[index].done = True

    def pending(self) -> list[Task]:
        return [t for t in self.tasks if not t.done]

    def render(self) -> str:
        if not self.tasks:
            return "(no tasks yet)"
        lines = []
        for i, task in enumerate(self.tasks):
            box = "[x]" if task.done else "[ ]"
            lines.append(f"{i}. {box} {task.title}")
        return "\n".join(lines)
