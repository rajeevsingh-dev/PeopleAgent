import logging
from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)


#analyze_query_modified
def analyze_query(openai_client, user_query):
    """
    Determine which data needs to be fetched based on the user query (Azure OpenAI).
    """
    system_prompt = """
    You are an AI assistant responsible for selecting the correct data source (intent) based on the user's question.
    The available intents are:
      profile, manager, reports, devices, colleagues, documents, access, github, skills, hr data, time_tracking, powerbi, project_assignment, project_demands.
    
    When the query mentions 'profile', 'manager', 'reports', or 'colleagues', also consider including 'hr data', 'skills', 'project_assignment', and add 'time' when appropriate.
    If the query refers to skills, competency, or language, include 'hr data'.
    When unsure, return all intents to cover every possibility.

    
    Example Intent Generation:
      For a question like "What is this person working on?" or "what is this person doing?" or any variation, include 'profile','manager', 'reports', 'colleagues','hr data', 'skills', 'project_assignment', 'github', and 'time_tracking'.
      For a question like "What are this person's skills?", the answer should be 'hr data, skills'.
      For a question like "What is this person's location?", the answer should be 'hr data'.
      For a question like "What is this can work on?", the answer should be 'hr data', 'skills', 'project_demands',   'project_assignment', 'github', and 'time_tracking'.
      For a question contains the word position add  'project_demands' and 'skills' 
      for unknown purposes, return all intents to cover every possibility.

    Response Guidelines:
      - Output one or more of the available intents as a comma-separated list.
      - Use only lowercase letters.
      - Do not include any extra text or explanation.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    print("user_query:", user_query)
    intent = openai_client.invoke(messages).content.strip().lower()
    print("Generated intent:", intent)
    return intent.split(',')


def analyze_query_old2(openai_client, user_query):
    """
    Determine which data needs to be fetched based on the user query (Azure OpenAI).
    """
    system_prompt = """
    You are an AI assistant responsible for selecting the correct data source (intent) based on the user's question.
    The available intents are:
      profile, manager, reports, devices, colleagues, documents, access, github, skills, hr data, time_tracking, powerbi, project_assignment, project_demands.
    
    When the query mentions 'profile', 'manager', 'reports', or 'colleagues', also consider including 'hr data', 'skills', 'project_assignment', and add 'time' when appropriate.
    If the query refers to skills, competency, or language, include 'hr data'.
    When unsure, return all intents to cover every possibility.

    
    Example Intent Generation:
      For a question like "What is this person working on?" or "what is this person doing?" or any variation, include 'profile','manager', 'reports', 'colleagues','hr data', 'skills', 'project_assignment', 'github', and 'time_tracking'.
      For a question like "What are this person's skills?", the answer should be 'hr data, skills'.
      For a question like "What is this person's location?", the answer should be 'hr data'.
      For a question like "What is this can work on?", the answer should be 'hr data', 'skills', 'project_demands',   'project_assignment', 'github', and 'time_tracking'.
      For a question contains the word position add  'project_demands' and 'skills' 
      for unknown purposes, return all intents to cover every possibility.

    Response Guidelines:
      - Output one or more of the available intents as a comma-separated list.
      - Use only lowercase letters.
      - Do not include any extra text or explanation.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    print("user_query:", user_query)
    intent = openai_client.invoke(messages).content.strip().lower()
    print("Generated intent:", intent)
    return intent.split(',')

def analyze_query_old(openai_client, user_query):
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