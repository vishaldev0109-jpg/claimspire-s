def test_health_and_anonymous_rejection(client):
    assert client.get('/health').json()['aws_required'] is False
    assert client.get('/api/v1/admin/tenants').status_code == 401
    assert client.post('/api/v1/auth/login',json={'email':'platform@claimspire.local','password':'wrong'}).status_code == 401

def test_admin_navigation_and_roles(client, platform_headers):
    roles=client.get('/api/v1/admin/roles',headers=platform_headers)
    assert roles.status_code==200
    assert len(roles.json())==16
    nav=client.get('/api/v1/admin/navigation',headers=platform_headers)
    assert nav.json()['surface']=='INTERNAL_ADMIN_DEMO'

def test_scoping(client,platform_headers,harbor_headers):
    all_tenants=client.get('/api/v1/admin/tenants',headers=platform_headers).json()
    assert len(all_tenants)==2
    own=client.get('/api/v1/admin/tenants',headers=harbor_headers).json()
    assert len(own)==1
    other_id=next(t['id'] for t in all_tenants if t['id']!=own[0]['id'])
    assert client.get(f'/api/v1/admin/tenants/{other_id}',headers=harbor_headers).status_code==403
    assert client.get('/api/v1/admin/claims',headers=harbor_headers,params={'tenant_id':other_id}).status_code==403
    assert len(client.get('/api/v1/admin/claims',headers=harbor_headers).json())==8
    assert len(client.get('/api/v1/admin/claims',headers=platform_headers).json())==16

def test_dashboard_overviews(client,harbor_headers):
    r=client.get('/api/v1/admin/dashboard/summary',headers=harbor_headers)
    assert r.status_code==200,r.text
    assert r.json()['claims']==8
    assert r.json()['qa_reviews']==2
    flow=client.get('/api/v1/admin/workflow-stages',headers=harbor_headers).json()['flow']
    assert len(flow)==8
    assert flow[0]['key']=='FNOL'
    assert len(client.get('/api/v1/admin/assignments',headers=harbor_headers).json())==3
    assert len(client.get('/api/v1/admin/qa-reviews',headers=harbor_headers).json())==2
    assert len(client.get('/api/v1/admin/financial-items',headers=harbor_headers).json())==2

def test_flag_update_is_audited(client,harbor_headers):
    flags=client.get('/api/v1/admin/features',headers=harbor_headers).json()
    flag=next(f for f in flags if f['key']=='AI_NBA_EXPLANATION')
    r=client.patch(f"/api/v1/admin/features/{flag['id']}",headers=harbor_headers,json={'enabled':True,'reason':'Test demo enable'})
    assert r.status_code==200,r.text
    assert r.json()['enabled'] is True
    history=client.get('/api/v1/admin/audit-events',headers=harbor_headers,params={'action':'feature.changed'})
    assert history.status_code==200
    assert any(e['detail']['key']=='AI_NBA_EXPLANATION' for e in history.json())
    bad=client.patch(f"/api/v1/admin/features/{flag['id']}",headers=harbor_headers,json={'enabled':False,'reason':'no'})
    assert bad.status_code==422

def test_non_admin_denied(client):
    r=client.post('/api/v1/auth/login',json={'email':'desk@harbor.local','password':'DemoAdmin123!'})
    assert r.status_code==200
    h={'Authorization':'Bearer '+r.json()['access_token']}
    assert client.get('/api/v1/admin/dashboard/summary',headers=h).status_code==403
    assert client.get('/api/v1/auth/me',headers=h).status_code==200

def test_tenant_admin_cannot_change_operating_model(client,harbor_headers):
    tenant_id=client.get('/api/v1/admin/tenants',headers=harbor_headers).json()[0]['id']
    r=client.patch(f'/api/v1/admin/tenants/{tenant_id}',headers=harbor_headers,json={'operating_model':'DESK_ONLY'})
    assert r.status_code==403

def test_user_create_and_update(client,harbor_headers):
    new_user=client.post('/api/v1/admin/users',headers=harbor_headers,json={'name':'Demo QA User','email':'new-qa@harbor.local','password':'MySecureDemo123!','role_code':'QA_REVIEWER'})
    assert new_user.status_code==201,new_user.text
    assert 'password_hash' not in new_user.json()
    uid=new_user.json()['id']
    r=client.patch('/api/v1/admin/users/'+uid,headers=harbor_headers,json={'is_active':False})
    assert r.status_code==200
    assert r.json()['is_active'] is False
    audit=client.get('/api/v1/admin/audit-events',headers=harbor_headers,params={'action':'user.updated'})
    assert audit.status_code==200
    assert len(audit.json())>=1

def test_workflow_and_readonly(client,harbor_headers):
    wf=client.get('/api/v1/admin/workflows',headers=harbor_headers)
    assert wf.status_code==200 and len(wf.json())==1
    assert client.post('/api/v1/admin/claims',headers=harbor_headers,json={}).status_code==405
    assert client.post('/api/v1/admin/qa-reviews',headers=harbor_headers,json={}).status_code==405

def test_ai_kill_switch_and_cross_tenant_guard(client,harbor_headers,platform_headers):
    own_flags=client.get('/api/v1/admin/ai/kill-switches',headers=harbor_headers)
    assert own_flags.status_code==200 and len(own_flags.json())==1
    all_flags=client.get('/api/v1/admin/ai/kill-switches',headers=platform_headers)
    assert len(all_flags.json())==2
    other=next(f for f in all_flags.json() if f['tenant_id']!=own_flags.json()[0]['tenant_id'])
    denied=client.patch(f"/api/v1/admin/ai/kill-switches/{other['id']}",headers=harbor_headers,json={'enabled':True,'reason':'Cross tenant attempt'})
    assert denied.status_code==403
    allowed=client.patch(f"/api/v1/admin/ai/kill-switches/{own_flags.json()[0]['id']}",headers=harbor_headers,json={'enabled':False,'reason':'Testing local kill switch'})
    assert allowed.status_code==200
    audit=client.get('/api/v1/admin/audit-events',headers=harbor_headers,params={'action':'ai.kill_switch.changed'}).json()
    assert len(audit)>=1

def test_duplicate_tenant_returns_conflict(client,platform_headers):
    r=client.post('/api/v1/admin/tenants',headers=platform_headers,json={'name':'Harbor Copy','slug':'harbor-mutual','operating_model':'HYBRID'})
    assert r.status_code==409,r.text

def test_demo_interface_is_served_without_auth(client):
    page = client.get('/demo')
    assert page.status_code == 200
    assert 'ClaimSpire' in page.text and 'LOCAL PROTOTYPE' in page.text
    assert client.get('/demo-assets/app.js').status_code == 200
    assert client.get('/demo-assets/styles.css').status_code == 200


def test_readiness_register_has_scope_boundaries(client, platform_headers):
    r = client.get('/api/v1/admin/implementation-readiness', headers=platform_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data['open_decisions']) >= 5
    assert any(i['classification']=='DEFERRED_BY_SOW' for i in data['capabilities'])
    assert client.get('/api/v1/admin/implementation-readiness').status_code == 401


def test_home_redirects_to_demo(client):
    assert client.get('/', follow_redirects=False).headers['location'] == '/demo'
    assert client.get('/').status_code == 200
    assert 'LOCAL PROTOTYPE' in client.get('/').text
    assert client.get('/health').json()['demo_ui'] is True
    assert client.get('/favicon.ico').status_code == 204

# Organization/workforce journey additions (v0.3 local demo, not client-approved permissions).
def test_organization_setup_catalog_and_scope(client, harbor_headers, platform_headers):
    catalog = client.get('/api/v1/admin/organization-setup/sections',headers=harbor_headers)
    assert catalog.status_code == 200 and len(catalog.json()['sections']) == 5
    assert catalog.json()['provisional'] is True
    all_setups=client.get('/api/v1/admin/organization-setup',headers=platform_headers).json()
    assert len(all_setups)==2
    own=client.get('/api/v1/admin/organization-setup',headers=harbor_headers).json()
    assert len(own)==1
    assert own[0]['organization_type']=='CARRIER_TPA'
    other_id=next(x['tenant_id'] for x in all_setups if x['tenant_id']!=own[0]['tenant_id'])
    assert client.get('/api/v1/admin/organization-setup/'+other_id,headers=harbor_headers).status_code==403
    assert client.put('/api/v1/admin/organization-setup/'+other_id+'/sections/profile',headers=harbor_headers,json={'data':{'legal_name':'Test'}}).status_code==403


def test_organization_collect_submit_review(client, harbor_headers, platform_headers):
    own=client.get('/api/v1/admin/organization-setup',headers=harbor_headers).json()[0]
    tid=own['tenant_id']
    first=client.get(f'/api/v1/admin/organization-setup/{tid}/readiness',headers=harbor_headers).json()
    assert first['ready_for_submission'] is False
    blocked=client.post(f'/api/v1/admin/organization-setup/{tid}/submit',headers=harbor_headers,json={'reason':'Initial submitted form'})
    assert blocked.status_code==409
    edits={
        'coverage':{'lob_codes':['PROPERTY','PERSONAL_AUTO'],'license_reference':'SAMPLE-NOT-VERIFIED'},
        'structure':{'structure_summary':'Carrier Claims Ops > Desk > Field'},
        'branding':{'display_name':'Harbor Mutual (DEMO)'},
    }
    for key,payload in edits.items():
        r=client.put(f'/api/v1/admin/organization-setup/{tid}/sections/{key}',headers=harbor_headers,json={'data':payload})
        assert r.status_code==200,r.text
    assert client.get(f'/api/v1/admin/organization-setup/{tid}/readiness',headers=harbor_headers).json()['ready_for_submission']
    submitted=client.post(f'/api/v1/admin/organization-setup/{tid}/submit',headers=harbor_headers,json={'reason':'Prepared draft for the demonstration'})
    assert submitted.status_code==200 and submitted.json()['status']=='IN_REVIEW'
    assert client.put(f'/api/v1/admin/organization-setup/{tid}/sections/branding',headers=harbor_headers,json={'data':{'display_name':'changed'}}).status_code==409
    assert client.post(f'/api/v1/admin/organization-setup/{tid}/decision',headers=harbor_headers,json={'decision':'APPROVE','note':'Looks good for the demo'}).status_code==403
    reviewed=client.post(f'/api/v1/admin/organization-setup/{tid}/decision',headers=platform_headers,json={'decision':'APPROVE','note':'Demo-only review accepted'})
    assert reviewed.status_code==200 and reviewed.json()['status']=='APPROVED'
    audits=client.get('/api/v1/admin/audit-events',headers=platform_headers,params={'action':'organization.setup.reviewed'}).json()
    assert any(x['entity_id']==own['id'] for x in audits)


def test_setup_provisional_approver_and_new_tenant_draft(client, platform_headers):
    r=client.post('/api/v1/admin/tenants',headers=platform_headers,json={'name':'New POC Carrier','slug':'new-poc-carrier','operating_model':'HYBRID'})
    assert r.status_code==201
    tid=r.json()['id']
    setup=client.get(f'/api/v1/admin/organization-setup/{tid}',headers=platform_headers)
    assert setup.status_code==200 and setup.json()['status']=='DRAFT'
    assert setup.json()['sections']=={}
    assert client.post(f'/api/v1/admin/organization-setup/{tid}/decision',headers=platform_headers,json={'decision':'APPROVE','note':'Trying to bypass setup'}).status_code==409


def test_workforce_availability_offboarding_and_events(client, harbor_headers, platform_headers):
    r=client.post('/api/v1/admin/users',headers=harbor_headers,json={'name':'Demo Field Inspect','email':'demo-field@harbor.local','password':'Demo123Password!','role_code':'FIELD_ADJUSTER'})
    assert r.status_code==201,r.text
    uid=r.json()['id']
    url=f'/api/v1/admin/workforce/{uid}/status'
    unavailable=client.post(url,headers=harbor_headers,json={'status':'UNAVAILABLE','reason':'Scheduled leave from demo workforce'})
    assert unavailable.status_code==200 and unavailable.json()['login_active'] is True
    assert unavailable.json()['new_status']=='UNAVAILABLE'
    returned=client.post(url,headers=harbor_headers,json={'status':'AVAILABLE','reason':'Returned from scheduled leave'})
    assert returned.status_code==200 and returned.json()['new_status']=='AVAILABLE'
    offboard=client.post(url,headers=harbor_headers,json={'status':'OFFBOARDED','reason':'User left the demo organization'})
    assert offboard.status_code==200 and offboard.json()['login_active'] is False
    again=client.post(url,headers=harbor_headers,json={'status':'AVAILABLE','reason':'Trying unsupported reactivation'})
    assert again.status_code==409
    assert client.post('/api/v1/auth/login',json={'email':'demo-field@harbor.local','password':'Demo123Password!'}).status_code==401
    events=client.get('/api/v1/admin/workforce/events',headers=harbor_headers).json()
    assert len([e for e in events if e['user_id']==uid])==3
    own_tenant=client.get('/api/v1/admin/tenants',headers=harbor_headers).json()[0]['id']
    other_id=next(t['id'] for t in client.get('/api/v1/admin/tenants',headers=platform_headers).json() if t['id']!=own_tenant)
    assert client.get('/api/v1/admin/workforce',headers=harbor_headers,params={'tenant_id':other_id}).status_code==403


def test_team_hierarchy_and_tenant_constraint(client, harbor_headers, platform_headers):
    tid=client.get('/api/v1/admin/tenants',headers=harbor_headers).json()[0]['id']
    teams=client.get('/api/v1/admin/organization-teams',headers=harbor_headers).json()
    assert len(teams)>=2
    root=client.post('/api/v1/admin/organization-teams',headers=harbor_headers,json={'tenant_id':tid,'name':'Demo Northeast Desk','team_type':'CLAIMS_OPERATIONS'})
    assert root.status_code==201,root.text
    child=client.post('/api/v1/admin/organization-teams',headers=harbor_headers,json={'tenant_id':tid,'name':'Demo Northeast QA','team_type':'QA','parent_team_id':root.json()['id']})
    assert child.status_code==201 and child.json()['parent_team_id']==root.json()['id']
    other=next(t for t in client.get('/api/v1/admin/organization-teams',headers=platform_headers).json() if t['tenant_id']!=tid)
    denied=client.post('/api/v1/admin/organization-teams',headers=harbor_headers,json={'tenant_id':tid,'name':'Bad Other Tenant Parent','parent_team_id':other['id']})
    assert denied.status_code==422


def test_team_membership_and_workload_review_flag(client, harbor_headers, platform_headers):
    tenant_id=client.get('/api/v1/admin/tenants',headers=harbor_headers).json()[0]['id']
    team=next(x for x in client.get('/api/v1/admin/organization-teams',headers=harbor_headers).json() if x['tenant_id']==tenant_id)
    desk=next(x for x in client.get('/api/v1/admin/users',headers=harbor_headers).json() if x['role_code']=='DESK_ADJUSTER')
    link=client.post(f"/api/v1/admin/organization-teams/{team['id']}/members",headers=harbor_headers,json={'user_id':desk['id']})
    assert link.status_code==201,link.text
    members=client.get(f"/api/v1/admin/organization-teams/{team['id']}/members",headers=harbor_headers).json()
    assert any(x['user_id']==desk['id'] for x in members)
    assert client.post(f"/api/v1/admin/organization-teams/{team['id']}/members",headers=harbor_headers,json={'user_id':desk['id']}).status_code==409
    other=next(t for t in client.get('/api/v1/admin/organization-teams',headers=platform_headers).json() if t['tenant_id']!=tenant_id)
    assert client.get(f"/api/v1/admin/organization-teams/{other['id']}/members",headers=harbor_headers).status_code==403
    change=client.post(f"/api/v1/admin/workforce/{desk['id']}/status",headers=harbor_headers,json={'status':'UNAVAILABLE','reason':'Temporary leave requires coverage review'})
    assert change.status_code==200 and change.json()['reassignment_status']=='REVIEW_REQUIRED'
    assert change.json()['assigned_demo_claims']>0
    assert client.delete(f"/api/v1/admin/organization-teams/{team['id']}/members/{desk['id']}",headers=harbor_headers).status_code==204
    assert client.get(f"/api/v1/admin/organization-teams/{team['id']}/members",headers=harbor_headers).json()==[]
