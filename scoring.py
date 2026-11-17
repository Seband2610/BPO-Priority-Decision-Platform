
def calculate_priority(request):
    """
    Calculates a request priority using the original BPO scoring rules.
    """

    urgency = int(request["urgency"])
    sla_hours = int(request["sla_hours"])
    customer_tier = str(request["customer_tier"]).strip().lower()

    score = 0
    reasons = []

    # Urgency score
    if urgency >= 9:
        score += 5
        reasons.append("Very high urgency (+5)")
    elif urgency >= 7:
        score += 3
        reasons.append("High urgency (+3)")
    elif urgency >= 4:
        score += 2
        reasons.append("Moderate urgency (+2)")
    else:
        score += 1
        reasons.append("Low urgency (+1)")

    # SLA score
    if sla_hours <= 2:
        score += 4
        reasons.append("Critical SLA (+4)")
    elif sla_hours <= 4:
        score += 3
        reasons.append("Short SLA (+3)")
    elif sla_hours <= 8:
        score += 2
        reasons.append("Limited SLA (+2)")

    # Customer tier score
    if customer_tier == "premium":
        score += 2
        reasons.append("Premium customer (+2)")

    # Priority classification
    if score >= 9:
        priority = "CRITICAL"
    elif score >= 7:
        priority = "HIGH"
    elif score >= 4:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "priority_score": score,
        "priority": priority,
        "reason": "; ".join(reasons)
    }
