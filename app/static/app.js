/* ClaimSpire self-contained ADMIN DEMO. Only synthetic local records; not production controls. */
const BASE = '/api/v1';
const state = {token:sessionStorage.getItem('claimspire_demo_token')||'', user:null, tenants:[], tenant:'', section:'overview', roles:[], dialogAction:null, navigation:[]};
const NAV = [
 ['overview','◫','Overview','Cross-surface operational summary'],
 ['tenants','▣','Tenants','Organization settings and operating models'],
 ['onboarding','◈','Organization Setup','Carrier/TPA or IA onboarding and review'],
 ['workforce','♧','Workforce Lifecycle','Teams, user availability and offboarding'],
 ['users','♙','Users & Personas','People, access and 16 canonical roles'],
 ['workflow','☷','Workflow Setup','High-level claim lifecycle templates'],
 ['claims','▤','Claims Overview','Read-only claim snapshots'],
 ['dispatch','↗','Dispatch Monitoring','Read-only assignment status'],
 ['qa','✓','QA Monitoring','Read-only inspection package checks'],
 ['finance','◇','Finance Monitoring','Read-only operational financial summary'],
 ['controls','⚙','Features & AI','Local demo switches and AI use cases'],
 ['integrations','⌁','Integrations','Connection inventory and status'],
 ['readiness','◎','Delivery Readiness','Confirmed scope versus open decisions'],
 ['audit','◷','Audit Trail','Change history and accountability'],
];
const $=id=>document.getElementById(id);
const escapeHtml=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const E=escapeHtml;
const human=s=>String(s??'').replaceAll('_',' ').replace(/\b\w/g,m=>m.toUpperCase());
const clip=s=>String(s??'').length>48?String(s).slice(0,45)+'...':String(s??'');
const yesno=s=>s?'<span class="pill">Enabled</span>':'<span class="pill off">Disabled</span>';
const badge=s=>{const t=String(s??'');const l=t.toLowerCase();const kind=/passed|active|connected|accepted|exported|approved|completed/.test(l)?'teal':/pending|needs|hold|correction|blocked/.test(l)?'amber':/fail|error|denied/.test(l)?'red':'gray';return `<span class="tag ${kind}">${E(human(t))}</span>`};
function notification(message,error=false){$('message').innerHTML=`<div class="toast ${error?'error-toast':''}">${E(message)}</div>`;setTimeout(()=>{if($('message').textContent===message)$('message').innerHTML=''},5000)}
async function api(path,opts={}){
 const headers={'Content-Type':'application/json',...(state.token?{'Authorization':`Bearer ${state.token}`}:{})};
 const res=await fetch(BASE+path,{...opts,headers:{...headers,...(opts.headers||{})}});
 const body=await res.json().catch(()=>({}));
 if(!res.ok){let msg=body.detail||body.message||`HTTP ${res.status}`;if(Array.isArray(msg))msg=msg.map(x=>x.msg).join('; ');else if(msg&&typeof msg==='object')msg=msg.missing_fields?'Missing setup details: '+msg.missing_fields.join(', '):(msg.error||JSON.stringify(msg));throw new Error(String(msg));}
 return body;
}
function scoped(path){if(!state.tenant)return path;return path+(path.includes('?')?'&':'?')+'tenant_id='+encodeURIComponent(state.tenant)}
function tenantName(id){if(!id)return 'Platform-wide';return (state.tenants.find(t=>t.id===id)||{}).name||String(id).slice(0,8)}
function panel(title,body,meta='',extra=''){return `<section class="panel"><div class="panel-header"><div><h2>${E(title)}</h2>${meta?`<p>${E(meta)}</p>`:''}</div>${extra}</div>${body}</section>`}
function stat(label,value,icon,info='Synthetic demo data'){return `<div class="stat-card"><div class="stat-icon">${icon}</div><span class="stat-label">${E(label)}</span><strong>${E(value)}</strong><small>${E(info)}</small></div>`}
function table(headers,rows){if(!rows.length)return '<div class="empty">No synthetic records available for the selected tenant.</div>';return `<div class="table-scroll"><table class="table"><thead><tr>${headers.map(h=>`<th>${E(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`}
function niceDate(s){if(!s)return '—';const d=new Date(s);return Number.isNaN(d.getTime())?String(s):d.toLocaleString(undefined,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}
function cardText(title,body){return `<div class="info-card"><h3>${E(title)}</h3><p>${E(body)}</p></div>`}
function loading(){return '<div class="panel"><div class="empty">Loading local demonstration data…</div></div>'}
function actionButton(label,action,id='',variant='subtle'){return `<button class="btn small ${variant==='primary'?'primary':'subtle'}" data-action="${E(action)}" data-id="${E(id)}">${E(label)}</button>`}
function setHeader(title,sub,actions=''){$('page-title').textContent=title;$('page-subtitle').textContent=sub;$('crumb-current').textContent=title;$('head-actions').innerHTML=actions}
async function initialize(){
 try{state.user=await api('/auth/me');if(!['PLATFORM_OPS','TENANT_IT_ADMIN'].includes(state.user.role_code))throw Error('This demo account has no Admin panel access');state.tenants=await api('/admin/tenants');
  if(state.user.role_code!=='PLATFORM_OPS'){state.tenant=state.user.tenant_id||'';}
  $('login-overlay').hidden=true;$('app').hidden=false;$('role-chip').textContent=human(state.user.role_code);renderNav();renderTenantFilter();await navigate('overview');
 }catch(err){state.token='';sessionStorage.removeItem('claimspire_demo_token');$('login-overlay').hidden=false;$('app').hidden=true;$('login-error').textContent=err.message}
}
function renderNav(){ $('nav').innerHTML=NAV.map(([key,ico,title])=>`<button class="nav-item ${state.section===key?'active':''}" data-section="${key}"><span class="nav-icon">${ico}</span>${E(title)}</button>`).join(''); }
function renderTenantFilter(){ const el=$('tenant-filter');if(state.user.role_code==='PLATFORM_OPS'){el.disabled=false;el.innerHTML='<option value="">All demo tenants</option>'+state.tenants.map(t=>`<option value="${E(t.id)}">${E(t.name.replace(' (DEMO)',''))}</option>`).join('');el.value=state.tenant;}else{el.disabled=true;el.innerHTML=`<option>${E(tenantName(state.user.tenant_id))}</option>`;}}
async function navigate(section){state.section=section;renderNav();let nav=NAV.find(x=>x[0]===section);setHeader(nav[2],nav[3]);$('content-area').innerHTML=loading();try{const map={overview:overview,tenants:tenants,onboarding:onboarding,workforce:workforce,users:users,workflow:workflow,claims:claims,dispatch:dispatch,qa:qa,finance:finance,controls:controls,integrations:integrations,readiness:readiness,audit:audit};await map[section]();}catch(err){$('content-area').innerHTML=panel('Unable to load this section',`<p class="error">${E(err.message)}</p>`);}}
async function overview(){
 const [stats,flow,auditRows,info]=await Promise.all([api(scoped('/admin/dashboard/summary')),api(scoped('/admin/workflow-stages')),api(scoped('/admin/audit-events')),api('/admin/implementation-readiness')]);
 let counts=Object.entries(stats.claim_statuses||{});const max=Math.max(...counts.map(([,n])=>n),1);
 const bars=counts.map(([label,n])=>`<div class="bar-row"><label>${E(human(label))}</label><div class="kpi-bar"><div class="kpi-bar-fill" style="width:${Math.round(100*n/max)}%"></div></div><b>${n}</b></div>`).join('');
 $('content-area').innerHTML=`<div class="stat-grid">${stat('Active demo tenants',stats.tenant_count,'▣')}${stat('Total claim records',stats.claims,'▤')}${stat('Field assignments',stats.assignments,'↗')}${stat('QA reviews',stats.qa_reviews,'✓')}</div>`+
 `<div class="panels-grid">${panel('Claim lifecycle distribution',bars||'<div class="empty">No claims</div>','Synthetic records by high-level stage')}${panel('System setup snapshot',`<div class="info-grid">${cardText('User profiles',`${stats.users} users`)}${cardText('Configured features',`${stats.configured_features} flags`)}${cardText('Financial items',`${stats.financial_items} records`)}${cardText('Integrations',`${stats.integrations} demo entries`)}</div>`,'Illustrative configuration counters')}</div>`+
 panel('Claim journey',`<div class="stage-grid">${flow.flow.map(s=>`<div class="stage-step"><b>${E(s.name)}</b><small>${E(s.main_persona)}</small><div class="stage-count">${s.demo_claim_count}</div></div>`).join('')}</div>`,'Desk-only cases may bypass field inspection. Specialist tracks can run in parallel.',`<span class="tag">READ-ONLY</span>`)+
 `<div class="panels-grid">${panel('Recent changes',table(['Action','Target','When'],auditRows.slice(0,5).map(x=>[E(x.action),E(x.entity_type),E(niceDate(x.created_at))])),'Local append-only demo events')}${panel('Scope checkpoint',`<p class="muted" style="font-size:12px;margin-bottom:14px">${info.open_decisions.length} open design/governance questions are documented. These do not prevent the local demonstration.</p><div class="action-row">${actionButton('Review delivery readiness','goto','readiness','primary')}</div><div class="hint">Signed Phase 1 internal Admin focus: Platform Ops AI controls and governance. Other demo modules are illustrative.</div>`,'SOW-aligned production planning')}</div>`;
}
async function tenants(){
 const rows=state.tenant?state.tenants.filter(x=>x.id===state.tenant):state.tenants;
 setHeader('Tenants','Organizations and simplified operating-model settings',state.user.role_code==='PLATFORM_OPS'?actionButton('+ Add demo tenant','new-tenant','','primary'):'');
 $('content-area').innerHTML=panel('Tenant directory',table(['Organization','Slug','Operating model','Status','Action'],rows.map(t=>[`<strong>${E(t.name)}</strong><small>${E(t.id)}</small>`,E(t.slug),badge(t.operating_model),badge(t.status),actionButton('Edit','edit-tenant',t.id)])),'Phase 1: managed initial tenant activation; full self-service administration deferred.')+
 `<div class="callout"><b>Source vs prototype</b><p>Creating additional tenants from this screen is a mock demonstration feature; it is not a committed production tenant onboarding interface.</p></div>`;
}

// Organization onboarding demonstrates a guided lifecycle, not approved future-tenant self service.
const SETUP_STEPS = ['Identify organization', 'Collect details', 'Configure structure', 'Review', 'Approve'];
function setupSectionInput(section, current={}){
 const labels={legal_name:'Legal organization name',organization_type:'Organization type',operating_model:'Operating model',primary_email:'Primary email',phone:'Phone (optional)',street_address:'Office / mailing address',lob_codes:'LOB codes (comma-separated)',license_reference:'License / credential reference',structure_summary:'Organization and team structure',team_contact:'Structure owner (optional)',display_name:'Brand display name',logo_reference:'Logo URL/reference (optional)'};
 const choices={organization_type:[{value:'CARRIER_TPA',label:'Carrier / TPA'},{value:'IA_FIRM',label:'IA / Inspection Firm'}],operating_model:[{value:'HYBRID',label:'Hybrid'},{value:'FIELD',label:'Field / IA'},{value:'DESK_ONLY',label:'Desk only'},{value:'CAT',label:'CAT'}]};
 return section.fields.map(k=>{
   const value=Array.isArray(current[k])?current[k].join(', '):(current[k]??'');
   const required=section.required.includes(k);
   if(choices[k])return `<div class="field"><label for="field-${k}">${E(labels[k])}</label><select name="${E(k)}" id="field-${E(k)}">${choices[k].map(o=>`<option value="${E(o.value)}" ${o.value===value?'selected':''}>${E(o.label)}</option>`).join('')}</select></div>`;
   return `<div class="field"><label for="field-${E(k)}">${E(labels[k]||k)}${required?' *':''}</label><input id="field-${E(k)}" name="${E(k)}" type="text" value="${E(value)}" ${required?'required':''} maxlength="500"></div>`;
 }).join('');
}
async function onboarding(){
 const [setups,catalogue]=await Promise.all([api(scoped('/admin/organization-setup')),api('/admin/organization-setup/sections')]);
 state.setupCatalog=catalogue;state.setups=setups;
 const content=[];
 for(const setup of setups){
   const ready=await api('/admin/organization-setup/'+setup.tenant_id+'/readiness');
   const isEditable=['DRAFT','CHANGES_REQUESTED'].includes(setup.status);
   const progress=Math.round(ready.completed_required_fields/ready.total_required_fields*100);
   let item=`<div class="onboard-head"><div><div class="eyebrow">${E(setup.organization_type==='IA_FIRM'?'IA / INSPECTION FIRM':'CARRIER / TPA')}</div><h3>${E(tenantName(setup.tenant_id))}</h3><p class="muted">Responsible admin: ${E(setup.responsible_user_id?.slice(0,8)||'Not selected')} · Status ${E(human(setup.status))}</p></div>${badge(setup.status)}</div>`;
   item+=`<div class="progress-track"><div class="progress-fill" style="width:${progress}%"></div></div><p class="muted mini-margin">${ready.completed_required_fields}/${ready.total_required_fields} required fields complete · ${ready.missing_fields.length} missing</p>`;
   item+=`<div class="setup-grid">${catalogue.sections.map(section=>{
     const filled=(setup.sections||{})[section.key]||{};
     const gaps=section.required.filter(name=>filled[name]===undefined||filled[name]===''||(Array.isArray(filled[name])&&!filled[name].length));
     return `<div class="setup-card"><div class="labelrow"><b>${E(section.label)}</b>${gaps.length?badge('PENDING'):badge('READY')}</div><p>${E(section.fields.map(f=>f+': '+(Array.isArray(filled[f])?filled[f].join(', '):(filled[f]||'—'))).join(' · '))}</p>${isEditable?actionButton('Edit details','setup-edit',setup.tenant_id+'|'+section.key):''}</div>`;
   }).join('')}</div>`;
   item+=`<div class="action-row" style="margin-top:14px">${isEditable?actionButton('Assign setup owner','setup-owner',setup.tenant_id):''}${isEditable?actionButton('Submit for review','setup-submit',setup.tenant_id,'primary'):''}${setup.status==='IN_REVIEW'&&state.user.role_code==='PLATFORM_OPS'?actionButton('Approve setup','setup-approve',setup.tenant_id,'primary')+actionButton('Return for changes','setup-return',setup.tenant_id):''}</div>`;
   if(ready.missing_fields.length)item+=`<div class="hint"><strong>Pending details:</strong> ${E(ready.missing_fields.join(', '))}</div>`;
   if(setup.review_note)item+=`<div class="hint info-blue">Reviewer note: ${E(setup.review_note)}</div>`;
   content.push(panel('Organization setup journey',item, 'Five provisional collection groups. Setup approval is local and does not provision a production tenant.'));
 }
 setHeader('Organization Setup','Guided collection, readiness, reviewer decision and organization structure');
 $('content-area').innerHTML=`<div class="callout"><b>From Pre-Phase I of the FigJam swimlane</b><p>Establish operating model → users and permissions → teams/queues → controls → governance. This local page adds a proposed five-section collection form and simulated review. The exact five named collection flows and final approver remain pending client/design confirmation.</p></div>`+content.join('');
}
async function workforce(){
 const [people, teams, events]=await Promise.all([api(scoped('/admin/workforce')),api(scoped('/admin/organization-teams')),api(scoped('/admin/workforce/events'))]);
 state.workforce=people;
 setHeader('Workforce Lifecycle','Team structure, availability and staff exit scenarios',actionButton('+ Add team','new-team','','primary'));
 $('content-area').innerHTML=`<div class="callout"><b>Onboarding, availability and offboarding</b><p>Creating user profiles uses the Users & Personas section. This workflow records when a user becomes unavailable or leaves. Temporary unavailability does not revoke login access in the demo; offboarding does. Existing work is not automatically reassigned.</p></div>`+
 panel('Organization teams',table(['Team','Category','Parent','Status','Members'],teams.map(t=>[`<strong>${E(t.name)}</strong>`,E(human(t.team_type)),E(t.parent_team_id?.slice(0,8)||'Root'),badge(t.status),actionButton('Manage members','team-members',t.id)])),'Simplified hierarchy for the organization; routing queues remain unimplemented.')+
 panel('Users and workforce status',table(['User','Persona','Tenant','Availability / Account','Action'],people.map(u=>[`<strong>${E(u.name)}</strong><small>${E(u.email)}</small>`,E(human(u.role_code)),E(tenantName(u.tenant_id)),`${badge(u.status)} <small>Login: ${u.login_active?'active':'disabled'}</small>`,u.status==='OFFBOARDED'?'Offboarded':actionButton('Change status','workforce-change',u.user_id)])),'Offboarding flags existing work for review rather than pretending to reassign live cases.')+
 panel('Recent workforce lifecycle events',table(['User','Transition','Reason','When'],events.map(e=>[`<strong>${E(people.find(p=>p.user_id===e.user_id)?.name||e.user_id.slice(0,8))}</strong>`,E(e.old_status+' → '+e.new_status),E(e.reason),E(niceDate(e.created_at))])),'Events are local demo history and contain no real employee information.');
}
async function users(){
 const [records,roles]=await Promise.all([api(scoped('/admin/users')),api('/admin/roles')]);state.roles=roles;
 setHeader('Users & Personas','Local role assignment and canonical persona catalogue',actionButton('+ Add demo user','new-user','','primary'));
 const rows=records.map(u=>[`<strong>${E(u.name)}</strong><small>${E(u.email)}</small>`,E(human(u.role_code)),E(tenantName(u.tenant_id)),u.is_active?badge('ACTIVE'):badge('INACTIVE'),u.role_code==='PLATFORM_OPS'?'Protected demo account':actionButton('Edit','edit-user',u.id)]);
 $('content-area').innerHTML=panel('User accounts',table(['User','Demo role','Organization','Status','Action'],rows),'Only PLATFORM_OPS and TENANT_IT_ADMIN roles can sign into this demo Admin UI.')+
 panel('16 canonical ClaimSpire personas',table(['Persona','Purpose','Primary surface'],roles.map(r=>[`<strong>${E(r.name)}</strong><small>${E(r.code)}</small>`,E(r.purpose),badge(r.primary_surface)])),'These are business personas, not an approved fine-grained RBAC matrix.');
}
async function workflow(){
 const [flows,template,lobs]=await Promise.all([api(scoped('/admin/workflow-stages')),api(scoped('/admin/workflows')),api(scoped('/admin/lines-of-business'))]);
 $('content-area').innerHTML=panel('Claims operating journey',`<div class="stage-grid">${flows.flow.map((s,i)=>`<div class="stage-step"><span class="tag">${String(i+1).padStart(2,'0')}</span><b style="margin-top:12px">${E(s.name)}</b><small>${E(s.main_persona)} · ${E(s.surface)}</small></div>`).join('')}</div>`,'High-level steps, not a full process engine; field/QA may be conditional.')+
 `<div class="two-col">${panel('Configured workflow templates',template.map(t=>`<div class="list-row"><div class="labelrow"><strong>${E(t.name)}</strong>${badge(t.active?'ACTIVE':'INACTIVE')}</div><p>${E(t.description)}</p><p><b>Stages:</b> ${E(t.stages.join(' → '))}</p></div>`).join('')||'<div class="empty">No templates</div>','Read-only high-level templates in this UI')}${panel('Lines of business',table(['Code','Name','Status'],lobs.map(l=>[E(l.code),E(l.name),badge(l.enabled?'ACTIVE':'INACTIVE')])),'Illustrative LOB setup')}</div>`;
}
async function claims(){const items=await api(scoped('/admin/claims'));$('content-area').innerHTML=panel('Claims snapshot',table(['Claim','Claimant / Location','LOB','Stage','Severity'],items.map(x=>[`<strong>${E(x.claim_number)}</strong>`,`<strong>${E(x.claimant_name)}</strong><small>${E(x.location)}</small>`,E(human(x.lob_code)),badge(x.status),badge(x.severity)])),'Synthetic read-only records; claim actions belong to Claim Core / Web App.')}
async function dispatch(){const items=await api(scoped('/admin/assignments'));$('content-area').innerHTML=panel('Field assignments',table(['Assignment','Assignee','Type','Status','When'],items.map(x=>[`<strong>${E(x.id.slice(0,8))}</strong><small>Claim: ${E(x.claim_id.slice(0,8))}</small>`,E(x.assignee_name),E(x.assignment_type),badge(x.status),E(niceDate(x.created_at))])),'Read-only assignment monitor. Eligibility/reassignment rules are not simulated.')}
async function qa(){const items=await api(scoped('/admin/qa-reviews'));$('content-area').innerHTML=panel('Inspection package QA',table(['Package','Claim','Result','Review notes'],items.map(x=>[`<strong>${E(x.package_ref)}</strong>`,E(x.claim_id.slice(0,8)),badge(x.status),E(x.notes)])),'Read-only synthetic QA. Phase 1 dedicated QA depth is not settled.')}
async function finance(){const items=await api(scoped('/admin/financial-items'));$('content-area').innerHTML=panel('Finance operation overview',table(['Claim','Entry type','Illustrative amount','Status'],items.map(x=>[E(x.claim_id.slice(0,8)),E(human(x.item_type)),`$${Number(x.amount).toLocaleString(undefined,{minimumFractionDigits:2})}`,badge(x.status)])),'Demo values only. No financial approvals, payment execution or accounting integration.')}
async function controls(){
 const [flags,ai]=await Promise.all([api(scoped('/admin/features')),api(scoped('/admin/ai/use-cases'))]);
 const flagRows=flags.map(x=>[`<strong>${E(x.key)}</strong><small>${E(x.description)}</small>`,E(tenantName(x.tenant_id)),yesno(x.enabled),actionButton(x.enabled?'Disable':'Enable','toggle-flag',x.id)]);
 const aiRows=ai.map(x=>[`<strong>${E(x.name)}</strong><small>${E(x.key)}</small>`,E(x.mode),yesno(x.enabled),actionButton(x.enabled?'Disable':'Enable','toggle-ai',x.id)]);
 state.flags=flags;state.ai=ai;
 $('content-area').innerHTML=`<div class="callout"><b>Local configuration simulation</b><p>Switches update demo database state and create an audit event. They do NOT operate real AI models, Bedrock services, client infrastructure, or production claim workflows.</p></div>`+
 panel('Capability toggles',table(['Flag','Tenant','Local state','Action'],flagRows),'Requires a reason to change; not connected to a runtime rules engine.')+
 panel('AI Use Case Register (demo)',table(['Use case','Mode','Local state','Action'],aiRows),'The signed Phase 1 Internal Admin UI includes AI governance and controlled use-case configuration.');
}
async function integrations(){const data=await api(scoped('/admin/integrations'));$('content-area').innerHTML=panel('Integration inventory',table(['Integration','Type','Demo status','Comment'],data.map(x=>[`<strong>${E(x.name)}</strong>`,E(x.category),badge(x.status),E(x.description)])),'All statuses are illustrative; nothing contacts outside services.');}
async function readiness(){
 const x=await api('/admin/implementation-readiness');
 const grouped={SOW_PHASE1_ADMIN:'Directly in signed Phase 1 Internal Admin scope',SOW_PHASE1_FOUNDATION:'Required Phase 1 foundation',SOW_PHASE1_MANAGED:'Managed initial tenant setup',DEMO_PROPOSAL:'Illustrative demonstration proposal',DEFERRED_BY_SOW:'Not included in signed Phase 1'};
 $('content-area').innerHTML=`<div class="callout"><b>Lead-developer delivery strategy</b><p>Deliver a thin working demo now. Freeze production UI/API contracts only after scope and RBAC approval. Continue schema, DTO, tests and adapter work independently of unanswered client decisions.</p></div>`+
 panel('Scope classification',table(['Capability','Source classification','Prototype state'],x.capabilities.map(i=>[`<strong>${E(i.module)}</strong><small>${E(i.why)}</small>`,E(grouped[i.classification]||human(i.classification)),badge(i.implementation)])),'Do not present this demo inventory as a signed feature list.')+
 panel('Decisions to resolve',table(['ID / Question','Decision owner','Impact','What can start now'],x.open_decisions.map(i=>[`<strong>${E(i.id)} · ${E(i.topic)}</strong><small>${E(i.needs)}</small>`,E(i.owner),badge(i.priority),E(i.can_build_now)])),'These are proposed review items, not evidence of current client sign-off.');
}
async function audit(){const data=await api(scoped('/admin/audit-events'));$('content-area').innerHTML=panel('Administrative action history',table(['Action / Subject','Entity','Tenant','Timestamp','Detail'],data.map(x=>[`<strong>${E(x.action)}</strong><small>${E(x.actor_id?.slice(0,8)||'System')}</small>`,E(x.entity_type),E(tenantName(x.tenant_id)),E(niceDate(x.created_at)),`<small>${E(clip(JSON.stringify(x.detail)))}</small>`])),'Local append-only demo events, not a tamper-evident production audit ledger.');}
function field(name,label,type='text',value='',options=null){let control;if(options){control=`<select id="field-${E(name)}" name="${E(name)}">${options.map(x=>`<option value="${E(x.value)}" ${String(x.value)===String(value)?'selected':''}>${E(x.label)}</option>`).join('')}</select>`}else control=`<input id="field-${E(name)}" name="${E(name)}" type="${E(type)}" value="${E(value)}" ${type==='password'?'autocomplete="new-password"':''} required>`;return `<div class="field"><label for="field-${E(name)}">${E(label)}</label>${control}</div>`}
function openDialog(title,description,fields,run){$('dialog-title').textContent=title;$('dialog-description').textContent=description;$('dialog-fields').innerHTML=fields;$('dialog-error').textContent='';state.dialogAction=run;$('edit-dialog').showModal()}
function canCreateTenant(){return state.user?.role_code==='PLATFORM_OPS'}
function selectedTenant(){return state.tenant||state.user.tenant_id||state.tenants[0]?.id}
function selectOptions(data,mapper){return data.map(mapper)}
async function performAction(action,id){
 const useTenant=selectedTenant();
 if(action==='goto'){return navigate(id)}

 if(action==='setup-edit'){
   const [tenantId,secKey]=id.split('|');const setup=state.setups.find(s=>s.tenant_id===tenantId);const sec=state.setupCatalog.sections.find(s=>s.key===secKey);
   if(!setup||!sec)throw Error('Setup section missing');
   return openDialog('Edit · '+sec.label,'Five-section draft collection model; these are provisional fields for the demonstration.',setupSectionInput(sec,(setup.sections||{})[secKey]||{}),async v=>{
     if('lob_codes' in v)v.lob_codes=v.lob_codes.split(',').map(x=>x.trim()).filter(Boolean);
     await api('/admin/organization-setup/'+tenantId+'/sections/'+secKey,{method:'PUT',body:JSON.stringify({data:v})});
   });
 }
 if(action==='setup-owner'){
   const people=await api('/admin/users?tenant_id='+encodeURIComponent(id));
   const options=people.filter(x=>x.is_active&&x.role_code!=='PLATFORM_OPS').map(x=>({value:x.id,label:x.name+' — '+human(x.role_code)}));
   if(!options.length)throw Error('Create an active tenant user before assigning setup ownership.');
   return openDialog('Assign responsible administrator','This person coordinates collecting setup data. It does not define the final approval role.',field('responsible_user_id','Responsible user','text',options[0].value,options),async v=>api('/admin/organization-setup/'+id+'/owner',{method:'PUT',body:JSON.stringify(v)}));
 }
 if(action==='setup-submit')return openDialog('Submit organization for review','Submission is blocked if any required demo field is missing or no owner is assigned.',field('reason','Submission reason','text','Initial setup ready for review'),async v=>api('/admin/organization-setup/'+id+'/submit',{method:'POST',body:JSON.stringify(v)}));
 if(action==='setup-approve'||action==='setup-return'){
   const approve=action==='setup-approve';
   return openDialog(approve?'Approve organization setup':'Return setup for changes','Platform Operations is the provisional demo reviewer. The actual client/design approver is not yet established.',field('note','Review note','text',approve?'Demo setup reviewed and approved':'Please correct the indicated setup details'),async v=>api('/admin/organization-setup/'+id+'/decision',{method:'POST',body:JSON.stringify({decision:approve?'APPROVE':'RETURN_FOR_CHANGES',note:v.note})}));
 }
 if(action==='new-team'){
   const tid=selectedTenant();const users=await api('/admin/users?tenant_id='+encodeURIComponent(tid));
   const opts=[{value:'',label:'No manager assigned'},...users.filter(x=>x.is_active&&x.role_code!=='PLATFORM_OPS').map(x=>({value:x.id,label:x.name}))];
   return openDialog('Create organization team','Adds a basic team, not a live dispatch or QA work queue.',field('name','Team name')+field('team_type','Team purpose','text','CLAIMS_OPERATIONS',[{value:'CLAIMS_OPERATIONS',label:'Claims Operations'},{value:'FIELD',label:'Field Operations'},{value:'QA',label:'QA'},{value:'FINANCE',label:'Finance'},{value:'OTHER',label:'Other'}])+field('manager_user_id','Team manager','text','',opts),async v=>api('/admin/organization-teams',{method:'POST',body:JSON.stringify({tenant_id:tid,name:v.name,team_type:v.team_type,manager_user_id:v.manager_user_id||null})}));
 }
 if(action==='team-members'){
   const people=await api(scoped('/admin/workforce'));
   const existing=await api('/admin/organization-teams/'+id+'/members');
   const current=new Set(existing.map(m=>m.user_id));
   const teamOptions=people.filter(p=>!current.has(p.user_id)&&p.login_active).map(p=>({value:p.user_id,label:p.name+' ('+human(p.role_code)+')'}));
   const description='Existing members: '+(existing.length?existing.map(m=>m.name).join(', '):'None yet')+'. Choose an active user from the same organization.';
   if(!teamOptions.length)throw Error('All eligible users are already assigned to this team.');
   return openDialog('Add team member',description,field('user_id','Available users','text',teamOptions[0].value,teamOptions),async v=>api('/admin/organization-teams/'+id+'/members',{method:'POST',body:JSON.stringify(v)}));
 }
 if(action==='workforce-change'){
   const person=state.workforce.find(p=>p.user_id===id);if(!person)throw Error('Workforce record not found');
   let choices=[{value:'AVAILABLE',label:'Available'},{value:'UNAVAILABLE',label:'Temporarily unavailable'},{value:'OFFBOARDED',label:'Offboard / leaves organization'}].filter(x=>x.value!==person.status);
   return openDialog('Update workforce status · '+person.name,'Unavailable is a staffing marker. Offboarding disables demo login. Assignment ownership must be reviewed separately.',field('status','New status','text',choices[0].value,choices)+field('reason','Reason for change'),async v=>{
     const response=await api('/admin/workforce/'+id+'/status',{method:'POST',body:JSON.stringify(v)});
     if(response.reassignment_status==='REVIEW_REQUIRED')notification('Status updated. Assigned claim ownership requires manual review.');
   });
 }
 if(action==='new-tenant'){if(!canCreateTenant())return notification('Platform operator required',true);return openDialog('Add demo tenant','A new synthetic tenant profile will be created. No tenant infrastructure is provisioned.',field('name','Organization name')+field('slug','Unique slug')+field('operating_model','Operating model','text','HYBRID'),async v=>api('/admin/tenants',{method:'POST',body:JSON.stringify(v)}));}
 if(action==='edit-tenant'){const t=state.tenants.find(x=>x.id===id);return openDialog('Edit organization',`Updates only the local demo record for ${t.name}.`,field('name','Organization name','text',t.name),async v=>api('/admin/tenants/'+id,{method:'PATCH',body:JSON.stringify(v)}));}
 if(action==='new-user'){const roles=state.roles.filter(x=>x.code!=='PLATFORM_OPS');return openDialog('Add demo user','Create a synthetic tenant account. Role does not confer Admin access unless Tenant IT Admin.',field('tenant_id','Tenant','text',useTenant)+field('name','Display name')+field('email','Email','email')+field('password','Local demo password','password')+field('role_code','Persona','text','TENANT_IT_ADMIN',selectOptions(roles,x=>({value:x.code,label:x.name}))),async v=>api('/admin/users',{method:'POST',body:JSON.stringify(v)}));}
 if(action==='edit-user'){const users=await api(scoped('/admin/users'));const x=users.find(x=>x.id===id);return openDialog('Update user',`Profile edits only. Use Workforce Lifecycle for availability and offboarding so a reason is recorded.`,field('name','Name','text',x.name),async v=>api('/admin/users/'+id,{method:'PATCH',body:JSON.stringify({name:v.name})}));}
 if(action==='toggle-flag'){const x=state.flags?.find(x=>x.id===id);return openDialog(`Change ${x.key}`,`Current demo state: ${x.enabled?'enabled':'disabled'}. This does not affect other services.`,field('enabled','New state','text',String(!x.enabled),[{value:'true',label:'Enabled'},{value:'false',label:'Disabled'}])+field('reason','Reason for change'),async v=>api('/admin/features/'+id,{method:'PATCH',body:JSON.stringify({enabled:v.enabled==='true',reason:v.reason})}));}
 if(action==='toggle-ai'){const x=state.ai?.find(x=>x.id===id);return openDialog(`Change ${x.name}`,`The use case is demo-only. No AI inference is executed.`,field('enabled','New state','text',String(!x.enabled),[{value:'true',label:'Enabled'},{value:'false',label:'Disabled'}])+field('reason','Reason for change'),async v=>api('/admin/ai/use-cases/'+id,{method:'PATCH',body:JSON.stringify({enabled:v.enabled==='true',reason:v.reason})}));}
}
$('login-form').addEventListener('submit',async ev=>{ev.preventDefault();$('login-error').textContent='';try{let r=await api('/auth/login',{method:'POST',body:JSON.stringify({email:$('login-email').value,password:$('login-password').value})});state.token=r.access_token;sessionStorage.setItem('claimspire_demo_token',state.token);await initialize()}catch(err){$('login-error').textContent=err.message}});
$('logout').addEventListener('click',()=>{sessionStorage.removeItem('claimspire_demo_token');state.token='';state.user=null;$('app').hidden=true;$('login-overlay').hidden=false;$('login-error').textContent=''});
$('tenant-filter').addEventListener('change',ev=>{state.tenant=ev.target.value;navigate(state.section)});
$('nav').addEventListener('click',ev=>{const btn=ev.target.closest('button[data-section]');if(btn)navigate(btn.dataset.section)});
document.addEventListener('click',ev=>{const btn=ev.target.closest('button[data-action]');if(btn)performAction(btn.dataset.action,btn.dataset.id).catch(err=>notification(err.message,true))});
$('edit-form').addEventListener('submit',async ev=>{ev.preventDefault();if(!state.dialogAction)return;const data=Object.fromEntries(new FormData($('edit-form')).entries());try{$('dialog-save').disabled=true;await state.dialogAction(data);$('edit-dialog').close();notification('Local demo data saved. Change recorded when applicable.');state.tenants=await api('/admin/tenants');renderTenantFilter();await navigate(state.section)}catch(err){$('dialog-error').textContent=err.message}finally{$('dialog-save').disabled=false}});
for(const btn of ['dialog-close','dialog-cancel'])$(btn).addEventListener('click',()=>$('edit-dialog').close());
if(state.token)initialize();
