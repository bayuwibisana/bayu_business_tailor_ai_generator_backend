from sqlalchemy import Column, String, Text
from database import Base

class ContentTone(Base):
    __tablename__ = "content_tones"
    
    id = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    prompt_modifier = Column(Text, nullable=True) 