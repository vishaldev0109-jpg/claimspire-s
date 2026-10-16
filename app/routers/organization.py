"""Demo organization onboarding, structure, and workforce lifecycle.

Client/design approval ownership and the exact five collection flows are unresolved.
This local POC uses configurable illustrative sections and provisional Platform Ops approval.
"""
import copy
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.catalogues import OPERATING_MODELS, ORG_TYPES
from app.database import get_db
from app.models import (Tenant, User, Claim, OrganizationSetup, OrganizationSetupSubmission,
                        OrganizationTeam, WorkforceStatus, WorkforceLifecycleEvent, OrganizationTeamMember)
from app.models import utc_now
from app.schemas import (OrganizationSetupOut, OrganizationSetupSubmissionOut, SetupSectionIn, SetupSubmitIn,
                         SetupDecisionIn, SetupOwnerIn, OrganizationTeamCreate, OrganizationTeamOut,
                         WorkforceChangeIn, OrganizationTeamMemberCreate)
from app.security import require_admin, require_platform, permitted_tenant, mutation_tenant, assert_resource_access
from app.helpers import audit, flush, save, ensure_tenant

router = APIRouter(prefix='/admin', tags=['Admin: Organization & Workforce'])

# Intentionally provisional groups. Once the design team supplies the five detailed
# data-collection flows, this catalogue can be replaced without rewriting the API.
SECTIONS = {
 'profile': {'label': 'Organization identity', 'fields': ['legal_name','organization_type','operating_model'], 'required':['legal_name','organization_type','operating_model']},
 'contacts': {'label': 'Address and contacts', 'fields':['primary_email','phone','street_address'], 'required':['primary_email','street_address']},
 'coverage': {'label': 'Lines of business and licenses', 'fields':['lob_codes','license_reference'], 'required':['lob_codes','license_reference']},
 'structure': {'label': 'Organization structure and teams', 'fields':['structure_summary','team_contact'], 'required':['structure_summary']},
 'branding': {'label': 'Branding basics', 'fields':['display_name','logo_reference'], 'required':['display_name']},
}
EDITABLE = frozenset(('DRAFT','CHANGES_REQUESTED'))
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def setup_for(db, tenant_id):
    setup = db.scalar(select(OrganizationSetup).where(OrganizationSetup.tenant_id==tenant_id))
    if not setup: raise HTTPException(status_code=404, detail='Organization setup missing')
    return setup

def missing(setup):
    missing_fields=[]
    for key, rule in SECTIONS.items():
        for name in rule['required']:
            val=(setup.sections or {}).get(key,{}).get(name)
            if val is None or val == '' or val == []:
                missing_fields.append(key+'.'+name)
    return missing_fields

def validation_issues(setup):
    """Typed/contextual checks beyond empty-field presence."""
    issues=[]
    sections=setup.sections or {}
    profile=sections.get('profile') or {}
    contacts=sections.get('contacts') or {}
    coverage=sections.get('coverage') or {}
    org_type=profile.get('organization_type') or setup.organization_type
    if org_type and org_type not in ORG_TYPES:
        issues.append({'field':'profile.organization_type','error':'UNSUPPORTED_ORGANIZATION_TYPE'})
    op_model=profile.get('operating_model')
    if op_model and op_model not in OPERATING_MODELS:
        issues.append({'field':'profile.operating_model','error':'UNSUPPORTED_OPERATING_MODEL'})
    email=contacts.get('primary_email')
    if email and not EMAIL_RE.match(str(email)):
        issues.append({'field':'contacts.primary_email','error':'INVALID_EMAIL'})
    legal=profile.get('legal_name')
    if legal is not None and isinstance(legal,str) and len(legal.strip()) < 2:
        issues.append({'field':'profile.legal_name','error':'TOO_SHORT'})
    lobs=coverage.get('lob_codes')
    if lobs is not None:
        if not isinstance(lobs,list) or not lobs:
            issues.append({'field':'coverage.lob_codes','error':'LOB_CODES_REQUIRED'})
        elif any(not isinstance(x,str) or not x.strip() for x in lobs):
            issues.append({'field':'coverage.lob_codes','error':'INVALID_LOB_CODES'})
    return issues

def require_draft(setup):
    if setup.status not in EDITABLE:
        raise HTTPException(status_code=409, detail='Setup is submitted/approved; return for changes before editing')

def check_version(setup, expected_version):
    if expected_version is not None and expected_version != setup.version:
        raise HTTPException(
            status_code=409,
            detail={'error':'VERSION_CONFLICT','current_version':setup.version,'expected_version':expected_version},
        )

def latest_open_submission(db, setup):
    return db.scalar(
        select(OrganizationSetupSubmission)
        .where(OrganizationSetupSubmission.setup_id==setup.id, OrganizationSetupSubmission.decision.is_(None))
        .order_by(OrganizationSetupSubmission.version.desc())
    )

@router.get('/organization-setup/sections')
def get_sections(actor: User = Depends(require_admin)):
    return {'provisional':True,'description':'Five proposed collection groups; final design-provided flows pending confirmation',
            'organization_types':sorted(ORG_TYPES),'operating_models':sorted(OPERATING_MODELS),
            'sections':[{'key':k, **v} for k,v in SECTIONS.items()]}

@router.get('/organization-setup',response_model=list[OrganizationSetupOut])
def list_setups(tenant_id: str | None=None, db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=permitted_tenant(actor,tenant_id)
    query=select(OrganizationSetup)
    if tid:query=query.where(OrganizationSetup.tenant_id==tid)
    return db.scalars(query.order_by(OrganizationSetup.created_at)).all()

@router.get('/organization-setup/{tenant_id}',response_model=OrganizationSetupOut)
def get_setup(tenant_id:str,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    assert_resource_access(actor,tenant_id)
    return setup_for(db,tenant_id)

@router.get('/organization-setup/{tenant_id}/readiness')
def setup_readiness(tenant_id:str,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    assert_resource_access(actor,tenant_id)
    setup=setup_for(db,tenant_id)
    gaps=missing(setup)
    issues=validation_issues(setup)
    tenant=db.get(Tenant,tenant_id)
    ready=not gaps and not issues
    return {
        'tenant_id':tenant_id,
        'status':setup.status,
        'version':setup.version,
        'tenant_status':tenant.status if tenant else None,
        'ready_for_submission':ready and setup.status in EDITABLE,
        'completed_required_fields':sum(len(x['required']) for x in SECTIONS.values())-len(gaps),
        'total_required_fields':sum(len(x['required']) for x in SECTIONS.values()),
        'missing_fields':gaps,
        'validation_issues':issues,
        'activation_blocked_until':'Organization setup APPROVED and separate tenant activation',
        'approval_role':'PLATFORM_OPS (DEMO ONLY; CLIENT DECISION PENDING)',
    }

@router.get('/organization-setup/{tenant_id}/submissions',response_model=list[OrganizationSetupSubmissionOut])
def list_submissions(tenant_id:str,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    assert_resource_access(actor,tenant_id)
    setup=setup_for(db,tenant_id)
    return db.scalars(
        select(OrganizationSetupSubmission)
        .where(OrganizationSetupSubmission.setup_id==setup.id)
        .order_by(OrganizationSetupSubmission.version.desc())
    ).all()

@router.put('/organization-setup/{tenant_id}/sections/{section_key}',response_model=OrganizationSetupOut)
def update_section(tenant_id:str,section_key:str,payload:SetupSectionIn,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    assert_resource_access(actor,tenant_id)
    setup=setup_for(db,tenant_id);require_draft(setup);check_version(setup,payload.expected_version)
    spec=SECTIONS.get(section_key)
    if spec is None:raise HTTPException(status_code=404,detail='Unknown collection section')
    extras=set(payload.data)-set(spec['fields'])
    if extras:raise HTTPException(status_code=422,detail='Unknown fields: '+', '.join(sorted(extras)))
    data=dict(setup.sections or {})
    group=dict(data.get(section_key,{}) or {})
    for key,value in payload.data.items():
        if key=='lob_codes':
            if not isinstance(value,list) or any(not isinstance(x,str) for x in value):
                raise HTTPException(status_code=422,detail='lob_codes must be a list of strings')
            value=[x.strip().upper() for x in value if x.strip()]
        elif not isinstance(value,str) or len(value)>500:
            raise HTTPException(status_code=422,detail=f'{key} must be text of at most 500 characters')
        if key=='organization_type' and value and value not in ORG_TYPES:
            raise HTTPException(status_code=422,detail='Organization type must be CARRIER_TPA or IA_FIRM')
        if key=='operating_model' and value and value not in OPERATING_MODELS:
            raise HTTPException(status_code=422,detail=f'operating_model must be one of: {", ".join(sorted(OPERATING_MODELS))}')
        if key=='primary_email' and value and not EMAIL_RE.match(value):
            raise HTTPException(status_code=422,detail='primary_email must be a valid email address')
        group[key]=value
    if section_key=='profile':
        orgtype=group.get('organization_type','')
        if orgtype:setup.organization_type=orgtype
        op_model=group.get('operating_model')
        if op_model:
            tenant=db.get(Tenant,tenant_id)
            if tenant and tenant.operating_model != op_model:
                # Keep tenant operating model aligned when edited during draft setup.
                tenant.operating_model=op_model
    data[section_key]=group
    setup.sections=data
    audit(db,actor,'organization.section.saved','organization_setup',setup.id,tenant_id,{'section':section_key,'field_keys':list(payload.data),'version':setup.version})
    save(db);db.refresh(setup);return setup

@router.put('/organization-setup/{tenant_id}/owner',response_model=OrganizationSetupOut)
def assign_owner(tenant_id:str,payload:SetupOwnerIn,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    assert_resource_access(actor,tenant_id)
    setup=setup_for(db,tenant_id);require_draft(setup);check_version(setup,payload.expected_version)
    owner=db.get(User,payload.responsible_user_id)
    if not owner or owner.tenant_id!=tenant_id or not owner.is_active:
        raise HTTPException(status_code=422,detail='Owner must be an active user in this tenant')
    setup.responsible_user_id=owner.id
    audit(db,actor,'organization.owner.assigned','organization_setup',setup.id,tenant_id,{'owner_id':owner.id})
    save(db);db.refresh(setup);return setup

@router.post('/organization-setup/{tenant_id}/submit',response_model=OrganizationSetupOut)
def submit_setup(tenant_id:str,payload:SetupSubmitIn,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    assert_resource_access(actor,tenant_id)
    setup=setup_for(db,tenant_id);require_draft(setup);check_version(setup,payload.expected_version)
    gaps=missing(setup)
    if gaps:raise HTTPException(status_code=409,detail={'error':'INCOMPLETE_SETUP','missing_fields':gaps})
    issues=validation_issues(setup)
    if issues:raise HTTPException(status_code=409,detail={'error':'INVALID_SETUP','validation_issues':issues})
    if not setup.responsible_user_id:
        raise HTTPException(status_code=409,detail={'error':'MISSING_RESPONSIBLE_ADMIN'})
    setup.version = (setup.version or 1) + 1
    snapshot = OrganizationSetupSubmission(
        setup_id=setup.id,
        tenant_id=tenant_id,
        version=setup.version,
        organization_type=setup.organization_type,
        sections_snapshot=copy.deepcopy(setup.sections or {}),
        submitted_by_id=actor.id,
        submit_reason=payload.reason,
    )
    db.add(snapshot)
    setup.status='IN_REVIEW';setup.submitted_by_id=actor.id;setup.review_note=''
    audit(db,actor,'organization.setup.submitted','organization_setup',setup.id,tenant_id,{
        'reason':payload.reason,'version':setup.version,'submission_pending':True,
    })
    save(db);db.refresh(setup);return setup

@router.post('/organization-setup/{tenant_id}/decision',response_model=OrganizationSetupOut)
def decide_setup(tenant_id:str,payload:SetupDecisionIn,db:Session=Depends(get_db),actor:User=Depends(require_platform)):
    setup=setup_for(db,tenant_id)
    if setup.status!='IN_REVIEW':raise HTTPException(status_code=409,detail='Setup must be IN_REVIEW')
    check_version(setup,payload.expected_version)
    if setup.submitted_by_id == actor.id:
        raise HTTPException(status_code=409,detail='Demo separation-of-duties: submitter cannot approve own setup')
    submission=latest_open_submission(db,setup)
    if payload.decision=='APPROVE':
        if missing(setup):raise HTTPException(status_code=409,detail='Incomplete setup cannot be approved')
        if validation_issues(setup):raise HTTPException(status_code=409,detail='Invalid setup cannot be approved')
        setup.status='APPROVED';setup.approved_by_id=actor.id
        # Approval does NOT activate the tenant — use POST /admin/tenants/{id}/activate.
    else:
        setup.status='CHANGES_REQUESTED';setup.approved_by_id=None
    setup.review_note=payload.note
    if submission:
        submission.decision=payload.decision
        submission.decided_by_id=actor.id
        submission.decision_note=payload.note
        submission.decided_at=utc_now()
    audit(db,actor,'organization.setup.reviewed','organization_setup',setup.id,tenant_id,{
        'decision':payload.decision,'note':payload.note,'version':setup.version,
        'submission_id':submission.id if submission else None,
        'tenant_remains_inactive_until_activation':True,
    })
    save(db);db.refresh(setup);return setup

@router.get('/organization-teams',response_model=list[OrganizationTeamOut])
def list_teams(tenant_id:str|None=None,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=permitted_tenant(actor,tenant_id)
    query=select(OrganizationTeam)
    if tid:query=query.where(OrganizationTeam.tenant_id==tid)
    return db.scalars(query.order_by(OrganizationTeam.name)).all()

@router.post('/organization-teams',response_model=OrganizationTeamOut,status_code=201)
def create_team(data:OrganizationTeamCreate,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=mutation_tenant(actor,data.tenant_id);ensure_tenant(db,tid)
    if data.parent_team_id:
        parent=db.get(OrganizationTeam,data.parent_team_id)
        if not parent or parent.tenant_id!=tid:raise HTTPException(status_code=422,detail='Parent team not in tenant')
    if data.manager_user_id:
        manager=db.get(User,data.manager_user_id)
        if not manager or manager.tenant_id!=tid or not manager.is_active:raise HTTPException(status_code=422,detail='Team manager not active in tenant')
    team=OrganizationTeam(tenant_id=tid,name=data.name,team_type=data.team_type,parent_team_id=data.parent_team_id,manager_user_id=data.manager_user_id)
    db.add(team);flush(db)
    audit(db,actor,'organization.team.created','organization_team',team.id,tid,{'name':team.name})
    save(db);db.refresh(team);return team

@router.get('/organization-teams/{team_id}/members')
def list_team_members(team_id:str,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    team=db.get(OrganizationTeam,team_id)
    if not team:raise HTTPException(status_code=404,detail='Team not found')
    assert_resource_access(actor,team.tenant_id)
    stmt=select(OrganizationTeamMember,User).join(User,User.id==OrganizationTeamMember.user_id).where(OrganizationTeamMember.team_id==team_id)
    return [{'id':m.id,'user_id':m.user_id,'name':u.name,'role_code':u.role_code,'is_active':u.is_active} for m,u in db.execute(stmt).all()]

@router.post('/organization-teams/{team_id}/members',status_code=201)
def add_team_member(team_id:str,data:OrganizationTeamMemberCreate,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    team=db.get(OrganizationTeam,team_id)
    if not team:raise HTTPException(status_code=404,detail='Team not found')
    assert_resource_access(actor,team.tenant_id)
    user=db.get(User,data.user_id)
    if not user or user.tenant_id!=team.tenant_id or not user.is_active:
        raise HTTPException(status_code=422,detail='Member must be an active user of the same tenant')
    membership=OrganizationTeamMember(tenant_id=team.tenant_id,team_id=team.id,user_id=user.id)
    db.add(membership);flush(db)
    audit(db,actor,'organization.team.member.added','organization_team',team.id,team.tenant_id,{'user_id':user.id})
    save(db)
    return {'id':membership.id,'team_id':team.id,'user_id':user.id,'tenant_id':team.tenant_id}

@router.delete('/organization-teams/{team_id}/members/{user_id}',status_code=204)
def remove_team_member(team_id:str,user_id:str,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    team=db.get(OrganizationTeam,team_id)
    if not team:raise HTTPException(status_code=404,detail='Team not found')
    assert_resource_access(actor,team.tenant_id)
    membership=db.scalar(select(OrganizationTeamMember).where(OrganizationTeamMember.team_id==team_id,OrganizationTeamMember.user_id==user_id))
    if not membership:raise HTTPException(status_code=404,detail='Membership not found')
    db.delete(membership)
    audit(db,actor,'organization.team.member.removed','organization_team',team.id,team.tenant_id,{'user_id':user_id})
    save(db)

@router.get('/workforce')
def list_workforce(tenant_id:str|None=None,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=permitted_tenant(actor,tenant_id)
    stmt=select(User,WorkforceStatus).outerjoin(WorkforceStatus,WorkforceStatus.user_id==User.id).where(User.tenant_id.is_not(None))
    if tid:stmt=stmt.where(User.tenant_id==tid)
    return [{'user_id':user.id,'tenant_id':user.tenant_id,'name':user.name,'email':user.email,
             'role_code':user.role_code,'status':(availability.status if availability else ('OFFBOARDED' if not user.is_active else 'AVAILABLE')),
             'login_active':user.is_active} for user,availability in db.execute(stmt.order_by(User.name)).all()]

@router.post('/workforce/{user_id}/status')
def change_workforce_status(user_id:str,data:WorkforceChangeIn,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    user=db.get(User,user_id)
    if not user:raise HTTPException(status_code=404,detail='User not found')
    assert_resource_access(actor,user.tenant_id)
    if not user.tenant_id or user.role_code=='PLATFORM_OPS':raise HTTPException(status_code=403,detail='Cannot change platform account')
    if user.id==actor.id and data.status=='OFFBOARDED':raise HTTPException(status_code=409,detail='Cannot offboard your own account')
    status=db.get(WorkforceStatus,user.id)
    previous=status.status if status else ('OFFBOARDED' if not user.is_active else 'AVAILABLE')
    if previous=='OFFBOARDED':raise HTTPException(status_code=409,detail='Offboarded account cannot be reactivated through this demo endpoint')
    if previous==data.status:raise HTTPException(status_code=409,detail='User already in this status')
    if not status:
        status=WorkforceStatus(user_id=user.id,tenant_id=user.tenant_id,status=data.status);db.add(status)
    else:status.status=data.status
    if data.status=='OFFBOARDED':user.is_active=False
    audit(db,actor,'workforce.status.changed','user',user.id,user.tenant_id,
          {'before':previous,'after':data.status,'reason':data.reason,'login_active':user.is_active})
    db.add(WorkforceLifecycleEvent(tenant_id=user.tenant_id,user_id=user.id,actor_id=actor.id,
                                   old_status=previous,new_status=data.status,reason=data.reason))
    save(db)
    workload=db.scalar(select(func.count()).select_from(Claim).where(Claim.desk_adjuster_id==user.id)) or 0
    return {'user_id':user.id,'old_status':previous,'new_status':data.status,
            'login_active':user.is_active,'assigned_demo_claims':workload,
            'reassignment_status':'REVIEW_REQUIRED' if workload and data.status!='AVAILABLE' else 'NOT_APPLICABLE',
            'note':'Demo does not reassign claims or update live dispatch queues'}

@router.get('/workforce/events')
def workforce_events(tenant_id:str|None=None,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=permitted_tenant(actor,tenant_id)
    stmt=select(WorkforceLifecycleEvent)
    if tid:stmt=stmt.where(WorkforceLifecycleEvent.tenant_id==tid)
    result=db.scalars(stmt.order_by(WorkforceLifecycleEvent.created_at.desc()).limit(100)).all()
    return [{'id':x.id,'tenant_id':x.tenant_id,'user_id':x.user_id,'old_status':x.old_status,
             'new_status':x.new_status,'reason':x.reason,'actor_id':x.actor_id,'created_at':x.created_at} for x in result]
