#!/bin/bash

echo "🚀 Starting Job Radar ID Setup..."

# 1. Check if venv exists
if [ -d "venv" ]; then
    echo "✅ Virtual Environment found."
else
    echo "📦 Creating new Virtual Environment..."
    python3 -m venv venv
fi

# 2. Activate Venv & Install
source venv/bin/activate

echo "⬇️  Installing Dependencies from requirements.txt..."
pip install -r requirements.txt

echo "🎉 Setup Complete! Run 'source venv/bin/activate' to start."
