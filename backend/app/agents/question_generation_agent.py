"""
Question Generation Agent
Third agent in the pipeline - creates adaptive assessments and evaluates responses
"""

from typing import Dict, Any, Optional, List
from loguru import logger
import random
import asyncio

from app.config import settings


class QuestionGenerationAgent:
    """
    Agent responsible for creating and evaluating assessments
    
    Responsibilities:
    Phase A - Question Creation:
    - Generate assessment questions using retrieved content
    - Adapt difficulty to learner profile
    - Select appropriate modality
    - Ensure diversity and progression
    
    Phase B - Response Evaluation:
    - Analyze learner response
    - Normalize multimodal inputs
    - Measure conceptual understanding
    - Identify misconceptions vs careless errors
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the Question Generation Agent
        
        Args:
            llm_client: LLM client for question generation
        """
        self.llm_client = llm_client
        self.name = "Question Generation Agent"
        self.role = "Adaptive Assessment Creator & Evaluator"
        self.goal = "Create perfectly calibrated questions and provide accurate evaluations"
        self.backstory = """You are an expert educational assessment designer with decades of
        experience creating adaptive tests. You understand Bloom's taxonomy deeply and can
        craft questions that accurately measure understanding at any cognitive level. You're
        also skilled at evaluating responses, distinguishing between genuine misconceptions
        and simple careless mistakes."""
    
    async def generate_question(
        self,
        retrieved_content: Dict[str, Any],
        query_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an adaptive question based on content and context
        
        Args:
            retrieved_content: Output from Information Retrieval Agent
            query_analysis: Output from Query Analysis Agent
            context: Session context
            
        Returns:
            Generated question with options and metadata
        """
        context = context or {}
        
        try:
            # Extract parameters
            content_chunks = retrieved_content.get("content_chunks", [])
            recommended_difficulty = query_analysis.get("recommendations", {}).get("suggested_difficulty", "medium")
            recommended_type = query_analysis.get("recommendations", {}).get("question_type", "mcq")
            
            # Get topic - prioritize context topic, then query_analysis
            topic_data = query_analysis.get("topic", {})
            if isinstance(topic_data, dict):
                topic = topic_data.get("main", "")
            else:
                topic = str(topic_data) if topic_data else ""
            
            # Fallback to context topic if query_analysis doesn't have it
            if not topic:
                topic = context.get("topic", "general topic")
            
            logger.info(f"[QuestionGen] Generating question for topic: '{topic}'")
            
            # Select content for question
            selected_content = self._select_content_for_question(content_chunks)
            
            # Determine question type based on context
            question_type = self._determine_question_type(
                recommended_type,
                context.get("session_history", []),
                context.get("learner_profile", {})
            )
            
            # Determine difficulty (random selection weighted by profile)
            difficulty = self._determine_difficulty(
                recommended_difficulty,
                context.get("learner_profile", {})
            )
            
            # Generate question using LLM
            logger.info(f"[QuestionGen] LLM client available: {self.llm_client is not None}, type: {type(self.llm_client)}")
            if self.llm_client:
                logger.info(f"[QuestionGen] Calling LLM to generate question for topic: '{topic}'")
                question = await self._llm_generate_question(
                    content=selected_content,
                    question_type=question_type,
                    difficulty=difficulty,
                    topic=topic,
                    context=context
                )
                logger.info(f"[QuestionGen] LLM returned question: {question.get('question_text', '')[:100]}")
            else:
                logger.warning(f"[QuestionGen] No LLM client, using rule-based generation")
                question = self._rule_based_generate_question(
                    content=selected_content,
                    question_type=question_type,
                    difficulty=difficulty,
                    topic=topic
                )
            
            return question
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return self._fallback_question(context)
    
    async def generate_batch_questions(
        self,
        retrieved_content: Dict[str, Any],
        query_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple questions at once
        
        Args:
            retrieved_content: Output from Information Retrieval Agent
            query_analysis: Output from Query Analysis Agent
            context: Session context
            count: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        context = context or {}
        questions = []
        
        try:
            # Extract parameters
            content_chunks = retrieved_content.get("content_chunks", [])
            topic_data = query_analysis.get("topic", {})
            if isinstance(topic_data, dict):
                topic = topic_data.get("main", "")
            else:
                topic = str(topic_data) if topic_data else ""
            
            if not topic:
                topic = context.get("topic", "general topic")
            
            logger.info(f"[QuestionGen] Generating {count} questions for topic: '{topic}'")
            
            # Get preferred question type from context
            preferred_type = context.get("preferred_type", "mcq")
            learner_profile = context.get("learner_profile", {})
            
            if self.llm_client:
                # Try batch generation first, then fall back to parallel individual generation
                try:
                    questions = await self._llm_generate_batch_questions(
                        content_chunks=content_chunks,
                        topic=topic,
                        count=count,
                        preferred_type=preferred_type,
                        learner_profile=learner_profile,
                        context=context
                    )
                    # Check if batch generation returned valid questions (not fallbacks)
                    if questions and len(questions) >= count and not all(
                        q.get("question_text", "").startswith("Based on your study of")
                        for q in questions
                    ):
                        return questions
                    
                    logger.warning(f"[QuestionGen] Batch generation returned fallbacks, trying parallel generation")
                except Exception as batch_error:
                    logger.warning(f"[QuestionGen] Batch generation failed: {batch_error}")
                
                # Fallback: Use parallel individual question generation
                logger.info(f"[QuestionGen] Using parallel individual question generation for {count} questions")
                questions = await self._parallel_generate_questions(
                    content_chunks=content_chunks,
                    topic=topic,
                    count=count,
                    preferred_type=preferred_type,
                    learner_profile=learner_profile,
                    context=context
                )
            else:
                # Fallback to rule-based generation
                for i in range(count):
                    # Vary difficulty across questions
                    difficulties = ["easy", "medium", "medium", "hard", "medium"]
                    difficulty = difficulties[i % len(difficulties)]
                    
                    # Select different content for each question
                    content = ""
                    if content_chunks and len(content_chunks) > i:
                        content = content_chunks[i % len(content_chunks)].get("content", "")
                    
                    question = self._rule_based_generate_question(
                        content=content,
                        question_type=preferred_type,
                        difficulty=difficulty,
                        topic=topic
                    )
                    # Add unique identifier to prevent duplicate questions
                    question["batch_index"] = i
                    questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Batch question generation failed: {e}")
            # Return fallback questions
            for i in range(count):
                fallback = self._fallback_question(context)
                fallback["batch_index"] = i
                questions.append(fallback)
            return questions
    
    async def _parallel_generate_questions(
        self,
        content_chunks: List[Dict[str, Any]],
        topic: str,
        count: int,
        preferred_type: str,
        learner_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate questions in parallel using asyncio.gather
        This is more robust than batch generation as individual failures don't affect others
        """
        difficulties = ["easy", "medium", "medium", "hard", "medium"]
        
        async def generate_single(index: int) -> Dict[str, Any]:
            try:
                difficulty = difficulties[index % len(difficulties)]
                content = ""
                if content_chunks and len(content_chunks) > 0:
                    content = content_chunks[index % len(content_chunks)].get("content", "")
                
                question = await self._llm_generate_question(
                    content=content,
                    question_type=preferred_type,
                    difficulty=difficulty,
                    topic=topic,
                    context={**context, "batch_index": index}
                )
                question["batch_index"] = index
                return question
            except Exception as e:
                logger.warning(f"[QuestionGen] Parallel gen failed for question {index}: {e}")
                fallback = self._academic_template_question(
                    topic=topic,
                    question_type=preferred_type,
                    difficulty=difficulties[index % len(difficulties)],
                    index=index
                )
                fallback["batch_index"] = index
                return fallback
        
        # Generate all questions in parallel
        tasks = [generate_single(i) for i in range(count)]
        questions = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and ensure all results are valid dicts
        valid_questions = []
        for i, q in enumerate(questions):
            if isinstance(q, dict):
                valid_questions.append(q)
            else:
                logger.warning(f"[QuestionGen] Question {i} returned exception: {q}")
                fallback = self._fallback_question(context)
                fallback["batch_index"] = i
                valid_questions.append(fallback)
        
        logger.info(f"[QuestionGen] Parallel generation completed: {len(valid_questions)} questions")
        return valid_questions
    
    async def _llm_generate_batch_questions(
        self,
        content_chunks: List[Dict[str, Any]],
        topic: str,
        count: int,
        preferred_type: str,
        learner_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple questions using LLM in a single call
        Uses rigorous academic prompts with XML behavior instructions
        """
        
        # Combine content from multiple chunks
        combined_content = "\n\n---\n\n".join([
            c.get("content", "") for c in content_chunks[:5]
        ])[:4000]  # Increased limit for better context
        
        # Extract learner profile data
        weaknesses = learner_profile.get("weaknesses", [])
        recent_accuracy = learner_profile.get("recent_accuracy", 50)
        
        # Check for previous attempts
        previous_attempts = context.get("previous_attempts", {})
        weak_concepts = previous_attempts.get("weak_concepts", [])
        previously_asked = previous_attempts.get("previously_asked_questions", [])
        
        # Determine difficulty distribution based on learner performance
        if recent_accuracy >= 80:
            difficulty_distribution = "40% hard, 40% medium, 20% expert"
            cognitive_focus = "analyze and evaluate"
        elif recent_accuracy >= 60:
            difficulty_distribution = "20% hard, 60% medium, 20% easy"
            cognitive_focus = "apply and analyze"
        else:
            difficulty_distribution = "40% easy, 40% medium, 20% hard"
            cognitive_focus = "understand and apply"
        
        # Type-specific output structure
        type_structure = {
            "mcq": '''For each question include:
            "options": [
                {"id": "A", "text": "Distractor: incomplete understanding", "is_correct": false},
                {"id": "B", "text": "Distractor: common misconception", "is_correct": false},
                {"id": "C", "text": "CORRECT answer (mark is_correct: true)", "is_correct": true},
                {"id": "D", "text": "Distractor: wrong scope/reversed logic", "is_correct": false}
            ]''',
            "fill_in_blank": '''For each question include:
            "blank_answer": "exact_term",
            "acceptable_answers": ["primary", "synonym", "abbreviation"]''',
            "essay": '''For each question include:
            "model_answer": "Comprehensive answer covering all key points",
            "rubric": {"conceptual_accuracy": "40%", "analysis": "30%", "application": "20%", "clarity": "10%"}'''
        }
        
        prompt = f'''<system_role>
You are an Expert Assessment Designer for high-stakes professional certification exams (CPA, MCAT, AWS Solutions Architect, Bar Exam).
You are creating a batch of {count} questions for the topic: {topic}
</system_role>

<behavior_instructions>
ABSOLUTE PROHIBITIONS (violation = invalid output):
1. NO TRIVIA - Never ask "What is...", "Define...", "Who invented...", "In what year..."
2. NO ROTE MEMORIZATION - Every question must require REASONING
3. NO OBVIOUS WRONG ANSWERS - Each distractor must fool someone with partial knowledge
4. NO DUPLICATE CONCEPTS - Each question must test a DIFFERENT aspect of {topic}
5. NO AMBIGUITY - Exactly ONE answer must be unambiguously correct

REQUIRED COGNITIVE LEVELS (Bloom's Taxonomy):
- Primary focus: {cognitive_focus.upper()}
- "Remember" level: FORBIDDEN
- "Understand" level: Maximum 1 question (must include application context)
- "Apply" level: Require specific scenarios with constraints
- "Analyze" level: Require comparison, cause-effect, or trade-off analysis
- "Evaluate" level: Require judgment between competing valid approaches

DISTRACTOR ENGINEERING (Critical for MCQ):
Each wrong answer MUST represent one of:
- Type 1: INCOMPLETE UNDERSTANDING - Partially correct but missing crucial insight
- Type 2: COMMON MISCONCEPTION - What someone who only skimmed the material would believe
- Type 3: REVERSED CAUSATION - Correct concept but wrong direction/scope
- Type 4: RELATED BUT DIFFERENT - True statement that doesn't answer the question

DIFFICULTY DISTRIBUTION: {difficulty_distribution}
</behavior_instructions>

<content_context>
REFERENCE MATERIAL (base questions on this content):
{combined_content if combined_content else f'Use established professional knowledge of {topic}'}

{f'ADAPTIVE FOCUS - Target these weak areas: {", ".join(weak_concepts[:5])}' if weak_concepts else ''}
{f'LEARNER WEAKNESSES: {", ".join(weaknesses[:3])}' if weaknesses else ''}
</content_context>

<avoid_repetition>
{f'DO NOT repeat or closely paraphrase these previously asked questions:{chr(10).join(f"- {q[:80]}..." for q in previously_asked[:5])}' if previously_asked else 'No previous questions to avoid.'}
</avoid_repetition>

<output_format>
Generate EXACTLY {count} questions in this JSON structure:
{{
    "questions": [
        {{
            "question_text": "Scenario-based question requiring analysis of {topic}",
            "question_context": "Specific constraints, values, or stakeholder perspectives",
            {type_structure.get(preferred_type, type_structure['mcq'])},
            "concepts": ["primary_concept_tested", "secondary_concept"],
            "explanation": "TEACHING explanation: (1) Why correct is correct, (2) Why each distractor is wrong, (3) Underlying principle",
            "difficulty": "easy|medium|hard|expert",
            "cognitive_level": "apply|analyze|evaluate",
            "points": 10,
            "time_limit_seconds": 90
        }}
    ]
}}

CRITICAL: The "explanation" must TEACH the concept, not just state facts.
</output_format>

<quality_checklist>
Before outputting, verify for EACH question:
[ ] Tests a DIFFERENT aspect of {topic} (no conceptual overlap)
[ ] Requires {cognitive_focus} - not just recall
[ ] Has specific scenario/constraints (not abstract)
[ ] For MCQ: Each distractor is wrong for a DIFFERENT reason
[ ] Explanation teaches the underlying principle
[ ] Could appear on a professional certification exam
</quality_checklist>'''

        try:
            if hasattr(self.llm_client, 'chat'):
                logger.info(f"[QuestionGen] Using OpenAI for batch generation ({count} questions)")
                response = await self.llm_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "You are an expert assessment designer. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                return self._parse_batch_questions(
                    response.choices[0].message.content,
                    preferred_type,
                    topic,
                    count
                )
            
            elif hasattr(self.llm_client, 'generate_content'):
                logger.info(f"[QuestionGen] Using Gemini for batch generation ({count} questions)")
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(
                        f"{prompt}\n\nIMPORTANT: Respond with valid JSON only. No markdown code blocks. No explanatory text."
                    )
                )
                logger.info(f"[QuestionGen] Gemini batch response received")
                return self._parse_batch_questions(
                    response.text,
                    preferred_type,
                    topic,
                    count
                )
                
        except Exception as e:
            logger.error(f"[QuestionGen] LLM batch generation failed: {e}", exc_info=True)
        
        # Fallback: Try individual LLM generation before rule-based
        logger.warning(f"[QuestionGen] Batch failed, attempting individual LLM generation")
        questions = []
        for i in range(count):
            try:
                content = content_chunks[i % len(content_chunks)].get("content", "") if content_chunks else ""
                question = await self._llm_generate_question(
                    content=content,
                    question_type=preferred_type,
                    difficulty=["easy", "medium", "medium", "hard", "medium"][i % 5],
                    topic=topic,
                    context=context
                )
                question["batch_index"] = i
                questions.append(question)
            except Exception as e:
                logger.warning(f"[QuestionGen] Individual LLM gen failed for question {i}: {e}")
                # Final fallback: academic template
                question = self._academic_template_question(
                    topic=topic,
                    question_type=preferred_type,
                    difficulty=["easy", "medium", "medium", "hard", "medium"][i % 5],
                    index=i
                )
                question["batch_index"] = i
                questions.append(question)
        return questions
    
    def _parse_batch_questions(
        self,
        response: str,
        question_type: str,
        topic: str,
        expected_count: int
    ) -> List[Dict[str, Any]]:
        """Parse LLM response containing multiple questions"""
        import json
        
        try:
            cleaned_response = self._extract_json_from_response(response)
            data = json.loads(cleaned_response)
            
            questions_data = data.get("questions", [])
            if not questions_data:
                raise ValueError("No questions in response")
            
            questions = []
            for i, q in enumerate(questions_data):
                # Build MCQ options
                options = None
                if question_type == "mcq" and q.get("options"):
                    options = [
                        {
                            "id": opt.get("id", chr(65 + j)),
                            "text": opt.get("text", ""),
                            "is_correct": opt.get("is_correct", False)
                        }
                        for j, opt in enumerate(q["options"])
                    ]
                
                question = {
                    "question_type": question_type,
                    "question_text": q.get("question_text", ""),
                    "context": q.get("question_context"),
                    "options": options,
                    "blank_answer": q.get("blank_answer"),
                    "acceptable_answers": q.get("acceptable_answers", []),
                    "model_answer": q.get("model_answer"),
                    "rubric": q.get("rubric"),
                    "concepts": q.get("concepts", [topic]),
                    "explanation": q.get("explanation"),
                    "points": q.get("points", 10),
                    "time_limit_seconds": q.get("time_limit_seconds", 60),
                    "batch_index": i,
                }
                questions.append(question)
            
            # If we didn't get enough questions, fill with fallbacks
            while len(questions) < expected_count:
                fallback = self._rule_based_generate_question(
                    content="",
                    question_type=question_type,
                    difficulty="medium",
                    topic=topic
                )
                fallback["batch_index"] = len(questions)
                questions.append(fallback)
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse batch questions JSON: {e}")
            # Return fallback questions
            questions = []
            for i in range(expected_count):
                fallback = self._rule_based_generate_question(
                    content="",
                    question_type=question_type,
                    difficulty="medium",
                    topic=topic
                )
                fallback["batch_index"] = i
                questions.append(fallback)
            return questions

    def _select_content_for_question(
        self,
        content_chunks: List[Dict[str, Any]]
    ) -> str:
        """Select the best content chunk for question generation"""
        
        if not content_chunks:
            return "General educational content."
        
        # Prefer highest scoring content
        sorted_chunks = sorted(
            content_chunks,
            key=lambda x: x.get("final_score", x.get("relevance_score", 0)),
            reverse=True
        )
        
        return sorted_chunks[0].get("content", "")
    
    def _determine_question_type(
        self,
        recommended_type: str,
        session_history: List[Dict[str, Any]],
        learner_profile: Dict[str, Any]
    ) -> str:
        """Determine question type, ensuring variety"""
        
        # Count recent question types
        recent_types = [
            h.get("question_type") for h in session_history[-5:]
            if h.get("question_type")
        ]
        
        # If recommended type was used recently, vary it
        available_types = ["mcq", "fill_in_blank", "essay"]
        
        if recent_types.count(recommended_type) >= 2:
            # Pick a different type
            other_types = [t for t in available_types if t != recommended_type]
            return random.choice(other_types)
        
        return recommended_type
    
    def _determine_difficulty(
        self,
        recommended: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Determine difficulty with some randomization"""
        
        from app.services.adaptive_engine import AdaptiveEngine
        
        # Use adaptive engine for weighted random selection
        # This creates variety while staying appropriate for the learner
        recent_accuracy = learner_profile.get("recent_accuracy", 50)
        
        difficulties = ["easy", "medium", "hard"]
        
        # Weight towards recommended but allow variation
        weights = {
            "easy": 0.2,
            "medium": 0.6,
            "hard": 0.2
        }
        
        if recommended in weights:
            weights[recommended] += 0.3
        
        # Adjust based on recent performance
        if recent_accuracy > 80:
            weights["hard"] += 0.2
            weights["easy"] -= 0.1
        elif recent_accuracy < 50:
            weights["easy"] += 0.2
            weights["hard"] -= 0.1
        
        # Normalize
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
        
        return random.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=1
        )[0]
    
    async def _llm_generate_question(
        self,
        content: str,
        question_type: str,
        difficulty: str,
        topic: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate question using LLM with retry logic for rate limits"""
        
        prompt = self._build_generation_prompt(
            content, question_type, difficulty, topic, context
        )
        
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if hasattr(self.llm_client, 'chat'):
                    logger.info(f"[QuestionGen] Using OpenAI-style client (attempt {attempt + 1})")
                    response = await self.llm_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[
                            {"role": "system", "content": self.backstory},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    return self._parse_generated_question(
                        response.choices[0].message.content,
                        question_type,
                        difficulty,
                        topic
                    )
                
                elif hasattr(self.llm_client, 'generate_content'):
                    # Gemini-style client - use sync method in async context
                    logger.info(f"[QuestionGen] Using Gemini client to generate question (attempt {attempt + 1})")
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: self.llm_client.generate_content(
                            f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
                        )
                    )
                    
                    # Check for valid response
                    if response and hasattr(response, 'text') and response.text:
                        response_text = response.text.strip()
                        # Check for rate limit error patterns in response
                        if 'quota' in response_text.lower() or 'rate limit' in response_text.lower():
                            raise Exception("Rate limit detected in response")
                        logger.info(f"[QuestionGen] Gemini response received: {response_text[:200]}")
                        return self._parse_generated_question(
                            response_text,
                            question_type,
                            difficulty,
                            topic
                        )
                    else:
                        logger.warning(f"[QuestionGen] Empty Gemini response on attempt {attempt + 1}")
                        raise Exception("Empty Gemini response")
                else:
                    logger.warning(f"[QuestionGen] Unknown LLM client type: {type(self.llm_client)}")
                    break
            
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = '429' in str(e) or 'quota' in error_str or 'rate' in error_str
                
                if is_rate_limit and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff: 2, 4, 8 seconds
                    logger.warning(f"[QuestionGen] Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"[QuestionGen] LLM question generation failed: {e}")
                    break
        
        logger.warning(f"[QuestionGen] Falling back to academic template generation")
        # Use index based on current time for variety
        import time
        unique_index = int(time.time() * 1000) % 100
        return self._academic_template_question(topic, question_type, difficulty, unique_index)
    
    def _build_generation_prompt(
        self,
        content: str,
        question_type: str,
        difficulty: str,
        topic: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build rigorous prompt for question generation using XML behavior instructions
        Designed for Gemini/Claude compliance with strict academic standards
        """
        
        import time
        random_seed = int(time.time() * 1000) % 10000
        
        # Extract learner profile data for adaptive difficulty
        learner_profile = context.get("learner_profile", {})
        recent_accuracy = learner_profile.get("recent_accuracy", 50)
        weaknesses = learner_profile.get("weaknesses", [])
        
        # Determine cognitive level based on difficulty and accuracy
        cognitive_mapping = {
            "easy": "understand",
            "medium": "apply",
            "hard": "analyze",
            "expert": "evaluate"
        }
        target_cognitive_level = cognitive_mapping.get(difficulty, "apply")
        
        # If learner has high accuracy, increase cognitive demand
        if recent_accuracy > 80:
            cognitive_upgrade = {"understand": "apply", "apply": "analyze", "analyze": "evaluate", "evaluate": "evaluate"}
            target_cognitive_level = cognitive_upgrade.get(target_cognitive_level, target_cognitive_level)
        
        # Difficulty-specific requirements
        difficulty_requirements = {
            "easy": "Single-concept application. Clear scenario with minimal confounding variables.",
            "medium": "Multi-step reasoning required. Integrate 2-3 related concepts.",
            "hard": "Complex scenario with trade-offs. Requires synthesis across multiple principles.",
            "expert": "Novel situation requiring deep expertise. Multi-step analysis with edge cases."
        }
        
        # Type-specific output format
        type_formats = {
            "mcq": '''"options": [
        {"id": "A", "text": "Plausible distractor representing incomplete understanding", "is_correct": false},
        {"id": "B", "text": "Distractor based on common misconception", "is_correct": false},
        {"id": "C", "text": "Correct answer with full technical accuracy", "is_correct": true},
        {"id": "D", "text": "Distractor with reversed cause-effect or wrong scope", "is_correct": false}
    ]''',
            "fill_in_blank": '''"blank_answer": "exact_technical_term",
    "acceptable_answers": ["primary_term", "acceptable_synonym", "abbreviated_form"]''',
            "essay": '''"model_answer": "Comprehensive model answer covering all key points",
    "rubric": {
        "conceptual_accuracy": "40% - Correct application of core principles",
        "analytical_depth": "30% - Quality of analysis and reasoning", 
        "practical_application": "20% - Real-world relevance",
        "communication": "10% - Clarity and organization"
    }'''
        }
        
        prompt = f'''<system_role>
You are an Expert Subject Matter Examiner for high-stakes professional assessments (CPA, MCAT, AWS Professional, Bar Exam level). You have 20+ years of experience designing questions for {topic}.
</system_role>

<behavior_instructions>
ABSOLUTE PROHIBITIONS:
1. NO TRIVIA QUESTIONS - Never ask "What is...", "Define...", "Who invented...", "What year..."
2. NO ROTE MEMORIZATION - Questions must require reasoning, not recall
3. NO OBVIOUS DISTRACTORS - Every wrong option must be plausible to someone with partial knowledge
4. NO AMBIGUOUS CORRECT ANSWERS - Exactly one answer must be unambiguously correct

REQUIRED BEHAVIORS:
1. BLOOM'S TAXONOMY COMPLIANCE - Target cognitive level: {target_cognitive_level.upper()}
   - Remember/Understand: FORBIDDEN for this assessment
   - Apply: Minimum acceptable level - use in concrete scenarios
   - Analyze: Break down complex situations, identify relationships
   - Evaluate: Judge between competing approaches with trade-offs
   - Create: Design solutions (for essay only)

2. DISTRACTOR ENGINEERING (for MCQ):
   - Distractor A: Represents INCOMPLETE understanding (partially correct but missing key insight)
   - Distractor B: Represents COMMON MISCONCEPTION (what a beginner typically believes)
   - Distractor C or D: Represents REVERSED LOGIC or WRONG SCOPE (correct concept, wrong application)
   - The correct answer must be defensible with evidence from the content

3. SCENARIO-BASED FRAMING:
   - Every question MUST include a realistic scenario or constraint
   - Use specific values, conditions, or stakeholder perspectives
   - Avoid abstract "in general" questions

4. ADAPTIVE RIGOR:
   - Difficulty: {difficulty.upper()}
   - Requirement: {difficulty_requirements.get(difficulty, "Multi-step reasoning required")}
   {'- FOCUS ON WEAKNESSES: ' + ', '.join(weaknesses[:3]) if weaknesses else ''}
</behavior_instructions>

<content_context>
Topic: {topic}
Question Type: {question_type}

REFERENCE MATERIAL:
{content[:3000] if content else f'Generate based on established professional knowledge of {topic}'}
</content_context>

<output_format>
Generate a JSON object with this EXACT structure:
{{
    "question_text": "Scenario-based question requiring {target_cognitive_level}-level thinking about {topic}",
    "question_context": "Additional context, constraints, or scenario details if needed",
    {type_formats.get(question_type, type_formats['mcq'])},
    "concepts": ["primary_concept", "secondary_concept"],
    "explanation": "Detailed explanation: (1) Why correct answer is correct, (2) Why each distractor is wrong, (3) The underlying principle being tested",
    "difficulty": "{difficulty}",
    "cognitive_level": "{target_cognitive_level}",
    "points": 10,
    "time_limit_seconds": {90 if question_type == "mcq" else 180 if question_type == "fill_in_blank" else 600}
}}
</output_format>

<quality_checklist>
Before outputting, verify:
[ ] Question requires {target_cognitive_level.upper()}-level thinking, not just recall
[ ] Scenario is specific and realistic for {topic}
[ ] For MCQ: Each distractor represents a different type of error
[ ] Correct answer is unambiguously correct based on the content
[ ] Explanation teaches the underlying principle, not just states the answer
[ ] Question reflects what would appear on a professional certification exam
</quality_checklist>'''
        
        return prompt
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response, handling markdown code blocks and malformed JSON"""
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
        
        # Fix common JSON issues from LLM outputs
        # Remove trailing commas before } or ]
        text = re.sub(r',\s*([}\]])', r'\1', text)
        # Fix unescaped newlines in strings
        text = re.sub(r'(?<!\\)\n(?=[^"]*"[^"]*$)', r'\\n', text)
        # Fix single quotes to double quotes (be careful with apostrophes)
        text = re.sub(r"(?<=[{,:\[\s])\'([^']*?)\'(?=[,}\]\s:])", r'"\1"', text)
        
        return text
    
    def _parse_generated_question(
        self,
        response: str,
        question_type: str,
        difficulty: str,
        topic: str
    ) -> Dict[str, Any]:
        """Parse LLM response into question format"""
        import json
        
        try:
            cleaned_response = self._extract_json_from_response(response)
            data = json.loads(cleaned_response)
            
            # Build MCQ options
            options = None
            if question_type == "mcq" and data.get("options"):
                options = [
                    {
                        "id": opt.get("id", chr(65 + i)),
                        "text": opt.get("text", ""),
                        "is_correct": opt.get("is_correct", False)
                    }
                    for i, opt in enumerate(data["options"])
                ]
            
            return {
                "question_type": question_type,
                "question_text": data.get("question_text", ""),
                "context": data.get("question_context"),
                "options": options,
                "blank_answer": data.get("blank_answer"),
                "acceptable_answers": data.get("acceptable_answers", []),
                "model_answer": data.get("model_answer"),
                "rubric": data.get("rubric"),
                "difficulty": difficulty,
                "concepts": data.get("concepts", [topic]),
                "explanation": data.get("explanation"),
                "points": data.get("points", 10),
                "time_limit_seconds": data.get("time_limit_seconds", 60),
            }
            
        except json.JSONDecodeError:
            logger.error("Failed to parse question JSON")
            return self._fallback_question({"topic": topic})
    
    def _rule_based_generate_question(
        self,
        content: str,
        question_type: str,
        difficulty: str = "medium",
        topic: str = "general"
    ) -> Dict[str, Any]:
        """Generate professional-quality question using rules when LLM unavailable"""
        
        # Extract key concepts from content for more relevant questions
        content_words = content.lower().split() if content else []
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'this', 'that', 'with', 'have', 'from', 'they', 'been', 'has', 'were', 'said', 'each', 'which', 'their', 'will', 'way', 'about', 'many', 'then', 'them', 'these', 'some', 'would', 'make', 'like', 'into', 'time', 'very', 'when', 'come', 'made', 'find', 'more', 'long', 'him', 'how', 'its', 'may', 'did', 'get', 'than', 'now', 'what', 'over', 'such', 'use'}
        key_concepts = [w for w in content_words if len(w) > 4 and w not in common_words][:10]
        
        import random
        import hashlib
        import time
        
        # Create unique seed based on topic, content, and current time for variety
        seed_str = f"{topic}_{content[:100] if content else 'default'}_{int(time.time())}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        
        if question_type == "mcq":
            # Professional-level MCQ templates - application and analysis focused
            mcq_templates = [
                (f"In a professional context, which approach would be MOST effective when implementing {topic}?",
                 [f"Systematic application of {topic} principles with iterative validation",
                  f"Rapid implementation without planning phases",
                  f"Complete avoidance of established {topic} methodologies",
                  f"Implementing only the simplest aspects while ignoring complex requirements"]),
                (f"When analyzing a system that utilizes {topic}, which factor is MOST critical for optimization?",
                 [f"Understanding the core mechanisms and their interactions within {topic}",
                  f"Focusing solely on surface-level metrics",
                  f"Ignoring performance considerations entirely",
                  f"Applying random modifications without analysis"]),
                (f"A senior engineer discovers a performance bottleneck related to {topic}. What is the recommended first step?",
                 [f"Analyze the {topic} implementation to identify the root cause",
                  f"Immediately rewrite the entire system",
                  f"Ignore the issue if it doesn't cause crashes",
                  f"Add more resources without investigation"]),
                (f"Which statement BEST describes an advanced application of {topic}?",
                 [f"{topic} can be leveraged for complex problem-solving when properly understood",
                  f"{topic} is only suitable for trivial applications",
                  f"{topic} cannot be combined with other methodologies",
                  f"{topic} provides no practical benefits in real systems"]),
                (f"What distinguishes expert-level understanding of {topic} from beginner knowledge?",
                 [f"Ability to apply {topic} concepts to novel situations and edge cases",
                  f"Memorization of basic definitions only",
                  f"Avoiding practical implementation entirely",
                  f"Relying solely on default configurations"]),
            ]
            
            template = rng.choice(mcq_templates)
            options = template[1].copy()
            correct_answer = options[0]  # First option is correct
            rng.shuffle(options)  # Shuffle to randomize position
            
            return {
                "question_type": "mcq",
                "question_text": template[0],
                "options": [
                    {"id": chr(65 + i), "text": opt, "is_correct": opt == correct_answer}
                    for i, opt in enumerate(options)
                ],
                "concepts": [topic] + key_concepts[:3],
                "explanation": f"Understanding {topic} at a professional level requires systematic application and deep analysis of core principles.",
                "points": 10,
                "time_limit_seconds": 90,
            }
        
        elif question_type == "fill_in_blank":
            fill_templates = [
                (f"When optimizing {topic} implementations, the technique of _______ is commonly used to improve performance.", "profiling"),
                (f"In {topic}, the principle of _______ helps ensure maintainable and scalable solutions.", "modularity"),
                (f"A critical consideration when working with {topic} at scale is proper _______ management.", "resource"),
                (f"Expert practitioners of {topic} recommend _______ as a best practice for complex implementations.", "documentation"),
            ]
            
            template = rng.choice(fill_templates)
            
            return {
                "question_type": "fill_in_blank",
                "question_text": template[0],
                "blank_answer": template[1],
                "acceptable_answers": [template[1], template[1].lower(), template[1].capitalize()],
                "concepts": [topic],
                "explanation": f"This term is fundamental to professional {topic} implementation.",
                "points": 10,
                "time_limit_seconds": 60,
            }
        
        else:  # essay
            essay_templates = [
                f"Analyze the trade-offs involved when implementing {topic} in a large-scale system. Discuss performance, maintainability, and scalability considerations.",
                f"Compare two different approaches to implementing {topic}. Evaluate their strengths, weaknesses, and appropriate use cases.",
                f"Describe a scenario where {topic} would be the optimal solution and another where it might be problematic. Justify your reasoning.",
                f"Design a solution using {topic} for a complex real-world problem. Explain your architectural decisions and potential challenges.",
            ]
            
            question = rng.choice(essay_templates)
            
            return {
                "question_type": "essay",
                "question_text": question,
                "model_answer": f"A comprehensive answer should include: 1) Technical analysis of {topic} principles, 2) Specific trade-offs and their implications, 3) Real-world considerations and constraints, 4) Evidence-based recommendations.",
                "rubric": {
                    "technical_accuracy": "Demonstrates deep technical understanding (30%)",
                    "analysis": "Provides thorough analysis of trade-offs (25%)",
                    "practical_application": "Relates concepts to real-world scenarios (25%)",
                    "clarity": "Well-organized with clear argumentation (20%)",
                },
                "concepts": [topic] + key_concepts[:2],
                "points": 25,
                "time_limit_seconds": 600,
            }
    
    def _fallback_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback question when all else fails - still topic-aware"""
        import time
        topic = context.get("topic", "the subject")
        question_type = context.get("preferred_type", "mcq")
        
        # Use time-based index for variety
        unique_index = int(time.time() * 1000) % 100
        
        # Use academic template generation for rigorous fallback
        return self._academic_template_question(
            topic=topic,
            question_type=question_type,
            difficulty="medium",
            index=unique_index
        )
    
    def _academic_template_question(
        self,
        topic: str,
        question_type: str,
        difficulty: str,
        index: int
    ) -> Dict[str, Any]:
        """
        Generate rigorous academic template questions
        
        These templates are designed based on professional certification exam formats
        (CPA, MCAT, AWS, etc.) and follow strict academic assessment principles.
        
        Used as final fallback when LLM generation fails.
        """
        import hashlib
        import time
        import uuid
        
        # Create truly varied seed based on topic, index, and unique identifier
        # This ensures different questions even when called multiple times within the same second
        seed_str = f"{topic}_{index}_{time.time()}_{uuid.uuid4().hex[:8]}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        
        # Domain-specific template banks
        templates = {
            "mcq": {
                "technical": [
                    {
                        "pattern": "scenario_analysis",
                        "question": f"A development team is implementing a solution using {topic}. During code review, they discover that [Approach A] was used instead of the recommended [Approach B]. What is the MOST significant implication of this decision?",
                        "options": [
                            ("The system may exhibit [specific degradation pattern] under [specific conditions], requiring refactoring", True),
                            ("There will be no noticeable difference in behavior or performance", False),
                            ("The code will fail to compile due to syntax errors", False),
                            ("All unit tests will automatically fail regardless of implementation", False),
                        ],
                        "explanation": "This question tests understanding of implementation trade-offs in {topic}. The correct answer addresses the nuanced performance implications, while distractors represent common oversimplifications."
                    },
                    {
                        "pattern": "troubleshooting",
                        "question": f"A production system using {topic} exhibits intermittent failures characterized by [Symptom X]. Diagnostic logs show [Pattern Y]. Which root cause is MOST consistent with these observations?",
                        "options": [
                            ("Resource contention occurring when [Condition A] coincides with [Condition B]", True),
                            ("Hardware failure that would cause consistent, not intermittent, issues", False),
                            ("User input errors that would be caught by validation", False),
                            ("Network latency that would affect all operations equally", False),
                        ],
                        "explanation": "Effective troubleshooting of {topic} requires correlating symptoms with underlying mechanisms. The correct answer identifies the condition that explains the intermittent nature of the failure."
                    },
                    {
                        "pattern": "optimization",
                        "question": f"When optimizing a {topic} implementation for high-throughput scenarios, which strategy provides the BEST balance between performance gain and implementation complexity?",
                        "options": [
                            ("Implement targeted caching at the critical path identified through profiling", True),
                            ("Add parallel processing to all operations regardless of bottleneck location", False),
                            ("Increase hardware resources without code changes", False),
                            ("Remove all validation and error handling to reduce overhead", False),
                        ],
                        "explanation": "Optimization in {topic} should be evidence-based. The correct approach targets identified bottlenecks rather than applying blanket changes."
                    },
                    {
                        "pattern": "comparison",
                        "question": f"When comparing [Method 1] and [Method 2] for implementing {topic}, under which conditions would [Method 1] be clearly preferred?",
                        "options": [
                            ("When [Constraint A] is present and [Requirement B] is critical to the use case", True),
                            ("In all circumstances, as [Method 1] is universally superior", False),
                            ("Only when budget constraints prevent using any solution", False),
                            ("When backwards compatibility is completely irrelevant", False),
                        ],
                        "explanation": "Method selection in {topic} depends on context. The correct answer identifies specific conditions, while distractors represent absolutist or irrelevant criteria."
                    },
                    {
                        "pattern": "edge_case",
                        "question": f"In a {topic} implementation, what is the expected behavior when [Edge Condition E] is encountered during [Operation O]?",
                        "options": [
                            ("The system should [graceful handling behavior] and [recovery action]", True),
                            ("The system should crash immediately to prevent data corruption", False),
                            ("Edge conditions are theoretical and never occur in practice", False),
                            ("The behavior is undefined and implementation-specific", False),
                        ],
                        "explanation": "Understanding edge cases in {topic} distinguishes expert practitioners. The correct answer demonstrates knowledge of proper error handling patterns."
                    }
                ]
            },
            "fill_in_blank": {
                "technical": [
                    {
                        "question": f"In {topic}, the principle of _______ ensures that changes to one component do not unexpectedly affect other components.",
                        "answer": "encapsulation",
                        "alternatives": ["abstraction", "isolation", "modularity"]
                    },
                    {
                        "question": f"When scaling {topic} implementations, _______ is the technique of distributing load across multiple instances.",
                        "answer": "load balancing",
                        "alternatives": ["horizontal scaling", "distribution", "partitioning"]
                    },
                    {
                        "question": f"The _______ pattern in {topic} allows for lazy initialization and controlled access to expensive resources.",
                        "answer": "singleton",
                        "alternatives": ["factory", "proxy", "lazy loading"]
                    },
                    {
                        "question": f"In professional {topic} development, _______ testing verifies that individual components work correctly in isolation.",
                        "answer": "unit",
                        "alternatives": ["component", "module", "isolated"]
                    }
                ]
            },
            "essay": {
                "technical": [
                    {
                        "question": f"You are tasked with migrating a legacy system to use modern {topic} practices. The system has significant technical debt and limited documentation. Describe your approach, including: (1) assessment methodology, (2) migration strategy, (3) risk mitigation, and (4) success metrics.",
                        "rubric": {
                            "assessment_methodology": "25% - Demonstrates systematic approach to understanding existing system",
                            "migration_strategy": "30% - Presents feasible, phased approach with clear milestones",
                            "risk_mitigation": "25% - Identifies key risks and proposes concrete mitigation strategies",
                            "success_metrics": "20% - Defines measurable criteria for migration success"
                        }
                    },
                    {
                        "question": f"Analyze a scenario where two valid approaches to {topic} appear to conflict. Describe: (1) the apparent conflict, (2) underlying principles that explain when each approach is appropriate, (3) a decision framework for choosing between them, and (4) potential hybrid approaches.",
                        "rubric": {
                            "conflict_analysis": "25% - Clearly articulates the apparent conflict and its context",
                            "principles": "25% - Demonstrates deep understanding of underlying concepts",
                            "decision_framework": "25% - Provides practical, applicable framework for decisions",
                            "synthesis": "25% - Shows ability to integrate approaches when appropriate"
                        }
                    }
                ]
            }
        }
        
        difficulty_modifiers = {
            "easy": " Consider a straightforward case where standard conditions apply.",
            "medium": " Assume typical production constraints apply.",
            "hard": " Consider a complex scenario with multiple interacting factors.",
            "expert": " Address edge cases and non-obvious interactions."
        }
        
        if question_type == "mcq":
            template_bank = templates["mcq"]["technical"]
            template = template_bank[index % len(template_bank)]
            
            # Add difficulty modifier to question
            question_text = template["question"] + difficulty_modifiers.get(difficulty, "")
            
            # Prepare options with correct shuffling
            options = [(opt[0].replace("{topic}", topic), opt[1]) for opt in template["options"]]
            correct_text = next(opt[0] for opt in options if opt[1])
            rng.shuffle(options)
            
            return {
                "question_type": "mcq",
                "question_text": question_text.replace("{topic}", topic),
                "question_context": f"This question assesses {difficulty}-level understanding of {topic}.",
                "options": [
                    {"id": chr(65 + i), "text": opt[0], "is_correct": opt[1]}
                    for i, opt in enumerate(options)
                ],
                "concepts": [topic, f"{topic} implementation", f"{topic} analysis"],
                "explanation": template["explanation"].replace("{topic}", topic),
                "difficulty": difficulty,
                "cognitive_level": "analyze" if difficulty in ["hard", "expert"] else "apply",
                "points": 10,
                "time_limit_seconds": 90,
                "source": "academic_template"
            }
        
        elif question_type == "fill_in_blank":
            template_bank = templates["fill_in_blank"]["technical"]
            template = template_bank[index % len(template_bank)]
            
            return {
                "question_type": "fill_in_blank",
                "question_text": template["question"].replace("{topic}", topic) + difficulty_modifiers.get(difficulty, ""),
                "blank_answer": template["answer"],
                "acceptable_answers": [template["answer"]] + template["alternatives"],
                "concepts": [topic],
                "explanation": f"The term '{template['answer']}' is fundamental to professional {topic} practice.",
                "difficulty": difficulty,
                "points": 10,
                "time_limit_seconds": 60,
                "source": "academic_template"
            }
        
        else:  # essay
            template_bank = templates["essay"]["technical"]
            template = template_bank[index % len(template_bank)]
            
            return {
                "question_type": "essay",
                "question_text": template["question"].replace("{topic}", topic),
                "question_context": f"This is a {difficulty}-level analytical question about {topic}.",
                "model_answer": f"A comprehensive response should address all four components specified in the question, demonstrating both theoretical understanding and practical application of {topic} principles.",
                "rubric": template["rubric"],
                "concepts": [topic, f"{topic} analysis", f"{topic} design"],
                "difficulty": difficulty,
                "points": 25,
                "time_limit_seconds": 600,
                "source": "academic_template"
            }
    
    async def evaluate_response(
        self,
        assessment: Dict[str, Any],
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a learner's response
        
        Args:
            assessment: The question that was asked
            response: The learner's response
            context: Session context
            
        Returns:
            Evaluation results
        """
        context = context or {}
        
        try:
            question_type = assessment.get("question_type", "mcq")
            
            if question_type == "mcq":
                return self._evaluate_mcq(assessment, response)
            elif question_type == "fill_in_blank":
                return self._evaluate_fill_in_blank(assessment, response)
            elif question_type == "essay":
                return await self._evaluate_essay(assessment, response, context)
            else:
                return self._default_evaluation(False)
                
        except Exception as e:
            logger.error(f"Response evaluation failed: {e}")
            return self._default_evaluation(False)
    
    def _evaluate_mcq(
        self,
        assessment: Dict[str, Any],
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate MCQ response - checks both option ID and text"""
        
        selected_id = response.get("selected_option_id")
        selected_content = response.get("content", "").strip()
        options = assessment.get("options", [])
        
        # Find correct option
        correct_option = next(
            (opt for opt in options if opt.get("is_correct")),
            None
        )
        
        if not correct_option:
            logger.warning("No correct option found in MCQ assessment")
            return self._default_evaluation(False)
        
        correct_id = correct_option.get("id")
        correct_text = correct_option.get("text", "").strip().lower()
        
        # Check if correct by ID match
        is_correct_by_id = selected_id and selected_id.upper() == correct_id.upper() if correct_id else False
        
        # Check if correct by text match (fallback)
        is_correct_by_text = selected_content.lower() == correct_text if selected_content and correct_text else False
        
        # Also check if the selected_id matches the text of an option (in case frontend sends text as ID)
        is_correct_by_text_as_id = False
        if selected_id:
            matching_opt = next(
                (opt for opt in options if opt.get("text", "").strip().lower() == selected_id.lower()),
                None
            )
            if matching_opt:
                is_correct_by_text_as_id = matching_opt.get("is_correct", False)
        
        is_correct = is_correct_by_id or is_correct_by_text or is_correct_by_text_as_id
        
        logger.info(f"MCQ Evaluation: selected_id={selected_id}, selected_content={selected_content[:50] if selected_content else None}, correct_id={correct_id}, is_correct={is_correct}")
        
        return {
            "is_correct": is_correct,
            "score": assessment.get("points", 10) if is_correct else 0,
            "correct_answer": correct_option.get("text") if correct_option else None,
            "correct_option_id": correct_id,
            "explanation": assessment.get("explanation", ""),
            "conceptual_understanding": 100 if is_correct else 30,
            "misconceptions": [] if is_correct else ["Selected incorrect option"],
            "knowledge_gaps": [] if is_correct else assessment.get("concepts", []),
            "next_steps": ["Continue to next question"] if is_correct else ["Review the concept"],
        }
    
    def _evaluate_fill_in_blank(
        self,
        assessment: Dict[str, Any],
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate fill-in-blank response"""
        
        user_answer = response.get("content", "").strip().lower()
        correct_answer = assessment.get("blank_answer", "").lower()
        acceptable = [a.lower() for a in assessment.get("acceptable_answers", [])]
        
        is_correct = (
            user_answer == correct_answer or
            user_answer in acceptable
        )
        
        # Partial credit for close answers
        partial_score = 0
        if not is_correct:
            # Check for partial match
            if correct_answer in user_answer or user_answer in correct_answer:
                partial_score = assessment.get("points", 10) * 0.5
        
        return {
            "is_correct": is_correct,
            "score": assessment.get("points", 10) if is_correct else partial_score,
            "correct_answer": assessment.get("blank_answer"),
            "explanation": assessment.get("explanation", ""),
            "conceptual_understanding": 100 if is_correct else (50 if partial_score > 0 else 20),
            "misconceptions": [] if is_correct else ["Incorrect term used"],
            "knowledge_gaps": [] if is_correct else assessment.get("concepts", []),
            "next_steps": ["Continue practicing"] if is_correct else ["Review terminology"],
        }
    
    async def _evaluate_essay(
        self,
        assessment: Dict[str, Any],
        response: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate essay response using LLM"""
        
        user_answer = response.get("content", "")
        model_answer = assessment.get("model_answer", "")
        rubric = assessment.get("rubric", {})
        
        if self.llm_client:
            return await self._llm_evaluate_essay(
                user_answer, model_answer, rubric, assessment
            )
        
        # Simple evaluation without LLM
        word_count = len(user_answer.split())
        
        if word_count < 10:
            score = 0
            understanding = 10
        elif word_count < 50:
            score = assessment.get("points", 20) * 0.5
            understanding = 50
        else:
            score = assessment.get("points", 20) * 0.7
            understanding = 70
        
        return {
            "is_correct": score > assessment.get("points", 20) * 0.5,
            "score": score,
            "correct_answer": model_answer,
            "explanation": "Response evaluated based on length and content",
            "conceptual_understanding": understanding,
            "misconceptions": [],
            "knowledge_gaps": [],
            "next_steps": ["Continue developing your explanation skills"],
        }
    
    async def _llm_evaluate_essay(
        self,
        user_answer: str,
        model_answer: str,
        rubric: Dict[str, Any],
        assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to evaluate essay response"""
        
        prompt = f"""Evaluate the following student response against the model answer.

QUESTION: {assessment.get('question_text', '')}

STUDENT RESPONSE:
{user_answer}

MODEL ANSWER:
{model_answer}

RUBRIC CRITERIA:
{rubric}

Evaluate and respond in JSON:
{{
    "score": <0 to {assessment.get('points', 20)}>,
    "conceptual_understanding": <0 to 100>,
    "strengths": ["strength1", "strength2"],
    "misconceptions": ["misconception1"],
    "knowledge_gaps": ["gap1"],
    "feedback": "Detailed feedback",
    "next_steps": ["step1", "step2"]
}}"""
        
        try:
            if hasattr(self.llm_client, 'chat'):
                result = await self.llm_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "You are an expert educational evaluator."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                import json
                data = json.loads(result.choices[0].message.content)
                
                return {
                    "is_correct": data.get("score", 0) > assessment.get("points", 20) * 0.5,
                    "score": data.get("score", 0),
                    "correct_answer": model_answer,
                    "explanation": data.get("feedback", ""),
                    "conceptual_understanding": data.get("conceptual_understanding", 50),
                    "misconceptions": data.get("misconceptions", []),
                    "knowledge_gaps": data.get("knowledge_gaps", []),
                    "next_steps": data.get("next_steps", []),
                }
            
            elif hasattr(self.llm_client, 'generate_content'):
                # Gemini-style client - use sync method in async context
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(
                        f"{prompt}\n\nRespond with valid JSON only."
                    )
                )
                
                import json
                data = json.loads(result.text)
                
                return {
                    "is_correct": data.get("score", 0) > assessment.get("points", 20) * 0.5,
                    "score": data.get("score", 0),
                    "correct_answer": model_answer,
                    "explanation": data.get("feedback", ""),
                    "conceptual_understanding": data.get("conceptual_understanding", 50),
                    "misconceptions": data.get("misconceptions", []),
                    "knowledge_gaps": data.get("knowledge_gaps", []),
                    "next_steps": data.get("next_steps", []),
                }
        
        except Exception as e:
            logger.error(f"LLM essay evaluation failed: {e}")
        
        return self._default_evaluation(False)
    
    def _default_evaluation(self, is_correct: bool) -> Dict[str, Any]:
        """Return default evaluation"""
        return {
            "is_correct": is_correct,
            "score": 10 if is_correct else 0,
            "correct_answer": None,
            "explanation": "",
            "conceptual_understanding": 100 if is_correct else 30,
            "misconceptions": [],
            "knowledge_gaps": [],
            "next_steps": [],
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
