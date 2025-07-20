# main.py
#
# Main entry point for the ARSS Python Agent.
# This script runs a Flask web server that provides a simple UI for interacting
# with the agent and an API endpoint to process user requests.

from flask import Flask, render_template_string, request, Response
from agent import AutonomousAgent
import config

app = Flask(__name__)

# --- HTML & CSS for the Web UI ---
# A simple, self-contained web page for interacting with the agent.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARSS Agent Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .log-entry { border-left: 3px solid; padding-left: 1rem; margin-bottom: 0.75rem; }
        .log-user { border-color: #6366f1; }
        .log-agent { border-color: #10b981; }
        .log-llm { border-color: #3b82f6; }
        .log-tool-call { border-color: #f97316; }
        .log-tool-response { border-color: #f59e0b; }
        .log-error { border-color: #ef4444; }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto p-4 max-w-4xl">
        <div class="bg-gray-800 rounded-2xl shadow-lg p-6">
            <h1 class="text-3xl font-bold text-center mb-2 text-cyan-400">Autonomous Robotics Scene Synthesizer</h1>
            <p class="text-center text-gray-400 mb-6">Give the agent a high-level goal for a Unity scene.</p>

            <form id="prompt-form" class="space-y-4">
                <textarea id="prompt-input" rows="3" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none transition" placeholder="e.g., Create a scene with a fox standing on a log. The lighting should be sunset."></textarea>
                <button type="submit" id="submit-btn" class="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center">
                    Execute Plan
                </button>
            </form>
        </div>

        <div class="mt-6 bg-gray-800 rounded-2xl shadow-lg p-6">
            <h2 class="text-xl font-semibold mb-4 text-gray-300">Agent Log</h2>
            <div id="log-output" class="text-sm text-gray-300 h-96 overflow-y-auto bg-gray-900 p-4 rounded-md font-mono">
                Waiting for user command...
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('prompt-form');
        const input = document.getElementById('prompt-input');
        const submitBtn = document.getElementById('submit-btn');
        const logOutput = document.getElementById('log-output');

        function addLogEntry(message, type) {
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            
            const title = document.createElement('strong');
            title.className = 'capitalize';
            title.textContent = type.replace('-', ' ');
            
            const content = document.createElement('div');
            content.textContent = message;
            
            entry.appendChild(title);
            entry.appendChild(content);
            
            logOutput.appendChild(entry);
            logOutput.scrollTop = logOutput.scrollHeight;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const prompt = input.value.trim();
            if (!prompt) return;

            submitBtn.disabled = true;
            submitBtn.textContent = 'Agent is thinking...';
            logOutput.innerHTML = ''; // Clear log
            addLogEntry(prompt, 'user');

            const response = await fetch('/run_agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\\n');
                
                lines.forEach(line => {
                    if (line.trim() === '') return;
                    let type = 'agent';
                    if (line.startsWith('LLM')) type = 'llm';
                    if (line.startsWith('TOOL CALL')) type = 'tool-call';
                    if (line.startsWith('TOOL RESPONSE')) type = 'tool-response';
                    if (line.startsWith('ERROR')) type = 'error';
                    addLogEntry(line, type);
                });
            }

            submitBtn.disabled = false;
            submitBtn.textContent = 'Execute Plan';
        });
    </script>
</body>
</html>
"""

# --- Flask Routes ---
@app.route('/')
def index():
    """Serves the main web UI."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/run_agent', methods=['POST'])
def run_agent_endpoint():
    """
    Receives a prompt from the UI and starts the agent's execution loop.
    Streams the agent's log back to the client as Server-Sent Events.
    """
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return Response("Error: Prompt is required.", status=400)

    agent = AutonomousAgent()
    
    def event_stream():
        # The agent's run method is a generator. We yield each message
        # from it as a separate event in the stream.
        for message in agent.run(prompt):
            yield f"{message}\n"
    
    # The Response object is configured to stream the output.
    return Response(event_stream(), mimetype='text/plain')

if __name__ == '__main__':
    # Perform a check to ensure the Unity assets path is configured.
    if "ABSOLUTE_PATH_TO_YOUR_UNITY_PROJECT" in config.UNITY_ASSETS_PATH:
        print("="*60)
        print("!!! CONFIGURATION ERROR !!!")
        print("Please open 'config.py' and set the 'UNITY_ASSETS_PATH' variable")
        print("to the correct absolute path for your Unity project's Assets folder.")
        print("="*60)
    else:
        print("="*60)
        print("ARSS Agent Server is running.")
        print("Open http://127.0.0.1:5002 in your browser.")
        print("Make sure your Unity project is open and in Play mode.")
        print("="*60)
        app.run(host='0.0.0.0', port=5002, debug=False) 