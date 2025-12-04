#!/bin/bash
# Start FastAPI Backend

cd "$(dirname "$0")"

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load env
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🔌 Starting FastAPI backend..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

