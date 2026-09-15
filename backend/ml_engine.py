# backend/ml_engine.py
from transformers import pipeline

print("Initializing Production FinBERT and Zero-Shot Models...")

sentiment_pipeline = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    tokenizer="ProsusAI/finbert"
)

zero_shot_classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-3"
)

SECTOR_CANDIDATES = [
    "Foreign Exchange & Currency",
    "Banking & Monetary Policy",
    "Energy, Power & Fuel Tariffs",
    "Tech & Export Services",
    "Automobile & Manufacturing",
    "Agriculture & Commodities"
]

def derive_desk_signals(headline: str, sector: str, sentiment: str) -> dict:
    """
    Translates macroeconomic sector & sentiment into actionable
    Treasury (Fixed Income, FX) and ECM desk positioning signals.
    """
    text = headline.lower()
    
    # Defaults
    yield_bias = "Yield Neutral"
    fx_pressure = "FX Neutral"
    ecm_window = "Window Neutral"
    desk_note = "Routine macro flow; no acute repricing triggered across fixed income or FX desks."

    # 1. Foreign Exchange & Balance of Payments
    if sector == "Foreign Exchange & Currency" or any(k in text for k in ["rupee", "pkr", "remittance", "forex", "reserves", "current account"]):
        if sentiment == "BULLISH":
            fx_pressure = "PKR Supportive / Inflows"
            yield_bias = "Yields Down / Bullish FI"
            ecm_window = "Window Favorable"
            desk_note = "External account liquidity improvement; eases interbank dollar demand and curbs imported inflation."
        elif sentiment == "BEARISH":
            fx_pressure = "PKR Depreciation Pressure"
            yield_bias = "Yields Up / Bearish FI"
            ecm_window = "Window Constrained"
            desk_note = "Reserve depletion or debt repayment drain; interbank USD tightening expected with upward yield pressure."
            
    # 2. Banking, Rates & Monetary Policy
    elif sector == "Banking & Monetary Policy" or any(k in text for k in ["sbp", "interest rate", "inflation", "cpi", "kibor", "auction", "t-bill", "pib"]):
        if sentiment == "BULLISH":
            yield_bias = "Yields Down / Bullish FI"
            ecm_window = "Window Favorable"
            desk_note = "Disinflationary signal or policy easing bias; favorable for secondary bond duration and lower borrowing costs."
        elif sentiment == "BEARISH":
            yield_bias = "Yields Up / Bearish FI"
            ecm_window = "Window Constrained"
            desk_note = "Inflationary risk or policy tightening cue; risk of higher cut-off yields in primary debt auctions."

    # 3. Energy, Commodities & Fiscal Subsidies
    elif sector in ["Energy, Power & Fuel Tariffs", "Agriculture & Commodities"] or any(k in text for k in ["oil", "crude", "circular debt", "nepra", "tariff"]):
        if sentiment == "BEARISH":
            yield_bias = "Yields Up / Bearish FI"
            fx_pressure = "PKR Depreciation Pressure"
            ecm_window = "Window Constrained"
            desk_note = "Cost-push inflation driver; threatens sovereign fiscal space and widens import bill exposure."
        elif sentiment == "BULLISH":
            yield_bias = "Yields Down / Bullish FI"
            fx_pressure = "PKR Supportive / Inflows"
            desk_note = "Commodity relief softens external financing requirements and moderates core CPI trajectory."

    # 4. Global Wires / Federal Reserve
    if any(k in text for k in ["fed", "federal reserve", "treasury yield", "dollar index"]):
        if "rate cut" in text or sentiment == "BULLISH":
            ecm_window = "Window Favorable"
            fx_pressure = "PKR Supportive / Inflows"
            desk_note = "Global easing tone; supportive of frontier sovereign debt risk appetite and foreign portfolio flows."

    return {
        "yield_bias": yield_bias,
        "fx_pressure": fx_pressure,
        "ecm_window": ecm_window,
        "desk_note": desk_note
    }

def analyze_story(text: str) -> dict:
    # 1. FinBERT Sentiment
    sent_result = sentiment_pipeline(text)[0]
    raw_label = sent_result['label'].upper()
    sent_score = sent_result['score']

    if raw_label == "POSITIVE":
        impact = "BULLISH"
    elif raw_label == "NEGATIVE":
        impact = "BEARISH"
    else:
        impact = "NEUTRAL"

    # 2. DistilBART Zero-Shot Sector Classification
    sec_result = zero_shot_classifier(text, candidate_labels=SECTOR_CANDIDATES)
    top_sector = sec_result['labels'][0]
    sec_score = sec_result['scores'][0]

    # 3. Desk Signal Synthesis
    desk_signals = derive_desk_signals(text, top_sector, impact)

    return {
        "impact_direction": impact,
        "sentiment_confidence": round(float(sent_score), 4),
        "affected_sector": top_sector,
        "sector_confidence": round(float(sec_score), 4),
        "yield_bias": desk_signals["yield_bias"],
        "fx_pressure": desk_signals["fx_pressure"],
        "ecm_window": desk_signals["ecm_window"],
        "desk_note": desk_signals["desk_note"]
    }