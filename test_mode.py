#!/usr/bin/env python3

# Test Mode - VLM Scene Architect (No Unity Required)
# This shows you how the AI processes natural language into Unity commands

import os
import json
from openai import OpenAI

# Your API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")

client = OpenAI(api_key=OPENAI_API_KEY)

def test_prompt_to_commands(prompt):
    """Test how natural language gets converted to Unity commands"""
    
    system_prompt = """
    You are an expert AI assistant that translates natural language commands into structured JSON for the Unity game engine.
    Your task is to parse the user's request and generate a list of commands to manipulate objects in a 3D scene.

    You must only respond with a valid JSON list of objects. Do not include any other text, explanations, or markdown.

    The available commands are:
    1. `spawn`: Creates a new object.
       - `object_name` (string): The name of the primitive to spawn (e.g., "cube", "sphere", "capsule", "cylinder", "plane").
       - `position` (dict): A dictionary with "x", "y", and "z" float values.
       - `scale` (dict, optional): A dictionary with "x", "y", and "z" float values. Defaults to 1,1,1.
       - `color` (dict, optional): A dictionary with "r", "g", and "b" float values between 0.0 and 1.0.

    2. `clear_scene`: Removes all previously spawned objects.
       - This command has no parameters.
    """

    try:
        print(f"🤖 Processing: '{prompt}'")
        print("⏳ Asking OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        response_content = response.choices[0].message.content
        parsed_json = json.loads(response_content)

        # Find the command list
        command_list = None
        for key, value in parsed_json.items():
            if isinstance(value, list):
                command_list = value
                break

        if command_list:
            print("✅ OpenAI Response:")
            print(json.dumps(command_list, indent=2))
            return command_list
        else:
            print("❌ No command list found in response")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🧪 VLM Scene Architect - Test Mode")
    print("=" * 50)
    print("This shows how your prompts get converted to Unity commands")
    print("(Unity not required for this test)")
    print("")
    
    # Test prompts
    test_prompts = [
        "create a blue ball",
        "make a red cube at x=2, y=0, z=1 and a green sphere above it",
        "clear the scene",
        "build a simple house with walls and a roof"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎯 Test {i}:")
        test_prompt_to_commands(prompt)
        print("-" * 30) 