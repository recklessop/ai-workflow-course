"""Core task logic for the demo app.

Same running example from Modules 1 and 2, carried forward. It has grown one feature since then:
a `pending_count()` helper that the AI added to back a `count` command. The feature "works" in
the obvious case, which is exactly the kind of code this module teaches you to verify properly.
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
        # Added by the AI to support `cli.py count`. Looks right, ran fine in a quick check.
        return len(self.tasks)

    def render(self) -> str:
        if not self.tasks:
            return "(no tasks yet)"
        lines = []
        for i, task in enumerate(self.tasks):
            box = "[x]" if task.done else "[ ]"
            lines.append(f"{i}. {box} {task.title}")
        return "\n".join(lines)
