from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from typing import Set

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory token blacklist (in a production app, use Redis or a database)
token_blacklist: Set[str] = set()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def invalidate_token(token: str):
    """Add a token to the blacklist"""
    token_blacklist.add(token)
    return True

def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted"""
    return token in token_blacklist

async def get_current_user(token: str = Depends(security)):
    try:
        # Check if token is blacklisted
        if is_token_blacklisted(token.credentials):
            raise HTTPException(status_code=401, detail="Token has been invalidated")
            
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")