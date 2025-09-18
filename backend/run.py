#!/usr/bin/env python3
"""
Math Routing Agent - Backend Server Runner
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import the app after setting up the path
from app.main import app

def setup_environment():
    """Setup environment and create necessary directories"""
    try:
        # Create data directories
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        vector_store_dir = data_dir / "vector_store"
        vector_store_dir.mkdir(exist_ok=True)
        
        # Create initial data files if they don't exist
        kb_path = data_dir / "math_dataset.json"
        feedback_path = data_dir / "feedback_data.json"
        
        if not feedback_path.exists():
            import json
            initial_feedback = {
                "feedback": {},
                "stats": {},
                "suggestions": [],
                "last_updated": None
            }
            with open(feedback_path, 'w') as f:
                json.dump(initial_feedback, f, indent=2)
        
        logger.info("Environment setup completed")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup environment: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    # Only enforce minimal runtime deps; heavy libs are optional and handled via fallbacks
    required_packages = [
        'fastapi',
        'uvicorn',
        'aiohttp',
        'sympy',
        'bs4',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages (pip): fastapi uvicorn aiohttp sympy bs4 numpy")
        return False
    
    logger.info("All required dependencies are installed")
    return True

def main():
    """Main function to start the server"""
    print("🔬 Math Routing Agent - Backend Server")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Server configuration
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "log_level": "info",
        "access_log": True,
        "loop": "auto"
    }
    
    # Override with environment variables if present
    config["host"] = os.getenv("HOST", config["host"])
    config["port"] = int(os.getenv("PORT", config["port"]))
    config["reload"] = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"Starting server on {config['host']}:{config['port']}")
    logger.info(f"Reload mode: {config['reload']}")
    logger.info("API docs will be available at: http://localhost:8000/docs")
    logger.info("Health check: http://localhost:8000/health")
    
    try:
        # Start the server with the imported app
        uvicorn.run(app, **config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()