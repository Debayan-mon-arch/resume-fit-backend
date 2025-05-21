from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF

app = Flask(__name__)
CORS(app)

# Utility to extract text from a file
def extract_text(file_storage):
    try:
        text = ""
        if file_storage:
            file_storage.stream.seek(0)  # Ensure stream is at beginning
            doc = fitz.open(stream=file_storage.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
        return text.lower()
    except Exception as e:
        print(f"Failed to extract text: {e}")
        return ""

# Matching logic
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

        if jd_val in [None, "", []] or cv_val in [None, "", []]:
            continue

        if isinstance(jd_val, list) and isinstance(cv_val, list):
            jd_set = set(map(str.strip, map(str.lower, jd_val)))
            cv_set = set(map(str.strip, map(str.lower, cv_val)))
            matches = jd_set & cv_set
            match_ratio = len(matches) / len(jd_set) if jd_set else 0

        elif isinstance(jd_val, int) and isinstance(cv_val, int):
            match_ratio = 1 if abs(jd_val - cv_val) <= 2 else 0

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

# API route
@app.route('/parse', methods=['POST'])
def parse():
    try:
        jd_file = request.files.get('jd')
        cv_files = request.files.getlist('cvs')

        if not jd_file or not cv_files:
            return jsonify({"error": "JD and at least one CV are required."}), 400

        jd_text = extract_text(jd_file)
        cv_texts = [extract_text(f) for f in cv_files]

        # Optional fields
        jd_extras = {
            "experience": int(request.form.get("experience")) if request.form.get("experience") else None,
            "joining": request.form.get("joining"),
            "age": int(request.form.get("age")) if request.form.get("age") else None,
            "gender": request.form.get("gender"),
            "graduate": request.form.get("graduate")
        }

        jd = {
            "skills": jd_text.split(","),
            "domain": jd_text.split(","),
            "tools": jd_text.split(","),
            "education": jd_text.split(","),
            **jd_extras
        }

        results = []
        for i, text in enumerate(cv_texts):
            cv = {
                "skills": text.split(","),
                "domain": text.split(","),
                "tools": text.split(","),
                "education": text.split(","),
                **jd_extras  # For now using JD extras, can be customized per CV later
            }
            score, label = calculate_match(jd, cv)
            results.append({
                "cv": cv_files[i].filename,
                "score": score,
                "label": label
            })

        return jsonify({"results": results})

    except Exception as e:
        print(f"Error in /parse: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Render entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
