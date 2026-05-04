import pytest

from todo_cli.cli import run
from todo_cli.task_store import TaskStore


def test_add_command_prints_added_task(capsys):
    store = TaskStore()
    exit_code = run(["add", "買い物に行く"], store=store)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "1" in captured.out
    assert "買い物に行く" in captured.out
    assert store.list()[0].title == "買い物に行く"


def test_list_command_shows_tasks(capsys):
    store = TaskStore()
    store.add("掃除")
    store.add("洗濯")
    exit_code = run(["list"], store=store)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "掃除" in captured.out
    assert "洗濯" in captured.out


def test_list_command_marks_done_tasks(capsys):
    store = TaskStore()
    store.add("やること")
    store.complete(1)
    run(["list"], store=store)
    captured = capsys.readouterr()
    assert "[x]" in captured.out


def test_list_command_marks_pending_tasks(capsys):
    store = TaskStore()
    store.add("やること")
    run(["list"], store=store)
    captured = capsys.readouterr()
    assert "[ ]" in captured.out


def test_done_command_marks_task_complete(capsys):
    store = TaskStore()
    store.add("買い物")
    exit_code = run(["done", "1"], store=store)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert store.list()[0].done is True
    assert "1" in captured.out


def test_done_command_unknown_id_returns_error(capsys):
    store = TaskStore()
    exit_code = run(["done", "999"], store=store)
    captured = capsys.readouterr()
    assert exit_code != 0
    assert "999" in captured.err or "999" in captured.out


def test_no_command_shows_help(capsys):
    exit_code = run([], store=TaskStore())
    captured = capsys.readouterr()
    assert exit_code != 0
    assert "usage" in (captured.out + captured.err).lower()


def test_add_requires_title():
    store = TaskStore()
    with pytest.raises(SystemExit):
        run(["add"], store=store)
