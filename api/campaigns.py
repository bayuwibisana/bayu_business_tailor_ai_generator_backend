from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from models.campaign import Campaign
from models.user import User
from models.campaign_post import CampaignPost
from database import get_db
import auth

router = APIRouter()

# Pydantic models for request/response
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    brand_name: str
    target_audience: Optional[str] = None
    tone_id: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    brand_name: Optional[str] = None
    target_audience: Optional[str] = None
    tone_id: Optional[str] = None
    status: Optional[str] = None

class CampaignResponse(CampaignBase):
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CampaignPostResponse(BaseModel):
    id: str
    batch_job_id: str
    campaign_id: str
    brand_name: str
    topic: Optional[str] = None
    tone: str
    brief: Optional[str] = None
    target_audience: Optional[str] = None
    generated_caption: Optional[str] = None
    generated_image_url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Get user_id from username
async def get_user_id(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user.id

# Create a new campaign
@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)
):
    try:
        # Get user ID from username
        user_id = await get_user_id(username, db)
        
        new_campaign = Campaign(
            name=campaign.name,
            description=campaign.description,
            brand_name=campaign.brand_name,
            target_audience=campaign.target_audience,
            tone_id=campaign.tone_id,
            user_id=user_id,
            status="draft"
        )
        
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)
        
        return new_campaign
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

# Get all campaigns for the current user
@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)
):
    # Get user ID from username
    user_id = await get_user_id(username, db)
    
    campaigns = db.query(Campaign).filter(
        Campaign.user_id == user_id,
        Campaign.status != "deleted"
    ).offset(skip).limit(limit).all()
    
    return campaigns

# Get a specific campaign
@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)
):
    # Get user ID from username
    user_id = await get_user_id(username, db)
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == user_id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign

# Update a campaign
@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)
):
    # Get user ID from username
    user_id = await get_user_id(username, db)
    
    # Find the campaign
    db_campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == user_id
    ).first()
    
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update the campaign with non-None values
    update_data = campaign_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_campaign, key, value)
    
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign

# Delete a campaign (soft delete)
@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)
):
    # Get user ID from username
    user_id = await get_user_id(username, db)
    
    # Find the campaign
    db_campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == user_id
    ).first()
    
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Soft delete by changing status
    db_campaign.status = "deleted"
    db.commit()
    
    return None

# Get all posts for a specific campaign
@router.get("/{campaign_id}/posts", response_model=List[CampaignPostResponse])
async def get_campaign_posts(
    campaign_id: UUID,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    username: str = Depends(auth.get_current_user)
):
    """
    Get all posts for a specific campaign
    """
    try:
        # Get user ID from username
        user_id = await get_user_id(username, db)
        
        # First verify the campaign belongs to the user
        campaign = db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id
        ).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Build query for campaign posts
        query = db.query(CampaignPost).filter(
            CampaignPost.campaign_id == str(campaign_id)
        )
        
        # Filter by status if provided
        if status:
            query = query.filter(CampaignPost.status == status)
        
        # Get posts with pagination
        posts = query.order_by(CampaignPost.created_at.desc()).offset(skip).limit(limit).all()
        
        return posts
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign posts: {str(e)}"
        ) 