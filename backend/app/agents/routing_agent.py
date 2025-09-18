import logging
from typing import Dict, Any, Tuple, Optional
from enum import Enum
from app.core.config import get_settings
from app.services.knowledge_base import KnowledgeBaseService
from app.services.web_search import WebSearchService
from app.agents.math_solver import MathSolverAgent

logger = logging.getLogger(__name__)
settings = get_settings()

class RouteDecision(Enum):
    KNOWLEDGE_BASE = "knowledge_base"
    WEB_SEARCH = "web_search"
    HYBRID = "hybrid"
    FALLBACK = "fallback"

class RoutingAgent:
    """Main routing agent that decides between knowledge base and web search"""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBaseService()
        self.web_search = WebSearchService()
        self.math_solver = MathSolverAgent()
        self.routing_history = []
    
    def route_query(self, query: str, metadata: Dict[str, Any] = None) -> Tuple[RouteDecision, Dict[str, Any]]:
        """
        Determine the best route for the query
        Returns: (route_decision, routing_metadata)
        """
        if metadata is None:
            metadata = {}
        
        routing_metadata = {
            "query": query,
            "confidence_scores": {},
            "reasoning": "",
            "fallback_used": False
        }
        
        try:
            # Check knowledge base first
            kb_results = self.knowledge_base.search(query, top_k=3)
            kb_confidence = self._calculate_kb_confidence(kb_results, query)
            routing_metadata["confidence_scores"]["knowledge_base"] = kb_confidence
            
            # Determine route based on confidence
            if kb_confidence >= settings.confidence_threshold:
                routing_metadata["reasoning"] = f"High confidence match in knowledge base (score: {kb_confidence:.3f})"
                route = RouteDecision.KNOWLEDGE_BASE
            else:
                # Check if we should use web search
                web_search_score = self._should_use_web_search(query, metadata)
                routing_metadata["confidence_scores"]["web_search"] = web_search_score
                
                if web_search_score >= 0.5:
                    if kb_confidence > 0.3:  # Moderate KB confidence
                        routing_metadata["reasoning"] = "Using hybrid approach - combining KB and web search"
                        route = RouteDecision.HYBRID
                    else:
                        routing_metadata["reasoning"] = f"Using web search due to low KB confidence ({kb_confidence:.3f})"
                        route = RouteDecision.WEB_SEARCH
                else:
                    routing_metadata["reasoning"] = "Using fallback to math solver"
                    routing_metadata["fallback_used"] = True
                    route = RouteDecision.FALLBACK
            
            # Add route_used to routing_metadata
            routing_metadata["route_used"] = route.value
            
            # Log routing decision
            self.routing_history.append({
                "query": query[:100],
                "route": route.value,
                "confidence": routing_metadata["confidence_scores"],
                "reasoning": routing_metadata["reasoning"]
            })
            
            return route, routing_metadata
            
        except Exception as e:
            logger.error(f"Error in routing decision: {str(e)}")
            routing_metadata["reasoning"] = f"Error occurred, using fallback: {str(e)}"
            routing_metadata["fallback_used"] = True
            routing_metadata["route_used"] = RouteDecision.FALLBACK.value
            return RouteDecision.FALLBACK, routing_metadata
    
    def _calculate_kb_confidence(self, results: list, query: str) -> float:
        """Calculate confidence score for knowledge base results"""
        if not results:
            return 0.0
        
        # Get the best score from results
        best_score = max([result.get('score', 0.0) for result in results])
        
        # Adjust score based on query characteristics
        query_lower = query.lower()
        
        # Boost confidence for specific math topics
        topic_boost = 0.0
        math_topics = ['derivative', 'integral', 'quadratic', 'linear', 'equation', 'formula']
        for topic in math_topics:
            if topic in query_lower:
                topic_boost += 0.1
        
        # Boost confidence for computational queries
        if any(word in query_lower for word in ['solve', 'calculate', 'find', 'compute']):
            topic_boost += 0.1
        
        final_confidence = min(best_score + topic_boost, 1.0)
        return final_confidence
    
    def _should_use_web_search(self, query: str, metadata: Dict[str, Any]) -> float:
        """Determine if web search should be used"""
        query_lower = query.lower()
        
        # High priority for web search keywords
        web_search_indicators = [
            'latest', 'recent', 'new', 'current', 'today', '2024', '2025',
            'research', 'paper', 'study', 'theorem', 'conjecture',
            'explain', 'what is', 'definition', 'concept'
        ]
        
        # Topics that likely need web search
        advanced_topics = [
            'riemann', 'fermat', 'basel', 'euler', 'gauss', 'newton',
            'hypothesis', 'conjecture', 'problem', 'paradox'
        ]
        
        score = 0.0
        
        # Check for web search indicators
        for indicator in web_search_indicators:
            if indicator in query_lower:
                score += 0.2
        
        # Check for advanced topics
        for topic in advanced_topics:
            if topic in query_lower:
                score += 0.3
        
        # Check query complexity (longer queries might need web search)
        if len(query.split()) > 10:
            score += 0.2
        
        # Check if it's asking for explanation vs computation
        if any(word in query_lower for word in ['explain', 'what is', 'how does', 'why']):
            score += 0.3
        else:
            score += 0.1  # Computational queries can often use KB
        
        return min(score, 1.0)
    
    async def process_query(self, query: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main method to process a query through the routing system
        Returns: Complete response with solution
        """
        if metadata is None:
            metadata = {}
        
        try:
            # Make routing decision
            route_decision, routing_metadata = self.route_query(query, metadata)
            
            # Add route_used to routing_metadata
            routing_metadata["route_used"] = route_decision.value
            
            response = {
                "query": query,
                "route_used": route_decision.value,
                "routing_metadata": routing_metadata,
                "solution": "",
                "steps": [],
                "sources": [],
                "confidence": 0.0,
                "error": None
            }
            
            # Execute based on route decision
            if route_decision == RouteDecision.KNOWLEDGE_BASE:
                result = await self._process_knowledge_base(query)
                response.update(result)
                
            elif route_decision == RouteDecision.WEB_SEARCH:
                result = await self._process_web_search(query)
                response.update(result)
                
            elif route_decision == RouteDecision.HYBRID:
                kb_result = await self._process_knowledge_base(query)
                web_result = await self._process_web_search(query)
                result = self._combine_results(kb_result, web_result)
                response.update(result)
                
            else:  # FALLBACK
                result = await self._process_fallback(query, metadata)
                response.update(result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "query": query,
                "route_used": "error",
                "routing_metadata": {"route_used": "error"},
                "solution": "An error occurred while processing your query.",
                "steps": [],
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _process_knowledge_base(self, query: str) -> Dict[str, Any]:
        """Process query using knowledge base"""
        try:
            results = self.knowledge_base.search(query, top_k=3)
            if results:
                best_result = results[0]
                solution = await self.math_solver.solve_from_knowledge(best_result, query)
                return {
                    "solution": solution["solution"],
                    "steps": solution["steps"],
                    "sources": [{"type": "knowledge_base", "content": best_result}],
                    "confidence": best_result.get('score', 0.0)
                }
            else:
                return {
                    "solution": "No relevant information found in knowledge base.",
                    "steps": [],
                    "sources": [],
                    "confidence": 0.0
                }
        except Exception as e:
            logger.error(f"Knowledge base processing error: {str(e)}")
            return {
                "solution": f"Error accessing knowledge base: {str(e)}",
                "steps": [],
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _process_web_search(self, query: str) -> Dict[str, Any]:
        """Process query using web search"""
        try:
            results = await self.web_search.search(query)
            if results:
                solution = await self.math_solver.solve_from_web_search(results, query)
                return {
                    "solution": solution["solution"],
                    "steps": solution["steps"],
                    "sources": [{"type": "web_search", "results": results[:3]}],
                    "confidence": solution.get("confidence", 0.5)
                }
            else:
                return {
                    "solution": "No relevant information found through web search.",
                    "steps": [],
                    "sources": [],
                    "confidence": 0.0
                }
        except Exception as e:
            logger.error(f"Web search processing error: {str(e)}")
            return {
                "solution": f"Error during web search: {str(e)}",
                "steps": [],
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _process_fallback(self, query: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process query using fallback math solver"""
        try:
            solution = await self.math_solver.solve_direct(query, metadata)
            return {
                "solution": solution["solution"],
                "steps": solution["steps"],
                "sources": [{"type": "direct_solver", "method": "mathematical_analysis"}],
                "confidence": solution.get("confidence", 0.3)
            }
        except Exception as e:
            logger.error(f"Fallback processing error: {str(e)}")
            return {
                "solution": "I'm having trouble solving this problem. Could you please rephrase your question or provide more context?",
                "steps": ["Unable to process the query with available methods"],
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _combine_results(self, kb_result: Dict[str, Any], web_result: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from knowledge base and web search"""
        combined_solution = f"Based on my knowledge base: {kb_result['solution']}\n\n"
        
        if web_result['solution'] and web_result['solution'] != kb_result['solution']:
            combined_solution += f"Additional information from web search: {web_result['solution']}"
        
        combined_steps = kb_result['steps'] + web_result['steps']
        combined_sources = kb_result['sources'] + web_result['sources']
        
        avg_confidence = (kb_result['confidence'] + web_result['confidence']) / 2
        
        return {
            "solution": combined_solution,
            "steps": combined_steps,
            "sources": combined_sources,
            "confidence": avg_confidence
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about routing decisions"""
        if not self.routing_history:
            return {"total_queries": 0}
        
        route_counts = {}
        avg_confidences = {}
        
        for entry in self.routing_history:
            route = entry["route"]
            route_counts[route] = route_counts.get(route, 0) + 1
            
            if route not in avg_confidences:
                avg_confidences[route] = []
            
            # Get the primary confidence score
            confidence_scores = entry.get("confidence", {})
            if confidence_scores:
                primary_score = list(confidence_scores.values())[0]
                avg_confidences[route].append(primary_score)
        
        # Calculate averages
        for route in avg_confidences:
            if avg_confidences[route]:
                avg_confidences[route] = sum(avg_confidences[route]) / len(avg_confidences[route])
            else:
                avg_confidences[route] = 0.0
        
        return {
            "total_queries": len(self.routing_history),
            "route_distribution": route_counts,
            "average_confidence_by_route": avg_confidences,
            "recent_queries": self.routing_history[-5:] if len(self.routing_history) >= 5 else self.routing_history
        }