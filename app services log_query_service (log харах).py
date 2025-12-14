from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import Log

def list_logs(db: Session, task_id: int | None = None, user_id: int | None = None, limit: int = 100, offset: int = 0) -> list[Log]:
    stmt = select(Log).order_by(Log.created_at.desc()).limit(limit).offset(offset)
    if task_id is not None:
        stmt = stmt.where(Log.task_id == task_id)
    if user_id is not None:
        stmt = stmt.where(Log.user_id == user_id)
    return db.execute(stmt).scalars().all()
