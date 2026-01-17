"""
EduSynapse Database Configuration
MongoDB connection and initialization using Motor and Beanie ODM
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from loguru import logger
from typing import Optional

from app.config import settings


class Database:
    """Database connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect(cls):
        """Establish database connection"""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
            
            # Import models here to avoid circular imports
            from app.models.user import User
            from app.models.session import LearningSession
            from app.models.assessment import Assessment, AssessmentResponse
            from app.models.feedback import Feedback
            from app.models.knowledge import KnowledgeChunk
            from app.models.learner_profile import LearnerProfile
            
            # Initialize Beanie with document models
            await init_beanie(
                database=cls.client[settings.mongodb_db_name],
                document_models=[
                    User,
                    LearningSession,
                    Assessment,
                    AssessmentResponse,
                    Feedback,
                    KnowledgeChunk,
                    LearnerProfile,
                ]
            )
            
            logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def get_database(cls):
        """Get database instance"""
        if cls.client is None:
            raise RuntimeError("Database not connected. Call Database.connect() first.")
        return cls.client[settings.mongodb_db_name]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection"""
        return cls.get_database()[collection_name]


# Dependency for FastAPI
async def get_db():
    """FastAPI dependency for database access"""
    return Database.get_database()
