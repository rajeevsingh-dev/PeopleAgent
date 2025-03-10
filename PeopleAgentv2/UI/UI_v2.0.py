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
    with gr.Blocks(css=".container { max-width: 800px; margin: auto; }") as demo:
        gr.Markdown("# Microsoft 365 People Agent")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### User Information")
                user_identifier = gr.Textbox(label="User Identifier", 
                                           lines=1, 
                                           value="",
                                           placeholder="Enter email or username")

            with gr.Column(scale=1):
                gr.Markdown("### Question")
                user_query = gr.Textbox(label="Your Question", 
                                       lines=2, 
                                       placeholder="Ask about a manager, devices, etc.")
        
        with gr.Row():
            gr.Markdown("### Suggested Questions")
            
        with gr.Row():
            # Create buttons for sample prompts
            profile_btn = gr.Button("👤 Profile", elem_id="prompt-btn")
            manager_btn = gr.Button("👨‍💼 Manager", elem_id="prompt-btn") 
            reports_btn = gr.Button("👥 Direct Reports", elem_id="prompt-btn")
            devices_btn = gr.Button("💻 Devices", elem_id="prompt-btn")
            colleagues_btn = gr.Button("👪 Colleagues", elem_id="prompt-btn")
        
        with gr.Row():
            with gr.Column(scale=3):
                submit_btn = gr.Button("Submit", variant="primary", size="lg")
                
        with gr.Row():
            response_box = gr.Textbox(label="Response", lines=10)

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
        profile_btn.click(lambda: set_prompt("profile"), inputs=None, outputs=user_query)
        manager_btn.click(lambda: set_prompt("manager"), inputs=None, outputs=user_query)
        reports_btn.click(lambda: set_prompt("reports"), inputs=None, outputs=user_query)
        devices_btn.click(lambda: set_prompt("devices"), inputs=None, outputs=user_query)
        colleagues_btn.click(lambda: set_prompt("colleagues"), inputs=None, outputs=user_query)

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
    ui.launch(server_name="127.0.0.1", server_port=7860, share=False)