def disagreement_profile(synthetic_probability=None,speaker_similarity=None,risk_score=None,context=None,synthetic_threshold=.8,match_threshold=.75):
    fake=synthetic_probability is not None and float(synthetic_probability)>=synthetic_threshold;match=speaker_similarity is not None and float(speaker_similarity)>=match_threshold
    clone=fake and match; mismatch=speaker_similarity is not None and not match; critical=bool((context or {}).get("sensitive")) or (risk_score is not None and float(risk_score)>=80)
    signals={"synthetic_detector":"LIKELY_FAKE" if fake else "LIKELY_REAL" if synthetic_probability is not None else "UNKNOWN","speaker_verifier":"HIGH_MATCH" if match else "MISMATCH" if mismatch else "UNKNOWN","context":"CRITICAL" if critical else "NORMAL"}
    disagreement=len({v for v in signals.values() if v!="UNKNOWN"})>1
    return {"signals":signals,"disagreement":disagreement,"priority":"HIGH" if clone else "MEDIUM" if disagreement else "LOW","result":"possible cloned voice matching enrolled identity" if clone else "signals require contextual review" if disagreement else "no material disagreement observed","proof_of_attack":False}
