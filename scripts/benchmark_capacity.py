from __future__ import annotations
import json,platform,sys,time,tracemalloc
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
from api.dependencies import load_api_config
from api.main import create_app
def main():
 config=load_api_config();config["runtime"]["use_mock_models"]=True;rows=[];tracemalloc.start()
 with TestClient(create_app(config)) as client:
  for count in (1,2,5):
   def flow(_):
    sid=client.post("/api/v1/sessions",json={}).json()["session_id"];client.post(f"/api/v1/sessions/{sid}/start");return client.get(f"/api/v1/sessions/{sid}").status_code
   started=time.perf_counter()
   with ThreadPoolExecutor(max_workers=count) as pool:statuses=list(pool.map(flow,range(count)))
   rows.append({"concurrency":count,"mode":"MOCK MODEL CONTROL-PLANE TEST","elapsed_seconds":time.perf_counter()-started,"errors":sum(x!=200 for x in statuses)})
 current,peak=tracemalloc.get_traced_memory();result={"hardware":{"platform":platform.platform(),"processor":platform.processor() or "NOT REPORTED","logical_cpus":__import__('os').cpu_count(),"ram":"NOT MEASURED","gpu":"NOT TESTED"},"startup_time":"NOT MEASURED WITH REAL MODELS","python_tracemalloc_peak_mb":peak/1048576,"tests":rows,"warning":"This tests local API session concurrency with mock models, not inference throughput or telecom scale."};out=ROOT/"reports/phase11";out.mkdir(parents=True,exist_ok=True);(out/"capacity_report.json").write_text(json.dumps(result,indent=2));(out/"capacity_report.md").write_text("# Capacity report\n\n"+json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
