# ClaimSpire Admin — 7-Minute Stakeholder Demo Script

**Demo intent:** Communicate the Admin product boundary and enable concrete design decisions. This is **not a Phase 1 scope commitment** or a claims-processing system.

## Start (30 seconds)

Open `http://127.0.0.1:8000/demo`, choose **Platform Operations**, and sign in with the credentials in README. No internet, AWS, other service or npm is needed. State up front that the two tenants and all records are synthetic.

## Scene 1: Dashboard (60 seconds)

Explain: "Admin gives operations a high-level view across the ClaimSpire platform." Show the two demo tenants, claim distribution, assignments, QA status and simplified claim journey. Emphasize that this is **read-only monitoring**, not a second desk adjuster workspace. Some journey stages are conditional (desk-only claims may not have field inspection).

## Scene 2: Tenant and persona administration (75 seconds)

Open **Tenants**; show sample operating models. Open **Users & Personas**; show the 16 canonical roles. Add a demo user, choose a persona, then show them in the user list. Emphasize: persona catalogue is available; **production permission grants need P-07 approval**. The UI includes broader mocked Admin behavior than the currently signed self-service scope.

## Scene 3: Workflow setup and operational monitoring (75 seconds)

Open **Workflow Setup** and walk through FNOL → Triage → Desk → Dispatch → Field → QA → Finance → Closure. State: "This is a demonstration of lifecycle visibility; it is not an executable rule engine." Open **Dispatch Monitoring** and **QA Monitoring** to show separate, read-only views of those activities.

## Scene 4: AI controls and audit (90 seconds)

Open **Features & AI**. Pick one synthetic AI use case and click Enable/Disable. Enter a reason. Verify the state changes in the local data. Switch to **Audit Trail** to show the action recorded. State: "These local controls simulate the Admin experience. The production switch must integrate through approved governance/AppConfig/AI Gateway and report effective state, not just database state." This is the strongest signed-Phase-1 Admin feature to demonstrate.

## Scene 5: Delivery readiness (60 seconds)

Open **Delivery Readiness**. Show capability classification: signed Phase 1, managed setup, prototype proposal, or deferred. Highlight P-07 roles, toggle catalog, AI CHK mappings, screen approvals and API ownership. State: "These are manageable decisions, not reasons to stop contract/mock development."

## Wrap up (30 seconds)

"I recommend we agree the Admin screen boundary, RBAC owner and API service ownership first. Meanwhile, we can move forward with schemas, DTOs, mock APIs, tenant checks, tests and a working demo. This avoids a waiting period without guessing production business rules."

## Questions for the room

- Which specific Admin sections in the prototype are valuable for Phase 1, and which should be deferred?
- Can we get a single Product/Design approver for Admin navigation and error states?
- Who signs off on the P-07 permission matrix and operating-model toggles?
- Can the backend owners confirm where Admin APIs should live: orchestration layer vs existing governance services?

## Demo reset & reliability

Run `pytest -q` to verify backend behavior (includes tenant isolation tests). If you want clean seed data, stop the server, delete only the local file `claimspire_admin.db` and restart. Never use this command against a production database.

The dashboard is intentionally seeded with a claim in each illustrative high-level stage per tenant, several field assignments, QA reviews and financial items. No real claims, approvals, disbursements or AI calls occur.
