from security.privacy import pseudonymize,retained_assessment
from security.redaction import redact
def test_pseudonym_and_minimal_retention():
 assert pseudonymize("CEO_Rahul",key=b"test").startswith("SUBJECT_");result=retained_assessment({"session_id":"S","risk_score":1,"raw_audio":b"secret","speaker_embedding":[1,2]});assert result=={"session_id":"S","risk_score":1}
def test_sensitive_redaction():
 value=redact({"authorization":"Bearer secret","note":"mail me user@example.com or +919876543210"});assert value["authorization"]=="[REDACTED]";assert "example.com" not in value["note"] and "9876543210" not in value["note"]
