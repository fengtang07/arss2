# VLM Scene Architect

A system that allows you to create 3D scenes in Unity using natural language commands powered by OpenAI's GPT-4.

## How It Works
1. **User** types natural language commands in a web interface (e.g., "create a red cube at the origin")
2. **Python Agent** uses OpenAI API to convert text into structured JSON commands
3. **Unity** receives and executes these commands to manipulate 3D objects in real-time

## 🚀 Quick Start (READY TO USE!)

### ✅ All Dependencies Installed & Configured
- Python environment: Ready
- OpenAI API key: Set and working
- Dependencies: Flask, OpenAI, requests all installed

### 🎮 Unity Setup (Required)
1. Create a new Unity 3D project (or open existing)
2. Copy `HttpServer.cs` and `SceneBuilder.cs` to `Assets/Scripts/`
3. Create an empty GameObject named "SceneManager"
4. Add both scripts as components to this GameObject
5. **Press Play** - You should see: `[HttpServer] Server started and listening on http://127.0.0.1:8080/`

### 🚀 Run the System
**Option 1: Easy Script**
```bash
./run.sh
```

**Option 2: Manual**
```bash
source .venv/bin/activate
python vlm_scene_architect_agent.py
```

### 🌐 Use the System
1. Open browser: **http://127.0.0.1:5001**
2. Type commands like:
   - "Create a red cube at the origin"
   - "Place a blue sphere at x=5, y=2, z=0" 
   - "Make a tall green cylinder and a wide yellow plane"
   - "Clear the scene"

## System Architecture

```
[Web Browser] → [Python Flask Server] → [OpenAI API] → [Unity HTTP Server] → [3D Scene]
     ↑                    ↓                              ↓                       ↓
  User Input         JSON Commands                  Scene Manipulation    Visual Result
```

## Supported Commands
- **spawn**: Creates objects (cube, sphere, capsule, cylinder, plane)
- **clear_scene**: Removes all objects
- **Positioning**: Use coordinates like "at x=5, y=2, z=0"
- **Colors**: "red", "blue", "green", etc.
- **Scaling**: "tall", "wide", "small", "large"

## Troubleshooting

**Python agent won't start:**
- Check your OpenAI API key is set
- Ensure virtual environment is activated

**Unity not receiving commands:**
- Make sure Unity is in Play Mode
- Check Unity Console for HTTP server messages
- Verify both scripts are attached to the same GameObject

**Commands not working:**
- Check the web browser console for errors
- Verify Unity Console for command processing logs

## Example Session
```
User: "Create a red cube at the origin and a blue sphere above it"
→ Unity creates a red cube at (0,0,0) and blue sphere at (0,2,0)

User: "Add a green plane as the floor"
→ Unity adds a green plane at ground level

User: "Clear the scene"
→ Unity removes all objects
```

## Files
- `vlm_scene_architect_agent.py` - Python Flask web server with OpenAI integration
- `HttpServer.cs` - Unity HTTP server for receiving commands
- `SceneBuilder.cs` - Unity scene manipulation logic
- `requirements.txt` - Python dependencies 