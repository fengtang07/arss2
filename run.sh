#!/bin/bash

# VLM Scene Architect v2.0 - Launch Script

echo "🚀 Starting VLM Scene Architect v2.0..."
echo ""

# Check if Python dependencies are installed
if ! python -c "import flask, openai" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r python/requirements.txt
fi

# Check for API key
if [ ! -z "$1" ]; then
    export OPENAI_API_KEY="$1"
    echo "✅ Using API key from command line"
elif [ ! -z "$OPENAI_API_KEY" ]; then
    echo "✅ Using API key from environment"
else
    echo "⚠️  WARNING: No OpenAI API key found!"
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo "   Or run: ./run.sh 'your-key-here'"
    echo ""
fi

echo ""
echo "🌐 Starting VLM agent server..."
echo "📍 Open browser: http://localhost:5004"
echo "🎮 Make sure Unity is running in Play Mode!"
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

# Run the Python agent from the python folder
cd python && python main.py 