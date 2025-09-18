# Math Routing Agent

An Agentic-RAG architecture system that replicates a mathematical professor. When presented with a mathematical question, the system understands and generates a step-by-step solution, simplifying it for the student.

## Features

- **AI Gateway with Guardrails**: Input and output guardrails focused on delivering educational content in mathematics.
- **Knowledge Base**: Vector database for storing and retrieving mathematical questions and solutions.
- **Web Search Capability**: Falls back to web search when questions aren't found in the knowledge base.
- **Human-in-the-Loop Feedback**: Incorporates user feedback to improve responses over time.
- **Routing Pipeline**: Efficiently routes between knowledge base and web search based on confidence scores.

## Project Structure

```
math_agent_project/
├── backend/               # FastAPI backend
│   ├── data/              # Knowledge base and feedback data
│   ├── vector_store/      # Vector database files
│   ├── routes.py          # API endpoints
│   ├── schemas.py         # Pydantic models
│   ├── routing_agent.py   # Main routing logic
│   ├── math_solver.py     # Math solution generator
│   ├── knowledge_base.py  # Knowledge base operations
│   ├── web_search.py      # Web search functionality
│   ├── guardrails.py      # Input/output guardrails
│   ├── feedback_agent.py  # Feedback processing
│   └── run.py             # Server startup script
├── frontend/             # React frontend
│   ├── public/            # Static files
│   └── src/               # React source code
│       ├── components/    # React components
│       ├── services/      # API services
│       └── App.js         # Main application component
├── run.bat               # Script to run both frontend and backend
├── run-backend.bat       # Script to run only the backend
└── run-frontend.bat      # Script to run only the frontend
```

## Setup Instructions

### Prerequisites

- Python 3.8+ with pip
- Node.js and npm

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

## Running the Application

### Option 1: Run Both Services

Use the provided batch script to start both the backend and frontend:

```
run.bat
```

### Option 2: Run Services Separately

To run the backend only:

```
run-backend.bat
```

To run the frontend only:

```
run-frontend.bat
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Sample Questions

### From Knowledge Base

1. "What is the derivative of sin(x)?"
2. "Solve the quadratic equation x^2 - 4x + 4 = 0"
3. "Find the integral of 2x + 3"

### Requiring Web Search

1. "What is the Riemann hypothesis?"
2. "Explain the concept of a Hilbert space"
3. "What are the applications of differential equations in physics?"

## Feedback Mechanism

After receiving an answer, users can provide feedback on the quality of the response. This feedback is used to improve future responses through the human-in-the-loop mechanism.