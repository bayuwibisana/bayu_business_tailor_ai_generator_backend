#!/usr/bin/env python3

"""
Database initialization script
Run this to create all the necessary tables
"""

from database import engine, Base, SessionLocal
from models.batch_job import BatchJob
from models.campaign_post import CampaignPost
from models.campaign import Campaign
from models.user import User
from models.content_tone import ContentTone

def init_database():
    """Create all tables in the database"""
    print("Initializing database...")
    
    # Drop all existing tables and recreate them
    print("🗑️  Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("🔧 Creating tables...")
    print(f"Tables to create: {[table.name for table in Base.metadata.tables.values()]}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    
    # Insert default content tones
    print("📝 Inserting default content tones...")
    db = SessionLocal()
    try:
        content_tones = [
            ContentTone(
                id='friendly',
                name='Friendly',
                description='Warm and approachable',
                prompt_modifier='Use warm, welcoming language'
            ),
            ContentTone(
                id='casual',
                name='Casual',
                description='Relaxed and informal',
                prompt_modifier='Keep it conversational'
            ),
            ContentTone(
                id='modern',
                name='Modern',
                description='Contemporary and innovative',
                prompt_modifier='Use trendy language'
            ),
            ContentTone(
                id='professional',
                name='Professional',
                description='Formal and business-like',
                prompt_modifier='Maintain professional tone'
            ),
            ContentTone(
                id='humorous',
                name='Humorous',
                description='Funny and entertaining',
                prompt_modifier='Add humor and playfulness'
            )
        ]
        
        for tone in content_tones:
            db.add(tone)
        
        db.commit()
        print("✅ Default content tones inserted successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error inserting content tones: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 