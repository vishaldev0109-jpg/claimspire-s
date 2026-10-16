# Admin screen map → proposed local APIs

Use this to give the UI designer or frontend developer a simple navigation structure.

| # | Admin page | Cards/table/forms | Primary endpoints | Notes |
|---|---|---|---|---|
| 1 | **Overview Dashboard** | Tenant count, users, claims by stage, assignment/QA/finance status | `GET /admin/dashboard/summary`, `GET /admin/workflow-stages` | High-level synthetic metrics |
| 2 | **Tenant Directory** | Tenant list/detail, editable display name, operating model | `GET/POST /admin/tenants`, `GET/PATCH /admin/tenants/{id}` | Platform Ops may create; tenant admin is own-tenant |
| 3 | **Users & Personas** | 16 persona reference cards, user table, user create/edit | `GET /admin/roles`, `GET/POST /admin/users`, `GET/PATCH /admin/users/{id}` | Identity is local demo |
| 4 | **Lines of Business** | Property, Auto, Liability etc. | `GET/POST /admin/lines-of-business` | Demo taxonomy |
| 5 | **Workflow Templates** | Configurable visual workflow stage list | `GET/POST /admin/workflows`, `PATCH /admin/workflows/{id}` | Not an executable workflow engine |
| 6 | **Features & AI Control** | Feature toggles, AI use-case register, enable/disable reason | `GET/POST/PATCH /admin/features`, `GET/PATCH /admin/ai/use-cases` | No real AI and no AppConfig |
| 7 | **Claims Monitoring** | Search/list claims and statuses | `GET /admin/claims` | **Read-only** synthetic claims |
| 8 | **Dispatch Monitoring** | Field assignments and acceptance status | `GET /admin/assignments` | **Read-only**, no dispatch engine |
| 9 | **QA Monitoring** | Package review statuses and notes | `GET /admin/qa-reviews` | **Read-only**, no package validation engine |
| 10 | **Finance Monitoring** | Request/expense/invoice entries and status | `GET /admin/financial-items` | **Read-only**, never actual payments |
| 11 | **Integration Status** | Provider names and demo connection state | `GET/POST/PATCH /admin/integrations` | Manually simulated status |
| 12 | **Audit Trail** | Who changed configuration, what, when, why | `GET /admin/audit-events` | Local event history; not tamper-proof |

The UI can get navigation metadata from `GET /admin/navigation`.

### Suggested first-page dashboard layout

```text
┌────────────────────────── CLAIMSPIRE ADMIN ──────────────────────────┐
│ Tenant selector         Logged in user             Admin role         │
├──────────────────────────────────────────────────────────────────────┤
│ [Tenants] [Users] [Claims] [Assignments] [QA Reviews] [Finance]      │
│                                                                      │
│ Workflow: FNOL → TRIAGE → DESK → (FIELD) → (QA) → FINANCE → CLOSED   │
│               optional/parallel stages are simplified for demo      │
│                                                                      │
│ Claims by status             Dispatch/QA overview                  │
│ Configured LOBs              Feature/AI switch status              │
│ Integration status           Recent admin change audit             │
└──────────────────────────────────────────────────────────────────────┘
```


## Clickable interface status (lead prototype update)

`GET /demo` now serves a static HTML/CSS/JS console using these APIs. It implements Dashboard, Tenants, Users & Personas, Workflow Setup, Claims Overview, Dispatch Monitoring, QA Monitoring, Finance Monitoring, Features & AI, Integrations, Delivery Readiness and Audit Trail.

This UI is independent of the accepted Aubergine/Figma frontend implementation and must be treated as a review mock, not a final design. The source-of-truth scope remains the signed SOW and approved story-level requirements.
