from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
from sqlalchemy.exc import IntegrityError

from backend.database import get_db, engine, Base
from backend.models import NewsItem
from backend.scraper import fetch_wire_stories
from backend.ml_engine import analyze_story

Base.metadata.create_all(bind=engine)

app =FastAPI(title="Market Pulse", description="Real-time Market News Analysis", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

class FeedbackPayload(BaseModel):
    item_id: int
    is_positive: bool

class AnalyzeRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
def serve_dashboard(request: Request, db: Session = Depends(get_db)):
    items = db.query(NewsItem).order_by(NewsItem.created_at.desc()).limit(100).all()
    # Extract unique sources for filter pills
    sources = sorted(list({item.source for item in items if item.source}))
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"items": items, "sources": sources}
    )

@app.post("/api/v1/sync")
def sync_wire_feed(db: Session = Depends(get_db)):
    """Fetches latest wire stories and evaluates unindexed records with live deduplication."""
    print("Ingesting live feeds across institutional sources...")
    raw_stories = fetch_wire_stories()
    print(f"Retrieved {len(raw_stories)} raw wire items. Evaluating new stories...")

    # 1. In-memory deduplication across feeds
    unique_stories = []
    seen_headlines = set()
    for s in raw_stories:
        hl = s.get('headline', '').strip()
        if hl and hl not in seen_headlines:
            seen_headlines.add(hl)
            unique_stories.append(s)

    new_count = 0
    MAX_SYNC_BATCH = 35

    for story in unique_stories:
        if new_count >= MAX_SYNC_BATCH:
            print(f"Batch limit ({MAX_SYNC_BATCH}) reached for this sync cycle.")
            break

        # 2. Check if already recorded in SQLite
        existing = db.query(NewsItem).filter(NewsItem.headline == story['headline']).first()
        if not existing:
            new_count += 1
            print(f"[{new_count}/{MAX_SYNC_BATCH}] Classifying: {story['headline'][:50]}...")

            nlp_output = analyze_story(story['headline'])
            item = NewsItem(
    source=story.get('source', 'Financial Wire'),
    headline=story['headline'],
    summary=story.get('summary', ''),
    published_date=story.get('published_date', 'Recent'),
    affected_sector=nlp_output['affected_sector'],
    sector_confidence=nlp_output['sector_confidence'],
    impact_direction=nlp_output['impact_direction'],
    sentiment_confidence=nlp_output['sentiment_confidence'],
    yield_bias=nlp_output['yield_bias'],
    fx_pressure=nlp_output['fx_pressure'],
    ecm_window=nlp_output['ecm_window'],
    desk_note=nlp_output['desk_note']
)
            
            # 3. Safe commit per item with rollback guard
            try:
                db.add(item)
                db.commit()
            except IntegrityError:
                db.rollback()
                new_count -= 1
                continue

    print(f"Sync complete. Added {new_count} fresh evaluated stories to the terminal.")
    return {"status": f"Sync completed. {new_count} new stories added."}

@app.post("/api/v1/analyze-custom")
def analyze_custom_text(req: AnalyzeRequest):
    """ Analyze custom text input for sector and sentiment. """
    return analyze_story(req.text)

@app.post("/api/v1/feedback")
def submit_feedback(payload: FeedbackPayload, db: Session = Depends(get_db)):
    """ Submit feedback on the accuracy of a news item. """
    item = db.query(NewsItem).filter(NewsItem.id == payload.item_id).first()
    if item:
        if payload.is_positive:
            item.accuracy_upvotes += 1
        else:
            item.accuracy_downvotes += 1
        db.commit()
        return {"status": "Feedback recorded."}
    return {"status": "News item not found."}