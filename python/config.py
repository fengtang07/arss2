# config.py
#
# Configuration file for VLM Scene Architect Agent
# Stores API keys, paths, and system settings

import os

# --- OpenAI API Configuration ---
# Get API key from environment variable - REQUIRED for security
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configuration - GPT-4o required for vision analysis
OPENAI_MODEL = "gpt-4o"  # REQUIRED: Must support tool calling and vision

# --- Unity API Configuration ---
# Unity HTTP server endpoint
UNITY_API_URL = "http://127.0.0.1:8080"

# API timeout settings
UNITY_API_TIMEOUT = 15  # seconds
UNITY_RETRY_ATTEMPTS = 3

# --- Vision Analysis Configuration ---
# Screenshot settings
UNITY_SCREENSHOT_PATH = "scene_capture.png"
VISION_MAX_RETRIES = 2

# --- Web Tool Configuration ---
# For downloading GLB models from repositories
MOCK_SKETCHFAB_DATABASE = {
    "fox": {
        "name": "Low Poly Fox",
        "uid": "f23a1a3d387b42a78a6e39a65a719beb", 
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/Fox/glTF-Binary/Fox.glb"
    },
    "water bottle": {
        "name": "Water Bottle",
        "uid": "a1b2c3d4e5f67890a1b2c3d4e5f67890",
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/WaterBottle/glTF-Binary/WaterBottle.glb"
    },
    "bottle": {
        "name": "Water Bottle", 
        "uid": "a1b2c3d4e5f67890a1b2c3d4e5f67890",
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/WaterBottle/glTF-Binary/WaterBottle.glb"
    },
    "desk lamp": {
        "name": "Lantern",
        "uid": "b2c3d4e5f67890a1b2c3d4e5f67890a1", 
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/Lantern/glTF-Binary/Lantern.glb"
    },
    "lamp": {
        "name": "Lantern",
        "uid": "b2c3d4e5f67890a1b2c3d4e5f67890a1",
        "download_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/Lantern/glTF-Binary/Lantern.glb"
    }
}

# --- Project Paths ---
# Unity project Assets folder path
# Update this to match YOUR Unity project location
UNITY_ASSETS_PATH = os.getenv("UNITY_ASSETS_PATH", "/Users/dullmanatee/My project/Assets")

# Model download directory
MODEL_DOWNLOAD_DIR = os.path.join(UNITY_ASSETS_PATH, "ImportedModels")

# --- Flask Server Configuration ---
# Web interface settings
FLASK_HOST = "127.0.0.1"
FLASK_PORT_RANGE = range(5004, 5010)  # Try ports in this range
FLASK_DEBUG = False

# --- Agent Behavior Configuration ---
# Forced iteration settings
MAX_AGENT_ITERATIONS = 10  # Prevent infinite loops
VERIFICATION_REQUIRED = True  # Always verify with vision
SELF_CRITICAL_MODE = True  # Enable self-correction

# --- Logging Configuration ---
ENABLE_DETAILED_LOGGING = True
LOG_UNITY_API_CALLS = True
LOG_VISION_ANALYSIS = True
LOG_TOOL_EXECUTION = True

# --- Security Settings ---
# In production, these should be environment variables
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
API_RATE_LIMIT = 60  # requests per minute

# --- Validation ---
def validate_config():
    """Validate critical configuration settings"""
    if not OPENAI_API_KEY:
        raise ValueError("⚠️  OPENAI_API_KEY environment variable not set! Please set it before running the system.")
    
    if not os.path.exists(UNITY_ASSETS_PATH):
        print(f"Warning: Unity Assets path '{UNITY_ASSETS_PATH}' does not exist.")
        print("Update UNITY_ASSETS_PATH in config.py or set UNITY_ASSETS_PATH environment variable.")
    
    print("✅ Configuration validated successfully!")

if __name__ == "__main__":
    validate_config() 