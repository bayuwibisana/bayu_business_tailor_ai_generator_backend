from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
from pydantic import BaseModel

from services.batch_service import BatchGenerationService
from models.batch_job import BatchJob
from database import get_db
import auth

router = APIRouter()

# Pydantic models for request/response
class PostRequest(BaseModel):
    brand_name: str
    topic: str = "General"
    tone: str
    brief: str = ""
    target_audience: str = "General audience"

class BatchRequest(BaseModel):
    name: str = None
    posts: List[PostRequest]

class BatchJobResponse(BaseModel):
    id: str
    campaign_id: str
    name: str
    status: str
    total_posts: int
    completed_posts: int
    failed_posts: int
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@router.post("/campaigns/{campaign_id}/generate-batch")
async def start_batch_generation(
    campaign_id: str,
    batch_request: BatchRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)  # Add authentication
):
    try:
        # Create batch job record
        batch_job = BatchJob(
            campaign_id=campaign_id,
            name=batch_request.name or f'Batch {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            total_posts=len(batch_request.posts),
            status='pending',
            created_by=username  # Track who created this batch
        )
        db.add(batch_job)
        db.commit()
        db.refresh(batch_job)
        
        # Start background processing
        batch_service = BatchGenerationService(db)
        
        # Convert posts to dict format
        posts_data = [post.dict() for post in batch_request.posts]
        
        # For simplicity, we'll process synchronously
        # In production, use Celery or similar for background processing
        result = await batch_service.process_batch(
            str(batch_job.id), 
            posts_data
        )
        
        return {
            'batch_job': {
                'id': str(batch_job.id),
                'status': batch_job.status,
                'total_posts': batch_job.total_posts,
                'completed_posts': batch_job.completed_posts,
                'failed_posts': batch_job.failed_posts,
                'created_by': username
            },
            'result': result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/batches", response_model=List[BatchJobResponse])
async def get_batches_by_campaign(
    campaign_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)
):
    """
    Get all batch jobs for a specific campaign
    """
    try:
        # Get all batch jobs for this campaign and user
        batch_jobs = db.query(BatchJob).filter(
            BatchJob.campaign_id == campaign_id,
            BatchJob.created_by == username
        ).order_by(BatchJob.created_at.desc()).offset(skip).limit(limit).all()
        
        return batch_jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch-jobs/{job_id}/status")
async def get_batch_status(
    job_id: str, 
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)  # Add authentication
):
    batch_job = db.query(BatchJob).filter(BatchJob.id == job_id).first()
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    percentage = 0
    if batch_job.total_posts > 0:
        percentage = (batch_job.completed_posts / batch_job.total_posts) * 100
    
    return {
        'id': str(batch_job.id),
        'status': batch_job.status,
        'progress': {
            'total_posts': batch_job.total_posts,
            'completed_posts': batch_job.completed_posts,
            'failed_posts': batch_job.failed_posts,
            'remaining_posts': batch_job.total_posts - batch_job.completed_posts - batch_job.failed_posts,
            'percentage': round(percentage, 1)
        },
        'created_by': getattr(batch_job, 'created_by', username)
    }