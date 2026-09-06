import pytest
from security.input_validation import safe_filename,validate_speaker_id,validate_upload_header
from security.policy import enforce_fail_safe,policy_consistent,validate_explanation
def test_path_and_signature_validation():
 assert validate_speaker_id("CEO_001")=="CEO_001"
 with pytest.raises(ValueError):safe_filename("../secret.wav")
 with pytest.raises(ValueError):validate_upload_header(b"not wave","wav")
def test_fail_safe_and_policy():
 result=enforce_fail_safe({"errors":["phase3:RuntimeError"],"risk_level":"LOW","decision":"ALLOW","recommended_action":"proceed"});assert result["status"]=="SYSTEM_DEGRADED" and result["decision"]=="STEP_UP_VERIFICATION" and result["risk_level"]=="UNKNOWN"
 assert policy_consistent("CRITICAL","BLOCK_OR_ESCALATE");assert not validate_explanation({"risk_level":"CRITICAL","reasons":[]})
