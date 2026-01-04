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

<<<<<<< HEAD
echo "🎉 Setup Complete! Run 'source venv/bin/activate' to start."
=======
echo "🎉 Setup Complete! Run 'source venv/bin/activate' to start."
>>>>>>> 14340357d6c1dd9e02e8a8307d97cd67fefd3dda
