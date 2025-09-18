from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class QueryRequest(BaseModel):
    """Request model for mathematical queries"""
    query: str = Field(..., min_length=1, max_length=1000, description="Mathematical question or problem")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the query")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is the quadratic formula?",
                "context": {"difficulty_level": "intermediate"}
            }
        }

class RouteInfo(BaseModel):
    """Information about routing decision"""
    route_used: str = Field(..., description="Route that was used (knowledge_base, web_search, hybrid, fallback)")
    confidence_scores: Dict[str, float] = Field(default={}, description="Confidence scores for different routes")
    reasoning: str = Field(default="", description="Explanation of routing decision")
    fallback_used: bool = Field(default=False, description="Whether fallback was used")

class Source(BaseModel):
    """Source information for solutions"""
    type: str = Field(..., description="Source type (knowledge_base, web_search, direct_solver)")
    content: Optional[Dict[str, Any]] = Field(default=None, description="Source content")
    url: Optional[str] = Field(default=None, description="URL if from web search")
    relevance_score: Optional[float] = Field(default=None, description="Relevance score")

class QueryResponse(BaseModel):
    """Response model for mathematical queries"""
    query: str = Field(..., description="Original query")
    solution: str = Field(..., description="Step-by-step solution")
    steps: List[str] = Field(default=[], description="Individual solution steps")
    route_used: str = Field(..., description="Route that was used")
    routing_metadata: Optional[RouteInfo] = Field(default=None, description="Routing decision information")
    sources: List[Source] = Field(default=[], description="Sources used for the solution")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score for the solution")
    processing_time: Optional[float] = Field(default=None, description="Time taken to process the query")
    error: Optional[str] = Field(default=None, description="Error message if any")
    input_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Input processing metadata")
    output_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Output processing metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is the quadratic formula?",
                "solution": "The quadratic formula is x = (-b ± √(b²-4ac)) / (2a)",
                "steps": [
                    "Step 1: For equations of the form ax² + bx + c = 0",
                    "Step 2: Apply the quadratic formula",
                    "Step 3: x = (-b ± √(b²-4ac)) / (2a)"
                ],
                "route_used": "knowledge_base",
                "confidence": 0.95,
                "processing_time": 0.25
            }
        }

class FeedbackData(BaseModel):
    """User feedback data"""
    rating: int = Field(..., ge=1, le=5, description="User rating from 1-5")
    helpful: bool = Field(default=True, description="Whether the response was helpful")
    correct: bool = Field(default=True, description="Whether the solution is correct")
    clear: bool = Field(default=True, description="Whether the explanation is clear")
    complete: bool = Field(default=True, description="Whether the solution is complete")
    comments: Optional[str] = Field(default="", max_length=1000, description="Additional comments")
    suggested_improvement: Optional[str] = Field(default="", max_length=1000, description="Suggested improvements")
    alternative_solution: Optional[str] = Field(default="", max_length=2000, description="Alternative or corrected solution")
    
    class Config:
        schema_extra = {
            "example": {
                "rating": 4,
                "helpful": True,
                "correct": True,
                "clear": False,
                "complete": True,
                "comments": "The solution is correct but could be explained more clearly",
                "suggested_improvement": "Add more intermediate steps"
            }
        }

class FeedbackRequest(BaseModel):
    """Request model for submitting feedback"""
    query: str = Field(..., description="Original query")
    response: QueryResponse = Field(..., description="The response that was provided")
    feedback: FeedbackData = Field(..., description="User feedback")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is the quadratic formula?",
                "response": {
                    "query": "What is the quadratic formula?",
                    "solution": "The quadratic formula is x = (-b ± √(b²-4ac)) / (2a)",
                    "steps": ["Step 1: Identify quadratic equation", "Step 2: Apply formula"],
                    "route_used": "knowledge_base",
                    "confidence": 0.9
                },
                "feedback": {
                    "rating": 4,
                    "helpful": True,
                    "correct": True,
                    "clear": True,
                    "complete": True,
                    "comments": "Good explanation!"
                }
            }
        }

class KnowledgeBaseQuery(BaseModel):
    """Query model for knowledge base search"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    
class WebSearchQuery(BaseModel):
    """Query model for web search"""
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=10, description="Maximum number of results")

class SystemHealth(BaseModel):
    """System health status"""
    status: str = Field(..., description="Overall system status")
    components: Dict[str, str] = Field(..., description="Status of individual components")
    timestamp: float = Field(..., description="Timestamp of health check")

class FeedbackAnalysis(BaseModel):
    """Feedback analysis response"""
    overview: Dict[str, Any] = Field(..., description="Overview statistics")
    route_performance: Dict[str, Any] = Field(..., description="Performance by route")
    common_issues: Dict[str, Any] = Field(..., description="Common issues identified")
    improvement_priorities: List[Dict[str, Any]] = Field(..., description="Prioritized improvements")
    recent_trends: Dict[str, Any] = Field(..., description="Recent feedback trends")

class RoutingStats(BaseModel):
    """Routing statistics response"""
    total_queries: int = Field(..., description="Total number of queries processed")
    route_distribution: Dict[str, int] = Field(..., description="Distribution of routes used")
    average_confidence_by_route: Dict[str, float] = Field(..., description="Average confidence by route")
    recent_queries: List[Dict[str, Any]] = Field(..., description="Recent query information")

class KnowledgeBaseStats(BaseModel):
    """Knowledge base statistics"""
    total_documents: int = Field(..., description="Total documents in knowledge base")
    topics: Dict[str, int] = Field(..., description="Documents by topic")
    difficulties: Dict[str, int] = Field(..., description="Documents by difficulty")
    has_vector_index: bool = Field(..., description="Whether vector index is available")
    embedding_dimension: Optional[int] = Field(default=None, description="Embedding vector dimension")

class SampleQueries(BaseModel):
    """Sample queries for testing"""
    knowledge_base_queries: List[str] = Field(..., description="Queries that should use knowledge base")
    web_search_queries: List[str] = Field(..., description="Queries that should use web search")
    computational_queries: List[str] = Field(..., description="Queries for direct computation")

class ImprovementSuggestion(BaseModel):
    """Improvement suggestion based on feedback"""
    type: str = Field(..., description="Type of improvement")
    priority: str = Field(..., description="Priority level (low, medium, high, critical)")
    frequency: int = Field(..., description="How often this issue occurs")
    recommended_action: str = Field(..., description="Recommended action to take")

class SystemInfo(BaseModel):
    """System information response"""
    app_name: str = Field(..., description="Application name")
    features: Dict[str, bool] = Field(..., description="Available features")
    configuration: Dict[str, Any] = Field(..., description="System configuration")
    statistics: Dict[str, Any] = Field(..., description="System statistics")

# Enum definitions
class RouteType(str, Enum):
    KNOWLEDGE_BASE = "knowledge_base"
    WEB_SEARCH = "web_search"
    HYBRID = "hybrid"
    FALLBACK = "fallback"
    ERROR = "error"

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComponentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class FeedbackType(str, Enum):
    RATING = "rating"
    CORRECTNESS = "correctness"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    GENERAL = "general"

# Additional utility models
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(default=None, description="Error code")
    timestamp: Optional[float] = Field(default=None, description="Error timestamp")

class SuccessResponse(BaseModel):
    """Standard success response"""
    status: str = Field(default="success", description="Status message")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data")

class ValidationError(BaseModel):
    """Validation error details"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    invalid_value: Optional[Any] = Field(default=None, description="The invalid value")

# Configuration models
class GuardrailsConfig(BaseModel):
    """Guardrails configuration"""
    max_input_length: int = Field(default=1000, description="Maximum input length")
    confidence_threshold: float = Field(default=0.7, description="Confidence threshold for routing")
    allowed_topics: List[str] = Field(default=[], description="Allowed topics")

class SearchConfig(BaseModel):
    """Search configuration"""
    max_results: int = Field(default=5, description="Maximum search results")
    timeout_seconds: int = Field(default=10, description="Search timeout")
    enable_web_search: bool = Field(default=True, description="Enable web search")

# Response wrappers
class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

class MetricsResponse(BaseModel):
    """Metrics response wrapper"""
    metrics: Dict[str, float] = Field(..., description="Metric values")
    period: str = Field(..., description="Time period for metrics")
    last_updated: str = Field(..., description="Last update timestamp")

# Custom validators can be added here if needed
from pydantic import validator

class QueryRequestWithValidation(QueryRequest):
    """Query request with custom validation"""
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        
        # Check for basic mathematical content
        math_indicators = ['=', '+', '-', '*', '/', 'solve', 'calculate', 'find', 'derivative', 'integral']
        if not any(indicator in v.lower() for indicator in math_indicators):
            # This is just a warning, not an error
            pass
            
        return v.strip()
    
    @validator('context')
    def validate_context(cls, v):
        if v is not None and len(v) > 10:  # Limit context keys
            raise ValueError('Context cannot have more than 10 keys')
        return v