from sqlalchemy import Column, String, Text, DateTime, Boolean
from database import Base
from datetime import datetime
import uuid

class CampaignPost(Base):
    __tablename__ = "campaign_posts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_job_id = Column(String, nullable=False)
    campaign_id = Column(String, nullable=False)
    brand_name = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    tone = Column(String, nullable=False)
    brief = Column(Text, nullable=True)
    target_audience = Column(String, nullable=True)
    generated_caption = Column(Text, nullable=True)
    generated_image_url = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 