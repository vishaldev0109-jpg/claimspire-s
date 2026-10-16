"""Local demo authentication/authorization. NOT a replacement for production Cognito/PDP."""
import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.config import JWT_SECRET, JWT_EXPIRE_MINUTES
from app.database import get_db
from app.models import Tenant, User

bearer = HTTPBearer(auto_error=False)
ADMIN_ROLES = frozenset({'PLATFORM_OPS', 'TENANT_IT_ADMIN'})

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 250_000)
    return 'pbkdf2_sha256$250000$' + base64.urlsafe_b64encode(salt).decode() + '$' + base64.urlsafe_b64encode(dk).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        method, rounds, salt, expected = stored.split('$')
        if method != 'pbkdf2_sha256':
            return False
        derived = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.urlsafe_b64decode(salt), int(rounds))
        return hmac.compare_digest(derived, base64.urlsafe_b64decode(expected))
    except (ValueError, TypeError):
        return False

def create_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': user.id, 'iat': now, 'exp': now + timedelta(minutes=JWT_EXPIRE_MINUTES)}, JWT_SECRET, algorithm='HS256')

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Bearer token required')
    try:
        claims = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        user_id = claims['sub']
    except (jwt.InvalidTokenError, KeyError):
        raise HTTPException(status_code=401, detail='Invalid or expired token') from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail='User inactive or not found')
    return user

def require_admin(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    """Admin role + tenant membership. Suspended tenants cannot use Admin APIs."""
    if user.role_code not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail='Admin role required')
    if user.role_code != 'PLATFORM_OPS':
        if not user.tenant_id:
            raise HTTPException(status_code=403, detail='Tenant membership required for Admin access')
        tenant = db.get(Tenant, user.tenant_id)
        if not tenant:
            raise HTTPException(status_code=403, detail='Tenant membership invalid')
        if tenant.status == 'SUSPENDED':
            raise HTTPException(status_code=403, detail='Tenant is SUSPENDED; Admin access denied')
    return user

def require_platform(user: User = Depends(require_admin)) -> User:
    if user.role_code != 'PLATFORM_OPS':
        raise HTTPException(status_code=403, detail='Platform operations role required')
    return user

def is_platform(user: User) -> bool:
    return user.role_code == 'PLATFORM_OPS'

def permitted_tenant(user: User, requested_tenant: str | None) -> str | None:
    """Resolve list/filter scope.

    Platform Ops: None means all demo tenants; a concrete id scopes to one tenant.
    Tenant Admins: always forced to their own tenant_id (UI filter is not a security boundary).
    """
    if is_platform(user):
        return requested_tenant
    if not user.tenant_id:
        raise HTTPException(status_code=403, detail='Tenant membership required')
    if requested_tenant and requested_tenant != user.tenant_id:
        raise HTTPException(status_code=403, detail='Cross-tenant access denied')
    return user.tenant_id

def mutation_tenant(user: User, requested_tenant: str | None) -> str:
    tenant_id = permitted_tenant(user, requested_tenant)
    if not tenant_id:
        raise HTTPException(status_code=422, detail='tenant_id required for platform operator changes')
    return tenant_id

def assert_resource_access(user: User, tenant_id: str | None) -> None:
    """Deny Tenant Admins from touching another organization's resource."""
    if is_platform(user):
        return
    if not user.tenant_id:
        raise HTTPException(status_code=403, detail='Tenant membership required')
    if tenant_id != user.tenant_id:
        raise HTTPException(status_code=403, detail='Cross-tenant access denied')
