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
                # Use LLM to generate all questions at once
                questions = await self._llm_generate_batch_questions(
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
    
    async def _llm_generate_batch_questions(
        self,
        content_chunks: List[Dict[str, Any]],
        topic: str,
        count: int,
        preferred_type: str,
        learner_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate multiple questions using LLM in a single call"""
        
        # Combine content from multiple chunks
        combined_content = "\n\n".join([
            c.get("content", "") for c in content_chunks[:5]
        ])[:3000]  # Limit content length
        
        # Build adaptive learning context
        weakness_note = ""
        weaknesses = learner_profile.get("weaknesses", [])
        if weaknesses:
            weakness_note = f"The learner struggles with: {', '.join(weaknesses[:3])}. Include questions that help address these weaknesses."
        
        # Check for previous attempts and weak concepts
        previous_attempts = context.get("previous_attempts", {})
        adaptive_note = ""
        if previous_attempts.get("should_focus_weaknesses"):
            weak_concepts = previous_attempts.get("weak_concepts", [])
            attempt_count = previous_attempts.get("count", 0)
            if weak_concepts:
                adaptive_note = f"""
ADAPTIVE LEARNING CONTEXT:
This learner has attempted this topic {attempt_count} time(s) before.
They have struggled with these concepts in previous attempts: {', '.join(weak_concepts[:5])}
IMPORTANT: Generate questions that specifically target and help reinforce understanding of these weak areas.
Approximately {min(count // 2 + 1, count)} questions should focus on these weak concepts."""
        
        type_instructions = {
            "mcq": """For each MCQ question, include 4 options (A, B, C, D) where exactly one is correct.
Include plausible distractors based on common misconceptions.""",
            "fill_in_blank": """For each fill-in-the-blank question, include the correct answer and acceptable alternatives.""",
            "essay": """For each essay question, include a model answer outline and rubric criteria.""",
        }
        
        # Generate a random seed for variation
        import time
        random_seed = int(time.time() * 1000) % 10000
        
        # Randomly select question styles for variety
        question_styles = [
            "definition and explanation",
            "comparison between concepts", 
            "practical application scenario",
            "problem-solving",
            "cause and effect analysis",
            "identifying characteristics",
            "real-world example",
            "troubleshooting scenario",
            "best practices",
            "conceptual understanding"
        ]
        selected_styles = random.sample(question_styles, min(count, len(question_styles)))
        style_note = f"Use these question styles for variety: {', '.join(selected_styles)}"
        
        # Get previously asked questions to avoid repetition
        previously_asked = context.get("previous_attempts", {}).get("previously_asked_questions", [])
        avoid_note = ""
        if previously_asked:
            # Only include a few example questions to avoid, keep prompt manageable
            sample_questions = previously_asked[:10] if len(previously_asked) > 10 else previously_asked
            avoid_note = f"""
DO NOT REPEAT THESE PREVIOUSLY ASKED QUESTIONS (generate completely different questions):
{chr(10).join(f'- "{q[:100]}..."' if len(q) > 100 else f'- "{q}"' for q in sample_questions)}
"""
        
        prompt = f"""Generate {count} unique educational assessment questions about "{topic}".

RANDOMIZATION SEED: {random_seed} (use this to ensure unique questions each time)

CRITICAL REQUIREMENTS:
1. ALL questions MUST be directly and specifically about "{topic}" - no unrelated topics
2. Questions should cover DIFFERENT aspects, subtopics, and angles within "{topic}"
3. Vary the difficulty: mix of easy ({count // 3 + 1}), medium ({count // 3 + 1}), and hard ({count - 2 * (count // 3 + 1)}) questions
4. Make each question COMPLETELY UNIQUE - different wording, different concepts, different scenarios
5. {style_note}
6. Use creative and varied phrasing - avoid repetitive question structures
7. Include specific examples, scenarios, or context where appropriate
{avoid_note}
{adaptive_note}

TOPIC: {topic}
QUESTION TYPE: {preferred_type}

REFERENCE CONTENT:
{combined_content if combined_content else f'General educational content about {topic}'}

{type_instructions.get(preferred_type, type_instructions['mcq'])}

{weakness_note}

DIVERSITY GUIDELINES:
- Each question should test a different concept or subtopic within {topic}
- Vary the cognitive level: some recall, some application, some analysis
- Use different question formats: "What is...", "Which of the following...", "In a scenario where...", "Why does...", "How would you..."
- Include both theoretical and practical questions

Respond with a JSON object containing a "questions" array with exactly {count} questions:
{{
    "questions": [
        {{
            "question_text": "Question about {topic}",
            "question_context": "Optional context",
            "difficulty": "easy|medium|hard",
            "options": [  // For MCQ
                {{"id": "A", "text": "Option A", "is_correct": false}},
                {{"id": "B", "text": "Option B", "is_correct": true}},
                {{"id": "C", "text": "Option C", "is_correct": false}},
                {{"id": "D", "text": "Option D", "is_correct": false}}
            ],
            "blank_answer": "answer",  // For fill_in_blank
            "acceptable_answers": ["answer1", "answer2"],
            "model_answer": "Full answer",  // For essay
            "rubric": {{}},
            "concepts": ["concept1"],
            "explanation": "Why this is correct",
            "points": 10,
            "time_limit_seconds": 60,
            "targets_weakness": true|false  // Whether this targets a known weak area
        }}
    ]
}}

Ensure all {count} questions are unique and progressively cover different aspects of "{topic}"."""

        try:
            if hasattr(self.llm_client, 'chat'):
                logger.info(f"[QuestionGen] Using OpenAI for batch generation")
                response = await self.llm_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": self.backstory},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return self._parse_batch_questions(
                    response.choices[0].message.content,
                    preferred_type,
                    topic,
                    count
                )
            
            elif hasattr(self.llm_client, 'generate_content'):
                logger.info(f"[QuestionGen] Using Gemini for batch generation")
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(
                        f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
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
        
        # Fallback to generating individually
        logger.warning(f"[QuestionGen] Falling back to individual generation")
        questions = []
        for i in range(count):
            difficulties = ["easy", "medium", "medium", "hard", "medium"]
            content = content_chunks[i % len(content_chunks)].get("content", "") if content_chunks else ""
            question = self._rule_based_generate_question(
                content=content,
                question_type=preferred_type,
                difficulty=difficulties[i % len(difficulties)],
                topic=topic
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
                    "difficulty": q.get("difficulty", "medium"),
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
        """Generate question using LLM"""
        
        prompt = self._build_generation_prompt(
            content, question_type, difficulty, topic, context
        )
        
        try:
            if hasattr(self.llm_client, 'chat'):
                logger.info(f"[QuestionGen] Using OpenAI-style client")
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
                logger.info(f"[QuestionGen] Using Gemini client to generate question")
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(
                        f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
                    )
                )
                logger.info(f"[QuestionGen] Gemini response received: {response.text[:200] if response and response.text else 'None'}")
                return self._parse_generated_question(
                    response.text,
                    question_type,
                    difficulty,
                    topic
                )
            else:
                logger.warning(f"[QuestionGen] Unknown LLM client type: {type(self.llm_client)}")
        
        except Exception as e:
            logger.error(f"[QuestionGen] LLM question generation failed: {e}", exc_info=True)
        
        logger.warning(f"[QuestionGen] Falling back to rule-based generation")
        return self._rule_based_generate_question(content, question_type, difficulty, topic)
    
    def _build_generation_prompt(
        self,
        content: str,
        question_type: str,
        difficulty: str,
        topic: str,
        context: Dict[str, Any]
    ) -> str:
        """Build the prompt for question generation"""
        
        import time
        random_seed = int(time.time() * 1000) % 10000
        
        type_instructions = {
            "mcq": """Generate a multiple-choice question with 4 options (A, B, C, D).
One option must be correct. Include plausible distractors based on common misconceptions.""",
            "fill_in_blank": """Generate a fill-in-the-blank question.
The blank should test understanding of a key concept. Provide the correct answer and acceptable alternatives.""",
            "essay": """Generate an open-ended essay question.
Provide a model answer and rubric criteria for evaluation.""",
        }
        
        difficulty_guidance = {
            "easy": "Focus on recall and basic understanding. Use straightforward language.",
            "medium": "Require application of concepts. Include some complexity.",
            "hard": "Require analysis and evaluation. Include nuanced scenarios.",
        }
        
        # Randomly select a question style for variety
        question_styles = [
            "Ask about a definition or core concept",
            "Present a practical scenario or use case",
            "Compare two related concepts",
            "Ask about best practices or common patterns",
            "Present a problem-solving scenario",
            "Ask about advantages or disadvantages",
            "Test understanding of a process or workflow",
            "Ask about real-world applications",
        ]
        selected_style = random.choice(question_styles)
        
        learner_weaknesses = context.get("learner_profile", {}).get("weaknesses", [])
        weakness_note = f"The learner struggles with: {', '.join(learner_weaknesses)}" if learner_weaknesses else ""
        
        prompt = f"""Generate an educational assessment question based on the following:

RANDOMIZATION SEED: {random_seed} (use this for variety)

CRITICAL: The question MUST be about "{topic}". Do NOT generate questions about other topics.

TOPIC (REQUIRED): {topic}
QUESTION TYPE: {question_type}
DIFFICULTY: {difficulty}
QUESTION STYLE: {selected_style}

REFERENCE CONTENT (for context only):
{content[:1500] if content else f'General educational content about {topic}'}

TYPE INSTRUCTIONS:
{type_instructions.get(question_type, type_instructions['mcq'])}

DIFFICULTY GUIDANCE:
{difficulty_guidance.get(difficulty, difficulty_guidance['medium'])}

{weakness_note}

IMPORTANT RULES:
1. The question MUST be directly related to "{topic}"
2. Use the specified QUESTION STYLE to guide the question format
3. Make the question unique and interesting - avoid generic phrasing
4. Do NOT generate questions about unrelated topics
5. Use the reference content as inspiration but ensure the question is about "{topic}"
6. Make the question educationally valuable and appropriate for the difficulty level

Respond in JSON format with:
{{
    "question_text": "The question text (MUST be about {topic})",
    "question_context": "Optional additional context for the question",
    "options": [  // For MCQ only
        {{"id": "A", "text": "Option A", "is_correct": false}},
        {{"id": "B", "text": "Option B", "is_correct": true}},
        ...
    ],
    "blank_answer": "Correct answer",  // For fill_in_blank
    "acceptable_answers": ["answer1", "answer2"],  // Variations
    "model_answer": "Full model answer",  // For essay
    "rubric": {{"criteria": "description"}},  // For essay
    "concepts": ["concept1", "concept2"],
    "explanation": "Why this is the correct answer",
    "points": 10,
    "time_limit_seconds": 60
}}"""
        
        return prompt
    
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
        difficulty: str,
        topic: str
    ) -> Dict[str, Any]:
        """Generate question using rules when LLM unavailable - creates unique questions based on content"""
        
        # Extract key concepts from content for more relevant questions
        content_words = content.lower().split() if content else []
        # Filter to meaningful words (longer than 3 chars, not common words)
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'this', 'that', 'with', 'have', 'from', 'they', 'been', 'has', 'were', 'said', 'each', 'which', 'their', 'will', 'way', 'about', 'many', 'then', 'them', 'these', 'some', 'would', 'make', 'like', 'into', 'time', 'very', 'when', 'come', 'made', 'find', 'more', 'long', 'him', 'how', 'its', 'may', 'did', 'get', 'than', 'now', 'what', 'over', 'such', 'use'}
        key_concepts = [w for w in content_words if len(w) > 4 and w not in common_words][:10]
        
        import random
        import hashlib
        
        # Create deterministic but unique seed based on topic and content
        seed_str = f"{topic}_{content[:100] if content else 'default'}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        
        if question_type == "mcq":
            # Generate varied MCQ questions based on topic
            mcq_templates = [
                (f"What is the primary purpose of {topic}?",
                 [f"To provide a structured approach to understanding {topic}", 
                  "To replace all existing methods", 
                  "It has no specific purpose", 
                  "To complicate simple processes"]),
                (f"Which statement about {topic} is most accurate?",
                 [f"{topic} is essential for building foundational knowledge",
                  f"{topic} is rarely used in practice",
                  f"{topic} has been completely replaced by newer concepts",
                  f"{topic} is only theoretical with no applications"]),
                (f"In the context of {topic}, what is considered a best practice?",
                 ["Understanding core principles before advanced topics",
                  "Skipping foundational concepts",
                  "Memorizing without understanding",
                  "Avoiding practical applications"]),
                (f"How does {topic} relate to problem-solving?",
                 [f"{topic} provides frameworks for systematic problem-solving",
                  f"{topic} is unrelated to problem-solving",
                  f"{topic} makes problems more complex",
                  f"{topic} should be avoided when solving problems"]),
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
                "difficulty": difficulty,
                "concepts": [topic] + key_concepts[:3],
                "points": 10,
                "time_limit_seconds": 60,
            }
        
        elif question_type == "fill_in_blank":
            fill_templates = [
                (f"A key principle in {topic} is the concept of _______.", topic),
                (f"When working with {topic}, it's important to first understand the _______.", "fundamentals"),
                (f"The main goal of studying {topic} is to develop _______ skills.", "analytical"),
                (f"In {topic}, _______ is considered essential for mastery.", "practice"),
            ]
            
            template = rng.choice(fill_templates)
            
            return {
                "question_type": "fill_in_blank",
                "question_text": template[0],
                "blank_answer": template[1],
                "acceptable_answers": [template[1].lower(), template[1].upper(), template[1].capitalize()],
                "difficulty": difficulty,
                "concepts": [topic],
                "points": 10,
                "time_limit_seconds": 45,
            }
        
        else:  # essay
            essay_templates = [
                f"Explain the key concepts of {topic} and describe how they can be applied in a real-world scenario.",
                f"Discuss the importance of {topic} in your field of study. Provide specific examples.",
                f"Compare and contrast different approaches to understanding {topic}. What are the advantages of each?",
                f"Describe a situation where knowledge of {topic} would be essential. Explain your reasoning.",
            ]
            
            question = rng.choice(essay_templates)
            
            return {
                "question_type": "essay",
                "question_text": question,
                "model_answer": f"A comprehensive answer about {topic} should include: 1) Clear explanation of core concepts, 2) Relevant examples and applications, 3) Critical analysis of the topic's importance.",
                "rubric": {
                    "understanding": "Demonstrates clear understanding of core concepts",
                    "application": "Provides relevant real-world examples",
                    "analysis": "Shows critical thinking and analysis",
                    "clarity": "Well-organized and clearly expressed",
                },
                "difficulty": difficulty,
                "concepts": [topic] + key_concepts[:2],
                "points": 20,
                "time_limit_seconds": 300,
            }
    
    def _fallback_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback question when all else fails - still topic-aware"""
        topic = context.get("topic", "the subject")
        question_type = context.get("preferred_type", "mcq")
        difficulty = context.get("current_difficulty", "medium")
        
        # Use rule-based generation which now creates varied questions
        return self._rule_based_generate_question(
            content=f"Educational content about {topic}",
            question_type=question_type,
            difficulty=difficulty,
            topic=topic
        )
    
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
                        prompt,
                        generation_config={"response_mime_type": "application/json"}
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
