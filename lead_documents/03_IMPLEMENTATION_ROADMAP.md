# Implementation Roadmap — What a Lead Developer Can Deliver Now

**Planning convention:** Relative work packages, not committed client dates. The signed SOW has its own 18-week program and build-lock gates; do not replace those milestones with this estimate.

## Three tracks run in parallel

| Track | Goal | Artifact / Output |
|---|---|---|
| **Product discovery** | Validate which Admin screens belong in Phase 1, who uses them, where UX is incomplete | Scope & screen approval matrix; open-decision log; persona-to-actions list |
| **Architecture & API** | Contract first: define resource ownership, access, schema, events, failure states and tests | HLD, API catalogue, schemas, mock contracts, security map, ADRs |
| **Experience & demo** | Give stakeholders something they can see and challenge | Clickable local Admin, seeded tenants, synthetic operations data, demo walkthrough |

## Proposed delivery work packages

| Package | Implementation steps | Deliverables | Acceptance checks | Dependencies |
|---|---|---|---|---|
| 0. Scope and baseline | Review SOW §3.2/§5, FigJam, persona map, Gantt §4; tag each idea *SOW / managed setup / demo assumption / deferred* | Product-scope table, first screen list, source notes | Every screen has a scope label and owner | Existing docs available now |
| 1. Architecture | Define Admin vs business-domain boundaries, local-first adapters, DTOs, tenant context and audit approach | Architecture diagram, ADR 001, API contract map | No claims/finance production table mutation from Admin | Service owner review later |
| 2. Auth and common APIs | Add dev JWT, users, admin role, tenant scope, validation, error handling, tests | `/auth/*`, `/admin/users`, `/admin/roles`, `/admin/tenants` | Unauthenticated and non-admin denied; cross-tenant negative tests | P-07 required for production PDP |
| 3. Configuration | Build feature, AI use-case, LOB, workflow template and integration metadata APIs | CRUD/read models, local audit, Swagger | Valid reasons recorded for switch change; workflows non-executable | Toggle catalogue required for production |
| 4. Operations read models | Build dashboard summary and read-only claim/dispatch/QA/finance DTOs | `/admin/dashboard/summary`, read-only endpoints | Accurate seeded counts; no money-moving actions | Real domain API ownership later |
| 5. Clickable UI | Build compact Admin site served by FastAPI; tenant selector, modules, demo workflows | `/demo` UI, user list, settings forms, switch toggle, audit view | 5-minute local demo runs without network access | None |
| 6. Hardening and handoff | Test errors/permissions, publish docs, update API schema, script walkthrough | Tests, source ZIP, OpenAPI, README, handoff deck notes | Demo is reproducible on clean machine | No AWS required |
| 7. Production alignment (later) | Replace demo identity/config/audit/data with owning services and approved governance | Integration adapters, contract tests, rollout plan | Meets client-approved acceptance criteria | Design, CHK, auth, policy and release approvals |

**Already delivered in prototype:** Packages 0–6 at a *demonstration* level. Production alignment is intentionally not claimed.

## Suggested 10-business-day lead-owned sprint to validate the direction

This is a proposed planning example, not a commitment. It assumes one developer can consult design and architecture owners; adjust after estimation.

- **Days 1–2:** Review source mapping, inventory Admin screens, propose navigation and scope tags. Outcome: architecture and decision register v0.
- **Days 3–4:** Agree API standards, module DTOs, tenant context, auth behavior and data ownership; review with backend lead. Outcome: API catalogue v0 and ADRs.
- **Days 5–6:** Stabilize local FastAPI seed/mock backend and user/tenant/auth modules. Outcome: contract tests and demo fixtures.
- **Days 7–8:** Complete feature/AI controls, operations summaries and clickable UX flow. Outcome: full local walkthrough.
- **Day 9:** Add negative cases, error handling, logs, diagrams and recorded demonstration steps. Outcome: technical review candidate.
- **Day 10:** Present to manager, Product, Design and architecture stakeholders; collect decisions and create actionable implementation tickets. Outcome: prioritized backlog and owners.

## Recommended backlog slicing (each ticket includes why and acceptance)

| Ticket | Scope | Why | Definition of done |
|---|---|---|---|
| ADM-API-01 | Current actor + permission context | All later routes need tenant-scope identity | Contract, 401/403 tests, no role from request body |
| ADM-API-02 | Tenant read/update | Initial managed activation | Scoped reads; controlled writes; audit |
| ADM-API-03 | User and role list/update | Operational onboarding | Approved action design or explicit demo placeholder; negative tests |
| ADM-API-04 | AI use-case catalogue | Phase 1 governance | Registered use cases and known states |
| ADM-API-05 | Feature/AI switch mutation contract | Safety and recoverability | Reason, version, authority, audit, apply-status state model |
| ADM-API-06 | Audit read/export contract | Accountability | Authorized search and event integrity boundary |
| ADM-API-07 | Read-only operational dashboard | High-level visibility | DTO contracts, tenant filter, no domain writes |
| ADM-UX-01 | Navigation and empty/error states | UX/backend collaboration | Reviewed screen-to-API matrix |
| ADM-TEST-01 | Tenancy and role negative tests | Prevent leaks or privilege escalation | Automated and documented |
| ADM-DEV-01 | Seed data and demo reset | Reproducibility | Clean-machine script, demo credentials clearly labelled |

## How to run implementation meetings as lead

1. Publish source-backed inventory with **confidence/state labels**.
2. Split story discussions into *business intent*, *UX behavior*, *API contract*, *security gate*, *acceptance test*.
3. Ask exactly which user sees or mutates data—not merely which persona is in the chart.
4. Record decisions with owner, date, SOW/CHK reference, API impact and status.
5. Do not implement contract-changing logic before business approval. Continue low-risk DTO, adapters, docs, mocks and test harness work.
6. Before merging, require OpenAPI updates, negative tenant tests, audit event map, security review, rollout/rollback notes and demo/UAT evidence.

## Productionization roadmap (beyond demo)

1. Replace local JWT with approved Cognito identity; integrate PDP decisions rather than embedding role rules across handlers.
2. Replace SQLite with approved PostgreSQL/Aurora schema and tenant isolation/RLS; add Alembic.
3. Replace local feature updates with governed configuration versions and AppConfig deployment/effective-state reporting.
4. Integrate AI Gateway use-case/config registry and audit evidence; enforce AI CHK build-lock mapping.
5. Replace synthetic operational summaries with read-only, permission-filtered projections sourced from domain services.
6. Replace demo audit tables with authoritative Audit & Timeline queries and events.
7. Add SOW-aligned observability, IaC, migration rollback and CI/CD release controls.

None of these production integrations is required to run the local demonstration.
