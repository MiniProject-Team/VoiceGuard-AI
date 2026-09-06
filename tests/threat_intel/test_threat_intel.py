import json
from threat_intel.taxonomy import AttackFamily,AttackMetadata,attack_family
from threat_intel.indicators import derive_indicators
from threat_intel.campaign import analyze_campaign
from threat_intel.feeds import LocalThreatFeed
from threat_intel.scoring import policy_recommendation,threat_intelligence_risk,incident_summary
def test_taxonomy_and_unknown():assert attack_family("VOICE_CLONING")==AttackFamily.VOICE_CLONING and attack_family("made_up")==AttackFamily.UNKNOWN and AttackMetadata.from_mapping({}).language=="UNKNOWN"
def test_clone_indicator():assert any(x["name"]=="synthetic_high_match" and not x["proof_of_attack"] for x in derive_indicators({"synthetic_probability":.9,"speaker_similarity":.9}))
def test_campaign_is_cautious():
 e=[{"source_id":"pseudo","timestamp":f"2026-01-01T00:0{i}:00Z","risk_level":"CRITICAL","attack_family":"UNKNOWN"} for i in range(3)];r=analyze_campaign(e)[0];assert r["assessment"]=="possible coordinated activity" and r["confidence"]=="MEDIUM"
def test_feed_and_policy(tmp_path):
 p=tmp_path/"feed.json";p.write_text(json.dumps({"known_attack_patterns":["synthetic_high_match"]}));assert LocalThreatFeed(p).get_indicators()==["synthetic_high_match"]
 assert not policy_recommendation({"event_count":3,"risk_distribution":{"CRITICAL":2}})["automatic_change_applied"]
 assert threat_intelligence_risk(["x"],{"enabled":False})["risk"]==0
def test_incident_summary_is_allowlisted():assert "raw_audio" not in incident_summary({"risk_score":90,"raw_audio":"bad"})
