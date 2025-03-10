import logging
from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)

def analyze_query(openai_client, user_query):
    """
    Determine which data needs to be fetched based on the user query (Azure OpenAI).
    """
    system_prompt = """
    You are an AI assistant analyzing Microsoft 365 user queries.
    Determine which data needs to be fetched based on the query.
    Return one or more of these categories (comma-separated):
      profile, manager, reports, devices, colleagues, documents, access
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    intent = openai_client.invoke(messages).content.strip().lower()
    return intent.split(',')