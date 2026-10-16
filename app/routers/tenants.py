from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.catalogues import TENANT_STATUSES
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
    payload = data.model_dump(exclude={'organization_type', 'primary_contact_name', 'primary_contact_email'})
    tenant = Tenant(**payload, status='REGISTERED')
    db.add(tenant)
    flush(db)
    profile = {
        'legal_name': data.name,
        'organization_type': data.organization_type,
        'operating_model': data.operating_model,
    }
    contacts = {}
    if data.primary_contact_email:
        contacts['primary_email'] = data.primary_contact_email.lower().strip()
    if data.primary_contact_name:
        contacts['team_contact'] = data.primary_contact_name
    sections = {'profile': profile}
    if contacts:
        sections['contacts'] = contacts
    db.add(OrganizationSetup(
        tenant_id=tenant.id,
        sections=sections,
        organization_type=data.organization_type,
        status='DRAFT',
        version=1,
    ))
    audit(db, actor, 'tenant.created', 'tenant', tenant.id, tenant.id, {
        'slug': tenant.slug,
        'organization_type': data.organization_type,
        'status': tenant.status,
    })
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
    if not is_platform(actor) and any(field in changes for field in ('operating_model', 'status')):
        raise HTTPException(status_code=403, detail='Only Platform Ops may change tenant operating model/status')
    if 'status' in changes and changes['status'] == 'ACTIVE':
        raise HTTPException(status_code=422, detail='Use POST /admin/tenants/{id}/activate to mark a tenant ACTIVE')
    before = {k: getattr(tenant, k) for k in changes}
    for field, value in changes.items():
        setattr(tenant, field, value)
    audit(db, actor, 'tenant.updated', 'tenant', tenant.id, tenant.id, {'before': before, 'after': changes})
    save(db)
    db.refresh(tenant)
    return tenant

@router.post('/{tenant_id}/activate', response_model=TenantOut)
def activate_tenant(tenant_id: str, db: Session = Depends(get_db), actor: User = Depends(require_platform)):
    """Demo activation gate: setup must be APPROVED before the tenant becomes ACTIVE."""
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail='Tenant not found')
    if tenant.status == 'ACTIVE':
        raise HTTPException(status_code=409, detail='Tenant is already ACTIVE')
    if tenant.status not in ('REGISTERED', 'SUSPENDED'):
        raise HTTPException(status_code=409, detail=f'Cannot activate tenant in status {tenant.status}')
    setup = db.scalar(select(OrganizationSetup).where(OrganizationSetup.tenant_id == tenant_id))
    if not setup or setup.status != 'APPROVED':
        raise HTTPException(status_code=409, detail='Organization setup must be APPROVED before activation')
    before = tenant.status
    tenant.status = 'ACTIVE'
    audit(db, actor, 'tenant.activated', 'tenant', tenant.id, tenant.id, {
        'before': before,
        'after': 'ACTIVE',
        'setup_id': setup.id,
        'setup_version': setup.version,
    })
    save(db)
    db.refresh(tenant)
    return tenant

@router.post('/{tenant_id}/suspend', response_model=TenantOut)
def suspend_tenant(tenant_id: str, db: Session = Depends(get_db), actor: User = Depends(require_platform)):
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail='Tenant not found')
    if tenant.status == 'SUSPENDED':
        raise HTTPException(status_code=409, detail='Tenant is already SUSPENDED')
    if tenant.status not in TENANT_STATUSES:
        raise HTTPException(status_code=409, detail='Unknown tenant status')
    before = tenant.status
    tenant.status = 'SUSPENDED'
    audit(db, actor, 'tenant.suspended', 'tenant', tenant.id, tenant.id, {'before': before, 'after': 'SUSPENDED'})
    save(db)
    db.refresh(tenant)
    return tenant
