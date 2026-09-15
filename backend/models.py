from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.database import Base

class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String, unique=True, index=True)
    summary = Column(String)
    published_date = Column(String)
    affected_sector = Column(String, index=True)
    sector_confidence = Column(Float)
    impact_direction = Column(String, index=True)  # BULLISH, BEARISH, NEUTRAL
    sentiment_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Tester feedback tracking
    accuracy_upvotes = Column(Integer, default=0)
    accuracy_downvotes = Column(Integer, default=0)

    