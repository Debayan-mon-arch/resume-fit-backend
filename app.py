from flask import Flask, request, jsonify
from flask_cors import CORS
from parser_utils import extract_text
import re

app = Flask(__name__)
CORS(app)

# --- Static profile keyword templates ---
PROFILE_TEMPLATES = {
    "analyst": {
        "skills": ["excel", "sql", "data analysis", "communication"],
        "domain": ["analytics", "reporting"],
        "tools": ["tableau", "power bi"],
        "education": ["bachelor", "mba"]
    },
    "sde": {
        "skills": ["python", "java", "c++", "data structures"],
        "domain": ["backend", "frontend", "devops"],
        "tools": ["git", "docker", "vscode"],
        "education": ["btech", "mtech"]
    },
    "hr": {
        "skills": ["recruitment", "employee relations", "communication"],
        "domain": ["human resources", "people operations"],
        "tools": ["excel", "workday"],
        "education": ["mba", "pgdm"]
    },
    "marketing": {
        "skills": ["digital marketing", "seo", "content creation"],
        "domain": ["branding", "social media"],
        "tools": ["canva", "google analytics"],
        "education": ["bba", "mba"]
    }
}

def clean_jd_text(text):
    keywords = ["responsibilities", "role", "job description", "what you'll do", "key deliverables", "position"]
    for kw in keywords:
        idx = text.lower().find(kw)
        if idx != -1:
            return text[idx:]
    return text

def split_keywords(text):
    return [kw.strip().lower() for kw in re.split(r"[,\n;/\-–\| ]+", text) if kw.strip()]

# --- Matching logic ---
def calculate_match(jd, cv, priority_keywords=None):
    if priority_keywords is None:
        priority_keywords = []

    base_weights = {
        "skills": 4,
        "domain": 3,
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
            jd_set = set(map(str.lower, jd_val))
            cv_set = set(map(str.lower, cv_val))
            matches = {j for j in jd_set if any(j in c or c in j for c in cv_set)}
            matched_fields[field] = list(matches)
            match_ratio = len(matches) / len(jd_set) if jd_set else 0

        elif isinstance(jd_val, int) and isinstance(cv_val, int):
            match_ratio = 1 if abs(jd_val - cv_val) <= 2 else 0
            matched_fields[field] = [str(cv_val)] if match_ratio == 1 else []

        else:
            match_ratio = 1 if str(jd_val).lower() == str(cv_val).lower() else 0
            matched_fields[field] = [str(cv_val)] if match_ratio == 1 else []

        score += match_ratio * weight
        total_weight += weight

    # 🔥 Match priority keywords
    cv_blob = " ".join(cv.get(f, "") if isinstance(cv.get(f), str) else " ".join(cv.get(f, [])) for f in ["skills", "domain", "tools", "education"])
    matched_priority = [kw for kw in priority_keywords if kw.lower() in cv_blob]
    matched_fields["prioritySkill"] = matched_priority

    if matched_priority:
        score += 3 * len(matched_priority)
        total_weight += 3 * len(matched_priority)

    final_score = round((score / total_weight) * 100) if total_weight else 0

    if final_score >= 80:
        label = "✅ Best Fit"
    elif final_score >= 60:
        label = "👍 Good Fit"
    elif final_score >= 40:
        label = "⚠️ Average Fit"
    else:
        label = "❌ Not Fit"

    return final_score, label, matched_fields

# --- API route ---
@app.route('/parse', methods=['POST'])
def parse():
    try:
        profile = request.form.get("profile", "").lower()
        if profile not in PROFILE_TEMPLATES:
            return jsonify({"error": "Invalid profile type"}), 400

        jd_file = request.files.get("jd")
        cv_files = request.files.getlist("cvs")
        if not jd_file or not cv_files:
            return jsonify({"error": "JD and CV files are required"}), 400

        jd_raw = extract_text(jd_file)
        jd_clean = clean_jd_text(jd_raw)
        jd_keywords = split_keywords(jd_clean)
        profile_keywords = PROFILE_TEMPLATES[profile]

        jd = {
            "skills": profile_keywords["skills"] + jd_keywords,
            "domain": profile_keywords["domain"] + jd_keywords,
            "tools": profile_keywords["tools"] + jd_keywords,
            "education": profile_keywords["education"] + jd_keywords,
            "experience": int(request.form.get("experience")) if request.form.get("experience") else None,
            "joining": request.form.get("joining"),
            "age": int(request.form.get("age")) if request.form.get("age") else None,
            "gender": request.form.get("gender"),
            "graduate": request.form.get("graduate")
        }

        priority_raw = request.form.get("prioritySkill", "")
        priority_keywords = [kw.strip().lower() for kw in re.split(r"[,\n;/\-–\|]+", priority_raw) if kw.strip()]

        results = []
        for file in cv_files:
            cv_text = extract_text(file)
            cv_keywords = split_keywords(cv_text)
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

            score, label, matched = calculate_match(jd, cv, priority_keywords)
            results.append({
                "cv": file.filename,
                "score": score,
                "label": label,
                "matches": matched
            })

        return jsonify({"results": results})

    except Exception as e:
        print("Error in /parse:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
