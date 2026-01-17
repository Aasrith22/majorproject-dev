// Types for the EduSynapse API
// Using JSDoc for type documentation in JavaScript

// ============================================================================
// Constants for Type-Safe Values
// ============================================================================

/** @type {Object.<string, string>} */
export const TopicStatus = {
  NOT_STARTED: "not-started",
  IN_PROGRESS: "in-progress",
  COMPLETED: "completed",
};

/** @type {Object.<string, string>} */
export const SessionStatus = {
  ACTIVE: "active",
  COMPLETED: "completed",
  PAUSED: "paused",
};

/** @type {Object.<string, string>} */
export const AgentTypes = {
  QUERY_ANALYSIS: "query-analysis",
  INFORMATION_RETRIEVAL: "information-retrieval",
  QUESTION_GENERATION: "question-generation",
  FEEDBACK: "feedback",
};

/** @type {Object.<string, string>} */
export const AgentStatuses = {
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  ERROR: "error",
};

/** @type {Object.<string, string>} */
export const QueryIntents = {
  DEFINITIONAL: "definitional",
  CONCEPTUAL: "conceptual",
  APPLIED: "applied",
  FOLLOW_UP: "follow-up",
};

/** @type {Object.<string, string>} */
export const TestTypes = {
  MCQ: "mcq",
  FILL_IN_BLANK: "fill-in-blank",
  ESSAY: "essay",
};

/** @type {Object.<string, string>} */
export const QuestionTypes = {
  MULTIPLE_CHOICE: "multiple-choice",
  FILL_IN_BLANK: "fill-in-blank",
  ESSAY: "essay",
  SHORT_ANSWER: "short-answer",
  DIAGRAM: "diagram",
  VOICE: "voice",
};

/** @type {Object.<string, string>} */
export const InputModalities = {
  TEXT: "text",
  VOICE: "voice",
  DRAWING: "drawing",
};

/** @type {Object.<string, string>} */
export const DifficultyLevels = {
  EASY: "easy",
  MEDIUM: "medium",
  HARD: "hard",
  BEGINNER: "beginner",
  INTERMEDIATE: "intermediate",
  ADVANCED: "advanced",
};

/** @type {Object.<string, string>} */
export const SeverityLevels = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
};

/** @type {Object.<string, string>} */
export const TrendTypes = {
  IMPROVING: "improving",
  STABLE: "stable",
  DECLINING: "declining",
};

/** @type {Object.<string, string>} */
export const ResourceTypes = {
  ARTICLE: "article",
  VIDEO: "video",
  EXERCISE: "exercise",
  DIAGRAM: "diagram",
};

/** @type {Object.<string, string>} */
export const RetrievalTypes = {
  SEMANTIC: "semantic",
  KEYWORD: "keyword",
  HYBRID: "hybrid",
};

/** @type {Object.<string, string>} */
export const ExpectedModalities = {
  TEXT: "text",
  VOICE: "voice",
  DRAWING: "drawing",
  MULTIMODAL: "multimodal",
};

// ============================================================================
// Factory Functions for Creating Objects
// ============================================================================

/**
 * Create a user object
 * @param {Object} user
 * @param {string} user.id
 * @param {string} user.name
 * @param {string} user.email
 * @param {string} [user.avatar]
 * @param {Date} [user.createdAt]
 * @returns {Object}
 */
export function createUser(user = {}) {
  return {
    id: user.id || `user-${Date.now()}`,
    name: user.name || "",
    email: user.email || "",
    avatar: user.avatar || null,
    createdAt: user.createdAt || new Date(),
  };
}

/**
 * Create learning stats
 * @param {Object} stats
 * @returns {Object}
 */
export function createLearningStats(stats = {}) {
  return {
    totalSessions: stats.totalSessions || 0,
    completedSessions: stats.completedSessions || 0,
    inProgressSessions: stats.inProgressSessions || 0,
    averageScore: stats.averageScore || 0,
    totalTimeSpent: stats.totalTimeSpent || 0,
    streakDays: stats.streakDays || 0,
    questionsAnswered: stats.questionsAnswered || 0,
    correctAnswers: stats.correctAnswers || 0,
  };
}

/**
 * Create a topic
 * @param {Object} topic
 * @returns {Object}
 */
export function createTopic(topic = {}) {
  return {
    id: topic.id || `topic-${Date.now()}`,
    name: topic.name || "",
    subject: topic.subject || "",
    description: topic.description || null,
    progress: topic.progress || 0,
    status: topic.status || TopicStatus.NOT_STARTED,
    score: topic.score || null,
    lastAccessed: topic.lastAccessed || null,
    difficulty: topic.difficulty || DifficultyLevels.INTERMEDIATE,
  };
}

/**
 * Create a knowledge gap
 * @param {Object} gap
 * @returns {Object}
 */
export function createKnowledgeGap(gap = {}) {
  return {
    id: gap.id || `gap-${Date.now()}`,
    topic: gap.topic || "",
    concept: gap.concept || "",
    severity: gap.severity || SeverityLevels.MEDIUM,
    recommendation: gap.recommendation || "",
  };
}

/**
 * Create a learning path
 * @param {Object} path
 * @returns {Object}
 */
export function createLearningPath(path = {}) {
  return {
    currentTopic: path.currentTopic || null,
    recommendedTopics: path.recommendedTopics || [],
    completedTopics: path.completedTopics || [],
    knowledgeGaps: path.knowledgeGaps || [],
  };
}

/**
 * Create a user profile
 * @param {Object} profile
 * @returns {Object}
 */
export function createUserProfile(profile = {}) {
  return {
    user: profile.user || createUser(),
    stats: profile.stats || createLearningStats(),
    recentTopics: profile.recentTopics || [],
    learningPath: profile.learningPath || createLearningPath(),
  };
}

/**
 * Create a learning session
 * @param {Object} session
 * @returns {Object}
 */
export function createLearningSession(session = {}) {
  return {
    id: session.id || `session-${Date.now()}`,
    userId: session.userId || "",
    topicId: session.topicId || "",
    startedAt: session.startedAt || new Date(),
    endedAt: session.endedAt || null,
    status: session.status || SessionStatus.ACTIVE,
    interactions: session.interactions || [],
  };
}

/**
 * Create an interaction
 * @param {Object} interaction
 * @returns {Object}
 */
export function createInteraction(interaction = {}) {
  return {
    id: interaction.id || `interaction-${Date.now()}`,
    timestamp: interaction.timestamp || new Date(),
    query: interaction.query || null,
    agentResponses: interaction.agentResponses || [],
    question: interaction.question || null,
    userAnswer: interaction.userAnswer || null,
    feedback: interaction.feedback || null,
  };
}

/**
 * Create an agent response
 * @param {Object} response
 * @returns {Object}
 */
export function createAgentResponse(response = {}) {
  return {
    agentType: response.agentType || AgentTypes.QUERY_ANALYSIS,
    status: response.status || AgentStatuses.PENDING,
    result: response.result || null,
    processingTime: response.processingTime || null,
    error: response.error || null,
  };
}

/**
 * Create a query analysis result
 * @param {Object} result
 * @returns {Object}
 */
export function createQueryAnalysisResult(result = {}) {
  return {
    intent: result.intent || QueryIntents.CONCEPTUAL,
    entities: result.entities || {
      subject: null,
      topic: null,
      difficultyLevel: null,
    },
    context: result.context || "",
    confidence: result.confidence || 0,
  };
}

/**
 * Create a retrieval result
 * @param {Object} result
 * @returns {Object}
 */
export function createRetrievalResult(result = {}) {
  return {
    content: result.content || "",
    source: result.source || "",
    relevanceScore: result.relevanceScore || 0,
    type: result.type || RetrievalTypes.HYBRID,
  };
}

/**
 * Create a generated question
 * @param {Object} question
 * @returns {Object}
 */
export function createGeneratedQuestion(question = {}) {
  return {
    id: question.id || `question-${Date.now()}`,
    type: question.type || QuestionTypes.MULTIPLE_CHOICE,
    content: question.content || "",
    options: question.options || null,
    correctAnswer: question.correctAnswer || null,
    blanks: question.blanks || null,
    hints: question.hints || [],
    difficulty: question.difficulty || DifficultyLevels.MEDIUM,
    topic: question.topic || "",
    expectedModality: question.expectedModality || ExpectedModalities.TEXT,
  };
}

/**
 * Create a user query
 * @param {Object} query
 * @returns {Object}
 */
export function createUserQuery(query = {}) {
  return {
    id: query.id || `query-${Date.now()}`,
    modality: query.modality || InputModalities.TEXT,
    content: query.content || "",
    rawData: query.rawData || null,
    timestamp: query.timestamp || new Date(),
  };
}

/**
 * Create a user answer
 * @param {Object} answer
 * @returns {Object}
 */
export function createUserAnswer(answer = {}) {
  return {
    id: answer.id || `answer-${Date.now()}`,
    questionId: answer.questionId || "",
    modality: answer.modality || InputModalities.TEXT,
    content: answer.content || "",
    rawData: answer.rawData || null,
    timestamp: answer.timestamp || new Date(),
  };
}

/**
 * Create an improvement plan
 * @param {Object} plan
 * @returns {Object}
 */
export function createImprovementPlan(plan = {}) {
  return {
    id: plan.id || `plan-${Date.now()}`,
    targetConcepts: plan.targetConcepts || [],
    suggestedActions: plan.suggestedActions || [],
    estimatedTime: plan.estimatedTime || 0,
    priority: plan.priority || SeverityLevels.MEDIUM,
  };
}

/**
 * Create a resource
 * @param {Object} resource
 * @returns {Object}
 */
export function createResource(resource = {}) {
  return {
    id: resource.id || `resource-${Date.now()}`,
    title: resource.title || "",
    type: resource.type || ResourceTypes.ARTICLE,
    url: resource.url || null,
    description: resource.description || "",
  };
}

/**
 * Create feedback
 * @param {Object} feedback
 * @returns {Object}
 */
export function createFeedback(feedback = {}) {
  return {
    id: feedback.id || `feedback-${Date.now()}`,
    questionId: feedback.questionId || "",
    answerId: feedback.answerId || "",
    isCorrect: feedback.isCorrect || false,
    score: feedback.score || 0,
    analysis: feedback.analysis || {
      strengths: [],
      weaknesses: [],
      misconceptions: [],
    },
    explanation: feedback.explanation || "",
    improvementPlan: feedback.improvementPlan || createImprovementPlan(),
    resources: feedback.resources || [],
  };
}

/**
 * Create a performance metric
 * @param {Object} metric
 * @returns {Object}
 */
export function createPerformanceMetric(metric = {}) {
  return {
    date: metric.date || new Date().toISOString().split("T")[0],
    score: metric.score || 0,
    questionsAttempted: metric.questionsAttempted || 0,
    correctAnswers: metric.correctAnswers || 0,
    timeSpent: metric.timeSpent || 0,
  };
}

/**
 * Create concept mastery data
 * @param {Object} mastery
 * @returns {Object}
 */
export function createConceptMastery(mastery = {}) {
  return {
    concept: mastery.concept || "",
    mastery: mastery.mastery || 0,
    trend: mastery.trend || TrendTypes.STABLE,
    lastAssessed: mastery.lastAssessed || new Date(),
  };
}

/**
 * Create dashboard data
 * @param {Object} data
 * @returns {Object}
 */
export function createDashboardData(data = {}) {
  return {
    performanceHistory: data.performanceHistory || [],
    conceptMastery: data.conceptMastery || [],
    learningStats: data.learningStats || createLearningStats(),
    recentFeedback: data.recentFeedback || [],
    upcomingRecommendations: data.upcomingRecommendations || [],
  };
}

/**
 * Create an API response wrapper
 * @param {Object} response
 * @returns {Object}
 */
export function createApiResponse(response = {}) {
  return {
    success: response.success !== undefined ? response.success : true,
    data: response.data || null,
    error: response.error || null,
    message: response.message || null,
  };
}

/**
 * Create a paginated response
 * @param {Object} response
 * @returns {Object}
 */
export function createPaginatedResponse(response = {}) {
  return {
    items: response.items || [],
    total: response.total || 0,
    page: response.page || 1,
    pageSize: response.pageSize || 10,
    hasMore: response.hasMore || false,
  };
}

// ============================================================================
// Default Export
// ============================================================================

export default {
  // Constants
  TopicStatus,
  SessionStatus,
  AgentTypes,
  AgentStatuses,
  QueryIntents,
  TestTypes,
  QuestionTypes,
  InputModalities,
  DifficultyLevels,
  SeverityLevels,
  TrendTypes,
  ResourceTypes,
  RetrievalTypes,
  ExpectedModalities,
  // Factory Functions
  createUser,
  createLearningStats,
  createTopic,
  createKnowledgeGap,
  createLearningPath,
  createUserProfile,
  createLearningSession,
  createInteraction,
  createAgentResponse,
  createQueryAnalysisResult,
  createRetrievalResult,
  createGeneratedQuestion,
  createUserQuery,
  createUserAnswer,
  createImprovementPlan,
  createResource,
  createFeedback,
  createPerformanceMetric,
  createConceptMastery,
  createDashboardData,
  createApiResponse,
  createPaginatedResponse,
};
