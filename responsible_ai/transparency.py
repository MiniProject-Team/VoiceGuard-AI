MODEL_ANALYSIS="VoiceGuard analyzes acoustic and speaker-verification signals associated with synthetic or impersonated speech."
SCORE_MEANING="The risk score is decision-support evidence about an interaction, not proof of identity, intent, guilt, or criminal conduct."
SECONDARY_VERIFICATION="VoiceGuard detected characteristics associated with synthetic speech and recommends independent verification."
LIMIT="Outputs must not independently determine employment, disciplinary, criminal, or legal outcomes."
def explanation(risk_level,reasons=None):return {"summary":SECONDARY_VERIFICATION if str(risk_level).upper() in {"HIGH","CRITICAL"} else "VoiceGuard found no high-risk signal, but detection is not a guarantee.","what_is_analyzed":MODEL_ANALYSIS,"score_meaning":SCORE_MEANING,"limitations":LIMIT,"reasons":list(reasons or [])}
