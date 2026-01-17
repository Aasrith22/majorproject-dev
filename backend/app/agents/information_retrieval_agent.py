"""
Information Retrieval Agent
Second agent in the pipeline - fetches relevant content
"""

from typing import Dict, Any, Optional, List
from loguru import logger
import asyncio

from app.config import settings


class InformationRetrievalAgent:
    """
    Agent responsible for retrieving relevant learning materials
    
    Responsibilities:
    - Use intent and topic from Query Analysis Agent
    - Perform hybrid retrieval (semantic + keyword)
    - Use Annoy for efficient vector lookup
    - Filter content based on learner level
    """
    
    def __init__(self, llm_client=None, knowledge_service=None):
        """
        Initialize the Information Retrieval Agent
        
        Args:
            llm_client: LLM client for query expansion
            knowledge_service: Knowledge base service for retrieval
        """
        self.llm_client = llm_client
        self.knowledge_service = knowledge_service
        self.name = "Information Retrieval Agent"
        self.role = "Educational Content Curator"
        self.goal = "Find the most relevant and appropriate learning materials"
        self.backstory = """You are a master librarian and educational content specialist.
        You have an encyclopedic knowledge of educational resources and can quickly identify
        the most relevant materials for any learning need. You understand how to match
        content difficulty to learner levels and learning styles."""
    
    async def retrieve(
        self,
        query_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant content based on query analysis
        
        Args:
            query_analysis: Output from Query Analysis Agent
            context: Session context
            
        Returns:
            Retrieved content and metadata
        """
        context = context or {}
        
        try:
            # Extract search parameters from analysis
            topic_data = query_analysis.get("topic", {})
            if isinstance(topic_data, dict):
                topic = topic_data.get("main", "")
                subtopics = topic_data.get("subtopics", [])
            else:
                topic = str(topic_data) if topic_data else ""
                subtopics = []
            
            # Fallback to context topic if query_analysis doesn't have it
            if not topic:
                topic = context.get("topic", "general")
            
            logger.info(f"[InfoRetrieval] Retrieving content for topic: '{topic}'")
            
            difficulty = query_analysis.get("recommendations", {}).get("suggested_difficulty", "medium")
            intent = query_analysis.get("intent", {}).get("primary", "")
            
            # Expand query for better retrieval
            expanded_query = await self._expand_query(topic, subtopics, intent)
            
            # Perform retrieval
            results = await self._hybrid_retrieval(
                query=expanded_query,
                topic=topic,
                difficulty=difficulty,
                learner_profile=context.get("learner_profile", {}),
                modality=context.get("input_modality", "text")
            )
            
            # Rank and filter results
            ranked_results = self._rank_results(
                results,
                query_analysis,
                context
            )
            
            return {
                "status": "success",
                "query": expanded_query,
                "content_chunks": ranked_results,
                "total_found": len(ranked_results),
                "retrieval_metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "intent": intent,
                }
            }
            
        except Exception as e:
            logger.error(f"Information retrieval failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "content_chunks": [],
                "total_found": 0,
            }
    
    async def _expand_query(
        self,
        topic: str,
        subtopics: List[str],
        intent: str
    ) -> str:
        """Expand the search query for better retrieval"""
        
        # Combine topic and subtopics
        query_parts = [topic] + subtopics
        
        # Add intent-specific terms
        intent_expansions = {
            "definition_seeking": ["definition", "meaning", "what is"],
            "explanation_seeking": ["explanation", "how", "why", "concept"],
            "application_seeking": ["example", "application", "use case", "practice"],
            "clarification_seeking": ["simple explanation", "basics", "fundamentals"],
        }
        
        if intent in intent_expansions:
            query_parts.extend(intent_expansions[intent][:2])
        
        expanded = " ".join(query_parts)
        
        # Use LLM for more sophisticated expansion if available
        if self.llm_client:
            expanded = await self._llm_query_expansion(expanded, topic)
        
        return expanded
    
    async def _llm_query_expansion(self, query: str, topic: str) -> str:
        """Use LLM to expand search query"""
        
        prompt = f"""Expand the following educational search query with related terms and synonyms.
Keep the expansion focused and relevant to the topic.

Original query: "{query}"
Topic: "{topic}"

Return only the expanded query string, no explanation."""

        try:
            if hasattr(self.llm_client, 'chat'):
                response = await self.llm_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100
                )
                return response.choices[0].message.content.strip()
            
            elif hasattr(self.llm_client, 'generate_content'):
                # Gemini-style client - use sync method in async context
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(prompt)
                )
                return response.text.strip() if response.text else query
        
        except Exception as e:
            logger.warning(f"LLM query expansion failed: {e}")
        
        return query
    
    async def _hybrid_retrieval(
        self,
        query: str,
        topic: str,
        difficulty: str,
        learner_profile: Dict[str, Any],
        modality: str
    ) -> List[Dict[str, Any]]:
        """Perform hybrid semantic + keyword retrieval"""
        
        results = []
        
        # Semantic retrieval from knowledge base
        if self.knowledge_service:
            from app.services.knowledge_base import KnowledgeBaseService
            
            semantic_results = await KnowledgeBaseService.search(
                query=query,
                topic=topic if topic else None,
                difficulty=difficulty,
                limit=10,
                modality=modality
            )
            
            for result in semantic_results:
                results.append({
                    "content_id": result.content_id,
                    "content": result.content_text,
                    "summary": result.content_summary,
                    "topic": result.topic,
                    "difficulty": result.difficulty,
                    "relevance_score": result.relevance_score,
                    "concepts": result.concepts,
                    "source": "semantic_search"
                })
        
        # Fallback to sample content if no results
        if not results:
            results = self._get_fallback_content(topic, difficulty)
        
        return results
    
    def _get_fallback_content(
        self,
        topic: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Get fallback content when knowledge base is empty"""
        
        # Generate placeholder educational content
        return [{
            "content_id": f"fallback_{topic}",
            "content": f"""This is educational content about {topic}.
            
Key concepts:
- Understanding the fundamentals of {topic}
- Exploring how {topic} relates to broader concepts
- Practical applications of {topic}

Important points to remember:
1. {topic} is a fundamental concept that builds on prerequisite knowledge
2. Understanding {topic} requires practice and application
3. {topic} connects to many related areas of study""",
            "summary": f"Introduction to {topic} concepts",
            "topic": topic,
            "difficulty": difficulty,
            "relevance_score": 0.5,
            "concepts": [topic],
            "source": "fallback"
        }]
    
    def _rank_results(
        self,
        results: List[Dict[str, Any]],
        query_analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank and filter results based on relevance and learner profile"""
        
        if not results:
            return []
        
        learner_weaknesses = context.get("learner_profile", {}).get("weaknesses", [])
        learner_gaps = context.get("learner_profile", {}).get("knowledge_gaps", [])
        
        for result in results:
            score = result.get("relevance_score", 0.5)
            
            # Boost content that addresses known weaknesses
            content_concepts = result.get("concepts", [])
            for concept in content_concepts:
                if any(weakness.lower() in concept.lower() for weakness in learner_weaknesses):
                    score += 0.1
                if any(gap.lower() in concept.lower() for gap in learner_gaps):
                    score += 0.15
            
            # Adjust for difficulty match
            recommended_difficulty = query_analysis.get("recommendations", {}).get("suggested_difficulty", "medium")
            if result.get("difficulty") == recommended_difficulty:
                score += 0.1
            
            result["final_score"] = min(1.0, score)
        
        # Sort by final score
        ranked = sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)
        
        # Return top results
        return ranked[:5]
    
    def get_crew_agent_config(self) -> Dict[str, Any]:
        """Get configuration for CrewAI agent"""
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": True,
            "allow_delegation": False,
        }
