#!/bin/bash

# TradingAgents - Start Script
# Runs both FastAPI backend and Next.js frontend

echo "🚀 Starting TradingAgents..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Use Node 20 if available
if [ -d "/opt/homebrew/opt/node@20/bin" ]; then
    export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
    echo -e "${GREEN}Using Node.js $(node --version)${NC}"
fi

# Activate virtual environment if exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Load environment variables
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${GREEN}Loading environment variables...${NC}"
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start FastAPI backend
echo -e "${BLUE}Starting FastAPI backend on http://localhost:8000${NC}"
cd "$SCRIPT_DIR"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Next.js frontend
echo -e "${BLUE}Starting Next.js frontend on http://localhost:3000${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TradingAgents is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Frontend:  http://localhost:3000"
echo "🔌 API:       http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait

