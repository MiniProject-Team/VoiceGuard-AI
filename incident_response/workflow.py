from datetime import datetime,timezone
from .incident import IncidentStatus
TRANSITIONS={IncidentStatus.OPEN:{IncidentStatus.TRIAGED},IncidentStatus.TRIAGED:{IncidentStatus.INVESTIGATING,IncidentStatus.CONTAINED},IncidentStatus.INVESTIGATING:{IncidentStatus.CONTAINED,IncidentStatus.RESOLVED},IncidentStatus.CONTAINED:{IncidentStatus.INVESTIGATING,IncidentStatus.RESOLVED},IncidentStatus.RESOLVED:{IncidentStatus.CLOSED}}
DEFENSIVE_ACTIONS={"HOLD_TRANSACTION","REQUIRE_MFA","TRUSTED_CALLBACK","SUPERVISOR_APPROVAL","REVOKE_SESSION","NOTIFY_SECURITY"}
def transition(incident,status,role,resolution=None,audit=None):
 from governance.roles import Permission,authorize
 target=IncidentStatus(status);authorize(role,Permission.INCIDENT_CLOSE if target==IncidentStatus.CLOSED else Permission.INCIDENT_TRIAGE)
 if target not in TRANSITIONS.get(incident.status,set()):raise ValueError("Invalid incident transition.")
 if target in {IncidentStatus.RESOLVED,IncidentStatus.CLOSED} and not (resolution or incident.resolution):raise ValueError("Resolution is required.")
 incident.status=target;incident.resolution=resolution or incident.resolution;incident.timeline.append({"at":datetime.now(timezone.utc).isoformat(),"event":target.value,"by_role":str(getattr(role,"value",role))})
 if target==IncidentStatus.CLOSED and audit:audit.append("INCIDENT_CLOSED",session_id=incident.session_id,actor_role=role,incident_id=incident.incident_id,resolution=incident.resolution)
 return incident
def containment_action(incident,action,integration_policy_enabled=False):
 action=str(action).upper()
 if action not in DEFENSIVE_ACTIONS:raise ValueError("Unsupported defensive action.")
 return {"incident_id":incident.incident_id,"action":action,"mode":"EXECUTE" if integration_policy_enabled else "RECOMMEND_ONLY"}
