import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 400) {
        throw new Error(data.detail || 'Invalid request');
      } else if (status === 500) {
        throw new Error(data.detail || 'Server error occurred');
      } else if (status === 503) {
        throw new Error('Service temporarily unavailable');
      } else {
        throw new Error(data.detail || `HTTP ${status} error`);
      }
    } else if (error.request) {
      // Network error
      throw new Error('Network error - please check your connection');
    } else {
      // Other error
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

export const apiService = {
  // Main query processing
  async processQuery(query, context = null) {
    try {
      const response = await api.post('/query', {
        query,
        context
      });
      return response.data;
    } catch (error) {
      console.error('Error processing query:', error);
      throw error;
    }
  },

  // Submit feedback
  async submitFeedback(feedbackData) {
    try {
      const response = await api.post('/feedback', feedbackData);
      return response.data;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  },

  // Get feedback analysis
  async getFeedbackAnalysis() {
    try {
      const response = await api.get('/feedback/analysis');
      return response.data;
    } catch (error) {
      console.error('Error getting feedback analysis:', error);
      throw error;
    }
  },

  // Get satisfaction metrics
  async getSatisfactionMetrics() {
    try {
      const response = await api.get('/feedback/metrics');
      return response.data;
    } catch (error) {
      console.error('Error getting satisfaction metrics:', error);
      throw error;
    }
  },

  // Get routing statistics
  async getRoutingStats() {
    try {
      const response = await api.get('/routing/stats');
      return response.data;
    } catch (error) {
      console.error('Error getting routing stats:', error);
      throw error;
    }
  },

  // Get knowledge base stats
  async getKnowledgeBaseStats() {
    try {
      const response = await api.get('/knowledge-base/stats');
      return response.data;
    } catch (error) {
      console.error('Error getting knowledge base stats:', error);
      throw error;
    }
  },

  // Search knowledge base directly
  async searchKnowledgeBase(query, topK = 5) {
    try {
      const response = await api.post('/knowledge-base/search', {
        query,
        top_k: topK
      });
      return response.data;
    } catch (error) {
      console.error('Error searching knowledge base:', error);
      throw error;
    }
  },

  // Perform web search directly
  async performWebSearch(query, maxResults = 5) {
    try {
      const response = await api.post('/web-search', {
        query,
        max_results: maxResults
      });
      return response.data;
    } catch (error) {
      console.error('Error performing web search:', error);
      throw error;
    }
  },

  // Health check
  async getHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },

  // Get system information
  async getSystemInfo() {
    try {
      const response = await api.get('/system/info');
      return response.data;
    } catch (error) {
      console.error('Error getting system info:', error);
      throw error;
    }
  },

  // Get sample queries
  async getSampleQueries() {
    try {
      const response = await api.get('/sample-queries');
      return response.data;
    } catch (error) {
      console.error('Error getting sample queries:', error);
      // Return fallback samples
      return {
        knowledge_base_queries: [
          "What is the quadratic formula?",
          "Solve x^2 - 5x + 6 = 0",
          "Find the derivative of x^3 + 2x^2 - 5x + 1",
          "What is the Pythagorean theorem?",
          "How to solve linear equations?"
        ],
        web_search_queries: [
          "What is the Basel problem in mathematics?",
          "Explain the Riemann hypothesis in simple terms",
          "How to solve differential equations using Laplace transforms?",
          "What are the latest developments in number theory?",
          "Explain Fermat's Last Theorem proof"
        ],
        computational_queries: [
          "Solve 2x + 5 = 13",
          "Find the derivative of sin(x) * cos(x)",
          "Calculate the integral of x^2 + 3x + 2",
          "Factor x^2 - 9",
          "Simplify (x^2 - 4) / (x - 2)"
        ]
      };
    }
  },

  // Admin functions
  async applyImprovements() {
    try {
      const response = await api.post('/admin/improvements');
      return response.data;
    } catch (error) {
      console.error('Error applying improvements:', error);
      throw error;
    }
  },

  // Utility functions
  formatError(error) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    } else if (error.message) {
      return error.message;
    } else {
      return 'An unexpected error occurred';
    }
  },

  // Check if API is available
  async checkConnection() {
    try {
      await this.getHealth();
      return true;
    } catch {
      return false;
    }
  },

  // Batch operations
  async batchProcess(queries) {
    const results = [];
    
    for (const query of queries) {
      try {
        const result = await this.processQuery(query);
        results.push({ query, result, success: true });
      } catch (error) {
        results.push({ query, error: error.message, success: false });
      }
    }
    
    return results;
  },

  // Statistics and analytics
  async getAnalytics() {
    try {
      const [
        feedbackAnalysis,
        routingStats, 
        kbStats,
        satisfactionMetrics
      ] = await Promise.all([
        this.getFeedbackAnalysis(),
        this.getRoutingStats(),
        this.getKnowledgeBaseStats(),
        this.getSatisfactionMetrics()
      ]);

      return {
        feedback: feedbackAnalysis,
        routing: routingStats,
        knowledge_base: kbStats,
        satisfaction: satisfactionMetrics
      };
    } catch (error) {
      console.error('Error getting analytics:', error);
      throw error;
    }
  },

  // Helper function to validate queries
  validateQuery(query) {
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string');
    }
    
    if (query.trim().length === 0) {
      throw new Error('Query cannot be empty');
    }
    
    if (query.length > 1000) {
      throw new Error('Query is too long (maximum 1000 characters)');
    }
    
    // Basic math content validation
    const mathIndicators = [
      '=', '+', '-', '*', '/', '^', 
      'solve', 'calculate', 'find', 'derivative', 'integral',
      'equation', 'formula', 'theorem', 'proof'
    ];
    
    const hasMatContent = mathIndicators.some(indicator => 
      query.toLowerCase().includes(indicator)
    );
    
    if (!hasMatContent) {
      console.warn('Query may not contain mathematical content');
    }
    
    return true;
  },

  // Helper function to format responses
  formatResponse(response) {
    if (!response) return null;

    return {
      ...response,
      formatted_solution: this.formatMathText(response.solution),
      formatted_steps: response.steps?.map(step => this.formatMathText(step)) || [],
      confidence_percentage: Math.round((response.confidence || 0) * 100),
      processing_time_formatted: response.processing_time 
        ? `${response.processing_time.toFixed(2)}s` 
        : 'N/A'
    };
  },

  // Helper function to format mathematical text
  formatMathText(text) {
    if (!text) return text;

    return text
      .replace(/\*\*/g, '^')  // Convert ** to ^
      .replace(/sqrt\(/g, '√(')  // Convert sqrt to √
      .replace(/\bpi\b/g, 'π')   // Convert pi to π
      .replace(/infinity/g, '∞')  // Convert infinity to ∞
      .replace(/alpha/g, 'α')     // Convert alpha to α
      .replace(/beta/g, 'β')      // Convert beta to β
      .replace(/gamma/g, 'γ')     // Convert gamma to γ
      .replace(/theta/g, 'θ')     // Convert theta to θ
      .replace(/delta/g, 'δ')     // Convert delta to δ
      .replace(/lambda/g, 'λ')    // Convert lambda to λ
      .replace(/mu/g, 'μ')        // Convert mu to μ
      .replace(/sigma/g, 'σ');    // Convert sigma to σ
  }
};

// Export individual functions for convenience
export const {
  processQuery,
  submitFeedback,
  getFeedbackAnalysis,
  getSatisfactionMetrics,
  getRoutingStats,
  getKnowledgeBaseStats,
  searchKnowledgeBase,
  performWebSearch,
  getHealth,
  getSystemInfo,
  getSampleQueries,
  applyImprovements
} = apiService;

export default apiService;