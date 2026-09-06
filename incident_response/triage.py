from .severity import assess_severity
from .incident import IncidentStatus
def triage(incident,role,**context):
 from governance.roles import Permission,authorize
 authorize(role,Permission.INCIDENT_TRIAGE);incident.severity=assess_severity(incident.risk_score,incident.risk_level,**context);incident.status=IncidentStatus.TRIAGED;incident.timeline.append({"event":"TRIAGED","severity":incident.severity.name,"by_role":str(getattr(role,"value",role))});return incident
