#!/bin/bash

echo "🧹 Creating Clean Demo Branch"
echo "================================"

cd /Users/sivagar/Desktop/LMS/sem3/Trading_agent/TradingAgents

# Step 1: Commit current work
echo "📝 Step 1: Committing current changes to FE..."
git add .
git commit -m "WIP: Optimization attempts - before creating demo branch" || echo "Nothing to commit"

# Step 2: Clean up temp files
echo "🗑️  Step 2: Removing temporary files..."
rm -f test_timing.py test_timing_2analysts.py test_timing_demo_mode.py
rm -f demo_quick.py demo_all_analysts.py
rm -f DEMO_MODE_GUIDE.md OPTIMIZATION_SUMMARY.md QUICK_DEMO_GUIDE.md QUICK_START.md SPEED_OPTIMIZATION_ALL_ANALYSTS.md DEMO_OPTIONS.md
rm -f tradingagents/agents/analysts/*_demo.py
rm -f tradingagents/agents/analysts/quick_analysts_demo.py
rm -f tradingagents/demo_config.py
rm -f demo-quick.sh demo-all.sh

# Step 3: Commit cleanup
echo "📝 Step 3: Committing cleanup..."
git add -A
git commit -m "Clean up: Remove temporary test and demo files" || echo "Nothing to clean up"

# Step 4: Create new branch
echo "🌿 Step 4: Creating FE-demo branch..."
git checkout -b FE-demo

# Verify
echo ""
echo "✅ Done! You are now on branch:"
git branch | grep "*"
echo ""
echo "📊 Current status:"
git status
echo ""
echo "🚀 Ready to start fresh optimizations on FE-demo branch!"

