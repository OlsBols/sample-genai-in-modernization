#!/bin/bash

echo "Stopping AWS Migration Business Case Generator..."
echo ""

# Stop backend using PID file
if [ -f .pids/backend.pid ]; then
    BACKEND_PID=$(cat .pids/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill -9 $BACKEND_PID 2>/dev/null
        echo "✓ Backend stopped"
    else
        echo "⚠ Backend PID file exists but process not running"
    fi
    rm -f .pids/backend.pid
else
    echo "⚠ No backend PID file found"
fi

# Also kill any process on port 5000 (fallback)
BACKEND_PORT_PID=$(lsof -ti :5000 2>/dev/null)
if [ ! -z "$BACKEND_PORT_PID" ]; then
    echo "Killing process on port 5000 (PID: $BACKEND_PORT_PID)..."
    kill -9 $BACKEND_PORT_PID 2>/dev/null
    echo "✓ Port 5000 cleared"
fi

echo ""

# Stop frontend using PID file
if [ -f .pids/frontend.pid ]; then
    FRONTEND_PID=$(cat .pids/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill -9 $FRONTEND_PID 2>/dev/null
        echo "✓ Frontend stopped"
    else
        echo "⚠ Frontend PID file exists but process not running"
    fi
    rm -f .pids/frontend.pid
else
    echo "⚠ No frontend PID file found"
fi

# Also kill any process on port 3000 (fallback)
FRONTEND_PORT_PID=$(lsof -ti :3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    echo "Killing process on port 3000 (PID: $FRONTEND_PORT_PID)..."
    kill -9 $FRONTEND_PORT_PID 2>/dev/null
    echo "✓ Port 3000 cleared"
fi

# Clean up any remaining processes by pattern (extra safety)
pkill -f "python.*app.py" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

echo ""
echo "=========================================="
echo "All services stopped."
echo "=========================================="
echo ""
echo "To verify ports are free:"
echo "  lsof -i :5000  # Should show nothing"
echo "  lsof -i :3000  # Should show nothing"
echo ""
