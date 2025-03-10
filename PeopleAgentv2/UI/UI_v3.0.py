import gradio as gr
import asyncio
import logging
import re
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PeopleAgentv2.UTIL.config import load_config
from PeopleAgentv2.UTIL.logging_setup import setup_logging
from PeopleAgentv2.CORE.people_agent import PeopleAgent

logger = logging.getLogger(__name__)
# Load config & setup logging once
config = load_config()
setup_logging(config)

# Maintain state of currently selected user
current_user = {"identifier": None, "profile_displayed": False}

async def get_user_profile(user_identifier):
    """Get basic profile information for a user"""
    agent = PeopleAgent(user_identifier)
    return await agent.process_query("What is the profile information, timezone, and location for this user?")

async def get_response(user_query, user_identifier):
    agent = PeopleAgent(user_identifier)
    return await agent.process_query(user_query)

def format_profile_response(profile_text):
    """Format the profile response in a structured way"""
    # Apply formatting to highlight key information
    formatted_text = "Based on the available data, here is the information about the person:\n\n"
    
    # Try to extract information using regex patterns
    name_match = re.search(r"(?:Name|named):\s*([^,\n]+)", profile_text, re.IGNORECASE)
    email_match = re.search(r"Email:\s*([^,\n]+)", profile_text, re.IGNORECASE)
    title_match = re.search(r"(?:Title|Role|Position):\s*([^,\n]+)", profile_text, re.IGNORECASE)
    location_match = re.search(r"(?:Location|based in):\s*([^,\n]+)", profile_text, re.IGNORECASE)
    timezone_match = re.search(r"(?:Time ?[Zz]one):\s*([^,\n]+)", profile_text, re.IGNORECASE)
    
    # Build formatted response with bold markup
    if name_match:
        formatted_text += f"- **Name**: {name_match.group(1).strip()}\n"
    if email_match:
        formatted_text += f"- **Email**: {email_match.group(1).strip()}\n"
    if title_match:
        formatted_text += f"- **Title**: {title_match.group(1).strip()}\n"
    if location_match:
        formatted_text += f"- **Location**: {location_match.group(1).strip()}\n"
    if timezone_match:
        formatted_text += f"- **Time Zone**: {timezone_match.group(1).strip()}\n"
    
    # If we couldn't extract structured information, return the original text
    if not (name_match or email_match or title_match or location_match or timezone_match):
        return profile_text
        
    formatted_text += "\nIf you need further details about their team, reporting structure, or other specifics, please provide additional context or data."
    
    return formatted_text

def format_response(response_text, is_profile=False):
    """Format the response for better readability"""
    if is_profile:
        return format_profile_response(response_text)
    
    # For regular responses, add some simple formatting
    return response_text

def sync_handle(input_text, history):
    """Sync wrapper for async PeopleAgent logic with conversational context"""
    try:
        # Check if input is an email or user identifier (simplified check)
        is_email = re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", input_text.strip())
        is_exit = input_text.strip().lower() == "exit"
        
        if is_exit:
            current_user["identifier"] = None
            current_user["profile_displayed"] = False
            return "Session ended. Enter a user identifier to start a new session."
        
        # If input looks like an email or if no current user, treat as new user identifier
        if is_email or (not current_user["identifier"]):
            user_id = input_text.strip()
            current_user["identifier"] = user_id
            current_user["profile_displayed"] = True
            
            # Get profile information as first response
            profile = asyncio.run(get_user_profile(user_id))
            
            # Format response with better styling
            formatted_profile = format_response(profile, is_profile=True)
            
            # Format response to include instructions
            response = f"{formatted_profile}\n\nAsk a question about this user, enter another user's email/ID/name to switch, or type 'exit' to quit:"
            return response
        else:
            # Process as a question about the current user
            response = asyncio.run(get_response(input_text, current_user["identifier"]))
            formatted_response = format_response(response)
            return f"{formatted_response}\n\nAsk a question about this user, enter another user's email/ID/name to switch, or type 'exit' to quit:"
            
    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        return f"Error processing your request: {str(e)}\n\nPlease try again with a valid user identifier or question."

def build_ui():
    with gr.Blocks(css="""
        .container { max-width: 800px; margin: auto; }
        .heading { margin-bottom: 20px; text-align: center; }
        .chatbox { min-height: 400px; }
        .prompt-buttons { margin-top: 10px; }
        #prompt-btn { margin: 0 5px; }
    """) as demo:
        gr.Markdown("# Microsoft 365 People Agent", elem_classes="heading")
        
        # Conversation history
        chatbot = gr.Chatbot(
            label="Conversation",
            height=500,
            show_label=False,
            elem_classes="chatbox"
        )
        
        # Single input field for both user ID and questions
        with gr.Row():
            input_text = gr.Textbox(
                label="Enter user identifier or question",
                placeholder="Start by entering a user's email, ID, or name...",
                lines=2
            )
        
        with gr.Row():
            gr.Markdown("### Suggested Questions", elem_classes="prompt-heading")
            
        with gr.Row(elem_classes="prompt-buttons"):
            # Create buttons for sample prompts
            profile_btn = gr.Button("👤 Profile", elem_id="prompt-btn")
            manager_btn = gr.Button("👨‍💼 Manager", elem_id="prompt-btn") 
            reports_btn = gr.Button("👥 Direct Reports", elem_id="prompt-btn")
            devices_btn = gr.Button("💻 Devices", elem_id="prompt-btn")
            colleagues_btn = gr.Button("👪 Colleagues", elem_id="prompt-btn")
            
        with gr.Row():
            submit_btn = gr.Button("Submit", variant="primary", size="lg")
            clear_btn = gr.Button("New Session", size="lg")

        # Helper function to set prompt text
        def set_prompt(prompt_type):
            prompts = {
                "profile": "What is the profile information, timezone, and location for this user?",
                "manager": "Who is this person's manager and where are they located?",
                "reports": "Who are this person's direct reports?",
                "devices": "What devices does this user have?",
                "colleagues": "Who are this person's team members and frequent collaborators?"
            }
            return prompts.get(prompt_type, "")

        # Connect buttons to set the prompt text
        profile_btn.click(lambda: set_prompt("profile"), inputs=None, outputs=input_text)
        manager_btn.click(lambda: set_prompt("manager"), inputs=None, outputs=input_text)
        reports_btn.click(lambda: set_prompt("reports"), inputs=None, outputs=input_text)
        devices_btn.click(lambda: set_prompt("devices"), inputs=None, outputs=input_text)
        colleagues_btn.click(lambda: set_prompt("colleagues"), inputs=None, outputs=input_text)

        def user_input(text, history):
            # Add user message to history
            history = history + [(text, None)]
            return "", history

        def bot_response(history):
            # Get last user message
            user_message = history[-1][0]
            
            # Generate response
            bot_message = sync_handle(user_message, history[:-1])
            
            # Update last history item with the response
            history[-1][1] = bot_message
            
            return history
        
        def clear_conversation():
            # Reset the current user state
            current_user["identifier"] = None
            current_user["profile_displayed"] = False
            return None

        # Set up the chat flow
        submit_btn.click(
            user_input, 
            inputs=[input_text, chatbot], 
            outputs=[input_text, chatbot],
            queue=False
        ).then(
            bot_response,
            inputs=chatbot,
            outputs=chatbot
        )
        
        # Alternative submission via Enter key
        input_text.submit(
            user_input, 
            inputs=[input_text, chatbot], 
            outputs=[input_text, chatbot],
            queue=False
        ).then(
            bot_response,
            inputs=chatbot,
            outputs=chatbot
        )
        
        # Clear button to reset conversation
        clear_btn.click(
            clear_conversation,
            inputs=None,
            outputs=chatbot
        )

        # Initial instructions
        gr.Markdown("""
        ### How to use:
        1. Enter a user identifier (email, ID, or name) to start
        2. The system will show basic profile information
        3. Ask questions about the user
        4. Enter a different user identifier at any time to switch users
        5. Type 'exit' to end the current session
        """)

    return demo

if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="127.0.0.1", server_port=7860, share=False)