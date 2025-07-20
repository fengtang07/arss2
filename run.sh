#!/bin/bash

# VLM Scene Architect - Easy Run Script

echo "🚀 Starting VLM Scene Architect..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Set API key if provided as argument
if [ ! -z "$1" ]; then
    export OPENAI_API_KEY="$1"
    echo "✅ Using API key from command line"
elif [ ! -z "$OPENAI_API_KEY" ]; then
    echo "✅ Using API key from environment"
else
    echo "⚠️  Using API key from vlm_scene_architect_agent.py"
fi

echo ""
echo "🌐 Starting web server..."
echo "📍 Open browser: http://127.0.0.1:5001"
echo "🎮 Make sure Unity is running in Play Mode!"
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

# Run the Python agent
python vlm_scene_architect_agent.py 