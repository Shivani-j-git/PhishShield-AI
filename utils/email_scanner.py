def scan_email(email_text):
    keywords = [
        "verify", "password", "bank", "otp",
        "urgent", "click", "login", "reward",
        "winner", "update", "security"
    ]

    score = 0
    reasons = []

    for word in keywords:
        if word in email_text.lower():
            score += 10
            reasons.append(f"Contains '{word}'")

    if "http://" in email_text:
        score += 20
        reasons.append("Uses unsecured HTTP link")

    if score >= 50:
        result = "Phishing"
    else:
        result = "Safe"

    return result, min(score, 100), reasons
