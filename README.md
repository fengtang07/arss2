# ARSS-2: Autonomous Robotic Scene Synthesizer

🤖 **An advanced agentic system that leverages Vision-Language Models (VLMs) to autonomously generate and verify complex 3D scenes within the Unity engine.**

ARSS-2 is driven by natural language and can reason about, create, and iteratively refine 3D environments, bridging the gap between descriptive goals and high-fidelity simulated data. The system is built around a self-critical **Observe-Orient-Decide-Act (OODA) loop**, where the agent uses visual analysis to perceive its own actions and improve its performance until the user's objective is met.

## 🌟 **Core Features**

### **🧠 VLM-Powered Scene Generation**
Utilizes GPT-4o to interpret high-level user prompts, plan sequences of actions, and execute them in a live Unity environment.

### **🔍 Self-Correction via Visual Feedback**  
The agent captures screenshots of the Unity scene and uses VLM analysis to verify its work against the original request. If a discrepancy is found (e.g., a "bird" is created instead of a "fox"), the system automatically enters an iteration loop to correct the error.

### **🛠️ Dynamic Tool Use & Program Synthesis**
- **Web Integration**: Can search for and download 3D models (GLB/glTF) from the web and import them directly into the Unity project at runtime
- **Code Generation**: Capable of writing new C# scripts to create novel Unity components and behaviors that are not available through its core toolset

### **⚡ Real-time Unity Engine Control**
Communicates with a live Unity instance via a custom HTTP API to spawn objects, control lighting, run physics simulations, and query the state of the scene.

### **🔄 Forced Iteration Protocol**
The agent is explicitly programmed to not accept failure. It must continue to iterate and refine the scene until its own vision analysis confirms that the output matches the user's request, ensuring a high-quality result.

## 🎯 **How It Works**

The system operates on a continuous feedback loop that ensures the final output is a faithful representation of the user's prompt:

### **1. User Prompt** 
The user provides a high-level goal, such as *"Create a scene with a fox standing next to a green tree under sunset lighting."*

### **2. Planning & Decomposition**
The AutonomousAgent breaks the goal down into a series of concrete actions using its available tools (e.g., `set_lighting`, `search_web_for_3d_model`, `spawn_object`).

### **3. Execution & Action**
The agent executes the plan by sending commands to the Unity SceneController. This may involve downloading a 3D model of a fox and spawning it alongside a green cylinder primitive.

### **4. Observation & Vision Analysis**  
The agent calls `capture_and_analyze_scene`, which takes a screenshot from Unity and sends it to the VLM with a detailed query, such as *"Describe all objects, their colors, positions, and shapes in detail"*.

### **5. Self-Evaluation & Iteration**
The agent critically evaluates the VLM's description. If the analysis does not clearly describe a "fox" next to a "tree," it acknowledges the failure, formulates a new plan to fix the scene (e.g., adjusting object scale, position, or finding a new model), and returns to the execution step.

### **6. Success**
The process concludes only when the vision analysis explicitly confirms that the scene matches the original request.

## 📁 **Project Structure**

```
📦 ARSS-2
├── 🐍 python/              # Core Python application
│   ├── agent.py            # The primary VLM agent with its self-correction loop
│   ├── tools.py            # Definitions and implementations for all agent tools
│   ├── main.py             # Flask web server and UI for interaction
│   ├── config.py           # System configuration, API keys, and paths
│   └── requirements.txt    # Python dependencies
├── 🎮 unity/               # C# scripts for the Unity environment
│   ├── HttpServer.cs       # API server that listens for commands from the Python agent
│   ├── SceneController.cs  # Handles scene management, object spawning, and simulations
│   └── CommandModels.cs    # Data structures for API commands and responses
├── 📚 docs/                # Documentation
│   ├── README.md           # Full system documentation
│   └── UNITY_SETUP.md      # Guide for configuring the Unity project
├── run.sh                  # Main launch script
└── .gitignore              # Standard gitignore for Python/Unity projects
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Unity 2021.3 LTS or later  
- An OpenAI API key with GPT-4o access

### **Installation & Setup**

#### **1. Clone the Repository**
```bash
git clone https://github.com/fengtang07/arss2.git
cd arss2
```

#### **2. Configure Environment**
Set your OpenAI API key as an environment variable. This is required for the agent to function.
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

#### **3. Set Up Unity Project**
1. Create a new 3D project in Unity
2. Follow the instructions in [`docs/UNITY_SETUP.md`](docs/UNITY_SETUP.md) to copy the C# scripts and configure the SceneManager object
3. Press **Play** in the Unity Editor. You should see a confirmation message in the console that the server has started.

#### **4. Launch the Agent**
Use the provided shell script to install dependencies and start the web server:
```bash
./run.sh
```

Navigate to **http://localhost:5004** (or the port specified in the terminal) in your browser to interact with the agent.

## 🎮 **Example Usage**

### **Complex Scene Creation**
```
User: "Create a fox standing next to a green tree under sunset lighting"
→ Agent searches for fox 3D model → Downloads GLB file
→ Creates green cylinder tree → Sets sunset lighting  
→ Vision analysis: "fox-like shape next to green vertical structure"
→ Adjusts positioning and scale → Iterates until perfect
→ ✅ "Successfully created fox next to tree with sunset lighting"
```

### **Self-Correction in Action**
```
User: "Place a realistic fox in the forest scene"
→ Agent spawns model → Vision: "appears to be a bird-like object"
→ 🔄 Agent detects mismatch → Searches for different fox model
→ Downloads better model → Respawns → Adjusts scale and position
→ Vision: "orange and white fox with distinct features clearly visible"
→ ✅ Success confirmed through visual verification
```

## 📚 **Documentation**

- **[Complete System Documentation](docs/README.md)** - Detailed technical guide with advanced features
- **[Unity Setup Guide](docs/UNITY_SETUP.md)** - Step-by-step Unity configuration instructions  
- **[Python API Reference](python/)** - Core application code and tool implementations

## 🔧 **Advanced Capabilities**

- **🎯 Self-Critical OODA Loop**: Never accepts failure, always iterates to perfection
- **🌐 Dynamic Web Integration**: Real-time GLB model discovery and import from online repositories
- **👁️ Vision-Guided Verification**: GPT-4o visual analysis ensures output fidelity  
- **🛡️ Enterprise Security**: Environment-based API key management
- **📊 Comprehensive Instrumentation**: Detailed logging and performance monitoring
- **🔄 Fault Tolerance**: Robust error handling with automatic retry mechanisms

## 🚨 **Troubleshooting**

**Quick Solutions:**
- **API Key**: `export OPENAI_API_KEY="your-key"`
- **Unity Connection**: Ensure Unity is in Play Mode with all scripts attached
- **Port Conflicts**: System auto-detects available ports (5004+)

**For comprehensive troubleshooting:** See [docs/README.md](docs/README.md)

## 🎉 **System Verification**

**Test the complete OODA loop with:**
```
"Create a scene with a fox standing next to a green tree under sunset lighting. Make sure everything looks realistic and properly positioned."
```

**Expected autonomous behavior:**
1. ✅ **Observe**: Analyzes user request and current scene state
2. ✅ **Orient**: Plans multi-step action sequence with contingencies  
3. ✅ **Decide**: Executes optimal tool usage strategy
4. ✅ **Act**: Manipulates Unity environment and verifies results
5. ✅ **Iterate**: Self-corrects until vision analysis confirms success

---

🚀 **ARSS-2 represents the cutting edge of autonomous agentic systems for 3D content generation, combining the power of large language models with real-time environmental feedback to achieve unprecedented levels of scene synthesis fidelity.**

**Repository:** https://github.com/fengtang07/arss2 