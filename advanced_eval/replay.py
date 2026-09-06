from .benchmark import grouped_metrics
def evaluate_replay(rows,minimum=20,threshold=.5):return grouped_metrics(rows,"replay_status",minimum,threshold)
