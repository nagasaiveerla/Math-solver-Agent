import React from 'react';
import { Typography, Box } from '@mui/material';

const MathRenderer = ({ content, variant = 'body1', component = 'div' }) => {
  // Enhanced math expression detection and formatting
  const formatMathContent = (text) => {
    if (!text) return text;

    // Replace common mathematical notation for better display
    let formattedText = text
      // Replace common math symbols with Unicode equivalents
      .replace(/\^2/g, '²')
      .replace(/\^3/g, '³')
      .replace(/sqrt\(([^)]+)\)/g, '√($1)')
      .replace(/integral/g, '∫')
      .replace(/sum/g, '∑')
      .replace(/pi/g, 'π')
      .replace(/theta/g, 'θ')
      .replace(/alpha/g, 'α')
      .replace(/beta/g, 'β')
      .replace(/gamma/g, 'γ')
      .replace(/delta/g, 'δ')
      .replace(/infinity/g, '∞')
      .replace(/plus-minus|±/g, '±')
      .replace(/<=|≤/g, '≤')
      .replace(/>=|≥/g, '≥')
      .replace(/!=/g, '≠')
      .replace(/->/g, '→');

    return formattedText;
  };

  const renderContent = () => {
    const formatted = formatMathContent(content);
    
    // Check if content contains mathematical expressions
    const hasMath = /[=+\-*/^∫∑√πθαβγδ²³∞±≤≥≠→]|\b(derivative|integral|solve|equation|formula)\b/i.test(content);
    
    if (hasMath) {
      return (
        <Box 
          component={component}
          sx={{ 
            fontFamily: 'inherit',
            lineHeight: 1.6,
            '& .math-expression': {
              backgroundColor: 'rgba(25, 118, 210, 0.08)',
              padding: '2px 6px',
              borderRadius: '4px',
              fontWeight: 'bold',
              color: '#1976d2',
              fontFamily: 'monospace'
            }
          }}
        >
          {renderMathText(formatted)}
        </Box>
      );
    }

    return (
      <Typography variant={variant} component={component}>
        {formatted}
      </Typography>
    );
  };

  const renderMathText = (text) => {
    // Split text into paragraphs
    const paragraphs = text.split('\n').filter(p => p.trim());
    
    return paragraphs.map((paragraph, pIndex) => (
      <Typography 
        key={pIndex} 
        variant={variant} 
        paragraph={pIndex < paragraphs.length - 1}
        component="div"
      >
        {renderInlineElements(paragraph)}
      </Typography>
    ));
  };

  const renderInlineElements = (text) => {
    // Split by mathematical expressions and render them specially
    const parts = [];
    let lastIndex = 0;
    
    // Regular expression to match mathematical expressions
    const mathRegex = /([a-zA-Z]\s*=\s*[^,\n.]+|[a-zA-Z][²³]?|x\s*[+\-*/=]\s*[^,\n.]+|√\([^)]+\)|∫[^d]*d[a-z]|\d+\s*[+\-*/]\s*\d+)/g;
    let match;
    
    while ((match = mathRegex.exec(text)) !== null) {
      // Add text before the math expression
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }
      
      // Add the math expression with enhanced styling
      parts.push(
        <span 
          key={`math-${match.index}`} 
          className="math-expression"
          style={{ 
            backgroundColor: 'rgba(25, 118, 210, 0.12)',
            padding: '3px 8px',
            borderRadius: '6px',
            fontFamily: '"Cambria Math", "Times New Roman", serif',
            fontSize: '1.1em',
            fontWeight: 'bold',
            color: '#0d47a1',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            letterSpacing: '0.5px'
          }}
        >
          {match[0]}
        </span>
      );
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }
    
    return parts.length > 0 ? parts : text;
  };

  return renderContent();
};

export default MathRenderer;