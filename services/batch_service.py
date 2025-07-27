import asyncio
from asyncio import Semaphore
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.batch_job import BatchJob
from models.campaign_post import CampaignPost
from services.openai_service import openai_service

class BatchGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.max_concurrent = 5  # Adjust based on OpenAI rate limits
        
    async def process_batch(self, batch_job_id: str, posts_data: List[Dict]) -> Dict[str, Any]:
        """Main batch processing function - THIS IS YOUR CORE CHALLENGE"""
        
        # Update batch job status
        batch_job = self.db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
        batch_job.status = "processing"
        batch_job.total_posts = len(posts_data)
        self.db.commit()
        
        # Create semaphore for rate limiting
        semaphore = Semaphore(self.max_concurrent)
        
        async def process_single_post(post_data: Dict, index: int) -> Dict:
            """Process individual post with rate limiting"""
            async with semaphore:
                post = None
                try:
                    print(f"Processing post {index + 1}/{len(posts_data)}: {post_data.get('brand_name', 'Unknown Brand')}")
                    
                    # Create database record
                    post = CampaignPost(
                        campaign_id=batch_job.campaign_id,
                        batch_job_id=batch_job_id,
                        brand_name=post_data.get('brand_name'),
                        topic=post_data.get('topic'),
                        tone=post_data.get('tone'),
                        brief=post_data.get('brief'),
                        target_audience=post_data.get('target_audience'),
                        status='processing'
                    )
                    self.db.add(post)
                    self.db.commit()
                    self.db.refresh(post)
                    
                    # Generate caption
                    print(f"Generating caption for post {index + 1}...")
                    caption = await openai_service.generate_caption(post_data)
                    post.generated_caption = caption
                    post.status = 'generating_caption'
                    self.db.commit()
                        
                    # Generate image
                    print(f"Generating image for post {index + 1}...")
                    image_url = await openai_service.generate_image(post_data)
                    post.generated_image_url = image_url
                    
                    post.status = 'generating_image'
                    self.db.commit()
                    
                    # Mark as completed
                    # Update batch progress
                    post.status = 'completed'
                    batch_job.completed_posts += 1
                    self.db.commit()
                    
                    return {
                        'success': True,
                        'post_id': str(post.id),
                        'brand_name': post.brand_name,
                        'topic': post.topic,
                        'caption': post.generated_caption,
                        'image_url': post.generated_image_url
                    }
                    
                except Exception as e:
                    print(f"Error processing post {index + 1}: {str(e)}")
                    
                    # Update post with error if it exists
                    if post:
                        post.status = 'failed'
                        post.error_message = str(e)
                        self.db.commit()
                    
                    # Update failure count
                    batch_job.failed_posts += 1
                    self.db.commit()
                    
                    return {
                        'success': False,
                        'error': str(e),
                        'brand_name': post_data.get('brand_name', 'Unknown')
                    }
        
        # Execute all posts concurrently with rate limiting
        print(f"Starting batch generation for {len(posts_data)} posts...")
        start_time = datetime.utcnow()
        
        results = await asyncio.gather(
            *[process_single_post(post_data, i) for i, post_data in enumerate(posts_data)],
            return_exceptions=True
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Update final batch status
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
        batch_job.completed_posts = len(successful_results)
        batch_job.failed_posts = len(posts_data) - len(successful_results)
        batch_job.status = "completed" if batch_job.failed_posts == 0 else "completed_with_errors"
        self.db.commit()
        
        print(f"Batch completed in {processing_time:.2f} seconds")
        print(f"Success: {len(successful_results)}/{len(posts_data)} posts")
        
        return {
            'batch_id': batch_job_id,
            'total_posts': len(posts_data),
            'completed_posts': len(successful_results),
            'failed_posts': batch_job.failed_posts,
            'processing_time_seconds': processing_time,
            'results': results
        }