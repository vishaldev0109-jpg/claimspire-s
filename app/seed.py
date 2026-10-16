"""Explicitly synthetic ClaimSpire demo records. Idempotent per database."""
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import AIUseCase, Assignment, AuditEvent, Claim, FeatureFlag, FinancialItem, Integration, LineOfBusiness, QAReview, Role, Tenant, User, WorkflowTemplate
from app.security import hash_password

PERSONAS=[
('CLAIMS_OPS_ADMIN','Claims Operations Administrator','FNOL setup and intake coordination','Web'),
('CLAIMANT','Insured / Claimant','Reports loss and supplies information','Portal'),
('BROKER','Agent / Broker / Authorized Client','Supports and represents the customer','Portal'),
('DESK_ADJUSTER','Desk Adjuster / Examiner','Desk claim handling and investigation','Web'),
('FIELD_ADJUSTER','Field Adjuster','On-site evidence and inspection','Mobile'),
('QA_REVIEWER','QA Reviewer','Inspection package quality review','Web'),
('CLAIMS_SUPERVISOR','Claims Manager / Supervisor','Triage, exceptions, oversight','Web'),
('CAT_MANAGER','CAT Manager / Surge Lead','Catastrophe surge management','Web'),
('SIU_INVESTIGATOR','SIU / Fraud Investigator','Special investigations','Web'),
('SUBRO_SPECIALIST','Subrogation / Recovery Specialist','Third-party recovery tracking','Web'),
('FINANCE_OPS','Financial Ops / Accounting Ops','Financial work queues and reconciliation','Web'),
('FINANCE_MANAGER','Finance Manager / Controller','Financial governance and oversight','Web'),
('COMPLIANCE','Compliance / Regulatory','Regulatory controls and audit','Web'),
('TENANT_IT_ADMIN','Tenant IT / System Administrator','Tenant configurations and access','Admin'),
('PLATFORM_OPS','ClaimSpire Platform Operations','Internal platform governance','Admin'),
('WORKFORCE_ADMIN','Workforce / HR & Credentialing','Licenses and workforce readiness','Web'),
]

DEMO_PASSWORD='DemoAdmin123!'

def seed_demo_data(db: Session):
    if db.scalar(select(Tenant.id).limit(1)):
        return
    db.add_all([Role(code=code,name=name,purpose=purpose,primary_surface=surface) for code,name,purpose,surface in PERSONAS])
    acme=Tenant(name='Harbor Mutual Insurance (DEMO)',slug='harbor-mutual',operating_model='HYBRID')
    north=Tenant(name='Summit Independent Adjusting (DEMO)',slug='summit-ia',operating_model='FIELD')
    db.add_all([acme,north]);db.flush()
    users=[
        User(name='Platform Operator',email='platform@claimspire.local',tenant_id=None,role_code='PLATFORM_OPS',password_hash=hash_password(DEMO_PASSWORD)),
        User(name='Harbor Tenant Administrator',email='admin@harbor.local',tenant_id=acme.id,role_code='TENANT_IT_ADMIN',password_hash=hash_password(DEMO_PASSWORD)),
        User(name='Summit Tenant Administrator',email='admin@summit.local',tenant_id=north.id,role_code='TENANT_IT_ADMIN',password_hash=hash_password(DEMO_PASSWORD)),
        User(name='Harbor Supervisor',email='supervisor@harbor.local',tenant_id=acme.id,role_code='CLAIMS_SUPERVISOR',password_hash=hash_password(DEMO_PASSWORD)),
        User(name='Harbor Desk Adjuster',email='desk@harbor.local',tenant_id=acme.id,role_code='DESK_ADJUSTER',password_hash=hash_password(DEMO_PASSWORD)),
    ]
    db.add_all(users);db.flush()
    for tenant in (acme,north):
        for code,label in [('PROPERTY','Commercial Property'),('PERSONAL_AUTO','Personal Auto'),('LIABILITY','General Liability')]:
            db.add(LineOfBusiness(tenant_id=tenant.id,code=code,name=label))
        db.add(WorkflowTemplate(tenant_id=tenant.id,key='standard_property_claim',name='Property Claim Journey (DEMO)',description='High-level view; not executable production rules',stages=['FNOL','TRIAGE','DESK','DISPATCH','FIELD','QA','FINANCE','CLOSED']))
        for key,description,enabled in [('FNOL_INTAKE','Claim intake',True),('FIELD_OPERATIONS','Field inspections',True),('AI_NBA_EXPLANATION','Optional AI-generated NBA explanations',False),('CAT_SURGE','Catastrophe operation mode',False),('PORTAL_STATUS_VIEW','External read-only status view',True)]:
            db.add(FeatureFlag(tenant_id=tenant.id,key=key,description=description,enabled=enabled))
        for key,name,enabled in [('NBA_EXPLANATION','Next Best Action explanations',False),('ASK_CLAIMSPIRE','Ask ClaimSpire assistant (mock only)',False),('T_AND_E_DRAFT','Communications-to-expense drafts (mock only)',False)]:
            db.add(AIUseCase(tenant_id=tenant.id,key=key,name=name,description='Demo register only; no model calls',enabled=enabled))
        for name,cat,status in [('Policy Import (demo)','Policy Data','CONNECTED_DEMO'),('Email Intake (demo)','Communications','NOT_CONFIGURED'),('CSV Finance Export (demo)','Financial','CONNECTED_DEMO')]:
            db.add(Integration(tenant_id=tenant.id,name=name,category=cat,status=status,description='Synthetic integration status; no provider connection'))
        cases=[
            ('FNOL','LOW'),('TRIAGE','MEDIUM'),('DESK','MEDIUM'),('DISPATCH','HIGH'),
            ('FIELD','MEDIUM'),('QA','HIGH'),('FINANCE','MEDIUM'),('CLOSED','LOW'),
        ]
        for idx,(status,severity) in enumerate(cases,1):
            claim=Claim(tenant_id=tenant.id,claim_number=f'{tenant.slug.upper()[:3]}-2026-{idx:04}',claimant_name=f'Demo Policyholder {idx}',lob_code='PROPERTY' if idx%2 else 'PERSONAL_AUTO',location='Demo loss location',status=status,severity=severity,desk_adjuster_id=users[4].id if tenant.id==acme.id else None)
            db.add(claim);db.flush()
            if status in ('DISPATCH','FIELD','QA'):
                db.add(Assignment(tenant_id=tenant.id,claim_id=claim.id,assignee_name='Demo Field Adjuster',assignment_type='FIELD',status='ACCEPTED' if status!='DISPATCH' else 'PENDING'))
            if status in ('QA','FINANCE'):
                db.add(QAReview(tenant_id=tenant.id,claim_id=claim.id,package_ref=f'PKG-{idx:04}',status='NEEDS_CORRECTION' if status=='QA' else 'PASSED',notes='Synthetic package review'))
            if status in ('FINANCE','CLOSED'):
                db.add(FinancialItem(tenant_id=tenant.id,claim_id=claim.id,item_type='PAYMENT_REQUEST',amount=Decimal('4500.00')+idx,status='PENDING_REVIEW' if status=='FINANCE' else 'EXPORTED_DEMO'))
        db.add(AuditEvent(tenant_id=tenant.id,actor_id=None,action='demo.seeded',entity_type='tenant',entity_id=tenant.id,detail={'synthetic':True,'warning':'Not real claim or payment data'}))
    db.commit()
