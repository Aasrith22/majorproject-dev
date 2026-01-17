// Real API service for EduSynapse Backend
// Connects to the FastAPI backend server

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Helper for API calls
const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('edusynapse_token');
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
};

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  async register(email, username, password, fullName) {
    const data = await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password, full_name: fullName }),
    });
    
    if (data.access_token) {
      localStorage.setItem('edusynapse_token', data.access_token);
    }
    
    return data;
  },

  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    
    if (data.access_token) {
      localStorage.setItem('edusynapse_token', data.access_token);
    }
    
    return data;
  },

  async logout() {
    await apiRequest('/auth/logout', { method: 'POST' });
    localStorage.removeItem('edusynapse_token');
  },

  async getProfile() {
    return apiRequest('/auth/me');
  },

  async updateProfile(updates) {
    const params = new URLSearchParams(updates);
    return apiRequest(`/auth/me?${params}`, { method: 'PUT' });
  },

  async updatePreferences(preferences) {
    const params = new URLSearchParams(preferences);
    return apiRequest(`/auth/preferences?${params}`, { method: 'PUT' });
  },

  isAuthenticated() {
    return !!localStorage.getItem('edusynapse_token');
  },
};

// ============================================================================
// Sessions API
// ============================================================================

export const sessionsAPI = {
  async startSession(topicId, topicName, isCustomTopic, customQuery, targetQuestions = 10, assessmentTypes = ['mcq']) {
    return apiRequest('/sessions/start', {
      method: 'POST',
      body: JSON.stringify({
        topic_id: topicId,
        topic_name: topicName,
        is_custom_topic: isCustomTopic,
        custom_query: customQuery,
        target_questions: targetQuestions,
        assessment_types: assessmentTypes,
      }),
    });
  },

  async getSession(sessionId) {
    return apiRequest(`/sessions/${sessionId}`);
  },

  async listSessions(status, limit = 10) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (status) params.append('status', status);
    return apiRequest(`/sessions/?${params}`);
  },

  async submitInput(sessionId, content, inputType = 'text', metadata = null) {
    return apiRequest(`/sessions/${sessionId}/input`, {
      method: 'POST',
      body: JSON.stringify({
        input_type: inputType,
        content,
        metadata,
      }),
    });
  },

  async pauseSession(sessionId) {
    return apiRequest(`/sessions/${sessionId}/pause`, { method: 'POST' });
  },

  async resumeSession(sessionId) {
    return apiRequest(`/sessions/${sessionId}/resume`, { method: 'POST' });
  },

  async endSession(sessionId) {
    return apiRequest(`/sessions/${sessionId}/end`, { method: 'POST' });
  },
};

// ============================================================================
// Assessments API
// ============================================================================

export const assessmentsAPI = {
  async getQuestion(sessionId, preferredType = null, preferredDifficulty = null) {
    return apiRequest('/assessments/question', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        preferred_type: preferredType,
        preferred_difficulty: preferredDifficulty,
      }),
    });
  },

  async getBatchQuestions(sessionId, count = 5, preferredType = null) {
    return apiRequest('/assessments/batch-questions', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        count: count,
        preferred_type: preferredType,
      }),
    });
  },

  async submitAnswer(sessionId, assessmentId, responseContent, responseType = 'text', selectedOptionId = null, timeTakenSeconds = null) {
    return apiRequest('/assessments/submit', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        assessment_id: assessmentId,
        response_type: responseType,
        response_content: responseContent,
        selected_option_id: selectedOptionId,
        time_taken_seconds: timeTakenSeconds,
      }),
    });
  },

  async getFeedback(responseId) {
    return apiRequest(`/assessments/feedback/${responseId}`);
  },

  async getHistory(sessionId) {
    return apiRequest(`/assessments/history/${sessionId}`);
  },
};

// ============================================================================
// Dashboard API
// ============================================================================

export const dashboardAPI = {
  async getProgress() {
    return apiRequest('/dashboard/progress');
  },

  async getAnalytics(period = 'weekly') {
    return apiRequest(`/dashboard/analytics?period=${period}`);
  },

  async getRecommendations() {
    return apiRequest('/dashboard/recommendations');
  },

  async getRecentActivity(limit = 10) {
    return apiRequest(`/dashboard/recent-activity?limit=${limit}`);
  },

  async getAchievements() {
    return apiRequest('/dashboard/achievements');
  },

  async getTopicMastery() {
    return apiRequest('/dashboard/topic-mastery');
  },

  async getAvailableTopics() {
    return apiRequest('/dashboard/available-topics');
  },
};

// ============================================================================
// Agent Orchestration API (for direct testing)
// ============================================================================

export const orchestrationAPI = {
  async execute(input, userId, sessionId, modality = 'text') {
    return apiRequest('/orchestrate', {
      method: 'POST',
      body: JSON.stringify({
        input,
        user_id: userId,
        session_id: sessionId,
        modality,
      }),
    });
  },
};

// ============================================================================
// Health Check
// ============================================================================

export const healthAPI = {
  async check() {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
    
    try {
      const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      return { status: 'unhealthy', error: error.message };
    }
  },
};

// Export all APIs
export const realAPI = {
  auth: authAPI,
  sessions: sessionsAPI,
  assessments: assessmentsAPI,
  dashboard: dashboardAPI,
  orchestration: orchestrationAPI,
  health: healthAPI,
};

export default realAPI;
