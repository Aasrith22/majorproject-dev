"""
Information Retrieval Agent
Second agent in the pipeline - fetches relevant content
Implements dynamic fallback with Tavily search for academic content
"""

from typing import Dict, Any, Optional, List
from loguru import logger
import asyncio

from app.config import settings


class InformationRetrievalAgent:
    """
    Agent responsible for retrieving relevant learning materials
    
    Retrieval Priority:
    1. Local Knowledge Base (semantic search)
    2. Dynamic Fallback via Tavily Search API (academic content)
    3. Structured Templates (last resort)
    
    Responsibilities:
    - Use intent and topic from Query Analysis Agent
    - Perform hybrid retrieval (semantic + keyword)
    - Dynamic web search for missing content
    - Filter content based on learner level and academic rigor
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
        self.tavily_client = self._init_tavily_client()
        self.name = "Information Retrieval Agent"
        self.role = "Educational Content Curator"
        self.goal = "Find the most relevant and appropriate learning materials"
        self.backstory = """You are a master librarian and educational content specialist.
        You have an encyclopedic knowledge of educational resources and can quickly identify
        the most relevant materials for any learning need. You understand how to match
        content difficulty to learner levels and learning styles."""
    
    def _init_tavily_client(self):
        """Initialize Tavily client for dynamic content retrieval"""
        if settings.tavily_api_key:
            try:
                from tavily import TavilyClient
                logger.info("[InfoRetrieval] Tavily client initialized for dynamic fallback")
                return TavilyClient(api_key=settings.tavily_api_key)
            except ImportError:
                logger.warning("[InfoRetrieval] tavily-python not installed, dynamic fallback disabled")
            except Exception as e:
                logger.warning(f"[InfoRetrieval] Failed to initialize Tavily: {e}")
        else:
            logger.info("[InfoRetrieval] No Tavily API key configured, using static fallback only")
        return None
    
    async def retrieve(
        self,
        query_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant content based on query analysis
        
        Retrieval Chain:
        1. Try local knowledge base
        2. If insufficient, trigger Tavily dynamic search
        3. If Tavily fails, use structured templates
        
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
                subject_domain = topic_data.get("subject", "General")
            else:
                topic = str(topic_data) if topic_data else ""
                subtopics = []
                subject_domain = "General"
            
            # Fallback to context topic if query_analysis doesn't have it
            if not topic:
                topic = context.get("topic", "general")
            
            logger.info(f"[InfoRetrieval] Retrieving content for topic: '{topic}', domain: '{subject_domain}'")
            
            difficulty = query_analysis.get("recommendations", {}).get("suggested_difficulty", "medium")
            intent = query_analysis.get("intent", {}).get("primary", "")
            
            # Expand query for better retrieval
            expanded_query = await self._expand_query(topic, subtopics, intent)
            
            # Step 1: Try local knowledge base
            results = await self._local_retrieval(
                query=expanded_query,
                topic=topic,
                difficulty=difficulty,
                learner_profile=context.get("learner_profile", {}),
                modality=context.get("input_modality", "text")
            )
            
            # Step 2: Check if results are sufficient (need at least 2 quality chunks)
            if not results or len(results) < 2:
                logger.info(f"[InfoRetrieval] Local results insufficient ({len(results) if results else 0}), triggering dynamic fallback")
                
                # Try Tavily dynamic search
                dynamic_results = await self._tavily_dynamic_search(
                    topic=topic,
                    subject_domain=subject_domain,
                    difficulty=difficulty,
                    subtopics=subtopics
                )
                
                if dynamic_results:
                    results = dynamic_results
                    logger.info(f"[InfoRetrieval] Tavily returned {len(results)} results")
                else:
                    # Final fallback: structured templates
                    logger.warning(f"[InfoRetrieval] Tavily failed, using structured templates")
                    results = self._get_structured_template_content(topic, subject_domain, difficulty)
            
            # Rank and filter results
            ranked_results = self._rank_results(results, query_analysis, context)
            
            return {
                "status": "success",
                "query": expanded_query,
                "content_chunks": ranked_results,
                "total_found": len(ranked_results),
                "retrieval_metadata": {
                    "topic": topic,
                    "subject_domain": subject_domain,
                    "difficulty": difficulty,
                    "intent": intent,
                    "source": ranked_results[0].get("source", "unknown") if ranked_results else "none"
                }
            }
            
        except Exception as e:
            logger.error(f"Information retrieval failed: {e}")
            # Even on error, return structured templates
            topic = context.get("topic", "general")
            return {
                "status": "partial",
                "error": str(e),
                "content_chunks": self._get_structured_template_content(topic, "General", "medium"),
                "total_found": 1,
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
    
    async def _local_retrieval(
        self,
        query: str,
        topic: str,
        difficulty: str,
        learner_profile: Dict[str, Any],
        modality: str
    ) -> List[Dict[str, Any]]:
        """Perform semantic retrieval from local knowledge base"""
        
        results = []
        
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
                    "source": "local_knowledge_base"
                })
        
        return results
    
    async def _tavily_dynamic_search(
        self,
        topic: str,
        subject_domain: str,
        difficulty: str,
        subtopics: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Perform dynamic search via Tavily API for academic content
        
        This is the primary fallback mechanism when local KB is insufficient.
        Uses rigorous search queries optimized for academic/professional content.
        """
        if not self.tavily_client:
            return []
        
        try:
            # Build rigorous academic search query
            difficulty_terms = {
                "easy": "introductory fundamentals",
                "medium": "intermediate concepts and applications",
                "hard": "advanced technical deep-dive",
                "expert": "expert-level professional specification"
            }
            diff_context = difficulty_terms.get(difficulty, "intermediate concepts")
            
            # Domain-specific search optimization
            domain_qualifiers = {
                "Computer_Science": "technical documentation algorithms implementation",
                "STEM": "scientific principles mathematical analysis",
                "Professional_Certification": "professional standards exam preparation",
                "Medical": "clinical guidelines physiological mechanisms",
                "Legal": "legal framework statutory interpretation",
                "Business": "business strategy management principles",
                "Engineering": "engineering specifications design analysis",
            }
            domain_qualifier = domain_qualifiers.get(subject_domain, "academic professional")
            
            # Construct rigorous search query
            search_query = f"{topic} {diff_context} {domain_qualifier} exam-style assessment concepts"
            
            if subtopics:
                search_query += f" {' '.join(subtopics[:3])}"
            
            logger.info(f"[InfoRetrieval] Tavily search: '{search_query}'")
            
            # Execute Tavily search (synchronously in executor)
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None,
                lambda: self.tavily_client.search(
                    query=search_query,
                    search_depth=settings.tavily_search_depth,
                    max_results=5,
                    include_answer=True,
                    include_raw_content=False
                )
            )
            
            # Process and filter results for academic relevance
            processed_results = self._process_tavily_results(
                search_results, 
                topic, 
                difficulty,
                subject_domain
            )
            
            return processed_results
            
        except Exception as e:
            logger.error(f"[InfoRetrieval] Tavily search failed: {e}")
            return []
    
    def _process_tavily_results(
        self,
        tavily_response: Dict[str, Any],
        topic: str,
        difficulty: str,
        subject_domain: str
    ) -> List[Dict[str, Any]]:
        """
        Process Tavily results and filter for academic quality
        
        Filters out:
        - Blog-like or informal content
        - Content that's too introductory for the requested difficulty
        - Low-relevance results
        """
        results = []
        
        # Extract the AI-generated answer if available (highest quality summary)
        answer = tavily_response.get("answer", "")
        if answer and len(answer) > 100:
            results.append({
                "content_id": f"tavily_answer_{topic}",
                "content": f"""ACADEMIC CONTENT SUMMARY: {topic}

{answer}

ASSESSMENT CONTEXT:
- Subject Domain: {subject_domain}
- Difficulty Level: {difficulty}
- Focus Areas: Core concepts, practical applications, common misconceptions""",
                "summary": f"AI-synthesized academic summary for {topic}",
                "topic": topic,
                "difficulty": difficulty,
                "relevance_score": 0.9,
                "concepts": [topic, f"{topic} applications", f"{topic} analysis"],
                "source": "tavily_ai_answer"
            })
        
        # Process individual search results
        search_results = tavily_response.get("results", [])
        
        # Relevance filter keywords (content should include academic indicators)
        academic_indicators = [
            "technical", "specification", "implementation", "analysis",
            "methodology", "framework", "architecture", "principles",
            "algorithm", "mechanism", "protocol", "standard", "theory",
            "research", "study", "examination", "evaluation", "assessment"
        ]
        
        # Low-quality indicators (filter these out)
        low_quality_indicators = [
            "blog", "opinion", "personal", "beginner's guide", 
            "for dummies", "easy introduction", "simple explanation"
        ]
        
        for result in search_results[:5]:
            content = result.get("content", "")
            title = result.get("title", "").lower()
            url = result.get("url", "").lower()
            score = result.get("score", 0.5)
            
            # Skip low-quality content
            if any(indicator in title or indicator in url for indicator in low_quality_indicators):
                logger.debug(f"[InfoRetrieval] Filtered out low-quality result: {title}")
                continue
            
            # Boost results with academic indicators
            academic_score = sum(1 for ind in academic_indicators if ind in content.lower())
            adjusted_score = min(1.0, score + (academic_score * 0.05))
            
            # Only include results with meaningful content
            if len(content) > 150 and adjusted_score >= 0.4:
                results.append({
                    "content_id": f"tavily_{hash(url) % 10000}",
                    "content": f"""TECHNICAL REFERENCE: {result.get('title', topic)}

{content}

SOURCE: {url}
RELEVANCE: High - Contains technical depth suitable for {difficulty} level assessment""",
                    "summary": result.get("title", f"Content about {topic}"),
                    "topic": topic,
                    "difficulty": difficulty,
                    "relevance_score": adjusted_score,
                    "concepts": [topic],
                    "source": "tavily_search"
                })
        
        return results
    
    def _get_structured_template_content(
        self,
        topic: str,
        subject_domain: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """
        Final fallback: Structured academic templates
        
        These templates are designed to guide the Question Generation Agent
        to create rigorous, academically-sound questions even without
        specific content from the knowledge base or web search.
        """
        
        # Domain-specific template blueprints
        templates = {
            "Computer_Science": f"""TECHNICAL ASSESSMENT FRAMEWORK: {topic}

<assessment_context>
Domain: Computer Science / Software Engineering
Topic: {topic}
Difficulty: {difficulty}
</assessment_context>

<core_competencies>
1. ALGORITHMIC UNDERSTANDING
   - Time complexity analysis (Big-O notation)
   - Space complexity trade-offs
   - Optimization strategies and their limitations

2. IMPLEMENTATION KNOWLEDGE
   - Design patterns applicable to {topic}
   - Edge cases and boundary conditions
   - Error handling and fault tolerance

3. SYSTEM DESIGN
   - Scalability considerations for {topic}
   - Performance bottlenecks and solutions
   - Integration patterns with other systems

4. DEBUGGING & TROUBLESHOOTING
   - Common failure modes in {topic}
   - Diagnostic approaches
   - Resolution strategies
</core_competencies>

<question_blueprints>
BLUEPRINT_A (Analysis): "Given a scenario with [Variable A] and [Variable B], evaluate the impact of {topic} on system performance. Which trade-off is unavoidable?"

BLUEPRINT_B (Application): "A production system using {topic} experiences [Symptom X]. Analyze the most likely root cause and propose the optimal resolution strategy."

BLUEPRINT_C (Comparison): "Compare the implementation of {topic} using approach [Method 1] versus [Method 2]. Under what conditions would each be preferred?"
</question_blueprints>""",

            "Professional_Certification": f"""PROFESSIONAL ASSESSMENT FRAMEWORK: {topic}

<assessment_context>
Domain: Professional Certification Standards
Topic: {topic}
Difficulty: {difficulty}
</assessment_context>

<competency_areas>
1. REGULATORY KNOWLEDGE
   - Applicable standards and frameworks for {topic}
   - Compliance requirements
   - Industry best practices

2. PROCEDURAL EXPERTISE
   - Standard operating procedures
   - Decision-making frameworks
   - Risk assessment methodologies

3. PROFESSIONAL JUDGMENT
   - Ethical considerations in {topic}
   - Stakeholder impact analysis
   - Documentation and reporting requirements
</competency_areas>

<question_blueprints>
BLUEPRINT_A (Procedural): "In a scenario where [Condition X] is met, how does {topic} dictate the optimal procedural response according to [Framework Y]?"

BLUEPRINT_B (Judgment): "A professional encounters [Ethical Dilemma] while implementing {topic}. Evaluate the appropriate course of action considering [Constraint Z]."

BLUEPRINT_C (Integration): "How do the requirements of {topic} interact with [Related Standard W] when [Condition] exists?"
</question_blueprints>""",

            "Medical": f"""CLINICAL ASSESSMENT FRAMEWORK: {topic}

<assessment_context>
Domain: Medical / Biomedical Sciences
Topic: {topic}
Difficulty: {difficulty}
</assessment_context>

<competency_areas>
1. MECHANISTIC UNDERSTANDING
   - Physiological pathways related to {topic}
   - Cellular and molecular mechanisms
   - Homeostatic regulation

2. CLINICAL APPLICATION
   - Diagnostic criteria and differential diagnosis
   - Treatment protocols and contraindications
   - Patient monitoring parameters

3. PATHOPHYSIOLOGY
   - Disease mechanisms affecting {topic}
   - Compensatory responses
   - Therapeutic targets
</competency_areas>

<question_blueprints>
BLUEPRINT_A (Mechanism): "Analyze the physiological pathway of {topic}. If [Inhibitor Z] is introduced, which downstream effect most clearly demonstrates understanding of the mechanism?"

BLUEPRINT_B (Clinical): "A patient presents with [Symptom Complex]. Based on the pathophysiology of {topic}, which finding would most strongly support the suspected diagnosis?"

BLUEPRINT_C (Therapeutic): "When treating a condition affecting {topic}, what is the primary consideration when [Comorbidity X] is present?"
</question_blueprints>""",

            "STEM": f"""SCIENTIFIC ASSESSMENT FRAMEWORK: {topic}

<assessment_context>
Domain: STEM (Science, Technology, Engineering, Mathematics)
Topic: {topic}
Difficulty: {difficulty}
</assessment_context>

<competency_areas>
1. THEORETICAL FOUNDATIONS
   - Fundamental principles governing {topic}
   - Mathematical models and equations
   - Assumptions and limitations

2. EXPERIMENTAL METHODOLOGY
   - Measurement techniques for {topic}
   - Error analysis and uncertainty
   - Data interpretation

3. APPLICATIONS
   - Real-world implementations of {topic}
   - Engineering considerations
   - Interdisciplinary connections
</competency_areas>

<question_blueprints>
BLUEPRINT_A (Analysis): "Given the relationship between [Variable A] and [Variable B] in {topic}, predict the outcome when [Condition C] is modified. Justify your reasoning."

BLUEPRINT_B (Evaluation): "An experiment investigating {topic} yields [Result X]. Evaluate potential sources of systematic error and their impact on conclusions."

BLUEPRINT_C (Synthesis): "Design an approach to measure [Property P] of {topic} given the constraints of [Limitation L]. What trade-offs are inherent in your design?"
</question_blueprints>"""
        }
        
        # Default general template for unspecified domains
        default_template = f"""ACADEMIC ASSESSMENT FRAMEWORK: {topic}

<assessment_context>
Domain: General Academic
Topic: {topic}
Difficulty: {difficulty}
</assessment_context>

<competency_areas>
1. CONCEPTUAL UNDERSTANDING
   - Core definitions and principles of {topic}
   - Relationships between key concepts
   - Historical development and context

2. ANALYTICAL SKILLS
   - Critical evaluation of {topic}
   - Comparison with related concepts
   - Identification of strengths and limitations

3. APPLICATION
   - Practical uses of {topic}
   - Problem-solving approaches
   - Real-world implications
</competency_areas>

<question_blueprints>
BLUEPRINT_A (Analysis): "Evaluate the relationship between [Concept A] and [Concept B] within the context of {topic}. What implications arise from this relationship?"

BLUEPRINT_B (Application): "Given a scenario involving {topic} and [Constraint X], determine the optimal approach and justify your reasoning."

BLUEPRINT_C (Synthesis): "How does understanding {topic} contribute to solving [Problem Type Y]? Provide a structured analysis."
</question_blueprints>

<assessment_guidelines>
- Questions should test application and analysis, NOT mere recall
- Distractors must represent plausible misconceptions
- Scenarios should reflect realistic professional/academic challenges
- Explanations should illuminate underlying principles
</assessment_guidelines>"""
        
        template_content = templates.get(subject_domain, default_template)
        
        return [{
            "content_id": f"template_{topic}_{subject_domain}",
            "content": template_content,
            "summary": f"Structured assessment framework for {topic}",
            "topic": topic,
            "difficulty": difficulty,
            "relevance_score": 0.75,
            "concepts": [topic, f"{topic} analysis", f"{topic} application"],
            "source": "structured_template"
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
            
            # Boost dynamic sources over static templates
            source = result.get("source", "")
            if source == "tavily_ai_answer":
                score += 0.15
            elif source == "tavily_search":
                score += 0.1
            elif source == "local_knowledge_base":
                score += 0.05
            
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
