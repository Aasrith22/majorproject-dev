// Mock API service for EduSynapse
// This simulates the backend API and will be replaced with actual API calls

import type {
  UserProfile,
  LearningSession,
  GeneratedQuestion,
  UserQuery,
  UserAnswer,
  Feedback,
  DashboardData,
  AgentResponse,
  QueryAnalysisResult,
  RetrievalResult,
  Topic,
} from "@/types/api.types";

const API_DELAY = 800; // Simulate network delay

// Helper to simulate async API calls
const simulateDelay = <T>(data: T, delay = API_DELAY): Promise<T> => {
  return new Promise((resolve) => setTimeout(() => resolve(data), delay));
};

// Mock User Profile Data
const mockUserProfile: UserProfile = {
  user: {
    id: "user-1",
    name: "Alex Student",
    email: "alex@edusynapse.com",
    createdAt: new Date("2025-09-01"),
  },
  stats: {
    totalSessions: 45,
    completedSessions: 38,
    inProgressSessions: 7,
    averageScore: 82,
    totalTimeSpent: 2400,
    streakDays: 12,
    questionsAnswered: 234,
    correctAnswers: 189,
  },
  recentTopics: [
    {
      id: "dsa",
      name: "Data Structures & Algorithms",
      subject: "Computer Science",
      progress: 45,
      status: "in-progress",
      score: 78,
      difficulty: "intermediate",
      lastAccessed: new Date("2026-01-05"),
    },
    {
      id: "dbms",
      name: "Database Management Systems",
      subject: "Computer Science",
      progress: 30,
      status: "in-progress",
      score: 72,
      difficulty: "intermediate",
      lastAccessed: new Date("2026-01-04"),
    },
    {
      id: "cn",
      name: "Computer Networks",
      subject: "Computer Science",
      progress: 60,
      status: "in-progress",
      score: 85,
      difficulty: "intermediate",
      lastAccessed: new Date("2026-01-03"),
    },
    {
      id: "oops",
      name: "Object Oriented Programming",
      subject: "Computer Science",
      progress: 85,
      status: "in-progress",
      score: 92,
      difficulty: "beginner",
      lastAccessed: new Date("2026-01-02"),
    },
  ],
  learningPath: {
    currentTopic: {
      id: "dsa",
      name: "Data Structures & Algorithms",
      subject: "Computer Science",
      progress: 45,
      status: "in-progress",
      score: 78,
      difficulty: "intermediate",
    },
    recommendedTopics: [
      {
        id: "os",
        name: "Operating Systems",
        subject: "Computer Science",
        progress: 0,
        status: "not-started",
        difficulty: "advanced",
        description: "Learn about processes, memory, and system calls",
      },
      {
        id: "toc",
        name: "Theory of Computation",
        subject: "Computer Science",
        progress: 0,
        status: "not-started",
        difficulty: "advanced",
        description: "Automata theory and computational complexity",
      },
    ],
    completedTopics: [],
    knowledgeGaps: [
      {
        id: "gap-1",
        topic: "Data Structures & Algorithms",
        concept: "Dynamic Programming",
        severity: "medium",
        recommendation: "Practice more DP problems with memoization",
      },
      {
        id: "gap-2",
        topic: "Database Management Systems",
        concept: "Query Optimization",
        severity: "low",
        recommendation: "Review indexing strategies and execution plans",
      },
    ],
  },
};

// Mock Dashboard Data
const mockDashboardData: DashboardData = {
  performanceHistory: [
    { date: "2025-12-01", score: 72, questionsAttempted: 15, correctAnswers: 11, timeSpent: 45 },
    { date: "2025-12-08", score: 75, questionsAttempted: 18, correctAnswers: 13, timeSpent: 52 },
    { date: "2025-12-15", score: 78, questionsAttempted: 20, correctAnswers: 16, timeSpent: 48 },
    { date: "2025-12-22", score: 80, questionsAttempted: 22, correctAnswers: 18, timeSpent: 55 },
    { date: "2025-12-29", score: 82, questionsAttempted: 25, correctAnswers: 21, timeSpent: 60 },
    { date: "2026-01-05", score: 85, questionsAttempted: 20, correctAnswers: 17, timeSpent: 50 },
  ],
  conceptMastery: [
    { concept: "Data Structures", mastery: 78, trend: "improving", lastAssessed: new Date("2026-01-05") },
    { concept: "Algorithms", mastery: 72, trend: "improving", lastAssessed: new Date("2026-01-04") },
    { concept: "DBMS", mastery: 68, trend: "stable", lastAssessed: new Date("2026-01-03") },
    { concept: "OOP Concepts", mastery: 92, trend: "stable", lastAssessed: new Date("2026-01-02") },
    { concept: "Networking", mastery: 85, trend: "improving", lastAssessed: new Date("2026-01-01") },
  ],
  learningStats: mockUserProfile.stats,
  recentFeedback: [],
  upcomingRecommendations: mockUserProfile.learningPath.recommendedTopics,
};

// Mock Questions - CS Topics
const mockQuestions: GeneratedQuestion[] = [
  {
    id: "q-1",
    type: "multiple-choice",
    content: "What is the time complexity of searching in a balanced Binary Search Tree?",
    options: ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
    correctAnswer: "O(log n)",
    difficulty: "easy",
    topic: "Data Structures & Algorithms",
    expectedModality: "text",
    hints: ["Think about how many levels you traverse", "BST divides the search space in half each time"],
  },
  {
    id: "q-2",
    type: "short-answer",
    content: "Explain the difference between a stack and a queue. Give a real-world example for each.",
    difficulty: "medium",
    topic: "Data Structures & Algorithms",
    expectedModality: "text",
    hints: ["Consider the order of insertion and removal", "Think LIFO vs FIFO"],
  },
  {
    id: "q-3",
    type: "multiple-choice",
    content: "Which normal form eliminates transitive dependencies?",
    options: ["1NF", "2NF", "3NF", "BCNF"],
    correctAnswer: "3NF",
    difficulty: "medium",
    topic: "Database Management Systems",
    expectedModality: "text",
    hints: ["It comes after 2NF", "Transitive dependency is when A→B and B→C implies A→C"],
  },
  {
    id: "q-4",
    type: "short-answer",
    content: "What is the purpose of indexing in databases? Explain how a B+ tree index works.",
    difficulty: "hard",
    topic: "Database Management Systems",
    expectedModality: "text",
    hints: ["Indexing improves query performance", "B+ trees store all data in leaf nodes"],
  },
  {
    id: "q-5",
    type: "multiple-choice",
    content: "Which scheduling algorithm can lead to starvation?",
    options: ["Round Robin", "First Come First Serve", "Shortest Job First", "Multilevel Queue"],
    correctAnswer: "Shortest Job First",
    difficulty: "medium",
    topic: "Operating Systems",
    expectedModality: "text",
    hints: ["Think about what happens to long processes", "Which algorithm prioritizes shorter jobs?"],
  },
  {
    id: "q-6",
    type: "short-answer",
    content: "Explain the concept of virtual memory and how page replacement algorithms work.",
    difficulty: "hard",
    topic: "Operating Systems",
    expectedModality: "text",
    hints: ["Virtual memory extends physical RAM", "Consider LRU, FIFO, and Optimal algorithms"],
  },
  {
    id: "q-7",
    type: "multiple-choice",
    content: "At which layer of the OSI model does the TCP protocol operate?",
    options: ["Network Layer", "Transport Layer", "Session Layer", "Application Layer"],
    correctAnswer: "Transport Layer",
    difficulty: "easy",
    topic: "Computer Networks",
    expectedModality: "text",
    hints: ["TCP provides reliable data transfer", "It's layer 4 of the OSI model"],
  },
  {
    id: "q-8",
    type: "short-answer",
    content: "Explain the four pillars of Object-Oriented Programming with examples.",
    difficulty: "medium",
    topic: "Object Oriented Programming",
    expectedModality: "text",
    hints: ["Encapsulation, Inheritance, Polymorphism, Abstraction", "Use real-world analogies"],
  },
];

// API Functions

export const apiService = {
  // User & Profile
  async getUserProfile(): Promise<UserProfile> {
    return simulateDelay(mockUserProfile);
  },

  async getDashboardData(): Promise<DashboardData> {
    return simulateDelay(mockDashboardData);
  },

  // Topics
  async getTopics(): Promise<Topic[]> {
    return simulateDelay(mockUserProfile.recentTopics);
  },

  async getTopicById(topicId: string): Promise<Topic | undefined> {
    const topic = mockUserProfile.recentTopics.find((t) => t.id === topicId);
    return simulateDelay(topic);
  },

  // Learning Session
  async startSession(topicId: string): Promise<LearningSession> {
    const session: LearningSession = {
      id: `session-${Date.now()}`,
      userId: mockUserProfile.user.id,
      topicId,
      startedAt: new Date(),
      status: "active",
      interactions: [],
    };
    return simulateDelay(session);
  },

  async endSession(sessionId: string): Promise<void> {
    return simulateDelay(undefined, 300);
  },

  // Agent Processing - Simulates the CrewAI workflow
  async processQuery(query: UserQuery): Promise<{
    analysisResult: QueryAnalysisResult;
    retrievalResults: RetrievalResult[];
    agentResponses: AgentResponse[];
  }> {
    // Simulate Query Analysis Agent
    const analysisResult: QueryAnalysisResult = {
      intent: "conceptual",
      entities: {
        subject: "Biology",
        topic: "Photosynthesis",
        difficultyLevel: "intermediate",
      },
      context: query.content,
      confidence: 0.92,
    };

    // Simulate Information Retrieval Agent
    const retrievalResults: RetrievalResult[] = [
      {
        content: "Photosynthesis is the process by which plants convert light energy into chemical energy...",
        source: "Biology Textbook Ch. 8",
        relevanceScore: 0.95,
        type: "semantic",
      },
      {
        content: "The light-dependent reactions occur in the thylakoid membranes...",
        source: "Khan Academy",
        relevanceScore: 0.88,
        type: "hybrid",
      },
    ];

    const agentResponses: AgentResponse[] = [
      { agentType: "query-analysis", status: "completed", processingTime: 150 },
      { agentType: "information-retrieval", status: "completed", processingTime: 320 },
    ];

    return simulateDelay({ analysisResult, retrievalResults, agentResponses }, 1500);
  },

  // Question Generation
  async generateQuestion(topicId: string, difficulty?: string): Promise<GeneratedQuestion> {
    const filteredQuestions = mockQuestions.filter(
      (q) => !difficulty || q.difficulty === difficulty
    );
    const randomQuestion =
      filteredQuestions[Math.floor(Math.random() * filteredQuestions.length)];
    return simulateDelay(randomQuestion, 1200);
  },

  // Submit Answer & Get Feedback
  async submitAnswer(answer: UserAnswer): Promise<Feedback> {
    const feedback: Feedback = {
      id: `feedback-${Date.now()}`,
      questionId: answer.questionId,
      answerId: answer.id,
      isCorrect: Math.random() > 0.3, // 70% chance correct for demo
      score: Math.floor(60 + Math.random() * 40),
      analysis: {
        strengths: [
          "Good understanding of core concepts",
          "Clear logical reasoning in explanation",
        ],
        weaknesses: ["Could provide more specific examples"],
        misconceptions: [],
      },
      explanation:
        "Your answer shows a solid grasp of the fundamental concepts. To strengthen your understanding, try implementing this in code and analyzing the time/space complexity.",
      improvementPlan: {
        id: `plan-${Date.now()}`,
        targetConcepts: ["Time Complexity Analysis", "Space Optimization"],
        suggestedActions: [
          "Practice similar problems on LeetCode",
          "Implement the algorithm from scratch",
          "Analyze edge cases and optimize",
        ],
        estimatedTime: 30,
        priority: "medium",
      },
      resources: [
        {
          id: "res-1",
          title: "Algorithm Visualization",
          type: "video",
          url: "#",
          description: "Interactive visualization of the algorithm",
        },
        {
          id: "res-2",
          title: "Practice Problems",
          type: "exercise",
          url: "#",
          description: "Curated problems to reinforce the concept",
        },
      ],
    };
    return simulateDelay(feedback, 2000);
  },

  // Voice transcription (mock)
  async transcribeVoice(audioBlob: Blob): Promise<string> {
    return simulateDelay(
      "This is a mock transcription of the voice input. In production, this would use a speech-to-text API.",
      1000
    );
  },

  // Drawing/diagram analysis (mock)
  async analyzeDrawing(imageData: string): Promise<string> {
    return simulateDelay(
      "Drawing analysis: The diagram shows a chloroplast with labeled thylakoid membranes and stroma region.",
      1500
    );
  },
};

export default apiService;
