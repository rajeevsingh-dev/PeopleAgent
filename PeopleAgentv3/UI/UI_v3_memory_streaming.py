import gradio as gr
import asyncio
import logging
import re
import sys
import os
import uvicorn
from fastapi import FastAPI
import time

# Add the project root to the Python path so that modules can be imported correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load config and logging setup from UTIL folder.
from PeopleAgentv3.UTIL.config import load_config
from PeopleAgentv3.UTIL.logging_setup import setup_logging
from PeopleAgentv3.CORE.people_agent import PeopleAgent  # Import PeopleAgent class


# Initialize FastAPI application.
app = FastAPI()



# Setup logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Enable debug messages

# Load configuration and set up logging.
config = load_config()
setup_logging(config)

# Global dictionary to store agent instances by user identifier
# This provides agent persistence for memory management.
user_agents = {}

# Global state for the currently selected user.
current_user = {"identifier": None, "profile_displayed": False}

# Async function to retrieve or create a PeopleAgent instance per user.
async def get_or_create_agent(user_identifier):
    """Retrieve an existing agent or create a new one to maintain conversation memory."""
    if user_identifier not in user_agents:
        logger.info(f"Creating new agent instance for user: {user_identifier}")
        user_agents[user_identifier] = PeopleAgent(user_identifier)
    return user_agents[user_identifier]

# Async function to process a query using the persistent agent.
async def get_response(user_query, user_identifier):
    """Process a query using a persistent PeopleAgent instance to maintain context."""
    agent = await get_or_create_agent(user_identifier)
    # Process query using the agent's process_query method.
    return await agent.process_query(user_query)

def format_response(response_text, is_profile=False):
    """Format the response text for better readability in the UI.
    
    You can add additional formatting logic as needed.
    """
    return response_text

def sync_handle(input_text, history):
    """Synchronous handler that wraps asynchronous PeopleAgent logic while managing context."""
    try:
        # Check if input is an email or user identifier (simple regex check).
        is_email = re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", input_text.strip())
        # Check if the user wants to exit the session.
        is_exit = input_text.strip().lower() == "exit"
        
        if is_exit:
            # If the session ends, clear the agent memory and update current_user state.
            if current_user["identifier"] and current_user["identifier"] in user_agents:
                logger.info(f"Clearing memory for user: {current_user['identifier']}")
                user_agents[current_user["identifier"]].clear_memory()
                del user_agents[current_user["identifier"]]
            current_user["identifier"] = None
            current_user["profile_displayed"] = False
            return "Session ended."
        
        # If input appears to be an email or no user is set, treat it as a new user session.
        if is_email or (not current_user["identifier"]):
            user_id = input_text.strip()
            
            # If switching users, clear previous user's agent memory.
            if current_user["identifier"] and current_user["identifier"] != user_id:
                if current_user["identifier"] in user_agents:
                    logger.info(f"Switching users, clearing memory for: {current_user['identifier']}")
                    user_agents[current_user["identifier"]].clear_memory()
                    del user_agents[current_user["identifier"]]
            
            # Set new user details.
            current_user["identifier"] = user_id
            current_user["profile_displayed"] = True
            
            # Return session initialization information.
            return f"User {user_id} session started."
        else:
            # Otherwise, process input as a query related to the current user.
            response = asyncio.run(get_response(input_text, current_user["identifier"]))
            
            # Log the conversation history length for debugging.
            if current_user["identifier"] in user_agents:
                history_len = len(user_agents[current_user["identifier"]].conversation_history)
                logger.debug(f"User {current_user['identifier']} conversation history length: {history_len}")
            
            formatted_response = format_response(response)
            return formatted_response
            
    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        return f"Error processing your request: {str(e)}"

def clear_conversation():
    """Clear conversation memory when starting a new session."""
    if current_user["identifier"] and current_user["identifier"] in user_agents:
        logger.info(f"Clearing memory for user: {current_user['identifier']}")
        user_agents[current_user["identifier"]].clear_memory()
        del user_agents[current_user["identifier"]]
    
    # Reset current user state.
    current_user["identifier"] = None
    current_user["profile_displayed"] = False
    return None

def bot(message: str, history: list):
    """Stream responses from PeopleAgent using its generate functionality."""
    # If the input is an email or no current user, handle it synchronously via sync_handle.
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", message.strip()) or not current_user["identifier"]:
        response = sync_handle(message, history)
        yield response
        return

    # Otherwise, get the persistent agent to stream the response.
    agent = asyncio.run(get_or_create_agent(current_user["identifier"]))
    # Call process_query with streaming enabled.
    response_generator = agent.process_query(message, stream=True)
    answer = ""

    # Iterate over each response chunk.
    for chunk in response_generator:
        # Log each received chunk with a timestamp.
        #logger.debug(f"Received chunk: {chunk}")
        #logger.debug(f"Chunk received at {time.strftime('%H:%M:%S')}: {chunk[:50]}... (length: {len(chunk)})")
        answer += chunk
        yield answer

def build_ui():
    """Build the Gradio user interface for the People Agent."""
    with gr.Blocks(css=""" 
        /* Custom styling for the chatbot */
        :root {
            --primary-color: #0078d4;
            --secondary-color: #f5f5f5;
            --text-color: #323130;
        }
        body {
            font-family: "Segoe UI", sans-serif;
            background-color: white;
            color: var(--text-color);
        }
        .header-container {
            display: flex;
            align-items: center;
            padding: 8px 16px;
            background: var(--secondary-color);
            border-bottom: 1px solid #e1dfdd;
        }
        .header-container h1 {
            font-size: 20px;
            margin: 0;
            color: var(--primary-color);
        }
        .header-container p {
            font-size: 14px;
            margin: 0;
            color: var(--text-color);
        }
        .login-container {
            margin-top: 16px;
            display: flex;
            align-items: center;
            padding-left: 16px;
        }
        .login-input input {
            border: 1px solid #e1dfdd;
            border-radius: 4px;
            padding: 8px 10px;
            font-size: 14px;
            width: 15px; /* reduced width for text box */
        }
        .gr-button {
            width: 130px; 
            margin-left: 8px;            
            color: black;
            border: none;           
        }
    """, title="Understand Your People Agent") as demo:
        
        # --- Header Section ---
        logo_path = os.path.join(os.path.dirname(__file__), "../icons/Orglogo.png")
        if not os.path.exists(logo_path):
            logger.warning("Logo file not found at: %s", logo_path)
            print(f"Logo file not found at: {logo_path}")
            logo_src = ""
        else:
            import base64
            with open(logo_path, "rb") as img_file:
                logo_data = base64.b64encode(img_file.read()).decode("utf-8")
            logo_src = f"data:image/png;base64,{logo_data}"
            
        with gr.Row(elem_classes="header-container"):
            with gr.Column(scale=1, min_width=60, elem_classes="logo-container"):
                gr.HTML(f"<img src='{logo_src}' width='40' height='20' alt='Logo' style='pointer-events: none; user-select: none;'/>")
            with gr.Column(scale=4, elem_classes="title-container"):
                gr.HTML("<h1 class='heading'>Understand Your People Agent</h1>")
                gr.HTML("<p class='subheading'>AI-powered insights from Graph API, HR, Skills, Time Tracking, PSA, and GitHub data</p>")
        
        # --- Chat Interface Section ---
        gr.ChatInterface(
            fn=bot,  # Use the bot function for processing agent messages
            type="messages"
        )
        
        # --- Instructions Section ---
        gr.Markdown("""
        ### How to use:
        1. Enter a user identifier or question.
        2. Type 'exit' to end the session.
        """)
    
    return demo

# Build the UI using Gradio.
ui = build_ui()

# Mount the Gradio app on FastAPI at the root path.
app = gr.mount_gradio_app(app, ui, path="/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # Launch the UI locally with specified server details.
    ui.launch(server_name="127.0.0.1", server_port=port, share=False)