#!/bin/bash

# Start both backend and frontend

echo "Starting AWS Migration Business Case Generator..."

# Start backend in background
echo "Starting backend server..."
cd ui/backend
source venv/bin/activate
python3 app.py &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd ui
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "Services started successfully!"
echo "=========================================="
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access the application at: http://localhost:3000"
echo ""
echo "To stop the services, run: ./stop-all.sh"
echo "Or press Ctrl+C and run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Wait for both processes
wait
