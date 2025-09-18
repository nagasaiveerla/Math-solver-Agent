import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from collections import defaultdict
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class FeedbackAgent:
    """Human-in-the-loop feedback agent for continuous improvement"""
    
    def __init__(self):
        self.feedback_storage = {}
        self.feedback_stats = defaultdict(int)
        self.improvement_suggestions = []
        self._load_feedback_data()
    
    def _load_feedback_data(self):
        """Load existing feedback data from storage"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(settings.feedback_data_path), exist_ok=True)
            
            if os.path.exists(settings.feedback_data_path):
                with open(settings.feedback_data_path, 'r') as f:
                    data = json.load(f)
                    self.feedback_storage = data.get('feedback', {})
                    self.feedback_stats = defaultdict(int, data.get('stats', {}))
                    self.improvement_suggestions = data.get('suggestions', [])
                logger.info(f"Loaded {len(self.feedback_storage)} feedback entries")
            else:
                logger.info("No existing feedback data found, starting fresh")
                self._save_feedback_data()
        except Exception as e:
            logger.error(f"Error loading feedback data: {str(e)}")
            self.feedback_storage = {}
            self.feedback_stats = defaultdict(int)
            self.improvement_suggestions = []
    
    def collect_feedback(self, query: str, response: Dict[str, Any], feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect and process user feedback
        
        Args:
            query: Original user query
            response: System response that was provided
            feedback_data: User feedback including rating, comments, corrections
        
        Returns:
            Dictionary with feedback processing results
        """
        try:
            feedback_id = self._generate_feedback_id()
            
            # Structure feedback entry
            feedback_entry = {
                "id": feedback_id,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": {
                    "solution": response.get('solution', ''),
                    "steps": response.get('steps', []),
                    "route_used": response.get('route_used', ''),
                    "confidence": response.get('confidence', 0.0)
                },
                "feedback": {
                    "rating": feedback_data.get('rating', 0),  # 1-5 scale
                    "helpful": feedback_data.get('helpful', False),
                    "correct": feedback_data.get('correct', True),
                    "clear": feedback_data.get('clear', True),
                    "complete": feedback_data.get('complete', True),
                    "comments": feedback_data.get('comments', ''),
                    "suggested_improvement": feedback_data.get('suggested_improvement', ''),
                    "alternative_solution": feedback_data.get('alternative_solution', '')
                },
                "metadata": {
                    "response_time": response.get('processing_time', 0),
                    "route_confidence": response.get('routing_metadata', {}).get('confidence_scores', {}),
                    "user_satisfaction": feedback_data.get('rating', 0)
                }
            }
            
            # Store feedback
            self.feedback_storage[feedback_id] = feedback_entry
            
            # Update statistics
            self._update_feedback_stats(feedback_entry)
            
            # Process feedback for improvements
            improvements = self._process_feedback_for_improvements(feedback_entry)
            
            # Save data
            self._save_feedback_data()
            
            return {
                "feedback_id": feedback_id,
                "status": "collected",
                "improvements_identified": len(improvements),
                "suggestions": improvements
            }
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_feedback_id(self) -> str:
        """Generate unique feedback ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        counter = len(self.feedback_storage) + 1
        return f"feedback_{timestamp}_{counter:04d}"
    
    def _update_feedback_stats(self, feedback_entry: Dict[str, Any]):
        """Update feedback statistics"""
        feedback = feedback_entry['feedback']
        route = feedback_entry['response']['route_used']
        
        # Overall stats
        self.feedback_stats['total_feedback'] += 1
        self.feedback_stats[f'rating_{feedback["rating"]}'] += 1
        
        # Route-specific stats
        self.feedback_stats[f'route_{route}_total'] += 1
        if feedback['helpful']:
            self.feedback_stats[f'route_{route}_helpful'] += 1
        if feedback['correct']:
            self.feedback_stats[f'route_{route}_correct'] += 1
        
        # Quality metrics
        if feedback['rating'] >= 4:
            self.feedback_stats['high_satisfaction'] += 1
        elif feedback['rating'] <= 2:
            self.feedback_stats['low_satisfaction'] += 1
        
        # Common issues
        if not feedback['clear']:
            self.feedback_stats['clarity_issues'] += 1
        if not feedback['complete']:
            self.feedback_stats['completeness_issues'] += 1
    
    def _process_feedback_for_improvements(self, feedback_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process feedback to identify improvement opportunities"""
        improvements = []
        feedback = feedback_entry['feedback']
        response = feedback_entry['response']
        
        # Low rating analysis
        if feedback['rating'] <= 2:
            improvements.append({
                "type": "low_satisfaction",
                "route": response['route_used'],
                "issue": "User gave low rating",
                "suggestion": "Review solution quality and approach",
                "priority": "high"
            })
        
        # Correctness issues
        if not feedback['correct']:
            improvements.append({
                "type": "correctness",
                "route": response['route_used'],
                "issue": "Solution marked as incorrect",
                "suggestion": "Verify computational accuracy and logic",
                "priority": "critical",
                "user_correction": feedback.get('alternative_solution', '')
            })
        
        # Clarity issues
        if not feedback['clear']:
            improvements.append({
                "type": "clarity",
                "route": response['route_used'],
                "issue": "Solution not clear to user",
                "suggestion": "Improve explanation and step-by-step breakdown",
                "priority": "medium"
            })
        
        # Completeness issues
        if not feedback['complete']:
            improvements.append({
                "type": "completeness",
                "route": response['route_used'],
                "issue": "Solution incomplete",
                "suggestion": "Provide more comprehensive solution steps",
                "priority": "medium"
            })
        
        # Low confidence with negative feedback
        if response['confidence'] < 0.5 and feedback['rating'] <= 3:
            improvements.append({
                "type": "confidence_accuracy",
                "route": response['route_used'],
                "issue": "Low confidence correlated with poor user experience",
                "suggestion": "Improve routing decision accuracy",
                "priority": "high"
            })
        
        # Store improvements for later analysis
        self.improvement_suggestions.extend(improvements)
        
        return improvements
    
    def get_feedback_analysis(self) -> Dict[str, Any]:
        """Get comprehensive feedback analysis"""
        try:
            total_feedback = self.feedback_stats['total_feedback']
            if total_feedback == 0:
                return {"message": "No feedback data available yet"}
            
            # Calculate averages and trends
            avg_rating = self._calculate_average_rating()
            route_performance = self._analyze_route_performance()
            improvement_priorities = self._prioritize_improvements()
            
            return {
                "overview": {
                    "total_feedback_entries": total_feedback,
                    "average_rating": avg_rating,
                    "high_satisfaction_rate": self.feedback_stats['high_satisfaction'] / total_feedback,
                    "low_satisfaction_rate": self.feedback_stats['low_satisfaction'] / total_feedback
                },
                "route_performance": route_performance,
                "common_issues": {
                    "clarity_rate": self.feedback_stats['clarity_issues'] / total_feedback,
                    "completeness_rate": self.feedback_stats['completeness_issues'] / total_feedback
                },
                "improvement_priorities": improvement_priorities,
                "recent_trends": self._analyze_recent_trends()
            }
            
        except Exception as e:
            logger.error(f"Error generating feedback analysis: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_average_rating(self) -> float:
        """Calculate average user rating"""
        total_ratings = 0
        total_count = 0
        
        for i in range(1, 6):
            count = self.feedback_stats[f'rating_{i}']
            total_ratings += i * count
            total_count += count
        
        return total_ratings / total_count if total_count > 0 else 0.0
    
    def _analyze_route_performance(self) -> Dict[str, Any]:
        """Analyze performance by routing method"""
        routes = ['knowledge_base', 'web_search', 'hybrid', 'fallback']
        performance = {}
        
        for route in routes:
            total = self.feedback_stats[f'route_{route}_total']
            if total > 0:
                helpful = self.feedback_stats[f'route_{route}_helpful']
                correct = self.feedback_stats[f'route_{route}_correct']
                
                performance[route] = {
                    "total_usage": total,
                    "helpful_rate": helpful / total,
                    "correct_rate": correct / total,
                    "effectiveness_score": (helpful + correct) / (2 * total)
                }
        
        return performance
    
    def _prioritize_improvements(self) -> List[Dict[str, Any]]:
        """Prioritize improvement suggestions"""
        # Group improvements by type and priority
        priority_groups = defaultdict(list)
        
        for improvement in self.improvement_suggestions:
            priority = improvement.get('priority', 'medium')
            priority_groups[priority].append(improvement)
        
        # Sort by priority and frequency
        prioritized = []
        for priority in ['critical', 'high', 'medium', 'low']:
            items = priority_groups[priority]
            # Group by type to show frequency
            type_counts = defaultdict(int)
            for item in items:
                type_counts[item['type']] += 1
            
            for improvement_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                prioritized.append({
                    "type": improvement_type,
                    "priority": priority,
                    "frequency": count,
                    "recommended_action": self._get_recommended_action(improvement_type)
                })
        
        return prioritized[:10]  # Top 10 priorities
    
    def _get_recommended_action(self, improvement_type: str) -> str:
        """Get recommended action for improvement type"""
        actions = {
            "correctness": "Review mathematical computation logic and verify solutions against known answers",
            "clarity": "Improve step-by-step explanations and use simpler language",
            "completeness": "Ensure all solution steps are included and properly explained",
            "low_satisfaction": "Conduct detailed review of user experience and solution quality",
            "confidence_accuracy": "Calibrate routing confidence scores and improve decision thresholds"
        }
        
        return actions.get(improvement_type, "Investigate specific issues and implement targeted improvements")
    
    def _analyze_recent_trends(self) -> Dict[str, Any]:
        """Analyze recent feedback trends"""
        # Get recent feedback (last 20 entries)
        recent_feedback = list(self.feedback_storage.values())[-20:]
        
        if not recent_feedback:
            return {"message": "No recent feedback available"}
        
        recent_ratings = [f['feedback']['rating'] for f in recent_feedback]
        recent_avg = sum(recent_ratings) / len(recent_ratings)
        
        # Compare with overall average
        overall_avg = self._calculate_average_rating()
        trend = "improving" if recent_avg > overall_avg else "declining" if recent_avg < overall_avg else "stable"
        
        return {
            "recent_average_rating": recent_avg,
            "overall_average_rating": overall_avg,
            "trend": trend,
            "recent_feedback_count": len(recent_feedback)
        }
    
    def apply_feedback_improvements(self) -> Dict[str, Any]:
        """Apply improvements based on collected feedback"""
        try:
            improvements_applied = []
            
            # Analyze improvement priorities
            priorities = self._prioritize_improvements()
            
            for priority_item in priorities[:5]:  # Apply top 5 improvements
                improvement_type = priority_item['type']
                
                if improvement_type == "confidence_accuracy":
                    # Suggest confidence threshold adjustments
                    improvements_applied.append({
                        "type": "confidence_threshold",
                        "action": "Adjust routing confidence thresholds",
                        "recommendation": "Lower threshold for knowledge base routing to 0.6"
                    })
                
                elif improvement_type == "clarity":
                    # Suggest explanation improvements
                    improvements_applied.append({
                        "type": "explanation_enhancement",
                        "action": "Enhance step-by-step explanations",
                        "recommendation": "Add more detailed intermediate steps"
                    })
                
                elif improvement_type == "completeness":
                    # Suggest solution completeness improvements
                    improvements_applied.append({
                        "type": "solution_completeness",
                        "action": "Ensure complete solutions",
                        "recommendation": "Add verification steps to all solutions"
                    })
            
            return {
                "status": "improvements_identified",
                "applied_count": len(improvements_applied),
                "improvements": improvements_applied
            }
            
        except Exception as e:
            logger.error(f"Error applying feedback improvements: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def get_feedback_by_id(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get specific feedback entry by ID"""
        return self.feedback_storage.get(feedback_id)
    
    def get_feedback_by_query(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get feedback entries for similar queries"""
        matching_feedback = []
        query_lower = query.lower()
        
        for feedback_entry in self.feedback_storage.values():
            if query_lower in feedback_entry['query'].lower():
                matching_feedback.append(feedback_entry)
        
        # Sort by timestamp (most recent first)
        matching_feedback.sort(key=lambda x: x['timestamp'], reverse=True)
        return matching_feedback[:limit]
    
    def update_knowledge_base_from_feedback(self) -> Dict[str, Any]:
        """Generate knowledge base updates based on feedback"""
        try:
            updates = []
            
            # Find feedback with corrections or alternative solutions
            for feedback_entry in self.feedback_storage.values():
                feedback = feedback_entry['feedback']
                
                if feedback.get('alternative_solution') and not feedback['correct']:
                    updates.append({
                        "type": "correction",
                        "original_query": feedback_entry['query'],
                        "incorrect_solution": feedback_entry['response']['solution'],
                        "corrected_solution": feedback['alternative_solution'],
                        "user_comments": feedback['comments']
                    })
                
                elif feedback.get('suggested_improvement'):
                    updates.append({
                        "type": "improvement",
                        "query": feedback_entry['query'],
                        "current_solution": feedback_entry['response']['solution'],
                        "suggested_improvement": feedback['suggested_improvement']
                    })
            
            return {
                "potential_updates": len(updates),
                "updates": updates[:10],  # Return top 10
                "status": "updates_identified"
            }
            
        except Exception as e:
            logger.error(f"Error generating KB updates from feedback: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def get_user_satisfaction_metrics(self) -> Dict[str, Any]:
        """Get detailed user satisfaction metrics"""
        try:
            total_feedback = self.feedback_stats['total_feedback']
            if total_feedback == 0:
                return {"message": "No feedback data available"}
            
            # Rating distribution
            rating_dist = {}
            for i in range(1, 6):
                rating_dist[f"rating_{i}"] = {
                    "count": self.feedback_stats[f'rating_{i}'],
                    "percentage": (self.feedback_stats[f'rating_{i}'] / total_feedback) * 100
                }
            
            # Quality metrics
            quality_metrics = {
                "helpfulness": sum(1 for entry in self.feedback_storage.values() 
                                 if entry['feedback']['helpful']) / total_feedback,
                "correctness": sum(1 for entry in self.feedback_storage.values() 
                                 if entry['feedback']['correct']) / total_feedback,
                "clarity": sum(1 for entry in self.feedback_storage.values() 
                              if entry['feedback']['clear']) / total_feedback,
                "completeness": sum(1 for entry in self.feedback_storage.values() 
                                   if entry['feedback']['complete']) / total_feedback
            }
            
            return {
                "average_rating": self._calculate_average_rating(),
                "rating_distribution": rating_dist,
                "quality_metrics": quality_metrics,
                "satisfaction_trend": self._analyze_recent_trends()
            }
            
        except Exception as e:
            logger.error(f"Error calculating satisfaction metrics: {str(e)}")
            return {"error": str(e)}
    
    def _save_feedback_data(self):
        """Save feedback data to storage"""
        try:
            data = {
                "feedback": self.feedback_storage,
                "stats": dict(self.feedback_stats),
                "suggestions": self.improvement_suggestions,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(settings.feedback_data_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Feedback data saved successfully")
        except Exception as e:
            logger.error(f"Error saving feedback data: {str(e)}")