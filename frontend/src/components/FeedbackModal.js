import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Rating,
  FormControlLabel,
  Switch,
  TextField,
  Divider,
  Paper,
  Chip,
  Alert
} from '@mui/material';
import {
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Feedback as FeedbackIcon
} from '@mui/icons-material';
import MathRenderer from './MathRenderer';

const FeedbackModal = ({ open, onClose, onSubmit, conversation }) => {
  const [feedbackData, setFeedbackData] = useState({
    rating: 3,
    helpful: true,
    correct: true,
    clear: true,
    complete: true,
    comments: '',
    suggested_improvement: '',
    alternative_solution: ''
  });

  const [submitting, setSubmitting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      setFeedbackData({
        rating: 3,
        helpful: true,
        correct: true,
        clear: true,
        complete: true,
        comments: '',
        suggested_improvement: '',
        alternative_solution: ''
      });
      setSubmitting(false);
      setShowAdvanced(false);
    }
  }, [open]);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await onSubmit(feedbackData);
      onClose();
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleFieldChange = (field) => (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setFeedbackData(prev => ({ ...prev, [field]: value }));
  };

  const getRatingLabel = (rating) => {
    const labels = {
      1: 'Very Poor',
      2: 'Poor', 
      3: 'Average',
      4: 'Good',
      5: 'Excellent'
    };
    return labels[rating] || '';
  };

  const getRouteDescription = (route) => {
    const descriptions = {
      knowledge_base: 'Used internal knowledge database',
      web_search: 'Searched the web for information',
      hybrid: 'Combined knowledge base and web search',
      fallback: 'Used direct mathematical computation'
    };
    return descriptions[route] || route;
  };

  if (!conversation) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { maxHeight: '90vh' }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FeedbackIcon color="primary" />
          <Typography variant="h6">
            Provide Feedback
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Your feedback helps us improve the mathematical problem-solving experience
        </Typography>
      </DialogTitle>

      <DialogContent dividers sx={{ p: 3 }}>
        {/* Original Query & Response Summary */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Your Question:
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, mb: 2, backgroundColor: 'grey.50' }}>
            <Typography variant="body2">
              {conversation.query}
            </Typography>
          </Paper>

          <Typography variant="subtitle2" gutterBottom>
            Our Response Summary:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Chip 
              label={getRouteDescription(conversation.response?.route_used)}
              size="small"
              color="primary"
              variant="outlined"
            />
            <Chip 
              label={`${Math.round((conversation.response?.confidence || 0) * 100)}% confident`}
              size="small"
              color="secondary"
              variant="outlined"
            />
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Overall Rating */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Overall Rating *
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Rating
              value={feedbackData.rating}
              onChange={(event, newValue) => {
                if (newValue !== null) {
                  setFeedbackData(prev => ({ ...prev, rating: newValue }));
                }
              }}
              size="large"
            />
            <Typography variant="body2" color="text.secondary">
              {getRatingLabel(feedbackData.rating)}
            </Typography>
          </Box>
        </Box>

        {/* Quick Assessment */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Quick Assessment
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={feedbackData.helpful}
                  onChange={handleFieldChange('helpful')}
                  color="primary"
                />
              }
              label="Helpful"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={feedbackData.correct}
                  onChange={handleFieldChange('correct')}
                  color="primary"
                />
              }
              label="Correct"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={feedbackData.clear}
                  onChange={handleFieldChange('clear')}
                  color="primary"
                />
              }
              label="Clear"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={feedbackData.complete}
                  onChange={handleFieldChange('complete')}
                  color="primary"
                />
              }
              label="Complete"
            />
          </Box>
        </Box>

        {/* Comments */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Comments
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            placeholder="Share your thoughts about this response..."
            value={feedbackData.comments}
            onChange={handleFieldChange('comments')}
            variant="outlined"
          />
        </Box>

        {/* Advanced Options */}
        <Box sx={{ mb: 2 }}>
          <Button
            variant="text"
            onClick={() => setShowAdvanced(!showAdvanced)}
            sx={{ mb: showAdvanced ? 2 : 0 }}
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Options
          </Button>

          {showAdvanced && (
            <Box>
              {/* Suggestions for Improvement */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Suggestions for Improvement
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="How could we improve this response?"
                  value={feedbackData.suggested_improvement}
                  onChange={handleFieldChange('suggested_improvement')}
                  variant="outlined"
                />
              </Box>

              {/* Alternative Solution */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Alternative or Corrected Solution
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  If our solution was incorrect or incomplete, please provide the correct approach
                </Alert>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  placeholder="Provide the correct solution or approach..."
                  value={feedbackData.alternative_solution}
                  onChange={handleFieldChange('alternative_solution')}
                  variant="outlined"
                />
              </Box>
            </Box>
          )}
        </Box>

        {/* Feedback Impact Info */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>How your feedback helps:</strong> Your input is used to improve routing decisions, 
            enhance solution quality, and update our knowledge base for better future responses.
          </Typography>
        </Alert>
      </DialogContent>

      <DialogActions sx={{ p: 3, gap: 1 }}>
        <Button 
          onClick={onClose}
          disabled={submitting}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={submitting || feedbackData.rating === 0}
          startIcon={submitting ? null : <ThumbUpIcon />}
        >
          {submitting ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FeedbackModal;