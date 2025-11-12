from __future__ import annotations
from pathlib import Path
from datetime import datetime, date

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .todo_manager import TodoManager
from .todo_model import DATE_FMT, parse_date


console = Console()
ROOT = Path(__file__).resolve().parents[1]
STORAGE = ROOT / "storage.json"


def render_tasks(mgr: TodoManager, tasks=None) -> None:
    tasks = tasks if tasks is not None else mgr.all()
    table = Table(title="To-Do List")
    table.add_column("ID", justify="right")
    table.add_column("Title")
    table.add_column("Due (YYYY-MM-DD)")
    table.add_column("Done", justify="center")
    table.add_column("Created At")

    for t in tasks:
        table.add_row(str(t.id), t.title, t.due or "-", "✅" if t.done else "❌", t.created_at)
    console.print(table)


def add_task(mgr: TodoManager) -> None:
    title = Prompt.ask("제목")
    desc = Prompt.ask("설명", default="")
    due = Prompt.ask("마감일(YYYY-MM-DD, 빈칸 가능)", default="")
    due = due or None
    try:
        if due and not parse_date(due):
            console.print("[red]날짜 형식이 올바르지 않습니다[/red]")
            return
        task = mgr.add(title, desc, due)
        console.print(f"[green]추가됨[/green]: #{task.id} {task.title}")
    except Exception as e:
        console.print(f"[red]{e}[/red]")


def edit_task(mgr: TodoManager) -> None:
    task_id = int(Prompt.ask("수정할 ID"))
    t = mgr.get(task_id)
    if not t:
        console.print("[red]해당 ID가 없습니다[/red]")
        return
    title = Prompt.ask("새 제목(Enter=유지)", default=t.title)
    desc = Prompt.ask("새 설명(Enter=유지)", default=t.description)
    due = Prompt.ask("새 마감일(YYYY-MM-DD, 빈칸=없음, Enter=유지)", default=t.due or "")
    due = due if due != "" else None
    try:
        mgr.edit(task_id, title=title, description=desc, due=due)
        console.print("[green]수정 완료[/green]")
    except Exception as e:
        console.print(f"[red]{e}[/red]")


def delete_task(mgr: TodoManager) -> None:
    task_id = int(Prompt.ask("삭제할 ID"))
    t = mgr.get(task_id)
    if not t:
        console.print("[red]해당 ID가 없습니다[/red]")
        return
    if Confirm.ask(f"정말 삭제하시겠습니까? #{task_id} {t.title}", default=False):
        if mgr.delete(task_id):
            console.print("[green]삭제 완료[/green]")
        else:
            console.print("[red]삭제 실패[/red]")


def toggle_task(mgr: TodoManager) -> None:
    task_id = int(Prompt.ask("완료/해제 토글할 ID"))
    t = mgr.toggle(task_id)
    if t:
        console.print(f"[green]상태 변경[/green]: #{t.id} -> {'완료' if t.done else '미완료'}")
    else:
        console.print("[red]해당 ID가 없습니다[/red]")


def filter_due(mgr: TodoManager) -> None:
    s = Prompt.ask("필터할 날짜 (YYYY-MM-DD)")
    d = parse_date(s)
    if not d:
        console.print("[red]날짜 형식이 올바르지 않습니다[/red]")
        return
    tasks = mgr.due_on(d)
    render_tasks(mgr, tasks)


def search_tasks(mgr: TodoManager) -> None:
    key = Prompt.ask("검색 키워드")
    tasks = mgr.search(key)
    render_tasks(mgr, tasks)


def main() -> None:
    mgr = TodoManager(STORAGE)

    actions = {
        "1": ("목록 보기", lambda: render_tasks(mgr)),
        "2": ("추가", lambda: add_task(mgr)),
        "3": ("수정", lambda: edit_task(mgr)),
        "4": ("삭제", lambda: delete_task(mgr)),
        "5": ("완료/해제 토글", lambda: toggle_task(mgr)),
        "6": ("날짜로 필터(YYYY-MM-DD)", lambda: filter_due(mgr)),
        "7": ("검색", lambda: search_tasks(mgr)),
        "0": ("종료", None),
    }

    while True:
        console.rule("[bold blue]To-Do Manager")
        for k, (label, _) in actions.items():
            console.print(f"[cyan]{k}[/cyan] {label}")
        choice = Prompt.ask("선택")
        if choice == "0":
            console.print("[bold]안녕히 가세요![/bold]")
            break
        action = actions.get(choice)
        if action:
            action[1]()
        else:
            console.print("[red]올바르지 않은 선택입니다[/red]")


if __name__ == "__main__":
    main()
