from flask import Flask, request, jsonify
from flask_cors import CORS
from parser_utils import extract_text, extract_keywords_from_text, get_profile_keywords, expand_keywords

app = Flask(__name__)
CORS(app)

# Sectional weight distribution
WEIGHTS = {
    "section1": 40,  # Dept + Level
    "section2": 20,  # Critical Skills
    "section3": 40   # JD vs CV
}

def soft_match_score(base, target):
    base_set = set(expand_keywords(base))
    target_set = set(expand_keywords(target))
    matches = [kw for kw in base_set if any(kw in tgt for tgt in target_set)]
    score = round((len(matches) / len(base_set)) * 100) if base_set else 0
    return score, matches

@app.route('/parse', methods=['POST'])
def parse():
    try:
        dept = request.form.get("dept")
        level = request.form.get("level")
        priority_skills = request.form.get("priority_skills", "").split(",")
        jd_file = request.files.get("jd")
        cv_files = request.files.getlist("cvs")

        if not dept or not level or not jd_file or not cv_files:
            return jsonify({"error": "Missing inputs"}), 400

        jd_text = extract_text(jd_file)
        jd_keywords = extract_keywords_from_text(jd_text)

        role_keywords = get_profile_keywords(dept, level)

        results = []
        for f in cv_files:
            cv_text = extract_text(f)
            cv_keywords = extract_keywords_from_text(cv_text)

            # SECTION 1: Role Match
            s1_score, _ = soft_match_score(
                role_keywords['skills'] + role_keywords['tools'] + role_keywords['domain'] + role_keywords['education'],
                cv_keywords['skills'] + cv_keywords['tools'] + cv_keywords['domain'] + cv_keywords['education']
            )

            # SECTION 2: Priority Skills
            s2_score, matched_priority = soft_match_score(priority_skills, cv_keywords['skills'])

            # SECTION 3: JD vs CV
            s3_score, top_keywords = soft_match_score(jd_keywords['skills'], cv_keywords['skills'])

            final = round(
                (s1_score * WEIGHTS["section1"] +
                 s2_score * WEIGHTS["section2"] +
                 s3_score * WEIGHTS["section3"]) / 100
            )

            if final >= 80:
                label = "✅ Best Fit"
            elif final >= 60:
                label = "👍 Good Fit"
            elif final >= 40:
                label = "⚠️ Average Fit"
            else:
                label = "❌ Not Fit"

            results.append({
                "cv": f.filename,
                "section1_score": s1_score,
                "section2_score": s2_score,
                "section3_score": s3_score,
                "score": final,
                "label": label,
                "priority": ", ".join(matched_priority),
                "top_keywords": top_keywords  # hidden from frontend table but available for CSV
            })

        return jsonify({"results": results})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
