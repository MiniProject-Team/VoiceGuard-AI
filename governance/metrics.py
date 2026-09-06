from collections import Counter
EVENT_METRICS={"AI_DECISION_OVERRIDDEN":"overrides","POLICY_ACTIVATED":"policy_changes","POLICY_RETIRED":"policy_changes","EXCEPTION_CREATED":"exceptions","MODEL_ACCEPTED":"model_approvals","MODEL_REJECTED":"model_rejections","RETENTION_DELETION":"retention_deletions"}
def governance_metrics(records):
 counts=Counter(EVENT_METRICS.get(x.get("event")) for x in records);counts.pop(None,None);return {name:counts.get(name,0) for name in set(EVENT_METRICS.values())}
