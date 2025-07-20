#!/usr/bin/env python3

# Quick test: Skip OpenAI, send hardcoded command to Unity

import requests
import json

# Test sending a command directly to Unity
def test_unity_direct():
    commands = [
        {
            "command": "spawn",
            "object_name": "sphere", 
            "position": {"x": 2, "y": 0, "z": 0},
            "color": {"r": 0, "g": 0, "b": 1}
        }
    ]
    
    try:
        print("🎯 Sending test command to Unity...")
        response = requests.post(
            "http://127.0.0.1:8080",
            headers={"Content-Type": "application/json"},
            data=json.dumps(commands),
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Unity responded:", response.text)
            print("🎉 Check Unity - you should see a blue sphere at X=2!")
        else:
            print(f"❌ Unity error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🧪 Quick Unity Test (No OpenAI needed)")
    print("=" * 40)
    test_unity_direct() 