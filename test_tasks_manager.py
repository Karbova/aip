import pytest
from tasks_manager.models import TaskManager


@pytest.fixture
def task_manager():
    return TaskManager()


def test_add_task(task_manager):
    task = task_manager.add_task("Test Task", "Description", "Alice", "2024-12-31")
    assert task["id"] == 1
    assert task["title"] == "Test Task"
    assert task["status"] == "Не начата"
    assert len(task_manager.tasks) == 1


def test_add_task_missing_fields(task_manager):
    with pytest.raises(ValueError, match="Все поля задачи должны быть заполнены"):
        task_manager.add_task("Test Task", "", "Alice", "2024-12-31")


def test_mark_completed(task_manager):
    task_manager.add_task("Test Task", "Description", "Alice", "2024-12-31")
    task_manager.mark_completed(1)
    assert task_manager.tasks[0]["status"] == "Выполнена"


def test_mark_in_progress(task_manager):
    task_manager.add_task("Test Task", "Description", "Alice", "2024-12-31")
    task_manager.mark_in_progress(1)
    assert task_manager.tasks[0]["status"] == "В процессе"


def test_delete_task(task_manager):
    task_manager.add_task("Test Task", "Description", "Alice", "2024-12-31")
    task_manager.delete_task(1)
    assert len(task_manager.tasks) == 0


def test_get_task_by_id(task_manager):
    task_manager.add_task("Test Task", "Description", "Alice", "2024-12-31")
    task = task_manager.get_task_by_id(1)
    assert task["title"] == "Test Task"


def test_get_task_by_id_not_found(task_manager):
    with pytest.raises(ValueError, match="Задача с ID 999 не найдена"):
        task_manager.get_task_by_id(999)


def test_save_to_json(task_manager, tmp_path):
    task_manager.add_task("Test Task", "Description", "Alice", "2024-12-31")
    filename = tmp_path / "tasks.json"
    task_manager.save_to_json(filename)
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()
    assert '"title": "Test Task"' in data


def test_load_from_json(task_manager, tmp_path):
    filename = tmp_path / "tasks.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(
            '[{"id": 1, "title": "Test Task", "description": "Description", "assignee": "Alice", "deadline": "2024-12-31", "status": "Не начата"}]'
        )
    task_manager.load_from_json(filename)
    assert len(task_manager.tasks) == 1
    assert task_manager.tasks[0]["title"] == "Test Task"
