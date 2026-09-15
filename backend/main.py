from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path

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
    """ Fetched latets wire stories and evaluates unindexed records."""
    raw_stories = fetch_wire_stories()
    new_count = 0

    for story in raw_stories:
        exixting = db.query(NewsItem).filter(NewsItem.headline == story['headline']).first()
        if not exixting:
            nlp_output = analyze_story(story['headline'])
            item = NewsItem(
                source=story.get('source', 'Financial Wire'),
                headline=story['headline'],
                summary=story['summary'],
                published_date=story['published_date'],
                source=story['source'],
                affected_sector=nlp_output['affected_sector'],
                sector_confidence=nlp_output['sector_confidence'],
                impact_direction=nlp_output['impact_direction'],
                sentiment_confidence=nlp_output['sentiment_confidence']
            )
            db.add(item)
            new_count += 1

    db.commit()
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