from flask import Flask, request, jsonify
from flask_cors import CORS
from parser_utils import extract_text, get_profile_keywords, extract_keywords_from_text

app = Flask(__name__)
CORS(app)

# Weighted scoring per section
SECTION_WEIGHTS = {
    "section1": 0.40,
    "section2": 0.20,
    "section3": 0.40
}

def calculate_match(jd_keywords, cv_keywords, profile_keywords, priority_keywords):
    # SECTION 1: Profile keywords match
    profile_score = sum(1 for field in ["skills", "domain", "tools", "education"]
                        if any(k in cv_keywords for k in profile_keywords.get(field, [])))
    section1 = (profile_score / 4) * 100  # out of 100

    # SECTION 2: Priority skills match
    matched_priority = []
    priority_score = 0
    if priority_keywords:
        for p in priority_keywords:
            if p in cv_keywords:
                matched_priority.append(p)
        if priority_keywords:
            priority_score = (len(matched_priority) / len(priority_keywords)) * 100

    # SECTION 3: JD vs CV keywords
    overlap = set(jd_keywords) & set(cv_keywords)
    jd_score = (len(overlap) / len(set(jd_keywords))) * 100 if jd_keywords else 0
    section3 = jd_score

    # Weighted score
    total_score = round(
        section1 * SECTION_WEIGHTS["section1"] +
        priority_score * SECTION_WEIGHTS["section2"] +
        section3 * SECTION_WEIGHTS["section3"]
    )

    # Label
    if total_score >= 80:
        label = "✅ Best Fit"
    elif total_score >= 60:
        label = "👍 Good Fit"
    elif total_score >= 40:
        label = "⚠️ Average Fit"
    else:
        label = "❌ Not Fit"

    return total_score, label, matched_priority, {
        "section1": round(section1),
        "section2": round(priority_score),
        "section3": round(section3)
    }

@app.route("/parse", methods=["POST"])
def parse():
    try:
        dept = request.form.get("dept", "").lower()
        level = request.form.get("level", "").upper()
        priority_raw = request.form.get("prioritySkill", "")
        priority_keywords = [p.strip().lower() for p in priority_raw.split(",") if p.strip()]

        jd_file = request.files.get("jd")
        cv_files = request.files.getlist("cvs")

        if not jd_file or not cv_files:
            return jsonify({"error": "JD and CVs required"}), 400

        # Extract text from JD
        jd_text = extract_text(jd_file)
        jd_keywords = extract_keywords_from_text(jd_text)

        # Profile keywords from dept+level
        profile_keywords = get_profile_keywords(dept, level)

        results = []
        for file in cv_files:
            cv_text = extract_text(file)
            cv_keywords = extract_keywords_from_text(cv_text)

            score, label, matched_priority, section_scores = calculate_match(
                jd_keywords, cv_keywords, profile_keywords, priority_keywords
            )

            results.append({
                "cv": file.filename,
                "score": score,
                "label": label,
                "matched_priority": ", ".join(matched_priority) if matched_priority else "",
                "section_scores": section_scores
            })

        return jsonify({"results": results})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
