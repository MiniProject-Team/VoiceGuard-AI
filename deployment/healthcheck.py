import json,sys,urllib.request
try:
 with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health/ready",timeout=8) as response:data=json.load(response)
 healthy=response.status==200 and data.get("status")=="ready" and all(value=="ready" for value in data.get("components",{}).values())
except Exception:healthy=False
raise SystemExit(0 if healthy else 1)
