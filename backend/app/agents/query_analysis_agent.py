"""
Query Analysis Agent
First agent in the pipeline - understands learner intent
"""

from typing import Dict, Any, Optional
from loguru import logger
import asyncio

from app.config import settings


class QueryAnalysisAgent:
    """
    Agent responsible for understanding learner input
    
    Responsibilities:
    - Analyze learner input semantically
    - Classify intent (definition, explanation, application)
    - Extract topic, subject, and difficulty
    - Interpret input in context of session history
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the Query Analysis Agent
        
        Args:
            llm_client: LLM client for analysis (OpenAI or Gemini)
        """
        self.llm_client = llm_client
        self.name = "Query Analysis Agent"
        self.role = "Educational Intent Analyzer"
        self.goal = "Understand exactly what the learner needs and categorize their request"
        self.backstory = """You are an expert educational psychologist and learning analyst. 
        Your specialty is understanding what students really mean when they ask questions or 
        provide answers. You can read between the lines, identify misconceptions, and 
        categorize learning needs with high accuracy."""
    
    async def analyze(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user input and extract structured intent
        
        Args:
            user_input: Raw user input (text, transcribed voice, or OCR text)
            context: Session context including history and profile
            
        Returns:
            Structured intent analysis
        """
        context = context or {}
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(user_input, context)
        
        try:
            logger.info(f"[QueryAnalysis] LLM client available: {self.llm_client is not None}")
            if self.llm_client:
                # Use LLM for analysis
                logger.info(f"[QueryAnalysis] Calling LLM for topic: '{user_input[:100]}'")
                response = await self._call_llm(prompt)
                logger.info(f"[QueryAnalysis] LLM response received")
                return self._parse_llm_response(response)
            else:
                # Fallback to rule-based analysis
                logger.warning(f"[QueryAnalysis] No LLM client, using rule-based analysis")
                return self._rule_based_analysis(user_input, context)
                
        except Exception as e:
            logger.error(f"[QueryAnalysis] Query analysis failed: {e}", exc_info=True)
            return self._default_analysis(user_input, context)
    
    def _build_analysis_prompt(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """Build the prompt for LLM analysis - Academic Assessment Focus"""
        
        session_history = context.get("session_history", [])
        learner_profile = context.get("learner_profile", {})
        topic = context.get("topic", "")
        
        prompt = f"""Analyze the following learner input for an ACADEMIC ASSESSMENT context.

LEARNER INPUT:
"{user_input}"

CONTEXT:
- Current Topic: {topic}
- Session History: {len(session_history)} previous interactions
- Known Weaknesses: {learner_profile.get('weaknesses', [])}
- Recent Accuracy: {learner_profile.get('recent_accuracy', 'Unknown')}%

Provide a structured analysis with the following:

1. SUBJECT DOMAIN CLASSIFICATION:
   - Domain: (STEM | Humanities | Professional_Certification | Computer_Science | Business | Medical | Legal | Engineering | Other)
   - Subdomain: Specific field within the domain (e.g., "Data Structures", "Constitutional Law")
   - Academic Level: (undergraduate | graduate | professional_certification | competitive_exam)

2. INTENT CLASSIFICATION:
   - Primary Intent: (definition_seeking | explanation_seeking | application_seeking | 
                      clarification_seeking | assessment_response | problem_solving)
   - Confidence: (0.0 to 1.0)

3. TOPIC EXTRACTION:
   - Main Topic: The specific technical/academic subject
   - Subtopics: Related technical concepts
   - Key Terminology: Domain-specific terms that should be used
   - Prerequisites: Foundational concepts needed

4. COGNITIVE RIGOR MAPPING:
   - Bloom's Level: (remember | understand | apply | analyze | evaluate | create)
   - Target Level: For assessment, prioritize 'analyze' or 'evaluate' over 'remember'
   - Complexity: (foundational | intermediate | advanced | expert)
   - Exam Context: Type of exam this might relate to (e.g., "University Exam", "Certification", "Competitive")

5. LEARNER STATE:
   - Understanding Level: (novice | developing | proficient | expert)
   - Engagement Level: (low | medium | high)
   - Learning Style Indicators: (theoretical | practical | visual | hands-on)

6. ASSESSMENT RECOMMENDATIONS:
   - Suggested Difficulty: (foundational | intermediate | advanced | expert)
   - Question Type: (mcq | fill_in_blank | essay | case_study | problem_solving)
   - Focus Areas: Specific technical concepts to assess
   - Avoid: Generic or trivia-style questions

IMPORTANT: Prioritize technical depth and professional exam standards.
Respond in JSON format."""

        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the analysis prompt"""
        
        try:
            if hasattr(self.llm_client, 'chat'):
                # OpenAI-style client
                response = await self.llm_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": self.backstory},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content
            
            elif hasattr(self.llm_client, 'generate_content_async'):
                # Gemini async client
                response = await self.llm_client.generate_content_async(
                    f"{self.backstory}\n\n{prompt}\n\nIMPORTANT: Respond with valid JSON only, no extra text."
                )
                # Check if response has candidates
                if hasattr(response, 'text') and response.text:
                    return response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    return response.candidates[0].content.parts[0].text
                else:
                    logger.warning(f"[QueryAnalysis] Empty Gemini response")
                    return "{}"
            
            elif hasattr(self.llm_client, 'generate_content'):
                # Gemini sync client - use in executor
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(
                        f"{self.backstory}\n\n{prompt}\n\nIMPORTANT: Respond with valid JSON only, no extra text."
                    )
                )
                # Check if response has text
                if hasattr(response, 'text') and response.text:
                    return response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    return response.candidates[0].content.parts[0].text
                else:
                    logger.warning(f"[QueryAnalysis] Empty Gemini response")
                    return "{}"
            
            return "{}"
            
        except Exception as e:
            logger.error(f"[QueryAnalysis] LLM call failed: {e}", exc_info=True)
            raise
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response, handling markdown code blocks"""
        import re
        
        if not response:
            return "{}"
        
        text = response.strip()
        
        # Try to extract JSON from markdown code blocks
        # Matches ```json ... ``` or ``` ... ```
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        matches = re.findall(code_block_pattern, text)
        if matches:
            text = matches[0].strip()
        
        # Find the first { and last } to extract JSON object
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
        
        return text
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        import json
        
        try:
            cleaned_response = self._extract_json_from_response(response)
            data = json.loads(cleaned_response)
            return {
                "intent": {
                    "primary": data.get("intent_classification", {}).get("primary_intent", "general_question"),
                    "confidence": data.get("intent_classification", {}).get("confidence", 0.5),
                },
                "topic": {
                    "main": data.get("topic_extraction", {}).get("main_topic", ""),
                    "subtopics": data.get("topic_extraction", {}).get("subtopics", []),
                    "subject": data.get("topic_extraction", {}).get("subject_area", ""),
                },
                "cognitive": {
                    "blooms_level": data.get("cognitive_level", {}).get("blooms_level", "understand"),
                    "complexity": data.get("cognitive_level", {}).get("complexity", "intermediate"),
                },
                "learner_state": data.get("learner_state", {}),
                "recommendations": data.get("assessment_recommendations", {}),
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}. Response was: {response[:200]}")
            return self._default_analysis("", {})
    
    def _rule_based_analysis(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback rule-based analysis when LLM is unavailable"""
        
        input_lower = user_input.lower()
        
        # Intent classification based on keywords
        intent = "general_question"
        if any(word in input_lower for word in ["what is", "define", "meaning of"]):
            intent = "definition_seeking"
        elif any(word in input_lower for word in ["explain", "how does", "why"]):
            intent = "explanation_seeking"
        elif any(word in input_lower for word in ["example", "apply", "use"]):
            intent = "application_seeking"
        elif any(word in input_lower for word in ["confused", "don't understand", "clarify"]):
            intent = "clarification_seeking"
        elif len(user_input.split()) < 20:
            # Short responses are likely assessment responses
            intent = "assessment_response"
        
        # Extract topic from context or input
        topic = context.get("topic", "")
        if not topic:
            # Simple extraction - first noun phrase
            words = user_input.split()
            topic = " ".join(words[:3]) if words else "general"
        
        # Determine complexity based on input length and vocabulary
        word_count = len(user_input.split())
        complexity = "basic" if word_count < 10 else "intermediate" if word_count < 50 else "advanced"
        
        # Determine difficulty recommendation
        recent_accuracy = context.get("learner_profile", {}).get("recent_accuracy", 50)
        if recent_accuracy > 80:
            difficulty = "hard"
        elif recent_accuracy > 60:
            difficulty = "medium"
        else:
            difficulty = "easy"
        
        return {
            "intent": {
                "primary": intent,
                "confidence": 0.7,  # Lower confidence for rule-based
            },
            "topic": {
                "main": topic,
                "subtopics": [],
                "subject": context.get("topic", "general"),
            },
            "cognitive": {
                "blooms_level": "understand",
                "complexity": complexity,
            },
            "learner_state": {
                "understanding_level": "partial",
                "emotional_tone": "neutral",
                "engagement_level": "medium",
            },
            "recommendations": {
                "suggested_difficulty": difficulty,
                "question_type": "mcq",
                "focus_areas": [],
            },
        }
    
    def _default_analysis(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return default analysis when all else fails"""
        return {
            "intent": {
                "primary": "general_question",
                "confidence": 0.3,
            },
            "topic": {
                "main": context.get("topic", "general"),
                "subtopics": [],
                "subject": "general",
            },
            "cognitive": {
                "blooms_level": "understand",
                "complexity": "intermediate",
            },
            "learner_state": {
                "understanding_level": "partial",
                "emotional_tone": "neutral",
                "engagement_level": "medium",
            },
            "recommendations": {
                "suggested_difficulty": "medium",
                "question_type": "mcq",
                "focus_areas": [],
            },
        }
    
    def get_crew_agent_config(self) -> Dict[str, Any]:
        """Get configuration for CrewAI agent"""
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": True,
            "allow_delegation": False,
        }
