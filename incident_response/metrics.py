from datetime import datetime
def incident_metrics(incidents):
 rows=list(incidents);result={"incidents_created":len(rows),"SEV1_count":sum(x.severity.name=="SEV1" for x in rows),"SEV2_count":sum(x.severity.name=="SEV2" for x in rows),"false_positive_incidents":sum((x.resolution or "").lower().find("false positive")>=0 for x in rows)}
 for label,event in (("time_to_triage","TRIAGED"),("time_to_containment","CONTAINED"),("time_to_resolution","RESOLVED")):
  values=[]
  for x in rows:
   match=next((e for e in x.timeline if e.get("event")==event and e.get("at")),None)
   if match:values.append((datetime.fromisoformat(match["at"])-datetime.fromisoformat(x.created_at)).total_seconds())
  result[label]=sum(values)/len(values) if values else None
 return result
