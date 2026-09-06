from collections import Counter
from datetime import datetime, timezone
import hashlib

def analyze_campaign(events: list[dict], window_minutes=60):
    if not events:return []
    groups={}
    for e in events:
        key=(e.get("source_id","UNKNOWN"),e.get("transaction_type","UNKNOWN"));groups.setdefault(key,[]).append(e)
    out=[]
    for key,rows in groups.items():
        if len(rows)<2:continue
        times=[datetime.fromisoformat(str(x["timestamp"]).replace("Z","+00:00")) for x in rows if x.get("timestamp")]
        span=(max(times)-min(times)).total_seconds()/60 if len(times)>1 else 0
        if span>window_minutes:continue
        digest=hashlib.sha256((str(key)+str(min(times) if times else "UNKNOWN")).encode()).hexdigest()[:12].upper()
        critical=sum(x.get("risk_level")=="CRITICAL" for x in rows)
        out.append({"campaign_id":f"CAMPAIGN_{digest}","event_count":len(rows),"time_window":{"minutes":round(span,2)},"risk_distribution":dict(Counter(x.get("risk_level","UNKNOWN") for x in rows)),"attack_family_distribution":dict(Counter(x.get("attack_family","UNKNOWN") for x in rows)),"confidence":"MEDIUM" if len(rows)>=3 and critical>=2 else "LOW","assessment":"possible coordinated activity"})
    return out
