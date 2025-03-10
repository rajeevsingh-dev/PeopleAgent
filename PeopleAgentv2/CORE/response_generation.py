import logging

logger = logging.getLogger(__name__)

def generate_response(openai_client, query, context):
    """
    Generate a natural language response from structured data using Azure OpenAI.
    """
    system_prompt = """
    You are an AI assistant specializing in Microsoft 365 user information.
    Provide natural, professional responses based on the available data.
    If information is missing, acknowledge it clearly.
    Format complex data in an easily readable way.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}\nAvailable Data: {context}"}
    ]
    return openai_client.invoke(messages).content