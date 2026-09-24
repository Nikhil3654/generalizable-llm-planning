def valid_plan_rate(results):
    if len(results) == 0:
        return 0.0

    valid = sum(result["valid"] for result in results)

    return valid / len(results)