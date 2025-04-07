#Improved version of Original Code
#Parallel Calls and pass to LLM

#in-memory cache with TTL support for API calls

#Your current design caches complete responses based on an exact query and context hash, 
# so even if the underlying API data (like location) is already fetched and cached, 
# a new query that asks only for a subset (e.g. "What is my Location?") 
# won’t match the previously cached final answer.
# More improved caching mechanism to be added...



import logging
import sys
import asyncio
import re
import time
from langchain_openai import AzureChatOpenAI
from PeopleAgentv3_native_streaming.UTIL.config import load_config
from PeopleAgentv3_native_streaming.UTIL.logging_setup import setup_logging
from PeopleAgentv3_native_streaming.CORE.auth import get_access_token
from PeopleAgentv3_native_streaming.CORE.ms_graph_client import MSGraphClient
from PeopleAgentv3_native_streaming.CORE.ai_analysis import analyze_query
from PeopleAgentv3_native_streaming.CORE.response_generation import generate_response
from PeopleAgentv3_native_streaming.CORE.response_generation import generate_response, generate_response_streaming
import time
from functools import wraps
import hashlib

# Setup logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Enable debug messages

# in-memory cache with TTL support for API calls
def ttl_cache(ttl: int):
    def decorator(func):
        cache = {}
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            current_time = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    self_logger = getattr(args[0], "logger", None)
                    if self_logger:
                        self_logger.debug(f"Cache hit for {func.__name__}")
                    else:
                        print(f"Cache hit for {func.__name__}")
                    return result
            result = await func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        return wrapper
    return decorator

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

        # Begin addition for caching responses:
        self.response_cache = {}
        self.response_cache_times = {}
        self.response_cache_ttl = 60  # cache TTL in seconds

    async def analyze_query(self, user_query):
        """
        Determine answer intent via Azure OpenAI.
        """
        return analyze_query(self.openai_client, user_query)

     # API-level caching with TTL (60 seconds in this example)
    @ttl_cache(ttl=60)
    async def get_user_profile(self):
        return await self.graph_client.get_user_profile(self.user_identifier)

    @ttl_cache(ttl=60)
    async def get_manager_info(self):
        return await self.graph_client.get_manager_info(self.user_identifier)

    @ttl_cache(ttl=60)
    async def get_direct_reports(self):
        return await self.graph_client.get_direct_reports(self.user_identifier)

    @ttl_cache(ttl=60)
    async def get_devices(self):
        return await self.graph_client.get_devices(self.user_identifier)

    @ttl_cache(ttl=60)
    async def get_colleagues(self):
        return await self.graph_client.get_colleagues(self.user_identifier)

    @ttl_cache(ttl=60)
    async def get_documents(self):
        return await self.graph_client.get_documents(self.user_identifier)

    @ttl_cache(ttl=60)
    async def get_all_users(self):
        return await self.graph_client.get_all_users()

    def _build_response_key(self, query, context):
        """
        Build a unique key for final response caching based on user identifier,
        the query, and a hash of the context.
        """
        context_str = str(context)
        context_hash = hashlib.md5(context_str.encode("utf-8")).hexdigest()
        key = f"{self.user_identifier}:{query}:{context_hash}"
        return key

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
                        "jobTitle": user_entry.get("jobTitle", "")
                    })
                result = all_users
        except Exception as e:
            return f"Error formatting {data_type} data: {str(e)}"
        return result

    def extract_citations(self, response: str):
        """
        Extract citations from the response. Assumes citations are marked as [1] ..., [2] ... etc.
        """
        citations = re.findall(r"(\[\d+\]\s+.*?)(?=\n|$)", response)
        return citations

    def format_citations(self, citations):
        """
        Format the extracted citations into a references block.
        """
        return "\n".join(citations)


# ––––– Flow Changes Summary –––––
#
# In response_generation.py, the new generate_response_streaming() method builds the messages,
# invokes the Azure OpenAI client with stream=True, and yields chunks via a generator wrapped in a 
# Flask Response with appropriate SSE formatting.
#
# In people_agent.py, the generate_response method now accepts a stream flag. When stream=True, it
# delegates to generate_response_streaming so that native streaming is used. Otherwise, it falls back 
# to the full response version.
#
# Ensure your OpenAI client library supports streaming with stream=True and that the chunk structure 
# (e.g. chunk.text) is correct.

   
    def generate_response(self, query, context, stream=False):
        """
        Generate a full response from Azure OpenAI.
        If stream is True, delegate to generate_response_streaming (returning a generator for Gradio).
        Otherwise, get a complete response.
        """
        if stream:
            # Return a streaming generator (for Gradio) by not wrapping in a Flask Response.
            return generate_response_streaming(self.openai_client, query, context, self.conversation_history, flask_response=False)
        else:
            raw_response = generate_response(self.openai_client, query, context, self.conversation_history)
            citations = self.extract_citations(raw_response)
            if citations:
                citation_block = self.format_citations(citations)
                final_response = f"{raw_response}\n\nReferences:\n{citation_block}"
            else:
                final_response = raw_response
            return final_response
        

        
    def process_query(self, query: str, stream: bool = True):
        full_response = asyncio.run(self._process_query_core(query))
        if stream:
            chunk_size = 10  # fixed chunk size for simulation of streaming
            for i in range(0, len(full_response), chunk_size):
                yield full_response[i:i+chunk_size]
        else:
            return full_response    

            
    def generate_response_old(self, query, context):
        """
        Use Azure OpenAI to generate a final natural language response.
        Includes conversation history for context awareness.
        Post-process the response to append a References section if citations are present.
        """
        raw_response = generate_response(self.openai_client, query, context, self.conversation_history)
        citations = self.extract_citations(raw_response)
        if citations:
            citation_block = self.format_citations(citations)
            final_response = f"{raw_response}\n\nReferences:\n{citation_block}"
        else:
            final_response = raw_response
        return final_response
    

    async def _process_query_core(self, user_query):
            """
            Main method:
            1) Fetch data in parallel from all sources (API-level caching applied)
            2) Check final response cache; if a fresh answer exists, return it
            3) Otherwise, generate a new answer using the LLM and cache it
            4) Update conversation history and return the response
            """
            self.conversation_history.append({"role": "user", "content": user_query})
            
            # Create asynchronous tasks for parallel API calls
            tasks = {
                "profile": asyncio.create_task(self.get_user_profile()),
                "manager": asyncio.create_task(self.get_manager_info()),
                "reports": asyncio.create_task(self.get_direct_reports()),
                "devices": asyncio.create_task(self.get_devices()),
                "colleagues": asyncio.create_task(self.get_colleagues()),
                "documents": asyncio.create_task(self.get_documents()),
                "all_users": asyncio.create_task(self.get_all_users())
            }

            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            data_sources = dict(zip(tasks.keys(), results))

            # Build a combined context from API results
            context = {}
            for key, data in data_sources.items():
                if isinstance(data, Exception):
                    self.logger.error(f"Error fetching {key}: {data}")
                    context[key] = f"Error getting {key}: {str(data)}"
                else:
                    context[key] = self.format_data(key, data)

            # Build a unique cache key based on the query and context
            final_key = self._build_response_key(user_query, context)
            now = time.time()
            if final_key in self.response_cache and (now - self.response_cache_times.get(final_key, 0)) < self.response_cache_ttl:
                self.logger.debug(f"Final response cache hit for key: {final_key}")
                return self.response_cache[final_key]

            self.logger.info(f"Parallel API calls completed. Context: {context}")
            response = self.generate_response(user_query, context)
            self.conversation_history.append({"role": "assistant", "content": response})

            # Cache the generated response and record its timestamp
            self.response_cache[final_key] = response
            self.response_cache_times[final_key] = now

            if len(self.conversation_history) > self.memory_limit:
                self.conversation_history = self.conversation_history[-self.memory_limit:]
            self.logger.debug(f"Conversation history length: {len(self.conversation_history)}")
            return response


       
        
    def process_query_old(self, query: str, stream: bool = True):
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