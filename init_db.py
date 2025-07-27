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
from auth import get_password_hash
from sqlalchemy import text

def init_database():
    """Create all tables in the database"""
    print("Initializing database...")
    
    # Drop all existing tables and recreate them
    print("🗑️  Dropping existing tables...")
    try:
        # Try to drop all tables normally first
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print(f"⚠️  Standard drop failed: {str(e)}")
        print("🔧 Using CASCADE to handle foreign key constraints...")
        
        # Drop tables manually with CASCADE for PostgreSQL
        with engine.connect() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("SET session_replication_role = replica;"))
            
            # Drop tables in reverse dependency order
            tables_to_drop = [
                'campaign_posts',
                'batch_jobs', 
                'campaigns',
                'users',
                'content_tones'
            ]
            
            for table_name in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
                    print(f"   Dropped table: {table_name}")
                except Exception as table_error:
                    print(f"   Warning: Could not drop {table_name}: {table_error}")
            
            # Re-enable foreign key checks
            conn.execute(text("SET session_replication_role = DEFAULT;"))
            conn.commit()
    
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
    
    # Insert default admin user
    print("👤 Creating default admin user...")
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                first_name="admin",
                last_name="test"
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Email: admin@example.com")
        else:
            print("ℹ️  Admin user already exists, skipping creation")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 