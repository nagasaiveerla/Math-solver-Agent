import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, AppBar, Toolbar, Fab, Alert, Snackbar } from '@mui/material';
import ScienceIcon from '@mui/icons-material/Science';
import FeedbackIcon from '@mui/icons-material/Feedback';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import ChatInterface from './components/ChatInterface';
import FeedbackModal from './components/FeedbackModal';
import apiService from './services/api';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2e7d32',
    },
    secondary: {
      main: '#0277bd',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [feedbackContext, setFeedbackContext] = useState(null);
  const [pendingFeedback, setPendingFeedback] = useState(0);

  // Check system health on mount
  useEffect(() => {
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await apiService.getHealth();
      setSystemHealth(health);
    } catch (err) {
      console.error('Health check failed:', err);
      setSystemHealth({ status: 'degraded' });
    }
  };

  const handleQuery = async (query) => {
    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);

    const newConversation = {
      id: Date.now(),
      query: query,
      response: null,
      timestamp: new Date(),
      loading: true
    };

    setConversations(prev => [...prev, newConversation]);

    try {
      const response = await apiService.processQuery(query);
      
      setConversations(prev => 
        prev.map(conv => 
          conv.id === newConversation.id 
            ? { ...conv, response, loading: false, needsFeedback: true }
            : conv
        )
      );

      setPendingFeedback(prev => prev + 1);

    } catch (err) {
      console.error('Query error:', err);
      setError(err.message || 'An error occurred while processing your query');
      
      setConversations(prev => 
        prev.map(conv => 
          conv.id === newConversation.id 
            ? { ...conv, loading: false, error: err.message }
            : conv
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (feedbackData) => {
    try {
      await apiService.submitFeedback({
        query: feedbackContext.query,
        response: feedbackContext.response,
        feedback: feedbackData
      });

      // Update conversation to mark feedback as submitted
      setConversations(prev => 
        prev.map(conv => 
          conv.id === feedbackContext.id 
            ? { ...conv, needsFeedback: false, feedbackSubmitted: true }
            : conv
        )
      );

      setPendingFeedback(prev => Math.max(0, prev - 1));
      setSuccess('Thank you for your feedback!');
      setFeedbackModalOpen(false);
      setFeedbackContext(null);

    } catch (err) {
      console.error('Feedback error:', err);
      setError('Failed to submit feedback. Please try again.');
    }
  };

  const handleFeedbackRequest = (conversation) => {
    setFeedbackContext(conversation);
    setFeedbackModalOpen(true);
  };

  const handleClearConversations = () => {
    setConversations([]);
    setPendingFeedback(0);
    setError(null);
    setSuccess(null);
  };

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <ScienceIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Math Routing Agent
          </Typography>
          {systemHealth && (
            <Box sx={{ ml: 2 }}>
              <Typography variant="caption" sx={{ 
                color: systemHealth.status === 'healthy' ? 'lightgreen' : 'orange',
                fontWeight: 'bold'
              }}>
                System: {systemHealth.status}
              </Typography>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom align="center">
            AI-Powered Mathematical Problem Solver
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary">
            Ask any mathematical question and get step-by-step solutions with intelligent routing
          </Typography>
        </Box>

        {/* System Health Warning */}
        {systemHealth && systemHealth.status !== 'healthy' && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            System is running in degraded mode. Some features may not work optimally.
          </Alert>
        )}

        {/* Chat Interface */}
        <ChatInterface 
          conversations={conversations}
          onSubmit={handleQuery}
          onClear={handleClearConversations}
          loading={loading}
          onFeedbackRequest={handleFeedbackRequest}
          getSampleQueries={apiService.getSampleQueries}
        />
      </Container>

      {/* Feedback Button */}
      {pendingFeedback > 0 && (
        <Fab 
          color="secondary" 
          sx={{ position: 'fixed', bottom: 20, right: 20 }}
          onClick={() => {
            // Find first conversation needing feedback
            const needsFeedback = conversations.find(c => c.needsFeedback);
            if (needsFeedback) {
              handleFeedbackRequest(needsFeedback);
            }
          }}
        >
          <FeedbackIcon />
        </Fab>
      )}

      {/* Feedback Modal */}
      <FeedbackModal 
        open={feedbackModalOpen}
        onClose={() => setFeedbackModalOpen(false)}
        onSubmit={handleFeedback}
        conversation={feedbackContext}
      />

      {/* Snackbars */}
      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar 
        open={!!success} 
        autoHideDuration={4000} 
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default App;