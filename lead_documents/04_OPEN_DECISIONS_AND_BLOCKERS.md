# Admin Surface — Open Decisions, Dependencies and Safe Workarounds

**Use as a discussion register.** These are issues to confirm from project source documents and proposed questions for design/architecture owners; they are not claims that a specific client has rejected a solution. Severity describes whether *production implementation* needs a decision, not whether a local demo can be built.

| ID | Decision / dependency | Why it matters | Suggested owner | Production impact | What can be developed now |
|---|---|---|---|---|---|
| ADM-01 | Signed scope vs Aubergine Gantt §4 additional Admin screens | Avoid implementing full tenant self-service or advanced admin modules as Phase 1 commitments | Client Product / GoML Lead / Aubergine | Final screen inventory and delivery commitment | Demo shell and clearly labeled optional modules |
| ADM-02 | Admin user access and Persona-to-permission matrix (SOW P-07) | Critical controls need approved role/attribute/SoD policy | Client + GoML Security | PDP build lock | Local demo admin roles, 401/403 and tenant-scope tests |
| ADM-03 | Operating model toggle catalogue (SOW P-02) | Must know accepted capability names/defaults and their effective scope | Client Product | Production AppConfig schemas and permissions | Generic feature flag DTO and sample records |
| ADM-04 | Authority thresholds (SOW P-08) | Governance approvals cannot be invented | Claims/Finance leadership | Reserve/payment/approval-policy config | Define schema and validation interfaces only |
| ADM-05 | Classification/retention/legal hold (SOW P-05/P-09) | Sensitive data and audit retention need authority | Legal/Security | Production policy and schema | Seed nonsensitive demo data; audit event shape |
| ADM-06 | AI CHK mapping, approved use cases/model/prompt versions | AI Admin controls must be tied to approved evidence | AI Governance / GoML | Real model configuration and deployment | Demo register; versioned API draft; kill-switch state machine |
| ADM-07 | Final Aubergine screen behavior and owners | A clickable demo is not proof of UX sign-off | Design / Product | Final UI/API contract for production | Screen mocks, empty/error states, demo acceptance |
| ADM-08 | Service ownership: Admin API vs Governance/AI Gateway domains | Avoid duplicate policy engines/databases | GoML Architecture | Deployed services and database ownership | FastAPI modular adapters / interface-first contracts |
| ADM-09 | What operational KPIs can Admin see by role and tenant? | Prevent cross-tenant info leakage or exposing restricted SIU/finance details | Claims Ops / Compliance | Dashboard field-level ABAC | Nonsensitive, aggregated synthetic records |
| ADM-10 | Config change approval, emergency controls and rollback | Kill switches and governance overrides need safe application semantics | Security / Platform Ops | Production mutation workflow | Reason fields, local audit, mocked apply status; do not claim effective AWS change |
| ADM-11 | Integration inventory, credential ownership, readiness meaning | Fake 'connected' statuses would mislead if presented as real | Client IT / Integration Lead | Actual provider integrations and credential handling | Metadata catalogue labelled `CONNECTED_DEMO` |

## Recommended decision categories

**Blocking a production contract:** ADM-01, ADM-02, ADM-03, ADM-06, ADM-08. Resolve before locking API/UI ownership and permissions.

**Blocking a particular business configuration:** ADM-04, ADM-05, ADM-09, ADM-10, ADM-11. Design DTOs and tests now; wait before enabling meaningful production changes.

**Not blocking the prototype:** All of the above. Demo values and read models are intentionally synthetic.

## Questions to ask at the next stakeholder review

1. Which exact Admin UI screens from Aubergine section 4 are agreed for the Phase 1 internal Admin surface, and which are future backlog?
2. Should the initial tenant be configured through internal operational tooling only, or are specific tenant-facing administration screens required at go-live?
3. Who may read/change each type of AI use-case setting and kill switch, and what approval or reason-code controls apply?
4. Who owns the approved persona-to-action RBAC/ABAC/SoD matrix and can confirm the P-07 baseline?
5. Do Admin dashboards show claim-level details or only aggregate summaries, and which statuses are sensitive by role?
6. Will configuration APIs be part of the Governance/AI Gateway services or one Admin orchestration/BFF layer?
7. Which configuration changes require versioning, rollback, explicit effective-state confirmation and audit evidence?

## Decision record template

| Field | Value |
|---|---|
| Decision ID | ADR/DEC-... |
| Business owner | ... |
| Design/technical owner | ... |
| Source row / SOW / CHK ID | ... |
| Proposed behavior | ... |
| Other considered options | ... |
| Decision status | Proposed / Approved / Deferred |
| UI impact | ... |
| API/data/security impact | ... |
| Approval date / link | ... |

Keep the tracker current. A decision should not be marked approved without an authoritative owner/source.
