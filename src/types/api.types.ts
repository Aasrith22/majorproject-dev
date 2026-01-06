// Types for the EduSynapse API

// User Types
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  createdAt: Date;
}

export interface UserProfile {
  user: User;
  stats: LearningStats;
  recentTopics: Topic[];
  learningPath: LearningPath;
}

export interface LearningStats {
  totalSessions: number;
  completedSessions: number;
  inProgressSessions: number;
  averageScore: number;
  totalTimeSpent: number; // in minutes
  streakDays: number;
  questionsAnswered: number;
  correctAnswers: number;
}

// Topic Types
export interface Topic {
  id: string;
  name: string;
  subject: string;
  description?: string;
  progress: number;
  status: "not-started" | "in-progress" | "completed";
  score?: number;
  lastAccessed?: Date;
  difficulty: "beginner" | "intermediate" | "advanced";
}

export interface LearningPath {
  currentTopic?: Topic;
  recommendedTopics: Topic[];
  completedTopics: Topic[];
  knowledgeGaps: KnowledgeGap[];
}

export interface KnowledgeGap {
  id: string;
  topic: string;
  concept: string;
  severity: "low" | "medium" | "high";
  recommendation: string;
}

// Query & Session Types
export interface LearningSession {
  id: string;
  userId: string;
  topicId: string;
  startedAt: Date;
  endedAt?: Date;
  status: "active" | "completed" | "paused";
  interactions: Interaction[];
}

export interface Interaction {
  id: string;
  timestamp: Date;
  query: UserQuery;
  agentResponses: AgentResponse[];
  question?: GeneratedQuestion;
  userAnswer?: UserAnswer;
  feedback?: Feedback;
}

// Agent Types
export type AgentType =
  | "query-analysis"
  | "information-retrieval"
  | "question-generation"
  | "feedback";

export interface AgentResponse {
  agentType: AgentType;
  status: "pending" | "processing" | "completed" | "error";
  result?: unknown;
  processingTime?: number;
  error?: string;
}

export interface QueryAnalysisResult {
  intent: "definitional" | "conceptual" | "applied" | "follow-up";
  entities: {
    subject?: string;
    topic?: string;
    difficultyLevel?: string;
  };
  context: string;
  confidence: number;
}

export interface RetrievalResult {
  content: string;
  source: string;
  relevanceScore: number;
  type: "semantic" | "keyword" | "hybrid";
}

// Question Types
export type QuestionType =
  | "multiple-choice"
  | "short-answer"
  | "essay"
  | "diagram"
  | "voice";

export interface GeneratedQuestion {
  id: string;
  type: QuestionType;
  content: string;
  options?: string[]; // For multiple choice
  correctAnswer?: string;
  hints?: string[];
  difficulty: "easy" | "medium" | "hard";
  topic: string;
  expectedModality: "text" | "voice" | "drawing" | "multimodal";
}

// Input Types
export type InputModality = "text" | "voice" | "drawing";

export interface UserQuery {
  id: string;
  modality: InputModality;
  content: string; // Text content or transcription
  rawData?: string; // Base64 for voice/drawing
  timestamp: Date;
}

export interface UserAnswer {
  id: string;
  questionId: string;
  modality: InputModality;
  content: string;
  rawData?: string;
  timestamp: Date;
}

// Feedback Types
export interface Feedback {
  id: string;
  questionId: string;
  answerId: string;
  isCorrect: boolean;
  score: number; // 0-100
  analysis: {
    strengths: string[];
    weaknesses: string[];
    misconceptions: string[];
  };
  explanation: string;
  improvementPlan: ImprovementPlan;
  resources?: Resource[];
}

export interface ImprovementPlan {
  id: string;
  targetConcepts: string[];
  suggestedActions: string[];
  estimatedTime: number; // in minutes
  priority: "low" | "medium" | "high";
}

export interface Resource {
  id: string;
  title: string;
  type: "article" | "video" | "exercise" | "diagram";
  url?: string;
  description: string;
}

// Analytics Types
export interface PerformanceMetric {
  date: string;
  score: number;
  questionsAttempted: number;
  correctAnswers: number;
  timeSpent: number;
}

export interface ConceptMastery {
  concept: string;
  mastery: number; // 0-100
  trend: "improving" | "stable" | "declining";
  lastAssessed: Date;
}

export interface DashboardData {
  performanceHistory: PerformanceMetric[];
  conceptMastery: ConceptMastery[];
  learningStats: LearningStats;
  recentFeedback: Feedback[];
  upcomingRecommendations: Topic[];
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
