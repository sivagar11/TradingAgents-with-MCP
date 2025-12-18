#!/bin/bash

# All Analysts Demo - Runs in ~1.5-2 minutes

echo "🚀 TradingAgents - Complete Demo (All 4 Analysts)"
echo "================================================="
echo ""
echo "⚡ Optimized for ~1.5-2 minutes"
echo "   ✅ All 4 analysts enabled"
echo "   ✅ No debate rounds"
echo "   ✅ Fast LLM models"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Activating virtual environment${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠ Warning: No virtual environment found${NC}"
fi

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Loading environment variables${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠ Warning: No .env file found${NC}"
fi

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠ Warning: OPENAI_API_KEY not set${NC}"
    echo "   Please set your API key in .env file"
fi

echo ""
echo -e "${CYAN}📊 Analysts Enabled:${NC}"
echo "   📈 Market Analyst - Technical indicators"
echo "   💬 Social Analyst - Sentiment analysis"
echo "   📰 News Analyst - Current events"
echo "   📊 Fundamentals Analyst - Financial metrics"
echo ""
echo -e "${BLUE}Starting analysis...${NC}"
echo ""

# Run the demo
python demo_all_analysts.py

echo ""
echo "✅ Demo complete!"

