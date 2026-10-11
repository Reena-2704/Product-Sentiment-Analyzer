from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import csv
import io
import re
from collections import Counter
import numpy as np
import pandas as pd
from sentiment import analyze_sentiment
from database import save_reviews, get_reviews, database_status
from scraper import scrape_reviews

app = Flask(__name__)
CORS(app) #cross-origin resource sharing communication between frontend and backend

DEMO_REVIEWS = [
    {"product": "Demo Smartphone", "review": "The camera quality is excellent and the battery lasts all day.", "rating": "5"},
    {"product": "Demo Smartphone", "review": "I love the display. It is fast and easy to use.", "rating": "5"},
    {"product": "Demo Smartphone", "review": "The product is okay, nothing special.", "rating": "3"},
    {"product": "Demo Smartphone", "review": "The phone became slow after a few days and I am disappointed.", "rating": "2"},
    {"product": "Demo Smartphone", "review": "Battery life is terrible and the product stopped working.", "rating": "1"},
]

STOP_WORDS = {
    "the","and","for","this","that","with","was","are","but","have","has","had","not","you","your","from","they","its","very","just","all","can","will","would","could","there","their","what","when","where","which","about","been","were","our","out","too","more","than","into","also","product","phone","item","one","get","got","use","using","used","really","good","bad"
}

def enrich(items):
    output = []
    for item in items:
        result = dict(item)
        result.update(analyze_sentiment(result.get("review", "")))
        output.append(result)
    return output

def all_reviews():
    return get_reviews()

@app.get("/")
def home():
    return jsonify({"message": "Product Sentiment Analyzer API is running", "database": database_status()})

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "database": database_status()})

@app.get("/api/demo")
def demo():
    return jsonify(enrich(DEMO_REVIEWS))

@app.post("/api/scrape")
def scrape():
    data = request.get_json(silent=True) or {}
    url = str(data.get("url", "")).strip()
    if not url:
        return jsonify({"error": "Product link is required"}), 400
    try:
        raw = scrape_reviews(url)
        results = enrich(raw)
        saved = save_reviews(results)
        product = results[0]["product"] if results else "Unknown Product"
        return jsonify({"product": product, "url": url, "reviews": saved, "total": len(saved)})
    except Exception as exc:
        return jsonify({"error": "Could not collect reviews", "details": str(exc)}), 500

@app.get("/api/history")
def history():
    rows = all_reviews()
    if not rows:
        return jsonify([])
    df = pd.DataFrame(rows)
    if "created_at" not in df.columns:
        return jsonify([])
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["created_at"])
    if df.empty:
        return jsonify([])
    df["date"] = df["created_at"].dt.strftime("%Y-%m-%d")
    pivot = pd.crosstab(df["date"], df["sentiment"]).reset_index()
    for label in ["Positive", "Neutral", "Negative"]:
        if label not in pivot.columns:
            pivot[label] = 0
    result = pivot[["date", "Positive", "Neutral", "Negative"]].sort_values("date").to_dict(orient="records")
    return jsonify(result)

@app.get("/api/word-frequency")
def word_frequency():
    rows = all_reviews()
    words = []
    for row in rows:
        text = str(row.get("review", "")).lower()
        tokens = re.findall(r"[a-zA-Z]{3,}", text)
        words.extend(w for w in tokens if w not in STOP_WORDS)
    counts = Counter(words).most_common(15)
    return jsonify([{"word": word, "count": count} for word, count in counts])

@app.get("/api/export")
def export_csv():
    rows = get_reviews()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["product", "review", "rating", "sentiment", "polarity", "created_at"], extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=sentiment_reviews.csv"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

# cd C:\Users\Asus\Downloads\Product_Sentiment_Analyzer_COMPLETE_PDF\backend; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; python app.py
# cd C:\Users\Asus\Downloads\Product_Sentiment_Analyzer_COMPLETE_PDF\frontend; npm install; npm run dev