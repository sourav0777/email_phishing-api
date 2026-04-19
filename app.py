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

# 🔥 CACHE MEMORY
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

    # 🔥 CACHE HIT
    if text_hash in cache:
        return jsonify(cache[text_hash])

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        result = response.json()[0]

        label = result["label"]
        score = result["score"]

        output = {
            "email_prediction": 1 if label == "phishing" else 0,
            "confidence": round(score * 100, 2)
        }

        # 🔥 SAVE CACHE
        cache[text_hash] = output

        return jsonify(output)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "🔥 Optimized Email API Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
