from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz
from docx import Document
from parser_utils import extract_text, extract_keywords_from_text, get_profile_keywords

app = Flask(__name__)
CORS(app, origins=["https://debayan-mon-arch.github.io", "https://debayan-mon-arch.github.io/resume-fit-frontend/"])

def calculate_match(jd_keywords, cv_keywords, profile_keywords, priority_skills, cv_data):
    # --- Section 1: Department & Level keyword match ---
    sec1_fields = ["skills", "tools", "domain", "education"]
    sec1_match = []
    sec1_total = 0
    for field in sec1_fields:
        jd_set = set(profile_keywords.get(field, []))
        cv_set = set(map(str.lower, cv_data.get(field, [])))
        if jd_set:
            match = len(jd_set & cv_set) / len(jd_set)
            sec1_match.append(match)
            sec1_total += 1
    section1_score = round((sum(sec1_match) / sec1_total) * 100) if sec1_total else 0

    # --- Section 2: Critical Skills ---
    priority = [s.strip().lower() for s in priority_skills.split(",") if s.strip()]
    section2_score = 0
    priority_matched = []
    if priority:
        cv_skills = set(map(str.lower, cv_data.get("skills", [])))
        match_ratio = len(set(priority) & cv_skills) / len(priority) if priority else 0
        section2_score = round(match_ratio * 100)
        priority_matched = list(set(priority) & cv_skills)

    # --- Section 3: JD–CV full field match ---
    jd_terms = set(
        jd_keywords.get("skills", []) +
        jd_keywords.get("tools", []) +
        jd_keywords.get("domain", []) +
        jd_keywords.get("education", [])
    )

    cv_terms = set(
        cv_keywords.get("skills", []) +
        cv_keywords.get("tools", []) +
        cv_keywords.get("domain", []) +
        cv_keywords.get("education", [])
    )

    match_terms = jd_terms & cv_terms
    section3_score = round(len(match_terms) / len(jd_terms) * 100) if jd_terms else 0

    # --- Weight adjustment logic ---
    if priority:
        weight_1, weight_2, weight_3 = 20, 10, 70
    else:
        weight_1, weight_2, weight_3 = 20, 0, 80

    # --- Final score ---
    score = round(
        (section1_score * weight_1 +
         section2_score * weight_2 +
         section3_score * weight_3) / 100
    )

    if score >= 60:
        label = "✅ Best Fit"
    elif score >= 35:
        label = "👍 Good Fit"
    elif score >= 40:
        label = "⚠️ Average Fit"
    else:
        label = "❌ Not Fit"

    return {
        "score": score,
        "label": label,
        "section1_score": section1_score,
        "section2_score": section2_score,
        "section3_score": section3_score,
        "priority": ", ".join(priority_matched),
        "top_keywords": list(match_terms)
    }

@app.route("/parse", methods=["POST"])
def parse():
    try:
        dept = request.form.get("dept", "").lower()
        level = request.form.get("level", "").lower()
        priority_skills = request.form.get("priority_skills", "")

        jd_file = request.files.get("jd")
        cv_files = request.files.getlist("cvs")

        if not dept or not level or not jd_file or not cv_files:
            return jsonify({"error": "Missing required fields or files"}), 400

        # Extract JD keywords
        jd_text = extract_text(jd_file)
        jd_keywords = extract_keywords_from_text(jd_text)

        # Profile-based keywords from dept & level
        profile_keywords = get_profile_keywords(dept, level)

        results = []
        for file in cv_files:
            cv_text = extract_text(file)
            cv_keywords = extract_keywords_from_text(cv_text)

            cv_data = {
                "skills": cv_keywords.get("skills", []),
                "tools": cv_keywords.get("tools", []),
                "domain": cv_keywords.get("domain", []),
                "education": cv_keywords.get("education", [])
            }

            match = calculate_match(jd_keywords, cv_keywords, profile_keywords, priority_skills, cv_data)

            results.append({
                "cv": file.filename,
                "score": match["score"],
                "label": match["label"],
                "section1_score": match["section1_score"],
                "section2_score": match["section2_score"],
                "section3_score": match["section3_score"],
                "priority": match["priority"],
                "top_keywords": match["top_keywords"]
            })

        return jsonify({"results": results})
    except Exception as e:
        print("Error in /parse:", e)
        return jsonify({"error": "Something went wrong on the server."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
