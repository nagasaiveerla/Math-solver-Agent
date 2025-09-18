import json
import os
from typing import List, Dict, Any
import logging
from app.core.config import get_settings
import pickle

logger = logging.getLogger(__name__)
settings = get_settings()

class KnowledgeBaseService:
    """Service for managing mathematical knowledge base with vector search"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.documents = []
        self.embeddings = None
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with mathematical content"""
        try:
            # Lazy import heavy deps; fall back gracefully if unavailable
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.warning(f"SentenceTransformer unavailable, using keyword fallback. Reason: {e}")
                self.model = None
            
            # Load or create knowledge base
            self._load_or_create_knowledge_base()
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            self._create_fallback_knowledge_base()
    
    def _load_or_create_knowledge_base(self):
        """Load existing knowledge base or create new one"""
        kb_path = settings.knowledge_base_path
        vector_path = settings.vector_store_path
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(kb_path), exist_ok=True)
        os.makedirs(vector_path, exist_ok=True)
        
        if os.path.exists(kb_path):
            self._load_existing_knowledge_base(kb_path, vector_path)
        else:
            self._create_new_knowledge_base(kb_path, vector_path)
    
    def _load_existing_knowledge_base(self, kb_path: str, vector_path: str):
        """Load existing knowledge base and vector index"""
        try:
            # Load documents
            with open(kb_path, 'r') as f:
                self.documents = json.load(f)
            logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
            
            # Load vector index (only if faiss available)
            index_path = os.path.join(vector_path, 'faiss_index.bin')
            embeddings_path = os.path.join(vector_path, 'embeddings.pkl')
            
            if os.path.exists(index_path) and os.path.exists(embeddings_path):
                try:
                    import faiss  # type: ignore
                    self.index = faiss.read_index(index_path)
                    with open(embeddings_path, 'rb') as f:
                        self.embeddings = pickle.load(f)
                    logger.info("Loaded existing vector index")
                except Exception as e:
                    logger.warning(f"FAISS unavailable, skipping index load. Reason: {e}")
                    self.index = None
                    self.embeddings = None
            else:
                logger.info("Vector index not found, rebuilding...")
                self._build_vector_index()
                
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            self._create_new_knowledge_base(kb_path, vector_path)
    
    def _create_new_knowledge_base(self, kb_path: str, vector_path: str):
        """Create new knowledge base with mathematical content"""
        logger.info("Creating new knowledge base...")
        
        # Sample mathematical knowledge base
        self.documents = [
            {
                "id": "quad_formula",
                "question": "What is the quadratic formula?",
                "answer": "The quadratic formula is x = (-b ± √(b²-4ac)) / (2a)",
                "explanation": "This formula solves quadratic equations of the form ax² + bx + c = 0",
                "topic": "algebra",
                "difficulty": "intermediate",
                "keywords": ["quadratic", "formula", "equation", "roots"]
            },
            {
                "id": "derivative_rules",
                "question": "What are the basic derivative rules?",
                "answer": "Power rule: d/dx(x^n) = nx^(n-1), Product rule: d/dx(uv) = u'v + uv', Chain rule: d/dx(f(g(x))) = f'(g(x))g'(x)",
                "explanation": "These are the fundamental rules for finding derivatives in calculus",
                "topic": "calculus",
                "difficulty": "intermediate",
                "keywords": ["derivative", "calculus", "power rule", "product rule", "chain rule"]
            },
            {
                "id": "pythagorean_theorem",
                "question": "What is the Pythagorean theorem?",
                "answer": "In a right triangle, a² + b² = c², where c is the hypotenuse",
                "explanation": "The square of the hypotenuse equals the sum of squares of the other two sides",
                "topic": "geometry",
                "difficulty": "basic",
                "keywords": ["pythagorean", "theorem", "triangle", "hypotenuse", "geometry"]
            },
            {
                "id": "integration_basic",
                "question": "What is integration?",
                "answer": "Integration is the reverse process of differentiation, used to find areas under curves",
                "explanation": "The integral ∫f(x)dx represents the antiderivative of f(x) plus a constant",
                "topic": "calculus",
                "difficulty": "intermediate",
                "keywords": ["integration", "integral", "antiderivative", "calculus"]
            },
            {
                "id": "linear_equation",
                "question": "How to solve linear equations?",
                "answer": "For ax + b = c, solve by isolating x: x = (c - b) / a",
                "explanation": "Linear equations have the form ax + b = c and can be solved by algebraic manipulation",
                "topic": "algebra",
                "difficulty": "basic",
                "keywords": ["linear", "equation", "algebra", "solve"]
            },
            {
                "id": "trig_identities",
                "question": "What are basic trigonometric identities?",
                "answer": "sin²θ + cos²θ = 1, tan θ = sin θ / cos θ, sin(2θ) = 2sin θ cos θ",
                "explanation": "These identities are fundamental relationships between trigonometric functions",
                "topic": "trigonometry",
                "difficulty": "intermediate",
                "keywords": ["trigonometry", "identities", "sin", "cos", "tan"]
            },
            {
                "id": "factorial",
                "question": "What is a factorial?",
                "answer": "n! = n × (n-1) × (n-2) × ... × 1, with 0! = 1",
                "explanation": "Factorial is the product of all positive integers up to n",
                "topic": "combinatorics",
                "difficulty": "basic",
                "keywords": ["factorial", "combinatorics", "multiplication"]
            },
            {
                "id": "slope_formula",
                "question": "What is the slope formula?",
                "answer": "slope = (y₂ - y₁) / (x₂ - x₁) for points (x₁,y₁) and (x₂,y₂)",
                "explanation": "Slope measures the rate of change between two points on a line",
                "topic": "algebra",
                "difficulty": "basic",
                "keywords": ["slope", "formula", "line", "rate", "change"]
            },
            {
                "id": "area_circle",
                "question": "What is the area of a circle?",
                "answer": "Area = πr², where r is the radius",
                "explanation": "The area of a circle is pi times the square of its radius",
                "topic": "geometry",
                "difficulty": "basic",
                "keywords": ["area", "circle", "radius", "pi", "geometry"]
            },
            {
                "id": "solve_quadratic",
                "question": "How to solve x² - 5x + 6 = 0?",
                "answer": "x = 2 or x = 3",
                "explanation": "Factor as (x-2)(x-3) = 0 or use quadratic formula",
                "topic": "algebra",
                "difficulty": "intermediate",
                "keywords": ["quadratic", "solve", "factoring", "equation"]
            }
        ]
        
        # Save to file
        with open(kb_path, 'w') as f:
            json.dump(self.documents, f, indent=2)
        logger.info(f"Created knowledge base with {len(self.documents)} documents")
        
        # Build vector index
        self._build_vector_index()
    
    def _build_vector_index(self):
        """Build FAISS vector index for similarity search"""
        try:
            if not self.documents:
                logger.warning("No documents to index")
                return
            
            # Create text representations for embedding
            texts = []
            for doc in self.documents:
                # Combine question, answer, and keywords for better matching
                text = f"{doc['question']} {doc['answer']} {' '.join(doc['keywords'])}"
                texts.append(text)
            
            # If no model available, skip building index
            if self.model is None:
                logger.warning("Embedding model not available; skipping vector index build.")
                self.index = None
                self.embeddings = None
                return
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self.model.encode(texts)
            self.embeddings = embeddings
            
            # Create FAISS index
            try:
                import faiss  # type: ignore
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
            except Exception as e:
                logger.warning(f"FAISS unavailable; skipping index build. Reason: {e}")
                self.index = None
                return
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
            # Save index and embeddings
            vector_path = settings.vector_store_path
            index_path = os.path.join(vector_path, 'faiss_index.bin')
            embeddings_path = os.path.join(vector_path, 'embeddings.pkl')
            
            faiss.write_index(self.index, index_path)
            with open(embeddings_path, 'wb') as f:
                pickle.dump(embeddings, f)
            
            logger.info(f"Built and saved vector index with {len(embeddings)} documents")
            
        except Exception as e:
            logger.error(f"Error building vector index: {str(e)}")
            self._create_fallback_index()
    
    def _create_fallback_knowledge_base(self):
        """Create minimal fallback knowledge base"""
        logger.warning("Creating fallback knowledge base")
        self.documents = [
            {
                "id": "fallback",
                "question": "General math help",
                "answer": "I can help with basic mathematical problems. Please ask specific questions.",
                "explanation": "This is a fallback response when the knowledge base is unavailable",
                "topic": "general",
                "difficulty": "basic",
                "keywords": ["math", "help", "question"]
            }
        ]
        self.index = None
        self.embeddings = None
    
    def _create_fallback_index(self):
        """Create simple fallback index"""
        self.index = None
        self.embeddings = None
        logger.warning("Using keyword-based fallback search")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant documents
        Returns list of documents with similarity scores
        """
        try:
            if self.index is None or self.model is None:
                return self._keyword_search(query, top_k)
            
            # Generate query embedding
            query_embedding = self.model.encode([query])
            try:
                import faiss  # type: ignore
                faiss.normalize_L2(query_embedding)
            except Exception:
                return self._keyword_search(query, top_k)
            
            # Search using FAISS
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and idx < len(self.documents):  # Valid index
                    doc = self.documents[idx].copy()
                    doc['score'] = float(score)
                    doc['rank'] = i + 1
                    results.append(doc)
            
            # Filter by minimum score threshold
            results = [r for r in results if r['score'] > 0.3]
            
            logger.info(f"Found {len(results)} relevant documents for query: {query[:50]}")
            return results
            
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return self._keyword_search(query, top_k)
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback keyword-based search"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        for doc in self.documents:
            score = 0.0
            
            # Check keywords
            for keyword in doc['keywords']:
                if keyword.lower() in query_lower:
                    score += 0.5
            
            # Check question and answer
            doc_text = f"{doc['question']} {doc['answer']}".lower()
            for word in query_words:
                if word in doc_text:
                    score += 0.2
            
            if score > 0:
                doc_copy = doc.copy()
                doc_copy['score'] = score
                results.append(doc_copy)
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def add_document(self, document: Dict[str, Any]) -> bool:
        """Add a new document to the knowledge base"""
        try:
            # Validate document structure
            required_fields = ['id', 'question', 'answer', 'topic', 'keywords']
            if not all(field in document for field in required_fields):
                logger.error("Document missing required fields")
                return False
            
            # Check for duplicate ID
            if any(doc['id'] == document['id'] for doc in self.documents):
                logger.warning(f"Document with ID {document['id']} already exists")
                return False
            
            # Add document
            self.documents.append(document)
            
            # Rebuild index (in production, you'd want incremental updates)
            self._build_vector_index()
            
            # Save updated knowledge base
            with open(settings.knowledge_base_path, 'w') as f:
                json.dump(self.documents, f, indent=2)
            
            logger.info(f"Added new document: {document['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve a specific document by ID"""
        for doc in self.documents:
            if doc['id'] == doc_id:
                return doc
        return None
    
    def get_documents_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific topic"""
        return [doc for doc in self.documents if doc['topic'].lower() == topic.lower()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        topics = {}
        difficulties = {}
        
        for doc in self.documents:
            topic = doc['topic']
            difficulty = doc['difficulty']
            
            topics[topic] = topics.get(topic, 0) + 1
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        return {
            "total_documents": len(self.documents),
            "topics": topics,
            "difficulties": difficulties,
            "has_vector_index": self.index is not None,
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else None
        }
    
    def update_from_feedback(self, doc_id: str, feedback_data: Dict[str, Any]):
        """Update document based on user feedback"""
        try:
            doc = self.get_document_by_id(doc_id)
            if not doc:
                return False
            
            # Update document based on feedback
            if 'improved_answer' in feedback_data:
                doc['answer'] = feedback_data['improved_answer']
            
            if 'additional_keywords' in feedback_data:
                doc['keywords'].extend(feedback_data['additional_keywords'])
                doc['keywords'] = list(set(doc['keywords']))  # Remove duplicates
            
            # Save updated knowledge base
            with open(settings.knowledge_base_path, 'w') as f:
                json.dump(self.documents, f, indent=2)
            
            # Rebuild index to reflect changes
            self._build_vector_index()
            
            logger.info(f"Updated document {doc_id} based on feedback")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document from feedback: {str(e)}")
            return False