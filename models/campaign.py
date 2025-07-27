from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from datetime import datetime
import uuid

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    brand_name = Column(String(255), nullable=False)
    target_audience = Column(Text, nullable=True)
    tone_id = Column(String(20), nullable=True)
    status = Column(String(20), nullable=True, default="draft")
    created_at = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow) 