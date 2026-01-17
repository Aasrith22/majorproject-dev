"""
Adaptive Engine Service
Manages difficulty adjustment and personalization logic
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.config import DifficultyLevels
from app.models.learner_profile import LearnerProfile, PerformanceWindow


class AdaptiveEngine:
    """Engine for adaptive difficulty and learning path management"""
    
    # Difficulty progression order
    DIFFICULTY_ORDER = [
        DifficultyLevels.BEGINNER,
        DifficultyLevels.EASY,
        DifficultyLevels.MEDIUM,
        DifficultyLevels.HARD,
        DifficultyLevels.EXPERT,
    ]
    
    # Thresholds for difficulty adjustment
    INCREASE_THRESHOLD = 0.80  # 80% accuracy to increase
    DECREASE_THRESHOLD = 0.50  # Below 50% to decrease
    MIN_QUESTIONS_FOR_ADJUSTMENT = 5
    
    @classmethod
    def calculate_next_difficulty(
        cls,
        current_difficulty: str,
        recent_performances: List[PerformanceWindow],
        force_direction: Optional[str] = None  # "up", "down", or None
    ) -> str:
        """
        Calculate the next appropriate difficulty level
        
        Args:
            current_difficulty: Current difficulty level
            recent_performances: List of recent performance entries
            force_direction: Force difficulty change direction
            
        Returns:
            Recommended difficulty level
        """
        if force_direction == "up":
            return cls._increase_difficulty(current_difficulty)
        elif force_direction == "down":
            return cls._decrease_difficulty(current_difficulty)
        
        # Need minimum questions for auto-adjustment
        if len(recent_performances) < cls.MIN_QUESTIONS_FOR_ADJUSTMENT:
            return current_difficulty
        
        # Calculate recent accuracy
        recent = recent_performances[-cls.MIN_QUESTIONS_FOR_ADJUSTMENT:]
        correct = sum(1 for p in recent if p.is_correct)
        accuracy = correct / len(recent)
        
        # Determine adjustment
        if accuracy >= cls.INCREASE_THRESHOLD:
            return cls._increase_difficulty(current_difficulty)
        elif accuracy < cls.DECREASE_THRESHOLD:
            return cls._decrease_difficulty(current_difficulty)
        
        return current_difficulty
    
    @classmethod
    def _increase_difficulty(cls, current: str) -> str:
        """Increase difficulty by one level"""
        try:
            current_index = cls.DIFFICULTY_ORDER.index(current)
            if current_index < len(cls.DIFFICULTY_ORDER) - 1:
                return cls.DIFFICULTY_ORDER[current_index + 1]
        except ValueError:
            pass
        return current
    
    @classmethod
    def _decrease_difficulty(cls, current: str) -> str:
        """Decrease difficulty by one level"""
        try:
            current_index = cls.DIFFICULTY_ORDER.index(current)
            if current_index > 0:
                return cls.DIFFICULTY_ORDER[current_index - 1]
        except ValueError:
            pass
        return current
    
    @classmethod
    def select_random_difficulty(cls, profile: Optional[LearnerProfile] = None) -> str:
        """
        Select a random difficulty for question generation
        
        Uses weighted random selection based on learner profile
        """
        import random
        
        if not profile:
            # Default weights favor medium difficulty
            weights = {
                DifficultyLevels.BEGINNER: 0.1,
                DifficultyLevels.EASY: 0.2,
                DifficultyLevels.MEDIUM: 0.4,
                DifficultyLevels.HARD: 0.2,
                DifficultyLevels.EXPERT: 0.1,
            }
        else:
            # Adjust weights based on profile
            recent_accuracy = profile.get_recent_accuracy()
            current_idx = cls.DIFFICULTY_ORDER.index(profile.current_difficulty)
            
            weights = {}
            for i, diff in enumerate(cls.DIFFICULTY_ORDER):
                # Base weight - higher for difficulties near current level
                distance = abs(i - current_idx)
                base_weight = max(0.1, 0.5 - (distance * 0.15))
                
                # Adjust based on accuracy
                if recent_accuracy > 70 and i > current_idx:
                    base_weight *= 1.3  # Encourage harder questions
                elif recent_accuracy < 50 and i < current_idx:
                    base_weight *= 1.3  # Encourage easier questions
                
                weights[diff] = base_weight
        
        # Normalize weights
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
        
        # Weighted random selection
        return random.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=1
        )[0]
    
    @classmethod
    def analyze_performance_trend(
        cls,
        performances: List[PerformanceWindow],
        window_size: int = 10
    ) -> str:
        """
        Analyze performance trend
        
        Returns: "improving", "stable", or "declining"
        """
        if len(performances) < window_size * 2:
            return "stable"
        
        # Compare recent vs older performance
        older = performances[-(window_size * 2):-window_size]
        recent = performances[-window_size:]
        
        older_accuracy = sum(1 for p in older if p.is_correct) / len(older)
        recent_accuracy = sum(1 for p in recent if p.is_correct) / len(recent)
        
        difference = recent_accuracy - older_accuracy
        
        if difference > 0.1:
            return "improving"
        elif difference < -0.1:
            return "declining"
        return "stable"
    
    @classmethod
    def identify_weak_concepts(
        cls,
        profile: LearnerProfile,
        threshold: float = 0.6
    ) -> List[str]:
        """Identify concepts where the learner is struggling"""
        weak_concepts = []
        
        for concept, mastery in profile.concept_mastery.items():
            if mastery.mastery_level < threshold * 100:
                weak_concepts.append(concept)
        
        return weak_concepts
    
    @classmethod
    def identify_strong_concepts(
        cls,
        profile: LearnerProfile,
        threshold: float = 0.8
    ) -> List[str]:
        """Identify concepts where the learner excels"""
        strong_concepts = []
        
        for concept, mastery in profile.concept_mastery.items():
            if mastery.mastery_level >= threshold * 100:
                strong_concepts.append(concept)
        
        return strong_concepts
    
    @classmethod
    def recommend_next_topic(
        cls,
        profile: LearnerProfile,
        available_topics: List[str]
    ) -> Optional[str]:
        """
        Recommend the next topic to study based on:
        1. Knowledge gaps
        2. Weakness areas
        3. Topics not recently studied
        """
        if not available_topics:
            return None
        
        scored_topics = []
        
        for topic in available_topics:
            score = 0.5  # Base score
            
            # Boost for knowledge gaps
            if topic.lower() in [g.lower() for g in profile.knowledge_gaps]:
                score += 0.3
            
            # Boost for weaknesses
            if topic.lower() in [w.lower() for w in profile.weaknesses]:
                score += 0.2
            
            # Check if recently studied
            for progress in profile.topic_progress:
                if progress.topic_name.lower() == topic.lower():
                    if progress.last_studied:
                        days_since = (datetime.utcnow() - progress.last_studied).days
                        if days_since > 7:
                            score += 0.1  # Boost for not recently studied
                        elif days_since < 1:
                            score -= 0.2  # Reduce if studied today
                    break
            
            scored_topics.append((topic, score))
        
        # Sort by score and return top recommendation
        scored_topics.sort(key=lambda x: x[1], reverse=True)
        return scored_topics[0][0] if scored_topics else None
    
    @classmethod
    def calculate_mastery_level(
        cls,
        questions_attempted: int,
        questions_correct: int,
        difficulty_weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate mastery level as a percentage
        
        Uses weighted accuracy based on difficulty
        """
        if questions_attempted == 0:
            return 0.0
        
        base_accuracy = (questions_correct / questions_attempted) * 100
        
        # Could apply difficulty weighting here if we track
        # which difficulties the correct answers were at
        
        return min(100.0, base_accuracy)
    
    @classmethod
    def generate_learning_path(
        cls,
        profile: LearnerProfile,
        target_topic: str,
        max_steps: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate a recommended learning path for a topic
        """
        path = []
        
        # Start with prerequisites if there are knowledge gaps
        for gap in profile.knowledge_gaps[:3]:
            path.append({
                "step": len(path) + 1,
                "type": "prerequisite",
                "topic": gap,
                "reason": f"Building foundation: {gap}",
                "difficulty": DifficultyLevels.EASY,
            })
        
        # Add main topic at appropriate difficulty
        path.append({
            "step": len(path) + 1,
            "type": "main",
            "topic": target_topic,
            "reason": "Main topic focus",
            "difficulty": profile.current_difficulty,
        })
        
        # Add practice at higher difficulty
        if profile.get_recent_accuracy() > 70:
            path.append({
                "step": len(path) + 1,
                "type": "challenge",
                "topic": target_topic,
                "reason": "Challenge yourself",
                "difficulty": cls._increase_difficulty(profile.current_difficulty),
            })
        
        # Add review for weak areas
        for weakness in profile.weaknesses[:2]:
            path.append({
                "step": len(path) + 1,
                "type": "review",
                "topic": weakness,
                "reason": f"Strengthen weak area: {weakness}",
                "difficulty": DifficultyLevels.MEDIUM,
            })
        
        return path[:max_steps]
