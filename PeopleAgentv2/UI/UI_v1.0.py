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

async def get_response(user_query, user_identifier):
    agent = PeopleAgent(user_identifier)
    return await agent.process_query(user_query)

def sync_handle(user_query, user_identifier):
    """Sync wrapper for async PeopleAgent logic."""
    try:
        if not user_query or not user_identifier:
            return "Please provide both a user identifier and a question."
        return asyncio.run(get_response(user_query, user_identifier))
    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        return f"Error processing your request: {str(e)}"

def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## Microsoft 365 People Agent")

        user_identifier = gr.Textbox(label="User Identifier", lines=1, value="")
        user_query = gr.Textbox(label="Question", lines=1, placeholder="Ask about a manager, devices, etc.")

        submit_btn = gr.Button("Submit")
        response_box = gr.Textbox(label="Response", lines=5)

        def on_submit(identifier, query):
            try:
                if not identifier or not query:
                    return "Please provide both a user identifier and a question."
                return sync_handle(query.strip(), identifier.strip())
            except Exception as e:
                logger.exception(f"UI Error: {str(e)}")
                return f"UI Error: {str(e)}"

        submit_btn.click(
            on_submit, 
            inputs=[user_identifier, user_query], 
            outputs=response_box
        )
    return demo

if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="127.0.0.1", server_port=7860)