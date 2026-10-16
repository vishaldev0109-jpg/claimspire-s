# Senior Architect Talk Track — ClaimSpire Admin v0.3

**Use:** 5–8 minute briefing (or 30-minute kickoff with demo).  
**Companion:** `07_COMPLETE_ADMIN_EXPLANATION.md` for depth; `01`–`06` for proposal, journeys, roadmap, blockers, architecture.

---

## Opening (30 seconds)

Admin is the **platform control and organization-management surface**, not a second claims app. We prototyped the foundation that answers: who operates here, are they ready, how are they configured, and what changed.

---

## Problem (45 seconds)

Harbor (Carrier/TPA) and Summit (IA Firm) both use ClaimSpire differently. Without Admin, we cannot reliably know organization membership, access scope, teams, enabled capabilities, or onboarding completion. Web/Mobile/Portals own business work; Admin owns the environment those surfaces depend on.

---

## Three distinctions (1 minute)

| Concept | Not the same as |
|---|---|
| `CARRIER_TPA` / `IA_FIRM` | Operating model (`HYBRID`, `FIELD`, …) or persona |
| `Tenant` | `OrganizationSetup` (identity vs onboarding lifecycle) |
| Account active | Workforce available (login ≠ assignment readiness) |

One generic five-section setup form today; type is a classifier. Separate Carrier vs IA validation is deferred until design confirms field differences.

---

## Two Admin actors (1 minute)

| | Platform Ops | Tenant IT Admin |
|---|---|---|
| Scope | All demo tenants | Own tenant only |
| Creates tenants | Yes | No |
| Approves setup | Yes (demo provisional) | No |
| Day-to-day org setup / users / teams / flags | Yes | Own tenant |

Same Admin UI shell; **authorization is API-enforced**, not menu-hiding. Non-admin personas (e.g. Desk Adjuster) can authenticate but get `403` on Admin APIs.

---

## Lifecycle spine (90 seconds)

```text
Platform Ops creates Tenant + draft OrganizationSetup
→ Tenant Admin account linked to tenant
→ Fill 5 sections → readiness (backend) → assign owner
→ Submit (IN_REVIEW) → Approve / Return (Platform Ops + SoD)
→ Teams, users, features → workforce availability / offboarding
→ Read-only claims/dispatch/QA/finance + audit
```

**Business-command APIs** (`submit`, `decision`, workforce status) — not a free-form status PATCH — so callers cannot jump `DRAFT → APPROVED`.

---

## Stack & guarantees (1 minute)

- FastAPI · Pydantic · SQLAlchemy · SQLite · local JWT (PBKDF2 passwords)
- Tenant isolation via `permitted_tenant` / `assert_resource_access`
- 18 models; setup sections as JSON (provisional fields)
- Mutations audited locally; ops screens read-only synthetic data
- **20** automated API tests (auth, scoping, setup workflow, workforce, teams)

Explicitly **not** production Cognito/PDP, migrations, invitations/MFA, live AI/integrations, or claim mutation.

---

## Confirmed vs provisional (45 seconds)

**Grounded:** four surfaces, Carrier/TPA + IA relationships, 16 personas, managed initial onboarding / Platform Ops AI controls in SOW Phase 1.

**Prototype choices:** exact five collection groups, Platform Ops as setup approver, one role per user, self-service-ish demo tenant creation, local JWT.

Frame every demo screen as: *illustrates direction; does not claim client sign-off.*

---

## Ask / next decisions (45 seconds)

1. Approve organization-specific fields and mandatory rules.
2. Confirm setup approver and activation gates (setup approval ≠ go-live).
3. Lock RBAC/ABAC (P-07) before entitlement logic hardens.
4. Agree Admin BFF vs ownership inside Governance/AI services.
5. Sequence: invitation provisioning, service layer, real DB migrations, production audit.

---

## Closing line

> “This POC proves the Admin *journey and contracts* end to end. Production work starts when client and design freeze onboarding fields, approval authority, activation gates, and permissions — then we replace provisional defaults without rewriting the business-command shape of the API.”

---

## Optional live demo (8 minutes)

1. Platform Ops — all tenants visible; create demo tenant.  
2. Harbor Admin — only Harbor; incomplete submit → `409`.  
3. Complete sections + owner → submit → Platform Ops return → resubmit → approve.  
4. Create user/team; mark unavailable (`REVIEW_REQUIRED` if desk claims); offboard → login fails.  
5. Toggle feature with reason → Audit Trail.  
6. Cross-tenant claim list → `403`. Claims overview stays read-only.
