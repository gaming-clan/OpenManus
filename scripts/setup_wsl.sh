#!/bin/bash
# OpenManus WSL Setup Script
# Usage: bash scripts/setup_wsl.sh
set -e

# Print info
echo "[OpenManus] Starting WSL setup for user: $USER"

# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Reminder for API keys
if [ -f keys.example.txt ] && [ ! -f keys.txt ]; then
  echo "[OpenManus] NOTICE: A sample 'keys.example.txt' exists. Copy it to 'keys.txt' and update with your API keys:"
  echo "  cp keys.example.txt keys.txt"
fi

if [ ! -f keys.txt ]; then
  echo "[OpenManus] WARNING: keys.txt not found. Create it at project root or in your home directory and add your API keys."
fi

echo "[OpenManus] WSL setup complete. Activate your environment with: source .venv/bin/activate"
echo "[OpenManus] To run the app: python main.py --web  or  python main.py --agent"
