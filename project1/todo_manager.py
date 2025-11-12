from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import date

from .todo_model import Task, DATE_FMT, parse_date


class TodoManager:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self._tasks: List[Task] = []
        self._next_id = 1
        self.load()

    # ---------- Persistence ----------
    def load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = []
        else:
            data = []
        self._tasks = [Task.from_dict(d) for d in data]
        self._next_id = (max((t.id for t in self._tasks), default=0) + 1)

    def save(self) -> None:
        data = [t.to_dict() for t in self._tasks]
        self.storage_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- CRUD ----------
    def add(self, title: str, description: str = "", due: Optional[str] = None) -> Task:
        if due and not parse_date(due):
            raise ValueError(f"잘못된 날짜 형식입니다. YYYY-MM-DD 예: 2025-11-12 (입력: {due})")
        task = Task(id=self._next_id, title=title, description=description, due=due)
        self._tasks.append(task)
        self._next_id += 1
        self.save()
        return task

    def edit(self, task_id: int, *, title: Optional[str] = None,
             description: Optional[str] = None, due: Optional[str] = None) -> Optional[Task]:
        t = self.get(task_id)
        if not t:
            return None
        if title is not None:
            t.title = title
        if description is not None:
            t.description = description
        if due is not None:
            if due and not parse_date(due):
                raise ValueError(f"잘못된 날짜 형식입니다. YYYY-MM-DD (입력: {due})")
            t.due = due
        self.save()
        return t

    def delete(self, task_id: int) -> bool:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        changed = len(self._tasks) != before
        if changed:
            self.save()
        return changed

    def toggle(self, task_id: int) -> Optional[Task]:
        t = self.get(task_id)
        if not t:
            return None
        t.toggle()
        self.save()
        return t

    # ---------- Queries ----------
    def all(self) -> List[Task]:
        return list(self._tasks)

    def get(self, task_id: int) -> Optional[Task]:
        return next((t for t in self._tasks if t.id == task_id), None)

    def due_on(self, d: date) -> List[Task]:
        return [t for t in self._tasks if t.due and parse_date(t.due) == d]

    def search(self, keyword: str) -> List[Task]:
        key = keyword.lower().strip()
        return [t for t in self._tasks if key in t.title.lower() or key in t.description.lower()]
