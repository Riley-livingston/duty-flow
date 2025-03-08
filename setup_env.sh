#!/bin/bash

# Create a virtual environment
echo "Creating virtual environment..."
python -m venv dutyflow-env

# Activate the virtual environment
echo "Activating virtual environment..."
source dutyflow-env/bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! Virtual environment 'dutyflow-env' is now active."
echo "To activate this environment in the future, run: source dutyflow-env/bin/activate" 