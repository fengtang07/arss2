# tools.py (Upgraded for VLM, Simulation, and Queries)
#
# Defines the suite of tools that the Autonomous Agent can use to interact
# with the world (Unity, Web, GUI, Code). Each function is decorated to
# be recognizable by the OpenAI tool-calling API.

import requests
import json
import os
from pathlib import Path
import config
import base64
import pyautogui # For real GUI automation

# --- Helper Function for Unity Communication ---
def send_command_to_unity(endpoint: str, payload: dict, method: str = "POST") -> dict:
    """Helper function to send requests to the Unity API."""
    url = f"{config.UNITY_API_URL}/{endpoint}"
    try:
        if method.upper() == "POST":
            # Use curl as a workaround for Unity HttpServer Python compatibility issue
            import subprocess
            json_data = json.dumps(payload)
            
            curl_cmd = [
                'curl', '-X', 'POST', url,
                '-H', 'Content-Type: application/json',
                '-d', json_data,
                '-s', '-w', '%{http_code}'
            ]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=15)
            response_text = result.stdout
            
            # Extract status code (last 3 characters)
            if len(response_text) >= 3:
                status_code = int(response_text[-3:])
                response_body = response_text[:-3]
                
                if status_code == 200:
                    print(f"UNITY API SUCCESS: Called endpoint '{endpoint}'. Response: {response_body}")
                    return {"success": True, "data": response_body}
                else:
                    print(f"UNITY API ERROR: Status {status_code}. Response: {response_body}")
                    return {"success": False, "error": f"HTTP {status_code}: {response_body}"}
            else:
                return {"success": False, "error": "Invalid response from Unity"}
        else: # Default to GET
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                response_json = response.json()
                print(f"UNITY API SUCCESS: Called '{endpoint}'. Response: {response_json.get('message')}")
                return {"success": True, "data": response_json.get('message')}
            else:
                error_message = f"Unity API Error: Status {response.status_code} - {response.text}"
                print(error_message)
                return {"success": False, "error": error_message}
            
    except Exception as e:
        error_message = f"UNITY API ERROR: Failed to call endpoint '{endpoint}'. Is Unity in Play mode? Error: {e}"
        print(error_message)
        return {"success": False, "error": error_message}

# --- Core Tools ---
def spawn_object(object_name: str, position: dict, scale: dict = {"x": 1.0, "y": 1.0, "z": 1.0}, color: dict = None) -> dict:
    """
    Spawns a primitive object (cube, sphere, etc.) or a pre-existing asset/model in the Unity scene.
    
    :param object_name: The name of the primitive ('cube', 'sphere') or the name of the model file (e.g., 'classic_cola_can.glb').
    :param position: A dictionary with 'x', 'y', 'z' coordinates.
    :param scale: An optional dictionary with 'x', 'y', 'z' scale values.
    :param color: An optional dictionary with 'r', 'g', 'b' values (0-1) for primitives.
    """
    # Build the structured payload for the new ARSS API
    payload = {
        "object_name": object_name,
        "position": {"x": float(position["x"]), "y": float(position["y"]), "z": float(position["z"])}
    }
    
    if scale:
        payload["scale"] = {"x": float(scale["x"]), "y": float(scale["y"]), "z": float(scale["z"])}
    
    if color:
        payload["color"] = {"r": float(color["r"]), "g": float(color["g"]), "b": float(color["b"])}
    
    return send_command_to_unity("spawn", payload)

def clear_scene() -> dict:
    """
    Clears all objects from the Unity scene.
    """
    # Use the new ARSS endpoint approach (no payload needed for clear_scene)
    return send_command_to_unity("clear_scene", {})

def set_lighting(preset: str) -> dict:
    """
    Sets the scene's lighting to a specified preset.
    
    :param preset: The name of the lighting preset (e.g., 'day', 'night', 'sunset').
    """
    payload = {"preset": preset}
    return send_command_to_unity("set_lighting", payload)

def attach_script_to_object(object_name: str, script_name: str) -> dict:
    """
    Attaches a C# script component to a specified GameObject in the scene.
    
    :param object_name: The name of the GameObject to attach the script to.
    :param script_name: The name of the script to attach (e.g., 'WobbleEffect'). Do not include '.cs'.
    """
    payload = {"object_name": object_name, "script_name": script_name}
    return send_command_to_unity("attach_script", payload)

# *** 1. NEW: VLM TOOL ***
def capture_and_analyze_scene(analysis_prompt: str) -> dict:
    """
    Captures the current view from the Unity camera and uses a VLM to analyze it.
    :param analysis_prompt: The question to ask the VLM about the scene image.
    """
    print(f"VISION TOOL: Capturing scene from Unity...")
    capture_result = send_command_to_unity("capture_vision", {})
    if not capture_result["success"]:
        return capture_result

    # The image is saved to Unity's project directory, so check there first
    image_path = Path("/Users/dullmanatee/My project/scene_capture.png")
    if not image_path.exists():
        # Fallback to current directory
        image_path = Path("scene_capture.png")
        if not image_path.exists():
            return {"success": False, "error": "Scene was captured but the image file was not found."}

    # --- REAL VLM ANALYSIS ---
    print(f"VISION TOOL: Analyzing image with VLM. Prompt: '{analysis_prompt}'")
    try:
        import base64
        from openai import OpenAI
        from config import OPENAI_API_KEY
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        vlm_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        simulated_response = vlm_response.choices[0].message.content
        print(f"VISION ANALYSIS RESULT: {simulated_response}")
        
    except Exception as e:
        simulated_response = f"VISION ERROR: Could not analyze image - {e}"
    
    return {"success": True, "vlm_analysis": simulated_response}

# *** 2. NEW: SIMULATION TOOL ***
def run_simulation_and_get_results(robot_name: str, target_name: str, duration: float = 10.0) -> dict:
    """
    Runs a physics-based simulation in Unity and returns the outcome.
    :param robot_name: The name of the robot object.
    :param target_name: The name of the target object.
    :param duration: How many seconds to run the simulation for.
    """
    print(f"SIMULATION TOOL: Running simulation. Robot: '{robot_name}', Target: '{target_name}'.")
    payload = {"robot_name": robot_name, "target_name": target_name, "duration": duration}
    return send_command_to_unity("run_simulation", payload)

# *** 3. NEW: QUERY TOOLS ***
def get_object_position(object_name: str) -> dict:
    """Gets the current 3D world coordinates of a named object in Unity."""
    print(f"QUERY TOOL: Getting position for '{object_name}'")
    return send_command_to_unity("get_object_position", {"object_name": object_name})

def list_all_objects() -> dict:
    """Lists the names of all objects currently in the Unity scene."""
    print(f"QUERY TOOL: Listing all objects in the scene.")
    return send_command_to_unity("list_all_objects", {})

# *** 4. NEW: REAL GUI AUTOMATION ***
def click_unity_play_button() -> dict:
    """
    Uses GUI automation to click the 'Play' button in the Unity Editor.
    NOTE: This is highly dependent on screen resolution and requires configuration.
    """
    try:
        # User must find these coordinates manually using a tool or screenshot
        # This is an example coordinate for a 1920x1080 screen.
        play_button_coords = (950, 60) 
        print(f"GUI TOOL: Clicking Unity Play button at {play_button_coords}")
        pyautogui.click(play_button_coords)
        return {"success": True, "message": f"Clicked screen at {play_button_coords}."}
    except Exception as e:
        return {"success": False, "error": f"GUI automation failed: {e}. Is pyautogui installed and configured?"}

# --- Tool 2: Web Tool ---
# This tool simulates searching for and "downloading" assets from the web.

def search_web_for_3d_model(query: str) -> dict:
    """
    Searches a mock database (simulating Sketchfab) for a 3D model.
    
    :param query: A description of the model to search for (e.g., 'fox', 'soda can').
    """
    print(f"WEB TOOL: Searching for 3D model with query: '{query}'")
    # In a real implementation, this would make an API call to Sketchfab.
    for key, model_info in config.MOCK_SKETCHFAB_DATABASE.items():
        if key in query.lower():
            print(f"WEB TOOL: Found model '{model_info['name']}'.")
            return {"success": True, "model_name": model_info['name'], "download_url": model_info['download_url']}
    print(f"WEB TOOL: No model found for query '{query}'.")
    return {"success": False, "error": f"No 3D model found for query: {query}"}

def download_and_import_model(model_name: str, download_url: str) -> dict:
    """
    Downloads a real 3D model from the web and places it in the Unity project's 'ImportedModels' directory.
    
    :param model_name: The name to save the model as (e.g., 'Low Poly Fox').
    :param download_url: The URL to the model file.
    """
    print(f"WEB TOOL: Downloading {model_name} from {download_url}")
    if "ABSOLUTE_PATH_TO_YOUR_UNITY_PROJECT" in config.UNITY_ASSETS_PATH:
        error_msg = "UNITY_ASSETS_PATH is not configured in config.py. Please set it to your project's path."
        print(f"ERROR: {error_msg}")
        return {"success": False, "error": error_msg}

    # Create a clean filename and the target directory path.
    file_extension = download_url.split('.')[-1]  # Get actual extension (.gltf, .glb, etc.)
    file_name = f"{model_name.replace(' ', '_').lower()}.{file_extension}"
    # Unity prefab name (without extension)
    unity_prefab_name = f"{model_name.replace(' ', '_').lower()}"
    import_dir = Path(config.UNITY_ASSETS_PATH) / "ImportedModels"
    import_dir.mkdir(exist_ok=True)
    file_path = import_dir / file_name

    # Check if file already exists
    if file_path.exists():
        print(f"WEB TOOL: Model {model_name} already exists at {file_path}")
        return {"success": True, "file_path": str(file_path), "model_filename": file_name, "unity_name": unity_prefab_name}

    try:
        # Actually download the file
        import urllib.request
        urllib.request.urlretrieve(download_url, file_path)
        print(f"WEB TOOL: Successfully downloaded {model_name} to {file_path}")
        return {"success": True, "file_path": str(file_path), "model_filename": file_name, "unity_name": unity_prefab_name}
    except Exception as e:
        print(f"WEB TOOL: Failed to download {model_name}: {e}")
        # Fallback: create empty placeholder
        file_path.touch()
        return {"success": False, "error": f"Download failed: {e}", "file_path": str(file_path), "model_filename": file_name}

# --- Tool 3: Code Generation Tool ---
# This tool writes new C# scripts directly into the Unity project folder.

def write_new_unity_script(script_name: str, csharp_code: str) -> dict:
    """
    Writes a new C# script file into the Unity project's 'GeneratedScripts' directory.
    
    :param script_name: The name of the script (e.g., 'WobbleEffect'). Should be a valid C# class name.
    :param csharp_code: A string containing the full C# code for the script.
    """
    print(f"CODE GEN TOOL: Writing C# script '{script_name}.cs'")
    if "ABSOLUTE_PATH_TO_YOUR_UNITY_PROJECT" in config.UNITY_ASSETS_PATH:
        error_msg = "UNITY_ASSETS_PATH is not configured in config.py. Please set it to your project's path."
        print(f"ERROR: {error_msg}")
        return {"success": False, "error": error_msg}

    script_dir = Path(config.UNITY_ASSETS_PATH) / "GeneratedScripts"
    script_dir.mkdir(exist_ok=True)
    file_path = script_dir / f"{script_name}.cs"

    try:
        with open(file_path, "w") as f:
            f.write(csharp_code)
        print(f"CODE GEN TOOL: Successfully wrote script to {file_path}")
        return {"success": True, "path": str(file_path)}
    except Exception as e:
        print(f"CODE GEN TOOL: Error writing script: {e}")
        return {"success": False, "error": str(e)}

# --- Tool 4: GUI Automation Tool (Placeholder) ---
# In a real implementation, this would use a library like askui or pyautogui.

def click_gui_element(element_description: str) -> dict:
    """
    (Placeholder) Simulates clicking on a GUI element within the Unity Editor.
    
    :param element_description: A textual description of the element to click (e.g., 'the color swatch for the main material').
    """
    message = f"GUI TOOL (MOCK): Clicking on element described as: '{element_description}'"
    print(message)
    return {"success": True, "message": message}

# --- Updated Tool Definitions for OpenAI ---
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "spawn_object",
            "description": "Spawns a primitive or imported model in the Unity scene.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of the primitive ('cube', 'sphere') or model file ('my_model.glb')."},
                    "position": {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}, "z": {"type": "number"}}},
                    "scale": {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}, "z": {"type": "number"}}},
                    "color": {"type": "object", "properties": {"r": {"type": "number"}, "g": {"type": "number"}, "b": {"type": "number"}}},
                },
                "required": ["object_name", "position"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_scene",
            "description": "Clears all objects from the Unity scene.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_lighting",
            "description": "Sets the scene's lighting to a preset.",
            "parameters": {
                "type": "object",
                "properties": {"preset": {"type": "string", "enum": ["day", "night", "sunset"]}},
                "required": ["preset"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "capture_and_analyze_scene",
            "description": "Takes a picture of the Unity scene and uses a Vision-Language Model to answer a question about it. Use this to verify results or analyze the visual state.",
            "parameters": {
                "type": "object",
                "properties": { "analysis_prompt": {"type": "string", "description": "The question to ask about the visual scene. E.g., 'Is the red cube on top of the blue sphere?'"} },
                "required": ["analysis_prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_simulation_and_get_results",
            "description": "Executes a physics simulation for a set duration to see if a robot can reach a target. Generates physical data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "robot_name": {"type": "string"},
                    "target_name": {"type": "string"},
                    "duration": {"type": "number", "description": "Maximum seconds to run the simulation."}
                },
                "required": ["robot_name", "target_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_object_position",
            "description": "Returns the current {x, y, z} world coordinates of any object in the scene.",
            "parameters": { "type": "object", "properties": {"object_name": {"type": "string"}}, "required": ["object_name"], },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_objects",
            "description": "Returns a list of names of all objects the agent has created in the scene.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click_unity_play_button",
            "description": "Performs a GUI click on the Unity Editor's play button. Use this to start a simulation that requires manual starting.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web_for_3d_model",
            "description": "Searches the web (a mock database) for a 3D model if it's not a basic primitive.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "A search query like 'soda can' or 'desk lamp'."}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "download_and_import_model",
            "description": "Downloads a model found with the web search tool and places it in the Unity project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "The name of the model, e.g., 'Classic Cola Can'."},
                    "download_url": {"type": "string", "description": "The download URL provided by the search tool."},
                },
                "required": ["model_name", "download_url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_new_unity_script",
            "description": "Writes a new C# MonoBehaviour script to create novel behaviors not supported by the API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_name": {"type": "string", "description": "A valid C# class name for the script, e.g., 'WobbleEffect'."},
                    "csharp_code": {"type": "string", "description": "The full, complete C# code for the MonoBehaviour script."},
                },
                "required": ["script_name", "csharp_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "attach_script_to_object",
            "description": "Attaches a previously written C# script to an object in the scene.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "The name of the target GameObject."},
                    "script_name": {"type": "string", "description": "The name of the script component to attach."},
                },
                "required": ["object_name", "script_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click_gui_element",
            "description": "(Placeholder) Simulates clicking on a GUI element in the Unity Editor for tasks not covered by the API.",
            "parameters": {
                "type": "object",
                "properties": {"element_description": {"type": "string", "description": "A clear, textual description of the GUI element to be clicked."}},
                "required": ["element_description"],
            },
        },
    },
]

# A dictionary to map tool names to their actual functions.
AVAILABLE_TOOLS = {
    "spawn_object": spawn_object,
    "clear_scene": clear_scene,
    "set_lighting": set_lighting,
    "capture_and_analyze_scene": capture_and_analyze_scene,
    "run_simulation_and_get_results": run_simulation_and_get_results,
    "get_object_position": get_object_position,
    "list_all_objects": list_all_objects,
    "click_unity_play_button": click_unity_play_button,
    "search_web_for_3d_model": search_web_for_3d_model,
    "download_and_import_model": download_and_import_model,
    "write_new_unity_script": write_new_unity_script,
    "attach_script_to_object": attach_script_to_object,
    "click_gui_element": click_gui_element,
} 