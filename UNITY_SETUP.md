# 🎮 Unity Setup Checklist

## ✅ What You Need
- Unity 2021.3 LTS or later (free)
- The two C# script files from this folder

## 🚀 5-Minute Setup

### 1. Install Unity
- Download Unity Hub: https://unity.com/download
- Install Unity 2021.3 LTS (free)

### 2. Create Project
- New Project → 3D Core Template
- Name: "VLM Scene Architect"

### 3. Add Scripts
```
Copy to Unity project:
📁 Assets/Scripts/HttpServer.cs     ← Copy this file
📁 Assets/Scripts/SceneBuilder.cs   ← Copy this file
```

### 4. Setup GameObject
1. **Create** empty GameObject (right-click Hierarchy → Create Empty)
2. **Name** it "SceneManager"
3. **Add Components:**
   - Click "Add Component" → Search "HttpServer" → Add
   - Click "Add Component" → Search "SceneBuilder" → Add

### 5. Test It!
1. **Press Play ▶️** in Unity
2. **Check Console** - should see: `[HttpServer] Server started and listening on http://127.0.0.1:8080/`
3. **Go to web browser**: http://127.0.0.1:5001
4. **Type**: "create a blue ball"
5. **Watch Unity**: A blue sphere should appear! 🎉

## 🚨 Troubleshooting
- **No console message?** → Scripts not attached properly
- **"Failed to fetch"?** → Unity not in Play Mode
- **Nothing spawns?** → Check Unity Console for errors

## 💡 Tips
- Keep Unity in Play Mode while using the web interface
- Press Space in Unity to focus the scene view
- Use mouse to rotate camera and see your creations! 