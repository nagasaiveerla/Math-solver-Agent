import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote_plus
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class WebSearchService:
    """Web search service using DuckDuckGo (no API key required)"""
    
    def __init__(self):
        self.search_url = "https://duckduckgo.com/html/"
        self.session = None
        self.math_domains = [
            "mathworld.wolfram.com",
            "en.wikipedia.org",
            "khanacademy.org", 
            "mathstackexchange.com",
            "brilliant.org",
            "mit.edu",
            "stanford.edu"
        ]
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        return self.session
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search using DuckDuckGo
        Returns list of search results with title, snippet, and URL
        """
        try:
            # Enhance query for mathematical content
            enhanced_query = self._enhance_math_query(query)
            logger.info(f"Searching for: {enhanced_query}")
            
            session = await self._get_session()
            
            # Prepare search parameters
            params = {
                'q': enhanced_query,
                'kp': '-2',  # Safe search off
                'kl': 'us-en',  # English results
                'kd': '-1'  # Don't track
            }
            
            async with session.get(self.search_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Search request failed with status {response.status}")
                    return []
                
                html = await response.text()
                results = self._parse_duckduckgo_results(html)
                
                # Filter and rank results
                filtered_results = self._filter_math_results(results, query)
                
                # Get additional content for top results
                enriched_results = await self._enrich_results(filtered_results[:max_results])
                
                logger.info(f"Found {len(enriched_results)} relevant results")
                return enriched_results
                
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return await self._fallback_search(query)
    
    def _enhance_math_query(self, query: str) -> str:
        """Enhance query with mathematical context"""
        query_lower = query.lower()
        
        # Add mathematical context to general queries
        if not any(word in query_lower for word in ['math', 'formula', 'equation', 'solve']):
            if any(word in query_lower for word in ['what is', 'define', 'explain']):
                query += " mathematics"
        
        return query
    
    def _parse_duckduckgo_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML results"""
        results = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find result containers
            result_divs = soup.find_all('div', class_=['result', 'web-result'])
            
            for div in result_divs:
                try:
                    # Extract title and URL
                    title_link = div.find('a', class_=['result__a'])
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Extract snippet
                    snippet_elem = div.find('div', class_=['result__snippet'])
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': 'duckduckgo'
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing result item: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo results: {str(e)}")
        
        return results
    
    def _filter_math_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Filter and rank results based on mathematical relevance"""
        scored_results = []
        query_lower = query.lower()
        
        for result in results:
            score = 0.0
            
            # Check domain reputation
            url = result.get('url', '').lower()
            for domain in self.math_domains:
                if domain in url:
                    score += 2.0
                    break
            
            # Check title relevance
            title = result.get('title', '').lower()
            if any(word in title for word in ['math', 'formula', 'equation', 'theorem', 'proof']):
                score += 1.0
            
            # Check snippet relevance
            snippet = result.get('snippet', '').lower()
            if any(word in snippet for word in ['solve', 'formula', 'equation', 'calculate']):
                score += 0.5
            
            # Query term matching
            query_words = query_lower.split()
            content = f"{title} {snippet}".lower()
            
            matching_words = sum(1 for word in query_words if word in content)
            score += (matching_words / len(query_words)) * 1.5
            
            # Penalize irrelevant content
            if any(term in content for term in ['shopping', 'buy', 'price', 'sale']):
                score -= 1.0
            
            if score > 0.5:  # Only include results with reasonable score
                result['relevance_score'] = score
                scored_results.append(result)
        
        # Sort by relevance score
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_results
    
    async def _enrich_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch additional content from top results"""
        enriched = []
        session = await self._get_session()
        
        for result in results:
            try:
                # Try to fetch content from the URL
                content = await self._fetch_page_content(session, result['url'])
                if content:
                    result['content'] = content[:1000]  # Limit content size
                    result['has_content'] = True
                else:
                    result['has_content'] = False
                
                enriched.append(result)
                
            except Exception as e:
                logger.debug(f"Error enriching result {result['url']}: {str(e)}")
                result['has_content'] = False
                enriched.append(result)
        
        return enriched
    
    async def _fetch_page_content(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch and extract relevant content from a webpage"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Extract text content
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Extract mathematical content
                math_content = self._extract_mathematical_content(text)
                
                return math_content if math_content else text[:500]
                
        except Exception as e:
            logger.debug(f"Error fetching content from {url}: {str(e)}")
            return None
    
    def _extract_mathematical_content(self, text: str) -> Optional[str]:
        """Extract mathematically relevant content from text"""
        # Look for mathematical patterns and formulas
        math_patterns = [
            r'[a-zA-Z]\s*=\s*[^,\n]{1,100}',  # Equations like x = ...
            r'∫[^∫]{1,50}d[a-zA-Z]',  # Integrals
            r'∑[^∑]{1,50}',  # Summations
            r'lim[^a-zA-Z][^,\n]{1,50}',  # Limits
            r'[a-zA-Z]+\s*\([^)]{1,50}\)\s*=',  # Functions
            r'theorem[^.]{1,200}\.',  # Theorems
            r'formula[^.]{1,200}\.',  # Formulas
        ]
        
        mathematical_sentences = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 500:
                continue
                
            # Check for mathematical content
            has_math = False
            for pattern in math_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    has_math = True
                    break
            
            # Check for mathematical keywords
            math_keywords = [
                'equation', 'formula', 'solve', 'derivative', 'integral',
                'theorem', 'proof', 'calculate', 'function', 'variable'
            ]
            
            if not has_math:
                has_math = any(keyword in sentence.lower() for keyword in math_keywords)
            
            if has_math:
                mathematical_sentences.append(sentence)
        
        if mathematical_sentences:
            return '. '.join(mathematical_sentences[:3])  # Return top 3 mathematical sentences
        
        return None
    
    async def _fallback_search(self, query: str) -> List[Dict[str, Any]]:
        """Fallback search results when web search fails"""
        logger.warning("Using fallback search results")
        
        # Return some basic mathematical information based on query
        fallback_results = []
        
        if 'quadratic' in query.lower():
            fallback_results.append({
                'title': 'Quadratic Formula',
                'snippet': 'The quadratic formula is x = (-b ± √(b²-4ac)) / (2a) for equations ax² + bx + c = 0',
                'url': 'fallback://quadratic',
                'source': 'fallback',
                'relevance_score': 0.8,
                'has_content': True,
                'content': 'Use the quadratic formula when factoring is difficult or impossible.'
            })
        
        elif 'derivative' in query.lower():
            fallback_results.append({
                'title': 'Basic Derivative Rules',
                'snippet': 'Power rule: d/dx(x^n) = nx^(n-1), Product rule, Chain rule are fundamental',
                'url': 'fallback://derivatives',
                'source': 'fallback',
                'relevance_score': 0.8,
                'has_content': True,
                'content': 'Derivatives measure the rate of change of functions.'
            })
        
        elif any(word in query.lower() for word in ['solve', 'equation']):
            fallback_results.append({
                'title': 'Solving Equations',
                'snippet': 'Mathematical equations can be solved using various algebraic techniques',
                'url': 'fallback://solving',
                'source': 'fallback',
                'relevance_score': 0.6,
                'has_content': True,
                'content': 'Isolate the variable by performing the same operations on both sides.'
            })
        
        return fallback_results
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.session and not self.session.closed:
            try:
                asyncio.create_task(self.session.close())
            except:
                pass

# MCP (Model Context Protocol) alternative implementation
class MCPSearchService:
    """Alternative search using Model Context Protocol pattern"""
    
    def __init__(self):
        self.context_sources = [
            "mathematical_knowledge",
            "computational_methods", 
            "theorem_database",
            "formula_repository"
        ]
    
    async def search_with_context(self, query: str, context_type: str = "general") -> Dict[str, Any]:
        """Search using MCP pattern with contextual information"""
        # This would integrate with MCP servers in a real implementation
        # For now, return structured mathematical context
        
        context_data = {
            "query": query,
            "context_type": context_type,
            "mathematical_context": self._get_mathematical_context(query),
            "suggested_approaches": self._get_solution_approaches(query),
            "related_concepts": self._get_related_concepts(query)
        }
        
        return context_data
    
    def _get_mathematical_context(self, query: str) -> Dict[str, Any]:
        """Extract mathematical context from query"""
        query_lower = query.lower()
        
        # Identify mathematical domain
        domains = {
            "algebra": ["equation", "solve", "variable", "polynomial", "linear", "quadratic"],
            "calculus": ["derivative", "integral", "limit", "function", "continuous"],
            "geometry": ["triangle", "circle", "area", "volume", "angle", "theorem"],
            "statistics": ["probability", "mean", "median", "distribution", "sample"],
            "trigonometry": ["sin", "cos", "tan", "angle", "triangle", "identity"]
        }
        
        identified_domain = "general"
        domain_confidence = 0.0
        
        for domain, keywords in domains.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            confidence = matches / len(keywords)
            if confidence > domain_confidence:
                domain_confidence = confidence
                identified_domain = domain
        
        return {
            "domain": identified_domain,
            "confidence": domain_confidence,
            "complexity": self._assess_complexity(query),
            "mathematical_entities": self._extract_entities(query)
        }
    
    def _get_solution_approaches(self, query: str) -> List[str]:
        """Suggest solution approaches based on query"""
        approaches = []
        query_lower = query.lower()
        
        if "solve" in query_lower:
            if "quadratic" in query_lower:
                approaches.extend(["factoring", "quadratic_formula", "completing_square"])
            elif "equation" in query_lower:
                approaches.extend(["algebraic_manipulation", "substitution", "graphical_method"])
        
        if "derivative" in query_lower:
            approaches.extend(["power_rule", "product_rule", "chain_rule"])
        
        if "integral" in query_lower:
            approaches.extend(["substitution", "integration_by_parts", "partial_fractions"])
        
        return approaches if approaches else ["analytical_approach", "step_by_step_solution"]
    
    def _get_related_concepts(self, query: str) -> List[str]:
        """Get related mathematical concepts"""
        concepts = []
        query_lower = query.lower()
        
        concept_map = {
            "quadratic": ["parabola", "discriminant", "vertex", "roots"],
            "derivative": ["rate_of_change", "slope", "tangent_line", "optimization"],
            "integral": ["area_under_curve", "antiderivative", "fundamental_theorem"],
            "triangle": ["pythagorean_theorem", "trigonometry", "similarity"],
            "probability": ["statistics", "random_variable", "distribution"]
        }
        
        for key, related in concept_map.items():
            if key in query_lower:
                concepts.extend(related)
        
        return list(set(concepts))  # Remove duplicates
    
    def _assess_complexity(self, query: str) -> str:
        """Assess the complexity level of the mathematical query"""
        complexity_indicators = {
            "basic": ["add", "subtract", "multiply", "divide", "simple"],
            "intermediate": ["solve", "equation", "formula", "calculate"],
            "advanced": ["prove", "theorem", "complex", "analysis", "optimization"]
        }
        
        query_lower = query.lower()
        scores = {}
        
        for level, indicators in complexity_indicators.items():
            scores[level] = sum(1 for indicator in indicators if indicator in query_lower)
        
        return max(scores, key=scores.get) if any(scores.values()) else "intermediate"
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract mathematical entities from query"""
        import re
        
        entities = []
        
        # Extract variables (single letters)
        variables = re.findall(r'\b[a-zA-Z]\b', query)
        entities.extend([f"variable_{var}" for var in variables])
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', query)
        entities.extend([f"number_{num}" for num in numbers])
        
        # Extract mathematical functions
        functions = re.findall(r'\b(sin|cos|tan|log|ln|sqrt|exp)\b', query, re.IGNORECASE)
        entities.extend([f"function_{func.lower()}" for func in functions])
        
        return list(set(entities))  # Remove duplicates