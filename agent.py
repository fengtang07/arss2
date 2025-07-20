# agent.py
#
# Contains the AutonomousAgent class, which is the core reasoning engine.
# It uses the OpenAI API with the "tool calling" feature to decompose a
# high-level goal into a sequence of concrete actions.

import json
from openai import OpenAI
import config
from tools import TOOL_DEFINITIONS, AVAILABLE_TOOLS

class AutonomousAgent:
    def __init__(self):
        if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
            raise ValueError("OpenAI API key is not configured in config.py.")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self):
        """Defines the agent's persona, goals, and constraints."""
        return """
        You are ARSS (Autonomous Robotics Scene Synthesizer), an expert AI agent that controls the Unity game engine.
        Your primary goal is to translate a user's high-level request into a fully realized 3D scene for robotics simulation.
        You must decompose the user's request into a logical sequence of steps and use the provided tools to execute those steps.

        **Your Workflow:**
        1.  **Decompose:** Break down the user's prompt into the smallest possible logical steps.
        2.  **Tool Selection:** For each step, decide which tool is most appropriate.
        3.  **Execution:** Call the selected tool with the correct parameters.
        4.  **Observation:** Analyze the result of the tool call. If it fails, you can try to recover or report the failure. If it succeeds, move to the next step.

        **Tool Usage Guidelines:**
        - **`spawn_object`**: Use for basic shapes ('cube', 'sphere') and for models you have already downloaded (e.g., 'classic_cola_can.glb').
        - **`search_web_for_3d_model`**: Use this FIRST if the user requests a complex object that is not a basic primitive (e.g., 'a fox', 'a desk lamp').
        - **`download_and_import_model`**: Use this AFTER a successful web search to get the model into the project.
        - **`write_new_unity_script`**: Use this ONLY when the user requests a novel behavior that the existing API cannot handle (e.g., 'make the object float', 'change color on click'). You must provide complete, valid C# code.
        - **`attach_script_to_object`**: Use this AFTER you have successfully written a new script to apply its behavior to an object.
        - **`set_lighting`**: Use to control the scene's ambient lighting.
        - **Chain of Thought**: Think step-by-step. For example, to get a custom model, you must first `search`, then `download`, then `spawn`. To create a custom behavior, you must first `write_script`, then `attach_script`.
        """

    def run(self, user_prompt: str):
        """
        Runs the main agent loop: prompt -> plan -> execute tools -> respond.
        
        :param user_prompt: The high-level goal from the user.
        :return: A generator that yields messages about the agent's progress.
        """
        yield "Agent waking up... Analyzing user prompt."
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Start the conversation with the initial user prompt
        response = self.client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        messages.append(response_message)

        # The main loop continues as long as the model wants to call tools.
        while response_message.tool_calls:
            yield "LLM has decided to use tools. Executing..."
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_TOOLS.get(function_name)
                
                if not function_to_call:
                    yield f"ERROR: LLM tried to call an unknown tool: {function_name}"
                    continue

                try:
                    function_args = json.loads(tool_call.function.arguments)
                    yield f"TOOL CALL: Calling `{function_name}` with arguments: {function_args}"
                    
                    # Call the actual tool function
                    function_response = function_to_call(**function_args)
                    
                    yield f"TOOL RESPONSE: `{function_name}` returned: {function_response}"
                    
                    # Append the tool's response to the message history
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_response),
                    })
                except Exception as e:
                    yield f"ERROR executing tool {function_name}: {e}"
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps({"success": False, "error": str(e)}),
                    })
            
            # Send the conversation history (including tool responses) back to the model
            yield "Sending tool results back to LLM for next step..."
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            messages.append(response_message)

        # If the model responds with a message instead of more tool calls, the task is complete.
        final_response = response_message.content
        yield f"AGENT: Task complete. Final response: {final_response or 'No final message from LLM.'}" 