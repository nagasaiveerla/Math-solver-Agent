import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  Grid,
  Tooltip,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Send as SendIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  Feedback as FeedbackIcon,
  Timeline as TimelineIcon,
  Search as SearchIcon,
  Storage as StorageIcon,
  Psychology as PsychologyIcon,
  QuestionMark as QuestionMarkIcon
} from '@mui/icons-material';
import MathRenderer from './MathRenderer';

const ChatInterface = ({ 
  conversations, 
  onSubmit, 
  onFeedbackRequest, 
  onClear, 
  loading,
  getSampleQueries 
}) => {
  const [query, setQuery] = useState('');
  const [sampleQueries, setSampleQueries] = useState(null);
  const [sampleMenuAnchor, setSampleMenuAnchor] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations]);

  // Load sample queries on component mount
  useEffect(() => {
    const loadSamples = async () => {
      const samples = await getSampleQueries();
      setSampleQueries(samples);
    };
    loadSamples();
  }, [getSampleQueries]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query);
      setQuery('');
    }
  };

  const handleSampleQuery = (sampleQuery) => {
    setQuery(sampleQuery);
    setSampleMenuAnchor(null);
    // Focus input after setting query
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const getRouteIcon = (route) => {
    switch (route) {
      case 'knowledge_base':
        return <StorageIcon fontSize="small" />;
      case 'web_search':
        return <SearchIcon fontSize="small" />;
      case 'hybrid':
        return <TimelineIcon fontSize="small" />;
      case 'fallback':
        return <PsychologyIcon fontSize="small" />;
      default:
        return <QuestionMarkIcon fontSize="small" />;
    }
  };

  const getRouteColor = (route) => {
    switch (route) {
      case 'knowledge_base':
        return 'primary';
      case 'web_search':
        return 'secondary';
      case 'hybrid':
        return 'warning';
      case 'fallback':
        return 'default';
      default:
        return 'default';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
      {/* Conversation Area */}
      <Paper 
        elevation={1} 
        sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2, 
          mb: 2,
          backgroundColor: '#fafafa'
        }}
      >
        {conversations.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Welcome to Math Routing Agent!
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Ask any mathematical question and get intelligent, step-by-step solutions
            </Typography>
            
            {/* Feature highlights */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <StorageIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="subtitle2">Knowledge Base</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Instant answers from curated math content
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <SearchIcon color="secondary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="subtitle2">Web Search</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Latest mathematical insights from the web
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <FeedbackIcon color="info" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="subtitle2">Human Feedback</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Continuous learning from your input
                  </Typography>
                </Card>
              </Grid>
            </Grid>

            <Button
              variant="outlined"
              startIcon={<QuestionMarkIcon />}
              onClick={(e) => setSampleMenuAnchor(e.currentTarget)}
            >
              Try Sample Questions
            </Button>
          </Box>
        ) : (
          conversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              onFeedbackRequest={onFeedbackRequest}
              getRouteIcon={getRouteIcon}
              getRouteColor={getRouteColor}
              getConfidenceColor={getConfidenceColor}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </Paper>

      {/* Input Area */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            ref={inputRef}
            multiline
            maxRows={3}
            fullWidth
            variant="outlined"
            placeholder="Ask a mathematical question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            helperText={loading ? "Processing your question..." : "Press Enter to submit or Shift+Enter for new line"}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          
          <Tooltip title="Sample Questions">
            <IconButton 
              onClick={(e) => setSampleMenuAnchor(e.currentTarget)}
              disabled={loading}
            >
              <QuestionMarkIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Clear Conversation">
            <IconButton 
              onClick={onClear} 
              disabled={loading || conversations.length === 0}
            >
              <ClearIcon />
            </IconButton>
          </Tooltip>
          
          <Button
            type="submit"
            variant="contained"
            endIcon={<SendIcon />}
            disabled={loading || !query.trim()}
            sx={{ minWidth: '100px' }}
          >
            {loading ? 'Thinking...' : 'Ask'}
          </Button>
        </Box>
        
        {loading && <LinearProgress sx={{ mt: 1 }} />}
      </Paper>

      {/* Sample Queries Menu */}
      <Menu
        anchorEl={sampleMenuAnchor}
        open={Boolean(sampleMenuAnchor)}
        onClose={() => setSampleMenuAnchor(null)}
        PaperProps={{
          style: {
            maxHeight: 400,
            width: '400px',
          },
        }}
      >
        {sampleQueries && Object.entries(sampleQueries).map(([category, queries]) => [
          <MenuItem key={`${category}-header`} disabled>
            <Typography variant="subtitle2" color="primary">
              {category.replace('_', ' ').toUpperCase()}
            </Typography>
          </MenuItem>,
          ...queries.map((query, index) => (
            <MenuItem
              key={`${category}-${index}`}
              onClick={() => handleSampleQuery(query)}
              sx={{ whiteSpace: 'normal', py: 1 }}
            >
              <Typography variant="body2">
                {query}
              </Typography>
            </MenuItem>
          )),
          <Divider key={`${category}-divider`} />
        ])}
      </Menu>
    </Box>
  );
};

// Individual conversation item component
const ConversationItem = ({ 
  conversation, 
  onFeedbackRequest, 
  getRouteIcon, 
  getRouteColor, 
  getConfidenceColor 
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Box sx={{ mb: 3 }}>
      {/* User Query */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Paper 
          elevation={1} 
          sx={{ 
            p: 2, 
            maxWidth: '70%', 
            backgroundColor: 'primary.light',
            color: 'primary.contrastText'
          }}
        >
          <Typography variant="body1">
            {conversation.query}
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.8, display: 'block', mt: 1 }}>
            {conversation.timestamp.toLocaleTimeString()}
          </Typography>
        </Paper>
      </Box>

      {/* System Response */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
        <Paper elevation={1} sx={{ p: 0, maxWidth: '85%', width: '100%' }}>
          {conversation.loading ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Processing your mathematical question...
              </Typography>
            </Box>
          ) : conversation.error ? (
            <Box sx={{ p: 2, backgroundColor: 'error.light', color: 'error.contrastText' }}>
              <Typography variant="body1">
                ❌ {conversation.error}
              </Typography>
            </Box>
          ) : conversation.response ? (
            <Box>
              {/* Response Header */}
              <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Chip
                    icon={getRouteIcon(conversation.response.route_used)}
                    label={conversation.response.route_used.replace('_', ' ')}
                    color={getRouteColor(conversation.response.route_used)}
                    size="small"
                  />
                  <Chip
                    label={`${Math.round(conversation.response.confidence * 100)}% confident`}
                    color={getConfidenceColor(conversation.response.confidence)}
                    size="small"
                    variant="outlined"
                  />
                  {conversation.response.processing_time && (
                    <Chip
                      label={`${conversation.response.processing_time.toFixed(2)}s`}
                      size="small"
                      variant="outlined"
                    />
                  )}
                </Box>
              </Box>

              {/* Main Solution */}
              <CardContent sx={{ 
                padding: '24px',
                background: 'linear-gradient(to right, #f9f9ff, #ffffff)',
                borderRadius: '8px',
                boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.05)'
              }}>
                <Typography 
                  variant="h6" 
                  component="div" 
                  sx={{ 
                    mb: 2, 
                    color: '#0d47a1',
                    fontWeight: 600,
                    borderBottom: '2px solid #e3f2fd',
                    paddingBottom: '8px'
                  }}
                >
                  Solution
                </Typography>
                <MathRenderer content={conversation.response.solution} />
              </CardContent>

              {/* Steps and Details */}
              {(conversation.response.steps?.length > 0 || conversation.response.sources?.length > 0) && (
                <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle2">
                      View Details & Steps
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {conversation.response.steps?.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom sx={{ 
                          color: '#0d47a1',
                          fontWeight: 600,
                          borderBottom: '1px solid #e3f2fd',
                          paddingBottom: '6px'
                        }}>
                          Solution Steps:
                        </Typography>
                        <List dense sx={{ 
                          backgroundColor: '#fafafa',
                          borderRadius: '8px',
                          padding: '12px'
                        }}>
                          {conversation.response.steps.map((step, index) => (
                            <ListItem key={index} sx={{
                              borderLeft: '3px solid #bbdefb',
                              marginBottom: '8px',
                              backgroundColor: 'white',
                              borderRadius: '0 6px 6px 0',
                              boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                            }}>
                              <ListItemText>
                                <MathRenderer content={step} />
                              </ListItemText>
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}

                    {conversation.response.sources?.length > 0 && (
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Sources:
                        </Typography>
                        {conversation.response.sources.map((source, index) => (
                          <Chip
                            key={index}
                            label={source.type}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                    )}
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Feedback Button */}
              {conversation.needsFeedback && (
                <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider', textAlign: 'center' }}>
                  <Button
                    startIcon={<FeedbackIcon />}
                    onClick={() => onFeedbackRequest(conversation)}
                    size="small"
                    variant="outlined"
                  >
                    Provide Feedback
                  </Button>
                </Box>
              )}

              {conversation.feedbackSubmitted && (
                <Box sx={{ p: 1, textAlign: 'center', backgroundColor: 'success.light' }}>
                  <Typography variant="caption" color="success.dark">
                    ✓ Feedback submitted - Thank you!
                  </Typography>
                </Box>
              )}
            </Box>
          ) : null}
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatInterface;