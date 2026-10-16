# General Admin backend — practical implementation plan

## Objective

Deliver a local, demonstrable FastAPI Admin backend representing the **top-level ClaimSpire Admin surface**, with enough working endpoints for a frontend prototype without implementing claim adjudication, workflow execution, AI, or third-party integrations.

## Track A — Foundation (already implemented in starter)

1. FastAPI app, typed OpenAPI, `api/v1` prefix and Swagger.
2. SQLAlchemy local database; synthetic tenant records; seed on first launch.
3. Local login/JWT + two Admin roles + per-tenant access checks.
4. All 16 canonical ClaimSpire persona reference records.
5. Tests for anonymous access, non-admin access and tenant isolation.

**Demo:** login as platform admin, load all tenants; login as tenant admin, see only own tenant.

## Track B — Configurable Admin modules (already implemented)

1. Tenant list/create/view/edit (restricted by local role).
2. Users list/create/view/edit + persona mapping.
3. LOB list/create.
4. Workflow template list/create/edit — high-level stage arrays, not engine logic.
5. Feature flag list/create/toggle with mandatory reason for toggles.
6. AI register list/toggle with mandatory reason — no provider calls.
7. Integration catalogue create/update mock status.
8. Append local audit event when changing Admin configuration.

**Demo:** enable the demo `AI_NBA_EXPLANATION` flag for Harbor, then show a `feature.changed` event in Audit Trail.

## Track C — Operational Admin overviews (already implemented)

1. Dashboard counts and summaries.
2. 8-stage flow metadata for the UI.
3. Read-only claims list with tenant/status filters.
4. Read-only field assignment list.
5. Read-only QA package-review list.
6. Read-only financial item list.

**Demo:** select Harbor tenant and show counts and status tables, then select Summit as Platform Ops to view its independent demo data.

## Track D — Clickable Admin frontend (implemented in lead demo)

1. Sidebar and navigation are implemented in `app/static/`; `GET /admin/navigation` remains a backend navigation contract.
2. Local login screen and demo JWT session storage are implemented; production session security must be redesigned.
3. Tenant/user forms, workflow/LOB reads, feature/AI toggles, and read-only monitoring pages are implemented.
4. Basic API validation/errors and UI notifications are present; finer empty/error-state design awaits accepted UX.
5. Tenant filtering, empty/loading states and confirmations are present; table search/sort/full server pagination UI remains future refinement.
6. Do not present demo feature switches as production AI switches.

## Track E — Hardening before any real environment (future work)

1. Replace seeded secrets and dev JWT with approved identity and session architecture.
2. Use Alembic migrations and persistent PostgreSQL with tenant row-level security.
3. Integrate actual Governance/PDP and an approved RBAC/ABAC/SoD matrix.
4. Add centrally enforced audit events and application telemetry.
5. Split Admin projections from canonical Claim Core, Assignment Router, Field Capture, QA and Finance service-owned data.
6. Implement configuration change review/approval and effective-versus-requested state.
7. Add rate limiting, secure secret management, concurrency controls, event processing and failure handling.
8. Test authorization boundaries, idempotency, concurrency, backup/restore and domain contract compatibility.
9. Reconcile screen-level scope with SOW, CHK and accepted Aubergine UX before committing the production Admin implementation.

## Simplifications deliberately chosen

| Decision | Prototype behavior | Later decision |
|---|---|---|
| User roles | Platform Ops / Tenant IT Admin may enter Admin | Client-approved access matrix |
| Workflow engine | Editable stage list only | Real transition gates/ownership |
| Claim overview | Read-only seeded claims | Query actual Claim Core APIs |
| Dispatch/QA/finance | Seeded read-only panels | Integrate real domain services |
| Feature flags | Boolean stored in SQL | Governance rules and AppConfig effective state |
| AI controls | Enable/disable demo use cases | AI Gateway/versioned prompt/model governance |
| Integration status | Manually simulated | Provider health/event monitoring |
| Audit | DB events for Admin writes | Regulator-grade append-only Audit & Timeline |
| Tenant creation | Platform-only demo API | Managed initial setup; self-service requires separate scope approval |

## Basic acceptance checklist

- [x] Start FastAPI without AWS.
- [x] Seed two demo tenants and 16 persona definitions.
- [x] Swagger shows all API contracts.
- [x] Login returns JWT; unauthenticated calls are rejected.
- [x] Non-admin persona cannot access Admin endpoints.
- [x] Tenant admin cannot read another tenant's claim information.
- [x] Config toggle needs a reason and writes audit event.
- [x] Dashboard returns valid counts and workflow stages.
- [x] Claim, assignment, QA and finance views are read-only.
- [x] Automated local tests pass (13 tests in current package).
- [x] Add clickable demo UI served by FastAPI.
- [ ] Validate final navigation/menu labels against accepted Aubergine Figma UI.
- [ ] Approve exact production Admin scope/RBAC before migrating beyond demo.
