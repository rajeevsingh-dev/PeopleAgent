# PeopleAgent_v3

Summary of code changes

#### Memory Management:
• people_agent.py now maintains a conversation history and offers a clear_memory() method.
• response_generation.py appends both the user query and agent response to history.
• UI_v1_1_memory_streaming.py caches PeopleAgent instances per user and clears memory when sessions end or users switch.

#### Streaming:
• people_agent.py now supports streaming responses via process_query, yielding response chunks.
• response_generation.py includes a generator function to yield updated responses.
• UI_v1_1_memory_streaming.py iterates over the streaming generator, logs each chunk with timing details, and updates the UI in real time.

## Code Changes:

### Memory Management Code Changes

#### PeopleAgent_v3.py

##### Earlier Code:
````python
# filepath: \PeopleAgent\PeopleAgentv3\PeopleAgent_v3.py
class PeopleAgent:
    def __init__(self, user_identifier):
        self.user_identifier = user_identifier
        # No conversation history
    def process_query(self, query):
        return self.some_llm_method(query)
````
##### New Code:
````python
# filepath: \PeopleAgent\PeopleAgentv3\PeopleAgent_v3.py
class PeopleAgent:
    def __init__(self, user_identifier):
        self.user_identifier = user_identifier
        self.conversation_history = []  # Added memory
    def clear_memory(self):
        # Clear the conversation history
        self.conversation_history.clear()
    def process_query(self, query, stream=False):
        if stream:
            return self._stream_response(query)
        else:
            response = self.some_llm_method(query)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
````

#### response_generation.py

##### Earlier Code:
````python
# filepath: \PeopleAgent\PeopleAgentv3\response_generation.py
def generate_response(agent, query):
    return agent.some_llm_method(query)
````
##### New Code:
````python
# filepath: \PeopleAgent\PeopleAgentv3\response_generation.py
def generate_streaming_response(agent, query):
    agent.conversation_history.append({"role": "user", "content": query})
    response = ""
    for chunk in agent.process_query(query, stream=True):
        response += chunk
        yield response   # Yield the updated response on the fly
    agent.conversation_history.append({"role": "assistant", "content": response})
````

#### UI_v1_1_memory_streaming.py

##### Earlier Code:
````python
# filepath: \PeopleAgent\PeopleAgentv3\UI_v1_1_memory_streaming.py
def sync_handle(input_text, history):
    response = asyncio.run(get_response(input_text, current_user["identifier"]))
    return response
````
##### New Code (Memory Management):
````python
# filepath: \PeopleAgent\PeopleAgentv3\UI_v1_1_memory_streaming.py
user_agents = {}
current_user = {"identifier": None, "profile_displayed": False}
async def get_or_create_agent(user_identifier):
    if user_identifier not in user_agents:
        user_agents[user_identifier] = PeopleAgent(user_identifier)
    return user_agents[user_identifier]
def sync_handle(input_text, history):
    is_exit = input_text.strip().lower() == "exit"
    if is_exit:
        if current_user["identifier"] in user_agents:
            user_agents[current_user["identifier"]].clear_memory()
            del user_agents[current_user["identifier"]]
        current_user["identifier"] = None
        return "Session ended..."
    # ...existing code...
````
##### Earlier Streaming Code:
````python
# filepath: \PeopleAgent\PeopleAgentv3\UI_v1_1_memory_streaming.py
def bot(message: str, history: list):
    response = asyncio.run(get_response(message, current_user["identifier"]))
    history.append({"role": "assistant", "content": response})
    yield history
````
##### New Streaming Code:
````python
# filepath: \PeopleAgent\PeopleAgentv3\UI_v1_1_memory_streaming.py
def bot(message: str, history: list):
    if some_condition_for_new_user:
        # handle new user identifier...
        pass
    else:
        agent = asyncio.run(get_or_create_agent(current_user["identifier"]))
        response_generator = agent.process_query(message, stream=True)
        history.append({"role": "assistant", "content": ""})
        for chunk in response_generator:
            logger.debug(f"Chunk received at {time.strftime('%H:%M:%S')}: {chunk[:50]}... (length: {len(chunk)})")
            history[-1]["content"] += chunk
            yield history

