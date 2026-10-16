# ClaimSpire Admin: Organization Onboarding & Workforce Journeys (Local POC v0.3)

## 1. Why these two workflows were added

The original API-only/overview prototype had CRUD for `Tenant` and `User`, but not the business process by which an organization joins ClaimSpire. The FigJam `Swimlane Diagram` labels **Pre-Phase I: Organisation / Workforce Setup** and explicitly names six setup pillars:

1. Establish operating model (Carrier/IA + applicable LOBs/modules).
2. Create/configure users and assign base roles.
3. Configure access/permissions and boundaries.
4. Configure teams, queues, workgroups and routing structure.
5. Configure operating controls (templates, labels, fees, toggles and AI).
6. Establish authority/governance (approvals, overrides and SoD).

The user-supplied additional walkthrough clarifies a finer organization journey: determine organization type and responsible person, collect organization info (name, address, contacts, licences, LOBs), resolve missing details, structure/team/branding setup, submit for approval, and then configure/establish the organization. It also mentions updates, availability, onboarding and offboarding of users.

**Scope boundary:** The supplied SOW has internal Platform Ops AI/control/governance capabilities and *managed initial* tenant activation as Phase 1; full tenant self-service onboarding is deferred. The extended screens are **illustrative**, not a contractual scope expansion.

## 2. Chronological workflows in v0.3

### Organization setup

`Existing/new demo tenant → Setup owner → Collect five provisional data groups → Missing-field gate → Submit with reason → IN_REVIEW → Platform Ops simulated approval or return for corrections → APPROVED / CHANGES_REQUESTED`

Current local demo states: `DRAFT`, `IN_REVIEW`, `CHANGES_REQUESTED`, `APPROVED`. Approval is only an internal demonstration marker. Neither application tenant activation nor real credentials/integration provisioning occurs. Role of the actual setup approver **is still an open client/design decision**; the demo temporarily uses Platform Ops and prohibits a submitter from approving their own request.

Five **proposed placeholder** collection groups (not source-confirmed as the five named design flows):

| Group | Local demo fields | Why represented |
|---|---|---|
| Organization identity | legal_name, organization_type, operating_model | Establish which kind of operation is joining |
| Address and contacts | primary_email, phone, street_address | Provide contact and location details |
| Lines of business and licenses | lob_codes, license_reference | Represent LOB coverage and credentials as unverified metadata |
| Organization structure and teams | structure_summary, team_contact | Capture a high-level hierarchy prior to operational queues |
| Branding basics | display_name, logo_reference | Demonstrate basic branding setup; not full white-label portal support |

Any required field is only a **local POC validation assumption**. Actual required fields and applicable license details depend on the approved design.

### User availability and exit

`User created (Users & Personas) → Available → Temporarily unavailable / Return to available → Offboarded (local account disabled)`.

`UNAVAILABLE` is a staff-capacity/status marker, **not** proof that production user access should remain enabled. The demo intentionally leaves local login unchanged for temporary unavailability, and disables it on `OFFBOARDED`. This policy and claims/assignment reassignment need confirmation. An offboarded user cannot be reactivated using this simple endpoint. All status changes require a reason and append an event. Existing assigned demo claims are **flagged for manual review**, never automatically reassigned.

## 3. Database extension

| New model | Key fields | Relationship |
|---|---|---|
| `OrganizationSetup` | tenant_id, organization_type, responsible_user_id, sections JSON, status, submitted_by_id, approved_by_id | One setup record to one tenant |
| `OrganizationTeam` | tenant_id, name, team_type, parent_team_id, manager_user_id | Many teams per tenant, optional parent team |
| `OrganizationTeamMember` | team_id, user_id | Many users to many teams, tenant-scoped membership |
| `WorkforceStatus` | user_id, tenant_id, status | One status to one tenant user |
| `WorkforceLifecycleEvent` | tenant_id, user_id, actor_id, old_status, new_status, reason | Many historical changes per user |

The `OrganizationSetup.sections` JSON is intentionally generic; it is easy to change during design discovery, **but production should use versioned, reviewed schemas** rather than unbounded mutable documents.

All new routes enforce the existing local admin role and tenant scoping. Writes produce the existing demo `AuditEvent` entries.

## 4. Added API contracts

```text
GET  /api/v1/admin/organization-setup/sections
GET  /api/v1/admin/organization-setup?tenant_id=...
GET  /api/v1/admin/organization-setup/{tenant_id}
GET  /api/v1/admin/organization-setup/{tenant_id}/readiness
PUT  /api/v1/admin/organization-setup/{tenant_id}/sections/{section_key}
PUT  /api/v1/admin/organization-setup/{tenant_id}/owner
POST /api/v1/admin/organization-setup/{tenant_id}/submit
POST /api/v1/admin/organization-setup/{tenant_id}/decision
GET  /api/v1/admin/organization-teams
POST /api/v1/admin/organization-teams
GET  /api/v1/admin/organization-teams/{team_id}/members
POST /api/v1/admin/organization-teams/{team_id}/members
DELETE /api/v1/admin/organization-teams/{team_id}/members/{user_id}
GET  /api/v1/admin/workforce
POST /api/v1/admin/workforce/{user_id}/status
GET  /api/v1/admin/workforce/events
```

Sample update:

```json
PUT /api/v1/admin/organization-setup/{tenant_id}/sections/coverage
{"data":{"lob_codes":["PROPERTY","LIABILITY"],"license_reference":"SAMPLE-NOT-VERIFIED"}}
```

Sample lifecycle change:

```json
POST /api/v1/admin/workforce/{user_id}/status
{"status":"UNAVAILABLE","reason":"Employee on scheduled leave"}
```

## 5. Current role/access behavior

- Platform Operations can read all demo tenants and approve an `IN_REVIEW` setup that they did not submit.
- Tenant IT Admin can create/update and submit setup **only for their own tenant**, but cannot approve it.
- Claims/Field/Finance personas have no Admin access in this local demo.
- Self-offboarding is blocked. Platform Operations accounts are protected.
- This is a teaching/prototype permission model; production requires client-approved RBAC/ABAC/SoD.

## 6. What remains unanswered (ask product/design)

1. Who owns and approves the organization setup: ClaimSpire Platform Ops, tenant administrator, carrier/TPA approver, IA owner, or an agreed combination? Is maker-checker required?
2. Are Carrier/TPA and IA firms both first-class organizations with different setup forms? Which fields are truly mandatory by type?
3. What are the **names and required fields of the five data-collection flows** referenced in discussions? Which source contains their accepted version?
4. Is organization setup completed **before** user/teams/permissions configuration or only **after** all six Pre-Phase I responsibilities pass readiness? What exactly activates the organization?
5. Which user changes require approval and who may update role/team/credentials after activation?
6. When a user becomes unavailable or leaves, should access be revoked immediately, who reassigns active claims/field work, and should the change affect assignment eligibility?
7. What level of tenant self-service or branding customization, if any, is included in **approved Phase 1** rather than a later phase/change request?

## 7. Recommended next real-engineering increment

1. Obtain the actual organization/user journey frames and final field definitions from Aubergine; map each Figma action to one API.
2. Agree a tenant onboarding state machine, owner/approver matrix, and idempotency/rollback policy.
3. Introduce versioned configurations and richer structured records for org structure and licensing.
4. Replace demo auth with the platform identity/PDP and enforce DB-level tenant isolation.
5. Integrate workforce status with assignment eligibility and authorized reassignment **only after the business rules are signed off**.
6. Keep tenant provisioning and cross-domain writes in owning services; Admin is an orchestrating/governance surface, not the Claim Core.
