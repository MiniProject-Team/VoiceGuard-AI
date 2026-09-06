from .benchmark import grouped_metrics

def leave_one_generator_out(rows, minimum=20, threshold=.5):
    """Scores held-out generator groups from precomputed predictions; it never retrains."""
    result=grouped_metrics(rows,"generator_family",minimum,threshold)
    for item in result:item["experiment"]="LEAVE_ONE_GENERATOR_OUT";item["training"]="NOT PERFORMED"
    return result

def cross_dataset(rows, train_dataset, validation_dataset, test_dataset, minimum=20, threshold=.5):
    test=[r for r in rows if (r.get("source_dataset") or "UNKNOWN")==test_dataset]
    item=grouped_metrics(test,"source_dataset",minimum,threshold)
    return {"train_dataset":train_dataset,"validation_dataset":validation_dataset,"test_dataset":test_dataset,"training":"NOT PERFORMED","results":item}
