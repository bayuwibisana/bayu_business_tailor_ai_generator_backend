#!/usr/bin/env python3

"""
Database initialization script
Run this to create all the necessary tables
"""

from database import engine, Base
from models.batch_job import BatchJob
from models.campaign_post import CampaignPost
from models.campaign import Campaign

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

if __name__ == "__main__":
    init_database() 