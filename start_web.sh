#!/bin/bash

# OpenManus Web Interface Startup Script

echo "Starting OpenManus Web Interface..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "test_server.py" ]; then
    echo "Error: test_server.py not found. Please run this script from the OpenManus directory."
    exit 1
fi

# Install minimal dependencies if requirements.min.txt exists
if [ -f "requirements.min.txt" ]; then
    echo "Installing minimal dependencies..."
    pip install -r requirements.min.txt
fi

# Start the web server
echo "Starting Flask development server..."
echo "Web interface will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 test_server.py
