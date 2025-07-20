# 🎮 Unity Setup Guide - VLM Scene Architect

**Complete setup for the Vision-Language Model Scene Architect in Unity**

## ✅ **Prerequisites**
- Unity 2021.3 LTS or later (free)
- The 3 C# script files from this project
- Basic Unity knowledge (creating GameObjects, adding components)

## 🚀 **5-Minute Setup**

### **1. Install Unity**
- Download Unity Hub: https://unity.com/download
- Install Unity 2021.3 LTS (free Personal license)
- Create account if needed

### **2. Create New Project**
```
Unity Hub → New Project → 3D Core Template
Name: "VLM Scene Architect" 
Location: Choose your preferred folder
```

### **3. Add Required Scripts**
**Copy these 3 files from the `unity/` folder to your Unity project:**
```
📁 unity/HttpServer.cs      → Assets/Scripts/HttpServer.cs
📁 unity/SceneController.cs → Assets/Scripts/SceneController.cs  
📁 unity/CommandModels.cs   → Assets/Scripts/CommandModels.cs
```

**Create Scripts folder if needed:**
- Right-click `Assets` → Create → Folder → Name it "Scripts"

### **4. Setup Scene Manager GameObject**
1. **Create empty GameObject:**
   - Right-click in Hierarchy → Create Empty
   - Name it: **"SceneManager"**

2. **Add all 3 script components:**
   - Select "SceneManager" GameObject
   - Click "Add Component" → Search "HttpServer" → Add
   - Click "Add Component" → Search "SceneController" → Add  
   - Click "Add Component" → Search "CommandModels" → Add

### **5. Configure Scene**
**Important settings for proper operation:**

1. **Set up Camera** (if needed):
   - Main Camera position: (0, 5, -10)
   - Rotation: (20, 0, 0) for good overview

2. **Add Directional Light** (if missing):
   - Right-click Hierarchy → Light → Directional Light
   - Position: (0, 3, 0), Rotation: (50, -30, 0)

### **6. Test the Setup** 🧪
1. **Press Play ▶️** in Unity
2. **Check Console** for success message:
   ```
   [HttpServer] Server started and listening on http://127.0.0.1:8080/
   ```
3. **If you see this message → ✅ Unity setup complete!**

## 🔧 **Advanced Configuration**

### **🎯 Optimal Scene Settings**
```
Camera Position: (0, 5, -10)  # Good overview angle
Camera Rotation: (20, 0, 0)   # Slight downward angle
Directional Light: Enabled    # Required for vision analysis
Background: Solid Color       # Better for vision processing
```

### **📊 Component Verification**
**Your SceneManager GameObject should have:**
- ✅ Transform (default)
- ✅ HttpServer (C# Script)
- ✅ SceneController (C# Script) 
- ✅ CommandModels (C# Script)

### **🔍 Console Messages Reference**
```bash
✅ SUCCESS: "[HttpServer] Server started and listening on http://127.0.0.1:8080/"
❌ ERROR: "NullReferenceException" → Scripts not attached properly
❌ ERROR: "Port already in use" → Close other Unity instances
```

## 🚨 **Troubleshooting**

### **❌ Common Issues**

**"No console message when pressing Play"**
- Check all 3 scripts are attached to SceneManager GameObject
- Verify script files are in Assets/Scripts/ folder
- Look for compile errors in Console

**"Failed to start server" or port errors**
- Close other Unity instances
- Restart Unity if needed
- Check no other apps using port 8080

**"Objects not spawning when testing"**
- Unity MUST be in Play Mode
- Check Hierarchy for new objects (they might spawn outside camera view)
- Verify no compile errors in scripts

**"Vision analysis fails"**
- Add Directional Light to scene
- Ensure camera has clear view of spawn area
- Check scene has adequate lighting

### **⚡ Quick Fixes**
```bash
Problem: Scripts won't attach
Solution: Check for compile errors in Console tab

Problem: Server won't start  
Solution: File → Build Settings → Switch Platform to current OS

Problem: Can't see spawned objects
Solution: Select spawned object in Hierarchy, press 'F' to focus camera
```

## 🎮 **Usage with VLM Agent**

### **🔄 Workflow**
1. **Start Unity** → Press Play ▶️
2. **Start Python agent** → `python main.py`
3. **Open browser** → `http://localhost:5004`
4. **Send commands** → Agent creates objects in Unity
5. **Watch vision analysis** → GPT-4o verifies results

### **💡 Pro Tips**
- **Keep Unity in Play Mode** while using the agent
- **Use Scene view** to manually inspect created objects
- **Check Console** for detailed API call logs
- **Press 'F'** to focus camera on selected objects
- **Use mouse** to rotate Scene view and explore

## ✅ **Verification Test**

**After setup, test with this command in the web interface:**
```
"Create a blue sphere at position x=0, y=1, z=0"
```

**Expected Unity behavior:**
1. ✅ Blue sphere appears in scene
2. ✅ Console shows: "Successfully spawned 'Primitive_sphere'"
3. ✅ Object visible in Hierarchy as "Primitive_sphere"
4. ✅ Agent reports successful vision verification

---

🎉 **Unity is now ready for autonomous scene creation with vision verification!**

**Next step:** Run `python main.py` to start the VLM agent and begin creating scenes! 