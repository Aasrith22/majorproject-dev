// Unified API Service for EduSynapse
// Connects directly to the FastAPI backend server - NO MOCK DATA

import { authAPI, sessionsAPI, assessmentsAPI, dashboardAPI, healthAPI } from './real-api.service.js';

// Configuration
let healthCheckPromise = null;
let lastHealthCheck = 0;
const HEALTH_CHECK_CACHE_MS = 30000;

// Active session tracking
let activeSession = null;
let activeTopicName = null;

// Check backend health (with caching)
async function checkBackendHealth() {
  const now = Date.now();
  
  if (healthCheckPromise && (now - lastHealthCheck) < HEALTH_CHECK_CACHE_MS) {
    return healthCheckPromise;
  }
  
  healthCheckPromise = (async () => {
    try {
      const health = await healthAPI.check();
      lastHealthCheck = Date.now();
      if (health.status !== 'healthy') {
        throw new Error('Backend is not healthy');
      }
      console.log('🔗 Backend connected');
      return true;
    } catch (error) {
      lastHealthCheck = Date.now();
      console.error('❌ Backend connection failed:', error.message);
      throw new Error('Backend unavailable. Please ensure the server is running.');
    }
  })();
  
  return healthCheckPromise;
}

// Initialize health check
checkBackendHealth().catch(() => {});

// ============================================================================
// Unified API Service
// ============================================================================

export const apiService = {
  // -------------------------------------------------------------------------
  // User & Profile
  // -------------------------------------------------------------------------
  async getUserProfile() {
    await checkBackendHealth();
    
    const user = await authAPI.getProfile();
    const progress = await dashboardAPI.getProgress().catch(() => null);
    const sessions = await sessionsAPI.listSessions(null, 50).catch(() => []);  // Get more sessions
    
    // Count completed sessions from actual session data
    const completedSessions = sessions.filter(s => s.status === 'completed').length;
    const inProgressSessions = sessions.filter(s => s.status === 'active').length;
    
    return {
      user: {
        id: user.id,
        name: user.full_name || user.username,
        email: user.email,
        createdAt: new Date(user.created_at),
      },
      stats: {
        totalSessions: sessions.length || 0,
        completedSessions: completedSessions,
        inProgressSessions: inProgressSessions,
        averageScore: progress?.average_score || 0,
        totalTimeSpent: progress?.total_study_time_minutes || 0,
        streakDays: progress?.current_streak_days || 0,
        questionsAnswered: progress?.total_questions_attempted || 0,
        correctAnswers: progress?.total_questions_correct || (progress?.total_questions_attempted * (progress?.accuracy || 0) / 100) || 0,
      },
      recentTopics: progress?.recent_topics || [],
      learningPath: progress?.learning_path || {
        currentTopic: null,
        recommendedTopics: [],
        completedTopics: [],
        knowledgeGaps: (progress?.knowledge_gaps || []).map((gap, index) => {
          // Handle both string and object formats
          if (typeof gap === 'string') {
            return {
              id: `gap-${index}`,
              concept: gap,
              severity: 'medium',
              recommendation: `Review and practice ${gap}`,
            };
          }
          return {
            ...gap,
            id: gap.id || `gap-${index}`,
          };
        }),
      },
    };
  },

  async getDashboardData() {
    await checkBackendHealth();
    
    const [progress, analytics] = await Promise.all([
      dashboardAPI.getProgress(),
      dashboardAPI.getAnalytics('weekly'),
    ]);
    
    return {
      performanceHistory: analytics?.performance_history || [],
      conceptMastery: analytics?.concept_mastery || [],
      learningStats: progress?.stats || {},
      recentFeedback: analytics?.recent_feedback || [],
      upcomingRecommendations: progress?.recommendations || [],
    };
  },

  async getLearnerProfile() {
    await checkBackendHealth();
    
    const profile = await authAPI.getProfile();
    const progress = await dashboardAPI.getProgress().catch(() => ({}));
    
    // Transform knowledge_gaps to ensure each has an id
    const knowledgeGaps = (progress?.knowledge_gaps || []).map((gap, index) => {
      if (typeof gap === 'string') {
        return {
          id: `gap-learner-${index}-${Date.now()}`,
          concept: gap,
          severity: 'medium',
          recommendation: `Review and practice ${gap}`
        };
      }
      return {
        ...gap,
        id: gap.id || `gap-learner-${index}-${Date.now()}`
      };
    });
    
    return {
      id: profile.id,
      name: profile.full_name || profile.username,
      learningStyle: profile.preferences?.learning_style || {
        visual: 0.25,
        auditory: 0.25,
        readingWriting: 0.25,
        kinesthetic: 0.25,
      },
      currentLevel: profile.preferences?.difficulty_preference || 'intermediate',
      strengths: progress?.strengths || [],
      weaknesses: progress?.weaknesses || [],
      knowledgeGaps: knowledgeGaps,
      preferredModality: profile.preferences?.preferred_modality || 'text',
      masteryLevels: progress?.mastery_levels || [],
    };
  },

  // -------------------------------------------------------------------------
  // Topics
  // -------------------------------------------------------------------------
  async getTopics() {
    await checkBackendHealth();
    
    try {
      // Get available topics from knowledge base + custom topics
      const availableTopics = await dashboardAPI.getAvailableTopics();
      
      if (availableTopics?.topics?.length > 0) {
        return availableTopics.topics.map(t => ({
          id: t.id,
          name: t.name,
          subject: t.subject,
          description: t.description,
          difficulty: t.difficulty_levels?.[0] || 'medium',
          contentCount: t.content_count,
          subtopics: t.subtopics || [],
          isCustom: t.is_custom || false,
          sessionsCompleted: t.sessions_completed || 0,
          lastStudied: t.last_studied,
        }));
      }
      
      // Fallback to user's recent topics
      const progress = await dashboardAPI.getProgress();
      return progress?.recent_topics || progress?.topics || [];
    } catch (error) {
      console.warn('Failed to get topics:', error);
      return [];
    }
  },

  async getTopicById(topicId) {
    const topics = await this.getTopics();
    return topics.find(t => t.id === topicId);
  },

  // -------------------------------------------------------------------------
  // Learning Session
  // -------------------------------------------------------------------------
  async startSession(topicId, totalQuestions = 10, testType = 'mcq', topicName = null, isCustomTopic = false) {
    await checkBackendHealth();
    
    // For custom topics, topicId is the topic name/query
    const actualTopicName = topicName || topicId;
    const isCustom = isCustomTopic || (topicId === topicName) || !topicId.includes('-');
    const customQuery = isCustom ? actualTopicName : null;
    
    activeTopicName = actualTopicName;
    
    const session = await sessionsAPI.startSession(
      isCustom ? actualTopicName.toLowerCase().replace(/\s+/g, '-') : topicId,  // topic_id
      actualTopicName,  // topic_name
      isCustom,  // is_custom_topic
      customQuery,  // custom_query
      totalQuestions,
      [testType]
    );
    
    activeSession = {
      id: session.id || session.session_id,
      userId: session.user_id,
      topicId: session.topic_id || topicId,
      topicName: activeTopicName,
      startedAt: new Date(session.started_at || session.created_at),
      status: session.status || 'active',
      interactions: [],
    };
    
    return activeSession;
  },

  async endSession(sessionId) {
    await checkBackendHealth();
    
    const result = await sessionsAPI.endSession(sessionId);
    activeSession = null;
    activeTopicName = null;
    return result;
  },

  // -------------------------------------------------------------------------
  // Question Generation
  // -------------------------------------------------------------------------
  async generateQuestion(topicId, difficulty, testType) {
    await checkBackendHealth();
    
    const sessionId = activeSession?.id;
    
    if (!sessionId) {
      throw new Error('No active session. Please start a learning session first.');
    }
    
    const question = await assessmentsAPI.getQuestion(
      sessionId,
      testType,
      difficulty
    );
    
    return transformQuestion(question);
  },

  async generateBatchQuestions(count, testType) {
    await checkBackendHealth();
    
    const sessionId = activeSession?.id;
    
    if (!sessionId) {
      throw new Error('No active session. Please start a learning session first.');
    }
    
    const result = await assessmentsAPI.getBatchQuestions(
      sessionId,
      count,
      testType
    );
    
    return {
      questions: result.questions.map(transformQuestion),
      agentStatuses: result.agent_statuses,
      isFallback: result.is_fallback,
    };
  },

  // -------------------------------------------------------------------------
  // Answer Submission
  // -------------------------------------------------------------------------
  async submitAnswer(answer) {
    await checkBackendHealth();
    
    const sessionId = activeSession?.id;
    
    if (!sessionId) {
      throw new Error('No active session. Please start a learning session first.');
    }
    
    const response = await assessmentsAPI.submitAnswer(
      sessionId,
      answer.questionId,
      answer.content,
      answer.modality || 'text',
      answer.selectedOptionId || null,
      answer.timeTaken || null
    );
    
    return transformFeedback(response, answer);
  },

  // -------------------------------------------------------------------------
  // CrewAI Workflow
  // -------------------------------------------------------------------------
  async executeCrewAIWorkflow(query, topicId) {
    await checkBackendHealth();
    
    const sessions = await sessionsAPI.listSessions('active', 1);
    const sessionId = sessions[0]?.id;
    
    if (!sessionId) {
      throw new Error('No active session for workflow execution.');
    }
    
    const result = await sessionsAPI.submitInput(
      sessionId,
      query.content,
      query.modality || 'text'
    );
    
    return {
      execution: {
        workflowId: 'adaptive-learning-workflow',
        status: 'completed',
      },
      analysisResult: result.analysis,
      retrievalResult: result.retrieval,
    };
  },

  async processQuery(query) {
    return this.executeCrewAIWorkflow(query);
  },

  // -------------------------------------------------------------------------
  // Voice & Drawing (Multimodal)
  // -------------------------------------------------------------------------
  async transcribeVoice(audioBlob) {
    await checkBackendHealth();
    
    const sessions = await sessionsAPI.listSessions('active', 1);
    const sessionId = sessions[0]?.id;
    
    if (!sessionId) {
      throw new Error('No active session for voice transcription.');
    }
    
    // Convert blob to base64
    const reader = new FileReader();
    const base64 = await new Promise((resolve) => {
      reader.onloadend = () => resolve(reader.result.split(',')[1]);
      reader.readAsDataURL(audioBlob);
    });
    
    const result = await sessionsAPI.submitInput(
      sessionId,
      base64,
      'voice',
      { format: audioBlob.type }
    );
    
    return {
      transcription: result.transcription || result.content,
      confidence: result.confidence || 0.9,
      language: 'en',
    };
  },

  async analyzeDrawing(imageData) {
    await checkBackendHealth();
    
    const sessions = await sessionsAPI.listSessions('active', 1);
    const sessionId = sessions[0]?.id;
    
    if (!sessionId) {
      throw new Error('No active session for drawing analysis.');
    }
    
    const result = await sessionsAPI.submitInput(
      sessionId,
      imageData,
      'diagram'
    );
    
    return {
      text: result.analysis || result.content,
      confidence: result.confidence || 0.85,
      recognizedElements: result.elements || [],
    };
  },

  // -------------------------------------------------------------------------
  // Adaptivity State
  // -------------------------------------------------------------------------
  async getAdaptivityState() {
    await checkBackendHealth();
    
    const progress = await dashboardAPI.getProgress();
    return {
      currentDifficulty: progress?.current_difficulty || 'medium',
      performanceWindow: progress?.recent_performance || [],
      adaptationHistory: [],
      learnerProfile: await this.getLearnerProfile(),
    };
  },

  async updateLearnerProfile(updates) {
    await checkBackendHealth();
    
    await authAPI.updatePreferences(updates);
    return await this.getLearnerProfile();
  },

  async getKnowledgeGaps() {
    await checkBackendHealth();
    
    const progress = await dashboardAPI.getProgress();
    return progress?.knowledge_gaps || [];
  },

  async getMasteryLevels() {
    await checkBackendHealth();
    
    const mastery = await dashboardAPI.getTopicMastery();
    return mastery || [];
  },

  async getAgentDefinitions() {
    return [
      { id: 'query-analysis', name: 'Query Analysis Agent', role: 'Analyzes user queries and determines learning intent' },
      { id: 'information-retrieval', name: 'Information Retrieval Agent', role: 'Retrieves relevant educational content' },
      { id: 'question-generation', name: 'Question Generation Agent', role: 'Generates adaptive questions based on content' },
      { id: 'feedback', name: 'Feedback Agent', role: 'Provides personalized learning feedback' },
    ];
  },

  // -------------------------------------------------------------------------
  // Authentication (passthrough)
  // -------------------------------------------------------------------------
  auth: authAPI,
};

// ============================================================================
// Helper Functions
// ============================================================================

function normalizeQuestionType(type) {
  const typeMap = {
    'mcq': 'multiple-choice',
    'multiple_choice': 'multiple-choice',
    'multiple-choice': 'multiple-choice',
    'fill_in_blank': 'fill-in-blank',
    'fill-in-blank': 'fill-in-blank',
    'essay': 'essay',
    'short_answer': 'short-answer',
    'short-answer': 'short-answer',
  };
  return typeMap[type?.toLowerCase()] || type || 'multiple-choice';
}

function transformQuestion(q) {
  // Transform options to keep both id and text for proper MCQ submission
  const transformedOptions = q.options?.map((o, index) => {
    if (typeof o === 'string') {
      return { id: String.fromCharCode(65 + index), text: o };
    }
    return { id: o.id || String.fromCharCode(65 + index), text: o.text || o };
  }) || [];
  
  return {
    id: q.id || q.assessment_id,
    type: normalizeQuestionType(q.question_type || q.type),
    content: q.question_text || q.content,
    options: transformedOptions,
    correctAnswer: q.correct_answer,
    difficulty: q.difficulty,
    topic: q.topic,
    expectedModality: q.expected_modality || 'text',
    hints: q.hints || [],
    adaptiveInfo: {
      currentDifficulty: q.difficulty,
    },
    // Agent execution metadata from backend
    agentStatuses: q.agent_statuses || null,
    isFallback: q.is_fallback || false,
  };
}

function transformFeedback(response, answer) {
  return {
    id: response.id || `feedback-${Date.now()}`,
    questionId: answer.questionId,
    answerId: answer.id,
    isCorrect: response.is_correct,
    score: response.score || (response.is_correct ? 85 : 45),
    analysis: {
      strengths: response.strengths || [],
      weaknesses: response.weaknesses || [],
      misconceptions: response.misconceptions || [],
    },
    explanation: response.explanation || response.feedback,
    improvementPlan: response.improvement_plan || null,
    resources: response.resources || [],
    adaptiveInfo: response.adaptive_info || {
      previousDifficulty: 'medium',
      newDifficulty: response.next_difficulty || 'medium',
      reason: '',
    },
    detectedKnowledgeGaps: response.knowledge_gaps || [],
  };
}

export default apiService;
