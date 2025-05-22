from flask import Flask, request, jsonify
from flask_cors import CORS
from parser_utils import extract_text, get_profile_keywords, extract_keywords_from_text

app = Flask(__name__)
CORS(app)

# --- Matching logic with section-wise scoring ---
def calculate_match(jd_keywords, cv_keywords, priority_skills):
    weights = {
        "section1": 40,  # Dept + Level profile keywords
        "section2": 20,  # Priority critical skills
        "section3": 40   # JD → CV parsed keyword overlap
    }

    section_scores = []

    # Section 1: Profile-based match
    s1_matches = sum(1 for field in jd_keywords for word in jd_keywords[field] if word in cv_keywords.get(field, []))
    s1_total = sum(len(jd_keywords[field]) for field in jd_keywords)
    s1_score = round((s1_matches / s1_total) * weights["section1"]) if s1_total else 0
    section_scores.append(s1_score)

    # Section 2: Priority skill match
    ps = [s.strip().lower() for s in priority_skills.split(",") if s.strip()]
    ps_matches = [s for s in ps if s in cv_keywords.get("skills", [])]
    s2_score = round((len(ps_matches) / len(ps)) * weights["section2"]) if ps else 0
    section_scores.append(s2_score)

    # Section 3: JD parsed keywords match
    all_jd_words = set(jd_keywords.get("skills", []) + jd_keywords.get("tools", []) +
                       jd_keywords.get("domain", []) + jd_keywords.get("education", []))
    all_cv_words = set(cv_keywords.get("skills", []) + cv_keywords.get("tools", []) +
                       cv_keywords.get("domain", []) + cv_keywords.get("education", []))
    match_count = len(all_jd_words & all_cv_words)
    s3_score = round((match_count / len(all_jd_words)) * weights["section3"]) if all_jd_words else 0
    section_scores.append(s3_score)

    total = sum(section_scores)
    if total >= 80:
        label = "✅ Best Fit"
    elif total >= 60:
        label = "👍 Good Fit"
    elif total >= 40:
        label = "⚠️ Average Fit"
    else:
        label = "❌ Not Fit"

    return total, label, section_scores, ", ".join(ps_matches)

# --- Main API route ---
@app.route("/parse", methods=["POST"])
def parse():
    try:
        dept = request.form.get("department", "").strip()
        level = request.form.get("level", "").strip()
        priority_skills = request.form.get("prioritySkills", "").strip()

        jd_file = request.files.get("jd")
        cv_files = request.files.getlist("cvs")

        if not dept or not level or not jd_file or not cv_files:
            return jsonify({"error": "Missing required fields"}), 400

        jd_text = extract_text(jd_file)
        jd_parsed = extract_keywords_from_text(jd_text)
        jd_keywords = get_profile_keywords(dept, level)
        for field in jd_keywords:
            jd_keywords[field] += jd_parsed  # Add parsed JD tokens for section 3

        results = []
        for file in cv_files:
            cv_text = extract_text(file)
            cv_keywords = extract_keywords_from_text(cv_text)
            score, label, section_scores, matched = calculate_match(jd_keywords, cv_keywords, priority_skills)
            results.append({
                "cv": file.filename,
                "score": score,
                "label": label,
                "section_scores": section_scores,
                "priority_matched": matched
            })

        return jsonify({"results": results})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# --- Entry Point ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
