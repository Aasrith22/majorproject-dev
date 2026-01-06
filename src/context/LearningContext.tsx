import {
  createContext,
  useContext,
  useReducer,
  ReactNode,
  useCallback,
} from "react";
import type {
  UserProfile,
  LearningSession,
  GeneratedQuestion,
  Feedback,
  AgentResponse,
  UserQuery,
  InputModality,
} from "@/types/api.types";
import apiService from "@/services/api.service";

// State Types
interface LearningState {
  // User & Profile
  userProfile: UserProfile | null;
  isLoadingProfile: boolean;

  // Current Session
  currentSession: LearningSession | null;
  isSessionActive: boolean;

  // Current Question & Answer Flow
  currentQuestion: GeneratedQuestion | null;
  isGeneratingQuestion: boolean;
  isSubmittingAnswer: boolean;
  currentFeedback: Feedback | null;

  // Agent Processing
  agentResponses: AgentResponse[];
  isProcessingQuery: boolean;

  // Input State
  currentInputModality: InputModality;
  queryHistory: UserQuery[];

  // Error handling
  error: string | null;
}

// Action Types
type LearningAction =
  | { type: "SET_PROFILE"; payload: UserProfile }
  | { type: "SET_LOADING_PROFILE"; payload: boolean }
  | { type: "START_SESSION"; payload: LearningSession }
  | { type: "END_SESSION" }
  | { type: "SET_QUESTION"; payload: GeneratedQuestion }
  | { type: "SET_GENERATING_QUESTION"; payload: boolean }
  | { type: "SET_SUBMITTING_ANSWER"; payload: boolean }
  | { type: "SET_FEEDBACK"; payload: Feedback }
  | { type: "CLEAR_FEEDBACK" }
  | { type: "SET_AGENT_RESPONSES"; payload: AgentResponse[] }
  | { type: "UPDATE_AGENT_STATUS"; payload: AgentResponse }
  | { type: "SET_PROCESSING_QUERY"; payload: boolean }
  | { type: "SET_INPUT_MODALITY"; payload: InputModality }
  | { type: "ADD_QUERY"; payload: UserQuery }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "RESET_QUESTION_STATE" };

// Initial State
const initialState: LearningState = {
  userProfile: null,
  isLoadingProfile: false,
  currentSession: null,
  isSessionActive: false,
  currentQuestion: null,
  isGeneratingQuestion: false,
  isSubmittingAnswer: false,
  currentFeedback: null,
  agentResponses: [],
  isProcessingQuery: false,
  currentInputModality: "text",
  queryHistory: [],
  error: null,
};

// Reducer
function learningReducer(
  state: LearningState,
  action: LearningAction
): LearningState {
  switch (action.type) {
    case "SET_PROFILE":
      return { ...state, userProfile: action.payload, isLoadingProfile: false };
    case "SET_LOADING_PROFILE":
      return { ...state, isLoadingProfile: action.payload };
    case "START_SESSION":
      return {
        ...state,
        currentSession: action.payload,
        isSessionActive: true,
        error: null,
      };
    case "END_SESSION":
      return {
        ...state,
        currentSession: null,
        isSessionActive: false,
        currentQuestion: null,
        currentFeedback: null,
        agentResponses: [],
      };
    case "SET_QUESTION":
      return {
        ...state,
        currentQuestion: action.payload,
        isGeneratingQuestion: false,
        currentFeedback: null,
      };
    case "SET_GENERATING_QUESTION":
      return { ...state, isGeneratingQuestion: action.payload };
    case "SET_SUBMITTING_ANSWER":
      return { ...state, isSubmittingAnswer: action.payload };
    case "SET_FEEDBACK":
      return {
        ...state,
        currentFeedback: action.payload,
        isSubmittingAnswer: false,
      };
    case "CLEAR_FEEDBACK":
      return { ...state, currentFeedback: null };
    case "SET_AGENT_RESPONSES":
      return { ...state, agentResponses: action.payload };
    case "UPDATE_AGENT_STATUS":
      return {
        ...state,
        agentResponses: state.agentResponses.map((r) =>
          r.agentType === action.payload.agentType ? action.payload : r
        ),
      };
    case "SET_PROCESSING_QUERY":
      return { ...state, isProcessingQuery: action.payload };
    case "SET_INPUT_MODALITY":
      return { ...state, currentInputModality: action.payload };
    case "ADD_QUERY":
      return {
        ...state,
        queryHistory: [...state.queryHistory, action.payload],
      };
    case "SET_ERROR":
      return { ...state, error: action.payload };
    case "RESET_QUESTION_STATE":
      return {
        ...state,
        currentQuestion: null,
        currentFeedback: null,
        isGeneratingQuestion: false,
        isSubmittingAnswer: false,
      };
    default:
      return state;
  }
}

// Context Types
interface LearningContextType {
  state: LearningState;
  // Actions
  loadUserProfile: () => Promise<void>;
  startLearningSession: (topicId: string) => Promise<void>;
  endLearningSession: () => Promise<void>;
  processUserQuery: (query: string, modality?: InputModality) => Promise<void>;
  generateQuestion: (difficulty?: string) => Promise<void>;
  submitAnswer: (answer: string, modality?: InputModality) => Promise<void>;
  setInputModality: (modality: InputModality) => void;
  clearError: () => void;
  resetQuestionState: () => void;
}

// Context
const LearningContext = createContext<LearningContextType | undefined>(
  undefined
);

// Provider
interface LearningProviderProps {
  children: ReactNode;
}

export function LearningProvider({ children }: LearningProviderProps) {
  const [state, dispatch] = useReducer(learningReducer, initialState);

  const loadUserProfile = useCallback(async () => {
    dispatch({ type: "SET_LOADING_PROFILE", payload: true });
    try {
      const profile = await apiService.getUserProfile();
      dispatch({ type: "SET_PROFILE", payload: profile });
    } catch (error) {
      dispatch({ type: "SET_ERROR", payload: "Failed to load user profile" });
      dispatch({ type: "SET_LOADING_PROFILE", payload: false });
    }
  }, []);

  const startLearningSession = useCallback(async (topicId: string) => {
    try {
      const session = await apiService.startSession(topicId);
      dispatch({ type: "START_SESSION", payload: session });

      // Initialize agent responses
      dispatch({
        type: "SET_AGENT_RESPONSES",
        payload: [
          { agentType: "query-analysis", status: "pending" },
          { agentType: "information-retrieval", status: "pending" },
          { agentType: "question-generation", status: "pending" },
          { agentType: "feedback", status: "pending" },
        ],
      });
    } catch (error) {
      dispatch({ type: "SET_ERROR", payload: "Failed to start session" });
    }
  }, []);

  const endLearningSession = useCallback(async () => {
    if (state.currentSession) {
      try {
        await apiService.endSession(state.currentSession.id);
        dispatch({ type: "END_SESSION" });
      } catch (error) {
        dispatch({ type: "SET_ERROR", payload: "Failed to end session" });
      }
    }
  }, [state.currentSession]);

  const processUserQuery = useCallback(
    async (query: string, modality: InputModality = "text") => {
      dispatch({ type: "SET_PROCESSING_QUERY", payload: true });

      const userQuery: UserQuery = {
        id: `query-${Date.now()}`,
        modality,
        content: query,
        timestamp: new Date(),
      };

      dispatch({ type: "ADD_QUERY", payload: userQuery });

      // Update agent statuses to show processing
      dispatch({
        type: "UPDATE_AGENT_STATUS",
        payload: { agentType: "query-analysis", status: "processing" },
      });

      try {
        const result = await apiService.processQuery(userQuery);
        dispatch({ type: "SET_AGENT_RESPONSES", payload: result.agentResponses });
        dispatch({ type: "SET_PROCESSING_QUERY", payload: false });
      } catch (error) {
        dispatch({ type: "SET_ERROR", payload: "Failed to process query" });
        dispatch({ type: "SET_PROCESSING_QUERY", payload: false });
      }
    },
    []
  );

  const generateQuestion = useCallback(
    async (difficulty?: string) => {
      if (!state.currentSession) {
        dispatch({ type: "SET_ERROR", payload: "No active session" });
        return;
      }

      dispatch({ type: "SET_GENERATING_QUESTION", payload: true });
      dispatch({
        type: "UPDATE_AGENT_STATUS",
        payload: { agentType: "question-generation", status: "processing" },
      });

      try {
        const question = await apiService.generateQuestion(
          state.currentSession.topicId,
          difficulty
        );
        dispatch({ type: "SET_QUESTION", payload: question });
        dispatch({
          type: "UPDATE_AGENT_STATUS",
          payload: { agentType: "question-generation", status: "completed" },
        });
      } catch (error) {
        dispatch({ type: "SET_ERROR", payload: "Failed to generate question" });
        dispatch({ type: "SET_GENERATING_QUESTION", payload: false });
      }
    },
    [state.currentSession]
  );

  const submitAnswer = useCallback(
    async (answer: string, modality: InputModality = "text") => {
      if (!state.currentQuestion) {
        dispatch({ type: "SET_ERROR", payload: "No question to answer" });
        return;
      }

      dispatch({ type: "SET_SUBMITTING_ANSWER", payload: true });
      dispatch({
        type: "UPDATE_AGENT_STATUS",
        payload: { agentType: "feedback", status: "processing" },
      });

      try {
        const feedback = await apiService.submitAnswer({
          id: `answer-${Date.now()}`,
          questionId: state.currentQuestion.id,
          modality,
          content: answer,
          timestamp: new Date(),
        });
        dispatch({ type: "SET_FEEDBACK", payload: feedback });
        dispatch({
          type: "UPDATE_AGENT_STATUS",
          payload: { agentType: "feedback", status: "completed" },
        });
      } catch (error) {
        dispatch({ type: "SET_ERROR", payload: "Failed to submit answer" });
        dispatch({ type: "SET_SUBMITTING_ANSWER", payload: false });
      }
    },
    [state.currentQuestion]
  );

  const setInputModality = useCallback((modality: InputModality) => {
    dispatch({ type: "SET_INPUT_MODALITY", payload: modality });
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: "SET_ERROR", payload: null });
  }, []);

  const resetQuestionState = useCallback(() => {
    dispatch({ type: "RESET_QUESTION_STATE" });
  }, []);

  const value: LearningContextType = {
    state,
    loadUserProfile,
    startLearningSession,
    endLearningSession,
    processUserQuery,
    generateQuestion,
    submitAnswer,
    setInputModality,
    clearError,
    resetQuestionState,
  };

  return (
    <LearningContext.Provider value={value}>
      {children}
    </LearningContext.Provider>
  );
}

// Hook
export function useLearning() {
  const context = useContext(LearningContext);
  if (context === undefined) {
    throw new Error("useLearning must be used within a LearningProvider");
  }
  return context;
}

export default LearningContext;
