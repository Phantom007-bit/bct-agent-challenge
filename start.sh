#!/bin/bash
ROOT="$HOME/MACHINE LEARNING WSL/bct-agent-challenge"

echo "🛑 Clearing ports..."
fuser -k 8000/tcp 2>/dev/null
fuser -k 3000/tcp 2>/dev/null
sleep 1

echo "🚀 Starting BCT Agent..."

cd "$ROOT"
source .venv/bin/activate
python main.py &
echo "✅ Backend running on port 8000"
sleep 3

cd "$ROOT/gateway"
node server.js &
echo "✅ Gateway running on port 3000"
sleep 1

cd "$ROOT/frontend"
npm run dev &
echo "✅ Frontend running"

echo ""
echo "All services online. Ctrl+C to stop all."
wait
