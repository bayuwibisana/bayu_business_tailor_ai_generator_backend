from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from database import get_db
from models.user import User
import auth
from auth import verify_password, get_password_hash, create_access_token, invalidate_token

router = APIRouter()

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str

class LogoutResponse(BaseModel):
    message: str
    status: str

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return an access token
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    token_data = {
        "sub": user_data.username,
        "user_id": str(new_user.id)
    }
    
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(new_user.id),
        "username": new_user.username
    }

@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token
    """
    # Find user by username
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    token_data = {
        "sub": user.username,
        "user_id": str(user.id)
    }
    
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "username": user.username
    }

@router.post("/logout", response_model=LogoutResponse)
async def logout_user(token: str = Depends(auth.security)):
    """
    Logout a user by invalidating their token
    """
    try:
        # Add token to blacklist
        invalidate_token(token.credentials)
        
        return {
            "message": "Successfully logged out",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}"
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(username: str = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """
    Get current authenticated user info
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    } 