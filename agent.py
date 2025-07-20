# agent.py
#
# Contains the AutonomousAgent class, which is the core reasoning engine.
# It uses the OpenAI API with the "tool calling" feature to decompose a
# high-level goal into a sequence of concrete actions.

import time
from tools import TOOL_DEFINITIONS, AVAILABLE_TOOLS
from config import OPENAI_API_KEY, OPENAI_MODEL

# --- Agents ---
class AutonomousAgent:
    """
    The core LLM-based agent that plans and executes Unity scene synthesis.
    """
    def __init__(self):
        from openai import OpenAI
        if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
            raise ValueError("OpenAI API key is not configured in config.py.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # Enhanced system prompt
        self.system_prompt = """
        You are an advanced Vision-Language Model (VLM) agent specializing in autonomous robotics scene synthesis in Unity.

        **Core Capabilities:**
        1. **Create:** Spawn objects, set lighting, arrange complex 3D scenes
        2. **See:** Capture and analyze scene images with computer vision
        3. **Simulate:** Run physics simulations and pathfinding
        4. **Query:** Get object positions, inventory, and scene state
        5. **Adapt:** Click Unity controls and recover from errors autonomously

        **CRITICAL OODA Loop Methodology:**
        1. **Observe:** Capture scene state with vision tools
        2. **Orient:** Analyze what you see and plan next steps  
        3. **Decide:** Choose the best tools and actions
        4. **Act:** Execute your plan and verify results

        **Core Operating Principles:**
        - **ABSOLUTE HONESTY:** Report exactly what vision analysis says, word for word. Never lie or make up results.
        - **DESCRIPTIVE VISION:** Ask detailed vision questions like "Describe all objects, their colors, positions, and shapes in detail"
        - **VERIFY EVERYTHING:** After every major action, use vision to confirm it worked
        - **STEP-BY-STEP:** Break complex tasks into small, verifiable steps
        - **NEVER GUESS:** If you are unsure about an object's position, use `get_object_position` to find out.
        - **ALWAYS VERIFY:** After creating a complex arrangement, use `capture_and_analyze_scene` to visually confirm it's correct before running a simulation.
        - **EXAMPLE 1 - Primitives:** For "blue robot, yellow target, red obstacle":
            1. spawn_object("cube", {"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": 1}, {"r": 0.0, "g": 0.0, "b": 1.0})
            2. spawn_object("sphere", {"x": 5, "y": 0, "z": 0}, {"x": 1.5, "y": 1.5, "z": 1.5}, {"r": 1.0, "g": 1.0, "b": 0.0})
            3. spawn_object("cylinder", {"x": 2.5, "y": 0, "z": 0}, {"x": 1, "y": 3, "z": 1}, {"r": 1.0, "g": 0.0, "b": 0.0})
        - **EXAMPLE 2 - GLB Models:** For "fox and tree":
            1. search_web_for_3d_model("fox") → download_and_import_model()
            2. spawn_object("low_poly_fox.glb", {"x": 0, "y": 0, "z": 0})  # MUST include .glb
            3. spawn_object("cylinder", {"x": 2, "y": 0, "z": 0}, scale={"y": 5}, color={"r": 0.6, "g": 0.3, "b": 0.1})

        **CRITICAL: Self-Evaluation and Quality Control:**
        - **MANDATORY VERIFICATION**: After creating any scene, you MUST:
          1. Use `capture_and_analyze_scene` with a detailed prompt
          2. **CRITICALLY EVALUATE** if the vision results match the user's original request
          3. If NOT, acknowledge the failure and iterate to fix it
          4. Never claim success when vision shows something different than requested
        
        - **FAILURE DETECTION**: If vision analysis shows:
          * "bird" instead of "fox" → Scene is WRONG, must fix
          * "cylindrical object" instead of "tree" → Scene is WRONG, must fix  
          * Objects described differently than requested → Scene is WRONG, must fix
        
        - **ITERATION PROTOCOL**: When vision doesn't match request:
          1. Acknowledge: "The current scene doesn't match the request"
          2. Analyze: "Vision shows X but user wanted Y"
          3. Plan: "I need to adjust Z to achieve the goal"
          4. Act: Make specific changes (positioning, scaling, different models)
          5. Verify: Capture and analyze again
          6. Repeat until vision clearly matches the original request
        
        - **SUCCESS CRITERIA**: Only declare success when vision analysis clearly describes:
          * The exact objects the user requested (fox = fox, tree = tree)
          * In the correct arrangement (next to each other, specific colors, etc.)
          * With accurate visual descriptions that match the intent

        **Extended Tool Guidelines:**
        - **`spawn_object`**: For COLORED objects, ALWAYS specify the color parameter. Examples:
          * Blue robot: spawn_object("cube", {"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": 1}, {"r": 0.0, "g": 0.0, "b": 1.0})
          * Yellow target: spawn_object("sphere", {"x": 5, "y": 0, "z": 0}, {"x": 1.5, "y": 1.5, "z": 1.5}, {"r": 1.0, "g": 1.0, "b": 0.0})
          * Red obstacle: spawn_object("cylinder", {"x": 2.5, "y": 0, "z": 0}, {"x": 1, "y": 3, "z": 1}, {"r": 1.0, "g": 0.0, "b": 0.0})
        - **CRITICAL**: For primitives, use "cube", "sphere", "cylinder" - NOT "robot", "target", "obstacle"
        - **`search_web_for_3d_model`**: Use this FIRST if the user requests a complex object that is not a basic primitive (e.g., 'a fox', 'a desk lamp').
        - **`download_and_import_model`**: Use this AFTER a successful web search to get the model into the project.
        - **CRITICAL GLB MODELS**: When spawning downloaded models, ALWAYS use the full filename with .glb extension:
          * spawn_object("low_poly_fox.glb", position) NOT spawn_object("low_poly_fox", position)
          * spawn_object("water_bottle.glb", position) NOT spawn_object("water_bottle", position)
        - **`capture_and_analyze_scene`**: Use this to visually verify scene setup and answer questions about what you see.
        - **CRITICAL VISION HONESTY**: Always report EXACTLY what the vision analysis says, word for word. Never interpret or change the vision results.
        - **DESCRIPTIVE VISION QUESTIONS**: Ask detailed questions like:
          * "Describe all objects in this scene, including their shapes, colors, and approximate positions"
          * "List every visible object and describe what it looks like in detail"
          * "What exactly do you see in this Unity scene? Be specific about models and colors"
        - **`run_simulation_and_get_results`**: Use this to execute physics simulations between objects.
        - **`get_object_position`**: Use this to get precise coordinates of any object in the scene.
        - **`list_all_objects`**: Use this to get an inventory of all objects you've created.
        - **`click_unity_play_button`**: Use this if you need to manually start Unity's play mode for advanced simulations.
        - **`write_new_unity_script`**: Use this ONLY when the user requests a novel behavior that the existing API cannot handle.
        - **`attach_script_to_object`**: Use this AFTER you have successfully written a new script to apply its behavior to an object.
        - **`set_lighting`**: Use to control the scene's ambient lighting.
        """

    def run(self, user_prompt: str):
        """
        Runs the main agent loop: prompt -> plan -> execute tools -> respond.
        
        :param user_prompt: The high-level user request for scene synthesis.
        """
        yield "Agent waking up... Analyzing user prompt."

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        while True:
            # Generate response
            yield "llm"
            try:
                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    tools=TOOL_DEFINITIONS
                )
            except Exception as e:
                yield f"Error calling OpenAI: {e}"
                return

            message = response.choices[0].message
            messages.append(message)

            # Check if the LLM wants to call tools
            if message.tool_calls:
                yield "LLM has decided to use tools. Executing..."
                yield "tool call"
                for tool_call in message.tool_calls:
                    yield f"TOOL CALL: Calling `{tool_call.function.name}` with arguments: {tool_call.function.arguments}"
                    function_name = tool_call.function.name
                    
                    # Parse arguments as JSON
                    import json
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        yield f"Error parsing tool arguments: {e}"
                        continue

                    # Call the function
                    if function_name in AVAILABLE_TOOLS:
                        function_to_call = AVAILABLE_TOOLS[function_name]
                        try:
                            function_result = function_to_call(**function_args)
                        except Exception as e:
                            function_result = {"error": str(e)}
                    else:
                        function_result = {"error": f"Function {function_name} not found"}

                    yield "tool response"
                    yield f"TOOL RESPONSE: `{function_name}` returned: {function_result}"

                    # Add the result to the conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result)
                    })

                yield "agent"
                yield "Sending tool results back to LLM for next step..."
            else:
                # No more tool calls, but FORCE self-evaluation before final response
                yield "agent"
                
                # MANDATORY: Check if this is a scene creation task
                if any(keyword in user_prompt.lower() for keyword in ["create", "scene", "fox", "tree", "robot", "target"]):
                    # FORCE a final verification step
                    yield "MANDATORY VERIFICATION: Checking if scene matches original request..."
                    
                    # Extract the original request keywords
                    import re
                    request_objects = []
                    if "fox" in user_prompt.lower():
                        request_objects.append("fox")
                    if "tree" in user_prompt.lower():
                        request_objects.append("tree")
                    if "robot" in user_prompt.lower():
                        request_objects.append("robot")
                    if "target" in user_prompt.lower():
                        request_objects.append("target")
                    
                    # Get the last vision analysis from the conversation
                    last_vision = None
                    for msg in reversed(messages):
                        # Handle both dict and object types safely
                        try:
                            # Get role - handle both dict and object
                            if hasattr(msg, 'role'):
                                msg_role = msg.role
                            elif isinstance(msg, dict):
                                msg_role = msg.get("role", "")
                            else:
                                continue
                            
                            # Get content - handle both dict and object
                            if hasattr(msg, 'content'):
                                msg_content = getattr(msg, 'content', '')
                            elif isinstance(msg, dict):
                                msg_content = msg.get("content", "")
                            else:
                                continue
                            
                            if msg_role == "tool" and "vlm_analysis" in str(msg_content):
                                import json
                                tool_result = json.loads(msg_content)
                                if "vlm_analysis" in tool_result:
                                    last_vision = tool_result["vlm_analysis"].lower()
                                    break
                        except Exception as e:
                            continue
                    
                    if last_vision and request_objects:
                        # Check if vision matches request
                        vision_matches = True
                        missing_objects = []
                        
                        for obj in request_objects:
                            if obj not in last_vision:
                                vision_matches = False
                                missing_objects.append(obj)
                        
                        # Check for wrong descriptions
                        wrong_descriptions = []
                        if "fox" in request_objects and ("bird" in last_vision or "elongated shape" in last_vision):
                            wrong_descriptions.append("Vision describes 'bird' or vague shape instead of 'fox'")
                        if "tree" in request_objects and ("horizontal" in last_vision or "cylindrical" in last_vision):
                            wrong_descriptions.append("Vision describes 'horizontal cylinder' instead of 'vertical tree'")
                        
                        if not vision_matches or wrong_descriptions:
                            yield f"❌ VERIFICATION FAILED!"
                            yield f"REQUESTED: {', '.join(request_objects)}"
                            yield f"VISION ANALYSIS: {last_vision[:200]}..."
                            if missing_objects:
                                yield f"MISSING OBJECTS: {', '.join(missing_objects)}"
                            if wrong_descriptions:
                                yield f"WRONG DESCRIPTIONS: {', '.join(wrong_descriptions)}"
                            yield "CONCLUSION: Scene does NOT match request. FORCING AGENT TO CONTINUE ITERATING..."
                            
                            # FORCE the agent to continue instead of stopping
                            messages.append({
                                "role": "user", 
                                "content": f"❌ VERIFICATION FAILED! The vision analysis shows vague descriptions instead of clearly identifying {', '.join(request_objects)}. You MUST continue working to fix this scene. Try different positioning, scaling, or add more objects to make the {', '.join(request_objects)} clearly recognizable. Do not stop until vision clearly describes '{', '.join(request_objects)}' without vague terms like 'possibly' or 'appears to'."
                            })
                            
                            # Don't break - continue the conversation loop
                            continue
                        else:
                            yield "✅ VERIFICATION PASSED: Scene matches request!"
                            final_response = message.content
                    else:
                        final_response = message.content
                else:
                    final_response = message.content
                
                yield f"AGENT: {final_response}"
                break