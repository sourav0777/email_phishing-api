from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔥 HuggingFace API
API_URL = "https://api-inference.huggingface.co/models/mrm8488/distilbert-base-uncased-finetuned-phishing"

HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

@app.route("/scan_email", methods=["POST"])
def scan_email():
    data = request.get_json()

    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Text required"}), 400

    response = requests.post(API_URL, headers=headers, json={"inputs": text})

    result = response.json()[0]

    label = result["label"]
    score = result["score"]

    prediction = 1 if label == "phishing" else 0

    return jsonify({
        "email_prediction": prediction,
        "confidence": round(score * 100, 2)
    })

@app.route("/")
def home():
    return "🔥 Email Phishing API Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
