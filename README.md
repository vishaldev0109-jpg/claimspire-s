**IMPORTANT:** If `/demo` previously showed 404, use `RUN_ON_MAC.md` and run this **fixed** folder, not the earlier `claimspire_admin_backend` folder. The main `/` path now opens the demo too.

# ClaimSpire Admin Backend — Local Prototype

A **working FastAPI backend** for an illustrative ClaimSpire Admin product surface. It uses **SQLite by default**, includes a **synthetic demo dataset**, and runs with **no AWS account, credentials, or cloud integrations**.

> **Scope:** High-level admin navigation and CRUD for administrative configuration, plus read-only cross-domain operations. This is a demonstration and planning baseline, **not** a fully approved Phase 1 requirement set, carrier claim system, real financial ledger, real authentication provider, or production implementation.


## v0.3 — Organization onboarding and workforce lifecycle extension

Two extra navigation pages have been added to the earlier fixed Admin demo:

- **Organization Setup:** Demonstrates the Carrier/TPA versus IA firm choice, accountable setup owner, five **provisional** data-collection groups, missing-details validation, submit-for-review, and a review decision. The demo temporarily uses Platform Operations as approver, with maker-checker protection; this is not a confirmed client role. Approval marks the local setup record only; it does not activate real tenants or provision infrastructure.
- **Workforce Lifecycle:** Displays organization teams, allows creating simple team records, shows user availability, supports **AVAILABLE → UNAVAILABLE → AVAILABLE** and **AVAILABLE/UNAVAILABLE → OFFBOARDED** transitions, requires a reason, and creates audit/lifecycle history. Offboarding disables the local login. **No automatic claims reassignment, dispatch, HR integration, or data deletion** is performed.

The five provisional groups are Organization Identity, Address & Contacts, LOB & License Reference, Organization Structure, and Branding Basics. **These are not claims about the exact five workflows in the design documents**; the final source-specific field definitions must be provided/approved. The FigJam Pre-Phase I gives *six* high-level responsibility areas (Operating Model, Users, Access, Teams/Queues, Operating Controls, Governance). See `docs/ADMIN_ONBOARDING_EXTENSIONS.md` for mapped sources and open questions.

**Demo sequence:** Sign in as `admin@harbor.local`, open **Organization Setup**, complete Harbor's pending collection groups and submit. Sign out, log in as `platform@claimspire.local`, open the same page and approve. Go to **Workforce Lifecycle**, create a team or change a demo user's availability, and inspect **Audit Trail**. Or, signed in as Platform Ops, approve the already submitted Summit IA demo record.

**If upgrading from the older local SQLite database**, new tables are created by `create_all` at startup and seeded idempotently; old records are preserved. For a guaranteed identical demo, use a fresh copy of the folder with no existing `claimspire_admin.db`.

## 1. Start locally

```bash
# Python 3.11+
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
cp .env.example .env          # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/demo** for the clickable Admin console, or **http://127.0.0.1:8000/docs** for interactive Swagger endpoints. The app creates `claimspire_admin.db` in the current working directory and seeds demo data once on first startup. It never connects to AWS.

Companion **lead presentation package:** See `../lead_documents/` in the full downloadable ZIP, including the executive proposal, risk register, step-by-step implementation roadmap, architecture ownership and demo walkthrough.

Other docs: [Admin implementation plan](docs/IMPLEMENTATION_PLAN.md) · [API catalog](docs/API_CATALOG.md) · [Architecture and boundaries](docs/ARCHITECTURE.md) · [Screen mapping](docs/ADMIN_SCREENS.md).

## Clickable Admin UI (new)

Open **http://127.0.0.1:8000/demo** and choose the seeded Platform Ops or Tenant Admin account. The UI is served directly by FastAPI; it needs no Node, React, separate frontend server or AWS setup.

It demonstrates: dashboard, tenant directory, user/persona management, workflow and LOB catalogues, read-only claims/dispatch/QA/finance, synthetic AI/feature controls, integration metadata, audit records, and a delivery readiness register. The user interface includes functional local tenant/user edits and reason-coded feature/AI changes. No real policy/claim/QA/financial actions are executed.

**Important:** Admin expansion beyond Platform Ops AI/governance and managed initial tenant configuration is demonstration scope, not an approved Phase 1 commitment. The `implementation-readiness` endpoint explicitly tags the boundary.

## 2. Login accounts (synthetic demo only)

| Email | Password | Role | Access |
|---|---|---|---|
| `platform@claimspire.local` | `DemoAdmin123!` | Platform Operations | All demo tenants |
| `admin@harbor.local` | `DemoAdmin123!` | Tenant IT Admin | Harbor tenant only |
| `admin@summit.local` | `DemoAdmin123!` | Tenant IT Admin | Summit tenant only |
| `supervisor@harbor.local` | `DemoAdmin123!` | Claims Supervisor | No Admin endpoint access (negative test) |
| `desk@harbor.local` | `DemoAdmin123!` | Desk Adjuster | No Admin endpoint access (negative test) |

Demo tenants: **Harbor Mutual Insurance** and **Summit Independent Adjusting**. All claims, insured names, locations, workflow statuses, financial values, and integrations are *invented placeholders*.

### Example API call

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"platform@claimspire.local","password":"DemoAdmin123!"}'
```

Copy `access_token` and set `Authorization: Bearer <TOKEN>` in Swagger's **Authorize** menu (or Postman). Then call:

```text
GET /api/v1/admin/dashboard/summary
GET /api/v1/admin/workflow-stages
GET /api/v1/admin/roles
GET /api/v1/admin/claims
GET /api/v1/admin/qa-reviews
GET /api/v1/admin/features
```

For updates, see the full request/response examples in [docs/API_CATALOG.md](docs/API_CATALOG.md).

## 3. What's implemented

| Module | Features | Behavior |
|---|---|---|
| Auth | Local login, JWT, current user | Dev-only local replacement for cloud authentication |
| Tenants | List, detail, create, update | Scoped by platform/tenant admin |
| Users/Personas | All 16 persona definitions; list/create/update users | Tenant-scoped; no password exposure in outputs |
| Workflow templates | List/create/edit high-level stage lists | **Demonstration configuration only**; no engine execution |
| Lines of Business | List/add LOBs | Demo taxonomy; no policy ingestion logic |
| Features | List/add/toggle flags with reason + audit | Stored locally; no AppConfig or enforcement of cross-service features |
| AI use cases | List/toggle demo register | No models or AI calls |
| Integrations | List/create/change demo status | No actual external connections |
| Operations dashboard | Claim/dispatch/QA/finance counts, stages | Read-only synthetic operational records |
| Audit trail | List filtered admin change records | Local append-only API; not a tamper-proof production ledger |
| OpenAPI | Auto Swagger and `openapi.json` | Typed request/response contracts |
| Clickable demo | Self-contained HTML/CSS/JS at `/demo` | Browser-based admin without separate frontend build |
| Delivery readiness | `/api/v1/admin/implementation-readiness` | Signed-scope vs demo vs deferred labels, dependency register |

Routes are in `app/routers/`; schema is in `app/models.py`; fake data is in `app/seed.py`.

## 4. Test

```bash
pytest -q
```

The included tests cover authentication, the 16 personas, tenant isolation, forbidden access, dashboard/flow data, read-only endpoints, feature-change audit, and user administration.

## 5. Local persistence and reset

SQLite file is `./claimspire_admin.db`. To wipe **demo data only**, stop the server, delete that file, and restart. **Do not do this in production.** Seed is idempotent on an existing database.

For local PostgreSQL instead, install a PostgreSQL driver (`pip install 'psycopg[binary]'`) and set an SQLAlchemy URL such as `postgresql+psycopg://user:password@localhost:5432/claimspire_admin` in `.env`. Database table auto-creation is for this prototype; use Alembic migrations before a real deployment.

## 6. Important boundaries

- No AWS setup, Cognito, AppConfig, Bedrock, EventBridge, or infrastructure is required to run the project.
- Admin CRUD writes only to simplified local configuration data. It does **not** approve claims, reassign production adjusters, perform QA, release funds, or initiate actual payments.
- Read-only claim/dispatch/QA/finance entries are synthetic admin dashboard representations, not an authoritative operational domain model.
- The signed ClaimSpire SOW centers the Phase 1 **Internal Admin UI** on Platform Operations AI/governance controls, while separately including **managed initial tenant activation**. Broader admin modules in this demo are deliberately assumed for prototyping; they must not be presented as signed Phase 1 commitments.
- Local JWT/password handling, authorization, audit and toggles are **development simulators**, not a substitute for production-grade identity, PDP, security review, RLS, key management, append-only forensic audit, or controlled approvals.

## 7. Project structure

```text
claimspire_admin_backend/
├── app/
│   ├── main.py                 # app, lifespan, Swagger, router registration
│   ├── config.py               # .env-based local settings
│   ├── database.py             # SQLAlchemy engine/session
│   ├── models.py               # demo tenant/user/config/overview entities
│   ├── schemas.py              # Pydantic input/output contracts
│   ├── security.py             # local JWT, role and tenant checks
│   ├── helpers.py              # writes, audit and scoping utilities
│   ├── seed.py                 # 16 personas + synthetic business data
│   └── routers/
│       ├── auth.py
│       ├── tenants.py
│       ├── people.py
│       ├── configuration.py
│       ├── operations.py
│       └── audit.py
├── docs/
│   ├── ADMIN_SCREENS.md
│   ├── API_CATALOG.md
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── app/static/                 # browser-based demo Admin UI
├── openapi.json
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```
