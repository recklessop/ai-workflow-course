"""Core task logic for the demo app.

Deliberately small and deliberately split across two files (this and cli.py) so that the
copy-paste workflow has more than one place to go wrong. This is the running example used in
Modules 1 and 2.
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

    def render(self) -> str:
        if not self.tasks:
            return "(no tasks yet)"
        lines = []
        for i, task in enumerate(self.tasks):
            box = "[x]" if task.done else "[ ]"
            lines.append(f"{i}. {box} {task.title}")
        return "\n".join(lines)
