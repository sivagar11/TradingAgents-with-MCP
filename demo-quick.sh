#!/bin/bash

# Quick Demo Launcher - Runs optimized 1-minute demo

echo "🚀 TradingAgents - Quick Demo"
echo "================================"
echo ""
echo "⚡ Optimized for ~1 minute runtime"
echo "   • Market analyst only"
echo "   • No debate rounds"
echo "   • Fast LLM models"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}Warning: No virtual environment found${NC}"
fi

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${GREEN}Loading environment variables...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}Warning: No .env file found${NC}"
fi

echo ""
echo -e "${BLUE}Starting quick demo...${NC}"
echo ""

# Run the quick demo
python demo_quick.py

echo ""
echo "✅ Demo complete!"

