"""Read-only cross-domain Admin overviews backed by local seeded demo data."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Assignment, Claim, FinancialItem, QAReview, Tenant, User, FeatureFlag, Integration, WorkflowTemplate
from app.schemas import AssignmentOut, ClaimOut, FinancialItemOut, QAReviewOut
from app.security import require_admin, permitted_tenant, is_platform

router = APIRouter(prefix='/admin', tags=['Admin: Operations (Read Only)'])

# Explicitly labeled demo status groups: for a real application the owning services supply these.
FLOW = [
    {'key':'FNOL','name':'FNOL / Intake','surface':'Web App','main_persona':'Claims Ops Administrator'},
    {'key':'TRIAGE','name':'Claim Creation & Triage','surface':'Web App','main_persona':'Claims Supervisor'},
    {'key':'DESK','name':'Desk Review','surface':'Web App','main_persona':'Desk Adjuster'},
    {'key':'DISPATCH','name':'Field Dispatch (if needed)','surface':'Web App','main_persona':'Desk / Dispatch team'},
    {'key':'FIELD','name':'Field Inspection','surface':'Mobile App','main_persona':'Field Adjuster'},
    {'key':'QA','name':'Package QA / Review','surface':'Web App','main_persona':'QA Reviewer'},
    {'key':'FINANCE','name':'Claim Evaluation & Financial Operations','surface':'Web App','main_persona':'Desk / Finance'},
    {'key':'CLOSED','name':'Resolution / Closure','surface':'Web App','main_persona':'Desk / Supervisor'}
]
NAV_ITEMS = [
    {'key':'dashboard','label':'Dashboard','path':'/dashboard','read_only':True},
    {'key':'tenants','label':'Tenants','path':'/tenants','read_only':False},
    {'key':'users','label':'Users & Personas','path':'/users','read_only':False},
    {'key':'workflows','label':'Workflow Templates','path':'/workflows','read_only':False},
    {'key':'lob','label':'Lines of Business','path':'/lines-of-business','read_only':False},
    {'key':'features','label':'Features & AI Controls','path':'/features','read_only':False},
    {'key':'claims','label':'Claims Overview','path':'/claims','read_only':True},
    {'key':'assignments','label':'Dispatch Overview','path':'/assignments','read_only':True},
    {'key':'qa','label':'QA Overview','path':'/qa-reviews','read_only':True},
    {'key':'finance','label':'Finance Overview','path':'/financial-items','read_only':True},
    {'key':'integrations','label':'Integration Status','path':'/integrations','read_only':False},
    {'key':'audit','label':'Audit Trail','path':'/audit-events','read_only':True}
]

def filtered_stmt(model, actor, tenant_id):
    tid=permitted_tenant(actor,tenant_id)
    stmt=select(model)
    if tid is not None:
        stmt=stmt.where(model.tenant_id==tid)
    return stmt

def grouped(db,model,column,actor,tenant_id):
    tid=permitted_tenant(actor,tenant_id)
    stmt=select(column,func.count()).select_from(model).group_by(column)
    if tid is not None:stmt=stmt.where(model.tenant_id==tid)
    return {str(k):v for k,v in db.execute(stmt).all()}

def count(db,model,actor,tenant_id):
    tid=permitted_tenant(actor,tenant_id)
    stmt=select(func.count()).select_from(model)
    if tid is not None:stmt=stmt.where(model.tenant_id==tid)
    return db.scalar(stmt) or 0

@router.get('/navigation')
def navigation(actor:User=Depends(require_admin)):
    return {'user_role':actor.role_code, 'items':NAV_ITEMS, 'surface':'INTERNAL_ADMIN_DEMO'}

@router.get('/dashboard/summary')
def summary(tenant_id:str|None=None,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=permitted_tenant(actor,tenant_id)
    tenant_count=db.scalar(select(func.count()).select_from(Tenant)) if is_platform(actor) and tid is None else 1
    return {
        'scope': {'tenant_id':tid,'all_tenants':tid is None},
        'tenant_count':tenant_count,
        'users':count(db,User,actor,tid),
        'claims':count(db,Claim,actor,tid),
        'assignments':count(db,Assignment,actor,tid),
        'qa_reviews':count(db,QAReview,actor,tid),
        'financial_items':count(db,FinancialItem,actor,tid),
        'configured_features':count(db,FeatureFlag,actor,tid),
        'integrations':count(db,Integration,actor,tid),
        'claim_statuses':grouped(db,Claim,Claim.status,actor,tid),
        'assignment_statuses':grouped(db,Assignment,Assignment.status,actor,tid),
        'qa_statuses':grouped(db,QAReview,QAReview.status,actor,tid),
        'financial_statuses':grouped(db,FinancialItem,FinancialItem.status,actor,tid),
        'note':'Local demo aggregates, not live ClaimSpire financial or claim system-of-record data'
    }

@router.get('/workflow-stages')
def workflow_stages(tenant_id:str|None=None,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    by_status=grouped(db,Claim,Claim.status,actor,tenant_id)
    return {'flow':[{**s,'demo_claim_count':by_status.get(s['key'],0)} for s in FLOW], 'note':'Illustrative operational stages; real claims may skip/parallelize branches.'}

@router.get('/claims',response_model=list[ClaimOut])
def claims(tenant_id:str|None=None,status:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    stmt=filtered_stmt(Claim,actor,tenant_id)
    if status:stmt=stmt.where(Claim.status==status)
    return db.scalars(stmt.order_by(Claim.created_at.desc()).limit(limit).offset(offset)).all()

@router.get('/assignments',response_model=list[AssignmentOut])
def assignments(tenant_id:str|None=None,status:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    stmt=filtered_stmt(Assignment,actor,tenant_id)
    if status:stmt=stmt.where(Assignment.status==status)
    return db.scalars(stmt.order_by(Assignment.created_at.desc()).limit(limit).offset(offset)).all()

@router.get('/qa-reviews',response_model=list[QAReviewOut])
def qa_reviews(tenant_id:str|None=None,status:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    stmt=filtered_stmt(QAReview,actor,tenant_id)
    if status:stmt=stmt.where(QAReview.status==status)
    return db.scalars(stmt.order_by(QAReview.created_at.desc()).limit(limit).offset(offset)).all()

@router.get('/financial-items',response_model=list[FinancialItemOut])
def financial_items(tenant_id:str|None=None,status:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    stmt=filtered_stmt(FinancialItem,actor,tenant_id)
    if status:stmt=stmt.where(FinancialItem.status==status)
    return db.scalars(stmt.order_by(FinancialItem.created_at.desc()).limit(limit).offset(offset)).all()

@router.get('/permissions')
def local_permissions(db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    # This describes local-demo access only; it is NOT the client-approved RBAC/ABAC matrix.
    tenant=db.get(Tenant,actor.tenant_id) if actor.tenant_id else None
    return {
        'role_code':actor.role_code,
        'tenant_id':actor.tenant_id,
        'tenant_name':tenant.name if tenant else None,
        'tenant_status':tenant.status if tenant else None,
        'tenant_scope':'ALL_DEMO_TENANTS' if is_platform(actor) else 'OWN_TENANT_ONLY',
        'isolation':'API-enforced; UI filter is not a security boundary',
        'allowed_modules':[item['key'] for item in NAV_ITEMS],
        'restrictions':[
            'tenant_admin_cannot_change_tenant_status_or_operating_model',
            'tenant_admin_cannot_provision_TENANT_IT_ADMIN',
            'tenant_admin_cannot_create_or_activate_tenants',
            'suspended_tenant_blocks_admin_access',
            'no_live_claim_qa_finance_mutations',
        ],
        'note':'Generic demo permissions, not ClaimSpire PDP policy'
    }
