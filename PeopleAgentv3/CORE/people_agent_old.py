import logging
import sys
import asyncio  # added import for asyncio
from langchain_openai import AzureChatOpenAI
from PeopleAgentv3.UTIL.config import load_config
from PeopleAgentv3.UTIL.logging_setup import setup_logging
from PeopleAgentv3.CORE.auth import get_access_token
from PeopleAgentv3.CORE.ms_graph_client import MSGraphClient
from PeopleAgentv3.CORE.ai_analysis import analyze_query
from PeopleAgentv3.CORE.response_generation import generate_response

logger = logging.getLogger(__name__)

class PeopleAgent:
    def __init__(self, user_identifier):
        """
        This agent uses a client credentials flow for Graph API queries.
        """
        self.logger = logger
        self.config = load_config()
        setup_logging(self.config)

        self.access_token = get_access_token(self.config)
        if not self.access_token:
            self.logger.error("Failed to acquire access token.")
            sys.exit(1)

        self.logger.info(f"Initializing PeopleAgent for user: {user_identifier}")
        self.user_identifier = user_identifier

         # Initialize conversation memory
        self.conversation_history = []
        self.memory_limit = self.config.get("CONVERSATION_MEMORY_LIMIT", 10)

        # OpenAI client
        self.openai_client = AzureChatOpenAI(
            azure_deployment=self.config.get("AOAI_DEPLOYMENT", ""),
            api_version=self.config.get("AOAI_API_VERSION", "2024-02-15-preview"),
            api_key=self.config.get("AOAI_KEY", ""),
            azure_endpoint=self.config.get("AOAI_ENDPOINT", "")
        )

        # MS Graph client
        self.graph_client = MSGraphClient(self.config, self.access_token)

    async def analyze_query(self, user_query):
        """
        Determine answer intent via Azure OpenAI.
        """
        return analyze_query(self.openai_client, user_query)

    async def get_all_users(self):
        return await self.graph_client.get_all_users()

    async def find_user_by_name(self, name):
        return await self.graph_client.find_user_by_name(name)

    async def get_user_profile(self):
        return await self.graph_client.get_user_profile(self.user_identifier)

    async def get_manager_info(self):
        return await self.graph_client.get_manager_info(self.user_identifier)

    async def get_direct_reports(self):
        return await self.graph_client.get_direct_reports(self.user_identifier)

    async def get_devices(self):
        return await self.graph_client.get_devices(self.user_identifier)

    async def get_colleagues(self):
        return await self.graph_client.get_colleagues(self.user_identifier)

    async def get_documents(self):
        return await self.graph_client.get_documents(self.user_identifier)

    def format_data(self, data_type, data):
        """
        Format different types of Graph API responses into structured content.
        """
        if isinstance(data, str):
            return data  # Likely an error message

        result = {}
        try:
            if data_type == "profile":
                result = {
                    "name": data.get("displayName"),
                    "email": data.get("mail"),
                    "title": data.get("jobTitle"),
                    "location": data.get("officeLocation", "Unknown"),
                    "timezone": data.get("mailboxSettings", {}).get("timeZone", "Unknown")
                }
            elif data_type == "manager":
                result = {
                    "name": data.get("displayName"),
                    "title": data.get("jobTitle"),
                    "email": data.get("mail"),
                    "location": data.get("officeLocation", "Unknown")
                }
            elif data_type == "devices":
                value_list = data.get("value", [])
                result = [
                    {
                        "name": device.get("displayName", "Unknown"),
                        "type": device.get("deviceType", "Unknown"),
                        "manufacturer": device.get("manufacturer", "Unknown"),
                        "model": device.get("model", "Unknown"),
                        "os": device.get("operatingSystem", "Unknown"),
                        "status": device.get("complianceState", "Unknown")
                    }
                    for device in value_list
                ]
            elif data_type == "colleagues":
                result = data.get("value", [])
            elif data_type == "documents":
                result = data.get("value", [])
            elif data_type == "reports":
                result = data.get("value", [])
            elif data_type == "all_users":
                user_list = data.get("value", [])
                all_users = []
                for user_entry in user_list:
                    all_users.append({
                        "displayName": user_entry.get("displayName"),
                        "userPrincipalName": user_entry.get("userPrincipalName"),
                        "mail": user_entry.get("mail"),
                        "jobTitle": user_entry.get("jobTitle", ""),
                    })
                result = all_users
        except Exception as e:
            return f"Error formatting {data_type} data: {str(e)}"
        return result

    def generate_response(self, query, context):
        """
        Use Azure OpenAI to generate a final natural language response.
        Includes conversation history for context awareness.
        """
        return generate_response(self.openai_client, query, context, self.conversation_history)

    async def _process_query_core(self, user_query):
        """
        Main method:
          1) Query analysis
          2) Data fetching
          3) Response generation
          4) Update conversation memory
        """

        # Add user query to conversation history
        self.conversation_history.append({"role": "user", "content": user_query})

        intents = await self.analyze_query(user_query)
        context = {}
        for intent in intents:
            intent = intent.strip()
            if intent == "profile":
                raw_data = await self.get_user_profile()
                context["profile"] = self.format_data("profile", raw_data)
            elif intent == "manager":
                raw_data = await self.get_manager_info()
                context["manager"] = self.format_data("manager", raw_data)
            elif intent == "reports":
                raw_data = await self.get_direct_reports()
                context["reports"] = self.format_data("reports", raw_data)
            elif intent == "devices":
                raw_data = await self.get_devices()
                context["devices"] = self.format_data("devices", raw_data)
            elif intent == "colleagues":
                raw_data = await self.get_colleagues()
                context["colleagues"] = self.format_data("colleagues", raw_data)
            elif intent == "documents":
                raw_data = await self.get_documents()
                context["documents"] = self.format_data("documents", raw_data)
            elif intent == "all_users":
                raw_data = await self.get_all_users()
                context["all_users"] = self.format_data("all_users", raw_data)

        response = self.generate_response(user_query, context)
        # Add agent response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})

        # Limit conversation history to prevent excessive token usage
        if len(self.conversation_history) > self.memory_limit:
            self.conversation_history = self.conversation_history[-self.memory_limit:]
        self.logger.debug(f"Conversation history length: {len(self.conversation_history)}")
        return response

    def process_query(self, query: str, stream: bool = True):
        full_response = asyncio.run(self._process_query_core(query))
        if stream:
            chunk_size = 10  # fixed chunk size for simulation of streaming
            for i in range(0, len(full_response), chunk_size):
                yield full_response[i:i+chunk_size]
        else:
            return full_response

    def clear_memory(self):
        """
        Clear conversation history when switching contexts or users.
        """
        self.conversation_history = []
        self.logger.info("Conversation memory cleared")