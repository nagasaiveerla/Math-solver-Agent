import re
import sympy as sp
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class MathSolverAgent:
    """Mathematical problem solver with step-by-step solutions"""
    
    def __init__(self):
        self.solution_templates = {
            "quadratic": self._solve_quadratic,
            "linear": self._solve_linear,
            "derivative": self._solve_derivative,
            "integral": self._solve_integral,
            "equation": self._solve_general_equation,
            "simplify": self._simplify_expression,
            "factor": self._factor_expression
        }
        
    async def solve_from_knowledge(self, kb_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Generate solution based on knowledge base result"""
        try:
            # Extract information from KB result
            answer = kb_result.get('answer', '')
            explanation = kb_result.get('explanation', '')
            topic = kb_result.get('topic', '')
            
            # Generate step-by-step solution
            steps = self._generate_steps_from_kb(kb_result, query)
            
            # Create detailed solution
            solution = self._format_solution(answer, explanation, steps)
            
            return {
                "solution": solution,
                "steps": steps,
                "topic": topic,
                "confidence": kb_result.get('score', 0.8),
                "method": "knowledge_base"
            }
            
        except Exception as e:
            logger.error(f"Error solving from knowledge base: {str(e)}")
            return self._generate_error_response(str(e))
    
    async def solve_from_web_search(self, search_results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Generate solution based on web search results"""
        try:
            if not search_results:
                return self._generate_no_results_response()
            
            # Extract best information from search results
            best_info = self._extract_best_info(search_results, query)
            
            # Generate solution steps
            steps = self._generate_steps_from_web(best_info, query)
            
            # Create solution text
            solution = self._create_web_based_solution(best_info, steps)
            
            return {
                "solution": solution,
                "steps": steps,
                "sources": search_results[:2],  # Include top 2 sources
                "confidence": best_info.get('confidence', 0.6),
                "method": "web_search"
            }
            
        except Exception as e:
            logger.error(f"Error solving from web search: {str(e)}")
            return self._generate_error_response(str(e))
    
    async def solve_direct(self, query: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Solve mathematical problems directly using symbolic computation"""
        try:
            # Identify problem type
            problem_type = self._identify_problem_type(query)
            
            # Use appropriate solver
            if problem_type in self.solution_templates:
                result = await self.solution_templates[problem_type](query)
            else:
                result = await self._solve_general_problem(query)
            
            result["method"] = "direct_computation"
            return result
            
        except Exception as e:
            logger.error(f"Error in direct solving: {str(e)}")
            return self._generate_error_response(str(e))
    
    def _generate_steps_from_kb(self, kb_result: Dict[str, Any], query: str) -> List[str]:
        """Generate solution steps from knowledge base result"""
        steps = []
        
        question = kb_result.get('question', '')
        answer = kb_result.get('answer', '')
        topic = kb_result.get('topic', '')
        
        # Start with problem identification
        steps.append(f"Problem Type: This is a {topic} problem.")
        
        if 'quadratic' in question.lower() and 'formula' in question.lower():
            steps.extend([
                "Step 1: Identify the quadratic equation in the form ax² + bx + c = 0",
                "Step 2: Apply the quadratic formula: x = (-b ± √(b²-4ac)) / (2a)",
                "Step 3: Substitute the values of a, b, and c",
                "Step 4: Simplify to find the solutions"
            ])
        elif 'derivative' in question.lower():
            steps.extend([
                "Step 1: Identify the function to differentiate",
                "Step 2: Apply appropriate differentiation rules",
                "Step 3: Simplify the result"
            ])
        elif 'solve' in query.lower():
            steps.extend([
                "Step 1: Write the equation in standard form",
                "Step 2: Apply appropriate solving technique",
                "Step 3: Verify the solution"
            ])
        else:
            # Generic steps
            steps.extend([
                "Step 1: Understand the problem requirements",
                "Step 2: Apply relevant mathematical principles",
                "Step 3: Calculate the result"
            ])
        
        return steps
    
    def _generate_steps_from_web(self, info: Dict[str, Any], query: str) -> List[str]:
        """Generate solution steps from web search information"""
        steps = []
        
        # Extract method from web content
        content = info.get('content', '')
        
        if 'step' in content.lower():
            # Try to extract existing steps from content
            step_pattern = r'step\s*\d+[:\-.]?\s*([^.!?]*[.!?])'
            found_steps = re.findall(step_pattern, content, re.IGNORECASE)
            
            if found_steps:
                for i, step in enumerate(found_steps[:5], 1):  # Max 5 steps
                    steps.append(f"Step {i}: {step.strip()}")
        
        if not steps:
            # Generate generic steps based on query
            if 'solve' in query.lower():
                steps = [
                    "Step 1: Identify the type of equation or problem",
                    "Step 2: Choose the appropriate solution method",
                    "Step 3: Apply the method systematically",
                    "Step 4: Check and verify the solution"
                ]
            else:
                steps = [
                    "Step 1: Understand the mathematical concept",
                    "Step 2: Apply relevant formulas or theorems",
                    "Step 3: Simplify and present the result"
                ]
        
        return steps
    
    def _identify_problem_type(self, query: str) -> str:
        """Identify the type of mathematical problem"""
        query_lower = query.lower()
        
        # Check for specific problem types
        if re.search(r'x\^?2|quadratic', query_lower):
            return "quadratic"
        elif re.search(r'derivative|d/dx|differentiat', query_lower):
            return "derivative"
        elif re.search(r'integral|∫|integrat', query_lower):
            return "integral"
        elif re.search(r'=.*[x-z]|solve.*for', query_lower):
            return "equation"
        elif re.search(r'simplify|expand', query_lower):
            return "simplify"
        elif re.search(r'factor|factorize', query_lower):
            return "factor"
        elif re.search(r'[x-z]\s*=|linear', query_lower):
            return "linear"
        else:
            return "general"
    
    async def _solve_quadratic(self, query: str) -> Dict[str, Any]:
        """Solve quadratic equations"""
        try:
            # Extract equation from query
            equation_match = re.search(r'([x-z]\^?2[^=]*=\s*\d+)', query)
            if equation_match:
                equation_str = equation_match.group(1)
            else:
                # Look for coefficients pattern like "x² - 5x + 6 = 0"
                coeff_match = re.search(r'([x-z])\^?2\s*([+-]\s*\d*[x-z])?\s*([+-]\s*\d+)?\s*=\s*(\d+)', query)
                if coeff_match:
                    var = coeff_match.group(1)
                    equation_str = f"{var}**2{coeff_match.group(2) or ''}{coeff_match.group(3) or ''} - {coeff_match.group(4) or '0'}"
                else:
                    return self._generate_generic_quadratic_solution()
            
            # Use SymPy to solve
            x = sp.Symbol('x')
            # Convert equation string to SymPy expression
            equation_str = equation_str.replace('^', '**').replace('=', '-(') + ')'
            expr = sp.sympify(equation_str)
            solutions = sp.solve(expr, x)
            
            steps = [
                "Step 1: Identify this as a quadratic equation",
                f"Step 2: Rearrange to standard form ax² + bx + c = 0",
                "Step 3: Apply the quadratic formula or factoring",
                f"Step 4: Solutions are: {', '.join(str(sol) for sol in solutions)}"
            ]
            
            solution_text = f"The solutions are: {', '.join(str(sol) for sol in solutions)}"
            
            return {
                "solution": solution_text,
                "steps": steps,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Error solving quadratic: {str(e)}")
            return self._generate_generic_quadratic_solution()
    
    async def _solve_linear(self, query: str) -> Dict[str, Any]:
        """Solve linear equations"""
        try:
            # Extract equation
            equation_match = re.search(r'([^=]+=[^=]+)', query)
            if not equation_match:
                return self._generate_generic_linear_solution()
            
            equation_str = equation_match.group(1)
            
            # Use SymPy
            x = sp.Symbol('x')
            left, right = equation_str.split('=')
            equation = sp.Eq(sp.sympify(left), sp.sympify(right))
            solution = sp.solve(equation, x)
            
            steps = [
                "Step 1: Identify this as a linear equation",
                "Step 2: Isolate the variable by performing same operations on both sides",
                f"Step 3: Solution is x = {solution[0] if solution else 'undefined'}"
            ]
            
            solution_text = f"x = {solution[0] if solution else 'No solution found'}"
            
            return {
                "solution": solution_text,
                "steps": steps,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Error solving linear equation: {str(e)}")
            return self._generate_generic_linear_solution()
    
    async def _solve_derivative(self, query: str) -> Dict[str, Any]:
        """Solve derivative problems"""
        try:
            # Extract function from query
            func_match = re.search(r'of\s+([^,\s]+)|d/dx\s*\(?([^)]+)\)?', query)
            if func_match:
                func_str = func_match.group(1) or func_match.group(2)
                func_str = func_str.replace('^', '**')
                
                x = sp.Symbol('x')
                func = sp.sympify(func_str)
                derivative = sp.diff(func, x)
                
                steps = [
                    f"Step 1: Function to differentiate: f(x) = {func}",
                    "Step 2: Apply differentiation rules",
                    f"Step 3: f'(x) = {derivative}"
                ]
                
                solution_text = f"The derivative is: {derivative}"
                
                return {
                    "solution": solution_text,
                    "steps": steps,
                    "confidence": 0.9
                }
            else:
                return self._generate_generic_derivative_solution()
                
        except Exception as e:
            logger.error(f"Error solving derivative: {str(e)}")
            return self._generate_generic_derivative_solution()
    
    async def _solve_integral(self, query: str) -> Dict[str, Any]:
        """Solve integration problems"""
        try:
            # Extract function from query
            func_match = re.search(r'∫\s*([^d]+)d[x-z]|integral\s+of\s+([^,\s]+)', query)
            if func_match:
                func_str = func_match.group(1) or func_match.group(2)
                func_str = func_str.replace('^', '**').strip()
                
                x = sp.Symbol('x')
                func = sp.sympify(func_str)
                integral = sp.integrate(func, x)
                
                steps = [
                    f"Step 1: Function to integrate: f(x) = {func}",
                    "Step 2: Apply integration rules",
                    f"Step 3: ∫f(x)dx = {integral} + C"
                ]
                
                solution_text = f"The integral is: {integral} + C"
                
                return {
                    "solution": solution_text,
                    "steps": steps,
                    "confidence": 0.9
                }
            else:
                return self._generate_generic_integral_solution()
                
        except Exception as e:
            logger.error(f"Error solving integral: {str(e)}")
            return self._generate_generic_integral_solution()
    
    async def _solve_general_equation(self, query: str) -> Dict[str, Any]:
        """Solve general equations"""
        return await self._solve_general_problem(query)
    
    async def _simplify_expression(self, query: str) -> Dict[str, Any]:
        """Simplify mathematical expressions"""
        try:
            # Extract expression to simplify
            expr_match = re.search(r'simplify\s+(.+)', query, re.IGNORECASE)
            if expr_match:
                expr_str = expr_match.group(1).replace('^', '**')
                expr = sp.sympify(expr_str)
                simplified = sp.simplify(expr)
                
                steps = [
                    f"Step 1: Original expression: {expr}",
                    "Step 2: Apply simplification rules",
                    f"Step 3: Simplified form: {simplified}"
                ]
                
                solution_text = f"Simplified expression: {simplified}"
                
                return {
                    "solution": solution_text,
                    "steps": steps,
                    "confidence": 0.9
                }
            else:
                return self._generate_generic_simplification_solution()
                
        except Exception as e:
            logger.error(f"Error simplifying expression: {str(e)}")
            return self._generate_generic_simplification_solution()
    
    async def _factor_expression(self, query: str) -> Dict[str, Any]:
        """Factor mathematical expressions"""
        try:
            # Extract expression to factor
            expr_match = re.search(r'factor\s+(.+)', query, re.IGNORECASE)
            if expr_match:
                expr_str = expr_match.group(1).replace('^', '**')
                expr = sp.sympify(expr_str)
                factored = sp.factor(expr)
                
                steps = [
                    f"Step 1: Original expression: {expr}",
                    "Step 2: Look for common factors and patterns",
                    f"Step 3: Factored form: {factored}"
                ]
                
                solution_text = f"Factored expression: {factored}"
                
                return {
                    "solution": solution_text,
                    "steps": steps,
                    "confidence": 0.9
                }
            else:
                return self._generate_generic_factoring_solution()
                
        except Exception as e:
            logger.error(f"Error factoring expression: {str(e)}")
            return self._generate_generic_factoring_solution()
    
    async def _solve_general_problem(self, query: str) -> Dict[str, Any]:
        """Handle general mathematical problems"""
        steps = [
            "Step 1: Analyzing the mathematical problem",
            "Step 2: Identifying relevant mathematical concepts",
            "Step 3: Applying appropriate solution methods"
        ]
        
        # Generate a helpful response based on query content
        solution = self._generate_contextual_help(query)
        
        return {
            "solution": solution,
            "steps": steps,
            "confidence": 0.5
        }
    
    def _generate_contextual_help(self, query: str) -> str:
        """Generate contextual help based on query content"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['quadratic', 'x^2', 'x²']):
            return "For quadratic equations, you can use the quadratic formula: x = (-b ± √(b²-4ac)) / (2a), or try factoring if possible."
        
        elif any(word in query_lower for word in ['derivative', 'differentiate']):
            return "To find derivatives, use rules like: power rule d/dx(x^n) = nx^(n-1), product rule, and chain rule."
        
        elif any(word in query_lower for word in ['integral', 'integrate']):
            return "For integration, try substitution method, integration by parts, or look up standard integral formulas."
        
        elif any(word in query_lower for word in ['solve', 'equation']):
            return "To solve equations: isolate the variable by performing the same operations on both sides, or use specific methods for different equation types."
        
        else:
            return "Please provide more specific details about your mathematical problem so I can give you a detailed step-by-step solution."
    
    # Helper methods for generating generic solutions
    def _generate_generic_quadratic_solution(self) -> Dict[str, Any]:
        return {
            "solution": "For quadratic equations ax² + bx + c = 0, use the quadratic formula: x = (-b ± √(b²-4ac)) / (2a)",
            "steps": [
                "Step 1: Identify coefficients a, b, and c",
                "Step 2: Calculate discriminant b² - 4ac",
                "Step 3: Apply quadratic formula",
                "Step 4: Simplify to get solutions"
            ],
            "confidence": 0.7
        }
    
    def _generate_generic_linear_solution(self) -> Dict[str, Any]:
        return {
            "solution": "For linear equations ax + b = c, solve by isolating x: x = (c - b) / a",
            "steps": [
                "Step 1: Subtract b from both sides",
                "Step 2: Divide both sides by a",
                "Step 3: x = (c - b) / a"
            ],
            "confidence": 0.7
        }
    
    def _generate_generic_derivative_solution(self) -> Dict[str, Any]:
        return {
            "solution": "Use differentiation rules: power rule, product rule, chain rule as appropriate",
            "steps": [
                "Step 1: Identify the function type",
                "Step 2: Apply appropriate differentiation rule",
                "Step 3: Simplify the result"
            ],
            "confidence": 0.6
        }
    
    def _generate_generic_integral_solution(self) -> Dict[str, Any]:
        return {
            "solution": "Use integration techniques: substitution, integration by parts, or standard formulas",
            "steps": [
                "Step 1: Identify the function type",
                "Step 2: Choose appropriate integration method",
                "Step 3: Apply the method and add constant C"
            ],
            "confidence": 0.6
        }
    
    def _generate_generic_simplification_solution(self) -> Dict[str, Any]:
        return {
            "solution": "To simplify expressions, combine like terms, factor common elements, and apply algebraic rules",
            "steps": [
                "Step 1: Identify like terms",
                "Step 2: Combine and factor where possible",
                "Step 3: Write in simplest form"
            ],
            "confidence": 0.6
        }
    
    def _generate_generic_factoring_solution(self) -> Dict[str, Any]:
        return {
            "solution": "To factor expressions, look for common factors, difference of squares, or trinomial patterns",
            "steps": [
                "Step 1: Look for greatest common factor",
                "Step 2: Check for special patterns",
                "Step 3: Factor completely"
            ],
            "confidence": 0.6
        }
    
    def _extract_best_info(self, search_results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Extract the most relevant information from search results"""
        best_result = search_results[0] if search_results else {}
        
        # Combine information from multiple results
        combined_content = ""
        for result in search_results[:3]:  # Top 3 results
            if result.get('has_content') and result.get('content'):
                combined_content += result['content'] + " "
        
        return {
            "title": best_result.get('title', ''),
            "content": combined_content.strip(),
            "confidence": best_result.get('relevance_score', 0.5),
            "source_count": len(search_results)
        }
    
    def _create_web_based_solution(self, info: Dict[str, Any], steps: List[str]) -> str:
        """Create solution text based on web search information"""
        title = info.get('title', '')
        content = info.get('content', '')
        
        if content:
            # Extract key mathematical information
            solution = f"Based on search results about '{title}':\n\n{content[:300]}..."
        else:
            solution = f"Found information about '{title}', but specific solution steps need to be worked out based on the mathematical principles involved."
        
        return solution
    
    def _format_solution(self, answer: str, explanation: str, steps: List[str]) -> str:
        """Format the final solution text"""
        solution_parts = []
        
        if answer:
            solution_parts.append(f"Answer: {answer}")
        
        if explanation:
            solution_parts.append(f"\nExplanation: {explanation}")
        
        if steps:
            solution_parts.append(f"\nDetailed Steps:\n" + "\n".join(steps))
        
        return "\n".join(solution_parts)
    
    def _generate_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "solution": "I encountered an error while solving this problem. Please try rephrasing your question or check if all necessary information is provided.",
            "steps": [
                "Error occurred during processing",
                "Please verify your input and try again"
            ],
            "confidence": 0.0,
            "error": error_msg
        }
    
    def _generate_no_results_response(self) -> Dict[str, Any]:
        """Generate response when no search results found"""
        return {
            "solution": "I couldn't find specific information about this problem online. Please provide more details or try a different approach to the question.",
            "steps": [
                "No relevant search results found",
                "Consider rephrasing the question",
                "Provide more specific mathematical details"
            ],
            "confidence": 0.0
        }
        