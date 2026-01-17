"""
Dashboard Routes
Handles progress tracking and analytics
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger

from app.models.user import User
from app.models.session import LearningSession, SessionStatus
from app.models.assessment import AssessmentResponse
from app.models.feedback import Feedback
from app.models.learner_profile import LearnerProfile, LearnerProfileResponse, ProgressAnalytics
from app.routes.auth import get_or_create_guest_user


router = APIRouter()


@router.get("/progress", response_model=LearnerProfileResponse)
async def get_progress(current_user: User = Depends(get_or_create_guest_user)):
    """Get learner's overall progress"""
    
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    if not profile:
        # Create profile if it doesn't exist
        profile = LearnerProfile(user_id=str(current_user.id))
        await profile.insert()
    
    # Get current focus topics from recent sessions
    recent_sessions = await LearningSession.find(
        LearningSession.user_id == str(current_user.id)
    ).sort(-LearningSession.last_activity_at).limit(10).to_list()
    
    # Extract unique topics being studied
    current_focus_topics = list(set([
        s.topic_name for s in recent_sessions 
        if s.topic_name and s.status in [SessionStatus.ACTIVE, SessionStatus.COMPLETED]
    ]))[:5]  # Limit to 5 topics
    
    # Update profile with current focus topics
    if current_focus_topics and current_focus_topics != profile.current_focus_topics:
        profile.current_focus_topics = current_focus_topics
        await profile.save()
    
    return LearnerProfileResponse(
        user_id=profile.user_id,
        current_difficulty=profile.current_difficulty,
        current_focus_topics=current_focus_topics or profile.current_focus_topics,
        overall_mastery=profile.overall_mastery,
        accuracy=profile.accuracy,
        total_questions_attempted=profile.total_questions_attempted,
        total_study_time_minutes=profile.total_study_time_minutes,
        strengths=profile.strengths,
        weaknesses=profile.weaknesses,
        knowledge_gaps=profile.knowledge_gaps,
        current_streak_days=profile.current_streak_days,
        achievements=profile.achievements,
    )


@router.get("/analytics")
async def get_analytics(
    period: str = "weekly",  # daily, weekly, monthly
    current_user: User = Depends(get_or_create_guest_user)
):
    """Get detailed learning analytics"""
    
    # Determine date range
    now = datetime.utcnow()
    if period == "daily":
        start_date = now - timedelta(days=1)
    elif period == "weekly":
        start_date = now - timedelta(weeks=1)
    elif period == "monthly":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(weeks=1)
    
    # Get sessions in period
    sessions = await LearningSession.find(
        LearningSession.user_id == str(current_user.id),
        LearningSession.started_at >= start_date
    ).to_list()
    
    # Get responses in period
    responses = await AssessmentResponse.find(
        AssessmentResponse.user_id == str(current_user.id),
        AssessmentResponse.submitted_at >= start_date
    ).to_list()
    
    # Calculate metrics
    total_questions = len(responses)
    correct_answers = sum(1 for r in responses if r.is_correct)
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    total_score = sum(r.score for r in responses)
    average_score = (total_score / total_questions) if total_questions > 0 else 0
    
    # Calculate study time
    total_study_time = sum(s.total_duration_seconds for s in sessions if s.total_duration_seconds)
    
    # Difficulty distribution
    difficulty_distribution = {}
    for r in responses:
        # Get assessment to find difficulty
        from app.models.assessment import Assessment
        assessment = await Assessment.get(r.assessment_id)
        if assessment:
            diff = assessment.difficulty
            difficulty_distribution[diff] = difficulty_distribution.get(diff, 0) + 1
    
    # Topic breakdown
    topic_stats = {}
    for s in sessions:
        topic = s.topic_name
        if topic not in topic_stats:
            topic_stats[topic] = {
                "topic": topic,
                "sessions": 0,
                "questions": 0,
                "correct": 0,
                "time_minutes": 0
            }
        topic_stats[topic]["sessions"] += 1
        topic_stats[topic]["questions"] += s.questions_answered
        topic_stats[topic]["correct"] += s.correct_answers
        topic_stats[topic]["time_minutes"] += (s.total_duration_seconds or 0) // 60
    
    # Calculate accuracy trends (group by day)
    accuracy_trend = []
    responses_by_day = {}
    for r in responses:
        day = r.submitted_at.date().isoformat()
        if day not in responses_by_day:
            responses_by_day[day] = {"total": 0, "correct": 0}
        responses_by_day[day]["total"] += 1
        if r.is_correct:
            responses_by_day[day]["correct"] += 1
    
    for day, stats in sorted(responses_by_day.items()):
        accuracy_trend.append({
            "date": day,
            "accuracy": (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0,
            "questions": stats["total"]
        })
    
    # Get learner profile for comparison
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    # Calculate improvement
    previous_accuracy = profile.get_recent_accuracy(20) if profile else 0
    current_accuracy = profile.get_recent_accuracy(10) if profile else 0
    improvement = current_accuracy - previous_accuracy
    
    return ProgressAnalytics(
        user_id=str(current_user.id),
        period=period,
        questions_attempted=total_questions,
        questions_correct=correct_answers,
        accuracy=accuracy,
        average_score=average_score,
        total_study_time_minutes=total_study_time // 60 if total_study_time else 0,
        sessions_completed=len([s for s in sessions if s.status == SessionStatus.COMPLETED]),
        difficulty_distribution=difficulty_distribution,
        topics_studied=list(topic_stats.values()),
        accuracy_trend=accuracy_trend,
        mastery_trend=[],  # Would need historical data
        improvement_percentage=improvement,
    ).model_dump() | {
        # Add performance history for charts
        "performance_history": [
            {
                "date": day,
                "score": (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0,
                "correctAnswers": stats["correct"],
                "questionsAttempted": stats["total"],
                "timeSpent": sum((s.total_duration_seconds or 0) // 60 for s in sessions if s.started_at.date().isoformat() == day)
            }
            for day, stats in sorted(responses_by_day.items())
        ],
        # Add concept mastery from topic stats
        "concept_mastery": [
            {
                "concept": topic_data["topic"],
                "mastery": (topic_data["correct"] / topic_data["questions"] * 100) if topic_data["questions"] > 0 else 0,
                "trend": "improving" if topic_data["correct"] / max(topic_data["questions"], 1) > 0.7 else "stable" if topic_data["correct"] / max(topic_data["questions"], 1) > 0.4 else "declining"
            }
            for topic_data in topic_stats.values()
            if topic_data["questions"] > 0
        ]
    }


@router.get("/recommendations")
async def get_recommendations(current_user: User = Depends(get_or_create_guest_user)):
    """Get personalized learning recommendations"""
    
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    recommendations = []
    
    if profile:
        # Recommend based on weaknesses
        for weakness in profile.weaknesses[:3]:
            recommendations.append({
                "type": "focus_area",
                "priority": 1,
                "title": f"Practice {weakness}",
                "description": f"You've been struggling with {weakness}. Focused practice will help.",
                "action": "start_session",
                "action_data": {"topic": weakness}
            })
        
        # Recommend based on knowledge gaps
        for gap in profile.knowledge_gaps[:2]:
            recommendations.append({
                "type": "knowledge_gap",
                "priority": 2,
                "title": f"Fill the gap: {gap}",
                "description": f"Understanding {gap} will strengthen your foundation.",
                "action": "start_session",
                "action_data": {"topic": gap}
            })
        
        # Difficulty recommendation
        recent_accuracy = profile.get_recent_accuracy()
        if recent_accuracy > 80:
            recommendations.append({
                "type": "difficulty",
                "priority": 3,
                "title": "Ready for a challenge!",
                "description": "Your recent performance is excellent. Try harder questions.",
                "action": "increase_difficulty",
                "action_data": {}
            })
        elif recent_accuracy < 50:
            recommendations.append({
                "type": "difficulty",
                "priority": 3,
                "title": "Build your foundation",
                "description": "Let's strengthen your basics with easier questions.",
                "action": "decrease_difficulty",
                "action_data": {}
            })
        
        # Streak recommendation
        if profile.current_streak_days > 0:
            recommendations.append({
                "type": "streak",
                "priority": 4,
                "title": f"Keep your {profile.current_streak_days}-day streak!",
                "description": "You're doing great! Don't break your learning streak.",
                "action": "continue_learning",
                "action_data": {}
            })
    
    # Default recommendation if no profile data
    if not recommendations:
        recommendations.append({
            "type": "start",
            "priority": 1,
            "title": "Start your learning journey",
            "description": "Begin with any topic that interests you!",
            "action": "start_session",
            "action_data": {}
        })
    
    return {
        "user_id": str(current_user.id),
        "recommendations": sorted(recommendations, key=lambda x: x["priority"]),
        "generated_at": datetime.utcnow()
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Get recent learning activity"""
    
    # Get recent sessions
    sessions = await LearningSession.find(
        LearningSession.user_id == str(current_user.id)
    ).sort(-LearningSession.last_activity_at).limit(limit).to_list()
    
    activities = []
    for session in sessions:
        activities.append({
            "type": "session",
            "session_id": str(session.id),
            "topic": session.topic_name,
            "status": session.status.value,
            "questions_answered": session.questions_answered,
            "accuracy": session.accuracy,
            "timestamp": session.last_activity_at
        })
    
    return {
        "user_id": str(current_user.id),
        "activities": activities
    }


@router.get("/achievements")
async def get_achievements(current_user: User = Depends(get_or_create_guest_user)):
    """Get user achievements and badges"""
    
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    # Define all possible achievements
    all_achievements = [
        {"id": "first_question", "name": "First Step", "description": "Answer your first question", "icon": "🎯"},
        {"id": "ten_questions", "name": "Getting Started", "description": "Answer 10 questions", "icon": "📚"},
        {"id": "hundred_questions", "name": "Dedicated Learner", "description": "Answer 100 questions", "icon": "🏆"},
        {"id": "first_streak", "name": "Consistency Beginner", "description": "Achieve a 3-day streak", "icon": "🔥"},
        {"id": "week_streak", "name": "Week Warrior", "description": "Achieve a 7-day streak", "icon": "⚡"},
        {"id": "perfect_session", "name": "Perfectionist", "description": "Get 100% in a session", "icon": "💯"},
        {"id": "hard_master", "name": "Challenge Accepted", "description": "Complete a hard difficulty session", "icon": "💪"},
        {"id": "hour_study", "name": "Hour Power", "description": "Study for 1 hour total", "icon": "⏱️"},
        {"id": "multi_topic", "name": "Explorer", "description": "Study 5 different topics", "icon": "🗺️"},
    ]
    
    # Check which achievements the user has
    earned = profile.achievements if profile else []
    
    achievements = []
    for achievement in all_achievements:
        achievements.append({
            **achievement,
            "earned": achievement["id"] in earned,
            "earned_at": None  # Would need to track this
        })
    
    return {
        "user_id": str(current_user.id),
        "total_earned": len(earned),
        "total_available": len(all_achievements),
        "achievements": achievements
    }


@router.get("/topic-mastery")
async def get_topic_mastery(current_user: User = Depends(get_or_create_guest_user)):
    """Get mastery levels for all studied topics"""
    
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    if not profile:
        return {"topics": []}
    
    topics = []
    for progress in profile.topic_progress:
        topics.append({
            "topic_id": progress.topic_id,
            "topic_name": progress.topic_name,
            "mastery_level": progress.overall_mastery,
            "sessions_completed": progress.sessions_completed,
            "total_time_minutes": progress.total_time_minutes,
            "last_studied": progress.last_studied,
            "concepts": [
                {
                    "name": c.concept,
                    "mastery": c.mastery_level,
                    "trend": c.trend
                }
                for c in progress.concepts
            ]
        })
    
    return {
        "user_id": str(current_user.id),
        "overall_mastery": profile.overall_mastery,
        "topics": sorted(topics, key=lambda x: x["mastery_level"], reverse=True)
    }


@router.get("/available-topics")
async def get_available_topics(current_user: User = Depends(get_or_create_guest_user)):
    """Get all available topics from the knowledge base plus user's custom topics"""
    from app.models.knowledge import KnowledgeChunk
    
    try:
        # Get distinct topics from knowledge base
        chunks = await KnowledgeChunk.find_all().to_list()
        
        # Group by topic
        topic_map = {}
        for chunk in chunks:
            topic = chunk.topic
            if topic not in topic_map:
                topic_map[topic] = {
                    "id": topic.lower().replace(" ", "-"),
                    "name": topic,
                    "subject": chunk.subject,
                    "description": f"Learn about {topic}",
                    "difficulty_levels": set(),
                    "content_count": 0,
                    "subtopics": set(),
                }
            topic_map[topic]["difficulty_levels"].add(chunk.difficulty)
            topic_map[topic]["content_count"] += 1
            topic_map[topic]["subtopics"].update(chunk.subtopics)
        
        # Convert sets to lists for JSON serialization
        topics = []
        for topic, data in topic_map.items():
            data["difficulty_levels"] = list(data["difficulty_levels"])
            data["subtopics"] = list(data["subtopics"])[:5]  # Limit subtopics
            data["is_custom"] = False
            topics.append(data)
        
        # Sort by content count (most content first)
        topics = sorted(topics, key=lambda x: x["content_count"], reverse=True)
        
        # Add user's custom topics
        profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
        if profile and profile.custom_topics:
            for custom_topic in profile.custom_topics:
                # Don't duplicate if it already exists in predefined topics
                if not any(t["name"].lower() == custom_topic["name"].lower() for t in topics):
                    topics.append({
                        "id": custom_topic.get("id", custom_topic["name"].lower().replace(" ", "-")),
                        "name": custom_topic["name"],
                        "subject": "Custom",
                        "description": custom_topic.get("description", f"Custom topic: {custom_topic['name']}"),
                        "difficulty_levels": ["easy", "medium", "hard"],
                        "content_count": 0,
                        "subtopics": [],
                        "is_custom": True,
                        "sessions_completed": custom_topic.get("sessions_completed", 0),
                        "last_studied": custom_topic.get("last_studied"),
                    })
        
        return {
            "topics": topics,
            "total": len(topics),
        }
        
    except Exception as e:
        logger.error(f"Failed to get available topics: {e}")
        return {"topics": [], "total": 0}
