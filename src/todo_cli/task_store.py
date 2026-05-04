from dataclasses import dataclass, field


@dataclass
class Task:
    id: int
    title: str
    done: bool = False


@dataclass
class TaskStore:
    _tasks: list[Task] = field(default_factory=list)
    _next_id: int = 1

    def add(self, title: str) -> Task:
        task = Task(id=self._next_id, title=title)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def list(self) -> list[Task]:
        return list(self._tasks)

    def complete(self, task_id: int) -> None:
        for task in self._tasks:
            if task.id == task_id:
                task.done = True
                return
        raise KeyError(task_id)
