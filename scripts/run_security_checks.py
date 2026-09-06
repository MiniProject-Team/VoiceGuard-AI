from __future__ import annotations
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import yaml
from security.audit import verify_audit_chain
from security.privacy import assert_privacy_defaults
from evaluation.report import write_json
PATTERN=re.compile(r"(?i)(API_KEY|SECRET|TOKEN)\s*=|PRIVATE KEY")
def secret_findings():
 findings=[];skip={"node_modules",".git","models","reports","dist","data"}
 for path in ROOT.rglob("*"):
  if not path.is_file() or any(part in skip for part in path.parts):continue
  try:
   for line,text in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
    if PATTERN.search(text) and "PATTERN=" not in text:findings.append({"file":str(path.relative_to(ROOT)),"line":line})
  except (UnicodeDecodeError,OSError):pass
 return findings
def main():
 security=yaml.safe_load((ROOT/"configs/security.yaml").read_text());privacy=yaml.safe_load((ROOT/"configs/privacy.yaml").read_text());checks={}
 checks["Phase 3 Model"]=(ROOT/"models/best_model/model.pt").is_file();checks["Phase 4 Model"]=(ROOT/"models/speaker_verification/model_cache/embedding_model.ckpt").is_file();checks["Risk Config"]=(ROOT/"configs/risk_engine.yaml").is_file()
 try:assert_privacy_defaults(privacy);checks["Privacy Config"]=True
 except Exception:checks["Privacy Config"]=False
 checks["Upload Limits"]=0<float(security["uploads"]["max_size_mb"])<=50 and 0<int(security["uploads"]["max_duration_seconds"])<=900;checks["Restricted CORS"]=not security["cors"]["allow_wildcard"] and "*" not in security["cors"]["allowed_origins"];checks["Debug Disabled"]=security["debug"] is False;checks["Audit Integrity"]=verify_audit_chain(ROOT/security["audit"]["path"])["valid"];checks["Frontend Build"]=(ROOT/"frontend/dist/index.html").is_file();checks["WebSocket"]=subprocess.run([sys.executable,"-m","pytest","tests/api/test_websocket.py","-q"],cwd=ROOT,capture_output=True).returncode==0;findings=secret_findings();checks["Secrets Check"]=not findings
 inventory=subprocess.run([sys.executable,"-m","pip","freeze"],capture_output=True,text=True).stdout;package=ROOT/"frontend/package-lock.json";inventory+="\nFrontend lockfile: "+("present" if package.exists() else "missing")+"\n";(ROOT/"reports/phase9").mkdir(parents=True,exist_ok=True);(ROOT/"reports/phase9/dependency_inventory.txt").write_text(inventory,encoding="utf-8");summary={"checks":checks,"secret_findings":findings,"all_passed":all(checks.values()),"disclaimer":"Dependency inventory is not a vulnerability assessment."};write_json(ROOT/"reports/phase9/security_checks.json",summary);print("VOICEGUARD READINESS CHECK\n");[print(f"{name:<28} {'PASS' if passed else 'FAIL'}") for name,passed in checks.items()];sys.exit(0 if summary["all_passed"] else 1)
if __name__=="__main__":main()
