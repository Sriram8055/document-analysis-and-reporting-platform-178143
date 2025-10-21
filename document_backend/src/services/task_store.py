"""
Thread-safe in-memory task store for tracking document processing tasks.

This module provides:
- TaskStatus enum for lifecycle tracking
- Task dataclass with fields covering progress, messages, files, outputs, timestamps
- In-memory store with thread-safety
- CRUD helpers to create, get, update, list tasks, append messages
- Utilities to safely set progress and status

Designed to be import-safe for use by FastAPI routes and background workers.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any


class TaskStatus(str, Enum):
    """Lifecycle status for a processing task."""
    QUEUED = "queued"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    MAPPING = "mapping"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Holds the state and metadata for a single processing task."""
    id: str
    status: TaskStatus = TaskStatus.QUEUED
    progress: int = 0  # 0..100
    messages: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    excel_template_path: Optional[str] = None
    extracted_text: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    mapping: Dict[str, Any] = field(default_factory=dict)
    validation_issues: List[Dict[str, Any]] = field(default_factory=list)
    report_path: Optional[str] = None
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict representation of the task."""
        data = asdict(self)
        # Ensure Enum is converted to value
        data["status"] = self.status.value if isinstance(self.status, Enum) else self.status
        return data


class _InMemoryTaskStore:
    """
    Private, thread-safe in-memory storage for tasks.

    Uses a re-entrant lock to allow nested updates from the same thread
    while ensuring cross-thread safety for CRUD operations.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._tasks: Dict[str, Task] = {}

    def _now(self) -> float:
        return time.time()

    def _touch(self, task: Task) -> None:
        task.updated_at = self._now()

    # PUBLIC_INTERFACE
    def create_task(self, *, initial_files: Optional[List[str]] = None, excel_template_path: Optional[str] = None) -> Task:
        """Create a new task with a unique UUID and optional initial files/template."""
        with self._lock:
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                files=list(initial_files) if initial_files else [],
                excel_template_path=excel_template_path,
            )
            self._tasks[task_id] = task
            return task

    # PUBLIC_INTERFACE
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its ID or None if not found."""
        with self._lock:
            return self._tasks.get(task_id)

    # PUBLIC_INTERFACE
    def list_tasks(self) -> List[Task]:
        """Return a list of all tasks."""
        with self._lock:
            return list(self._tasks.values())

    # PUBLIC_INTERFACE
    def update_task(self, task_id: str, **fields: Any) -> Optional[Task]:
        """
        Update arbitrary fields on a task, safely.

        Returns the updated Task or None if not found.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None

            for k, v in fields.items():
                if k == "status":
                    # Allow setting by str or TaskStatus
                    if isinstance(v, str):
                        try:
                            v = TaskStatus(v)
                        except ValueError:
                            raise ValueError(f"Invalid TaskStatus value: {v}")
                if k == "progress":
                    # Enforce 0..100
                    v = max(0, min(100, int(v)))
                if hasattr(task, k):
                    setattr(task, k, v)
                else:
                    raise AttributeError(f"Task has no attribute '{k}'")
            self._touch(task)
            return task

    # PUBLIC_INTERFACE
    def append_message(self, task_id: str, message: str) -> Optional[Task]:
        """Append a message to the task's message list."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            task.messages.append(message)
            self._touch(task)
            return task

    # PUBLIC_INTERFACE
    def set_progress(self, task_id: str, progress: int) -> Optional[Task]:
        """Safely set task progress within 0..100, returns updated task or None."""
        return self.update_task(task_id, progress=max(0, min(100, int(progress))))

    # PUBLIC_INTERFACE
    def set_status(self, task_id: str, status: TaskStatus | str) -> Optional[Task]:
        """Safely set task status using enum or string."""
        if isinstance(status, str):
            status = TaskStatus(status)
        return self.update_task(task_id, status=status)


# Singleton store instance, import-safe
_store_singleton = _InMemoryTaskStore()


# PUBLIC_INTERFACE
def get_task_store() -> _InMemoryTaskStore:
    """Return the singleton in-memory task store."""
    return _store_singleton


# Convenience module-level wrappers for common operations

# PUBLIC_INTERFACE
def create_task(*, initial_files: Optional[List[str]] = None, excel_template_path: Optional[str] = None) -> Task:
    """Create a new task via the singleton store."""
    return _store_singleton.create_task(initial_files=initial_files, excel_template_path=excel_template_path)

# PUBLIC_INTERFACE
def get_task(task_id: str) -> Optional[Task]:
    """Get a task by id via the singleton store."""
    return _store_singleton.get_task(task_id)

# PUBLIC_INTERFACE
def list_tasks() -> List[Task]:
    """List all tasks via the singleton store."""
    return _store_singleton.list_tasks()

# PUBLIC_INTERFACE
def update_task(task_id: str, **fields: Any) -> Optional[Task]:
    """Update a task via the singleton store."""
    return _store_singleton.update_task(task_id, **fields)

# PUBLIC_INTERFACE
def append_message(task_id: str, message: str) -> Optional[Task]:
    """Append a message to a task via the singleton store."""
    return _store_singleton.append_message(task_id, message)

# PUBLIC_INTERFACE
def set_progress(task_id: str, progress: int) -> Optional[Task]:
    """Set progress on a task via the singleton store."""
    return _store_singleton.set_progress(task_id, progress)

# PUBLIC_INTERFACE
def set_status(task_id: str, status: TaskStatus | str) -> Optional[Task]:
    """Set status on a task via the singleton store."""
    return _store_singleton.set_status(task_id, status)
