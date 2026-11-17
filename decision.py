
def make_decision(request):
    """
    Determines whether a BPO request needs critical attention.
    """

    priority = request["priority"]

    critical = priority in ["CRITICAL", "HIGH"]

    if critical:
        decision = "CRITICAL ATTENTION"
        reason = (
            f"Priority is {priority}. "
            "The request requires immediate attention."
        )
    else:
        decision = "NORMAL PROCESSING"
        reason = (
            f"Priority is {priority}. "
            "The request can follow the normal process."
        )

    return {
        "decision": decision,
        "decision_reason": reason
    }
