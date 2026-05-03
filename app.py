from flask import Flask, request, jsonify
import requests
import os
import hashlib

app = Flask(__name__)

API_URL = "https://api-inference.huggingface.co/models/mrm8488/distilbert-base-uncased-finetuned-phishing"
HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# 🔥 CACHE
cache = {}

def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

@app.route("/scan_email", methods=["POST"])
def scan_email():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Text required"}), 400

    text_hash = get_hash(text)

    # ✅ CACHE HIT
    if text_hash in cache:
        return jsonify(cache[text_hash])

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})

        hf_output = response.json()
        print("🔥 HF RAW:", hf_output)

        # ✅ SAFE PARSING
        if isinstance(hf_output, list) and len(hf_output) > 0:
            result = hf_output[0][0]  # 🔥 FIXED

            label = result.get("label", "unknown")
            score = result.get("score", 0)

            output = {
                "email_prediction": 1 if label.lower() == "phishing" else 0,
                "confidence": round(score * 100, 2)
            }

        else:
            return jsonify({"error": "Invalid model response"}), 500

        # ✅ SAVE CACHE
        cache[text_hash] = output

        return jsonify(output)

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "🔥 Email Phishing API Running Successfully"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
