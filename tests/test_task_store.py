from todo_cli.task_store import TaskStore


def test_new_store_is_empty():
    store = TaskStore()
    assert store.list() == []


def test_add_task_returns_task_with_id_and_title():
    store = TaskStore()
    task = store.add("買い物に行く")
    assert task.id == 1
    assert task.title == "買い物に行く"
    assert task.done is False


def test_add_assigns_incrementing_ids():
    store = TaskStore()
    a = store.add("A")
    b = store.add("B")
    assert (a.id, b.id) == (1, 2)


def test_complete_marks_task_done():
    store = TaskStore()
    task = store.add("掃除")
    store.complete(task.id)
    assert store.list()[0].done is True


def test_complete_unknown_id_raises():
    store = TaskStore()
    try:
        store.complete(999)
    except KeyError:
        return
    raise AssertionError("KeyError expected")
