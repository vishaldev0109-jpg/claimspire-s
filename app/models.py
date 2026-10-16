"""Small, generic demo models. They do not replace ClaimSpire domain services."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def uuid_str() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TimeStamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class Tenant(Base, TimeStamped):
    __tablename__ = 'tenants'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    operating_model: Mapped[str] = mapped_column(String(40), default='HYBRID')
    # REGISTERED = created but not operational; ACTIVE = demo-operational after activation gate.
    status: Mapped[str] = mapped_column(String(30), default='REGISTERED')

class Role(Base):
    __tablename__ = 'roles'
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(140))
    purpose: Mapped[str] = mapped_column(Text)
    primary_surface: Mapped[str] = mapped_column(String(40))

class User(Base, TimeStamped):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str | None] = mapped_column(ForeignKey('tenants.id'), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    role_code: Mapped[str] = mapped_column(ForeignKey('roles.code'))
    password_hash: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class FeatureFlag(Base):
    __tablename__ = 'feature_flags'
    __table_args__ = (UniqueConstraint('tenant_id', 'key', name='uq_feature_tenant_key'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    key: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(300), default='')
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class WorkflowTemplate(Base):
    __tablename__ = 'workflow_templates'
    __table_args__ = (UniqueConstraint('tenant_id', 'key', name='uq_workflow_tenant_key'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    key: Mapped[str] = mapped_column(String(90))
    name: Mapped[str] = mapped_column(String(140))
    description: Mapped[str] = mapped_column(String(300), default='')
    stages: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class LineOfBusiness(Base):
    __tablename__ = 'lines_of_business'
    __table_args__ = (UniqueConstraint('tenant_id', 'code', name='uq_lob_tenant_code'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

class Integration(Base):
    __tablename__ = 'integrations'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(35), default='NOT_CONFIGURED')
    description: Mapped[str] = mapped_column(String(300), default='')
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class AIUseCase(Base):
    __tablename__ = 'ai_use_cases'
    __table_args__ = (UniqueConstraint('tenant_id', 'key', name='uq_ai_tenant_key'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    key: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(300), default='')
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mode: Mapped[str] = mapped_column(String(40), default='DEMO_RULE_BASED')

class Claim(Base, TimeStamped):
    __tablename__ = 'claims'
    __table_args__ = (UniqueConstraint('tenant_id','claim_number',name='uq_claim_tenant_number'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    claim_number: Mapped[str] = mapped_column(String(50))
    claimant_name: Mapped[str] = mapped_column(String(120))
    lob_code: Mapped[str] = mapped_column(String(50))
    location: Mapped[str] = mapped_column(String(150), default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    severity: Mapped[str] = mapped_column(String(30), default='MEDIUM')
    desk_adjuster_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)

class Assignment(Base, TimeStamped):
    __tablename__ = 'assignments'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    claim_id: Mapped[str] = mapped_column(ForeignKey('claims.id'), index=True)
    assignee_name: Mapped[str] = mapped_column(String(120))
    assignment_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))

class QAReview(Base, TimeStamped):
    __tablename__ = 'qa_reviews'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    claim_id: Mapped[str] = mapped_column(ForeignKey('claims.id'), index=True)
    package_ref: Mapped[str] = mapped_column(String(75))
    status: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str] = mapped_column(String(300), default='')

class FinancialItem(Base, TimeStamped):
    __tablename__ = 'financial_items'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    claim_id: Mapped[str] = mapped_column(ForeignKey('claims.id'), index=True)
    item_type: Mapped[str] = mapped_column(String(40))
    amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
    status: Mapped[str] = mapped_column(String(40))

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str | None] = mapped_column(ForeignKey('tenants.id'), nullable=True, index=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(90), index=True)
    entity_type: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


# Administration onboarding add-on. These are local demonstration workflow records.
# They are not the final Client-approved tenant self-service feature.
class OrganizationSetup(Base, TimeStamped):
    __tablename__ = 'organization_setups'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), unique=True, index=True)
    organization_type: Mapped[str] = mapped_column(String(30), default='CARRIER_TPA')
    responsible_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    sections: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default='DRAFT')
    version: Mapped[int] = mapped_column(Integer, default=1)
    submitted_by_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    approved_by_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    review_note: Mapped[str] = mapped_column(String(500), default='')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class OrganizationSetupSubmission(Base, TimeStamped):
    """Immutable snapshot of a submitted organization setup version."""
    __tablename__ = 'organization_setup_submissions'
    __table_args__ = (UniqueConstraint('setup_id', 'version', name='uq_setup_submission_version'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    setup_id: Mapped[str] = mapped_column(ForeignKey('organization_setups.id'), index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    version: Mapped[int] = mapped_column(Integer)
    organization_type: Mapped[str] = mapped_column(String(30))
    sections_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    submitted_by_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    submit_reason: Mapped[str] = mapped_column(String(300), default='')
    decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    decided_by_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    decision_note: Mapped[str] = mapped_column(String(500), default='')
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class OrganizationTeam(Base, TimeStamped):
    __tablename__ = 'organization_teams'
    __table_args__ = (UniqueConstraint('tenant_id', 'name', name='uq_org_team_name'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    name: Mapped[str] = mapped_column(String(120))
    team_type: Mapped[str] = mapped_column(String(50), default='CLAIMS_OPERATIONS')
    parent_team_id: Mapped[str | None] = mapped_column(ForeignKey('organization_teams.id'), nullable=True)
    manager_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE')

class WorkforceStatus(Base):
    __tablename__ = 'workforce_statuses'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    status: Mapped[str] = mapped_column(String(30), default='AVAILABLE')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class WorkforceLifecycleEvent(Base):
    __tablename__ = 'workforce_lifecycle_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    old_status: Mapped[str] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class OrganizationTeamMember(Base, TimeStamped):
    __tablename__ = 'organization_team_members'
    __table_args__ = (UniqueConstraint('team_id','user_id',name='uq_team_member'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'), index=True)
    team_id: Mapped[str] = mapped_column(ForeignKey('organization_teams.id'), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
