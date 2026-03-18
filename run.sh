#!/bin/bash
# Script to start the Certificate Portal

cd "$(dirname "$0")"

# Activate virtual environment if it exists, otherwise create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing requirements..."
pip install flask reportlab pypdf

echo "Starting Portal on http://127.0.0.1:5000"
# Run the flask application
python3 app.py
