from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any
from app.models.schemas import QueryRequest, FeedbackRequest, QueryResponse
from app.core.guardrails import GuardrailsManager
from app.agents.routing_agent import RoutingAgent
from app.agents.feedback_agent import FeedbackAgent
from app.services.knowledge_base import KnowledgeBaseService
from app.services.web_search import WebSearchService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
guardrails = GuardrailsManager()
routing_agent = RoutingAgent()
feedback_agent = FeedbackAgent()
knowledge_base = KnowledgeBaseService()
web_search = WebSearchService()

@router.post("/query", response_model=QueryResponse)
async def process_math_query(request: QueryRequest):
    """
    Main endpoint to process mathematical queries
    """
    start_time = time.time()
    
    try:
        # Input guardrails
        is_valid, filtered_query, input_metadata = guardrails.process_input(request.query)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=input_metadata.get('error', 'Invalid input')
            )
        
        logger.info(f"Processing query: {filtered_query[:100]}")
        
        # Process through routing agent
        response = await routing_agent.process_query(filtered_query, input_metadata)
        
        # Output guardrails
        is_valid_output, filtered_solution, output_metadata = guardrails.process_output(
            response['solution'], response.get('routing_metadata', {})
        )
        
        if not is_valid_output:
            logger.warning("Output failed guardrails, using filtered version")
        
        response['solution'] = filtered_solution
        response['processing_time'] = time.time() - start_time
        response['input_metadata'] = input_metadata
        response['output_metadata'] = output_metadata
        
        return QueryResponse(**response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "query": request.query,
                "solution": "An error occurred while processing your query. Please try again.",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
        )

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Submit user feedback for a query response
    """
    try:
        # Collect feedback
        feedback_result = feedback_agent.collect_feedback(
            query=request.query,
            response=request.response.dict(),
            feedback_data=request.feedback.dict()
        )
        
        if feedback_result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=feedback_result['error'])
        
        # Process improvements in background
        background_tasks.add_task(process_feedback_improvements, feedback_result)
        
        return {
            "status": "success",
            "feedback_id": feedback_result['feedback_id'],
            "message": "Thank you for your feedback!",
            "improvements_identified": feedback_result.get('improvements_identified', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/analysis")
async def get_feedback_analysis():
    """
    Get comprehensive feedback analysis
    """
    try:
        analysis = feedback_agent.get_feedback_analysis()
        return analysis
    except Exception as e:
        logger.error(f"Error getting feedback analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/metrics")
async def get_satisfaction_metrics():
    """
    Get user satisfaction metrics
    """
    try:
        metrics = feedback_agent.get_user_satisfaction_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting satisfaction metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routing/stats")
async def get_routing_statistics():
    """
    Get routing agent statistics
    """
    try:
        stats = routing_agent.get_routing_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting routing stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """
    Get knowledge base statistics
    """
    try:
        stats = knowledge_base.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/search")
async def search_knowledge_base(request: dict):
    """
    Search the knowledge base directly
    """
    try:
        query = request.get('query', '')
        top_k = request.get('top_k', 5)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        results = knowledge_base.search(query, top_k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web-search")
async def perform_web_search(request: dict):
    """
    Perform web search directly
    """
    try:
        query = request.get('query', '')
        max_results = request.get('max_results', 5)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        results = await web_search.search(query, max_results)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing web search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Check key components
        kb_healthy = knowledge_base.get_stats().get('total_documents', 0) > 0
        feedback_healthy = len(feedback_agent.feedback_storage) >= 0  # Always true, just checking access
        
        return {
            "status": "healthy",
            "components": {
                "knowledge_base": "healthy" if kb_healthy else "degraded",
                "feedback_agent": "healthy" if feedback_healthy else "degraded",
                "routing_agent": "healthy",
                "guardrails": "healthy"
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

@router.get("/system/info")
async def get_system_info():
    """
    Get system information and configuration
    """
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        return {
            "app_name": settings.app_name,
            "features": {
                "knowledge_base": True,
                "web_search": True,
                "human_feedback": True,
                "guardrails": True,
                "routing": True
            },
            "configuration": {
                "max_input_length": settings.max_input_length,
                "confidence_threshold": settings.confidence_threshold,
                "search_results_limit": settings.search_results_limit
            },
            "statistics": {
                "knowledge_base": knowledge_base.get_stats(),
                "routing": routing_agent.get_routing_stats(),
                "feedback": feedback_agent.get_feedback_analysis()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/improvements")
async def apply_improvements():
    """
    Apply improvements based on feedback (admin endpoint)
    """
    try:
        improvements = feedback_agent.apply_feedback_improvements()
        kb_updates = feedback_agent.update_knowledge_base_from_feedback()
        
        return {
            "improvements_applied": improvements,
            "knowledge_base_updates": kb_updates,
            "status": "improvements_processed"
        }
        
    except Exception as e:
        logger.error(f"Error applying improvements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-queries")
async def get_sample_queries():
    """
    Get sample queries for testing the system
    """
    return {
        "knowledge_base_queries": [
            "What is the quadratic formula?",
            "Solve x^2 - 5x + 6 = 0",
            "Find the derivative of x^3 + 2x^2 - 5x + 1",
            "What is the Pythagorean theorem?",
            "How to solve linear equations?"
        ],
        "web_search_queries": [
            "What is the Basel problem in mathematics?",
            "Explain the Riemann hypothesis in simple terms",
            "How to solve differential equations using Laplace transforms?",
            "What are the latest developments in number theory?",
            "Explain Fermat's Last Theorem proof"
        ],
        "computational_queries": [
            "Solve 2x + 5 = 13",
            "Find the derivative of sin(x) * cos(x)",
            "Calculate the integral of x^2 + 3x + 2",
            "Factor x^2 - 9",
            "Simplify (x^2 - 4) / (x - 2)"
        ]
    }

async def process_feedback_improvements(feedback_result: Dict[str, Any]):
    """
    Background task to process feedback improvements
    """
    try:
        logger.info(f"Processing improvements for feedback {feedback_result['feedback_id']}")
        
        # Apply any automated improvements
        improvements = feedback_agent.apply_feedback_improvements()
        
        logger.info(f"Applied {improvements.get('applied_count', 0)} improvements")
        
    except Exception as e:
        logger.error(f"Error processing feedback improvements: {str(e)}")

# Note: APIRouter does not support exception_handler decorators directly.
# Handlers should be registered on the FastAPI app (see app.main).