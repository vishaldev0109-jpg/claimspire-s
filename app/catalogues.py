"""Shared demo catalogues for organization and tenant lifecycle values."""

ORG_TYPES = frozenset(('CARRIER_TPA', 'IA_FIRM'))
OPERATING_MODELS = frozenset(('HYBRID', 'FIELD', 'DESK_ONLY', 'CAT'))
TENANT_STATUSES = frozenset(('REGISTERED', 'ACTIVE', 'SUSPENDED'))
SETUP_STATUSES = frozenset(('DRAFT', 'IN_REVIEW', 'APPROVED', 'CHANGES_REQUESTED'))
PRIVILEGED_TENANT_ROLES = frozenset(('TENANT_IT_ADMIN',))
WORKFORCE_STATUSES = frozenset(('AVAILABLE', 'UNAVAILABLE', 'OFFBOARDED'))
