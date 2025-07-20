# config.py
#
# Stores configuration variables and API keys for the agent.
# It's best practice to load these from environment variables in a real application.

import os

# --- OpenAI API Configuration ---
# IMPORTANT: Replace "YOUR_OPENAI_API_KEY" with your actual key.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o" # Use a model that supports tool calling, like gpt-4o or gpt-4-turbo

# --- Unity API Configuration ---
# The address of the Unity application's HTTP server.
UNITY_API_URL = "http://127.0.0.1:8080"

# --- Web Tool Configuration (Sketchfab) ---
# For this example, we will not use a real API key, but in a real-world scenario,
# you would authenticate with the Sketchfab API here.
SKETCHFAB_API_TOKEN = "YOUR_SKETCHFAB_API_TOKEN"
# A mock database of models the agent can "find" online.
# In a real implementation, this would be the result of an actual API call.
MOCK_SKETCHFAB_DATABASE = {
    "fox": {
        "name": "Low Poly Fox",
        "uid": "f23a1a3d387b42a78a6e39a65a719beb",
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/Fox/glTF-Binary/Fox.glb" # Real working model
    },
    "soda can": {
        "name": "Water Bottle",
        "uid": "a1b2c3d4e5f67890a1b2c3d4e5f67890",
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/WaterBottle/glTF-Binary/WaterBottle.glb" # Real working model
    },
    "desk lamp": {
        "name": "Lantern", 
        "uid": "b2c3d4e5f67890a1b2c3d4e5f67890a1",
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/Lantern/glTF-Binary/Lantern.glb" # Real working model
    }
}

# --- Project Paths ---
# The path to the Unity project's Assets folder.
# IMPORTANT: Update this to the absolute path of YOUR Unity project's Assets folder.
# Example: "C:/Users/YourUser/Documents/ARSS_Unity_Project/Assets"
UNITY_ASSETS_PATH = "ABSOLUTE_PATH_TO_YOUR_UNITY_PROJECT/Assets" 