"""
EduSynapse Agents Module
CrewAI agent definitions
"""

from app.agents.crew import EduSynapseCrew
from app.agents.query_analysis_agent import QueryAnalysisAgent
from app.agents.information_retrieval_agent import InformationRetrievalAgent
from app.agents.question_generation_agent import QuestionGenerationAgent
from app.agents.feedback_agent import FeedbackAgent

__all__ = [
    "EduSynapseCrew",
    "QueryAnalysisAgent",
    "InformationRetrievalAgent",
    "QuestionGenerationAgent",
    "FeedbackAgent",
]
