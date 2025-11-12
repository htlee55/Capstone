from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional, Dict, Any


DATE_FMT = "%Y-%m-%d"


def today_str() -> str:
    return date.today().strftime(DATE_FMT)


def parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except ValueError:
        return None


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    due: Optional[str] = None       # "YYYY-MM-DD" 또는 None
    done: bool = False
    created_at: str = datetime.utcnow().isoformat(timespec="seconds")

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Task":
        return cls(
            id=int(d["id"]),
            title=d.get("title", ""),
            description=d.get("description", ""),
            due=d.get("due"),
            done=bool(d.get("done", False)),
            created_at=d.get("created_at") or datetime.utcnow().isoformat(timespec="seconds"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def toggle(self) -> None:
        self.done = not self.done

    def due_date(self) -> Optional[date]:
        return parse_date(self.due)
