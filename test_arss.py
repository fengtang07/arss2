#!/usr/bin/env python3
"""
Test script for ARSS (Autonomous Robotics Scene Synthesizer)
Demonstrates the complete system with OpenAI integration
"""

from agent import AutonomousAgent
import time

def test_arss_system():
    """Test the complete ARSS system with OpenAI prompts"""
    
    print("🤖 ARSS - Autonomous Robotics Scene Synthesizer")
    print("=" * 50)
    print("Testing complete system with OpenAI integration...\n")
    
    try:
        # Initialize the ARSS agent
        print("🔧 Initializing ARSS agent...")
        agent = AutonomousAgent()
        print("✅ Agent initialized successfully!\n")
        
        # Test prompt for robotics scenario
        test_prompt = """
        Create a robotics training scenario with the following elements:
        - A fox standing on a wooden log
        - Set the lighting to sunset for golden hour training
        - The scene should be suitable for a robot to practice object detection and navigation
        """
        
        print("📝 Test Prompt:")
        print(f"   {test_prompt.strip()}")
        print("\n🚀 Starting autonomous scenario generation...\n")
        
        # Run the agent and stream the results
        for message in agent.run(test_prompt):
            print(f"🔄 {message}")
            time.sleep(0.5)  # Small delay to see the progression
            
        print("\n🎉 ARSS scenario generation completed!")
        print("✨ Check Unity to see the generated robotics training scenario!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure:")
        print("   - OpenAI API key is configured in config.py")
        print("   - Unity is running with HttpServer active")
        print("   - All dependencies are installed")

if __name__ == "__main__":
    test_arss_system() 