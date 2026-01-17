// Agent Framework Types for EduSynapse Multi-Agent Architecture
// Based on CrewAI orchestration patterns
// Using JSDoc for type documentation

// ============================================================================
// Agent Role Constants
// ============================================================================

/** @type {Object.<string, string>} */
export const AgentRoles = {
  QUERY_ANALYSIS: "query-analysis",
  INFORMATION_RETRIEVAL: "information-retrieval",
  QUESTION_GENERATION: "question-generation",
  FEEDBACK: "feedback",
};

/** @type {Object.<string, string>} */
export const QueryIntents = {
  DEFINITIONAL: "definitional",
  CONCEPTUAL: "conceptual",
  APPLIED: "applied",
  FOLLOW_UP: "follow-up",
  CLARIFICATION: "clarification",
  ASSESSMENT_REQUEST: "assessment-request",
  TOPIC_SWITCH: "topic-switch",
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
export const QuestionFormats = {
  MULTIPLE_CHOICE: "multiple-choice",
  FILL_IN_BLANK: "fill-in-blank",
  ESSAY: "essay",
  SHORT_ANSWER: "short-answer",
  DIAGRAM_LABEL: "diagram-label",
  VOICE_RESPONSE: "voice-response",
  CODE_COMPLETION: "code-completion",
};

/** @type {Object.<string, string>} */
export const ContentTypes = {
  DEFINITION: "definition",
  EXPLANATION: "explanation",
  EXAMPLE: "example",
  DIAGRAM: "diagram",
  EXERCISE: "exercise",
  VIDEO: "video",
  ARTICLE: "article",
  FORMULA: "formula",
};

/** @type {Object.<string, string>} */
export const WorkflowStatuses = {
  PENDING: "pending",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed",
  PAUSED: "paused",
};

/** @type {Object.<string, string>} */
export const TaskStatuses = {
  PENDING: "pending",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed",
  SKIPPED: "skipped",
};

/** @type {Object.<string, string>} */
export const InputModalities = {
  TEXT: "text",
  VOICE: "voice",
  DRAWING: "drawing",
};

/** @type {Object.<string, string>} */
export const TrendTypes = {
  IMPROVING: "improving",
  STABLE: "stable",
  DECLINING: "declining",
};

/** @type {Object.<string, string>} */
export const SeverityLevels = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
};

// ============================================================================
// Factory Functions for Creating Type-Safe Objects
// ============================================================================

/**
 * Create an agent definition
 * @param {Object} config
 * @param {string} config.id
 * @param {string} config.role - One of AgentRoles
 * @param {string} config.name
 * @param {string} config.description
 * @param {string} config.goal
 * @param {string} config.backstory
 * @param {string[]} config.capabilities
 * @param {Object} config.llmConfig
 * @returns {Object}
 */
export function createAgentDefinition(config) {
  return {
    id: config.id,
    role: config.role,
    name: config.name,
    description: config.description,
    goal: config.goal,
    backstory: config.backstory,
    capabilities: config.capabilities || [],
    llmConfig: config.llmConfig || {
      provider: "openai",
      model: "gpt-4",
      temperature: 0.7,
      maxTokens: 2000,
      fallbackProvider: "gemini",
    },
  };
}

/**
 * Create an LLM configuration
 * @param {Object} config
 * @param {string} config.provider - "openai" or "gemini"
 * @param {string} config.model
 * @param {number} config.temperature
 * @param {number} config.maxTokens
 * @param {string} [config.fallbackProvider]
 * @returns {Object}
 */
export function createLLMConfig(config) {
  return {
    provider: config.provider || "openai",
    model: config.model || "gpt-4",
    temperature: config.temperature || 0.7,
    maxTokens: config.maxTokens || 2000,
    fallbackProvider: config.fallbackProvider,
  };
}

/**
 * Create a query analysis input
 * @param {Object} input
 * @param {string} input.query
 * @param {string} input.modality - "text", "voice", or "drawing"
 * @param {Object} [input.sessionContext]
 * @param {string} [input.rawData]
 * @returns {Object}
 */
export function createQueryAnalysisInput(input) {
  return {
    query: input.query,
    modality: input.modality || "text",
    sessionContext: input.sessionContext || null,
    rawData: input.rawData || null,
  };
}

/**
 * Create a query analysis output
 * @param {Object} output
 * @returns {Object}
 */
export function createQueryAnalysisOutput(output) {
  return {
    intent: output.intent || QueryIntents.CONCEPTUAL,
    entities: output.entities || {
      subject: null,
      topic: null,
      subtopic: null,
      difficultyLevel: null,
      conceptKeywords: [],
      questionType: null,
    },
    context: output.context || {
      sessionHistory: [],
      currentTopic: null,
      learnerLevel: "intermediate",
      previousMisconceptions: [],
      knowledgeState: {
        masteredConcepts: [],
        partialConcepts: [],
        unknownConcepts: [],
        misconceptions: [],
      },
    },
    confidence: output.confidence || 0,
    processingDetails: output.processingDetails || {
      inputType: "text",
      normalizedText: "",
      processingPipeline: [],
      totalProcessingTime: 0,
      modelsUsed: [],
    },
  };
}

/**
 * Create extracted entities
 * @param {Object} entities
 * @returns {Object}
 */
export function createExtractedEntities(entities = {}) {
  return {
    subject: entities.subject || null,
    topic: entities.topic || null,
    subtopic: entities.subtopic || null,
    difficultyLevel: entities.difficultyLevel || null,
    conceptKeywords: entities.conceptKeywords || [],
    questionType: entities.questionType || null,
  };
}

/**
 * Create a session context
 * @param {Object} context
 * @returns {Object}
 */
export function createSessionContext(context = {}) {
  return {
    sessionId: context.sessionId || `session-${Date.now()}`,
    topicId: context.topicId || "",
    previousQueries: context.previousQueries || [],
    answeredQuestions: context.answeredQuestions || [],
    performanceHistory: context.performanceHistory || [],
  };
}

/**
 * Create a performance point
 * @param {Object} point
 * @returns {Object}
 */
export function createPerformancePoint(point = {}) {
  return {
    questionId: point.questionId || "",
    score: point.score || 0,
    difficulty: point.difficulty || "medium",
    topic: point.topic || "",
    timestamp: point.timestamp || new Date(),
  };
}

/**
 * Create a knowledge state
 * @param {Object} state
 * @returns {Object}
 */
export function createKnowledgeState(state = {}) {
  return {
    masteredConcepts: state.masteredConcepts || [],
    partialConcepts: state.partialConcepts || [],
    unknownConcepts: state.unknownConcepts || [],
    misconceptions: state.misconceptions || [],
  };
}

/**
 * Create a misconception record
 * @param {Object} record
 * @returns {Object}
 */
export function createMisconceptionRecord(record = {}) {
  return {
    concept: record.concept || "",
    misconception: record.misconception || "",
    detectedAt: record.detectedAt || new Date(),
    corrected: record.corrected || false,
  };
}

/**
 * Create a retrieval input
 * @param {Object} input
 * @returns {Object}
 */
export function createRetrievalInput(input = {}) {
  return {
    analysisResult: input.analysisResult || null,
    topicId: input.topicId || "",
    maxResults: input.maxResults || 10,
    includeTypes: input.includeTypes || Object.values(ContentTypes),
  };
}

/**
 * Create a retrieval output
 * @param {Object} output
 * @returns {Object}
 */
export function createRetrievalOutput(output = {}) {
  return {
    results: output.results || [],
    searchMetadata: output.searchMetadata || {
      queryVector: [],
      searchType: "hybrid",
      totalResults: 0,
      processingTime: 0,
      indexUsed: "",
    },
    relevanceScores: output.relevanceScores || [],
  };
}

/**
 * Create retrieved content
 * @param {Object} content
 * @returns {Object}
 */
export function createRetrievedContent(content = {}) {
  return {
    id: content.id || `content-${Date.now()}`,
    content: content.content || "",
    source: content.source || {
      name: "",
      type: "textbook",
      url: null,
      chapter: null,
      section: null,
    },
    type: content.type || ContentTypes.EXPLANATION,
    relevanceScore: content.relevanceScore || 0,
    semanticEmbedding: content.semanticEmbedding || null,
    metadata: content.metadata || {
      difficulty: "intermediate",
      estimatedReadTime: null,
      tags: [],
      lastUpdated: new Date(),
      quality: 0.8,
    },
  };
}

/**
 * Create a question generation input
 * @param {Object} input
 * @returns {Object}
 */
export function createQuestionGenerationInput(input = {}) {
  return {
    retrievalResult: input.retrievalResult || null,
    analysisResult: input.analysisResult || null,
    targetDifficulty: input.targetDifficulty || "medium",
    questionType: input.questionType || QuestionFormats.MULTIPLE_CHOICE,
    learnerProfile: input.learnerProfile || null,
    adaptationRules: input.adaptationRules || {
      minDifficulty: "easy",
      maxDifficulty: "hard",
      difficultyStep: 1,
      consecutiveCorrectToIncrease: 3,
      consecutiveWrongToDecrease: 2,
      topicReinforcement: true,
    },
  };
}

/**
 * Create a generated assessment
 * @param {Object} assessment
 * @returns {Object}
 */
export function createGeneratedAssessment(assessment = {}) {
  return {
    id: assessment.id || `question-${Date.now()}`,
    type: assessment.type || QuestionFormats.MULTIPLE_CHOICE,
    content: assessment.content || "",
    options: assessment.options || null,
    correctAnswer: assessment.correctAnswer || null,
    blanks: assessment.blanks || null,
    hints: assessment.hints || [],
    difficulty: assessment.difficulty || "medium",
    topic: assessment.topic || "",
    subtopic: assessment.subtopic || null,
    conceptsTested: assessment.conceptsTested || [],
    expectedModality: assessment.expectedModality || "text",
    timeLimit: assessment.timeLimit || null,
    points: assessment.points || 10,
    scaffolding: assessment.scaffolding || null,
  };
}

/**
 * Create evaluation criteria
 * @param {Object} criteria
 * @returns {Object}
 */
export function createEvaluationCriteria(criteria = {}) {
  return {
    rubric: criteria.rubric || [],
    keyTerms: criteria.keyTerms || [],
    acceptableVariations: criteria.acceptableVariations || [],
    partialCreditRules: criteria.partialCreditRules || [],
    semanticMatchThreshold: criteria.semanticMatchThreshold || 0.7,
  };
}

/**
 * Create a learner profile
 * @param {Object} profile
 * @returns {Object}
 */
export function createLearnerProfile(profile = {}) {
  return {
    id: profile.id || `learner-${Date.now()}`,
    name: profile.name || "",
    learningStyle: profile.learningStyle || {
      visual: 0.25,
      auditory: 0.25,
      readingWriting: 0.25,
      kinesthetic: 0.25,
    },
    currentLevel: profile.currentLevel || "intermediate",
    strengths: profile.strengths || [],
    weaknesses: profile.weaknesses || [],
    knowledgeGaps: profile.knowledgeGaps || [],
    preferredModality: profile.preferredModality || "text",
    sessionHistory: profile.sessionHistory || [],
    masteryLevels: profile.masteryLevels || [],
  };
}

/**
 * Create a knowledge gap item
 * @param {Object} gap
 * @returns {Object}
 */
export function createKnowledgeGapItem(gap = {}) {
  return {
    id: gap.id || `gap-${Date.now()}`,
    topic: gap.topic || "",
    concept: gap.concept || "",
    severity: gap.severity || SeverityLevels.MEDIUM,
    detectedAt: gap.detectedAt || new Date(),
    attempts: gap.attempts || 0,
    lastAttempt: gap.lastAttempt || new Date(),
    recommendation: gap.recommendation || "",
  };
}

/**
 * Create a topic mastery record
 * @param {Object} mastery
 * @returns {Object}
 */
export function createTopicMastery(mastery = {}) {
  return {
    topicId: mastery.topicId || "",
    topicName: mastery.topicName || "",
    mastery: mastery.mastery || 0,
    confidence: mastery.confidence || 0,
    lastAssessed: mastery.lastAssessed || new Date(),
    trend: mastery.trend || TrendTypes.STABLE,
  };
}

/**
 * Create a feedback input
 * @param {Object} input
 * @returns {Object}
 */
export function createFeedbackInput(input = {}) {
  return {
    question: input.question || null,
    userAnswer: input.userAnswer || null,
    evaluationCriteria: input.evaluationCriteria || null,
    learnerProfile: input.learnerProfile || null,
  };
}

/**
 * Create an answer submission
 * @param {Object} submission
 * @returns {Object}
 */
export function createAnswerSubmission(submission = {}) {
  return {
    id: submission.id || `answer-${Date.now()}`,
    questionId: submission.questionId || "",
    content: submission.content || "",
    modality: submission.modality || InputModalities.TEXT,
    rawData: submission.rawData || null,
    timestamp: submission.timestamp || new Date(),
    timeSpent: submission.timeSpent || 0,
  };
}

/**
 * Create an answer evaluation
 * @param {Object} evaluation
 * @returns {Object}
 */
export function createAnswerEvaluation(evaluation = {}) {
  return {
    isCorrect: evaluation.isCorrect || false,
    score: evaluation.score || 0,
    partialCredit: evaluation.partialCredit || [],
    semanticSimilarity: evaluation.semanticSimilarity || 0,
    keyConceptsCovered: evaluation.keyConceptsCovered || [],
    missingConcepts: evaluation.missingConcepts || [],
    incorrectConcepts: evaluation.incorrectConcepts || [],
  };
}

/**
 * Create personalized feedback
 * @param {Object} feedback
 * @returns {Object}
 */
export function createPersonalizedFeedback(feedback = {}) {
  return {
    summary: feedback.summary || "",
    explanation: feedback.explanation || "",
    strengths: feedback.strengths || [],
    weaknesses: feedback.weaknesses || [],
    misconceptions: feedback.misconceptions || [],
    encouragement: feedback.encouragement || "",
    nextSteps: feedback.nextSteps || [],
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
    suggestedActivities: plan.suggestedActivities || [],
    estimatedTime: plan.estimatedTime || 0,
    priority: plan.priority || SeverityLevels.MEDIUM,
    resources: plan.resources || [],
    milestones: plan.milestones || [],
  };
}

/**
 * Create a profile update recommendation
 * @param {Object} update
 * @returns {Object}
 */
export function createProfileUpdateRecommendation(update = {}) {
  return {
    knowledgeGapsToAdd: update.knowledgeGapsToAdd || [],
    knowledgeGapsToRemove: update.knowledgeGapsToRemove || [],
    masteryUpdates: update.masteryUpdates || [],
    misconceptionsDetected: update.misconceptionsDetected || [],
    strengthsIdentified: update.strengthsIdentified || [],
    weaknessesIdentified: update.weaknessesIdentified || [],
  };
}

/**
 * Create a CrewAI workflow
 * @param {Object} workflow
 * @returns {Object}
 */
export function createCrewAIWorkflow(workflow = {}) {
  return {
    id: workflow.id || `workflow-${Date.now()}`,
    name: workflow.name || "",
    description: workflow.description || "",
    agents: workflow.agents || [],
    tasks: workflow.tasks || [],
    executionOrder: workflow.executionOrder || [],
    status: workflow.status || WorkflowStatuses.PENDING,
  };
}

/**
 * Create a workflow task
 * @param {Object} task
 * @returns {Object}
 */
export function createWorkflowTask(task = {}) {
  return {
    id: task.id || `task-${Date.now()}`,
    name: task.name || "",
    description: task.description || "",
    assignedAgent: task.assignedAgent || AgentRoles.QUERY_ANALYSIS,
    inputs: task.inputs || [],
    outputs: task.outputs || [],
    dependencies: task.dependencies || [],
    status: task.status || TaskStatuses.PENDING,
    result: task.result || null,
    startTime: task.startTime || null,
    endTime: task.endTime || null,
    error: task.error || null,
  };
}

/**
 * Create a workflow execution record
 * @param {Object} execution
 * @returns {Object}
 */
export function createWorkflowExecution(execution = {}) {
  return {
    workflowId: execution.workflowId || "",
    executionId: execution.executionId || `exec-${Date.now()}`,
    startTime: execution.startTime || new Date(),
    endTime: execution.endTime || null,
    status: execution.status || WorkflowStatuses.PENDING,
    taskResults: execution.taskResults || new Map(),
    agentLogs: execution.agentLogs || [],
    metrics: execution.metrics || {
      totalDuration: 0,
      agentDurations: new Map(),
      tokensUsed: 0,
      apiCalls: 0,
      retries: 0,
      errors: 0,
    },
  };
}

/**
 * Create an agent log entry
 * @param {Object} log
 * @returns {Object}
 */
export function createAgentLog(log = {}) {
  return {
    timestamp: log.timestamp || new Date(),
    agentRole: log.agentRole || AgentRoles.QUERY_ANALYSIS,
    action: log.action || "",
    details: log.details || "",
    level: log.level || "info",
  };
}

/**
 * Create a multimodal input
 * @param {Object} input
 * @returns {Object}
 */
export function createMultimodalInput(input = {}) {
  return {
    type: input.type || InputModalities.TEXT,
    content: input.content || "",
    rawData: input.rawData || null,
    metadata: input.metadata || {
      timestamp: new Date(),
      duration: null,
      dimensions: null,
      format: null,
      quality: null,
    },
  };
}

/**
 * Create a normalized input
 * @param {Object} input
 * @returns {Object}
 */
export function createNormalizedInput(input = {}) {
  return {
    originalType: input.originalType || InputModalities.TEXT,
    textContent: input.textContent || "",
    semanticEmbedding: input.semanticEmbedding || [],
    confidence: input.confidence || 0,
    processingSteps: input.processingSteps || [],
  };
}

/**
 * Create a voice processing result
 * @param {Object} result
 * @returns {Object}
 */
export function createVoiceProcessingResult(result = {}) {
  return {
    transcription: result.transcription || "",
    confidence: result.confidence || 0,
    language: result.language || "en",
    segments: result.segments || [],
  };
}

/**
 * Create an OCR result
 * @param {Object} result
 * @returns {Object}
 */
export function createOCRResult(result = {}) {
  return {
    text: result.text || "",
    confidence: result.confidence || 0,
    boundingBoxes: result.boundingBoxes || [],
    recognizedElements: result.recognizedElements || [],
  };
}

/**
 * Create an adaptivity engine state
 * @param {Object} state
 * @returns {Object}
 */
export function createAdaptivityEngine(state = {}) {
  return {
    learnerProfile: state.learnerProfile || null,
    currentDifficulty: state.currentDifficulty || DifficultyLevels.MEDIUM,
    performanceWindow: state.performanceWindow || [],
    adaptationHistory: state.adaptationHistory || [],
  };
}

/**
 * Create an adaptation event
 * @param {Object} event
 * @returns {Object}
 */
export function createAdaptationEvent(event = {}) {
  return {
    timestamp: event.timestamp || new Date(),
    trigger: event.trigger || "performance",
    previousDifficulty: event.previousDifficulty || DifficultyLevels.MEDIUM,
    newDifficulty: event.newDifficulty || DifficultyLevels.MEDIUM,
    reason: event.reason || "",
  };
}

/**
 * Create a difficulty scaling configuration
 * @param {Object} config
 * @returns {Object}
 */
export function createDifficultyScaling(config = {}) {
  return {
    currentLevel: config.currentLevel || 5,
    minLevel: config.minLevel || 1,
    maxLevel: config.maxLevel || 10,
    stepSize: config.stepSize || 1,
    consecutiveCorrect: config.consecutiveCorrect || 0,
    consecutiveWrong: config.consecutiveWrong || 0,
    lastAdjustment: config.lastAdjustment || new Date(),
  };
}

/**
 * Create a personalized learning path
 * @param {Object} path
 * @returns {Object}
 */
export function createPersonalizedPath(path = {}) {
  return {
    learnerId: path.learnerId || "",
    currentPosition: path.currentPosition || null,
    completedNodes: path.completedNodes || [],
    upcomingNodes: path.upcomingNodes || [],
    alternativePaths: path.alternativePaths || [],
    estimatedCompletion: path.estimatedCompletion || null,
  };
}

/**
 * Create a path node
 * @param {Object} node
 * @returns {Object}
 */
export function createPathNode(node = {}) {
  return {
    id: node.id || `node-${Date.now()}`,
    topicId: node.topicId || "",
    conceptId: node.conceptId || "",
    type: node.type || "lesson",
    difficulty: node.difficulty || DifficultyLevels.MEDIUM,
    prerequisites: node.prerequisites || [],
    estimatedDuration: node.estimatedDuration || 30,
    status: node.status || "locked",
  };
}

// ============================================================================
// Default Agent Definitions
// ============================================================================

export const defaultAgents = {
  queryAnalysis: createAgentDefinition({
    id: "agent-query-analysis",
    role: AgentRoles.QUERY_ANALYSIS,
    name: "Query Analysis Agent",
    description: "Entry point of intelligence - analyzes and understands learner queries",
    goal: "Accurately interpret learner intent and extract relevant context",
    backstory: "Expert in natural language understanding and educational context analysis",
    capabilities: [
      "Intent classification using fine-tuned BERT",
      "Entity extraction (topic, subject, difficulty)",
      "Context awareness via session history",
      "Multimodal input processing",
    ],
  }),

  informationRetrieval: createAgentDefinition({
    id: "agent-information-retrieval",
    role: AgentRoles.INFORMATION_RETRIEVAL,
    name: "Information Retrieval Agent",
    description: "Content discovery agent that finds relevant educational materials",
    goal: "Retrieve the most relevant educational content for the query",
    backstory: "Specialist in semantic search and educational content curation",
    capabilities: [
      "Hybrid semantic + keyword retrieval",
      "Sentence embedding generation",
      "Annoy-based vector similarity search",
      "Lightweight re-ranking",
    ],
  }),

  questionGeneration: createAgentDefinition({
    id: "agent-question-generation",
    role: AgentRoles.QUESTION_GENERATION,
    name: "Question Generation Agent",
    description: "Creates adaptive assessments and evaluates responses",
    goal: "Generate personalized, difficulty-aware questions and evaluate answers",
    backstory: "Expert in educational assessment design and adaptive learning",
    capabilities: [
      "Multimodal question generation",
      "Difficulty adaptation",
      "Dual LLM API routing (OpenAI / Gemini)",
      "Response evaluation with semantic analysis",
      "Speech-to-text processing",
      "OCR for diagrams/handwriting",
    ],
  }),

  feedback: createAgentDefinition({
    id: "agent-feedback",
    role: AgentRoles.FEEDBACK,
    name: "Feedback Agent",
    description: "Generates personalized improvement plans and recommendations",
    goal: "Provide actionable feedback and personalized learning paths",
    backstory: "Expert in learning analytics and personalized education",
    capabilities: [
      "Strength and weakness identification",
      "Knowledge gap detection",
      "Actionable feedback generation",
      "Remedial content recommendations",
      "Learning path optimization",
    ],
  }),
};

export default {
  AgentRoles,
  QueryIntents,
  DifficultyLevels,
  QuestionFormats,
  ContentTypes,
  WorkflowStatuses,
  TaskStatuses,
  InputModalities,
  TrendTypes,
  SeverityLevels,
  defaultAgents,
  // Factory functions
  createAgentDefinition,
  createLLMConfig,
  createQueryAnalysisInput,
  createQueryAnalysisOutput,
  createExtractedEntities,
  createSessionContext,
  createPerformancePoint,
  createKnowledgeState,
  createMisconceptionRecord,
  createRetrievalInput,
  createRetrievalOutput,
  createRetrievedContent,
  createQuestionGenerationInput,
  createGeneratedAssessment,
  createEvaluationCriteria,
  createLearnerProfile,
  createKnowledgeGapItem,
  createTopicMastery,
  createFeedbackInput,
  createAnswerSubmission,
  createAnswerEvaluation,
  createPersonalizedFeedback,
  createImprovementPlan,
  createProfileUpdateRecommendation,
  createCrewAIWorkflow,
  createWorkflowTask,
  createWorkflowExecution,
  createAgentLog,
  createMultimodalInput,
  createNormalizedInput,
  createVoiceProcessingResult,
  createOCRResult,
  createAdaptivityEngine,
  createAdaptationEvent,
  createDifficultyScaling,
  createPersonalizedPath,
  createPathNode,
};
