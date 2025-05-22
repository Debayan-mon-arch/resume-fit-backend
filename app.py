from flask import Flask, request, jsonify
from flask_cors import CORS
from parser_utils import extract_text, extract_keywords_from_text, get_profile_keywords, expand_keywords

app = Flask(__name__)
CORS(app)

# Matching weights
WEIGHTS = {
    "section1": 40,  # Department + Level keyword match
    "section2": 20,  # Critical skills match
    "section3": 40   # JD vs CV keyword match
}

def match_score(base, target):
    base_set = set(expand_keywords(base))
    target_set = set(expand_keywords(target))
    matched = base_set & target_set
    score = round((len(matched) / len(base_set)) * 100) if base_set else 0
    return score, list(matched)

@app.route('/parse', methods=['POST'])
def parse():
    try:
        dept = request.form.get("dept")
        level = request.form.get("level")
        priority_skills = request.form.get("priority_skills", "").split(",")
        jd_file = request.files.get("jd")
        cvs = request.files.getlist("cvs")

        if not dept or not level or not jd_file or not cvs:
            return jsonify({"error": "Missing inputs"}), 400

        jd_text = extract_text(jd_file)
        jd_keywords = extract_keywords_from_text(jd_text)

        role_keywords = get_profile_keywords(dept, level)

        results = []
        for f in cvs:
            cv_text = extract_text(f)
            cv_keywords = extract_keywords_from_text(cv_text)

            # Section 1: Dept+Level Match
            s1_score, _ = match_score(
                role_keywords['skills'] + role_keywords['tools'] + role_keywords['domain'] + role_keywords['education'],
                cv_keywords['skills'] + cv_keywords['tools'] + cv_keywords['domain'] + cv_keywords['education']
            )

            # Section 2: Priority Skills Match
            s2_score, matched_priorities = match_score(priority_skills, cv_keywords['skills'])

            # Section 3: JD Keyword Match
            s3_score, top_keywords = match_score(jd_keywords['skills'], cv_keywords['skills'])

            # Final Weighted Score
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
                "priority": ", ".join(matched_priorities),
                "top_keywords": top_keywords
            })

        return jsonify({"results": results})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
