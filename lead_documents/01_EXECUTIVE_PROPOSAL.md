# ClaimSpire Admin Surface — Lead Developer Proposal

**Working proposal · GoML internal discussion · 15 October 2026**  
**Purpose:** Start productively before final designs, permissions, and stakeholder decisions are complete.  
**Deliverables:** An implementation-ready Admin blueprint **and** an offline/local runnable demonstration.

## Executive recommendation

Build **Admin as the platform control and oversight surface**, not a second claim-processing application. For the *signed Phase 1 scope*, prioritize internal Platform Operations controls for Ask ClaimSpire use cases, AI kill switches, prompt/model settings, AI Use Case Register and governance evidence. Separately, support **managed activation of the initial tenant** (profile, feature toggles, persona/permissions, authority, retention, integration readiness) using controlled setup mechanisms. **Full tenant self-service administration is expressly deferred** unless change-ordered.

Use an **expanded demo-only navigation model** to show where the Admin surface could evolve: tenant directory, users/personas, LOB and workflow configuration, operations dashboards for claims/dispatch/QA/finance, integration inventory and audit. These are **illustrative product proposals**, not additional Phase 1 commitments.

This lets the lead developer contribute valuable architecture, UX-to-API mappings, DTOs, mock data, tests, and stakeholder questions *before* business-rule approvals, without coding unapproved claims, payouts, or advanced automation.

## Why we are doing each part

| Element | Business value | Why start now? | Production boundary |
|---|---|---|---|
| AI & feature controls | Govern sensitive AI availability, risk and rollback | Explicitly in SOW §3.2 | Production needs approved model/prompt configuration, runtime integrations and reason/audit controls |
| Tenant settings | Make initial tenant operational before FNOL intake | Managed initial onboarding is in SOW §5.6 | No full tenant self-service platform in Phase 1 |
| Users & 16 personas | Show what user groups exist and how access works | Persona model is available | Client-approved P-07 RBAC/ABAC matrix required for production |
| Workflow/LOB catalogue | Communicate operating model and configurable claim journeys | FigJam and FNOL diagrams define high-level stages | Demo stage arrays do not execute a claim workflow |
| Operations dashboard | One-screen understanding of FNOL → desk → field → QA → finance | Reuses familiar workflow stages for discussion | Read-only synthetic views; claim actions remain in their owning services |
| Integrations view | Expose readiness, owner and status concept | First-wave integrations are planned in SOW | Demo integration statuses do not prove connectivity |
| Audit history | Demonstrate accountability for Admin changes | SOW requires dual-write audit foundation | Local append-only demo table ≠ tamper-evident Audit Ledger |
| Delivery readiness | Make assumptions and dependencies visible | Removes ambiguity from team discussions | Proposed tracker, not client sign-off evidence |

## Personas and product-surface boundaries

- **Persona #15 — ClaimSpire Platform Operations:** principal user for the Internal Admin UI's Phase 1 control functions.
- **Persona #14 — Tenant IT/System Administrator:** manages tenant-side access and technical setup; managed initial tenant setup required, self-service UI deferred.
- **Persona #1 — Claims Operations Administrator:** primarily handles FNOL and claim administration in the **Web App**, not every item in the platform Admin.
- **Other 13 personas:** can be referenced in admin directories or visibility dashboards but must not be granted unrestricted Admin rights by their business titles.

## Two outcomes for the GoML team

### Outcome A — Implementation blueprint

Present a signed-scope versus proposed-demo capability matrix, end-to-end Admin journeys, API inventory, domain ownership map, role boundaries, implementation backlog, acceptance checklist, unresolved decision register and service integration approach. This is valuable whether or not the UI is approved yet.

### Outcome B — Clickable working demonstration

Run FastAPI locally with SQLite and sample data. Show navigation, two demonstration tenant contexts, all 16 canonical personas, users, workflow stages, LOBs, claims, assignments, QA and finance snapshots, feature/AI toggles, local audit records and the readiness register. There is **no AWS dependency**, no AI inference, no payment issuance, and no actual claim mutation.

## Proposal for a lead-owned kickoff review (30 minutes)

1. **5 min — Context:** What Admin does vs what Claims Web App does; signed scope vs demo scope.
2. **8 min — Clickable demo:** Navigate Overview → Tenant → Users → Journey → AI controls → Audit; perform a local toggle with reason.
3. **7 min — Architecture:** API contract, tenant checks, local DB, service ownership, adapters and audit.
4. **7 min — Decision gate:** Walk through open issues ranked by what blocks *production* versus what the team can build now.
5. **3 min — Ask:** Request owner for UX, RBAC approval, screen acceptance, config ownership, and a contract review meeting.

**Suggested positioning:** "This is not a claim that the client approved new screens. It is a working backend and Admin experience to validate the direction, de-risk the first build, and make decisions concrete before engineering begins."

## Source basis

1. Signed *ClaimSpire Production Pilot SOW*: §3.2 client surfaces; §§3.5–3.7 control-plane services; §4 prerequisites P-02/P-07/P-08/P-09 and AI CHK build-lock; §5.1 platform control plane; §5.6 managed initial tenant activation.
2. *ClaimSpire — 16 Core Personas & Workflow Overview*: canonical 16 business personas (working baseline).
3. *Aubergine Swimlane Workflows*: pre-FNOL setup, FNOL, triage, desk assignment, staff/IA field dispatch, inspection package, QA and carrier handoff.
4. *Aubergine Project Gantt*, section 4: broader proposed Admin screens are open items pending review.
5. *FNOL Intake Spine / Branch Pack*: evidence for high-level workflow navigation, not grounds for building a production FNOL engine in Admin.

**Important:** SOW scope takes precedence. The demo deliberately simplifies and makes explicit assumptions where a prototype benefits from them.
