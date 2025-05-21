def calculate_match(jd, cv):
    base_weights = {
        "skills": 3,
        "domain": 2,
        "tools": 2,
        "education": 1,
        "experience": 0.5,
        "joining": 0.5,
        "age": 0.5,
        "gender": 0.25,
        "graduate": 0.25
    }

    score = 0
    total_weight = 0

    for field, weight in base_weights.items():
        jd_val = jd.get(field)
        cv_val = cv.get(field)

        # Skip if either is missing
        if jd_val in [None, "", []] or cv_val in [None, "", []]:
            continue

        # For list-based fields
        if isinstance(jd_val, list) and isinstance(cv_val, list):
            jd_set = set(map(str.lower, jd_val))
            cv_set = set(map(str.lower, cv_val))
            matches = jd_set & cv_set
            match_ratio = len(matches) / len(jd_set) if jd_set else 0
        # For numeric fields like experience and age
        elif isinstance(jd_val, int) and isinstance(cv_val, int):
            match_ratio = 1 if abs(jd_val - cv_val) <= 2 else 0
        # For exact match text fields
        else:
            match_ratio = 1 if str(jd_val).lower() == str(cv_val).lower() else 0

        score += match_ratio * weight
        total_weight += weight

    final_score = round((score / total_weight) * 100) if total_weight else 0

    if final_score >= 80:
        label = "✅ Best Fit"
    elif final_score >= 60:
        label = "👍 Good Fit"
    elif final_score >= 40:
        label = "⚠️ Average Fit"
    else:
        label = "❌ Not Fit"

    return final_score, label