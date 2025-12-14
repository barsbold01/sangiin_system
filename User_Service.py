from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from ..models import User, Role
from .Log_Services import write_log

def change_user_role(db: Session, user_id: int, role_id: int, actor_user_id: int) -> User:
    u = db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User олдсонгүй")

    r = db.execute(select(Role).where(Role.role_id == role_id)).scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Role олдсонгүй")

    u.role_id = role_id
    write_log(db, user_id=actor_user_id, action="USER_ROLE_CHANGED", detail=f"user_id={user_id}, role_id={role_id}")
    return u

def set_user_active(db: Session, user_id: int, is_active: bool, actor_user_id: int) -> User:
    u = db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User олдсонгүй")

    u.is_active = is_active
    write_log(db, user_id=actor_user_id, action="USER_ACTIVE_CHANGED", detail=f"user_id={user_id}, is_active={is_active}")
    return u

