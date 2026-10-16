"""Static delivery-planning facts for a local demo, NOT an approved requirements register."""
from fastapi import APIRouter, Depends
from app.models import User
from app.security import require_admin

router = APIRouter(prefix='/admin', tags=['Admin: Delivery Readiness (Demo)'])

# Scope classifications are deliberately explicit: source-aligned vs demo proposal.
CAPABILITIES = [
    {'module':'AI governance controls','classification':'SOW_PHASE1_ADMIN','implementation':'DEMO_WORKING','why':'Platform Ops must view/operate governed AI switches and use-case controls.'},
    {'module':'Audit & operational governance','classification':'SOW_PHASE1_FOUNDATION','implementation':'DEMO_WORKING','why':'Administrative changes must be traceable.'},
    {'module':'Managed initial tenant configuration','classification':'SOW_PHASE1_MANAGED','implementation':'DEMO_WORKING','why':'Initial tenant must be configured before production operations.'},
    {'module':'Persona and access catalogue','classification':'SOW_PHASE1_FOUNDATION','implementation':'DEMO_WORKING','why':'Approved RBAC/ABAC matrix governs all four surfaces.'},
    {'module':'Workflow stages and LOB catalogue','classification':'DEMO_PROPOSAL','implementation':'DEMO_WORKING','why':'Demonstrates operating-model configuration without claiming a full production workflow engine.'},
    {'module':'Claims, dispatch, QA and finance dashboards','classification':'DEMO_PROPOSAL','implementation':'READ_ONLY_SYNTHETIC','why':'Shows admin visibility across surfaces, not core workflow execution.'},
    {'module':'Integration catalogue','classification':'DEMO_PROPOSAL','implementation':'DEMO_METADATA_ONLY','why':'Allows a simple integration readiness overview.'},
    {'module':'Organization onboarding journey (local demo)','classification':'DEMO_PROPOSAL','implementation':'DEMO_WORKING','why':'Guided Carrier/TPA or IA setup, five provisional collection sections, completeness gate and simulated review.'},
    {'module':'Team structure & workforce lifecycle','classification':'DEMO_PROPOSAL','implementation':'DEMO_WORKING','why':'Visualizes team setup, availability and offboarding without executing dispatch reassignment.'},
    {'module':'Full tenant self-service administration','classification':'DEFERRED_BY_SOW','implementation':'NOT_INCLUDED','why':'Explicitly outside signed Phase 1 unless separately approved.'},
]
DECISIONS = [
    {'id':'ADM-01','topic':'Admin UI scope and owner','owner':'Client / Product / Design','priority':'BLOCKS_PRODUCTION_SCOPE','needs':'Confirm which Aubergine section 4 admin screens are accepted into the Phase 1 internal Admin UI.','can_build_now':'Demo navigation, read-only screens and documented API contracts.'},
    {'id':'ADM-02','topic':'Approved role and permission matrix','owner':'Client + GoML','priority':'BLOCKS_PRODUCTION_AUTH','needs':'Approve P-07 personas, permission bundles, ABAC and separation-of-duties matrix.','can_build_now':'Local demo role checks, deny-by-default tests and permission-code proposals.'},
    {'id':'ADM-03','topic':'Tenant configuration and feature catalogue','owner':'Client / Product','priority':'BLOCKS_PRODUCTION_CONFIG','needs':'Approve operating-model toggle catalogue and which settings can be edited in the UI.','can_build_now':'Generic configuration schemas with synthetic toggles.'},
    {'id':'ADM-04','topic':'AI use-case configuration governance','owner':'Client / AI Governance','priority':'BLOCKS_AI_PRODUCTION','needs':'Approve mapped CHK rows, prompts/model versions, authorization and release process.','can_build_now':'Version-ready API contracts and demo switch changes with reason/audit.'},
    {'id':'ADM-05','topic':'Initial tenant authority thresholds','owner':'Client Claims / Finance','priority':'BLOCKS_PRODUCTION_CONFIG','needs':'Approve reserve/payment/settlement/write-off thresholds under P-08.','can_build_now':'Document data fields and create non-executable demo values if needed.'},
    {'id':'ADM-06','topic':'Data classification and retention','owner':'Client Legal / Security','priority':'BLOCKS_PRODUCTION_GOVERNANCE','needs':'Approve data classification and P-09 retention/legal hold/redaction policy.','can_build_now':'Metadata fields, non-destructive local audit, test matrix.'},
    {'id':'ADM-07','topic':'Design handoff and state transitions','owner':'Aubergine / Client / GoML','priority':'BLOCKS_FINAL_UI_CONTRACT','needs':'Confirm field states, empty/error flows, owner actions and accepted UI navigation.','can_build_now':'Clickable prototype plus screen-to-API map.'},
    {'id':'ADM-09','topic':'Organization onboarding approval authority','owner':'Client / Product / Design','priority':'BLOCKS_PRODUCTION_AUTH','needs':'Confirm who gathers, submits and approves organization setup for Carrier/TPA and IA firms; whether approval is required before activation.','can_build_now':'Local completion and approval workflow with a clearly provisional Platform Ops reviewer.'},
    {'id':'ADM-10','topic':'Exact five data collection flows','owner':'Aubergine / Client','priority':'BLOCKS_FINAL_FIELD_CONTRACT','needs':'Identify the actual names, mandatory fields, document evidence and branching of the five organization data-collection flows.','can_build_now':'Configurable five-section draft model with generic fields; no final business rules.'},
    {'id':'ADM-11','topic':'Workforce unavailability and offboarding rules','owner':'Client / Claims Ops / Workforce','priority':'BLOCKS_PRODUCTION_WORKFORCE','needs':'Define who approves exit/unavailability, revokes access, reassigns active work and preserves retention.','can_build_now':'Log a reasoned status transition, disable local login for offboard, flag work for review.'},
    {'id':'ADM-08','topic':'Backend integration ownership','owner':'GoML Architecture Leads','priority':'BLOCKS_SERVICE_INTEGRATION','needs':'Confirm whether Admin is a BFF/orchestrator or API routes live in existing governance services.','can_build_now':'Ports/adapters, open API spec and read-only summary DTOs.'},
]

@router.get('/implementation-readiness')
def implementation_readiness(actor: User = Depends(require_admin)):
    return {
        'surface':'CLAIMSPIRE_INTERNAL_ADMIN',
        'disclaimer':'Planning/demo illustration; this is not a client-approved feature or sign-off register.',
        'capabilities':CAPABILITIES,
        'open_decisions':DECISIONS,
        'source_notes':[
            'ClaimSpire SOW §3.2 and §§4-5: Phase 1 internal Platform Ops AI controls and managed initial tenant activation; self-service admin deferred.',
            '16 Persona Master View: roles are canonical personas, not a final UI/RBAC matrix.',
            'Aubergine Gantt §4: additional Admin screens are pending acceptance.',
        ],
    }
