import re
import logging
from typing import Dict, Any, Tuple
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class InputGuardrails:
    """Input validation and filtering guardrails"""
    
    def __init__(self):
        self.math_keywords = [
            "solve", "equation", "formula", "derivative", "integral", "limit",
            "function", "graph", "calculate", "find", "prove", "theorem",
            "algebra", "geometry", "calculus", "trigonometry", "statistics",
            "probability", "matrix", "vector", "polynomial", "logarithm",
            "exponential", "differential", "sum", "product", "factor"
        ]
        
        self.restricted_content = [
            "hack", "exploit", "bypass", "malware", "virus", "attack",
            "personal", "private", "confidential", "password", "credit card",
            "social security", "bank", "account", "political", "religious",
            "inappropriate", "adult", "violent", "illegal"
        ]
    
    def validate_input(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate input query against guardrails
        Returns: (is_valid, filtered_query, metadata)
        """
        metadata = {
            "original_length": len(query),
            "contains_math": False,
            "confidence_score": 0.0,
            "warnings": []
        }
        
        try:
            # Check length
            if len(query) > settings.max_input_length:
                return False, "", {"error": "Query too long"}
            
            # Check for empty or whitespace-only query
            if not query.strip():
                return False, "", {"error": "Empty query"}
            
            # Convert to lowercase for analysis
            query_lower = query.lower()
            
            # Check for restricted content
            for restricted in self.restricted_content:
                if restricted in query_lower:
                    logger.warning(f"Restricted content detected: {restricted}")
                    return False, "", {"error": "Inappropriate content detected"}
            
            # Check for mathematical content
            math_score = 0
            total_words = len(query.split())
            
            for keyword in self.math_keywords:
                if keyword in query_lower:
                    math_score += query_lower.count(keyword)
            
            # Check for mathematical symbols and patterns
            math_patterns = [
                r'\d+',  # Numbers
                r'[x-z]',  # Variables
                r'[+\-*/=<>]',  # Mathematical operators
                r'\\?[a-zA-Z]+\{.*\}',  # LaTeX commands
                r'\^|\_{.*}',  # Powers and subscripts
                r'sin|cos|tan|log|ln|sqrt',  # Math functions
            ]
            
            for pattern in math_patterns:
                if re.search(pattern, query):
                    math_score += len(re.findall(pattern, query))
            
            # Calculate confidence score
            if total_words > 0:
                confidence = min(math_score / total_words, 1.0)
            else:
                confidence = 0.0
            
            metadata["contains_math"] = math_score > 0
            metadata["confidence_score"] = confidence
            
            # Mathematical content validation
            if confidence < 0.1 and not any(keyword in query_lower for keyword in self.math_keywords):
                metadata["warnings"].append("Low mathematical content detected")
                return False, query.strip(), {"error": "Please ask a mathematics-related question"}
            
            # Clean and filter the query
            filtered_query = self._clean_query(query)
            
            return True, filtered_query, metadata
            
        except Exception as e:
            logger.error(f"Error in input validation: {str(e)}")
            return False, "", {"error": "Validation error occurred"}
    
    def _clean_query(self, query: str) -> str:
        """Clean and sanitize the input query"""
        # Remove excessive whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Remove potentially harmful characters while preserving math notation
        # Keep alphanumeric, math symbols, spaces, and common punctuation
        query = re.sub(r'[^\w\s+\-*/=<>(){}[\]^_.,?!:;\\]', '', query)
        
        return query

class OutputGuardrails:
    """Output validation and filtering guardrails"""
    
    def __init__(self):
        self.sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
        ]
    
    def validate_output(self, response: str, metadata: Dict[str, Any] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate output response against guardrails
        Returns: (is_valid, filtered_response, metadata)
        """
        if metadata is None:
            metadata = {}
        
        output_metadata = {
            "original_length": len(response),
            "filtered_length": 0,
            "contains_sensitive_data": False,
            "educational_content": True,
            "warnings": []
        }
        
        try:
            # Check for sensitive information
            for pattern in self.sensitive_patterns:
                if re.search(pattern, response):
                    output_metadata["contains_sensitive_data"] = True
                    output_metadata["warnings"].append("Sensitive data pattern detected")
                    # Mask sensitive information
                    response = re.sub(pattern, "[REDACTED]", response)
            
            # Ensure educational tone
            if not self._is_educational_content(response):
                output_metadata["educational_content"] = False
                output_metadata["warnings"].append("Non-educational content detected")
            
            # Clean response
            filtered_response = self._clean_response(response)
            output_metadata["filtered_length"] = len(filtered_response)
            
            return True, filtered_response, output_metadata
            
        except Exception as e:
            logger.error(f"Error in output validation: {str(e)}")
            return False, "An error occurred while processing the response.", {"error": str(e)}
    
    def _is_educational_content(self, response: str) -> bool:
        """Check if the response contains educational mathematical content"""
        educational_indicators = [
            "step", "solution", "solve", "calculate", "find", "derive",
            "proof", "theorem", "formula", "equation", "answer", "result",
            "method", "approach", "technique", "process", "explanation"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in educational_indicators)
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the output response"""
        # Remove excessive whitespace
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        response = re.sub(r' +', ' ', response)
        
        # Ensure proper formatting for mathematical expressions
        response = response.strip()
        
        return response

class GuardrailsManager:
    """Main guardrails manager"""
    
    def __init__(self):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
    
    def process_input(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Process input through guardrails"""
        return self.input_guardrails.validate_input(query)
    
    def process_output(self, response: str, metadata: Dict[str, Any] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Process output through guardrails"""
        return self.output_guardrails.validate_output(response, metadata)