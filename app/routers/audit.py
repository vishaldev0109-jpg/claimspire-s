from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditEvent, User
from app.schemas import AuditOut
from app.security import require_admin, permitted_tenant

router=APIRouter(prefix='/admin',tags=['Admin: Audit (Read Only)'])

@router.get('/audit-events', response_model=list[AuditOut])
def list_audit(tenant_id:str|None=None,action:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=permitted_tenant(actor,tenant_id)
    stmt=select(AuditEvent)
    if tid is not None:stmt=stmt.where(AuditEvent.tenant_id==tid)
    if action:stmt=stmt.where(AuditEvent.action==action)
    return db.scalars(stmt.order_by(AuditEvent.created_at.desc()).limit(limit).offset(offset)).all()
