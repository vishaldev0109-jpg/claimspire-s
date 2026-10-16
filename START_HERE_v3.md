# Start here: ClaimSpire Admin Organization Workflows v0.3.1

This is an **extension of `ClaimSpire_Admin_Demo_FIXED`**. It adds the organization onboarding and workforce journeys described in the latest discussion while preserving the earlier dashboard, tenant, user, AI, claims/dispatch/QA/finance, audit and readiness pages.

**v0.3.1 stabilizations:** email/password login (no hardcoded account dropdown), organization type at registration, `REGISTERED`→activate lifecycle, privileged `TENANT_IT_ADMIN` provisioning limited to Platform Ops, versioned setup submission snapshots, hardened multi-tenant API isolation (incl. suspended-tenant block), expanded API tests (25).

**Customer demo / multi-tenant walkthrough:** see `lead_documents/09_MULTI_TENANT_AND_CUSTOMER_DEMO.md`.

## Run on Mac

```bash
cd ~/Downloads/ClaimSpire_Admin_Organization_Workflows_v3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
# If upgrading from an older local SQLite file and something looks off:
# rm -f claimspire_admin.db
uvicorn app.main:app --reload
```

Browser: **http://127.0.0.1:8000/demo** (or `/`), Swagger: **http://127.0.0.1:8000/docs**, health: `/health`.

If port 8000 is already occupied by the older app, stop the older Uvicorn session first with `Ctrl+C`, or run this one with `--port 8001`.

Login uses **email + password** fields. Example accounts: `admin@harbor.local`, `admin@summit.local`, and `platform@claimspire.local`, password `DemoAdmin123!`. Newly created Tenant IT Admins can sign in with the credentials you set. **Local demonstration only.**

## The two newest menu items

1. **Organization Setup** — Displays Carrier/TPA and IA firm examples, responsible administrator, five proposed collection sections, completion progress, missing-data gate, submit and provisional reviewer decision.
2. **Workforce Lifecycle** — Shows teams, supports creating teams and adding users to them, displays workforce availability and lets administrators simulate unavailability/return/offboarding with a reason and audit trail.

## Suggested team demonstration

**A. Incomplete Carrier/TPA:** Log in as `admin@harbor.local`. Open Organization Setup → view Harbor's missing details → edit LOB/Licence, Structure and Branding → Submit for review. Sign out and log in as Platform Ops → Approve Harbor. The reviewer is *only a demo assumption*.

**B. Dynamic third organization:** Platform Ops → Tenants → Register organization (pick `IA_FIRM` or `CARRIER_TPA`) → Users → add `TENANT_IT_ADMIN` for that tenant → sign out → log in as that new admin (no HTML edits) → complete setup → submit → Platform Ops approves → **Activate tenant**. Tenant stays `REGISTERED` until activation.

**C. IA firm (seeded):** Log in as Platform Ops → Organization Setup → Summit IA is already ready and in review → Approve or Return for changes.

**D. Workforce:** Open Workforce Lifecycle → Add team → Manage members → choose one tenant user → Change status to Unavailable or Offboarded → Audit Trail. No actual claim assignment or dispatch is modified.

## Exactly what is and isn't proven

- Proven: local FastAPI endpoints, SQLite model relationships, **API-enforced multi-tenant isolation**, state validation, reasoned actions, audit records, frontend interaction and **25** passing backend tests; dynamic login; registration org-type; activation gate; privileged-role guard; submission snapshots; suspended-tenant Admin block.
- Not proven: production RBAC/PDP/Cognito, client-approved data groups, final approver routing, email invitations, actual policy/LOB/credential checks, live staffing/distribution, full tenant self-service, enterprise branding, or AWS deployment.
- Source mapping: FigJam Pre-Phase I lists **six** operating setup pillars. User described **five** data-collection flows, but their exact accepted names/fields aren't established in the available extracted source. The five UI sections are therefore deliberately configurable placeholders.

See `docs/ADMIN_ONBOARDING_EXTENSIONS.md` and `lead_documents/07_COMPLETE_ADMIN_EXPLANATION.md` for scope mapping and walkthrough.
