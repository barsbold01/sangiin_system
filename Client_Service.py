from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from ..models import Client
from .log_service import write_log

def create_client(db: Session, name: str, company: str | None, phone: str | None, email: str | None, actor_user_id: int) -> Client:
    client = Client(name=name, company=company, phone=phone, email=email)
    db.add(client)
    db.flush()

    write_log(db, user_id=actor_user_id, task_id=None, action="CLIENT_CREATED", detail=f"client_id={client.client_id}, name={name}")
    return client

def update_client(db: Session, client_id: int, actor_user_id: int, **fields) -> Client:
    client = db.execute(select(Client).where(Client.client_id == client_id)).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client олдсонгүй")

    allowed = {"name", "company", "phone", "email"}
    for k, v in fields.items():
        if k in allowed and v is not None:
            setattr(client, k, v)

    write_log(db, user_id=actor_user_id, task_id=None, action="CLIENT_UPDATED", detail=f"client_id={client_id}, fields={list(fields.keys())}")
    return client

def get_client(db: Session, client_id: int) -> Client:
    client = db.execute(select(Client).where(Client.client_id == client_id)).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client олдсонгүй")
    return client

def list_clients(db: Session, q: str | None = None, limit: int = 50, offset: int = 0) -> list[Client]:
    stmt = select(Client).order_by(Client.created_at.desc()).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    if q:
        q2 = q.lower()
        rows = [c for c in rows if (c.name and q2 in c.name.lower()) or (c.company and q2 in c.company.lower())]
    return rows

def delete_client(db: Session, client_id: int, actor_user_id: int) -> None:
    client = db.execute(select(Client).where(Client.client_id == client_id)).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client олдсонгүй")

    db.delete(client)
    write_log(db, user_id=actor_user_id, action="CLIENT_DELETED", detail=f"client_id={client_id}")
