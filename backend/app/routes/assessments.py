"""
Assessment Routes
Handles question generation and answer evaluation
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import Optional
from loguru import logger

from app.models.user import User
from app.models.session import LearningSession, SessionStatus
from app.models.assessment import (
    Assessment,
    AssessmentResponse,
    QuestionRequest,
    BatchQuestionRequest,
    QuestionResponse,
    AnswerSubmission,
    AnswerEvaluation,
)
from app.models.feedback import Feedback, FeedbackResponse
from app.models.learner_profile import LearnerProfile
from app.routes.auth import get_or_create_guest_user
from app.agents.crew import EduSynapseCrew


router = APIRouter()


@router.post("/question", response_model=QuestionResponse)
async def get_next_question(
    request: QuestionRequest,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Get the next adaptive question for the session"""
    
    # Get session
    session = await LearningSession.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Get learner profile for adaptive difficulty
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    # Prepare context for Question Generation Agent
    context = {
        "session_id": request.session_id,
        "user_id": str(current_user.id),
        "topic": session.topic_name,
        "is_custom_topic": session.is_custom_topic,
        "custom_query": session.custom_query,
        "current_difficulty": session.current_difficulty,
        "questions_answered": session.questions_answered,
        "session_accuracy": session.accuracy,
        "preferred_type": request.preferred_type,
        "preferred_difficulty": request.preferred_difficulty,
        "learner_profile": {
            "strengths": profile.strengths if profile else [],
            "weaknesses": profile.weaknesses if profile else [],
            "knowledge_gaps": profile.knowledge_gaps if profile else [],
            "recent_accuracy": profile.get_recent_accuracy() if profile else 0,
        }
    }
    
    # Trigger agent orchestration for question generation
    logger.info(f"[Assessments] Creating EduSynapseCrew for question generation, topic: {session.topic_name}")
    crew = EduSynapseCrew()
    logger.info(f"[Assessments] Calling crew.generate_question with context")
    question_result = await crew.generate_question(context)
    logger.info(f"[Assessments] Question result received: {question_result.get('question_text', '')[:100]}")
    
    # Create or get assessment from result
    assessment = Assessment(
        topic_id=session.topic_id,
        topic_name=session.topic_name,
        question_type=question_result.get("question_type", "mcq"),
        question_text=question_result.get("question_text", ""),
        question_context=question_result.get("context"),
        options=question_result.get("options"),
        blank_answer=question_result.get("blank_answer"),
        acceptable_answers=question_result.get("acceptable_answers"),
        model_answer=question_result.get("model_answer"),
        difficulty=question_result.get("difficulty", session.current_difficulty),
        points=question_result.get("points", 10),
        time_limit_seconds=question_result.get("time_limit_seconds"),
        concepts=question_result.get("concepts", []),
        generated_by="question_generation_agent",
        source_content_ids=question_result.get("source_content_ids", []),
    )
    await assessment.insert()
    
    logger.info(f"Question generated for session {request.session_id}: {assessment.id}")
    
    # Prepare response (hide correct answer for MCQ)
    options_response = None
    if assessment.options:
        options_response = [
            {"id": opt.id, "text": opt.text}
            for opt in assessment.options
        ]
    
    return QuestionResponse(
        id=str(assessment.id),
        question_type=assessment.question_type.value,
        question_text=assessment.question_text,
        question_context=assessment.question_context,
        options=options_response,
        difficulty=assessment.difficulty,
        points=assessment.points,
        time_limit_seconds=assessment.time_limit_seconds,
        concepts=assessment.concepts,
        agent_statuses=question_result.get("agent_statuses"),
        is_fallback=question_result.get("is_fallback", False),
    )


@router.post("/batch-questions")
async def get_batch_questions(
    request: BatchQuestionRequest,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Generate all questions for a session at once"""
    
    # Get session
    session = await LearningSession.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Get learner profile for adaptive difficulty
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    # Get previous attempts on this topic for adaptive question selection
    previous_sessions = await LearningSession.find(
        LearningSession.user_id == str(current_user.id),
        LearningSession.topic_name == session.topic_name,
        LearningSession.status == SessionStatus.COMPLETED
    ).sort(-LearningSession.completed_at).limit(5).to_list()
    
    # Analyze previous performance to identify weak areas
    previous_performance = []
    weak_concepts = []
    previously_asked_questions = []  # Track question texts to avoid repetition
    
    for prev_session in previous_sessions:
        # Get responses from previous sessions
        prev_responses = await AssessmentResponse.find(
            AssessmentResponse.session_id == str(prev_session.id)
        ).to_list()
        
        for response in prev_responses:
            # Track incorrect answers for weak concept identification
            if not response.is_correct:
                weak_concepts.extend(response.knowledge_gaps or [])
                weak_concepts.extend(response.identified_misconceptions or [])
            
            # Get the assessment to track question text
            assessment = await Assessment.get(response.assessment_id)
            if assessment:
                previously_asked_questions.append(assessment.question_text)
        
        previous_performance.append({
            "session_id": str(prev_session.id),
            "accuracy": prev_session.accuracy,
            "questions_answered": prev_session.questions_answered,
            "correct_answers": prev_session.correct_answers,
        })
    
    # Count weak concept frequencies
    from collections import Counter
    weak_concept_counts = Counter(weak_concepts)
    priority_weak_concepts = [concept for concept, count in weak_concept_counts.most_common(5)]
    
    # Prepare context for batch generation
    context = {
        "session_id": request.session_id,
        "user_id": str(current_user.id),
        "topic": session.topic_name,
        "is_custom_topic": session.is_custom_topic,
        "custom_query": session.custom_query,
        "current_difficulty": session.current_difficulty,
        "preferred_type": request.preferred_type,
        "learner_profile": {
            "strengths": profile.strengths if profile else [],
            "weaknesses": profile.weaknesses if profile else [],
            "knowledge_gaps": profile.knowledge_gaps if profile else [],
            "recent_accuracy": profile.get_recent_accuracy() if profile else 0,
        },
        # Previous attempts data for adaptive selection
        "previous_attempts": {
            "count": len(previous_sessions),
            "performance": previous_performance,
            "weak_concepts": priority_weak_concepts,
            "should_focus_weaknesses": len(previous_sessions) > 0,
            "previously_asked_questions": previously_asked_questions[-50:],  # Last 50 questions to avoid
        }
    }
    
    # Generate batch questions
    logger.info(f"[Assessments] Generating {request.count} questions for session {request.session_id}")
    crew = EduSynapseCrew()
    batch_result = await crew.generate_batch_questions(context, request.count)
    
    questions = batch_result.get("questions", [])
    agent_statuses = batch_result.get("agent_statuses", {})
    is_fallback = batch_result.get("is_fallback", False)
    
    # Store all questions in database
    stored_questions = []
    for q in questions:
        assessment = Assessment(
            topic_id=session.topic_id,
            topic_name=session.topic_name,
            question_type=q.get("question_type", "mcq"),
            question_text=q.get("question_text", ""),
            question_context=q.get("context"),
            options=q.get("options"),
            blank_answer=q.get("blank_answer"),
            acceptable_answers=q.get("acceptable_answers"),
            model_answer=q.get("model_answer"),
            difficulty=q.get("difficulty", "medium"),
            points=q.get("points", 10),
            time_limit_seconds=q.get("time_limit_seconds"),
            concepts=q.get("concepts", []),
            generated_by="question_generation_agent",
            source_content_ids=q.get("source_content_ids", []),
        )
        await assessment.insert()
        
        # Prepare response format
        options_response = None
        if assessment.options:
            options_response = [
                {"id": opt.id if hasattr(opt, 'id') else opt.get("id"), 
                 "text": opt.text if hasattr(opt, 'text') else opt.get("text")}
                for opt in assessment.options
            ]
        
        stored_questions.append({
            "id": str(assessment.id),
            "question_type": assessment.question_type.value if hasattr(assessment.question_type, 'value') else assessment.question_type,
            "question_text": assessment.question_text,
            "question_context": assessment.question_context,
            "options": options_response,
            "difficulty": assessment.difficulty,
            "points": assessment.points,
            "time_limit_seconds": assessment.time_limit_seconds,
            "concepts": assessment.concepts,
        })
    
    logger.info(f"Generated and stored {len(stored_questions)} questions for session {request.session_id}")
    
    return {
        "questions": stored_questions,
        "agent_statuses": agent_statuses,
        "is_fallback": is_fallback,
    }


@router.post("/submit", response_model=AnswerEvaluation)
async def submit_answer(
    submission: AnswerSubmission,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Submit an answer for evaluation"""
    
    # Get session
    session = await LearningSession.get(submission.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get assessment
    assessment = await Assessment.get(submission.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get learner profile
    profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
    
    # Prepare context for evaluation
    eval_context = {
        "session_id": submission.session_id,
        "user_id": str(current_user.id),
        "assessment": {
            "id": str(assessment.id),
            "question_type": assessment.question_type.value,
            "question_text": assessment.question_text,
            "options": [opt.model_dump() for opt in assessment.options] if assessment.options else None,
            "blank_answer": assessment.blank_answer,
            "acceptable_answers": assessment.acceptable_answers,
            "model_answer": assessment.model_answer,
            "difficulty": assessment.difficulty,
            "concepts": assessment.concepts,
        },
        "response": {
            "type": submission.response_type,
            "content": submission.response_content,
            "selected_option_id": submission.selected_option_id,
        },
        "learner_context": {
            "recent_accuracy": profile.get_recent_accuracy() if profile else 0,
            "known_weaknesses": profile.weaknesses if profile else [],
        }
    }
    
    # Trigger agent orchestration for evaluation
    crew = EduSynapseCrew()
    eval_result = await crew.evaluate_response(eval_context)
    
    # Determine if correct
    is_correct = eval_result.get("is_correct", False)
    score = eval_result.get("score", 0)
    
    # Create response record
    response = AssessmentResponse(
        user_id=str(current_user.id),
        session_id=submission.session_id,
        assessment_id=submission.assessment_id,
        response_type=submission.response_type,
        response_content=submission.response_content,
        selected_option_id=submission.selected_option_id,
        is_correct=is_correct,
        score=score,
        max_score=assessment.points,
        conceptual_understanding=eval_result.get("conceptual_understanding"),
        identified_misconceptions=eval_result.get("misconceptions", []),
        knowledge_gaps=eval_result.get("knowledge_gaps", []),
        evaluation_details=eval_result,
        time_taken_seconds=submission.time_taken_seconds,
    )
    await response.insert()
    
    # Update assessment statistics
    assessment.times_answered += 1
    if is_correct:
        assessment.times_correct += 1
    await assessment.save()
    
    # Update session
    session.questions_answered += 1
    if is_correct:
        session.correct_answers += 1
    session.total_score += score
    session.last_activity_at = datetime.utcnow()
    
    # Update session difficulty based on agent recommendation
    if eval_result.get("recommended_difficulty"):
        session.current_difficulty = eval_result["recommended_difficulty"]
    
    await session.save()
    
    # Update learner profile
    if profile:
        profile.add_performance(
            score=score,
            difficulty=assessment.difficulty,
            topic=session.topic_name,
            is_correct=is_correct
        )
        profile.total_questions_attempted += 1
        if is_correct:
            profile.total_questions_correct += 1
            
            # Track strengths - add concepts where learner answers correctly
            for concept in assessment.concepts:
                if concept and concept not in profile.strengths:
                    profile.strengths.append(concept)
                # If they mastered a concept, remove it from knowledge_gaps
                if concept in profile.knowledge_gaps:
                    profile.knowledge_gaps.remove(concept)
        else:
            # Update weaknesses from evaluation
            if eval_result.get("knowledge_gaps"):
                for gap in eval_result["knowledge_gaps"]:
                    if gap and gap not in profile.knowledge_gaps:
                        profile.knowledge_gaps.append(gap)
            
            # Track weaknesses for incorrect answers
            for concept in assessment.concepts:
                if concept and concept not in profile.weaknesses:
                    profile.weaknesses.append(concept)
                    # Remove from strengths if there
                    if concept in profile.strengths:
                        profile.strengths.remove(concept)
        
        # Keep lists manageable - limit to most recent 20 items
        profile.strengths = profile.strengths[-20:] if len(profile.strengths) > 20 else profile.strengths
        profile.weaknesses = profile.weaknesses[-20:] if len(profile.weaknesses) > 20 else profile.weaknesses
        profile.knowledge_gaps = profile.knowledge_gaps[-20:] if len(profile.knowledge_gaps) > 20 else profile.knowledge_gaps
        
        profile.updated_at = datetime.utcnow()
        await profile.save()
    
    # Update user statistics
    current_user.total_questions_answered += 1
    await current_user.save()
    
    logger.info(f"Answer submitted for assessment {submission.assessment_id}: correct={is_correct}")
    
    return AnswerEvaluation(
        response_id=str(response.id),
        is_correct=is_correct,
        score=score,
        max_score=assessment.points,
        correct_answer=eval_result.get("correct_answer"),
        explanation=eval_result.get("explanation", ""),
        conceptual_understanding=eval_result.get("conceptual_understanding", 0),
        misconceptions=eval_result.get("misconceptions", []),
        knowledge_gaps=eval_result.get("knowledge_gaps", []),
        next_steps=eval_result.get("next_steps", []),
    )


@router.get("/feedback/{response_id}", response_model=FeedbackResponse)
async def get_feedback(
    response_id: str,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Get detailed feedback for a response"""
    
    # Get response
    response = await AssessmentResponse.get(response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    if response.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if feedback already exists
    feedback = await Feedback.find_one(Feedback.response_id == response_id)
    
    if not feedback:
        # Generate feedback using Feedback Agent
        crew = EduSynapseCrew()
        
        # Get session and assessment for context
        session = await LearningSession.get(response.session_id)
        assessment = await Assessment.get(response.assessment_id)
        profile = await LearnerProfile.find_one(LearnerProfile.user_id == str(current_user.id))
        
        feedback_context = {
            "response_id": response_id,
            "session_id": response.session_id,
            "user_id": str(current_user.id),
            "assessment": {
                "question_text": assessment.question_text if assessment else "",
                "concepts": assessment.concepts if assessment else [],
                "difficulty": assessment.difficulty if assessment else "medium",
            },
            "response": {
                "content": response.response_content,
                "is_correct": response.is_correct,
                "score": response.score,
                "conceptual_understanding": response.conceptual_understanding,
                "misconceptions": response.identified_misconceptions,
                "knowledge_gaps": response.knowledge_gaps,
            },
            "learner_profile": {
                "strengths": profile.strengths if profile else [],
                "weaknesses": profile.weaknesses if profile else [],
                "recent_accuracy": profile.get_recent_accuracy() if profile else 0,
            }
        }
        
        feedback_result = await crew.generate_feedback(feedback_context)
        
        # Create feedback record
        feedback = Feedback(
            user_id=str(current_user.id),
            session_id=response.session_id,
            response_id=response_id,
            feedback_type="response",
            summary=feedback_result.get("summary", ""),
            detailed_feedback=feedback_result.get("detailed_feedback", ""),
            strengths=feedback_result.get("strengths", []),
            weaknesses=feedback_result.get("weaknesses", []),
            recommendations=feedback_result.get("recommendations", []),
            suggested_topics=feedback_result.get("suggested_topics", []),
            suggested_difficulty=feedback_result.get("suggested_difficulty", "medium"),
            encouragement_message=feedback_result.get("encouragement_message"),
            overall_performance_score=feedback_result.get("overall_performance_score", 0),
            improvement_trend=feedback_result.get("improvement_trend", "stable"),
            generated_by_agent="feedback_agent",
            agent_confidence=feedback_result.get("confidence", 0.8),
        )
        await feedback.insert()
        
        # Update response with feedback reference
        response.feedback_id = str(feedback.id)
        await response.save()
    
    return FeedbackResponse(
        id=str(feedback.id),
        feedback_type=feedback.feedback_type,
        summary=feedback.summary,
        detailed_feedback=feedback.detailed_feedback,
        strengths=[s.model_dump() for s in feedback.strengths],
        weaknesses=[w.model_dump() for w in feedback.weaknesses],
        recommendations=[r.model_dump() for r in feedback.recommendations],
        suggested_topics=feedback.suggested_topics,
        suggested_difficulty=feedback.suggested_difficulty,
        encouragement_message=feedback.encouragement_message,
        overall_performance_score=feedback.overall_performance_score,
        improvement_trend=feedback.improvement_trend,
        created_at=feedback.created_at,
    )


@router.get("/history/{session_id}")
async def get_assessment_history(
    session_id: str,
    current_user: User = Depends(get_or_create_guest_user)
):
    """Get assessment history for a session"""
    
    # Verify session ownership
    session = await LearningSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all responses for this session
    responses = await AssessmentResponse.find(
        AssessmentResponse.session_id == session_id
    ).sort(AssessmentResponse.submitted_at).to_list()
    
    history = []
    for resp in responses:
        assessment = await Assessment.get(resp.assessment_id)
        history.append({
            "response_id": str(resp.id),
            "question_text": assessment.question_text if assessment else "",
            "question_type": assessment.question_type.value if assessment else "",
            "difficulty": assessment.difficulty if assessment else "",
            "response_content": resp.response_content,
            "is_correct": resp.is_correct,
            "score": resp.score,
            "time_taken_seconds": resp.time_taken_seconds,
            "submitted_at": resp.submitted_at,
        })
    
    return {
        "session_id": session_id,
        "total_questions": len(history),
        "correct_answers": sum(1 for h in history if h["is_correct"]),
        "history": history
    }
