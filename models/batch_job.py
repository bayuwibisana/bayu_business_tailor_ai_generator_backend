from sqlalchemy import Column, String, Integer, DateTime, Text
from database import Base
from datetime import datetime
import uuid

class BatchJob(Base):
    __tablename__ = "batch_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    total_posts = Column(Integer, default=0)
    completed_posts = Column(Integer, default=0)
    failed_posts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_log = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)  # Username of the user who created this batch 