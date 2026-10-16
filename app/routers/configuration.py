"""Generic tenant configuration and demo AI governance routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AIUseCase, FeatureFlag, Integration, LineOfBusiness, User, WorkflowTemplate
from app.schemas import (AIUseCaseOut, AIUseCasePatch, FlagCreate, FlagPatch, FlagOut, WorkflowCreate, WorkflowPatch, WorkflowOut, LOBCreate, LOBOut, IntegrationOut, IntegrationCreate, IntegrationPatch)
from app.security import require_admin, permitted_tenant, mutation_tenant
from app.helpers import scoped_item, audit, flush, save, ensure_tenant

router = APIRouter(prefix='/admin', tags=['Admin: Configuration & Governance'])

def scoped_list(db, model, actor, tenant_id, limit, offset):
    tid = permitted_tenant(actor,tenant_id)
    stmt=select(model)
    if tid is not None:
        stmt=stmt.where(model.tenant_id == tid)
    return db.scalars(stmt.limit(limit).offset(offset)).all()

@router.get('/features', response_model=list[FlagOut])
def flags(tenant_id: str | None = None, limit:int=Query(50,ge=1,le=200), offset:int=Query(0,ge=0), db:Session=Depends(get_db), actor:User=Depends(require_admin)):
    return scoped_list(db,FeatureFlag,actor,tenant_id,limit,offset)

@router.post('/features', response_model=FlagOut, status_code=201)
def create_flag(data:FlagCreate, db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=mutation_tenant(actor,data.tenant_id)
    ensure_tenant(db,tid)
    item=FeatureFlag(tenant_id=tid, key=data.key, description=data.description, enabled=data.enabled)
    db.add(item);flush(db)
    audit(db,actor,'feature.created','feature',item.id,tid,{'key':item.key,'enabled':item.enabled,'reason':data.reason})
    save(db);db.refresh(item)
    return item

@router.patch('/features/{flag_id}', response_model=FlagOut)
def patch_flag(flag_id:str,data:FlagPatch,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    item=scoped_item(db,FeatureFlag,flag_id,actor)
    before=item.enabled
    item.enabled=data.enabled
    audit(db,actor,'feature.changed','feature',item.id,item.tenant_id,{'key':item.key,'before':before,'after':item.enabled,'reason':data.reason,'mode':'LOCAL_DEMO'})
    save(db);db.refresh(item)
    return item

@router.get('/workflows', response_model=list[WorkflowOut])
def workflows(tenant_id:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    return scoped_list(db,WorkflowTemplate,actor,tenant_id,limit,offset)

@router.post('/workflows', response_model=WorkflowOut,status_code=201)
def create_workflow(data:WorkflowCreate,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=mutation_tenant(actor,data.tenant_id);ensure_tenant(db,tid)
    item=WorkflowTemplate(**(data.model_dump(exclude={'tenant_id'}) | {'tenant_id':tid}))
    db.add(item);flush(db)
    audit(db,actor,'workflow.created','workflow',item.id,tid,{'key':item.key})
    save(db);db.refresh(item);return item

@router.patch('/workflows/{workflow_id}',response_model=WorkflowOut)
def patch_workflow(workflow_id:str,data:WorkflowPatch,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    item=scoped_item(db,WorkflowTemplate,workflow_id,actor)
    updates=data.model_dump(exclude_unset=True)
    before={k:getattr(item,k) for k in updates}
    for k,v in updates.items():setattr(item,k,v)
    audit(db,actor,'workflow.updated','workflow',item.id,item.tenant_id,{'before':before,'after':updates})
    save(db);db.refresh(item);return item

@router.get('/lines-of-business',response_model=list[LOBOut])
def lobs(tenant_id:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    return scoped_list(db,LineOfBusiness,actor,tenant_id,limit,offset)

@router.post('/lines-of-business',response_model=LOBOut,status_code=201)
def create_lob(data:LOBCreate,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=mutation_tenant(actor,data.tenant_id);ensure_tenant(db,tid)
    item=LineOfBusiness(tenant_id=tid,code=data.code,name=data.name,enabled=data.enabled)
    db.add(item);flush(db)
    audit(db,actor,'lob.created','lob',item.id,tid,{'code':item.code})
    save(db);db.refresh(item);return item

@router.get('/integrations',response_model=list[IntegrationOut])
def integrations(tenant_id:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    return scoped_list(db,Integration,actor,tenant_id,limit,offset)

@router.post('/integrations',response_model=IntegrationOut,status_code=201)
def create_integration(data:IntegrationCreate,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=mutation_tenant(actor,data.tenant_id);ensure_tenant(db,tid)
    item=Integration(tenant_id=tid,name=data.name,category=data.category,description=data.description,status=data.status)
    db.add(item);flush(db)
    audit(db,actor,'integration.created','integration',item.id,tid,{'name':item.name})
    save(db);db.refresh(item);return item

@router.patch('/integrations/{integration_id}',response_model=IntegrationOut)
def patch_integration(integration_id:str,data:IntegrationPatch,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    item=scoped_item(db,Integration,integration_id,actor)
    before=item.status
    item.status=data.status
    if data.description is not None:item.description=data.description
    audit(db,actor,'integration.status_changed','integration',item.id,item.tenant_id,{'before':before,'after':item.status,'demo_only':True})
    save(db);db.refresh(item);return item

@router.get('/ai/use-cases',response_model=list[AIUseCaseOut])
def ai_use_cases(tenant_id:str|None=None,limit:int=Query(50,ge=1,le=200),offset:int=Query(0,ge=0),db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    return scoped_list(db,AIUseCase,actor,tenant_id,limit,offset)

@router.patch('/ai/use-cases/{use_case_id}',response_model=AIUseCaseOut)
def patch_ai(use_case_id:str,data:AIUseCasePatch,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    item=scoped_item(db,AIUseCase,use_case_id,actor)
    before=item.enabled;item.enabled=data.enabled
    audit(db,actor,'ai.use_case_changed','ai_use_case',item.id,item.tenant_id,{'key':item.key,'before':before,'after':item.enabled,'reason':data.reason,'demo_only':True})
    save(db);db.refresh(item);return item

@router.get('/ai/kill-switches',response_model=list[FlagOut],tags=['Admin: AI Controls (Demo)'])
def ai_kill_switches(tenant_id:str|None=None,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    tid=permitted_tenant(actor,tenant_id)
    stmt=select(FeatureFlag).where(FeatureFlag.key.like('AI_%'))
    if tid is not None:stmt=stmt.where(FeatureFlag.tenant_id==tid)
    return db.scalars(stmt).all()

@router.patch('/ai/kill-switches/{flag_id}',response_model=FlagOut,tags=['Admin: AI Controls (Demo)'])
def patch_ai_kill_switch(flag_id:str,data:FlagPatch,db:Session=Depends(get_db),actor:User=Depends(require_admin)):
    item=scoped_item(db,FeatureFlag,flag_id,actor)
    if not item.key.startswith('AI_'):
        raise HTTPException(status_code=422,detail='Not an AI-related flag')
    before=item.enabled
    item.enabled=data.enabled
    audit(db,actor,'ai.kill_switch.changed','feature',item.id,item.tenant_id,{'key':item.key,'before':before,'after':item.enabled,'reason':data.reason,'mode':'LOCAL_DEMO_ONLY'})
    save(db);db.refresh(item)
    return item
