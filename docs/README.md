# VLM Scene Architect - Autonomous Vision-Language Model Agent

🤖 **A self-critical AI agent that creates, simulates, and visually verifies 3D scenes in Unity using natural language commands.**

## ✨ **What Makes This Special**

- **🔍 Vision-Powered Verification**: Uses GPT-4o vision to actually SEE and verify what it creates
- **🔄 Forced Iteration**: Never accepts failure - keeps improving until vision confirms success  
- **🌐 GLB Model Integration**: Downloads real 3D models from the web (KhronosGroup/Sketchfab)
- **🎯 Self-Critical**: Detects when "bird" ≠ "fox" and automatically fixes it
- **⚡ Real-time Unity Integration**: Live 3D scene manipulation with instant feedback

## 🚀 **Quick Start (COMPLETE SYSTEM)**

### **✅ Prerequisites**
- Python 3.8+ with pip
- Unity 2021.3 LTS or later
- OpenAI API key (GPT-4o vision access)

### **🐍 Python Setup**
```bash
# Install dependencies
pip install -r python/requirements.txt

# Set your OpenAI API key as environment variable
export OPENAI_API_KEY="your-openai-api-key-here"
# Or for Windows: set OPENAI_API_KEY=your-openai-api-key-here
```

### **🎮 Unity Setup** 
1. **Create Unity 3D project**
2. **Copy C# scripts to `Assets/Scripts/`:**
   - `HttpServer.cs` - Unity HTTP API server
   - `SceneController.cs` - Scene management & object spawning  
   - `CommandModels.cs` - Data structures
3. **Create empty GameObject → Add all 3 scripts as components**
4. **Press Play** ▶️ - Console shows: `Server started on http://127.0.0.1:8080/`

### **🌐 Run the VLM Agent**
```bash
# Start the system from python folder
cd python && python main.py

# Or use run script (from root directory)
./run.sh
```
**→ Open browser: `http://localhost:5004`** (auto-detects available port)

## 🎯 **How It Works**

```
User Prompt → Agent Plans → Downloads GLB Models → Spawns Objects → 
Vision Analysis → Self-Evaluation → Iteration (if needed) → Success ✅
```

### **🔍 Verification Loop**
1. **Agent creates scene** using tools
2. **Vision analysis** captures Unity screenshot  
3. **Self-verification** compares vision vs request
4. **If mismatch detected** → automatically iterate and improve
5. **Only stops when vision confirms success**

## 🛠️ **Agent Capabilities**

### **🎨 Object Creation**
- **Primitives**: Cubes, spheres, cylinders with custom colors/positions
- **GLB Models**: Downloads real 3D models (fox, bottles, lamps, etc.)
- **Scene Management**: Clear, lighting, camera control

### **🧠 Smart Tools**
- `spawn_object` - Create colored primitives or GLB models  
- `search_web_for_3d_model` - Find models on web
- `download_and_import_model` - Get GLB files into Unity
- `capture_and_analyze_scene` - GPT-4o vision analysis
- `clear_scene` - Reset environment
- `run_simulation_and_get_results` - Physics simulation

### **📊 Vision Analysis**
- Real OpenAI GPT-4o vision calls (not mocked!)
- Detailed object identification and positioning
- Color, shape, and arrangement verification
- Honest reporting of what's actually visible

## 🎮 **Example Sessions**

### **Basic Scene Creation**
```
User: "Create a red robot, yellow target, and blue obstacle"
→ Agent creates colored cubes/spheres
→ Vision verifies colors and positions
→ ✅ Success confirmed
```

### **GLB Model Scene**  
```
User: "Clear the scene, then create a fox next to a green tree"
→ Agent downloads Low Poly Fox GLB
→ Creates green cylinder "tree"  
→ Vision analysis: "stylized fox-like shape alongside green tree"
→ ✅ Iteration successful
```

### **Self-Correction Example**
```
User: "Place a fox model in the scene"
→ Agent spawns model
→ Vision: "appears to be a bird-like object"
→ 🔄 Agent detects mismatch, tries different positioning
→ Vision: "orange and white fox with distinct features" 
→ ✅ Success after iteration
```

## 📁 **File Structure**

### **🐍 Core Python Files** (`python/`)
```
agent.py          # Main VLM agent with forced iteration
tools.py          # All tool definitions and implementations  
main.py           # Flask web server and UI
config.py         # API keys and configuration
requirements.txt  # Python dependencies
```

### **🎮 Unity C# Scripts** (`unity/`)
```
HttpServer.cs      # Unity HTTP API endpoints
SceneController.cs # Object spawning and scene management
CommandModels.cs   # Data structures for commands
```

### **📚 Documentation** (`docs/`)
```
README.md         # Complete system documentation (this file)
UNITY_SETUP.md    # Unity configuration guide
```

## 🔧 **Advanced Features**

### **🎯 Forced Iteration System**
- Agent **cannot** declare success until vision confirms it
- Automatic failure detection (e.g., "bird" when "fox" requested)
- Progressive improvement with multiple attempts
- Self-critical evaluation at every step

### **🌐 Web Model Integration**
- KhronosGroup sample models (fox, bottles, lamps)
- Automatic GLB download and Unity import
- Model caching to avoid re-downloads
- Fallback to primitives when models unavailable

### **👁️ Vision Verification**
- Screenshot capture from Unity scene
- GPT-4o detailed visual analysis
- Object identification and positioning
- Color and shape verification
- Arrangement and spatial relationship detection

## 🚨 **Troubleshooting**

### **❌ Common Issues**

**"HTTP 500 Internal Server Error"**
- Check OpenAI API key is set: `echo $OPENAI_API_KEY` (should show your key)
- Verify Unity is in Play Mode
- Check console for detailed error logs

**"Agent creates wrong objects"**  
- ✅ **Working as designed!** Agent will self-correct
- Vision system detects mismatches
- Forced iteration ensures eventual success

**"Unity connection failed"**
- Ensure Unity HTTP server running on port 8080
- Verify all 3 C# scripts attached to same GameObject
- Check Unity Console for server startup message

**"Vision analysis timeout"**
- Unity must be in Play Mode for screenshots
- Check Unity scene has adequate lighting
- Verify scene has objects to analyze

### **✅ Success Indicators**
- Server starts on available port (5004+)
- Unity Console: "Server started on http://127.0.0.1:8080/"  
- Vision analysis returns detailed object descriptions
- Agent completes verification loop successfully

## 🎉 **System Verification**

**Test with this prompt:**
```
"Clear the scene, then create a fox next to a green tree. Use detailed vision analysis to make sure the final result is correct"
```

**Expected behavior:**
1. Clears existing objects
2. Downloads fox GLB model  
3. Creates green cylinder tree
4. Captures scene screenshot
5. Vision analysis describes objects
6. Self-verification confirms success
7. ✅ "Task completed successfully"

---

🚀 **Your VLM Scene Architect is ready to create, verify, and perfect 3D scenes with superhuman persistence!**
