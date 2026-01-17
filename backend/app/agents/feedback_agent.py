"""
Feedback Agent
Final agent in the pipeline - generates personalized learning guidance
"""

from typing import Dict, Any, Optional, List
from loguru import logger
import asyncio

from app.config import settings


class FeedbackAgent:
    """
    Agent responsible for generating personalized feedback
    
    Responsibilities:
    - Identify strengths and weaknesses
    - Generate actionable feedback
    - Suggest focused improvement areas
    - Recommend next learning actions
    - Analyze knowledge gaps and learning patterns
    - Provide performance metrics and analytics
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the Feedback Agent
        
        Args:
            llm_client: LLM client for feedback generation
        """
        self.llm_client = llm_client
        self.name = "Feedback Agent"
        self.role = "Personalized Learning Coach"
        self.goal = "Provide motivating, actionable feedback that accelerates learning"
        self.backstory = """You are an experienced educational coach who has helped thousands
        of students achieve their learning goals. You excel at providing constructive feedback
        that is encouraging yet honest. You understand the psychology of learning and know
        how to motivate students while addressing their weaknesses. You always provide
        specific, actionable recommendations."""
    
    async def generate_feedback(
        self,
        evaluation_result: Dict[str, Any],
        query_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized feedback based on evaluation
        
        Args:
            evaluation_result: Output from Question Generation Agent (evaluation phase)
            query_analysis: Output from Query Analysis Agent
            context: Session context
            
        Returns:
            Comprehensive feedback
        """
        context = context or {}
        
        try:
            # Extract key information
            is_correct = evaluation_result.get("is_correct", False)
            score = evaluation_result.get("score", 0)
            misconceptions = evaluation_result.get("misconceptions", [])
            knowledge_gaps = evaluation_result.get("knowledge_gaps", [])
            learner_profile = context.get("learner_profile", {})
            
            # Generate feedback using LLM or rules
            if self.llm_client:
                feedback = await self._llm_generate_feedback(
                    evaluation_result,
                    query_analysis,
                    context
                )
            else:
                feedback = self._rule_based_feedback(
                    evaluation_result,
                    query_analysis,
                    context
                )
            
            # Add encouragement based on performance
            feedback["encouragement_message"] = self._generate_encouragement(
                is_correct,
                learner_profile.get("recent_accuracy", 50),
                learner_profile.get("current_streak_days", 0)
            )
            
            # Calculate overall performance score
            feedback["overall_performance_score"] = self._calculate_performance_score(
                score,
                evaluation_result.get("conceptual_understanding", 50),
                len(misconceptions)
            )
            
            # Determine improvement trend
            feedback["improvement_trend"] = self._determine_trend(
                learner_profile.get("performance_window", [])
            )
            
            # Add advanced analytics
            feedback["analytics"] = self._generate_analytics(
                evaluation_result,
                learner_profile,
                context
            )
            
            return feedback
            
        except Exception as e:
            logger.error(f"Feedback generation failed: {e}")
            return self._default_feedback(context)
    
    def _generate_analytics(
        self,
        evaluation_result: Dict[str, Any],
        learner_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate advanced analytics for the feedback"""
        
        performance_window = learner_profile.get("performance_window", [])
        
        # Knowledge gap analysis
        knowledge_gap_analysis = self._analyze_knowledge_gaps(
            evaluation_result.get("knowledge_gaps", []),
            learner_profile.get("knowledge_gaps", [])
        )
        
        # Learning velocity calculation
        learning_velocity = self._calculate_learning_velocity(performance_window)
        
        # Difficulty appropriateness
        difficulty_analysis = self._analyze_difficulty_fit(
            evaluation_result.get("score", 0),
            evaluation_result.get("difficulty", "medium"),
            performance_window
        )
        
        # Concept mastery estimation
        concept_mastery = self._estimate_concept_mastery(
            evaluation_result,
            learner_profile
        )
        
        return {
            "knowledge_gap_analysis": knowledge_gap_analysis,
            "learning_velocity": learning_velocity,
            "difficulty_analysis": difficulty_analysis,
            "concept_mastery": concept_mastery,
            "retention_score": self._calculate_retention_score(performance_window),
            "engagement_level": self._estimate_engagement_level(context),
        }
    
    def _analyze_knowledge_gaps(
        self,
        current_gaps: List[str],
        historical_gaps: List[str]
    ) -> Dict[str, Any]:
        """Analyze knowledge gaps and their persistence"""
        
        # Find recurring gaps
        from collections import Counter
        all_gaps = current_gaps + historical_gaps
        gap_frequency = Counter(all_gaps)
        
        recurring_gaps = [gap for gap, count in gap_frequency.items() if count > 1]
        new_gaps = [gap for gap in current_gaps if gap not in historical_gaps]
        
        # Priority score for gaps (higher = needs more attention)
        gap_priorities = {
            gap: min(count * 20, 100)
            for gap, count in gap_frequency.items()
        }
        
        return {
            "total_gaps": len(set(all_gaps)),
            "recurring_gaps": recurring_gaps,
            "new_gaps": new_gaps,
            "gap_priorities": gap_priorities,
            "severity": "high" if len(recurring_gaps) > 2 else ("medium" if recurring_gaps else "low"),
        }
    
    def _calculate_learning_velocity(
        self,
        performance_window: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate how quickly the learner is improving"""
        
        if len(performance_window) < 5:
            return {
                "velocity": 0,
                "trend": "insufficient_data",
                "confidence": 0.3,
            }
        
        # Calculate improvement rate
        recent = performance_window[-5:]
        older = performance_window[-10:-5] if len(performance_window) >= 10 else performance_window[:-5]
        
        recent_correct = sum(1 for p in recent if p.get("is_correct", False)) / len(recent) * 100
        older_correct = sum(1 for p in older if p.get("is_correct", False)) / len(older) * 100 if older else 50
        
        velocity = recent_correct - older_correct
        
        # Determine trend
        if velocity > 10:
            trend = "accelerating"
        elif velocity > 0:
            trend = "improving"
        elif velocity > -10:
            trend = "stable"
        else:
            trend = "declining"
        
        return {
            "velocity": round(velocity, 2),
            "trend": trend,
            "recent_accuracy": round(recent_correct, 2),
            "confidence": min(len(performance_window) / 20, 1.0),
        }
    
    def _analyze_difficulty_fit(
        self,
        score: float,
        current_difficulty: str,
        performance_window: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze if the current difficulty level is appropriate"""
        
        difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
        current_level = difficulty_map.get(current_difficulty, 2)
        
        # Analyze recent performance at this difficulty
        same_difficulty = [
            p for p in performance_window[-10:]
            if p.get("difficulty") == current_difficulty
        ]
        
        if same_difficulty:
            avg_score = sum(p.get("score", 0) for p in same_difficulty) / len(same_difficulty)
            success_rate = sum(1 for p in same_difficulty if p.get("is_correct", False)) / len(same_difficulty) * 100
        else:
            avg_score = score
            success_rate = 100 if score > 5 else 0
        
        # Determine recommendation
        if success_rate > 80 and current_difficulty != "hard":
            recommendation = "increase"
            reason = "High success rate indicates readiness for more challenging content"
        elif success_rate < 40 and current_difficulty != "easy":
            recommendation = "decrease"
            reason = "Lower success rate suggests need for more foundational practice"
        else:
            recommendation = "maintain"
            reason = "Current difficulty level is appropriate for your performance"
        
        return {
            "current_difficulty": current_difficulty,
            "success_rate_at_level": round(success_rate, 2),
            "recommendation": recommendation,
            "reason": reason,
            "optimal_difficulty": "hard" if success_rate > 80 else ("easy" if success_rate < 40 else "medium"),
        }
    
    def _estimate_concept_mastery(
        self,
        evaluation_result: Dict[str, Any],
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate mastery level for concepts covered"""
        
        concepts = evaluation_result.get("concepts", [])
        conceptual_understanding = evaluation_result.get("conceptual_understanding", 50)
        is_correct = evaluation_result.get("is_correct", False)
        
        # Base mastery from this question
        base_mastery = conceptual_understanding
        
        # Adjust based on correctness
        if is_correct:
            base_mastery = min(100, base_mastery + 10)
        else:
            base_mastery = max(0, base_mastery - 10)
        
        concept_mastery = {}
        for concept in concepts:
            # Check if this is a known weakness
            if concept in learner_profile.get("weaknesses", []):
                mastery = base_mastery * 0.8  # Lower mastery for known weaknesses
            elif concept in learner_profile.get("strengths", []):
                mastery = min(100, base_mastery * 1.2)  # Higher for strengths
            else:
                mastery = base_mastery
            
            concept_mastery[concept] = {
                "mastery_level": round(mastery, 2),
                "status": "mastered" if mastery >= 80 else ("developing" if mastery >= 50 else "needs_work"),
            }
        
        return concept_mastery
    
    def _calculate_retention_score(
        self,
        performance_window: List[Dict[str, Any]]
    ) -> float:
        """Calculate how well the learner retains knowledge over time"""
        
        if len(performance_window) < 10:
            return 70.0  # Default score
        
        # Look for patterns where the learner answered similar topics
        from collections import defaultdict
        topic_performance = defaultdict(list)
        
        for p in performance_window:
            topic = p.get("topic", "unknown")
            topic_performance[topic].append(p.get("is_correct", False))
        
        # Calculate retention (consistency in performance over time)
        retention_scores = []
        for topic, results in topic_performance.items():
            if len(results) >= 2:
                # Check if performance improved or maintained
                early = sum(results[:len(results)//2]) / (len(results)//2) if results[:len(results)//2] else 0
                late = sum(results[len(results)//2:]) / (len(results) - len(results)//2) if results[len(results)//2:] else 0
                retention_scores.append(max(late - early + 0.5, 0) * 100)
        
        return round(sum(retention_scores) / len(retention_scores), 2) if retention_scores else 70.0
    
    def _estimate_engagement_level(
        self,
        context: Dict[str, Any]
    ) -> str:
        """Estimate learner engagement based on context"""
        
        # Check response time if available
        time_taken = context.get("time_taken_seconds", 0)
        expected_time = context.get("expected_time_seconds", 60)
        
        if time_taken > 0:
            if time_taken < expected_time * 0.3:
                return "low"  # Too fast, might be guessing
            elif time_taken > expected_time * 2:
                return "struggling"  # Taking too long
            else:
                return "high"  # Good engagement
        
        return "moderate"
    
    async def _llm_generate_feedback(
        self,
        evaluation_result: Dict[str, Any],
        query_analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate feedback using LLM"""
        
        prompt = self._build_feedback_prompt(evaluation_result, query_analysis, context)
        
        try:
            if hasattr(self.llm_client, 'chat'):
                response = await self.llm_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": self.backstory},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return self._parse_feedback_response(response.choices[0].message.content)
            
            elif hasattr(self.llm_client, 'generate_content'):
                # Gemini-style client - use sync method in async context
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.llm_client.generate_content(
                        f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
                    )
                )
                return self._parse_feedback_response(response.text)
        
        except Exception as e:
            logger.error(f"LLM feedback generation failed: {e}")
        
        return self._rule_based_feedback(evaluation_result, query_analysis, context)
    
    def _build_feedback_prompt(
        self,
        evaluation_result: Dict[str, Any],
        query_analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for feedback generation"""
        
        learner_profile = context.get("learner_profile", {})
        
        prompt = f"""Generate personalized learning feedback based on the following:

EVALUATION RESULT:
- Correct: {evaluation_result.get('is_correct')}
- Score: {evaluation_result.get('score')}/{evaluation_result.get('max_score', 10)}
- Conceptual Understanding: {evaluation_result.get('conceptual_understanding')}%
- Misconceptions: {evaluation_result.get('misconceptions', [])}
- Knowledge Gaps: {evaluation_result.get('knowledge_gaps', [])}

LEARNER CONTEXT:
- Topic: {query_analysis.get('topic', {}).get('main', 'Unknown')}
- Current Strengths: {learner_profile.get('strengths', [])}
- Current Weaknesses: {learner_profile.get('weaknesses', [])}
- Recent Accuracy: {learner_profile.get('recent_accuracy', 'Unknown')}%
- Learning Streak: {learner_profile.get('current_streak_days', 0)} days

Generate comprehensive feedback in JSON format:
{{
    "summary": "Brief 1-2 sentence summary of performance",
    "detailed_feedback": "Detailed explanation of what was done well and areas for improvement",
    "strengths": [
        {{"concept": "concept name", "proficiency_level": 0-100, "evidence": ["evidence1"]}}
    ],
    "weaknesses": [
        {{"concept": "concept name", "current_level": 0-100, "target_level": 80, "improvement_suggestions": ["suggestion1"]}}
    ],
    "recommendations": [
        {{"priority": 1, "action": "specific action", "reason": "why this helps", "estimated_time_minutes": 15}}
    ],
    "suggested_topics": ["topic1", "topic2"],
    "suggested_difficulty": "easy|medium|hard"
}}

Be encouraging but honest. Focus on growth and specific actions."""

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
    
    def _parse_feedback_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into feedback format"""
        import json
        
        try:
            cleaned_response = self._extract_json_from_response(response)
            data = json.loads(cleaned_response)
            
            return {
                "summary": data.get("summary", ""),
                "detailed_feedback": data.get("detailed_feedback", ""),
                "strengths": [
                    {
                        "concept": s.get("concept", ""),
                        "proficiency_level": s.get("proficiency_level", 50),
                        "evidence": s.get("evidence", [])
                    }
                    for s in data.get("strengths", [])
                ],
                "weaknesses": [
                    {
                        "concept": w.get("concept", ""),
                        "current_level": w.get("current_level", 30),
                        "target_level": w.get("target_level", 80),
                        "improvement_suggestions": w.get("improvement_suggestions", [])
                    }
                    for w in data.get("weaknesses", [])
                ],
                "recommendations": [
                    {
                        "priority": r.get("priority", 1),
                        "action": r.get("action", ""),
                        "reason": r.get("reason", ""),
                        "resources": r.get("resources", []),
                        "estimated_time_minutes": r.get("estimated_time_minutes")
                    }
                    for r in data.get("recommendations", [])
                ],
                "suggested_topics": data.get("suggested_topics", []),
                "suggested_difficulty": data.get("suggested_difficulty", "medium"),
            }
            
        except json.JSONDecodeError:
            logger.error("Failed to parse feedback JSON")
            return self._default_feedback({})
    
    def _rule_based_feedback(
        self,
        evaluation_result: Dict[str, Any],
        query_analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate feedback using rules when LLM unavailable"""
        
        is_correct = evaluation_result.get("is_correct", False)
        score = evaluation_result.get("score", 0)
        max_score = evaluation_result.get("max_score", 10)
        misconceptions = evaluation_result.get("misconceptions", [])
        knowledge_gaps = evaluation_result.get("knowledge_gaps", [])
        topic = query_analysis.get("topic", {}).get("main", "this topic")
        
        # Generate summary
        if is_correct:
            summary = f"Excellent work! You demonstrated a solid understanding of {topic}."
        elif score > max_score * 0.5:
            summary = f"Good effort! You're on the right track with {topic}, but there's room for improvement."
        else:
            summary = f"Keep practicing! Understanding {topic} takes time, and you're making progress."
        
        # Generate detailed feedback
        if is_correct:
            detailed = f"""Great job getting this question correct! Your understanding of {topic} 
            is developing well. To continue improving, try tackling more challenging questions 
            on this topic."""
        else:
            detailed = f"""This question was challenging, but don't be discouraged. 
            Review the core concepts of {topic} and pay attention to the explanation provided. 
            Practice similar questions to reinforce your understanding."""
        
        # Build strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if is_correct:
            strengths.append({
                "concept": topic,
                "proficiency_level": 70,
                "evidence": ["Correctly answered assessment question"]
            })
        else:
            weaknesses.append({
                "concept": topic,
                "current_level": 40,
                "target_level": 80,
                "improvement_suggestions": [
                    "Review fundamental concepts",
                    "Practice with simpler examples first",
                    "Focus on understanding the 'why' behind concepts"
                ]
            })
        
        # Add misconception-based weaknesses
        for misconception in misconceptions:
            weaknesses.append({
                "concept": misconception,
                "current_level": 30,
                "target_level": 70,
                "improvement_suggestions": [f"Address misconception: {misconception}"]
            })
        
        # Build recommendations
        recommendations = []
        
        if knowledge_gaps:
            recommendations.append({
                "priority": 1,
                "action": f"Review: {', '.join(knowledge_gaps[:2])}",
                "reason": "These concepts need more attention",
                "resources": [],
                "estimated_time_minutes": 15
            })
        
        recommendations.append({
            "priority": 2,
            "action": "Practice more questions on this topic",
            "reason": "Regular practice reinforces learning",
            "resources": [],
            "estimated_time_minutes": 20
        })
        
        # Suggested difficulty
        learner_accuracy = context.get("learner_profile", {}).get("recent_accuracy", 50)
        if learner_accuracy > 80:
            suggested_difficulty = "hard"
        elif learner_accuracy > 50:
            suggested_difficulty = "medium"
        else:
            suggested_difficulty = "easy"
        
        return {
            "summary": summary,
            "detailed_feedback": detailed,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "suggested_topics": knowledge_gaps[:3] if knowledge_gaps else [topic],
            "suggested_difficulty": suggested_difficulty,
        }
    
    def _generate_encouragement(
        self,
        is_correct: bool,
        recent_accuracy: float,
        streak_days: int
    ) -> str:
        """Generate encouraging message based on performance"""
        
        messages = []
        
        if is_correct:
            messages = [
                "You're doing great! Keep up the excellent work! 🌟",
                "Fantastic! Your hard work is paying off! 💪",
                "Brilliant answer! You're making real progress! 🎯",
                "Perfect! You've got this concept down! ✨",
            ]
        elif recent_accuracy > 70:
            messages = [
                "Don't worry about this one - you're doing well overall! 📈",
                "Everyone makes mistakes - your overall progress is impressive! 💫",
                "This is how we learn! Your accuracy is still great! 🌱",
            ]
        else:
            messages = [
                "Learning takes time - you're on the right path! 🛤️",
                "Every question is a learning opportunity! Keep going! 🚀",
                "Progress isn't always linear - stay committed! 💪",
                "You're building a strong foundation! Keep practicing! 🏗️",
            ]
        
        # Add streak bonus
        if streak_days >= 7:
            messages.append(f"Amazing! You're on a {streak_days}-day streak! 🔥")
        elif streak_days >= 3:
            messages.append(f"Great consistency! {streak_days} days in a row! ⚡")
        
        import random
        return random.choice(messages)
    
    def _calculate_performance_score(
        self,
        score: float,
        conceptual_understanding: float,
        num_misconceptions: int
    ) -> float:
        """Calculate overall performance score (0-100)"""
        
        # Weight different factors
        score_weight = 0.5
        understanding_weight = 0.4
        misconception_penalty = 0.1
        
        # Normalize score to 0-100
        normalized_score = min(100, (score / 10) * 100)
        
        # Calculate weighted score
        performance = (
            normalized_score * score_weight +
            conceptual_understanding * understanding_weight -
            (num_misconceptions * 10) * misconception_penalty
        )
        
        return max(0, min(100, performance))
    
    def _determine_trend(
        self,
        performance_window: List[Dict[str, Any]]
    ) -> str:
        """Determine performance trend"""
        
        if len(performance_window) < 5:
            return "stable"
        
        # Compare recent vs older performance
        older = performance_window[-10:-5] if len(performance_window) >= 10 else performance_window[:len(performance_window)//2]
        recent = performance_window[-5:]
        
        if not older or not recent:
            return "stable"
        
        older_correct = sum(1 for p in older if p.get("is_correct", False)) / len(older)
        recent_correct = sum(1 for p in recent if p.get("is_correct", False)) / len(recent)
        
        difference = recent_correct - older_correct
        
        if difference > 0.15:
            return "improving"
        elif difference < -0.15:
            return "declining"
        return "stable"
    
    def _default_feedback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Return default feedback"""
        return {
            "summary": "Keep learning and practicing!",
            "detailed_feedback": "Continue working through questions to build your understanding.",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [{
                "priority": 1,
                "action": "Continue practicing",
                "reason": "Regular practice builds mastery",
                "resources": [],
                "estimated_time_minutes": 15
            }],
            "suggested_topics": [],
            "suggested_difficulty": "medium",
            "encouragement_message": "You're making progress! Keep going! 💪",
            "overall_performance_score": 50,
            "improvement_trend": "stable",
        }
    
    async def generate_session_summary(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive summary feedback for an entire session"""
        
        questions_answered = session_data.get("questions_answered", 0)
        correct_answers = session_data.get("correct_answers", 0)
        accuracy = (correct_answers / questions_answered * 100) if questions_answered > 0 else 0
        
        # Analyze difficulty progression
        interactions = session_data.get("interactions", [])
        difficulty_progression = []
        topic_performance = {}
        concept_scores = {}
        time_per_question = []
        
        for interaction in interactions:
            agent_outputs = interaction.get("agent_outputs", {})
            
            # Track difficulty
            if agent_outputs.get("difficulty"):
                difficulty_progression.append(agent_outputs["difficulty"])
            
            # Track performance by concept
            concepts = agent_outputs.get("concepts", [])
            is_correct = interaction.get("is_correct", False)
            score = interaction.get("score", 0)
            
            for concept in concepts:
                if concept not in concept_scores:
                    concept_scores[concept] = {"correct": 0, "total": 0, "scores": []}
                concept_scores[concept]["total"] += 1
                concept_scores[concept]["scores"].append(score)
                if is_correct:
                    concept_scores[concept]["correct"] += 1
            
            # Track time (if available)
            time_taken = interaction.get("time_taken_seconds", 0)
            if time_taken > 0:
                time_per_question.append(time_taken)
        
        # Identify strengths and weaknesses from concept scores
        strengths = []
        weaknesses = []
        
        for concept, data in concept_scores.items():
            concept_accuracy = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            
            concept_data = {
                "concept": concept,
                "accuracy": round(concept_accuracy, 1),
                "questions_attempted": data["total"],
                "average_score": round(avg_score, 1),
            }
            
            if concept_accuracy >= 70:
                strengths.append(concept_data)
            else:
                weaknesses.append(concept_data)
        
        # Sort by accuracy
        strengths.sort(key=lambda x: x["accuracy"], reverse=True)
        weaknesses.sort(key=lambda x: x["accuracy"])
        
        # Analyze difficulty trend
        difficulty_analysis = self._analyze_session_difficulty(difficulty_progression, accuracy)
        
        # Calculate learning metrics
        learning_metrics = {
            "questions_answered": questions_answered,
            "correct_answers": correct_answers,
            "accuracy": round(accuracy, 1),
            "avg_time_per_question": round(sum(time_per_question) / len(time_per_question), 1) if time_per_question else 0,
            "difficulty_range": {
                "min": min(difficulty_progression) if difficulty_progression else "medium",
                "max": max(difficulty_progression) if difficulty_progression else "medium",
            },
            "consistency_score": self._calculate_consistency_score(interactions),
        }
        
        # Generate personalized recommendations
        recommendations = self._generate_session_recommendations(
            accuracy,
            strengths,
            weaknesses,
            difficulty_analysis
        )
        
        # Performance rating
        performance_rating = self._calculate_session_rating(accuracy, difficulty_progression, consistency=learning_metrics["consistency_score"])
        
        return {
            "learning_metrics": learning_metrics,
            "difficulty_progression": difficulty_progression,
            "difficulty_analysis": difficulty_analysis,
            "strengths": strengths[:5],  # Top 5
            "weaknesses": weaknesses[:5],  # Top 5
            "recommendations": recommendations,
            "performance_rating": performance_rating,
            "improvement_areas": [w["concept"] for w in weaknesses[:3]],
            "mastered_concepts": [s["concept"] for s in strengths if s["accuracy"] >= 90],
        }
    
    def _analyze_session_difficulty(
        self,
        difficulty_progression: List[str],
        accuracy: float
    ) -> Dict[str, Any]:
        """Analyze difficulty progression throughout the session"""
        
        if not difficulty_progression:
            return {
                "pattern": "unknown",
                "recommendation": "Continue practicing",
            }
        
        difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
        numeric_progression = [difficulty_map.get(d, 2) for d in difficulty_progression]
        
        # Calculate trend
        if len(numeric_progression) >= 2:
            first_half = sum(numeric_progression[:len(numeric_progression)//2]) / (len(numeric_progression)//2)
            second_half = sum(numeric_progression[len(numeric_progression)//2:]) / (len(numeric_progression) - len(numeric_progression)//2)
            trend = second_half - first_half
        else:
            trend = 0
        
        if trend > 0.5:
            pattern = "increasing"
            recommendation = "Great progress! You're handling increasingly difficult questions."
        elif trend < -0.5:
            pattern = "decreasing"
            recommendation = "Consider reviewing fundamentals to build a stronger foundation."
        else:
            pattern = "stable"
            recommendation = "Consistent difficulty level. Try challenging yourself with harder questions."
        
        return {
            "pattern": pattern,
            "average_difficulty": round(sum(numeric_progression) / len(numeric_progression), 2),
            "trend": round(trend, 2),
            "recommendation": recommendation,
        }
    
    def _calculate_consistency_score(
        self,
        interactions: List[Dict[str, Any]]
    ) -> float:
        """Calculate how consistent the learner's performance was"""
        
        if len(interactions) < 2:
            return 100.0
        
        scores = [i.get("score", 0) for i in interactions]
        if not scores:
            return 100.0
        
        # Calculate variance
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to consistency score (lower std_dev = higher consistency)
        # Assuming scores are 0-10, max std_dev would be about 5
        consistency = max(0, 100 - (std_dev / 5 * 100))
        return round(consistency, 1)
    
    def _generate_session_recommendations(
        self,
        accuracy: float,
        strengths: List[Dict[str, Any]],
        weaknesses: List[Dict[str, Any]],
        difficulty_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on session performance"""
        
        recommendations = []
        
        # Accuracy-based recommendations
        if accuracy < 40:
            recommendations.append({
                "priority": 1,
                "type": "review",
                "title": "Review Fundamentals",
                "description": "Focus on understanding the basic concepts before moving to more complex topics.",
                "action": "Start with easier questions and build up gradually",
            })
        elif accuracy < 60:
            recommendations.append({
                "priority": 1,
                "type": "practice",
                "title": "Targeted Practice",
                "description": "You're making progress! Focus on your weak areas for faster improvement.",
                "action": "Practice more questions on your weak concepts",
            })
        elif accuracy < 80:
            recommendations.append({
                "priority": 2,
                "type": "challenge",
                "title": "Push Your Limits",
                "description": "You're doing well! Try harder questions to continue growing.",
                "action": "Increase difficulty level in your next session",
            })
        else:
            recommendations.append({
                "priority": 3,
                "type": "explore",
                "title": "Explore New Topics",
                "description": "Excellent performance! Consider exploring related advanced topics.",
                "action": "Try a new or more advanced topic",
            })
        
        # Weakness-based recommendations
        if weaknesses:
            weak_concepts = [w["concept"] for w in weaknesses[:2]]
            recommendations.append({
                "priority": 1,
                "type": "focus",
                "title": "Focus Areas",
                "description": f"These concepts need more attention: {', '.join(weak_concepts)}",
                "action": f"Study and practice: {', '.join(weak_concepts)}",
            })
        
        # Difficulty-based recommendations
        if difficulty_analysis.get("pattern") == "decreasing":
            recommendations.append({
                "priority": 2,
                "type": "foundation",
                "title": "Strengthen Foundation",
                "description": "Building a strong foundation will help with harder questions later.",
                "action": "Review prerequisite concepts",
            })
        
        return sorted(recommendations, key=lambda x: x["priority"])
    
    def _calculate_session_rating(
        self,
        accuracy: float,
        difficulty_progression: List[str],
        consistency: float
    ) -> Dict[str, Any]:
        """Calculate an overall session rating"""
        
        # Base score from accuracy
        base_score = accuracy * 0.5
        
        # Bonus for harder difficulties
        difficulty_map = {"easy": 0, "medium": 1, "hard": 2}
        avg_difficulty = sum(difficulty_map.get(d, 1) for d in difficulty_progression) / len(difficulty_progression) if difficulty_progression else 1
        difficulty_bonus = avg_difficulty * 10
        
        # Consistency bonus
        consistency_bonus = consistency * 0.2
        
        total_score = min(100, base_score + difficulty_bonus + consistency_bonus)
        
        # Determine rating
        if total_score >= 90:
            rating = "Excellent"
            stars = 5
        elif total_score >= 75:
            rating = "Great"
            stars = 4
        elif total_score >= 60:
            rating = "Good"
            stars = 3
        elif total_score >= 40:
            rating = "Fair"
            stars = 2
        else:
            rating = "Needs Improvement"
            stars = 1
        
        return {
            "score": round(total_score, 1),
            "rating": rating,
            "stars": stars,
            "breakdown": {
                "accuracy_contribution": round(base_score, 1),
                "difficulty_bonus": round(difficulty_bonus, 1),
                "consistency_bonus": round(consistency_bonus, 1),
            }
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
