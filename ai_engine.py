def analyze_data(data):
    current = data["current"]
    lux = data["lux"]
    sound = data["sound"]
    # 🚨 SAFETY RULE (Highest Priority)
    if current > 10:
        return "EMERGENCY"

    # Normal QC Rules
    if current < 3:
        return "FAIL"

    if sound < 70:
        return "WARNING - Low Sound"

    return "PASS"