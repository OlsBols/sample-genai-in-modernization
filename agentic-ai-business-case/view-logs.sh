#!/bin/bash

# Quick log viewer script

echo "=========================================="
echo "Log Viewer - AWS Migration Business Case"
echo "=========================================="
echo ""

# Check if logs exist
if [ ! -f .pids/backend.log ]; then
    echo "❌ Backend log not found at .pids/backend.log"
    echo "   Services may not be running. Run ./start-all.sh first"
    exit 1
fi

if [ ! -f .pids/frontend.log ]; then
    echo "❌ Frontend log not found at .pids/frontend.log"
    echo "   Services may not be running. Run ./start-all.sh first"
    exit 1
fi

# Show menu
echo "Select log to view:"
echo "  1) Backend log (last 50 lines)"
echo "  2) Frontend log (last 50 lines)"
echo "  3) Backend log (real-time)"
echo "  4) Frontend log (real-time)"
echo "  5) Both logs (last 50 lines each)"
echo "  6) Check for errors in backend"
echo "  7) Check for errors in frontend"
echo "  q) Quit"
echo ""
read -p "Enter choice [1-7 or q]: " choice

case $choice in
    1)
        echo ""
        echo "========== Backend Log (Last 50 lines) =========="
        tail -50 .pids/backend.log
        ;;
    2)
        echo ""
        echo "========== Frontend Log (Last 50 lines) =========="
        tail -50 .pids/frontend.log
        ;;
    3)
        echo ""
        echo "========== Backend Log (Real-time) =========="
        echo "Press Ctrl+C to exit"
        echo ""
        tail -f .pids/backend.log
        ;;
    4)
        echo ""
        echo "========== Frontend Log (Real-time) =========="
        echo "Press Ctrl+C to exit"
        echo ""
        tail -f .pids/frontend.log
        ;;
    5)
        echo ""
        echo "========== Backend Log (Last 50 lines) =========="
        tail -50 .pids/backend.log
        echo ""
        echo "========== Frontend Log (Last 50 lines) =========="
        tail -50 .pids/frontend.log
        ;;
    6)
        echo ""
        echo "========== Backend Errors =========="
        grep -i "error\|exception\|traceback\|failed" .pids/backend.log | tail -20
        ;;
    7)
        echo ""
        echo "========== Frontend Errors =========="
        grep -i "error\|exception\|failed" .pids/frontend.log | tail -20
        ;;
    q|Q)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
