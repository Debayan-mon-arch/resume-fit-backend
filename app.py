from flask import Flask, request, jsonify
from flask_cors import CORS
from parser_utils import extract_text, get_profile_keywords, extract_keywords_from_text

app = Flask(__name__)
CORS(app)

# --- Scoring logic ---
def calculate_match(jd, cv, priority_keywords=None):
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
    matched_fields = {}

    for field, weight in base_weights.items():
        jd_val = jd.get(field)
        cv_val = cv.get(field)

        if jd_val in [None, "", []] or cv_val in [None, "", []]:
            continue

        if isinstance(jd_val, list) and isinstance(cv_val, list):
            jd_set = set(jd_val)
            cv_set = set(cv_val)
            matches = {j for j in jd_set if any(j in c or c in j for c in cv_set)}
            match_ratio = len(matches) / len(jd_set) if jd_set else 0
            matched_fields[field] = list(matches)
        elif isinstance(jd_val, int) and isinstance(cv_val, int):
            match_ratio = 1 if abs(jd_val - cv_val) <= 2 else 0
            matched_fields[field] = [str(cv_val)] if match_ratio else []
        else:
            match_ratio = 1 if str(jd_val).lower() == str(cv_val).lower() else 0
            matched_fields[field] = [str(cv_val)] if match_ratio else []

        score += match_ratio * weight
        total_weight += weight

    # --- Priority skill boost ---
    matched_priority = []
    if priority_keywords:
        cv_blob = " ".join(" ".join(cv.get(f, [])) if isinstance(cv.get(f), list) else str(cv.get(f)) for f in jd)
        for kw in priority_keywords:
            if kw in cv_blob:
                score += 1.5  # moderate boost
                total_weight += 1.5
                matched_priority.append(kw)

    final_score = round((score / total_weight) * 100) if total_weight else 0

    if final_score >= 80:
        label = "✅ Best Fit"
    elif final_score >= 60:
        label = "👍 Good Fit"
    elif final_score >= 40:
        label = "⚠️ Average Fit"
    else:
        label = "❌ Not Fit"

    return final_score, label, matched_priority

# --- API route ---
@app.route('/parse', methods=['POST'])
def parse():
    try:
        dept = request.form.get("dept", "").lower()
        level = request.form.get("level", "").upper()
        jd_file = request.files.get("jd")
        cv_files = request.files.getlist("cvs")

        if not jd_file or not cv_files:
            return jsonify({"error": "JD and CVs required"}), 400

        jd_text = extract_text(jd_file)
        jd_extracted = extract_keywords_from_text(jd_text)
        profile_keywords = get_profile_keywords(dept, level)

        jd = {
            "skills": profile_keywords["skills"] + jd_extracted,
            "domain": profile_keywords["domain"] + jd_extracted,
            "tools": profile_keywords["tools"] + jd_extracted,
            "education": profile_keywords["education"] + jd_extracted,
            "experience": int(request.form.get("experience")) if request.form.get("experience") else None,
            "joining": request.form.get("joining"),
            "age": int(request.form.get("age")) if request.form.get("age") else None,
            "gender": request.form.get("gender"),
            "graduate": request.form.get("graduate")
        }

        priority_raw = request.form.get("prioritySkill", "")
        priority_keywords = [p.strip().lower() for p in priority_raw.split(",") if p.strip()]

        results = []
        for file in cv_files:
            cv_text = extract_text(file)
            cv_keywords = extract_keywords_from_text(cv_text)
            cv = {
                "skills": cv_keywords,
                "domain": cv_keywords,
                "tools": cv_keywords,
                "education": cv_keywords,
                "experience": jd["experience"],
                "joining": jd["joining"],
                "age": jd["age"],
                "gender": jd["gender"],
                "graduate": jd["graduate"]
            }

            score, label, matched_priority = calculate_match(jd, cv, priority_keywords)
            results.append({
                "cv": file.filename,
                "score": score,
                "label": label,
                "matched_priority": ", ".join(matched_priority) if matched_priority else ""
            })

        return jsonify({"results": results})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
