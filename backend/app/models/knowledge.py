"""
Knowledge Chunk Model
Represents educational content stored in the knowledge base
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class KnowledgeChunk(Document):
    """Knowledge chunk document model for educational content"""
    
    # Content identification
    content_id: Indexed(str, unique=True)
    
    # Source information
    source_type: str  # textbook, article, video_transcript, etc.
    source_title: str
    source_url: Optional[str] = None
    source_author: Optional[str] = None
    
    # Content
    content_text: str
    content_summary: Optional[str] = None
    
    # Categorization
    subject: str
    topic: str
    subtopics: List[str] = Field(default_factory=list)
    
    # Difficulty and level
    difficulty: str = "medium"
    academic_level: str = "undergraduate"  # elementary, middle, high, undergraduate, graduate
    
    # Semantic information
    keywords: List[str] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    
    # Vector embedding
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_vector: Optional[List[float]] = None
    annoy_index_id: Optional[int] = None  # ID in Annoy index
    
    # Quality metrics
    quality_score: float = 1.0
    relevance_score: float = 1.0
    times_retrieved: int = 0
    
    # Modality suitability (0-1 scale)
    text_suitability: float = 1.0
    voice_suitability: float = 0.8
    diagram_suitability: float = 0.5
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "knowledge_chunks"
        use_state_management = True


class KnowledgeChunkCreate(BaseModel):
    """Schema for creating a knowledge chunk"""
    content_text: str
    source_type: str = "manual"
    source_title: str
    subject: str
    topic: str
    subtopics: List[str] = Field(default_factory=list)
    difficulty: str = "medium"
    keywords: List[str] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)


class KnowledgeSearchRequest(BaseModel):
    """Schema for searching knowledge base"""
    query: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)
    modality: str = "text"


class KnowledgeSearchResult(BaseModel):
    """Schema for knowledge search result"""
    content_id: str
    content_text: str
    content_summary: Optional[str]
    topic: str
    difficulty: str
    relevance_score: float
    concepts: List[str]
    
    class Config:
        from_attributes = True
