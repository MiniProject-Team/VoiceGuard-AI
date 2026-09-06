def responsible_ai_metrics(records):
 rows=list(records);total=len(rows);reviewed=[x for x in rows if x.human_action];overrides=[x for x in reviewed if str(x.human_action).endswith("OVERRIDE")]
 def rate(n,d=total):return n/d if d else 0.0
 return {"human_review_rate":rate(len(reviewed)),"override_rate":rate(len(overrides),len(reviewed)),"false_positive_review_rate":rate(sum(str(x.override_reason).endswith("KNOWN_FALSE_POSITIVE") for x in reviewed),len(reviewed)),"false_negative_discovery_rate":0.0,"high_uncertainty_review_rate":0.0}
