import json
from security.audit import AuditLog,verify_audit_chain
def test_audit_chain_detects_tampering(tmp_path):
 path=tmp_path/"audit.jsonl";log=AuditLog(path,"abc");log.append("SESSION_CREATED","SESSION_A");log.append("ANALYSIS_COMPLETED","SESSION_A",risk_score=90,risk_level="CRITICAL",decision="BLOCK_OR_ESCALATE");assert verify_audit_chain(path)["valid"]
 rows=path.read_text().splitlines();record=json.loads(rows[0]);record["event_type"]="TAMPERED";rows[0]=json.dumps(record);path.write_text("\n".join(rows));assert not verify_audit_chain(path)["valid"]
