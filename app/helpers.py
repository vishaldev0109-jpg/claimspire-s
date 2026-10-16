from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import AuditEvent, Tenant, User
from app.security import assert_resource_access


def audit(db: Session, actor: User, action: str, entity_type: str, entity_id: str | None, tenant_id: str | None, detail: dict | None = None) -> None:
    db.add(AuditEvent(actor_id=actor.id, action=action, entity_type=entity_type, entity_id=entity_id, tenant_id=tenant_id, detail=detail or {}))

def flush(db: Session) -> None:
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Duplicate or invalid reference') from None

def save(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Duplicate or invalid reference') from None

def scoped_item(db: Session, model: type, item_id: str, actor: User):
    obj = db.get(model, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail='Item not found')
    assert_resource_access(actor, getattr(obj, 'tenant_id', None))
    return obj

def ensure_tenant(db: Session, tenant_id: str) -> None:
    if not db.get(Tenant, tenant_id):
        raise HTTPException(status_code=404, detail='Tenant not found')

def paged(db: Session, model: type, tenant_id: str | None, limit: int, offset: int, *conditions):
    stmt = select(model)
    if tenant_id is not None:
        stmt = stmt.where(model.tenant_id == tenant_id)
    for cond in conditions:
        if cond is not None:
            stmt = stmt.where(cond)
    return db.scalars(stmt.limit(limit).offset(offset)).all()
