"""
Learner Profile Model
Represents the adaptive learning profile for each user
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConceptMastery(BaseModel):
    """Mastery level for a specific concept"""
    concept: str
    mastery_level: float = 0.0  # 0-100
    questions_attempted: int = 0
    questions_correct: int = 0
    last_attempted: Optional[datetime] = None
    trend: str = "stable"  # improving, stable, declining


class TopicProgress(BaseModel):
    """Progress tracking for a topic"""
    topic_id: str
    topic_name: str
    overall_mastery: float = 0.0
    concepts: List[ConceptMastery] = Field(default_factory=list)
    sessions_completed: int = 0
    total_time_minutes: int = 0
    last_studied: Optional[datetime] = None


class PerformanceWindow(BaseModel):
    """Recent performance snapshot"""
    timestamp: datetime
    score: float
    difficulty: str
    topic: str
    is_correct: bool


class LearningStyle(BaseModel):
    """Detected learning style preferences"""
    visual: float = 0.33  # Preference for diagrams, images
    auditory: float = 0.33  # Preference for voice, audio
    reading: float = 0.34  # Preference for text
    
    # Detected patterns
    best_time_of_day: Optional[str] = None  # morning, afternoon, evening
    optimal_session_length: int = 20  # minutes
    preferred_difficulty_progression: str = "gradual"  # gradual, aggressive


class LearnerProfile(Document):
    """Learner profile document model"""
    
    # User reference
    user_id: Indexed(str, unique=True)
    
    # Current adaptive state
    current_difficulty: str = "medium"
    current_focus_topics: List[str] = Field(default_factory=list)
    
    # Custom topics studied by the user (from custom query sessions)
    custom_topics: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Performance tracking
    performance_window: List[PerformanceWindow] = Field(default_factory=list)
    performance_window_size: int = 20  # Keep last N performances
    
    # Overall statistics
    overall_mastery: float = 0.0
    total_questions_attempted: int = 0
    total_questions_correct: int = 0
    total_study_time_minutes: int = 0
    
    # Topic-wise progress
    topic_progress: List[TopicProgress] = Field(default_factory=list)
    
    # Concept mastery (aggregated across topics)
    concept_mastery: Dict[str, ConceptMastery] = Field(default_factory=dict)
    
    # Identified strengths and weaknesses
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    
    # Knowledge gaps
    knowledge_gaps: List[str] = Field(default_factory=list)
    
    # Learning style
    learning_style: LearningStyle = Field(default_factory=LearningStyle)
    
    # Streaks and achievements
    current_streak_days: int = 0
    longest_streak_days: int = 0
    achievements: List[str] = Field(default_factory=list)
    
    # Recommendations queue
    pending_recommendations: List[str] = Field(default_factory=list)
    
    # Last session performance for adaptive starting baseline
    last_session_performance: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: Optional[datetime] = None
    
    class Settings:
        name = "learner_profiles"
        use_state_management = True
    
    @property
    def accuracy(self) -> float:
        """Calculate overall accuracy"""
        if self.total_questions_attempted == 0:
            return 0.0
        return (self.total_questions_correct / self.total_questions_attempted) * 100
    
    def add_performance(self, score: float, difficulty: str, topic: str, is_correct: bool):
        """Add a performance entry to the window"""
        entry = PerformanceWindow(
            timestamp=datetime.utcnow(),
            score=score,
            difficulty=difficulty,
            topic=topic,
            is_correct=is_correct
        )
        self.performance_window.append(entry)
        
        # Keep only recent performances
        if len(self.performance_window) > self.performance_window_size:
            self.performance_window = self.performance_window[-self.performance_window_size:]
    
    def get_recent_accuracy(self, n: int = 10) -> float:
        """Get accuracy for last N questions"""
        recent = self.performance_window[-n:] if self.performance_window else []
        if not recent:
            return 0.0
        correct = sum(1 for p in recent if p.is_correct)
        return (correct / len(recent)) * 100


class LearnerProfileResponse(BaseModel):
    """Schema for learner profile response"""
    user_id: str
    current_difficulty: str
    current_focus_topics: List[str]
    overall_mastery: float
    accuracy: float
    total_questions_attempted: int
    total_study_time_minutes: int
    strengths: List[str]
    weaknesses: List[str]
    knowledge_gaps: List[str]
    current_streak_days: int
    achievements: List[str]
    # Add recent_topics for dashboard Topics tab
    recent_topics: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class ProgressAnalytics(BaseModel):
    """Schema for progress analytics"""
    user_id: str
    period: str  # daily, weekly, monthly
    
    # Performance metrics
    questions_attempted: int
    questions_correct: int
    accuracy: float
    average_score: float
    
    # Time metrics
    total_study_time_minutes: int
    sessions_completed: int
    
    # Difficulty distribution
    difficulty_distribution: Dict[str, int]
    
    # Topic breakdown
    topics_studied: List[Dict[str, Any]]
    
    # Trends
    accuracy_trend: List[Dict[str, Any]]
    mastery_trend: List[Dict[str, Any]]
    
    # Comparisons
    improvement_percentage: float
    percentile_rank: Optional[float] = None
