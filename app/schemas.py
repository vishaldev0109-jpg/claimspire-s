from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class LoginIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(pattern=r'^[a-z][a-z0-9-]{2,79}$')
    operating_model: str = 'HYBRID'

class TenantPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    operating_model: str | None = None
    status: str | None = None

class TenantOut(ORMModel):
    id: str
    name: str
    slug: str
    operating_model: str
    status: str
    created_at: datetime

class RoleOut(ORMModel):
    code: str
    name: str
    purpose: str
    primary_surface: str

class UserCreate(BaseModel):
    tenant_id: str | None = None
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=10)
    role_code: str

class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    role_code: str | None = None
    is_active: bool | None = None

class UserOut(ORMModel):
    id: str
    tenant_id: str | None
    name: str
    email: str
    role_code: str
    is_active: bool
    created_at: datetime

class FlagCreate(BaseModel):
    reason: str = Field(min_length=5, max_length=300)
    tenant_id: str | None = None
    key: str = Field(pattern=r'^[A-Z][A-Z0-9_]{2,79}$')
    description: str = ''
    enabled: bool = False

class FlagPatch(BaseModel):
    enabled: bool
    reason: str = Field(min_length=5, max_length=300)

class FlagOut(ORMModel):
    id: str
    tenant_id: str
    key: str
    description: str
    enabled: bool
    updated_at: datetime

class WorkflowCreate(BaseModel):
    tenant_id: str | None = None
    key: str = Field(pattern=r'^[a-z][a-z0-9_]{2,89}$')
    name: str = Field(min_length=2)
    description: str = ''
    stages: list[str] = Field(min_length=1)
    active: bool = True

class WorkflowPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    stages: list[str] | None = None
    active: bool | None = None

class WorkflowOut(ORMModel):
    id: str
    tenant_id: str
    key: str
    name: str
    description: str
    stages: list[str]
    active: bool

class LOBCreate(BaseModel):
    tenant_id: str | None = None
    code: str = Field(pattern=r'^[A-Z][A-Z0-9_]{1,49}$')
    name: str = Field(min_length=2)
    enabled: bool = True

class LOBOut(ORMModel):
    id: str
    tenant_id: str
    code: str
    name: str
    enabled: bool

class IntegrationOut(ORMModel):
    id: str
    tenant_id: str
    name: str
    category: str
    status: str
    description: str
    last_checked_at: datetime | None

class IntegrationCreate(BaseModel):
    tenant_id: str | None = None
    name: str
    category: str
    description: str = ''
    status: str = 'NOT_CONFIGURED'

class IntegrationPatch(BaseModel):
    status: str
    description: str | None = None

class AIUseCaseOut(ORMModel):
    id: str
    tenant_id: str
    key: str
    name: str
    description: str
    enabled: bool
    mode: str

class AIUseCasePatch(BaseModel):
    enabled: bool
    reason: str = Field(min_length=5, max_length=300)

class ClaimOut(ORMModel):
    id: str
    tenant_id: str
    claim_number: str
    claimant_name: str
    lob_code: str
    location: str
    status: str
    severity: str
    desk_adjuster_id: str | None
    created_at: datetime

class AssignmentOut(ORMModel):
    id: str
    tenant_id: str
    claim_id: str
    assignee_name: str
    assignment_type: str
    status: str
    created_at: datetime

class QAReviewOut(ORMModel):
    id: str
    tenant_id: str
    claim_id: str
    package_ref: str
    status: str
    notes: str
    created_at: datetime

class FinancialItemOut(ORMModel):
    id: str
    tenant_id: str
    claim_id: str
    item_type: str
    amount: Decimal
    status: str
    created_at: datetime

class AuditOut(ORMModel):
    id: str
    tenant_id: str | None
    actor_id: str | None
    action: str
    entity_type: str
    entity_id: str | None
    detail: dict[str, Any]
    created_at: datetime


# v0.3 demo organization/workforce flows. Five collection sections are proposed placeholders.
class SetupSectionIn(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)

class SetupSubmitIn(BaseModel):
    reason: str = Field(min_length=5, max_length=300)

class SetupDecisionIn(BaseModel):
    decision: str = Field(pattern=r'^(APPROVE|RETURN_FOR_CHANGES)$')
    note: str = Field(min_length=5, max_length=500)

class SetupOwnerIn(BaseModel):
    responsible_user_id: str

class OrganizationSetupOut(ORMModel):
    id: str
    tenant_id: str
    organization_type: str
    responsible_user_id: str | None
    sections: dict[str, Any]
    status: str
    submitted_by_id: str | None
    approved_by_id: str | None
    review_note: str
    created_at: datetime
    updated_at: datetime

class OrganizationTeamCreate(BaseModel):
    tenant_id: str | None = None
    name: str = Field(min_length=2, max_length=120)
    team_type: str = Field(default='CLAIMS_OPERATIONS', max_length=50)
    parent_team_id: str | None = None
    manager_user_id: str | None = None

class OrganizationTeamOut(ORMModel):
    id: str
    tenant_id: str
    name: str
    team_type: str
    parent_team_id: str | None
    manager_user_id: str | None
    status: str
    created_at: datetime

class WorkforceChangeIn(BaseModel):
    status: str = Field(pattern=r'^(AVAILABLE|UNAVAILABLE|OFFBOARDED)$')
    reason: str = Field(min_length=5, max_length=300)


class OrganizationTeamMemberCreate(BaseModel):
    user_id: str
