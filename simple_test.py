#!/usr/bin/env python3

# Simple Test - See how your prompt becomes Unity commands

import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")

client = OpenAI(api_key=OPENAI_API_KEY)

def test_your_prompt():
    prompt = "create a blue ball"
    
    print(f"🎯 Your Prompt: '{prompt}'")
    print("🤖 Asking OpenAI to convert to Unity commands...")
    print()
    
    system_prompt = """Convert the user's request into JSON commands for Unity. 
    Return a JSON object with a "commands" array containing objects like:
    {"command": "spawn", "object_name": "sphere", "position": {"x": 0, "y": 0, "z": 0}, "color": {"r": 0, "g": 0, "b": 1}}
    
    Available objects: cube, sphere, capsule, cylinder, plane
    Available commands: spawn, clear_scene"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content
        print("✅ OpenAI Response:")
        print(result)
        print()
        print("🎮 This would normally be sent to Unity to create 3D objects!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 VLM Scene Architect - Quick Test")
    print("=" * 40)
    test_your_prompt() 