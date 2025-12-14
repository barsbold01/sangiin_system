from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from ..models import Task, Status, TaskStatusHistory, User
from .log_service import write_log

DONE_STATUS_NAME = "Дууссан"  # status.status_name яг ингэж seed хийгдсэн байх

def _validate_dates(start_date: date | None, due_date: date | None):
    if start_date and due_date and due_date < start_date:
        raise HTTPException(status_code=400, detail="due_date нь start_date-ээс өмнө байж болохгүй")

def create_task(
    db: Session,
    actor_user_id: int,
    client_id: int,
    status_id: int,
    title: str,
    description: str | None = None,
    priority: str = "medium",
    start_date: date | None = None,
    due_date: date | None = None,
    assigned_to_user_id: int | None = None,
    created_by_user_id: int | None = None,  # хэрвээ Task дээр creator талбар байгаа бол ашиглана
) -> Task:
    _validate_dates(start_date, due_date)

    # assign user байгаа бол active эсэхийг шалгаж болно
    if assigned_to_user_id is not None:
        u = db.execute(select(User).where(User.user_id == assigned_to_user_id)).scalar_one_or_none()
        if not u:
            raise HTTPException(status_code=404, detail="Assigned user олдсонгүй")
        if not u.is_active:
            raise HTTPException(status_code=400, detail="Assigned user идэвхгүй байна")

    task = Task(
        client_id=client_id,
        assigned_to_user_id=assigned_to_user_id,
        status_id=status_id,
        title=title,
        description=description,
        priority=priority,
        start_date=start_date,
        due_date=due_date,
        completion_percentage=0,
        completed_at=None,
    )

    # Танай модел дээр энэ багана байвал л ажиллана (байхгүй бол router/service дээр None явуул)
    if hasattr(Task, "created_by_user_id") and created_by_user_id is not None:
        task.created_by_user_id = created_by_user_id

    db.add(task)
    db.flush()

    write_log(db, user_id=actor_user_id, task_id=task.task_id, action="TASK_CREATED", detail=f"title={title}")
    return task

def get_task(db: Session, task_id: int) -> Task:
    task = db.execute(select(Task).where(Task.task_id == task_id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task олдсонгүй")
    return task

def list_tasks(
    db: Session,
    status_id: int | None = None,
    client_id: int | None = None,
    assigned_to_user_id: int | None = None,
    priority: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Task]:
    stmt = select(Task).order_by(Task.created_at.desc()).limit(limit).offset(offset)
    if status_id is not None:
        stmt = stmt.where(Task.status_id == status_id)
    if client_id is not None:
        stmt = stmt.where(Task.client_id == client_id)
    if assigned_to_user_id is not None:
        stmt = stmt.where(Task.assigned_to_user_id == assigned_to_user_id)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)

    return db.execute(stmt).scalars().all()

def update_task(
    db: Session,
    task_id: int,
    actor_user_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    start_date: date | None = None,
    due_date: date | None = None,
) -> Task:
    task = get_task(db, task_id)

    # date validation (шинэ/хуучныг нийлүүлж шалгана)
    new_start = start_date if start_date is not None else task.start_date
    new_due = due_date if due_date is not None else task.due_date
    _validate_dates(new_start, new_due)

    if title is not None: task.title = title
    if description is not None: task.description = description
    if priority is not None: task.priority = priority
    if start_date is not None: task.start_date = start_date
    if due_date is not None: task.due_date = due_date

    write_log(db, user_id=actor_user_id, task_id=task_id, action="TASK_UPDATED", detail="fields updated")
    return task

def assign_task(db: Session, task_id: int, assigned_to_user_id: int | None, actor_user_id: int) -> Task:
    task = get_task(db, task_id)

    if assigned_to_user_id is not None:
        u = db.execute(select(User).where(User.user_id == assigned_to_user_id)).scalar_one_or_none()
        if not u:
            raise HTTPException(status_code=404, detail="Assigned user олдсонгүй")
        if not u.is_active:
            raise HTTPException(status_code=400, detail="Assigned user идэвхгүй байна")

    task.assigned_to_user_id = assigned_to_user_id
    write_log(db, user_id=actor_user_id, task_id=task_id, action="TASK_ASSIGNED", detail=f"assigned_to={assigned_to_user_id}")
    return task

def update_progress(db: Session, task_id: int, completion_percentage: int, actor_user_id: int) -> Task:
    task = get_task(db, task_id)

    if completion_percentage < 0 or completion_percentage > 100:
        raise HTTPException(status_code=400, detail="completion_percentage 0-100 хооронд байх ёстой")

    task.completion_percentage = completion_percentage

    if completion_percentage == 100 and task.completed_at is None:
        task.completed_at = datetime.utcnow()
    if completion_percentage < 100:
        task.completed_at = None

    write_log(db, user_id=actor_user_id, task_id=task_id, action="TASK_PROGRESS_UPDATED", detail=f"progress={completion_percentage}")
    return task

def change_task_status(db: Session, task_id: int, to_status_id: int, actor_user_id: int, note: str | None = None) -> None:
    # lock хийх (race condition-с хамгаална)
    task = db.execute(select(Task).where(Task.task_id == task_id).with_for_update()).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task олдсонгүй")

    if task.status_id == to_status_id:
        raise HTTPException(status_code=400, detail="Адил статус руу өөрчлөх шаардлагагүй")

    to_status = db.execute(select(Status).where(Status.status_id == to_status_id)).scalar_one_or_none()
    if not to_status:
        raise HTTPException(status_code=404, detail="Status олдсонгүй")

    from_status_id = task.status_id
    task.status_id = to_status_id

    if to_status.status_name == DONE_STATUS_NAME:
        task.completion_percentage = 100
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None

    db.add(TaskStatusHistory(
        task_id=task_id,
        changed_by_user_id=actor_user_id,
        from_status_id=from_status_id,
        to_status_id=to_status_id,
        note=note
    ))

    write_log(
        db,
        user_id=actor_user_id,
        task_id=task_id,
        action="TASK_STATUS_CHANGED",
        detail=f"{from_status_id}->{to_status_id}, note={note or '-'}"
    )

def delete_task(db: Session, task_id: int, actor_user_id: int) -> None:
    task = get_task(db, task_id)
    db.delete(task)
    write_log(db, user_id=actor_user_id, task_id=task_id, action="TASK_DELETED", detail="deleted task")

def get_task_history(db: Session, task_id: int) -> list[TaskStatusHistory]:
    return db.execute(
        select(TaskStatusHistory).where(TaskStatusHistory.task_id == task_id).order_by(TaskStatusHistory.changed_at.asc())
    ).scalars().all()
