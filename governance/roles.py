from enum import Enum

class Permission(str, Enum):
    SESSION_READ="SESSION_READ"; SESSION_REVIEW="SESSION_REVIEW"
    INCIDENT_READ="INCIDENT_READ"; INCIDENT_CREATE="INCIDENT_CREATE"; INCIDENT_TRIAGE="INCIDENT_TRIAGE"; INCIDENT_CLOSE="INCIDENT_CLOSE"
    POLICY_READ="POLICY_READ"; POLICY_UPDATE="POLICY_UPDATE"; POLICY_APPROVE="POLICY_APPROVE"
    ENROLLMENT_DELETE="ENROLLMENT_DELETE"; SESSION_DELETE="SESSION_DELETE"
    AUDIT_READ="AUDIT_READ"; OVERRIDE_APPROVE="OVERRIDE_APPROVE"
    CONFIG_MANAGE="CONFIG_MANAGE"; INTEGRATION_MANAGE="INTEGRATION_MANAGE"; MODEL_APPROVE="MODEL_APPROVE"

class Role(str, Enum):
    VIEWER="VIEWER"; ANALYST="ANALYST"; SECURITY_OPERATOR="SECURITY_OPERATOR"
    SUPERVISOR="SUPERVISOR"; ADMIN="ADMIN"; AUDITOR="AUDITOR"

ROLE_PERMISSIONS={
 Role.VIEWER:{Permission.SESSION_READ},
 Role.ANALYST:{Permission.SESSION_READ,Permission.SESSION_REVIEW,Permission.INCIDENT_READ,Permission.INCIDENT_CREATE,Permission.POLICY_READ},
 Role.SECURITY_OPERATOR:{Permission.SESSION_READ,Permission.SESSION_REVIEW,Permission.INCIDENT_READ,Permission.INCIDENT_CREATE,Permission.INCIDENT_TRIAGE,Permission.POLICY_READ},
 Role.SUPERVISOR:{Permission.SESSION_READ,Permission.SESSION_REVIEW,Permission.INCIDENT_READ,Permission.INCIDENT_CREATE,Permission.INCIDENT_TRIAGE,Permission.INCIDENT_CLOSE,Permission.POLICY_READ,Permission.POLICY_APPROVE,Permission.OVERRIDE_APPROVE,Permission.MODEL_APPROVE},
 Role.ADMIN:set(Permission)-{Permission.AUDIT_READ,Permission.OVERRIDE_APPROVE,Permission.INCIDENT_CLOSE,Permission.MODEL_APPROVE},
 Role.AUDITOR:{Permission.SESSION_READ,Permission.INCIDENT_READ,Permission.POLICY_READ,Permission.AUDIT_READ},
}
def _role(value): return value if isinstance(value,Role) else Role(str(value).upper())
def _permission(value): return value if isinstance(value,Permission) else Permission(str(value).upper())
def has_permission(role, permission)->bool:
    try:return _permission(permission) in ROLE_PERMISSIONS[_role(role)]
    except (ValueError,KeyError):return False
def authorize(role, permission)->None:
    if not has_permission(role,permission):raise PermissionError(f"Role {role} lacks permission {_permission(permission).value}.")

# Convenient centralized constants.
for _p in Permission: globals()[_p.name]=_p
