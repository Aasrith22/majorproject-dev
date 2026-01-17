"""
Feedback Model
Represents personalized feedback from the Feedback Agent
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StrengthArea(BaseModel):
    """Identified strength area"""
    concept: str
    proficiency_level: float  # 0-100
    evidence: List[str] = Field(default_factory=list)


class WeaknessArea(BaseModel):
    """Identified weakness area"""
    concept: str
    current_level: float  # 0-100
    target_level: float
    improvement_suggestions: List[str] = Field(default_factory=list)


class LearningRecommendation(BaseModel):
    """Learning recommendation"""
    priority: int  # 1 = highest
    action: str
    reason: str
    resources: List[str] = Field(default_factory=list)
    estimated_time_minutes: Optional[int] = None


class Feedback(Document):
    """Feedback document model"""
    
    # References
    user_id: Indexed(str)
    session_id: Indexed(str)
    response_id: Optional[str] = None  # Specific response this feedback is for
    
    # Feedback type
    feedback_type: str = "response"  # response, session, topic, periodic
    
    # Main feedback content
    summary: str
    detailed_feedback: str
    
    # Strength and weakness analysis
    strengths: List[StrengthArea] = Field(default_factory=list)
    weaknesses: List[WeaknessArea] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[LearningRecommendation] = Field(default_factory=list)
    
    # Next actions
    suggested_topics: List[str] = Field(default_factory=list)
    suggested_difficulty: str = "medium"
    suggested_modality: str = "text"
    
    # Encouragement and motivation
    encouragement_message: Optional[str] = None
    achievement_unlocked: Optional[str] = None
    
    # Metrics
    overall_performance_score: float = 0.0
    improvement_trend: str = "stable"  # improving, stable, declining
    
    # Agent metadata
    generated_by_agent: str = "feedback_agent"
    agent_confidence: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "feedbacks"
        use_state_management = True


class FeedbackRequest(BaseModel):
    """Schema for requesting feedback"""
    session_id: str
    response_id: Optional[str] = None
    feedback_type: str = "response"


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: str
    feedback_type: str
    summary: str
    detailed_feedback: str
    strengths: List[Dict[str, Any]]
    weaknesses: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    suggested_topics: List[str]
    suggested_difficulty: str
    encouragement_message: Optional[str]
    overall_performance_score: float
    improvement_trend: str
    created_at: datetime
    
    class Config:
        from_attributes = True
