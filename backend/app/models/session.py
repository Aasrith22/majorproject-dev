"""
Learning Session Model
Represents a continuous learning interaction
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionInteraction(BaseModel):
    """Single interaction within a session"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_type: str  # text, voice, diagram
    input_content: str
    processed_content: Optional[str] = None  # After preprocessing
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    question_id: Optional[str] = None
    response_id: Optional[str] = None


class LearningSession(Document):
    """Learning session document model"""
    
    # Session identification
    user_id: Indexed(str)
    
    # Topic information
    topic_id: Optional[str] = None
    topic_name: str
    is_custom_topic: bool = False
    custom_query: Optional[str] = None
    
    # Session configuration
    target_questions: int = 10
    assessment_types: List[str] = Field(default_factory=lambda: ["mcq", "fill_in_blank", "essay"])
    
    # Session state
    status: SessionStatus = SessionStatus.ACTIVE
    current_difficulty: str = "medium"
    
    # Progress tracking
    questions_answered: int = 0
    correct_answers: int = 0
    total_score: float = 0.0
    
    # Interaction history
    interactions: List[SessionInteraction] = Field(default_factory=list)
    
    # Context for agents
    session_context: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Duration tracking
    total_duration_seconds: int = 0
    
    # Agent workflow results
    last_agent_output: Optional[Dict[str, Any]] = None
    
    class Settings:
        name = "learning_sessions"
        use_state_management = True
    
    @property
    def accuracy(self) -> float:
        """Calculate session accuracy"""
        if self.questions_answered == 0:
            return 0.0
        return (self.correct_answers / self.questions_answered) * 100
    
    @property
    def average_score(self) -> float:
        """Calculate average score per question"""
        if self.questions_answered == 0:
            return 0.0
        return self.total_score / self.questions_answered


class SessionCreate(BaseModel):
    """Schema for creating a new session"""
    topic_id: Optional[str] = None
    topic_name: str
    is_custom_topic: bool = False
    custom_query: Optional[str] = None
    target_questions: int = Field(default=10, ge=1, le=50)
    assessment_types: List[str] = Field(default_factory=lambda: ["mcq"])


class SessionInput(BaseModel):
    """Schema for submitting input to a session"""
    input_type: str = "text"  # text, voice, diagram
    content: str
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Schema for session response"""
    id: str
    user_id: str
    topic_name: str
    is_custom_topic: bool
    status: str
    current_difficulty: str
    questions_answered: int
    correct_answers: int
    accuracy: float
    total_score: float
    started_at: datetime
    last_activity_at: datetime
    
    class Config:
        from_attributes = True


class SessionSummary(BaseModel):
    """Schema for session summary with enhanced analytics"""
    session_id: str
    topic_name: str
    duration_minutes: int
    questions_answered: int
    correct_answers: int
    accuracy: float
    average_score: float
    difficulty_progression: List[str]
    strengths: List[Any]  # Can be strings or objects with detailed info
    weaknesses: List[Any]  # Can be strings or objects with detailed info
    recommendations: List[Any]  # Can be strings or objects with detailed info
    
    # Enhanced analytics from feedback agent
    learning_metrics: Optional[Dict[str, Any]] = None
    difficulty_analysis: Optional[Dict[str, Any]] = None
    performance_rating: Optional[Dict[str, Any]] = None
    improvement_areas: Optional[List[str]] = None
    mastered_concepts: Optional[List[str]] = None
