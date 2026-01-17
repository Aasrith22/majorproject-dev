"""
User Model
Represents learner accounts and authentication
"""

from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class UserPreferences(BaseModel):
    """User learning preferences"""
    preferred_modality: str = "text"  # text, voice, diagram
    preferred_difficulty: str = "medium"
    daily_goal_minutes: int = 30
    notification_enabled: bool = True
    theme: str = "light"


class User(Document):
    """User document model"""
    
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Account status
    is_active: bool = True
    is_verified: bool = False
    
    # Learning profile reference
    learner_profile_id: Optional[str] = None
    
    # Preferences
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Statistics
    total_sessions: int = 0
    total_questions_answered: int = 0
    total_study_time_minutes: int = 0
    
    class Settings:
        name = "users"
        use_state_management = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "learner@example.com",
                "username": "learner123",
                "full_name": "John Doe",
            }
        }


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    preferences: UserPreferences
    created_at: datetime
    total_sessions: int
    total_questions_answered: int
    total_study_time_minutes: int
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
