# ClaimSpire Admin — Complete Explanation (Business Flow → Backend)

**Audience:** Learning the v0.3 prototype and preparing to explain decisions to a senior architect or lead developer.  
**Prototype:** `ClaimSpire_Admin_Organization_Workflows_v3`  
**Verified against code:** 16 October 2026 — claims below match `app/security.py`, `app/routers/organization.py`, `app/models.py`, `app/static/app.js`, and `tests/test_api.py` (20 tests).

---

## Central idea

We built a small **administration control system** for ClaimSpire: authorized administrators can register organizations, collect setup information, manage users and teams, maintain configurations, monitor operations, and track changes.

We did **not** build the claims-processing engine inside Admin. We built the administrative foundation around which that engine will operate.

Admin answers four questions:

1. **Who is operating on the platform?** — Organizations, users, personas, teams.
2. **Is that organization ready to operate?** — Setup information, completeness, ownership, review.
3. **How is the organization configured and governed?** — LOBs, workflow templates, feature settings, AI controls, permissions.
4. **What is happening, and who changed what?** — Operational monitoring, workforce status, audit history.

---

## 1. Business problem

Two companies want to use ClaimSpire:

| Company | Type | Needs |
|---|---|---|
| Harbor Mutual Insurance | Carrier / TPA | Claims personnel, desk adjusters, supervisors, field resources, teams, claim-handling config |
| Summit Independent Adjusting | IA Firm | Dispatch teams, field adjusters, QA reviewers, workforce info, operational config |

Without administration, ClaimSpire cannot know which organization a user belongs to, who can access records, which teams exist, what capabilities are enabled, or whether setup is complete.

Claims Web App, Mobile App, and Portals are where business activities happen. **Admin establishes and governs the organizational environment** supporting those activities.

---

## Part 1 — Why two organization types?

| Organization type | Meaning | Business purpose |
|---|---|---|
| `CARRIER_TPA` | Carrier / Third-Party Administrator | Carrier or TPA claim-handling operations |
| `IA_FIRM` | Independent Adjusting Firm | Adjusting or inspection-related services |

### Are these categories static?

In current code, yes:

```python
ORG_TYPES = frozenset(("CARRIER_TPA", "IA_FIRM"))
```

The backend rejects unsupported types (`422`). This is a **scoped prototype simplification**, not a permanent product limitation.

### Have we created two completely different forms?

No. One generic onboarding structure with an organization-type field.

**Shared sections:** Identity · Contacts · LOB/Licenses · Structure · Branding → Completeness Check → Submit → Review

Both types share common data needs. One `OrganizationSetup` model and one collection process. Later, Carrier/TPA vs IA Firm can diverge via conditional fields and rules. **Today both use the same provisional five-section template.**

### Organization type vs operating model vs persona

| Concept | Question | Example |
|---|---|---|
| Organization type | What kind of company? | `CARRIER_TPA` or `IA_FIRM` |
| Operating model | How does it operate? | Desk, Field, Hybrid, CAT |
| Persona / role | What is a user responsible for? | Desk Adjuster, QA Reviewer, Tenant IT Admin |

In the database: `Tenant.operating_model` and `OrganizationSetup.organization_type` are separate.

**Current simplification:** creating a tenant via UI supplies name, slug, and operating model; the backend creates a draft `OrganizationSetup` defaulting to `CARRIER_TPA`. `IA_FIRM` can be selected later in Organization Identity. A better final design would ask organization type at the start.

---

## Part 2 — Two Admin personas

### Persona 15 — ClaimSpire Platform Operations

Platform-level administrator (not belonging to one insurance company).

- **Seeded account:** `platform@claimspire.local`
- Ordinary user-creation endpoint **does not** allow creating `PLATFORM_OPS`
- Cross-tenant visibility in the demo for testing (production needs governed support access)

**Can do (demo):** view all tenants; create tenants; update restricted tenant fields; review/approve/return setups; manage users/teams; view workflows/LOBs/integrations; toggle features/AI; monitor synthetic claims/dispatch/QA/finance; view audit and delivery readiness.

### Persona 14 — Tenant IT / System Administrator

Organization-scoped administrator (e.g. Harbor IT admin).

- Seeded: `admin@harbor.local`, `admin@summit.local`
- Backend restricts access to the assigned tenant

**Can do (own tenant):** collect/submit setup; create/update users; manage teams/membership; workforce availability; feature settings; authorized audit.

**Cannot:** approve setups; create platform tenants; change operating model / tenant status (and similar restricted fields).

Both personas generally see the **same menu**. Differences come from available actions and backend authorization — not two separate Admin websites.

| Activity | Platform Ops | Tenant IT Admin |
|---|---|---|
| View all demo tenants | Yes | No |
| Create new tenant | Yes | No |
| Complete / submit setup | Yes | Own tenant |
| Approve / return setup | Yes | No |
| Users / teams / workforce | Yes | Own tenant |
| Feature / AI toggles | Yes | Own tenant |
| Operational summaries / audit | All demo tenants | Own tenant |

This is **simplified demo permissions**, not the final RBAC/ABAC matrix.

---

## Part 3 — Admin lifecycle (chronological)

Example: Riverside Claims Services joins ClaimSpire.

### Stage 1 — Platform Ops registers the organization

`POST /api/v1/admin/tenants` with name, slug, operating model.

Creates:

- `Tenant` — “Which company is this?”
- `OrganizationSetup` (draft) — “What has been collected, who owns setup, has it been reviewed?”

**Simplification:** new setup is `DRAFT`; `Tenant.status` defaults to `ACTIVE`. Production activation should be tied to approved readiness, not inferred from tenant creation.

### Stage 2 — Establish Tenant IT Admin

Platform Ops creates a user with `tenant_id`, `TENANT_IT_ADMIN`, hashed password, `is_active=true`.

Key relationship: **User → Tenant**. Production invitation / MFA / credential delivery is not implemented.

### Stage 3 — Collect setup information

Five provisional groups in `app/routers/organization.py` → `SECTIONS`:

| Group | Key fields | Required (demo) |
|---|---|---|
| Organization identity (`profile`) | legal_name, organization_type, operating_model | all three |
| Address and contacts (`contacts`) | primary_email, phone, street_address | email, street |
| LOBs and licenses (`coverage`) | lob_codes, license_reference | both |
| Organization structure (`structure`) | structure_summary, team_contact | structure_summary |
| Branding (`branding`) | display_name, logo_reference | display_name |

`fields` = accepted keys; `required` = must exist before submit. Nine required demo fields total.

Save example: `PUT /api/v1/admin/organization-setup/{tenant_id}/sections/branding`  
Logo is a **text reference** only — no image upload.

### Stage 4 — Readiness check

`GET /api/v1/admin/organization-setup/{tenant_id}/readiness`

Backend-controlled completeness. Frontend displays gaps; it is not trusted to decide readiness.

### Stage 5 — Assign setup owner

Stores `OrganizationSetup.responsible_user_id` (active same-tenant user).  
**Setup owner ≠ setup approver.**

### Stage 6 — Submit for review

`POST .../submit` — requires editable status (`DRAFT` / `CHANGES_REQUESTED`), all required fields, responsible admin, tenant permission → status `IN_REVIEW`.

### Stage 7 — Platform Ops reviews

`POST .../decision` — only `PLATFORM_OPS`; must be `IN_REVIEW`; submitter cannot approve own submission (SoD); approval rechecks completeness; note required → `APPROVED` or `CHANGES_REQUESTED`.

Approver persona is a **provisional demo choice**.

### Stage 8 — Configure teams, users, capabilities

Users/personas, teams, LOBs, workflow templates, features/AI, integrations. No single transaction from `APPROVED` through full operational activation yet.

---

## Part 4 — User / workforce scenarios

| Scenario | What happens |
|---|---|
| A. New employee | `POST /admin/users` + `WorkforceStatus` = `AVAILABLE`; Mobile/Web own the actual work |
| B. Joins a team | `Tenant → Team ↔ User` via `OrganizationTeamMember` (admin metadata, not a dispatch queue) |
| C. Temporarily unavailable | `AVAILABLE → UNAVAILABLE` (reason required); login stays active; may return `REVIEW_REQUIRED` if desk-assigned demo claims |
| D. Returns | `UNAVAILABLE → AVAILABLE`; no automatic reclaim of prior assignments |
| E. Leaves | `→ OFFBOARDED`; `is_active=false`; login fails; no Cognito revoke / claim transfer |
| F. Profile edit | Name / permitted fields via PATCH — separate from workforce status |
| G. Feature change | Local flag + reason → audit; does not call live AI |
| H. Monitor ops | Dashboard / Claims / Dispatch / QA / Finance — **read-only** |

---

## Part 5 — Authentication

Four distinct concepts: authentication · authorization · tenant isolation · workforce availability.

```text
Login → POST /auth/login → find user → verify PBKDF2 hash
→ JWT (sub, iat, exp, HS256) → sessionStorage
→ Bearer on APIs → get_current_user → require_admin
→ PLATFORM_OPS | TENANT_IT_ADMIN → permitted_tenant()
```

- Password: PBKDF2-HMAC-SHA256, random salt, **250,000** iterations, constant-time compare.
- Token does **not** embed permissions; backend reloads user each request (inactive account blocks immediately).
- Limitations: no MFA, reset, invitations, refresh-token flow, session revocation service, or granular PDP.

---

## Part 6 — Models and APIs (engineering reasoning)

**Method:** business activity → actor → data → state → actions → model → API → permissions → UI/tests.

### 18 SQLAlchemy models

`Tenant`, `Role`, `User`, `OrganizationSetup`, `OrganizationTeam`, `OrganizationTeamMember`, `WorkforceStatus`, `WorkforceLifecycleEvent`, `LineOfBusiness`, `WorkflowTemplate`, `FeatureFlag`, `AIUseCase`, `Integration`, `Claim`, `Assignment`, `QAReview`, `FinancialItem`, `AuditEvent`.

SQLAlchemy models = persistence; Pydantic schemas = API contracts (`UserCreate` / `UserPatch` / `UserOut`, etc.).

### Business-command APIs (not arbitrary status PATCH)

| Action | API |
|---|---|
| Create company | `POST /admin/tenants` |
| Collect section | `PUT /admin/organization-setup/{id}/sections/{section}` |
| Readiness | `GET /admin/organization-setup/{id}/readiness` |
| Submit | `POST /admin/organization-setup/{id}/submit` |
| Decide | `POST /admin/organization-setup/{id}/decision` |
| Workforce transition | `POST /admin/workforce/{id}/status` |
| Feature toggle | `PATCH /admin/features/{id}` |

Prefix: `/api/v1`. Logic largely lives in route functions; a service layer is a sensible next step.

---

## Part 7 — Screens (14 navigation sections)

| # | Screen | Demo reality |
|---|---|---|
| 1 | Overview | Dashboard counts / stage summaries |
| 2 | Tenants | Create / update (Platform Ops primary) |
| 3 | Organization Setup | Sections, readiness, owner, submit/review |
| 4 | Workforce Lifecycle | Teams, members, availability, offboarding |
| 5 | Users & Personas | Create/update users; view 16 personas |
| 6 | Workflow Setup | Read-only UI; template/LOB APIs exist |
| 7–10 | Claims / Dispatch / QA / Finance | Read-only synthetic data |
| 11 | Features & AI | Local toggles + reason + audit |
| 12 | Integrations | Read-only UI; status APIs exist |
| 13 | Delivery Readiness | Static planning information |
| 14 | Audit Trail | Tenant-scoped change history |

**Tenants** = which orgs exist. **Organization Setup** = onboarding progress.  
**Users & Personas** = account/role. **Workforce Lifecycle** = availability/teams/exit.

---

## Part 8 — All 16 personas vs Admin access

Only `PLATFORM_OPS` and `TENANT_IT_ADMIN` pass `require_admin()`.  
Logging in as `desk@harbor.local` authenticates but Admin is denied.

Having a ClaimSpire account ≠ Admin access.

---

## Part 9 — Practice checklist & negative tests

Walk the full Riverside (or Harbor) journey: Platform Ops login → Harbor-only scope → create tenant → create Tenant Admin → incomplete submit fails → complete sections → readiness → submit → return → approve → user/team → unavailable → offboard → feature+audit → cross-tenant 403 → read-only ops screens.

| Negative scenario | Expected |
|---|---|
| Wrong password | 401 |
| Desk Adjuster hits Admin API | 403 |
| Harbor reads Summit | 403 |
| Tenant Admin creates tenant | 403 |
| Incomplete / locked setup edit | 409 |
| Tenant Admin approves setup | 403 |
| Bad organization type | 422 |
| Cross-tenant team member | 422 |
| Offboarded login | 401 |
| Feature without reason | 422 |

Automated suite: **20** tests covering these categories and key success paths.

---

## Part 10 — Senior Q&A (short answers)

- **Why not everything on Tenant?** Setup has its own lifecycle, status, owner, reviewer, sections, notes.
- **Why one form?** Shared structure + `organization_type` classifier; diverge later.
- **Why fixed org types?** Predictable POC validation for the two relationships in scope.
- **Why two Admin roles?** Platform vs organization authority and tenant scope differ.
- **Why return-for-changes?** Correction path without recreating the whole setup.
- **Why approval note?** Traceability.
- **Why setup approval ≠ activation?** Activation may need more gates (permissions, integrations, etc.).
- **Why JSON sections?** Fields are provisional; tradeoff is weaker DB-level validation.
- **Why one role per user?** Demo simplification pending approved RBAC/ABAC.
- **Why SQLite / no microservices?** Local runnable POC first; production DB/services are separate work.
- **Why Claims/QA/Finance in Admin?** Operational visibility only; mutations belong to domain services.

**Production priorities:** approved field/state model; tenant activation gate; stronger permissions; service/repository layer; migrations; invitation provisioning; production auth/audit; clear ownership boundaries. Demo user creation assigning `TENANT_IT_ADMIN` without privileged-access approval is **POC-only**.

---

## Part 11 — Confirmed vs designed

| Area | Grounding |
|---|---|
| Four product surfaces | Architecture / SOW |
| Carrier/TPA and IA workflows | FigJam / design context |
| 16 personas | Persona master |
| Platform Ops AI/governance | SOW Phase 1 Admin |
| Managed initial tenant onboarding | SOW Phase 1 |
| Exact five collection groups | **Provisional prototype** |
| Platform Ops as setup approver | **Provisional prototype** |
| Self-service extra tenants | Exploration; not established Phase 1 |
| One role / local JWT / 8-stage claim display | Prototype |

A working demo ≠ client approval for production behavior.

---

## Part 12 — Full lifecycle (remember this)

1. Platform initialization (Platform Ops)
2. Organization registration
3. Tenant administrator setup
4. Organization data collection
5. Setup readiness
6. Organization review (submit → approve / return)
7. Operating configuration
8. Workforce management
9. Operational oversight (read-only)
10. Governance and maintenance (ongoing)

Steps 7–10 are continuous, not one-time gates.

### Elevator positioning for a senior

> “I approached ClaimSpire Admin as a platform control and organization-management surface. Two organization categories—Carrier/TPA and IA Firm—and two Admin personas—Platform Operations and Tenant IT Administrator. Tenant identity and organization setup are separate lifecycles. A generic five-section collection model demonstrates completeness and review without locking unapproved fields. Teams, workforce availability, feature controls, and read-only operational monitoring sit around that core. FastAPI + Pydantic + SQLAlchemy + SQLite, local JWT, tenant scoping, audit, and automated tests. APIs are business commands (submit/approve/offboard), not only CRUD. This is a local POC; next we validate org-specific forms, approval authority, activation gates, and permissions with client and design, then align contracts to production architecture.”
