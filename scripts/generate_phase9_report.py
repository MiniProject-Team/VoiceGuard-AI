from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from evaluation.report import write_json
def read_json(name,default):
 path=ROOT/"reports/phase9"/name
 try:return json.loads(path.read_text(encoding="utf-8"))
 except (FileNotFoundError,json.JSONDecodeError):return default
def main():
 security=read_json("security_checks.json",{"status":"NOT TESTED"});multi=read_json("multilingual_summary.json",{"status":"NOT TESTED"});cal=read_json("calibration.json",{"status":"NOT TESTED"});latency=read_json("latency_summary.json",{"status":"NOT TESTED"});audit=read_json("audit_integrity_report.json",{"status":"NOT TESTED"})
 summary={"phase":"9","security":security,"multilingual":multi,"calibration":cal,"latency":latency,"audit":audit,"risk_score_note":"Risk Score is a decision-support score, not a statistically calibrated probability.","production_ready":False,"limitations":["Available evaluation metadata has no language labels.","Channel conditions are controlled simulations, not carrier recordings.","Prototype audit and session stores are local and single-process.","Authentication, encryption at rest, TLS, SIEM export, and centralized monitoring require production infrastructure."]};write_json(ROOT/"reports/phase9/phase9_summary.json",summary)
 markdown=f"""# VoiceGuard Phase 9 Security and Evaluation Report

## 1. Executive summary
Phase 9 adds risk-based security hardening, privacy-by-design controls, tamper-evident audit records, and reproducible evaluation tooling. It does not claim guaranteed detection or fraud prevention.

## 2. Architecture
Audio remains in memory for inference and is discarded. Structured assessments pass through validation, fail-safe policy, redaction, bounded services, and chained audit logging.

## 3. Privacy controls
Raw audio retention is disabled. Results retain only approved assessment fields. Speaker embeddings are sensitive biometric-like records and require encryption, access control, key rotation, and deletion workflows in production.

## 4. Security controls
Readiness result: `{security.get('all_passed','NOT TESTED')}`. Controls cover restricted CORS, debug disablement, upload signatures and bounds, opaque session IDs, rate/resource limits, secret scanning, safe errors, and confirmation-based session deletion.

## 5. Multilingual evaluation
Status: `{multi.get('status','NOT TESTED')}`. No language or accent is inferred from identity. Absent or undersized groups are explicitly reported as insufficient data.

## 6. Robustness evaluation
See `robustness_results.csv`. Non-clean conditions are labelled **SIMULATED CONDITION** and do not represent real carrier measurements.

## 7. Latency
```json
{json.dumps(latency,indent=2)}
```

## 8. Calibration
Brier score and ECE: `{cal.get('brier_score','NOT TESTED')}`, `{cal.get('expected_calibration_error','NOT TESTED')}`. Softmax output is not assumed perfectly calibrated.

## 9. False positives
See `false_positive_analysis.csv`; identifiers only, never audio content.

## 10. False negatives
See `false_negative_analysis.csv`. Missed synthetic audio receives priority in threshold review while maintaining usable false-positive rates.

## 11. Alert stability
Phase 6 cooldown and temporal smoothing remain enabled. Labeled incident/session data is still required for a representative alert-fatigue measurement.

## 12. Auditability
Audit status: `{audit.get('status','NOT TESTED')}`. Records use SHA-256 chained hashes; this is tamper evidence, not blockchain.

## 13. Known limitations
{chr(10).join('- '+item for item in summary['limitations'])}

## 14. Production recommendations
Deploy HTTPS/WSS, authentication and RBAC, a secrets manager, encrypted databases and embeddings, network segmentation, central monitoring/SIEM, gateway rate limiting, load balancing, model/drift monitoring, enforceable retention, and incident-response procedures.
""";(ROOT/"reports/phase9/phase9_report.md").write_text(markdown,encoding="utf-8");print(ROOT/"reports/phase9/phase9_report.md")
if __name__=="__main__":main()
