import {
  createContext,
  useContext,
  useReducer,
  useCallback,
} from "react";
import apiService from "@/services/unified-api.service.js";

// ============================================================================
// State Types & Initial State
// ============================================================================

const initialState = {
  // User & Profile
  userProfile: null,
  isLoadingProfile: false,
  learnerProfile: null,

  // Current Session
  currentSession: null,
  isSessionActive: false,

  // Question Count & Progress
  totalQuestions: 5,
  currentQuestionNumber: 0,
  allFeedback: [],
  isSessionComplete: false,

  // Batch Questions - all questions for the session
  sessionQuestions: [],
  isLoadingQuestions: false,

  // Session Analytics - from feedback agent
  sessionAnalytics: null,

  // Current Question & Answer Flow
  currentQuestion: null,
  isGeneratingQuestion: false,
  isSubmittingAnswer: false,
  currentFeedback: null,

  // Agent Processing
  agentResponses: [],
  isProcessingQuery: false,

  // Input State
  currentInputModality: "text",
  queryHistory: [],

  // Adaptivity State
  adaptivityState: null,
  knowledgeGaps: [],
  masteryLevels: [],

  // Error handling
  error: null,
};

// ============================================================================
// Action Types
// ============================================================================

const ActionTypes = {
  SET_PROFILE: "SET_PROFILE",
  SET_LOADING_PROFILE: "SET_LOADING_PROFILE",
  SET_LEARNER_PROFILE: "SET_LEARNER_PROFILE",
  START_SESSION: "START_SESSION",
  END_SESSION: "END_SESSION",
  SET_SESSION_QUESTIONS: "SET_SESSION_QUESTIONS",
  SET_LOADING_QUESTIONS: "SET_LOADING_QUESTIONS",
  SET_SESSION_ANALYTICS: "SET_SESSION_ANALYTICS",
  SET_QUESTION: "SET_QUESTION",
  ADVANCE_TO_NEXT_QUESTION: "ADVANCE_TO_NEXT_QUESTION",
  SET_GENERATING_QUESTION: "SET_GENERATING_QUESTION",
  SET_SUBMITTING_ANSWER: "SET_SUBMITTING_ANSWER",
  SET_FEEDBACK: "SET_FEEDBACK",
  ADD_FEEDBACK_AND_ADVANCE: "ADD_FEEDBACK_AND_ADVANCE",
  COMPLETE_SESSION: "COMPLETE_SESSION",
  CLEAR_FEEDBACK: "CLEAR_FEEDBACK",
  SET_AGENT_RESPONSES: "SET_AGENT_RESPONSES",
  UPDATE_AGENT_STATUS: "UPDATE_AGENT_STATUS",
  SET_PROCESSING_QUERY: "SET_PROCESSING_QUERY",
  SET_INPUT_MODALITY: "SET_INPUT_MODALITY",
  ADD_QUERY: "ADD_QUERY",
  SET_ERROR: "SET_ERROR",
  RESET_QUESTION_STATE: "RESET_QUESTION_STATE",
  SET_ADAPTIVITY_STATE: "SET_ADAPTIVITY_STATE",
  SET_KNOWLEDGE_GAPS: "SET_KNOWLEDGE_GAPS",
  SET_MASTERY_LEVELS: "SET_MASTERY_LEVELS",
  UPDATE_KNOWLEDGE_GAPS: "UPDATE_KNOWLEDGE_GAPS",
};

// ============================================================================
// Reducer
// ============================================================================

function learningReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_PROFILE:
      return { ...state, userProfile: action.payload, isLoadingProfile: false };
    
    case ActionTypes.SET_LOADING_PROFILE:
      return { ...state, isLoadingProfile: action.payload };
    
    case ActionTypes.SET_LEARNER_PROFILE:
      return { ...state, learnerProfile: action.payload };
    
    case ActionTypes.START_SESSION:
      return {
        ...state,
        currentSession: action.payload.session,
        isSessionActive: true,
        totalQuestions: action.payload.totalQuestions,
        currentQuestionNumber: 0,
        allFeedback: [],
        sessionQuestions: [],
        sessionAnalytics: null,
        isSessionComplete: false,
        error: null,
      };
    
    case ActionTypes.END_SESSION:
      return {
        ...state,
        currentSession: null,
        isSessionActive: false,
        currentQuestion: null,
        currentFeedback: null,
        agentResponses: [],
        totalQuestions: 5,
        currentQuestionNumber: 0,
        allFeedback: [],
        sessionQuestions: [],
        isSessionComplete: false,
      };
    
    case ActionTypes.SET_SESSION_QUESTIONS:
      return {
        ...state,
        sessionQuestions: action.payload,
        isLoadingQuestions: false,
      };
    
    case ActionTypes.SET_LOADING_QUESTIONS:
      return { ...state, isLoadingQuestions: action.payload };
    
    case ActionTypes.SET_SESSION_ANALYTICS:
      return { ...state, sessionAnalytics: action.payload };
    
    case ActionTypes.SET_QUESTION:
      return {
        ...state,
        currentQuestion: action.payload,
        isGeneratingQuestion: false,
        currentFeedback: null,
        currentQuestionNumber: state.currentQuestionNumber + 1,
      };
    
    case ActionTypes.ADVANCE_TO_NEXT_QUESTION:
      // Get next question from sessionQuestions
      const nextIndex = state.currentQuestionNumber;
      const nextQuestion = state.sessionQuestions[nextIndex] || null;
      return {
        ...state,
        currentQuestion: nextQuestion,
        currentFeedback: null,
        currentQuestionNumber: nextQuestion ? state.currentQuestionNumber + 1 : state.currentQuestionNumber,
        isGeneratingQuestion: false,
      };
    
    case ActionTypes.SET_GENERATING_QUESTION:
      return { ...state, isGeneratingQuestion: action.payload };
    
    case ActionTypes.SET_SUBMITTING_ANSWER:
      return { ...state, isSubmittingAnswer: action.payload };
    
    case ActionTypes.SET_FEEDBACK:
      return {
        ...state,
        currentFeedback: action.payload,
        isSubmittingAnswer: false,
      };
    
    case ActionTypes.ADD_FEEDBACK_AND_ADVANCE:
      return {
        ...state,
        allFeedback: [...state.allFeedback, action.payload],
        currentFeedback: null,
        currentQuestion: null,
        isSubmittingAnswer: false,
      };
    
    case ActionTypes.COMPLETE_SESSION:
      return {
        ...state,
        isSessionComplete: true,
        isSubmittingAnswer: false,
      };
    
    case ActionTypes.CLEAR_FEEDBACK:
      return { ...state, currentFeedback: null };
    
    case ActionTypes.SET_AGENT_RESPONSES:
      return { ...state, agentResponses: action.payload };
    
    case ActionTypes.UPDATE_AGENT_STATUS:
      return {
        ...state,
        agentResponses: state.agentResponses.map((r) =>
          r.agentType === action.payload.agentType ? action.payload : r
        ),
      };
    
    case ActionTypes.SET_PROCESSING_QUERY:
      return { ...state, isProcessingQuery: action.payload };
    
    case ActionTypes.SET_INPUT_MODALITY:
      return { ...state, currentInputModality: action.payload };
    
    case ActionTypes.ADD_QUERY:
      return {
        ...state,
        queryHistory: [...state.queryHistory, action.payload],
      };
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload };
    
    case ActionTypes.RESET_QUESTION_STATE:
      return {
        ...state,
        currentQuestion: null,
        currentFeedback: null,
        isGeneratingQuestion: false,
        isSubmittingAnswer: false,
      };
    
    case ActionTypes.SET_ADAPTIVITY_STATE:
      return { ...state, adaptivityState: action.payload };
    
    case ActionTypes.SET_KNOWLEDGE_GAPS:
      return { ...state, knowledgeGaps: action.payload };
    
    case ActionTypes.SET_MASTERY_LEVELS:
      return { ...state, masteryLevels: action.payload };
    
    case ActionTypes.UPDATE_KNOWLEDGE_GAPS:
      return {
        ...state,
        knowledgeGaps: [...state.knowledgeGaps, ...action.payload],
      };
    
    default:
      return state;
  }
}

// ============================================================================
// Context
// ============================================================================

const LearningContext = createContext(undefined);

// ============================================================================
// Provider
// ============================================================================

export function LearningProvider({ children }) {
  const [state, dispatch] = useReducer(learningReducer, initialState);

  // Load user profile
  const loadUserProfile = useCallback(async () => {
    dispatch({ type: ActionTypes.SET_LOADING_PROFILE, payload: true });
    try {
      const profile = await apiService.getUserProfile();
      dispatch({ type: ActionTypes.SET_PROFILE, payload: profile });
      
      // Also load learner profile for adaptive features
      const learnerProfile = await apiService.getLearnerProfile();
      dispatch({ type: ActionTypes.SET_LEARNER_PROFILE, payload: learnerProfile });
      
      // Load knowledge gaps and mastery levels
      const knowledgeGaps = await apiService.getKnowledgeGaps();
      dispatch({ type: ActionTypes.SET_KNOWLEDGE_GAPS, payload: knowledgeGaps });
      
      const masteryLevels = await apiService.getMasteryLevels();
      dispatch({ type: ActionTypes.SET_MASTERY_LEVELS, payload: masteryLevels });
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: "Failed to load user profile" });
      dispatch({ type: ActionTypes.SET_LOADING_PROFILE, payload: false });
    }
  }, []);

  // Start learning session
  const startLearningSession = useCallback(async (topicId, totalQuestions = 5, isCustomTopic = false, testType = 'mcq') => {
    try {
      // If it's a custom topic, topicId is actually the topic name/query
      const topicName = topicId;
      const session = await apiService.startSession(topicId, totalQuestions, testType, topicName, isCustomTopic);
      dispatch({ type: ActionTypes.START_SESSION, payload: { session, totalQuestions } });

      // Initialize agent responses to show batch generation is starting
      dispatch({
        type: ActionTypes.SET_AGENT_RESPONSES,
        payload: [
          { agentType: "query-analysis", status: "processing" },
          { agentType: "information-retrieval", status: "pending" },
          { agentType: "question-generation", status: "pending" },
          { agentType: "feedback", status: "pending" },
        ],
      });
      
      dispatch({ type: ActionTypes.SET_LOADING_QUESTIONS, payload: true });
      
      // Generate all questions at once
      const batchResult = await apiService.generateBatchQuestions(totalQuestions, testType);
      
      dispatch({ type: ActionTypes.SET_SESSION_QUESTIONS, payload: batchResult.questions });
      
      // Update agent statuses from batch result
      if (batchResult.agentStatuses) {
        const statuses = batchResult.agentStatuses;
        dispatch({
          type: ActionTypes.SET_AGENT_RESPONSES,
          payload: [
            { 
              agentType: "query-analysis", 
              status: statuses.query_analysis?.status || "completed",
              processingTime: statuses.query_analysis?.processingTime || 0,
            },
            { 
              agentType: "information-retrieval", 
              status: statuses.information_retrieval?.status || "completed",
              processingTime: statuses.information_retrieval?.processingTime || 0,
            },
            { 
              agentType: "question-generation", 
              status: statuses.question_generation?.status || "completed",
              processingTime: statuses.question_generation?.processingTime || 0,
            },
            { agentType: "feedback", status: "pending" },
          ],
        });
      }
      
      // Load adaptivity state
      const adaptivityState = await apiService.getAdaptivityState();
      dispatch({ type: ActionTypes.SET_ADAPTIVITY_STATE, payload: adaptivityState });
      
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: "Failed to start session" });
      dispatch({ type: ActionTypes.SET_LOADING_QUESTIONS, payload: false });
    }
  }, []);

  // End learning session (called when user clicks "Go Home" or "New Session")
  const endLearningSession = useCallback(async () => {
    if (state.currentSession && !state.isSessionComplete) {
      // Only call API if session wasn't already completed
      try {
        await apiService.endSession(state.currentSession.id);
      } catch (error) {
        console.error("Failed to end session:", error);
      }
    }
    dispatch({ type: ActionTypes.END_SESSION });
  }, [state.currentSession, state.isSessionComplete]);

  // Process user query through CrewAI workflow
  const processUserQuery = useCallback(
    async (query, modality = "text") => {
      dispatch({ type: ActionTypes.SET_PROCESSING_QUERY, payload: true });

      const userQuery = {
        id: `query-${Date.now()}`,
        modality,
        content: query,
        timestamp: new Date(),
      };

      dispatch({ type: ActionTypes.ADD_QUERY, payload: userQuery });

      // Update agent statuses to show processing
      dispatch({
        type: ActionTypes.UPDATE_AGENT_STATUS,
        payload: { agentType: "query-analysis", status: "processing" },
      });

      try {
        // Execute full CrewAI workflow
        const result = await apiService.executeCrewAIWorkflow(
          userQuery,
          state.currentSession?.topicId
        );
        
        dispatch({ type: ActionTypes.SET_AGENT_RESPONSES, payload: [
          { agentType: "query-analysis", status: "completed", processingTime: 150 },
          { agentType: "information-retrieval", status: "completed", processingTime: 320 },
          { agentType: "question-generation", status: "pending" },
          { agentType: "feedback", status: "pending" },
        ]});
        dispatch({ type: ActionTypes.SET_PROCESSING_QUERY, payload: false });
        
        return result;
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: "Failed to process query" });
        dispatch({ type: ActionTypes.SET_PROCESSING_QUERY, payload: false });
      }
    },
    [state.currentSession]
  );

  // Generate question with adaptive difficulty
  const generateQuestion = useCallback(
    async (difficulty, testType) => {
      if (!state.currentSession) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: "No active session" });
        return;
      }

      // If we have pre-loaded questions, use them
      if (state.sessionQuestions.length > 0 && state.currentQuestionNumber < state.sessionQuestions.length) {
        dispatch({ type: ActionTypes.ADVANCE_TO_NEXT_QUESTION });
        return;
      }
      
      // Fallback to generating single question if needed
      dispatch({ type: ActionTypes.SET_GENERATING_QUESTION, payload: true });
      
      // Set all agents to processing initially
      dispatch({
        type: ActionTypes.SET_AGENT_RESPONSES,
        payload: [
          { agentType: "query-analysis", status: "processing" },
          { agentType: "information-retrieval", status: "pending" },
          { agentType: "question-generation", status: "pending" },
          { agentType: "feedback", status: "pending" },
        ],
      });

      try {
        const question = await apiService.generateQuestion(
          state.currentSession.topicId,
          difficulty,
          testType
        );
        
        dispatch({ type: ActionTypes.SET_QUESTION, payload: question });
        
        // Use real agent statuses from backend if available
        if (question.agentStatuses) {
          const statuses = question.agentStatuses;
          dispatch({
            type: ActionTypes.SET_AGENT_RESPONSES,
            payload: [
              { 
                agentType: "query-analysis", 
                status: statuses.query_analysis?.status || "completed",
                processingTime: statuses.query_analysis?.processingTime || 0,
              },
              { 
                agentType: "information-retrieval", 
                status: statuses.information_retrieval?.status || "completed",
                processingTime: statuses.information_retrieval?.processingTime || 0,
              },
              { 
                agentType: "question-generation", 
                status: statuses.question_generation?.status || "completed",
                processingTime: statuses.question_generation?.processingTime || 0,
              },
              { agentType: "feedback", status: "pending" },
            ],
          });
        } else {
          // Fallback if no agent statuses returned
          dispatch({
            type: ActionTypes.SET_AGENT_RESPONSES,
            payload: [
              { agentType: "query-analysis", status: "completed", processingTime: 0 },
              { agentType: "information-retrieval", status: "completed", processingTime: 0 },
              { agentType: "question-generation", status: "completed", processingTime: 0 },
              { agentType: "feedback", status: "pending" },
            ],
          });
        }
        
        // Log if fallback question was used
        if (question.isFallback) {
          console.warn("Fallback question was used - agent pipeline may have failed");
        }
        
        // Update adaptivity state if available
        if (question.adaptiveInfo) {
          dispatch({ type: ActionTypes.SET_ADAPTIVITY_STATE, payload: {
            ...state.adaptivityState,
            currentDifficulty: question.adaptiveInfo.currentDifficulty,
          }});
        }
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: "Failed to generate question" });
        dispatch({ type: ActionTypes.SET_GENERATING_QUESTION, payload: false });
        
        // Mark agents as failed
        dispatch({
          type: ActionTypes.SET_AGENT_RESPONSES,
          payload: [
            { agentType: "query-analysis", status: "failed" },
            { agentType: "information-retrieval", status: "failed" },
            { agentType: "question-generation", status: "failed" },
            { agentType: "feedback", status: "pending" },
          ],
        });
      }
    },
    [state.currentSession, state.adaptivityState, state.sessionQuestions, state.currentQuestionNumber]
  );

  // Submit answer and get adaptive feedback
  const submitAnswer = useCallback(
    async (answer, modality = "text", selectedOptionId = null) => {
      if (!state.currentQuestion) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: "No question to answer" });
        return;
      }

      dispatch({ type: ActionTypes.SET_SUBMITTING_ANSWER, payload: true });
      dispatch({
        type: ActionTypes.UPDATE_AGENT_STATUS,
        payload: { agentType: "feedback", status: "processing" },
      });

      try {
        // For MCQ, selectedOptionId should be the option ID (A, B, C, D)
        // If not provided, try to find the option ID from the answer text
        let optionId = selectedOptionId;
        if (!optionId && state.currentQuestion.type === 'multiple-choice' && state.currentQuestion.options) {
          const matchedOption = state.currentQuestion.options.find(opt => 
            opt.text === answer || opt.id === answer
          );
          optionId = matchedOption?.id || answer;
        }
        
        const feedback = await apiService.submitAnswer({
          id: `answer-${Date.now()}`,
          questionId: state.currentQuestion.id,
          modality,
          content: answer,
          selectedOptionId: optionId,
          timestamp: new Date(),
          topic: state.currentQuestion.topic,
        });
        
        // Update knowledge gaps if detected
        if (feedback.detectedKnowledgeGaps && feedback.detectedKnowledgeGaps.length > 0) {
          dispatch({ type: ActionTypes.UPDATE_KNOWLEDGE_GAPS, payload: feedback.detectedKnowledgeGaps });
        }
        
        // Update adaptivity state
        if (feedback.adaptiveInfo) {
          dispatch({ type: ActionTypes.SET_ADAPTIVITY_STATE, payload: {
            ...state.adaptivityState,
            currentDifficulty: feedback.adaptiveInfo.newDifficulty,
            recentPerformance: feedback.adaptiveInfo.recentPerformance,
          }});
        }
        
        // Store feedback and check if session is complete
        dispatch({ type: ActionTypes.ADD_FEEDBACK_AND_ADVANCE, payload: feedback });
        dispatch({
          type: ActionTypes.UPDATE_AGENT_STATUS,
          payload: { agentType: "feedback", status: "completed" },
        });
        
        // Check if this was the last question
        if (state.currentQuestionNumber >= state.totalQuestions) {
          // End session on backend and get analytics
          try {
            const result = await apiService.endSession(state.currentSession.id);
            
            // Store session analytics from feedback agent
            if (result) {
              dispatch({ 
                type: ActionTypes.SET_SESSION_ANALYTICS, 
                payload: {
                  learning_metrics: result.learning_metrics,
                  difficulty_analysis: result.difficulty_analysis,
                  performance_rating: result.performance_rating,
                  strengths: result.strengths,
                  weaknesses: result.weaknesses,
                  recommendations: result.recommendations,
                  improvement_areas: result.improvement_areas,
                  mastered_concepts: result.mastered_concepts,
                }
              });
            }
          } catch (err) {
            console.error("Failed to get session analytics:", err);
          }
          
          dispatch({ type: ActionTypes.COMPLETE_SESSION });
        }
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: "Failed to submit answer" });
        dispatch({ type: ActionTypes.SET_SUBMITTING_ANSWER, payload: false });
      }
    },
    [state.currentQuestion, state.currentQuestionNumber, state.totalQuestions, state.adaptivityState]
  );

  // Set input modality
  const setInputModality = useCallback((modality) => {
    dispatch({ type: ActionTypes.SET_INPUT_MODALITY, payload: modality });
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    dispatch({ type: ActionTypes.SET_ERROR, payload: null });
  }, []);

  // Reset question state
  const resetQuestionState = useCallback(() => {
    dispatch({ type: ActionTypes.RESET_QUESTION_STATE });
  }, []);

  // Get adaptivity state
  const getAdaptivityState = useCallback(async () => {
    try {
      const adaptivityState = await apiService.getAdaptivityState();
      dispatch({ type: ActionTypes.SET_ADAPTIVITY_STATE, payload: adaptivityState });
      return adaptivityState;
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: "Failed to get adaptivity state" });
    }
  }, []);

  // Update learner profile
  const updateLearnerProfile = useCallback(async (updates) => {
    try {
      const updatedProfile = await apiService.updateLearnerProfile(updates);
      dispatch({ type: ActionTypes.SET_LEARNER_PROFILE, payload: updatedProfile });
      return updatedProfile;
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: "Failed to update learner profile" });
    }
  }, []);

  const value = {
    state,
    // Actions
    loadUserProfile,
    startLearningSession,
    endLearningSession,
    processUserQuery,
    generateQuestion,
    submitAnswer,
    setInputModality,
    clearError,
    resetQuestionState,
    getAdaptivityState,
    updateLearnerProfile,
  };

  return (
    <LearningContext.Provider value={value}>
      {children}
    </LearningContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

export function useLearning() {
  const context = useContext(LearningContext);
  if (context === undefined) {
    throw new Error("useLearning must be used within a LearningProvider");
  }
  return context;
}

export default LearningContext;
