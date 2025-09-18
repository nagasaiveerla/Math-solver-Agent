#!/bin/bash

# Math Routing Agent - Complete Setup Script
# This script sets up both backend and frontend for the Math Routing Agent

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print banner
print_banner() {
    echo ""
    echo "🔬 Math Routing Agent - Setup Script"
    echo "===================================="
    echo ""
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is required but not installed."
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
    log_info "Found Python $python_version"
    
    # Check pip
    if ! command_exists pip3; then
        log_error "pip3 is required but not installed."
        exit 1
    fi
    
    # Check Node.js
    if ! command_exists node; then
        log_error "Node.js is required but not installed."
        log_info "Please install Node.js from https://nodejs.org/"
        exit 1
    fi
    
    node_version=$(node --version)
    log_info "Found Node.js $node_version"
    
    # Check npm
    if ! command_exists npm; then
        log_error "npm is required but not installed."
        exit 1
    fi
    
    npm_version=$(npm --version)
    log_info "Found npm $npm_version"
    
    log_success "All system requirements met!"
}

# Setup backend
setup_backend() {
    log_info "Setting up backend..."
    
    cd backend || exit 1
    
    # Create virtual environment
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create necessary directories
    log_info "Creating data directories..."
    mkdir -p data/vector_store
    
    # Initialize empty feedback data if not exists
    if [ ! -f "data/feedback_data.json" ]; then
        log_info "Creating initial feedback data file..."
        cat > data/feedback_data.json << EOF
{
  "feedback": {},
  "stats": {},
  "suggestions": [],
  "last_updated": null
}
EOF
    fi
    
    # Test backend setup
    log_info "Testing backend setup..."
    python -c "
import sys
try:
    import fastapi
    import uvicorn
    import sympy
    import sentence_transformers
    import faiss
    print('✅ All backend dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    cd ..
    log_success "Backend setup completed!"
}

# Setup frontend
setup_frontend() {
    log_info "Setting up frontend..."
    
    cd frontend || exit 1
    
    # Install npm dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if not exists
    if [ ! -f ".env" ]; then
        log_info "Creating environment configuration..."
        cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_APP_NAME=Math Routing Agent
EOF
    fi
    
    cd ..
    log_success "Frontend setup completed!"
}

# Create run scripts
create_run_scripts() {
    log_info "Creating convenience scripts..."
    
    # Backend run script
    cat > run-backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Math Routing Agent Backend..."
cd backend
source venv/bin/activate
python run.py
EOF
    chmod +x run-backend.sh
    
    # Frontend run script
    cat > run-frontend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Math Routing Agent Frontend..."
cd frontend
npm start
EOF
    chmod +x run-frontend.sh
    
    # Combined run script
    cat > run-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Math Routing Agent (Backend + Frontend)..."

# Function to kill background processes on exit
cleanup() {
    echo "🛑 Stopping services..."
    jobs -p | xargs -r kill
    exit
}
trap cleanup EXIT INT TERM

# Start backend in background
echo "Starting backend..."
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Both services started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF
    chmod +x run-all.sh
    
    log_success "Run scripts created!"
}

# Create project documentation
create_documentation() {
    log_info "Creating project documentation..."
    
    cat > README.md << 'EOF'
# Math Routing Agent

An intelligent mathematical problem-solving system with routing capabilities, guardrails, and human-in-the-loop feedback.

## Features

- **AI Gateway with Guardrails**: Input/output validation and privacy protection
- **Knowledge Base Integration**: Vector database with mathematical content
- **Intelligent Routing**: Smart routing between knowledge base, web search, and direct computation
- **Web Search Capabilities**: DuckDuckGo integration for latest mathematical insights
- **Human-in-the-Loop Feedback**: Continuous learning from user feedback
- **Step-by-Step Solutions**: Detailed mathematical explanations

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation & Setup
```bash
# Clone the repository
git clone <repository-url>
cd math-routing-agent

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Running the Application

#### Option 1: Run Both Services
```bash
./run-all.sh
```

#### Option 2: Run Separately
```bash
# Terminal 1 - Backend
./run-backend.sh

# Terminal 2 - Frontend  
./run-frontend.sh
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Sample Questions

### Knowledge Base Questions:
- "What is the quadratic formula?"
- "Solve x^2 - 5x + 6 = 0"
- "Find the derivative of x^3 + 2x^2 - 5x + 1"

### Web Search Questions:
- "What is the Basel problem in mathematics?"
- "Explain the Riemann hypothesis in simple terms"
- "How to solve differential equations using Laplace transforms?"

### Computational Questions:
- "Solve 2x + 5 = 13"
- "Factor x^2 - 9"
- "Simplify (x^2 - 4) / (x - 2)"

## Architecture

- **Backend**: FastAPI with Python
- **Frontend**: React with Material-UI
- **Vector Store**: FAISS (local, no API required)
- **Web Search**: DuckDuckGo (free, no API key)
- **Math Rendering**: MathJax integration

## Development

### Backend Structure
```
backend/
├── app/
│   ├── core/          # Configuration and guardrails
│   ├── agents/        # Routing and feedback agents
│   ├── services/      # Knowledge base and search services
│   ├── models/        # Pydantic schemas
│   └── api/          # FastAPI routes
├── data/             # Knowledge base and feedback data
└── requirements.txt  # Python dependencies
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/   # React components
│   ├── services/     # API integration
│   └── App.js       # Main application
├── public/          # Static files
└── package.json     # Node.js dependencies
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## License

This project is licensed under the MIT License.
EOF

    log_success "Documentation created!"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Check backend
    if [ -d "backend/venv" ]; then
        log_success "Backend virtual environment created"
    else
        log_error "Backend virtual environment missing"
        return 1
    fi
    
    if [ -f "backend/requirements.txt" ]; then
        log_success "Backend requirements file exists"
    else
        log_error "Backend requirements file missing"
        return 1
    fi
    
    # Check frontend
    if [ -d "frontend/node_modules" ]; then
        log_success "Frontend dependencies installed"
    else
        log_error "Frontend dependencies missing"
        return 1
    fi
    
    if [ -f "frontend/package.json" ]; then
        log_success "Frontend package configuration exists"
    else
        log_error "Frontend package configuration missing"
        return 1
    fi
    
    # Check run scripts
    if [ -f "run-all.sh" ]; then
        log_success "Run scripts created"
    else
        log_error "Run scripts missing"
        return 1
    fi
    
    log_success "Installation verification completed!"
}

# Print usage instructions
print_usage() {
    echo ""
    log_info "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Start the application: ./run-all.sh"
    echo "2. Open your browser to: http://localhost:3000"
    echo "3. Try asking mathematical questions!"
    echo ""
    echo "Alternative commands:"
    echo "• Backend only: ./run-backend.sh"
    echo "• Frontend only: ./run-frontend.sh"
    echo "• API docs: http://localhost:8000/docs"
    echo ""
    echo "For help or issues, check the README.md file."
    echo ""
}

# Main execution
main() {
    print_banner
    
    check_requirements
    
    setup_backend
    
    setup_frontend
    
    create_run_scripts
    
    create_documentation
    
    verify_installation
    
    print_usage
}

# Run main function
main "$@"