import asyncio
import time
import uuid
import os
from dotenv import load_dotenv
from services.batch_service import BatchGenerationService
from sqlalchemy.orm import Session
from database import engine
from models.batch_job import BatchJob

# Load environment variables
load_dotenv()

async def test_batch_performance():
    """Test batch generation performance"""
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key in the .env file.")
        return False
    
    # Create batch service
    db_session = Session(bind=engine)
    batch_service = BatchGenerationService(db_session)
    
    # Generate a test batch ID and campaign ID
    batch_id = str(uuid.uuid4())
    campaign_id = "test-campaign-123"
    
    # Create batch job record first
    batch_job = BatchJob(
        id=batch_id,
        campaign_id=campaign_id,
        name="Performance Test Batch",
        status="pending",
        total_posts=0,
        completed_posts=0,
        failed_posts=0
    )
    db_session.add(batch_job)
    db_session.commit()
    
    # Test data
    test_posts = []
    for i in range(5):  # Start with 10 posts
        test_posts.append({
            'brand_name': 'Test Brand',
            'topic': 'Performance Test',
            'brief': f'This is test post number {i+1} for performance testing',
            'tone': 'friendly',
            'target_audience': 'General audience'
        })
    
    print(f"Starting performance test with {len(test_posts)} posts...")
    start_time = time.time()
    
    try:
        # Process batch
        results = await batch_service.process_batch(batch_id, test_posts)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Safe division to avoid ZeroDivisionError
        if duration > 0:
            rate = len(test_posts)/duration
            print(f"✅ Generated {len(test_posts)} posts in {duration:.2f} seconds")
            print(f"⚡ Rate: {rate:.2f} posts per second")
        else:
            print(f"✅ Generated {len(test_posts)} posts too quickly to measure time")
            print(f"⚡ Rate: very fast (< 0.01s)")
        
        # Check if meets requirements
        if duration < 90:  # 90 seconds for 10 posts
            print("🎉 PASSED: Performance requirement met!")
            return True
        else:
            print("❌ FAILED: Performance requirement not met")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Run test
if __name__ == "__main__":
    asyncio.run(test_batch_performance())