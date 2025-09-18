@echo off
echo Starting Math Routing Agent Backend...
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000