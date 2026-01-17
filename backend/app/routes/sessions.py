"""
Learning Sessions Routes
Handles session creation, management, and input processing
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List, Optional
from loguru import logger

from app.models.user import User
from app.models.session import (
    LearningSession, 
    SessionCreate, 
    SessionInput, 
    SessionResponse,
    SessionSummary,
    SessionStatus,
    SessionInteraction
)
from app.models.learner_profile import LearnerProfile
from app.routes.auth import get_or_create_guest_user
from app.services.preprocessing import PreprocessingService
from app.agents.crew import EduSynapseCrew


router = APIRouter()


def session_to_response(session: LearningSession) -> SessionResponse:
    """Convert session to response schema"""
    return SessionResponse(
        id=str(session.id),
        user_id=session.user_id,
        topic_name=session.topic_name,
        is_custom_topic=session.is_custom_topic,
        status=session.status.value,
        current_difficulty=session.current_difficulty,
        questions_answered=session.questions_answered,
        correct_answers=session.correct_answers,
        accuracy=session.accuracy,
        total_score=session.total_score,
        started_at=session.started_at,
        last_activity_at=session.last_activity_at,
    )


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Start a new learning session"""
    
    # Get user's learner profile for initial difficulty
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    initial_difficulty = profile.current_difficulty if profile else "medium"
    
    # Create session
    session = LearningSession(
        user_id=str(current_user.id),
        topic_id=session_data.topic_id,
        topic_name=session_data.topic_name,
        is_custom_topic=session_data.is_custom_topic,
        custom_query=session_data.custom_query,
        target_questions=session_data.target_questions,
        assessment_types=session_data.assessment_types,
        current_difficulty=initial_difficulty,
        session_context={
            "user_preferences": current_user.preferences.model_dump(),
            "initial_difficulty": initial_difficulty,
            "focus_topics": profile.current_focus_topics if profile else [],
            "known_weaknesses": profile.weaknesses if profile else [],
        }
    )
    await session.insert()
    
    # Update user statistics
    current_user.total_sessions += 1
    await current_user.save()
    
    logger.info(f"Session started: {session.id} for user {current_user.email}")
    
    return session_to_response(session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Get session details"""
    
    session = await LearningSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    return session_to_response(session)


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    status: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_or_create_guest_user)
):
    """List user's learning sessions"""
    
    query = LearningSession.find(LearningSession.user_id == str(current_user.id))
    
    if status:
        query = query.find(LearningSession.status == status)
    
    sessions = await query.sort(-LearningSession.started_at).limit(limit).to_list()
    
    return [session_to_response(s) for s in sessions]


@router.post("/{session_id}/input")
async def submit_input(
    session_id: str,
    input_data: SessionInput,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Submit learner input to a session and trigger agent orchestration"""
    
    # Get session
    session = await LearningSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Preprocess input based on modality
    preprocessing_service = PreprocessingService()
    processed_content = await preprocessing_service.process_input(
        input_type=input_data.input_type,
        content=input_data.content,
        metadata=input_data.metadata
    )
    
    # Create interaction record
    interaction = SessionInteraction(
        input_type=input_data.input_type,
        input_content=input_data.content,
        processed_content=processed_content,
    )
    
    # Get learner profile for context
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    # Package context for CrewAI
    context_package = {
        "session_id": session_id,
        "user_id": str(current_user.id),
        "current_input": processed_content,
        "input_modality": input_data.input_type,
        "topic": session.topic_name,
        "is_custom_topic": session.is_custom_topic,
        "custom_query": session.custom_query,
        "session_history": [i.model_dump() for i in session.interactions[-5:]],  # Last 5 interactions
        "learner_profile": {
            "current_difficulty": profile.current_difficulty if profile else "medium",
            "strengths": profile.strengths if profile else [],
            "weaknesses": profile.weaknesses if profile else [],
            "knowledge_gaps": profile.knowledge_gaps if profile else [],
            "recent_accuracy": profile.get_recent_accuracy() if profile else 0,
        }
    }
    
    # Trigger CrewAI orchestration
    crew = EduSynapseCrew()
    agent_result = await crew.execute(
        user_input=processed_content,
        user_id=str(current_user.id),
        session_id=session_id,
        modality=input_data.input_type,
        context=context_package
    )
    
    # Update interaction with agent outputs
    interaction.agent_outputs = agent_result
    
    # Update session
    session.interactions.append(interaction)
    session.last_activity_at = datetime.utcnow()
    session.last_agent_output = agent_result
    session.session_context.update({"last_interaction": interaction.model_dump()})
    await session.save()
    
    logger.info(f"Input processed for session {session_id}")
    
    return {
        "success": True,
        "processed_input": processed_content,
        "agent_result": agent_result
    }


@router.post("/{session_id}/pause")
async def pause_session(
    session_id: str,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Pause an active session"""
    
    session = await LearningSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    session.status = SessionStatus.PAUSED
    session.last_activity_at = datetime.utcnow()
    await session.save()
    
    return {"success": True, "message": "Session paused"}


@router.post("/{session_id}/resume")
async def resume_session(
    session_id: str,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Resume a paused session"""
    
    session = await LearningSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if session.status != SessionStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Session is not paused")
    
    session.status = SessionStatus.ACTIVE
    session.last_activity_at = datetime.utcnow()
    await session.save()
    
    return {"success": True, "message": "Session resumed"}


@router.post("/{session_id}/end", response_model=SessionSummary)
async def end_session(
    session_id: str,
    current_user: User = Depends(get_or_create_guest_user)
):
    """End a session and get summary"""
    
    session = await LearningSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate duration
    duration_seconds = int((datetime.utcnow() - session.started_at).total_seconds())
    
    # Update session
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.utcnow()
    session.total_duration_seconds = duration_seconds
    await session.save()
    
    # Update user statistics
    current_user.total_study_time_minutes += duration_seconds // 60
    await current_user.save()
    
    # Update learner profile
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    if profile:
        profile.total_study_time_minutes += duration_seconds // 60
        profile.last_activity_at = datetime.utcnow()
        
        # Save custom topic to profile if this was a custom topic session
        if session.is_custom_topic and session.custom_query:
            # Get subject area from session context (set during question generation)
            subject_area = session.session_context.get("detected_subject", "General")
            
            # Check if topic already exists in custom_topics
            existing_topic = next(
                (t for t in profile.custom_topics if t.get("name", "").lower() == session.custom_query.lower()),
                None
            )
            
            if existing_topic:
                # Update existing topic stats
                existing_topic["sessions_completed"] = existing_topic.get("sessions_completed", 0) + 1
                existing_topic["last_studied"] = datetime.utcnow().isoformat()
                existing_topic["total_questions"] = existing_topic.get("total_questions", 0) + session.questions_answered
                existing_topic["correct_answers"] = existing_topic.get("correct_answers", 0) + session.correct_answers
                if subject_area and subject_area != "General":
                    existing_topic["subject"] = subject_area
            else:
                # Add new custom topic with detected subject
                profile.custom_topics.append({
                    "id": session.topic_name.lower().replace(" ", "-"),
                    "name": session.custom_query or session.topic_name,
                    "subject": subject_area,
                    "description": f"{subject_area}: {session.custom_query or session.topic_name}",
                    "sessions_completed": 1,
                    "total_questions": session.questions_answered,
                    "correct_answers": session.correct_answers,
                    "last_studied": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                })
        
        await profile.save()
    
    # Generate session summary using Feedback Agent
    crew = EduSynapseCrew()
    summary_result = await crew.generate_session_summary(session_id)
    
    # Update learner profile with session analytics for adaptive baseline
    if profile and summary_result:
        # Update profile strengths/weaknesses from session analysis
        session_strengths = summary_result.get("strengths", [])
        session_weaknesses = summary_result.get("weaknesses", [])
        mastered = summary_result.get("mastered_concepts", [])
        improvement_areas = summary_result.get("improvement_areas", [])
        
        # Add new strengths
        for strength in session_strengths:
            if strength and strength not in profile.strengths:
                profile.strengths.append(strength)
        
        # Add new weaknesses/improvement areas
        for weakness in session_weaknesses + improvement_areas:
            if weakness and weakness not in profile.weaknesses:
                profile.weaknesses.append(weakness)
        
        # Update mastery - remove mastered concepts from knowledge gaps
        for concept in mastered:
            if concept in profile.knowledge_gaps:
                profile.knowledge_gaps.remove(concept)
            if concept not in profile.strengths:
                profile.strengths.append(concept)
        
        # Store last session performance for adaptive starting point
        profile.last_session_performance = {
            "accuracy": session.accuracy,
            "difficulty_reached": session.current_difficulty,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await profile.save()
    
    logger.info(f"Session ended: {session_id}")
    
    return SessionSummary(
        session_id=session_id,
        topic_name=session.topic_name,
        duration_minutes=duration_seconds // 60,
        questions_answered=session.questions_answered,
        correct_answers=session.correct_answers,
        accuracy=session.accuracy,
        average_score=session.average_score,
        difficulty_progression=summary_result.get("difficulty_progression", []),
        strengths=summary_result.get("strengths", []),
        weaknesses=summary_result.get("weaknesses", []),
        recommendations=summary_result.get("recommendations", []),
        # Enhanced analytics
        learning_metrics=summary_result.get("learning_metrics"),
        difficulty_analysis=summary_result.get("difficulty_analysis"),
        performance_rating=summary_result.get("performance_rating"),
        improvement_areas=summary_result.get("improvement_areas"),
        mastered_concepts=summary_result.get("mastered_concepts"),
    )
