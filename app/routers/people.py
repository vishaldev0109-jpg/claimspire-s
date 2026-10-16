from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Role, User, WorkforceStatus
from app.schemas import RoleOut, UserCreate, UserPatch, UserOut
from app.security import require_admin, is_platform, permitted_tenant, mutation_tenant
from app.helpers import audit, flush, save, scoped_item, ensure_tenant
from app.security import hash_password

router = APIRouter(tags=['Admin: People & Personas'])

@router.get('/admin/roles', response_model=list[RoleOut])
def roles(db: Session = Depends(get_db), actor: User = Depends(require_admin)):
    return db.scalars(select(Role).order_by(Role.name)).all()

@router.get('/admin/users', response_model=list[UserOut])
def list_users(tenant_id: str | None = None, role_code: str | None = None, active: bool | None = None, limit: int = Query(50,ge=1,le=200), offset: int = Query(0,ge=0), db: Session = Depends(get_db), actor: User = Depends(require_admin)):
    tid = permitted_tenant(actor, tenant_id)
    stmt = select(User)
    if tid is not None:
        stmt=stmt.where(User.tenant_id == tid)
    if role_code:
        stmt=stmt.where(User.role_code == role_code)
    if active is not None:
        stmt=stmt.where(User.is_active == active)
    return db.scalars(stmt.order_by(User.name).limit(limit).offset(offset)).all()

@router.post('/admin/users', response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), actor: User = Depends(require_admin)):
    tenant_id = mutation_tenant(actor,data.tenant_id)
    ensure_tenant(db,tenant_id)
    if not db.get(Role,data.role_code):
        raise HTTPException(status_code=422, detail='Unknown role_code')
    if data.role_code == 'PLATFORM_OPS':
        raise HTTPException(status_code=403, detail='Global Platform Ops users require a separate provisioning process')
    user = User(tenant_id=tenant_id, name=data.name, email=data.email.lower().strip(), password_hash=hash_password(data.password), role_code=data.role_code)
    db.add(user)
    flush(db)
    db.add(WorkforceStatus(user_id=user.id,tenant_id=tenant_id,status='AVAILABLE'))
    audit(db,actor,'user.created','user',user.id,tenant_id,{'role_code':user.role_code})
    save(db)
    db.refresh(user)
    return user

@router.get('/admin/users/{user_id}', response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db), actor: User = Depends(require_admin)):
    return scoped_item(db,User,user_id,actor)

@router.patch('/admin/users/{user_id}', response_model=UserOut)
def patch_user(user_id: str, data: UserPatch, db: Session = Depends(get_db), actor: User = Depends(require_admin)):
    user = scoped_item(db,User,user_id,actor)
    changes=data.model_dump(exclude_unset=True)
    if user.id == actor.id and (changes.get('is_active') is False or (changes.get('role_code') and changes['role_code'] != actor.role_code)):
        raise HTTPException(status_code=409, detail='Cannot deactivate or demote your own account')
    if user.role_code == 'PLATFORM_OPS' or changes.get('role_code') == 'PLATFORM_OPS':
        raise HTTPException(status_code=403, detail='Platform Ops accounts require a separate provisioning process')
    if changes.get('role_code') and not db.get(Role,changes['role_code']):
        raise HTTPException(status_code=422, detail='Unknown role_code')
    before={k:getattr(user,k) for k in changes}
    for field,value in changes.items():
        setattr(user,field,value)
    audit(db,actor,'user.updated','user',user.id,user.tenant_id,{'before':before,'after':changes})
    save(db)
    db.refresh(user)
    return user
