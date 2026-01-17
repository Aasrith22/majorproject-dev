"""
Assessment Model
Represents questions and learner responses
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Question type enumeration"""
    MCQ = "mcq"
    FILL_IN_BLANK = "fill_in_blank"
    ESSAY = "essay"
    DIAGRAM = "diagram"
    VOICE = "voice"


class MCQOption(BaseModel):
    """MCQ option model"""
    id: str
    text: str
    is_correct: bool = False


class Assessment(Document):
    """Assessment/Question document model"""
    
    model_config = {"protected_namespaces": ()}
    
    # Question identification
    topic_id: Optional[str] = None
    topic_name: str
    subject: Optional[str] = None
    
    # Question content
    question_type: QuestionType
    question_text: str
    question_context: Optional[str] = None  # Additional context for the question
    
    # For MCQ
    options: Optional[List[MCQOption]] = None
    
    # For Fill in Blank
    blank_answer: Optional[str] = None
    acceptable_answers: Optional[List[str]] = None  # Variations of correct answer
    
    # For Essay
    model_answer: Optional[str] = None
    rubric: Optional[Dict[str, Any]] = None
    
    # For Diagram
    diagram_url: Optional[str] = None
    diagram_labels: Optional[Dict[str, str]] = None
    
    # Difficulty and metadata
    difficulty: str = "medium"  # beginner, easy, medium, hard, expert
    points: int = 10
    time_limit_seconds: Optional[int] = None
    
    # Concept mapping
    concepts: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    
    # Source tracking
    generated_by: str = "system"  # system, agent, manual
    source_content_ids: List[str] = Field(default_factory=list)
    
    # Statistics
    times_answered: int = 0
    times_correct: int = 0
    average_time_seconds: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "assessments"
        use_state_management = True
    
    @property
    def success_rate(self) -> float:
        """Calculate question success rate"""
        if self.times_answered == 0:
            return 0.0
        return (self.times_correct / self.times_answered) * 100


class AssessmentResponse(Document):
    """Learner response to an assessment"""
    
    # References
    user_id: Indexed(str)
    session_id: Indexed(str)
    assessment_id: Indexed(str)
    
    # Response content
    response_type: str  # text, voice, diagram
    response_content: str
    raw_input: Optional[str] = None  # Original input before processing
    
    # For MCQ
    selected_option_id: Optional[str] = None
    
    # Evaluation results
    is_correct: bool = False
    score: float = 0.0
    max_score: float = 10.0
    
    # Agent analysis
    conceptual_understanding: Optional[float] = None  # 0-100
    identified_misconceptions: List[str] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)
    
    # Detailed evaluation (from Question Generation Agent)
    evaluation_details: Dict[str, Any] = Field(default_factory=dict)
    
    # Time tracking
    time_taken_seconds: Optional[int] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Feedback reference
    feedback_id: Optional[str] = None
    
    class Settings:
        name = "assessment_responses"
        use_state_management = True


class QuestionRequest(BaseModel):
    """Schema for requesting a new question"""
    session_id: str
    preferred_type: Optional[str] = None
    preferred_difficulty: Optional[str] = None


class BatchQuestionRequest(BaseModel):
    """Schema for requesting batch questions at session start"""
    session_id: str
    count: int = 5
    preferred_type: Optional[str] = None


class QuestionResponse(BaseModel):
    """Schema for question response"""
    id: str
    question_type: str
    question_text: str
    question_context: Optional[str]
    options: Optional[List[Dict[str, Any]]]  # For MCQ, without is_correct
    difficulty: str
    points: int
    time_limit_seconds: Optional[int]
    concepts: List[str]
    agent_statuses: Optional[Dict[str, Any]] = None  # Agent execution metadata
    is_fallback: Optional[bool] = False  # Whether this is a fallback question
    
    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    """Schema for submitting an answer"""
    session_id: str
    assessment_id: str
    response_type: str = "text"
    response_content: str
    selected_option_id: Optional[str] = None  # For MCQ
    time_taken_seconds: Optional[int] = None


class AnswerEvaluation(BaseModel):
    """Schema for answer evaluation result"""
    response_id: str
    is_correct: bool
    score: float
    max_score: float
    correct_answer: Optional[str]
    explanation: str
    conceptual_understanding: float
    misconceptions: List[str]
    knowledge_gaps: List[str]
    next_steps: List[str]
