from flask import Flask, request, jsonify
from flask_cors import CORS
from parser_utils import extract_text, get_profile_keywords, extract_keywords_from_text

app = Flask(__name__)
CORS(app)

# --- Scoring Logic ---
def calculate_match(jd_keywords, cv_keywords, priority_skills):
    weights = {
        "section1": 40,  # Department & Level
        "section2": 20,  # Critical skills
        "section3": 40   # JD-CV parsed keyword overlap
    }

    section_scores = {"section1": 0, "section2": 0, "section3": 0}

    # Section 1: Match JD keywords to CV
    matches = 0
    total = 0
    for field in jd_keywords:
        jd_set = set(jd_keywords[field])
        cv_set = set(cv_keywords.get(field, []))
        match_count = len(jd_set & cv_set)
        matches += match_count
        total += len(jd_set)
    section_scores["section1"] = round((matches / total) * weights["section1"]) if total else 0

    # Section 2: Priority skill match
    priority = [p.strip().lower() for p in priority_skills.split(",") if p.strip()]
    match_priority = [p for p in priority if p in cv_keywords.get("skills", [])]
    section_scores["section2"] = round((len(match_priority) / len(priority)) * weights["section2"]) if priority else 0

    # Section 3: JD-CV parsed match
    jd_all = set(jd_keywords.get("skills", []) + jd_keywords.get("tools", []) +
                 jd_keywords.get("domain", []) + jd_keywords.get("education", []))
    cv_all = set(cv_keywords.get("skills", []) + cv_keywords.get("tools", []) +
                 cv_keywords.get("domain", []) + cv_keywords.get("education", []))
    matched = len(jd_all & cv_all)
    section_scores["section3"] = round((matched / len(jd_all)) * weights["section3"]) if jd_all else 0

    # Total Score
    total_score = section_scores["section1"] + section_scores["section2"] + section_scores["section3"]

    # Label
    if total_score >= 80:
        label = "✅ Best Fit"
    elif total_score >= 60:
        label = "👍 Good Fit"
    elif total_score >= 40:
        label = "⚠️ Average Fit"
    else:
        label = "❌ Not Fit"

    return total_score, label, section_scores, ", ".join(match_priority)

# --- Main Endpoint ---
@app.route("/parse", methods=["POST"])
def parse():
    try:
        dept = request.form.get("dept", "").strip().lower()
        level = request.form.get("level", "").strip()
        priority_skills = request.form.get("priority_skills", "").strip()
        jd_file = request.files.get("jd")
        cv_files = request.files.getlist("cvs")

        if not dept or not level or not jd_file or not cv_files:
            return jsonify({"error": "Missing required fields"}), 400

        # Extract JD
        jd_text = extract_text(jd_file)
        parsed_jd = extract_keywords_from_text(jd_text)
        profile_keywords = get_profile_keywords(dept, level)

        # Add parsed JD keywords for section 3
        jd_combined = {}
        for key in ["skills", "tools", "domain", "education"]:
            jd_combined[key] = profile_keywords.get(key, []) + parsed_jd.get(key, [])

        results = []
        for cv_file in cv_files:
            cv_text = extract_text(cv_file)
            cv_keywords = extract_keywords_from_text(cv_text)
            score, label, section_scores, matched = calculate_match(jd_combined, cv_keywords, priority_skills)
            results.append({
                "cv": cv_file.filename,
                "score": score,
                "label": label,
                "section1_score": section_scores["section1"],
                "section2_score": section_scores["section2"],
                "section3_score": section_scores["section3"],
                "priority": matched
            })

        return jsonify({"results": results})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
