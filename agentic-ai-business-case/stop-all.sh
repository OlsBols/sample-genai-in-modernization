#!/bin/bash

echo "Stopping AWS Migration Business Case Generator..."

# Kill backend
pkill -f "python3 app.py"
echo "✓ Backend stopped"

# Kill frontend
pkill -f "npm start"
pkill -f "react-scripts start"
echo "✓ Frontend stopped"

echo "All services stopped."
