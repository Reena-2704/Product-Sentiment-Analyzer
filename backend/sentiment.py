from textblob import TextBlob


def analyze_sentiment(text: str):
    text = (text or "").strip()
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "sentiment": label,
        "polarity": round(polarity, 4)
    }
