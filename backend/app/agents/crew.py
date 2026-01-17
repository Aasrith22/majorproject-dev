"""
EduSynapse CrewAI Orchestrator
Manages the multi-agent workflow for adaptive learning
"""

from typing import Dict, Any, Optional
from loguru import logger
import asyncio
import random

from app.config import settings, LLMConfig
from app.agents.query_analysis_agent import QueryAnalysisAgent
from app.agents.information_retrieval_agent import InformationRetrievalAgent
from app.agents.question_generation_agent import QuestionGenerationAgent
from app.agents.feedback_agent import FeedbackAgent


class EduSynapseCrew:
    """
    Main orchestrator for the EduSynapse multi-agent system
    
    Manages the execution flow:
    1. Query Analysis Agent → Understands learner intent
    2. Information Retrieval Agent → Fetches relevant content
    3. Question Generation Agent → Creates assessments & evaluates responses
    4. Feedback Agent → Generates personalized guidance
    """
    
    def __init__(self):
        """Initialize the crew with all agents"""
        
        # Get LLM client based on configuration
        self.llm_client = self._initialize_llm_client()
        logger.info(f"[Crew] LLM client initialized: {self.llm_client is not None}, type: {type(self.llm_client)}")
        
        # Initialize agents
        self.query_agent = QueryAnalysisAgent(llm_client=self.llm_client)
        self.retrieval_agent = InformationRetrievalAgent(
            llm_client=self.llm_client,
            knowledge_service=None  # Will use static method
        )
        self.question_agent = QuestionGenerationAgent(llm_client=self.llm_client)
        self.feedback_agent = FeedbackAgent(llm_client=self.llm_client)
        
        logger.info("EduSynapse Crew initialized")
    
    def _initialize_llm_client(self):
        """Initialize the appropriate LLM client"""
        
        try:
            provider, config = LLMConfig.get_active_provider()
            logger.info(f"[Crew] Using LLM provider: {provider}, model: {config.get('model', 'unknown')}")
            
            if provider == "openai":
                return self._get_openai_client(config)
            elif provider == "gemini":
                return self._get_gemini_client(config)
            
        except ValueError as e:
            logger.warning(f"LLM not configured: {e}. Running in fallback mode.")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return None
    
    def _get_openai_client(self, config: Dict[str, Any]):
        """Get OpenAI client"""
        try:
            from openai import AsyncOpenAI
            
            return AsyncOpenAI(api_key=config["api_key"])
        except ImportError:
            logger.warning("OpenAI package not installed")
            return None
    
    def _get_gemini_client(self, config: Dict[str, Any]):
        """Get Google Gemini client"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=config["api_key"])
            return genai.GenerativeModel(config["model"])
        except ImportError:
            logger.warning("Google GenerativeAI package not installed")
            return None
    
    async def execute(
        self,
        user_input: str,
        user_id: str,
        session_id: str,
        modality: str = "text",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the full agent pipeline
        
        Args:
            user_input: Processed user input
            user_id: User identifier
            session_id: Session identifier
            modality: Input modality (text, voice, diagram)
            context: Additional context from backend
            
        Returns:
            Combined output from all agents
        """
        context = context or {}
        context.update({
            "user_id": user_id,
            "session_id": session_id,
            "input_modality": modality,
        })
        
        result = {
            "status": "success",
            "agents_executed": [],
            "errors": [],
        }
        
        try:
            # Stage 1: Query Analysis
            logger.info(f"[Crew] Starting Query Analysis for session {session_id}")
            query_analysis = await self._execute_with_retry(
                self.query_agent.analyze,
                user_input,
                context
            )
            # gentle delay to avoid bursting LLM requests
            await asyncio.sleep(2)
            result["query_analysis"] = query_analysis
            result["agents_executed"].append("query_analysis")
            
            # Stage 2: Information Retrieval
            logger.info(f"[Crew] Starting Information Retrieval for session {session_id}")
            retrieved_content = await self._execute_with_retry(
                self.retrieval_agent.retrieve,
                query_analysis,
                context
            )
            # small delay before next agent to reduce burstiness
            await asyncio.sleep(2)
            result["retrieved_content"] = retrieved_content
            result["agents_executed"].append("information_retrieval")
            
            # Combine results for downstream agents
            result["intent"] = query_analysis.get("intent", {})
            result["topic"] = query_analysis.get("topic", {})
            result["recommendations"] = query_analysis.get("recommendations", {})
            
            logger.info(f"[Crew] Pipeline completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"[Crew] Pipeline error: {e}")
            result["status"] = "error"
            result["errors"].append(str(e))
        
        return result
    
    async def generate_question(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a new question using the agent pipeline
        
        Args:
            context: Context including session, user, and topic info
            
        Returns:
            Generated question with agent execution metadata
        """
        import time
        agent_statuses = {
            "query_analysis": {"status": "pending", "processingTime": 0},
            "information_retrieval": {"status": "pending", "processingTime": 0},
            "question_generation": {"status": "pending", "processingTime": 0},
        }
        
        try:
            # Get topic info
            topic = context.get("topic", "")
            is_custom = context.get("is_custom_topic", False)
            custom_query = context.get("custom_query", "")
            session_id = context.get("session_id", "unknown")
            
            # Use custom query or topic for analysis
            query_input = custom_query if is_custom and custom_query else topic
            
            logger.info(f"[Crew] Starting question generation for session {session_id}, topic: '{topic}'")
            
            # Stage 1: Analyze the topic/query
            logger.info(f"[Crew] Stage 1: Query Analysis for topic '{query_input}'")
            agent_statuses["query_analysis"]["status"] = "processing"
            start_time = time.time()
            
            query_analysis = await self._execute_with_retry(
                self.query_agent.analyze,
                query_input,
                context
            )
            
            agent_statuses["query_analysis"]["processingTime"] = int((time.time() - start_time) * 1000)
            agent_statuses["query_analysis"]["status"] = "completed"
            logger.info(f"[Crew] Query Analysis complete: {query_analysis.get('topic', {})}")
            # avoid firing subsequent agents immediately
            await asyncio.sleep(1.5)
            
            # Stage 2: Retrieve relevant content
            logger.info(f"[Crew] Stage 2: Information Retrieval")
            agent_statuses["information_retrieval"]["status"] = "processing"
            start_time = time.time()
            
            retrieved_content = await self._execute_with_retry(
                self.retrieval_agent.retrieve,
                query_analysis,
                context
            )
            
            agent_statuses["information_retrieval"]["processingTime"] = int((time.time() - start_time) * 1000)
            agent_statuses["information_retrieval"]["status"] = "completed"
            logger.info(f"[Crew] Retrieved {len(retrieved_content.get('content_chunks', []))} content chunks")
            await asyncio.sleep(1.5)
            
            # Stage 3: Generate question
            logger.info(f"[Crew] Stage 3: Question Generation")
            agent_statuses["question_generation"]["status"] = "processing"
            start_time = time.time()
            
            question = await self._execute_with_retry(
                self.question_agent.generate_question,
                retrieved_content,
                query_analysis,
                context
            )
            
            agent_statuses["question_generation"]["processingTime"] = int((time.time() - start_time) * 1000)
            agent_statuses["question_generation"]["status"] = "completed"
            logger.info(f"[Crew] Question generated: {question.get('question_text', '')[:100]}...")
            
            # Add source content IDs for tracking
            content_chunks = retrieved_content.get("content_chunks", [])
            question["source_content_ids"] = [
                c.get("content_id") for c in content_chunks if c.get("content_id")
            ]
            
            # Add agent execution metadata
            question["agent_statuses"] = agent_statuses
            
            return question
            
        except Exception as e:
            logger.error(f"[Crew] Question generation error: {e}")
            # Mark all incomplete agents as failed
            for agent_name, status in agent_statuses.items():
                if status["status"] != "completed":
                    status["status"] = "failed"
                    status["error"] = str(e)
            
            # Return fallback question with agent statuses
            fallback = self.question_agent._fallback_question(context)
            fallback["agent_statuses"] = agent_statuses
            fallback["is_fallback"] = True
            return fallback
    
    async def generate_batch_questions(
        self,
        context: Dict[str, Any],
        count: int = 5
    ) -> Dict[str, Any]:
        """
        Generate multiple questions at once for a session
        
        Args:
            context: Context including session, user, and topic info
            count: Number of questions to generate
            
        Returns:
            List of generated questions with agent execution metadata
        """
        import time
        agent_statuses = {
            "query_analysis": {"status": "pending", "processingTime": 0},
            "information_retrieval": {"status": "pending", "processingTime": 0},
            "question_generation": {"status": "pending", "processingTime": 0},
        }
        
        try:
            # Get topic info
            topic = context.get("topic", "")
            is_custom = context.get("is_custom_topic", False)
            custom_query = context.get("custom_query", "")
            session_id = context.get("session_id", "unknown")
            
            # Use custom query or topic for analysis
            query_input = custom_query if is_custom and custom_query else topic
            
            logger.info(f"[Crew] Starting batch question generation ({count} questions) for session {session_id}, topic: '{topic}'")
            
            # Stage 1: Analyze the topic/query (once)
            logger.info(f"[Crew] Stage 1: Query Analysis for topic '{query_input}'")
            agent_statuses["query_analysis"]["status"] = "processing"
            start_time = time.time()
            
            query_analysis = await self._execute_with_retry(
                self.query_agent.analyze,
                query_input,
                context
            )
            
            agent_statuses["query_analysis"]["processingTime"] = int((time.time() - start_time) * 1000)
            agent_statuses["query_analysis"]["status"] = "completed"
            logger.info(f"[Crew] Query Analysis complete: {query_analysis.get('topic', {})}")
            await asyncio.sleep(1.5)
            
            # Stage 2: Retrieve relevant content (once with more chunks)
            logger.info(f"[Crew] Stage 2: Information Retrieval")
            agent_statuses["information_retrieval"]["status"] = "processing"
            start_time = time.time()
            
            # Request more content chunks for multiple questions
            context["max_chunks"] = max(10, count * 2)
            retrieved_content = await self._execute_with_retry(
                self.retrieval_agent.retrieve,
                query_analysis,
                context
            )
            
            agent_statuses["information_retrieval"]["processingTime"] = int((time.time() - start_time) * 1000)
            agent_statuses["information_retrieval"]["status"] = "completed"
            logger.info(f"[Crew] Retrieved {len(retrieved_content.get('content_chunks', []))} content chunks")
            await asyncio.sleep(1.5)
            
            # Stage 3: Generate all questions at once
            logger.info(f"[Crew] Stage 3: Batch Question Generation ({count} questions)")
            agent_statuses["question_generation"]["status"] = "processing"
            start_time = time.time()
            
            questions = await self._execute_with_retry(
                self.question_agent.generate_batch_questions,
                retrieved_content,
                query_analysis,
                context,
                count
            )
            
            agent_statuses["question_generation"]["processingTime"] = int((time.time() - start_time) * 1000)
            agent_statuses["question_generation"]["status"] = "completed"
            logger.info(f"[Crew] Generated {len(questions)} questions")
            
            # Add source content IDs for tracking
            content_chunks = retrieved_content.get("content_chunks", [])
            source_ids = [c.get("content_id") for c in content_chunks if c.get("content_id")]
            
            for q in questions:
                q["source_content_ids"] = source_ids
            
            return {
                "questions": questions,
                "agent_statuses": agent_statuses,
                "is_fallback": False
            }
            
        except Exception as e:
            logger.error(f"[Crew] Batch question generation error: {e}")
            # Mark all incomplete agents as failed
            for agent_name, status in agent_statuses.items():
                if status["status"] != "completed":
                    status["status"] = "failed"
                    status["error"] = str(e)
            
            # Return fallback questions
            fallback_questions = [self.question_agent._fallback_question(context) for _ in range(count)]
            return {
                "questions": fallback_questions,
                "agent_statuses": agent_statuses,
                "is_fallback": True
            }

    async def evaluate_response(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a user's response using the agent pipeline
        
        Args:
            context: Context including assessment, response, and learner info
            
        Returns:
            Evaluation results
        """
        try:
            assessment = context.get("assessment", {})
            response = context.get("response", {})
            learner_context = context.get("learner_context", {})
            
            # Evaluate the response
            evaluation = await self._execute_with_retry(
                self.question_agent.evaluate_response,
                assessment,
                response,
                {"learner_profile": learner_context}
            )
            
            # Determine recommended difficulty adjustment
            from app.services.adaptive_engine import AdaptiveEngine
            
            is_correct = evaluation.get("is_correct", False)
            current_difficulty = assessment.get("difficulty", "medium")
            
            # Simple adjustment logic
            if is_correct and evaluation.get("conceptual_understanding", 0) > 80:
                evaluation["recommended_difficulty"] = AdaptiveEngine._increase_difficulty(current_difficulty)
            elif not is_correct and evaluation.get("conceptual_understanding", 0) < 40:
                evaluation["recommended_difficulty"] = AdaptiveEngine._decrease_difficulty(current_difficulty)
            else:
                evaluation["recommended_difficulty"] = current_difficulty
            
            return evaluation
            
        except Exception as e:
            logger.error(f"[Crew] Evaluation error: {e}")
            return {
                "is_correct": False,
                "score": 0,
                "error": str(e)
            }
    
    async def generate_feedback(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate feedback for a response
        
        Args:
            context: Context including evaluation results and learner profile
            
        Returns:
            Personalized feedback
        """
        try:
            evaluation = {
                "is_correct": context.get("response", {}).get("is_correct", False),
                "score": context.get("response", {}).get("score", 0),
                "conceptual_understanding": context.get("response", {}).get("conceptual_understanding", 50),
                "misconceptions": context.get("response", {}).get("misconceptions", []),
                "knowledge_gaps": context.get("response", {}).get("knowledge_gaps", []),
            }
            
            query_analysis = {
                "topic": {
                    "main": context.get("assessment", {}).get("topic", ""),
                },
                "recommendations": {}
            }
            
            feedback = await self._execute_with_retry(
                self.feedback_agent.generate_feedback,
                evaluation,
                query_analysis,
                context
            )
            
            return feedback
            
        except Exception as e:
            logger.error(f"[Crew] Feedback generation error: {e}")
            return self.feedback_agent._default_feedback(context)
    
    async def generate_session_summary(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Generate summary for a completed session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary with recommendations
        """
        try:
            # Get session data
            from app.models.session import LearningSession
            session = await LearningSession.get(session_id)
            
            if not session:
                return {
                    "error": "Session not found",
                    "difficulty_progression": [],
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": [],
                }
            
            # Generate summary using feedback agent
            session_data = {
                "questions_answered": session.questions_answered,
                "correct_answers": session.correct_answers,
                "topic_name": session.topic_name,
                "interactions": [i.model_dump() for i in session.interactions],
                "total_score": session.total_score,
            }
            
            return await self.feedback_agent.generate_session_summary(session_data)
            
        except Exception as e:
            logger.error(f"[Crew] Session summary error: {e}")
            return {
                "error": str(e),
                "difficulty_progression": [],
                "strengths": [],
                "weaknesses": [],
                "recommendations": ["Continue practicing to improve"],
            }
    
    async def _execute_with_retry(
        self,
        func,
        *args,
        max_retries: int = None,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic
        
        Args:
            func: Async function to execute
            *args: Positional arguments
            max_retries: Maximum retry attempts
            **kwargs: Keyword arguments
            
        Returns:
            Function result
        """
        max_retries = max_retries or settings.crewai_max_retries
        
        for attempt in range(max_retries):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=settings.crewai_timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"[Crew] Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
            except Exception as e:
                # Improved backoff with jitter and special handling for rate limits
                msg = str(e)
                logger.warning(f"[Crew] Error on attempt {attempt + 1}/{max_retries}: {msg}")
                if attempt == max_retries - 1:
                    raise

                # Detect rate-limit / quota errors and choose a longer sleep
                rate_limit_indicators = ["429", "Too Many Requests", "quota", "insufficient_quota", "rate limit"]
                if any(ind in msg for ind in rate_limit_indicators):
                    # Use a longer wait when API indicates rate limiting
                    backoff = min( max(55, settings.crewai_timeout), 120 )
                    jitter = random.uniform(0, 5)
                    sleep_for = backoff + jitter
                    logger.warning(f"[Crew] Detected rate-limit. Backing off for {sleep_for:.1f}s before retry")
                else:
                    # Exponential backoff with jitter for other errors
                    base = 2
                    max_backoff = 60
                    sleep_for = min(max_backoff, base * (2 ** attempt) + random.uniform(0, 1.5))

                await asyncio.sleep(sleep_for)
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get status of the crew and all agents"""
        return {
            "llm_configured": self.llm_client is not None,
            "llm_provider": settings.default_llm_provider,
            "agents": {
                "query_analysis": {
                    "name": self.query_agent.name,
                    "role": self.query_agent.role,
                },
                "information_retrieval": {
                    "name": self.retrieval_agent.name,
                    "role": self.retrieval_agent.role,
                },
                "question_generation": {
                    "name": self.question_agent.name,
                    "role": self.question_agent.role,
                },
                "feedback": {
                    "name": self.feedback_agent.name,
                    "role": self.feedback_agent.role,
                },
            },
            "settings": {
                "verbose": settings.crewai_verbose,
                "max_retries": settings.crewai_max_retries,
                "timeout": settings.crewai_timeout,
            }
        }
