from .benchmark import grouped_metrics
def evaluate_channels(rows,minimum=20,threshold=.5):return grouped_metrics(rows,"channel_type",minimum,threshold)
def channel_attack_matrix(rows,minimum=20,threshold=.5):
    result={}
    for family in sorted({str(r.get("attack_family") or "UNKNOWN") for r in rows}):result[family]={x["group"]:x for x in grouped_metrics([r for r in rows if str(r.get("attack_family") or "UNKNOWN")==family],"channel_type",minimum,threshold)}
    return result
