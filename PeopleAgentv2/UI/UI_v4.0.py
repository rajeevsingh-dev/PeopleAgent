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
        .chatbox { min-height: 500px; width: 100%; }
        .input-area { width: 100%; padding: 10px 0; }
        .input-row { display: flex; align-items: center; gap: 8px; width: 100%; }
        .input-text { flex-grow: 1; }
        .btn-small { padding: 5px 10px !important; height: auto !important; }
    """) as demo:
        gr.Markdown("# Microsoft 365 People Agent", elem_classes="heading")
        
        # Create a column to ensure consistent width
        with gr.Column(scale=1, min_width=700):
            # State to store the current conversation
            state = gr.State([])
            
            # Conversation history display
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_label=False,
                elem_classes="chatbox",
                container=True,
                scale=1,
                visible=True,
            )
            
            # Use a container div for the input area
            with gr.Group(elem_classes="input-area"):
                # User input and buttons in one row 
                with gr.Row(elem_classes="input-row"):
                    input_text = gr.Textbox(
                        label="",
                        placeholder="Start by entering a user's email, ID, or name...",
                        lines=2,
                        max_lines=5,
                        elem_classes="input-text",
                        container=True,
                        scale=5
                    )
                    
                    submit_btn = gr.Button("Submit", variant="primary", elem_classes="btn-small", scale=1)
                    clear_btn = gr.Button("New Session", elem_classes="btn-small", scale=1)

        # Process user input and generate bot response in a single function
        def process_message(message, chat_history):
            if not message.strip():
                return "", chat_history  # Return unchanged if empty message
            
            try:
                # Add user message to conversation
                chat_history.append((message, None))
                
                # Process the message and get response
                response = sync_handle(message, [(q, a) for q, a in chat_history[:-1]])
                
                # Update the last message with the response
                chat_history[-1] = (message, response)
                
                return "", chat_history
                
            except Exception as e:
                logger.exception(f"Error processing message: {str(e)}")
                
                # Add error message to conversation
                if len(chat_history) > 0 and chat_history[-1][1] is None:
                    chat_history[-1] = (message, f"Error: {str(e)}")
                else:
                    chat_history.append((message, f"Error: {str(e)}"))
                    
                return "", chat_history
        
        def clear_conversation():
            # Reset the current user state
            current_user["identifier"] = None
            current_user["profile_displayed"] = False
            return []

        # Connect the submit button
        submit_btn.click(
            process_message,
            inputs=[input_text, chatbot],
            outputs=[input_text, chatbot],
        )
        
        # Connect the Enter key for submission
        input_text.submit(
            process_message,
            inputs=[input_text, chatbot],
            outputs=[input_text, chatbot],
        )
        
        # Connect the clear button
        clear_btn.click(
            clear_conversation,
            inputs=[],
            outputs=[chatbot],
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