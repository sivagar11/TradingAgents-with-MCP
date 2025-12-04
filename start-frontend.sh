#!/bin/bash
# Start Next.js Frontend

cd "$(dirname "$0")/frontend"

# Use Node 20 if available
if [ -d "/opt/homebrew/opt/node@20/bin" ]; then
    export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
fi

echo "📊 Starting Next.js frontend..."
echo "   URL: http://localhost:3000"
echo "   Node: $(node --version)"
echo ""

npm run dev

