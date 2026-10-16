# ClaimSpire Admin — API Catalog (Local Demo)

**API base URL:** `http://127.0.0.1:8000/api/v1`  
**Swagger:** `http://127.0.0.1:8000/docs`  
**OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`, also exported as `openapi.json` in the ZIP.

Except for `POST /auth/login` and `/health`, use `Authorization: Bearer <access_token>`.

## Authentication

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/login` | Obtain local demo JWT |
| GET | `/auth/me` | Current user |

Login request:

```json
{"email":"platform@claimspire.local","password":"DemoAdmin123!"}
```

## Tenants

| Method | Path | Description |
|---|---|---|
| GET | `/admin/tenants` | Platform: all tenants; tenant admin: own tenant |
| POST | `/admin/tenants` | Create demo tenant (Platform Ops only) |
| GET | `/admin/tenants/{tenant_id}` | Tenant detail |
| PATCH | `/admin/tenants/{tenant_id}` | Update display name; Platform Ops also controls operating model/status |

Example `POST /admin/tenants`:

```json
{"name":"Example Carrier (DEMO)","slug":"example-carrier","operating_model":"HYBRID"}
```

## Users & the 16 personas

| Method | Path | Description |
|---|---|---|
| GET | `/admin/roles` | List 16 canonical ClaimSpire persona descriptions |
| GET | `/admin/users` | List users, with tenant/role/active filters |
| POST | `/admin/users` | Create demo user in an allowed tenant |
| GET | `/admin/users/{user_id}` | View user |
| PATCH | `/admin/users/{user_id}` | Change role, name or active status |

Example `POST /admin/users` (tenant ID optional for tenant admins; required for Platform Ops):

```json
{
  "name":"Demo Reviewer",
  "email":"reviewer@example.local",
  "password":"LongDemoPassword123!",
  "role_code":"QA_REVIEWER"
}
```

No endpoint can create/promote a global Platform Ops account. This requires a separate provisioning process in this prototype. The user list never serializes password hashes.

## Operating configuration

| Method | Path | Description |
|---|---|---|
| GET | `/admin/lines-of-business` | LOB catalogue |
| POST | `/admin/lines-of-business` | Add local LOB entry |
| GET | `/admin/workflows` | High-level workflow templates |
| POST | `/admin/workflows` | Add stage list (non-executable template) |
| PATCH | `/admin/workflows/{workflow_id}` | Edit stage list/name/active flag |
| GET | `/admin/features` | Tenant feature toggles |
| POST | `/admin/features` | Add a local feature flag with a reason |
| PATCH | `/admin/features/{flag_id}` | Toggle flag with a mandatory reason; audit logged |

Example `POST /admin/workflows`:

```json
{
  "key":"personal_auto_journey",
  "name":"Personal Auto Journey (Demo)",
  "description":"For menu/screen prototyping; no real workflow transitions",
  "stages":["FNOL","TRIAGE","DESK","DISPATCH","FIELD","QA","FINANCE","CLOSED"],
  "active":true
}
```

Example `PATCH /admin/features/{flag_id}`:

```json
{"enabled":false,"reason":"Disable this demo capability for review"}
```

Example `POST /admin/features`:

```json
{"key":"DEMO_NEW_MODULE","description":"Demonstration capability","enabled":false,"reason":"Add module for admin UI preview"}
```

The `tenant_id` field can be omitted for tenant-scoped admin calls; a Platform Ops caller should specify it for new tenant-bound configuration.

## AI controls and integrations — mock-only

| Method | Path | Description |
|---|---|---|
| GET | `/admin/ai/use-cases` | Local AI use-case register |
| PATCH | `/admin/ai/use-cases/{use_case_id}` | Enable/disable register entry with reason |
| GET | `/admin/ai/kill-switches` | AI-prefixed local flags (`AI_*`) |
| PATCH | `/admin/ai/kill-switches/{flag_id}` | Toggle demo AI flag with reason and audit |
| GET | `/admin/integrations` | Local integration inventory and synthetic status |
| POST | `/admin/integrations` | Add a demo integration |
| PATCH | `/admin/integrations/{integration_id}` | Set mock status |

There is **no Bedrock call, AI model inference, AppConfig update or integration-health probe**. These routes only support representative Admin pages.

## Operational monitoring — read-only

| Method | Path | Purpose | Filters |
|---|---|---|---|
| GET | `/admin/navigation` | Sidebar/menu metadata | — |
| GET | `/admin/permissions` | Effective demo Admin scope | — |
| GET | `/admin/dashboard/summary` | Count cards + status breakdowns | `tenant_id` |
| GET | `/admin/workflow-stages` | Demo stages + sample counts | `tenant_id` |
| GET | `/admin/claims` | Synthetic claim list | `tenant_id`, `status`, `limit`, `offset` |
| GET | `/admin/assignments` | Synthetic desk/field assignment list | `tenant_id`, `status`, `limit`, `offset` |
| GET | `/admin/qa-reviews` | Synthetic package QA list | `tenant_id`, `status`, `limit`, `offset` |
| GET | `/admin/financial-items` | Synthetic finance entry list | `tenant_id`, `status`, `limit`, `offset` |

No POST/PATCH/DELETE routes exist for claims, assignments, QA reviews or financial entries. Their core actions belong in the respective ClaimSpire Web and Field workflows, not a generic control-plane prototype.

Example dashboard response (abbreviated):

```json
{
  "scope":{"tenant_id":"...","all_tenants":false},
  "tenant_count":1,
  "users":4,
  "claims":8,
  "assignments":3,
  "qa_reviews":2,
  "financial_items":2,
  "claim_statuses":{"FNOL":1,"TRIAGE":1,"DESK":1,"DISPATCH":1,"FIELD":1,"QA":1,"FINANCE":1,"CLOSED":1},
  "note":"Local demo aggregates, not live ClaimSpire financial or claim system-of-record data"
}
```

## Audit

| Method | Path | Description |
|---|---|---|
| GET | `/admin/audit-events` | Read local append-only admin event entries; filters: `tenant_id`, `action`, `limit`, `offset` |

Examples of recorded action codes include `tenant.created`, `tenant.updated`, `user.created`, `user.updated`, `workflow.created`, `workflow.updated`, `feature.changed`, `ai.kill_switch.changed`, `integration.status_changed`.

## Response conventions

| Code | Meaning |
|---|---|
| `200` | Read or update succeeded |
| `201` | Created |
| `401` | Missing, invalid or expired local JWT |
| `403` | Non-admin role, forbidden tenant or insufficient demo permission |
| `404` | Resource does not exist |
| `405` | No mutating route for read-only operational tables |
| `409` | Conflicting/double-create or forbidden self-account change |
| `422` | Pydantic input validation or missing tenant target |

List results are currently plain arrays with `limit` and `offset`, to keep the demo easy to connect. Standardized cursor pagination, server-side filtering expansion, policy-based field masking, and richer error envelopes are deferred until a production API contract is agreed.


## Delivery readiness / decision register (added in lead prototype)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/admin/implementation-readiness` | SOW-based Admin capability classifications, prototype scope and unapproved production decisions; requires Admin role |
| `GET` | `/demo` | Self-contained browser Admin prototype (login needed before seeing protected data) |
| `GET` | `/demo-assets/app.js`, `/demo-assets/styles.css` | Static UI resources served locally |

**Note:** Readiness content is a lead-developer planning fixture, not client-approved acceptance or a live decision workflow. All paths in this catalogue are local demo contracts until reviewed by API owners.

---

## v0.3 add-on: Organization and Workforce Administration

Additional API routes have been added to the local prototype; see `ADMIN_ONBOARDING_EXTENSIONS.md` for full field definitions, actor scoping, setup state diagram and business assumptions.

- `GET /admin/organization-setup/sections` — five **proposed placeholder** data-collection groups.
- `GET /admin/organization-setup` and `GET /admin/organization-setup/{tenant_id}` — tenant-scoped setup records.
- `GET /admin/organization-setup/{tenant_id}/readiness` — missing required demo fields.
- `PUT /admin/organization-setup/{tenant_id}/sections/{section_key}` — update draft section.
- `PUT /admin/organization-setup/{tenant_id}/owner` — assign responsible tenant user.
- `POST /admin/organization-setup/{tenant_id}/submit` — enter review state, requires reason and complete fields.
- `POST /admin/organization-setup/{tenant_id}/decision` — provisional Platform Ops review (non-self-approval).
- `GET /admin/organization-teams` and `POST /admin/organization-teams` — simple team hierarchy.
- `GET/POST /admin/organization-teams/{team_id}/members` and `DELETE /admin/organization-teams/{team_id}/members/{user_id}` — manage tenant-scoped team membership.
- `GET /admin/workforce` and `GET /admin/workforce/events` — user availability and history.
- `POST /admin/workforce/{user_id}/status` — change availability/offboarding with reason, audit and manual-workload-review indicator.

Paths above are relative to `/api/v1`. Check `/docs` for precise payloads and responses. Every change is local and synthetic. The five data group names, approver role, and workforce actions are **proposed**, not client-confirmed Phase 1 business rules.
