"""Candidate output: a SWAPPED model/prompt.

Same task, different model (or a tweaked prompt). This output "looks right" and
passes a casual manual check; adding three tasks and calling count returns 3.
But pending_count() returns the total number of tasks, not the number of
*pending* ones, so it's wrong the moment anything is marked done.

Nobody would notice this by skimming. The eval set notices it instantly. That's
the regression eval catching an unsafe swap, exactly the scenario this module
exists for. Replace this with your own swapped-model output when you run it for
real; you may get lucky and have it pass, or you may catch a regression like
this one.
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
        # WRONG, but plausibly so: counts every task, not just pending ones.
        return len(self.tasks)

    def render(self) -> str:
        if not self.tasks:
            return "(no tasks yet)"
        lines = []
        for i, task in enumerate(self.tasks):
            box = "[x]" if task.done else "[ ]"
            lines.append(f"{i}. {box} {task.title}")
        return "\n".join(lines)
