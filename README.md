# VLM Scene Architect v2.0

🤖 **A self-critical AI agent that creates, simulates, and visually verifies 3D scenes in Unity using natural language commands.**

## ✨ **What Makes This Special**

- **🔍 Vision-Powered Verification**: Uses GPT-4o vision to actually SEE and verify what it creates
- **🔄 Forced Iteration**: Never accepts failure - keeps improving until vision confirms success  
- **🌐 GLB Model Integration**: Downloads real 3D models from the web (KhronosGroup/Sketchfab)
- **🎯 Self-Critical**: Detects when "bird" ≠ "fox" and automatically fixes it
- **⚡ Real-time Unity Integration**: Live 3D scene manipulation with instant feedback

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+ with pip
- Unity 2021.3 LTS or later
- OpenAI API key (GPT-4o vision access)

### **Installation**
```bash
# Clone repository
git clone https://github.com/fengtang07/arss2.git
cd arss2

# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Run the system (installs dependencies automatically)
./run.sh
```

### **Setup Unity**
1. Create Unity 3D project
2. Copy files from `unity/` to `Assets/Scripts/`
3. Create empty GameObject → Add all 3 scripts as components
4. Press Play ▶️

**→ Open browser: `http://localhost:5004`**

## 📁 **Project Structure**

```
📦 VLM Scene Architect v2.0
├── 🐍 python/              # Core Python application
│   ├── agent.py            # Main VLM agent with forced iteration
│   ├── tools.py            # All tool definitions and implementations
│   ├── main.py             # Flask web server and UI
│   ├── config.py           # Configuration and API keys
│   └── requirements.txt    # Python dependencies
├── 🎮 unity/               # Unity C# scripts
│   ├── HttpServer.cs       # Unity HTTP API server
│   ├── SceneController.cs  # Scene management & object spawning
│   └── CommandModels.cs    # Data structures for commands
├── 📚 docs/                # Documentation
│   ├── README.md           # Complete system documentation
│   └── UNITY_SETUP.md      # Unity configuration guide
├── run.sh                  # Launch script
└── .gitignore             # Git ignore rules
```

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

## 🎮 **Example Usage**

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

## 📚 **Documentation**

- **[Complete Documentation](docs/README.md)** - Full system guide with examples
- **[Unity Setup Guide](docs/UNITY_SETUP.md)** - Step-by-step Unity configuration
- **[Python API](python/)** - Core application code and tools

## 🔧 **Advanced Features**

- **🎯 Forced Iteration**: Agent cannot declare success until vision confirms it
- **🌐 Web Model Integration**: KhronosGroup sample models with automatic caching
- **👁️ Vision Verification**: GPT-4o detailed visual analysis and verification
- **🛡️ Secure Configuration**: Environment variable API key management
- **📊 Comprehensive Logging**: Detailed debugging and monitoring

## 🚨 **Troubleshooting**

**Quick fixes:**
- **API Key**: `export OPENAI_API_KEY="your-key"`
- **Unity**: Must be in Play Mode with all 3 scripts attached
- **Port**: System auto-detects available ports (5004+)

**For detailed troubleshooting:** See [docs/README.md](docs/README.md)

## 🎉 **System Verification**

**Test with this prompt:**
```
"Clear the scene, then create a fox next to a green tree. Use detailed vision analysis to make sure the final result is correct"
```

**Expected behavior:**
1. ✅ Clears existing objects → Downloads fox GLB → Creates green tree
2. ✅ Vision analysis describes objects → Self-verification confirms success
3. ✅ "Task completed successfully"

---

🚀 **Your VLM Scene Architect is ready to create, verify, and perfect 3D scenes with superhuman persistence!**

**Repository:** https://github.com/fengtang07/arss2 