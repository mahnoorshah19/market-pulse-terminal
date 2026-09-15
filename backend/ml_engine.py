from transformers import pipeline

print("Initializing Production FinBERT and Zero-Shot Models...")

# 1. Financial Sentiment & Risk (FinBERT)
sentiment_pipeline = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    tokenizer="ProsusAI/finbert"
)

# 2. Sector / Market Classification (Zero-Shot)
zero_shot_classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-3"
)

SECTOR_TAXONOMY = [
    "Foreign Exchange & Currency",
    "Banking & Monetary Policy",
    "Energy, Power & Fuel Tariffs",
    "Tech & Export Services",
    "Automobile & Manufacturing",
    "Agriculture & Commodities"
]

def analyze_story(text: str) -> dict:
    # FinBERT inference
    s_res = sentiment_pipeline(text)[0]
    sentiment_label = s_res['label'].lower()
    
    impact_map = {
        "positive": "BULLISH",
        "negative": "BEARISH",
        "neutral": "NEUTRAL"
    }
    
    # Zero-Shot Sector inference
    zs_res = zero_shot_classifier(text, candidate_labels=SECTOR_TAXONOMY)
    
    return {
        "affected_sector": zs_res['labels'][0],
        "sector_confidence": float(zs_res['scores'][0]),
        "impact_direction": impact_map.get(sentiment_label, "NEUTRAL"),
        "sentiment_confidence": float(s_res['score'])
    }