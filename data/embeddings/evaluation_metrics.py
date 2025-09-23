import math

def precision_recall(results, truth):
    """Binary relevance: at least one match in results."""
    retrieved_ids = {(r["make"], r["model"], r["year"]) for r in results}
    return int(truth in retrieved_ids), len(retrieved_ids)