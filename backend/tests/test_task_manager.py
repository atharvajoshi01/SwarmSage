"""
Tests for app.models.task module.
"""

import threading
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from app.models.task import TaskStatus, Task, TaskManager


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.PROCESSING.value == "processing"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"

    def test_string_enum(self):
        assert str(TaskStatus.PENDING) == "TaskStatus.PENDING"
        assert TaskStatus.PENDING == "pending"


class TestTask:
    """Tests for the Task dataclass."""

    def test_to_dict(self):
        now = datetime.now()
        task = Task(
            task_id="test-1",
            task_type="graph_build",
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            progress=50,
            message="In progress",
        )
        d = task.to_dict()
        assert d["task_id"] == "test-1"
        assert d["task_type"] == "graph_build"
        assert d["status"] == "pending"
        assert d["progress"] == 50
        assert d["message"] == "In progress"
        assert d["result"] is None
        assert d["error"] is None

    def test_to_dict_with_result(self):
        now = datetime.now()
        task = Task(
            task_id="test-2",
            task_type="report",
            status=TaskStatus.COMPLETED,
            created_at=now,
            updated_at=now,
            result={"report_id": "r1"},
        )
        d = task.to_dict()
        assert d["result"] == {"report_id": "r1"}
        assert d["status"] == "completed"


class TestTaskManager:
    """Tests for the TaskManager singleton."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset TaskManager singleton between tests."""
        TaskManager._instance = None
        yield
        TaskManager._instance = None

    def test_singleton_pattern(self):
        tm1 = TaskManager()
        tm2 = TaskManager()
        assert tm1 is tm2

    def test_create_task_returns_unique_ids(self):
        tm = TaskManager()
        id1 = tm.create_task("type_a")
        id2 = tm.create_task("type_a")
        assert id1 != id2

    def test_get_task(self):
        tm = TaskManager()
        task_id = tm.create_task("test_type", metadata={"key": "value"})
        task = tm.get_task(task_id)
        assert task is not None
        assert task.task_id == task_id
        assert task.task_type == "test_type"
        assert task.status == TaskStatus.PENDING
        assert task.metadata == {"key": "value"}

    def test_get_task_nonexistent(self):
        tm = TaskManager()
        assert tm.get_task("nonexistent") is None

    def test_update_task(self):
        tm = TaskManager()
        task_id = tm.create_task("test")
        tm.update_task(task_id, status=TaskStatus.PROCESSING, progress=50, message="half done")
        task = tm.get_task(task_id)
        assert task.status == TaskStatus.PROCESSING
        assert task.progress == 50
        assert task.message == "half done"

    def test_complete_task(self):
        tm = TaskManager()
        task_id = tm.create_task("test")
        tm.complete_task(task_id, result={"data": "done"})
        task = tm.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.progress == 100
        assert task.result == {"data": "done"}

    def test_fail_task(self):
        tm = TaskManager()
        task_id = tm.create_task("test")
        tm.fail_task(task_id, error="Something broke")
        task = tm.get_task(task_id)
        assert task.status == TaskStatus.FAILED
        assert task.error == "Something broke"

    def test_list_tasks_all(self):
        tm = TaskManager()
        tm.create_task("type_a")
        tm.create_task("type_b")
        tasks = tm.list_tasks()
        assert len(tasks) == 2

    def test_list_tasks_filtered(self):
        tm = TaskManager()
        tm.create_task("type_a")
        tm.create_task("type_b")
        tm.create_task("type_a")
        tasks = tm.list_tasks(task_type="type_a")
        assert len(tasks) == 2
        for t in tasks:
            assert t["task_type"] == "type_a"

    def test_cleanup_old_tasks(self):
        tm = TaskManager()
        task_id = tm.create_task("test")
        tm.complete_task(task_id, result={})

        # Manually backdate the task
        task = tm.get_task(task_id)
        task.created_at = datetime.now() - timedelta(hours=48)

        tm.cleanup_old_tasks(max_age_hours=24)
        assert tm.get_task(task_id) is None

    def test_cleanup_preserves_recent_tasks(self):
        tm = TaskManager()
        task_id = tm.create_task("test")
        tm.complete_task(task_id, result={})
        tm.cleanup_old_tasks(max_age_hours=24)
        assert tm.get_task(task_id) is not None

    def test_thread_safety(self):
        tm = TaskManager()
        ids = []
        lock = threading.Lock()

        def create_tasks():
            for _ in range(10):
                tid = tm.create_task("concurrent")
                with lock:
                    ids.append(tid)

        threads = [threading.Thread(target=create_tasks) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(ids) == 50
        assert len(set(ids)) == 50  # All unique
