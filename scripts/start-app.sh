#!/bin/bash

# Define color codes
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Store initial directory
INITIAL_DIR=$(pwd)

# Check if we're in scripts directory and navigate accordingly
if [[ $(basename $(pwd)) == "scripts" ]]; then
    cd ..
fi

echo "Starting API (Flask) server..."

python3 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
cd server || {
    echo "Error: server directory not found"
    cd "$INITIAL_DIR"
    exit 1
}
export FLASK_DEBUG=1
export FLASK_PORT=5100
python app.py &

# Store the Python server process ID
SERVER_PID=$!

echo "Starting client (Astro)..."
cd ../client || {
    echo "Error: client directory not found"
    cd "$INITIAL_DIR"
    exit 1
}
npm install
npm run dev -- --no-clearScreen &

# Store the SvelteKit server process ID
CLIENT_PID=$!

# Sleep for 3 seconds
sleep 5

# Display the server URLs
echo -e "\n${GREEN}Server (Flask) running at: http://localhost:5100${NC}"
echo -e "${GREEN}Client (Astro) server running at: http://localhost:4321${NC}\n"

echo "Ctl-C to stop the servers"

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $SERVER_PID
    kill $CLIENT_PID
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Keep the script running
wait