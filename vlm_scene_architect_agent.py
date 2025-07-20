# vlm_scene_architect_agent.py
#
# This script is the core of the VLM Scene Architect project.
# It performs the following functions:
# 1. Runs a Flask web server to provide a simple front-end and an API endpoint.
# 2. Accepts natural language prompts from a user (e.g., "place a cube at the origin and a sphere at x=5").
# 3. Uses the OpenAI API (GPT-4o) to parse the natural language and convert it into a structured
#    list of JSON commands that Unity can understand.
# 4. Sends these JSON commands to the Unity application, which must be running and listening.
#
# Before running, make sure to install the required libraries:
# pip install Flask openai requests

import os
import requests
import json
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# --- Configuration ---
# IMPORTANT: Replace with your actual OpenAI API key.
# It's recommended to use environment variables for security.
# For example: OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")

# The address of the Unity application's HTTP server.
# Make sure this matches the address your Unity app is listening on.
UNITY_SERVER_URL = "http://127.0.0.1:8080"

# --- Initialization ---
app = Flask(__name__)
try:
    # Initialize OpenAI client with proper error handling
    if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY":
        client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        client = None
        print("⚠️  OPENAI_API_KEY not set properly!")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please make sure your OPENAI_API_KEY is set correctly.")
    client = None


# --- Core Agent Logic ---

def generate_unity_commands_from_prompt(prompt):
    """
    Uses the OpenAI API to convert a natural language prompt into a list of
    structured JSON commands for Unity.

    Args:
        prompt (str): The natural language command from the user.

    Returns:
        list: A list of dictionaries, where each dictionary is a command for Unity.
              Returns None if an error occurs.
    """
    if not client:
        print("OpenAI client not initialized.")
        return None

    # This is the system prompt that instructs the LLM on how to behave.
    # It defines the "API" that the LLM should generate JSON for.
    # This is a critical part of making the agent reliable.
    system_prompt = """
    You are an expert AI assistant that translates natural language commands into structured JSON for the Unity game engine.
    Your task is to parse the user's request and generate a list of commands to manipulate objects in a 3D SceneBuilder.cs.

    You must only respond with a valid JSON list of objects. Do not include any other text, explanations, or markdown.

    The available commands are:
    1. `spawn`: Creates a new object.
       - `object_name` (string): The name of the primitive to spawn (e.g., "cube", "sphere", "capsule", "cylinder", "plane").
       - `position` (dict): A dictionary with "x", "y", and "z" float values.
       - `scale` (dict, optional): A dictionary with "x", "y", and "z" float values. Defaults to 1,1,1.
       - `color` (dict, optional): A dictionary with "r", "g", and "b" float values between 0.0 and 1.0.

    2. `clear_scene`: Removes all previously spawned objects.
       - This command has no parameters. If the user asks to "start over", "clear the SceneBuilder.cs", or "delete everything", use this.

    Example user prompt: "Create a red cube at (2, 0, 1) and a blue sphere at the origin with a scale of 2."
    Your JSON response should be:
    [
        {
            "command": "spawn",
            "object_name": "cube",
            "position": {"x": 2.0, "y": 0.0, "z": 1.0},
            "color": {"r": 1.0, "g": 0.0, "b": 0.0}
        },
        {
            "command": "spawn",
            "object_name": "sphere",
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "scale": {"x": 2.0, "y": 2.0, "z": 2.0},
            "color": {"r": 0.0, "g": 0.0, "b": 1.0}
        }
    ]

    Example user prompt: "Clear the SceneBuilder.cs."
    Your JSON response should be:
    [
        {
            "command": "clear_scene"
        }
    ]
    """

    try:
        print(f"Sending prompt to OpenAI: {prompt}")
        
        # Simplified system prompt for Unity JsonUtility compatibility
        simple_system_prompt = """You are a Unity 3D scene builder. Convert user requests into JSON commands.
        
        Return a JSON object with a "commands" array. Each command has:
        - "command": "spawn" or "clear_scene"  
        - "object_name": "cube", "sphere", "capsule", "cylinder", or "plane"
        - "position": {"x": 0.0, "y": 0.0, "z": 0.0} (always use decimals like 0.0, 1.0, 2.0)
        - "color": {"r": 1.0, "g": 0.0, "b": 0.0} (optional, always use decimals 0.0-1.0)
        - "scale": {"x": 1.0, "y": 1.0, "z": 1.0} (optional, always use decimals)
        
        IMPORTANT: Always use decimal format (0.0, 1.0, 2.0) never integers (0, 1, 2).
        
        Example: {"commands": [{"command": "spawn", "object_name": "sphere", "position": {"x": 0.0, "y": 0.0, "z": 0.0}, "color": {"r": 0.0, "g": 0.0, "b": 1.0}}]}"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": simple_system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        response_content = response.choices[0].message.content
        print(f"Received raw response from OpenAI: {response_content}")

        if response_content is None:
            print("Error: OpenAI returned None response")
            return None

        parsed_json = json.loads(response_content)
        command_list = parsed_json.get("commands", [])

        if not command_list:
            print("Error: No commands found in OpenAI response")
            return None

        print(f"Successfully parsed commands: {json.dumps(command_list, indent=2)}")
        return command_list

    except Exception as e:
        print(f"An error occurred with the OpenAI API call: {e}")
        return None


def send_commands_to_unity(commands):
    """
    Sends a list of commands to the Unity HTTP server.

    Args:
        commands (list): A list of command dictionaries.

    Returns:
        bool: True if the commands were sent successfully, False otherwise.
    """
    if not commands:
        return False

    try:
        # Unity expects a specific JSON format - send the array directly
        json_data = json.dumps(commands)
        print(f"Sending to Unity: {json_data}")
        
        # Use curl as a workaround for Unity HttpServer Python compatibility issue
        import subprocess
        curl_cmd = [
            'curl', '-X', 'POST', UNITY_SERVER_URL,
            '-H', 'Content-Type: application/json',
            '-d', json_data,
            '-s', '-w', '%{http_code}'
        ]
        
        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
            response_text = result.stdout
            # Extract status code (last 3 characters)
            if len(response_text) >= 3:
                status_code = int(response_text[-3:])
                response_body = response_text[:-3]
                
                # Create a fake response object for compatibility
                class FakeResponse:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = text
                
                response = FakeResponse(status_code, response_body)
            else:
                response = FakeResponse(500, "Invalid response")
        except Exception as e:
            print(f"Curl command failed: {e}")
            response = FakeResponse(500, f"Error: {e}")
        # Check for a successful response from Unity
        if response.status_code == 200:
            print(f"Successfully sent commands to Unity. Response: {response.text}")
            return True
        else:
            print(f"Error sending commands to Unity. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to Unity server at {UNITY_SERVER_URL}. Is Unity running and in Play mode?")
        print(f"Error: {e}")
        return False


# --- Flask Web Server ---

# A simple HTML front-end for user interaction.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VLM Scene Architect</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #09f;
            animation: spin 1s ease infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-900 text-white flex flex-col items-center justify-center min-h-screen p-4">

    <div class="w-full max-w-2xl bg-gray-800 rounded-2xl shadow-lg p-8">
        <h1 class="text-3xl font-bold text-center mb-2 text-cyan-400">VLM Scene Architect</h1>
        <p class="text-center text-gray-400 mb-6">Describe the 3D SceneBuilder.cs you want to create in Unity.</p>

        <form id="prompt-form" class="space-y-4">
            <textarea id="prompt-input" rows="4" class="w-full p-4 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none transition" placeholder="e.g., Create a tall blue cylinder at x -5, and a wide green plane on the floor..."></textarea>
            <button type="submit" id="submit-btn" class="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center">
                <span id="btn-text">Generate Scene</span>
                <div id="loader" class="spinner hidden ml-3"></div>
            </button>
        </form>

        <div id="status-message" class="mt-6 text-center text-gray-400 h-6"></div>

        <div class="mt-6 p-4 bg-gray-900 rounded-lg">
            <h2 class="text-lg font-semibold mb-2 text-gray-300">Log</h2>
            <pre id="log-output" class="text-sm text-gray-400 h-48 overflow-y-auto bg-gray-800 p-3 rounded-md"></pre>
        </div>
    </div>

    <script>
        const form = document.getElementById('prompt-form');
        const input = document.getElementById('prompt-input');
        const submitBtn = document.getElementById('submit-btn');
        const btnText = document.getElementById('btn-text');
        const loader = document.getElementById('loader');
        const statusMessage = document.getElementById('status-message');
        const logOutput = document.getElementById('log-output');

        function log(message) {
            const timestamp = new Date().toLocaleTimeString();
            logOutput.innerHTML += `[${timestamp}] ${message}\\n`;
            logOutput.scrollTop = logOutput.scrollHeight;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const prompt = input.value.trim();
            if (!prompt) {
                log('Please enter a prompt.');
                return;
            }

            // UI feedback
            submitBtn.disabled = true;
            btnText.textContent = 'Generating...';
            loader.classList.remove('hidden');
            statusMessage.textContent = '';
            log(`User Prompt: "${prompt}"`);

            try {
                const response = await fetch('/process_prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });

                const result = await response.json();

                if (response.ok) {
                    statusMessage.textContent = 'Scene generated successfully in Unity!';
                    statusMessage.style.color = '#22c55e'; // green-500
                    log('Successfully sent commands to Unity.');
                    log('Generated Commands: ' + JSON.stringify(result.commands, null, 2));
                } else {
                    throw new Error(result.error || 'An unknown error occurred.');
                }

            } catch (error) {
                statusMessage.textContent = `Error: ${error.message}`;
                statusMessage.style.color = '#ef4444'; // red-500
                log(`Error: ${error.message}`);
            } finally {
                // Reset UI
                submitBtn.disabled = false;
                btnText.textContent = 'Generate Scene';
                loader.classList.add('hidden');
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/process_prompt', methods=['POST'])
def process_prompt():
    """
    API endpoint that receives a prompt, generates commands,
    and sends them to Unity.
    """
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request. 'prompt' is required."}), 400

    prompt = data['prompt']

    # 1. Generate commands from the prompt using OpenAI
    commands = generate_unity_commands_from_prompt(prompt)
    if not commands:
        return jsonify({"error": "Failed to generate commands from prompt via OpenAI."}), 500

    # 2. Send the generated commands to Unity
    success = send_commands_to_unity(commands)
    if not success:
        return jsonify({
            "error": "Unity not responding! Make sure Unity is running in Play Mode with HttpServer script attached.",
            "ai_result": "AI successfully generated commands",
            "commands": commands,
            "next_steps": "1. Open Unity 2. Copy HttpServer.cs & SceneBuilder.cs to Assets/Scripts/ 3. Create GameObject with both scripts 4. Press Play"
        }), 500

    return jsonify({
        "message": "Commands sent to Unity successfully.",
        "commands": commands
    }), 200


if __name__ == '__main__':
    # Check for API key before starting
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        print("=" * 60)
        print("!!! ERROR: OPENAI_API_KEY is not set! !!!")
        print("Please edit the vlm_scene_architect_agent.py file and replace")
        print("'YOUR_OPENAI_API_KEY' with your actual OpenAI API key.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("VLM Scene Architect Agent")
        print("Flask server running at http://127.0.0.1:5001")
        print(f"Attempting to connect to Unity at {UNITY_SERVER_URL}")
        print("Make sure Unity is in Play Mode to receive commands.")
        print("=" * 60)
        app.run(host='0.0.0.0', port=5001, debug=True)

