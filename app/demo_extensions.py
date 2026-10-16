"""Idempotent additional local demo records for organization and workforce journeys."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Tenant, User, OrganizationSetup, OrganizationTeam, WorkforceStatus


def seed_admin_extensions(db: Session):
    tenants=db.scalars(select(Tenant).order_by(Tenant.slug)).all()
    for tenant in tenants:
        if not db.scalar(select(OrganizationSetup.id).where(OrganizationSetup.tenant_id==tenant.id)):
            is_ia=tenant.slug=='summit-ia'
            admin=db.scalar(select(User).where(User.tenant_id==tenant.id,User.role_code=='TENANT_IT_ADMIN'))
            data={
                'profile':{'legal_name':tenant.name,'organization_type':'IA_FIRM' if is_ia else 'CARRIER_TPA','operating_model':tenant.operating_model},
                'contacts':{'primary_email':admin.email if admin else 'demo@example.invalid','phone':'','street_address':'Demo address - not a real location'},
                'coverage':{'lob_codes':['PROPERTY','LIABILITY'] if is_ia else [],'license_reference':'SAMPLE-LICENSE-NOT-VERIFIED' if is_ia else ''},
                'structure':{'structure_summary':'IA dispatch > field team > QA team' if is_ia else '', 'team_contact':''},
                'branding':{'display_name':tenant.name,'logo_reference':''} if is_ia else {},
            }
            db.add(OrganizationSetup(tenant_id=tenant.id,organization_type='IA_FIRM' if is_ia else 'CARRIER_TPA',
                                     responsible_user_id=admin.id if admin else None,sections=data,
                                     status='IN_REVIEW' if is_ia else 'DRAFT',submitted_by_id=admin.id if is_ia and admin else None))
        for name in ((['Summit IA Dispatch','Summit QA'] if tenant.slug=='summit-ia' else ['Harbor Claims Operations','Harbor Field Team'])):
            if not db.scalar(select(OrganizationTeam.id).where(OrganizationTeam.tenant_id==tenant.id,OrganizationTeam.name==name)):
                db.add(OrganizationTeam(tenant_id=tenant.id,name=name,team_type='QA' if 'QA' in name else ('FIELD' if 'Field' in name else 'CLAIMS_OPERATIONS')))
        users=db.scalars(select(User).where(User.tenant_id==tenant.id)).all()
        for user in users:
            if not db.get(WorkforceStatus,user.id):
                db.add(WorkforceStatus(user_id=user.id,tenant_id=tenant.id,status='AVAILABLE' if user.is_active else 'OFFBOARDED'))
    db.commit()
