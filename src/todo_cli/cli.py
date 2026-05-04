import argparse
import sys
from collections.abc import Sequence

from todo_cli.task_store import TaskStore


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="Tiny TODO CLI.")
    sub = parser.add_subparsers(dest="command")

    add = sub.add_parser("add", help="Add a new task")
    add.add_argument("title", help="Task title")

    sub.add_parser("list", help="List all tasks")

    done = sub.add_parser("done", help="Mark a task as done")
    done.add_argument("task_id", type=int, help="Task ID")

    return parser


def run(argv: Sequence[str], store: TaskStore) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        task = store.add(args.title)
        print(f"added: {task.id} {task.title}")
        return 0

    if args.command == "list":
        for task in store.list():
            mark = "[x]" if task.done else "[ ]"
            print(f"{mark} {task.id} {task.title}")
        return 0

    if args.command == "done":
        try:
            store.complete(args.task_id)
        except KeyError:
            print(f"error: task {args.task_id} not found", file=sys.stderr)
            return 1
        print(f"done: {args.task_id}")
        return 0

    parser.print_help(sys.stderr)
    return 2


def main() -> int:
    return run(sys.argv[1:], TaskStore())
