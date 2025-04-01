import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

#generate_response_newResponse + Chat History
def generate_response(openai_client, query, context, conversation_history=None):
    """
    Generate a natural language response from structured data using Azure OpenAI.
    """
    current_gmt_time = datetime.now(timezone.utc).strftime("%H:%M")
    print("Current GMT time:", current_gmt_time)

    #New Improved Prompt:
    system_prompt = f"""
            AI Generated Answer
            1. Start any reply with a clear, concise summary (max 150 words) of key information.
            2. Format with bullet points, brief sentences, and clear headings.
            3. Only include details if explicitly requested.
            4. Display the calculated local time based on location when available (current UTC: {current_gmt_time}).
            5. For missing information, briefly note it without suggestions.
            
            Data Sources to acknowledge: Profile (Graph API), Manager (Workday), Skills (Workday),
            Time Tracking (Replicon), Project data (PSA), and GitHub data when relevant.
            
            Error responses:
            • No Results: "I couldn't find any work items matching your query. Please check the user identity and try again."
            • Invalid Input: "The provided user is invalid. Please verify and try again."
            • Permission Issues: "You don't have permission to view these data. Please check your access rights."
    """
    messages = [
        {"role": "system", "content": system_prompt}       
    ]
    
    # Add conversation history if available to provide context
    if conversation_history and len(conversation_history) > 0:
        # Add up to the last 6 messages from history for context
        # Skip adding system messages from history
        history_to_add = [msg for msg in conversation_history[-6:] 
                         if msg["role"] != "system"]
        messages.extend(history_to_add)

     # Always add the current query and context as the latest message
    messages.append({"role": "user", "content": f"Query: {query}\nAvailable Data: {context}"})
    
    #return openai_client.invoke(messages).content
    # Slightly increased max_tokens for better completion
    return openai_client.invoke(messages, max_tokens=225, temperature=0.3).content



def generate_response_v1(openai_client, query, context):
    """
    Generate a natural language response from structured data using Azure OpenAI.
    """
    current_gmt_time = datetime.now(timezone.utc).strftime("%H:%M")
    print("Current GMT time:", current_gmt_time)

    #Improved Prompt:
    system_prompt = f"""
            AI Generated Answer
            1.	Start any reply with a section named 'AI Generated Answer', which is a summarized analysis of the data, highlighting key points and trends.
            2.	Focus the first section on analysis and insights.
            3.	If detail is not requested limit the reply to a summary 150 words
            4.  if details is requested, provide a full analysis
            Data Sources and Quality
            1.	Name the sources used in the analysis and indicate the quality of the data.
            2.	Only present detailed information if explicitly requested.
            3.	Present the data in a clear and concise format.
            4.	Acknowledge missing information clearly and indicate a potential source for the data.
            5.	Format complex data in an easily readable way, using headings, bullet points, and other formatting tools as necessary.
            6.	Display the calculated local time for the user without explaining how it was done. Current UTC time is {current_gmt_time}.
            Special Handling
            1.	Job Title can only be retrieved if HR data are present, and refer to it as job_title.
            2.	Job Level can only be retrieved if HR data are present.
            3. Job levels are ranked in descending order, with level 1 being the highest and level 15 being the lowest.
            4.	Contractor Data: Acknowledge that contractors will have less data, such as no skill or partial location data.
            5. if the person is a manager, time tracking, skills are provided for his complete organization.
            Error Handling
            •	No Results: "I couldn't find any work items matching your query. Please check the user identity and try again."
            •	Invalid Input: "The provided user is invalid. Please verify and try again."
            •	Permission Issues: "You don't have permission to view these data. Please check your access rights."
            •	General Errors: "An error occurred while processing your request. Please try again later."
            Data Sources and Mapping
            •	Profile: Graph API, Quality High
            •	Manager: Workday, Quality High
            •	Reports: Workday, Quality High
            •	Devices: Graph API, Quality High
            •	Colleagues: Graph API, Quality High
            •	Documents: Graph API, Quality High
            •	HR Data: Workday, Quality High
            •	Time Tracking: Replicon, Quality Low
            •	Skills: Workday, Quality High
            •	Project Assignment: PSA, Quality High
            •	Project Demands: PSA, Quality High
            •	GitHub: DXC Enterprise GitHub Extract, Quality Medium
            •	All Users: Graph API, Quality High
            Maintain Professionalism
            •	Respond promptly and accurately to all queries.
            •	Ensure the responses are natural, concise, polite, and professional.
            •	Use clear, concise language.
            •	Ensure data privacy and security by only accessing and sharing information the user is authorized to see.
            •	Support multiple queries simultaneously if needed.

    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}\nAvailable Data: {context}"}
    ]
    
    # Slightly increased max_tokens for better completion
    #return openai_client.invoke(messages, max_tokens=225, temperature=0.3).content
    return openai_client.invoke(messages).content

#Basic Prompt
def generate_response_old(openai_client, query, context):
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
