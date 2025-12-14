from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from ..models import Status
from .log_service import write_log

def create_status(db: Session, status_name: str, actor_user_id: int) -> Status:
    exists = db.execute(select(Status).where(Status.status_name == status_name)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Энэ status_name аль хэдийн байна")

    st = Status(status_name=status_name)
    db.add(st)
    db.flush()

    write_log(db, user_id=actor_user_id, action="STATUS_CREATED", detail=f"status_id={st.status_id}, name={status_name}")
    return st

def list_statuses(db: Session) -> list[Status]:
    return db.execute(select(Status).order_by(Status.status_id.asc())).scalars().all()

def update_status(db: Session, status_id: int, status_name: str, actor_user_id: int) -> Status:
    st = db.execute(select(Status).where(Status.status_id == status_id)).scalar_one_or_none()
    if not st:
        raise HTTPException(status_code=404, detail="Status олдсонгүй")

    st.status_name = status_name
    write_log(db, user_id=actor_user_id, action="STATUS_UPDATED", detail=f"status_id={status_id}, new_name={status_name}")
    return st

def delete_status(db: Session, status_id: int, actor_user_id: int) -> None:
    st = db.execute(select(Status).where(Status.status_id == status_id)).scalar_one_or_none()
    if not st:
        raise HTTPException(status_code=404, detail="Status олдсонгүй")

    db.delete(st)
    write_log(db, user_id=actor_user_id, action="STATUS_DELETED", detail=f"status_id={status_id}")
