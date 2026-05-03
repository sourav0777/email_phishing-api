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

cache = {}

def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

@app.route("/scan_email", methods=["POST"])
def scan_email():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Text required"}), 400

    text_hash = get_hash(text)

    if text_hash in cache:
        return jsonify(cache[text_hash])

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})

        hf_output = response.json()
        print("🔥 HF RAW:", hf_output)

        # 🔥 HANDLE ERROR RESPONSE
        if isinstance(hf_output, dict):
            return jsonify({"error": hf_output}), 500

        if not hf_output or not isinstance(hf_output, list):
            return jsonify({"error": "Invalid response from model"}), 500

        # 🔥 SAFE PARSING
        result = hf_output[0][0] if isinstance(hf_output[0], list) else hf_output[0]

        label = result.get("label", "unknown").lower()
        score = result.get("score", 0)

        output = {
            "email_prediction": 1 if "phish" in label else 0,
            "confidence": round(score * 100, 2)
        }

        cache[text_hash] = output

        return jsonify(output)

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "🔥 Email API Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
