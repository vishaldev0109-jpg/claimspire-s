from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tenant, User, OrganizationSetup
from app.schemas import TenantCreate, TenantOut, TenantPatch
from app.security import require_admin, require_platform, assert_resource_access, is_platform
from app.helpers import audit, flush, save

router = APIRouter(prefix='/admin/tenants', tags=['Admin: Tenants'])

@router.get('', response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db), actor: User = Depends(require_admin), limit: int = Query(50,ge=1,le=200), offset: int = Query(0,ge=0)):
    stmt = select(Tenant)
    if not is_platform(actor):
        stmt = stmt.where(Tenant.id == actor.tenant_id)
    return db.scalars(stmt.order_by(Tenant.name).limit(limit).offset(offset)).all()

@router.post('', response_model=TenantOut, status_code=201)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db), actor: User = Depends(require_platform)):
    tenant = Tenant(**data.model_dump())
    db.add(tenant)
    flush(db)
    db.add(OrganizationSetup(tenant_id=tenant.id,sections={},organization_type='CARRIER_TPA'))
    audit(db,actor,'tenant.created','tenant',tenant.id,tenant.id,{'slug':tenant.slug})
    save(db)
    db.refresh(tenant)
    return tenant

@router.get('/{tenant_id}', response_model=TenantOut)
def get_tenant(tenant_id: str, db: Session = Depends(get_db), actor: User = Depends(require_admin)):
    assert_resource_access(actor, tenant_id)
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail='Tenant not found')
    return tenant

@router.patch('/{tenant_id}', response_model=TenantOut)
def patch_tenant(tenant_id: str, data: TenantPatch, db: Session = Depends(get_db), actor: User = Depends(require_admin)):
    assert_resource_access(actor, tenant_id)
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail='Tenant not found')
    changes = data.model_dump(exclude_unset=True)
    if not is_platform(actor) and any(field in changes for field in ('operating_model','status')):
        raise HTTPException(status_code=403, detail='Only Platform Ops may change tenant operating model/status')
    before = {k:getattr(tenant,k) for k in changes}
    for field,value in changes.items():
        setattr(tenant,field,value)
    audit(db,actor,'tenant.updated','tenant',tenant.id,tenant.id,{'before':before,'after':changes})
    save(db)
    db.refresh(tenant)
    return tenant
