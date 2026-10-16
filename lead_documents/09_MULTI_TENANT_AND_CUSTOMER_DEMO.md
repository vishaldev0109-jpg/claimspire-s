# Multi-Tenant Handling & Customer Demo Guide (v0.3.1)

## Are we multi-tenant?

**Yes — for this Admin prototype.** Tenant isolation is enforced in the **backend APIs**, not by trusting the UI.

| Concern | How it works in the demo |
|---|---|
| Organization boundary | `Tenant` row + UUID `tenant_id` on users, setup, teams, config, claims, audit |
| Two org categories | `CARRIER_TPA` and `IA_FIRM` (many companies per category) |
| Seeded examples | Harbor Mutual (Carrier) and Summit IA (IA Firm) |
| Platform Ops | Cross-tenant visibility for demo support/ops |
| Tenant IT Admin | Forced to `user.tenant_id` on every list/get/mutate |
| Security boundary | `permitted_tenant`, `assert_resource_access`, `mutation_tenant`, `require_admin` |
| UI filter | Convenience only — wrong `tenant_id` still returns **403** |

### What production still needs (be honest in demos)

- Cognito + PDP (RBAC/ABAC/SoD), not local JWT role checks  
- PostgreSQL Row-Level Security  
- Tenant-scoped search/evidence/audit services  
- Real AppConfig / AI Gateway effective-state controls  

This POC **proves the Admin multi-tenant journey and API contracts**.

---

## How to run (before any walkthrough)

```bash
cd ~/Downloads/ClaimSpire_Admin_Organization_Workflows_v3
source .venv/bin/activate          # or create venv + pip install -r requirements-dev.txt
cp -n .env.example .env
rm -f claimspire_admin.db          # clean seed (optional but recommended for demos)
uvicorn app.main:app --reload
```

- UI: http://127.0.0.1:8000/demo  
- API docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  
- Regression: `pytest -q` (expect **25** tests)

**Accounts (password `DemoAdmin123!`):**

| Email | Role | Sees |
|---|---|---|
| `platform@claimspire.local` | Platform Ops | All tenants |
| `admin@harbor.local` | Tenant IT Admin | Harbor only |
| `admin@summit.local` | Tenant IT Admin | Summit only |

---

## Customer / stakeholder walkthrough (12–15 minutes)

State up front: *synthetic data, local demo, not live claims or AWS.*

### 1. Multi-tenant isolation (3 min) — most important proof

1. Login as **Harbor** Admin.  
2. Overview: callout says own-tenant scope; claim counts are Harbor-only.  
3. Claims / Features / Users — only Harbor.  
4. Sign out → login as **Summit** Admin — different org, different data.  
5. Sign out → login as **Platform Ops** — tenant filter “All” then Harbor / Summit.  
6. Optional technical aside: in Swagger, Harbor token + `tenant_id=<summit>` → **403**.

**Talking point:** *“Admin is multi-tenant. Carrier and IA firms share the product; data is isolated by organization. The UI hides other tenants; the API enforces it.”*

### 2. Dynamic onboarding of a third company (5 min)

As Platform Ops:

1. **Tenants → Register organization**  
   - Name, slug, type (`CARRIER_TPA` or `IA_FIRM`), operating model  
   - Status becomes **REGISTERED** (not active yet)  
2. **Users → Add** a `TENANT_IT_ADMIN` for that tenant (only Platform Ops can).  
3. Sign out → login as that **new email/password** (no code change).  
4. Complete **Organization Setup** five sections → Assign owner → Submit.  
5. Platform Ops → Approve setup (still REGISTERED).  
6. **Activate tenant** → ACTIVE.  

**Talking point:** *“Registering is not the same as going live. Setup review and activation are separate gates.”*

### 3. Workforce & governance (3 min)

1. Create a Field Adjuster user (non-Admin persona).  
2. **Workforce** → team + member → mark Unavailable (login still works) → Offboard (login fails).  
3. **Features & AI** → toggle with a reason → **Audit Trail** shows the change.  

**Talking point:** *“Admin configures people and controls; inspection and payments stay in their owning apps.”*

### 4. Boundaries (2 min)

Show Claims / Dispatch / QA / Finance are **read-only**.  
Open Delivery Readiness: signed Phase 1 vs demo proposals.

**Close:** *“Next production steps: Cognito/PDP, approved onboarding forms, real AI kill-switch effective state, Audit Ledger.”*

---

## What you can click through (checklist)

| Area | What works |
|---|---|
| Login | Any seeded or newly created Admin account |
| Overview | Tenant-scoped dashboard + isolation callout |
| Tenants | Register, edit name, activate, suspend (Platform Ops) |
| Organization Setup | Edit sections, readiness, owner, submit, approve/return, submissions |
| Users & Personas | Create/edit users; privileged Admin only via Platform Ops |
| Workforce | Teams, members, available/unavailable/offboard |
| Features & AI | Local toggles + reason + audit |
| Claims / Dispatch / QA / Finance | Read-only synthetic monitors |
| Integrations / Workflow / LOB | Inventory / templates (demo) |
| Audit | Tenant-scoped Admin history |
| Delivery Readiness | Scope/decision planning view |

### Negative demos (impressive for technical audiences)

| Try | Expect |
|---|---|
| Wrong password | 401 |
| `desk@harbor.local` on Admin APIs | 403 |
| Harbor + Summit `tenant_id` | 403 |
| Harbor creates another `TENANT_IT_ADMIN` | 403 |
| Suspend tenant → that Admin hits Admin API | 403 |
| Incomplete setup submit | 409 |
| Approve before IN_REVIEW | 409 |

---

## How to package / extract for a customer sample

1. Zip or git-push this folder (`ClaimSpire_Admin_Organization_Workflows_v3`).  
2. Point them to `START_HERE_v3.md` + this document.  
3. One command path: venv → `pip install -r requirements-dev.txt` → `uvicorn` → `/demo`.  
4. Do **not** include real client data; keep `claimspire_admin.db` out of the share (`.gitignore`).  
5. Optional: run `pytest -q` live to show automated isolation coverage.

---

## Multi-tenant implementation map (for architects)

```text
Browser tenant filter
        │  (not trusted)
        ▼
Authorization: Bearer JWT
        ▼
require_admin  →  role + tenant membership + block SUSPENDED
        ▼
permitted_tenant / assert_resource_access / mutation_tenant
        ▼
SQLAlchemy queries filtered by tenant_id
        ▼
AuditEvent written with tenant_id
```

Routers that apply scoping: tenants, people, organization, configuration, operations, audit.
