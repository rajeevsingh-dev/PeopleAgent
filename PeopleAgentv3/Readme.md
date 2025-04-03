# PeopleAgent_v3

This version introduces advanced memory management and streaming capabilities to maintain conversation context and deliver real-time responses. It builds on previous implementations by integrating persistent storage, context sharing, and enhanced logging to optimize conversational interactions.

### Memory/Chat History

- **Memory Storage:** Added a conversation history array in the `PeopleAgent` class (e.g., `self.conversation_history`) to store each interaction.
- **History Management:** Introduced methods to add new entries and clear the conversation history (e.g., `clear_memory()`).
- **Agent Persistence:** Created a global dictionary in the UI code (`user_agents`) to store `PeopleAgent` instances keyed by user identifier. Ensures each user session maintains its context between interactions.
- **Context Sharing:** Modified response generation (in `response_generation.py` and `PeopleAgent.process_query`) to include relevant conversation history in the prompt for the LLM, ensuring contextual responses.
- **Memory Lifecycle:** Implemented logic in the UI (`sync_handle` and `clear_conversation` functions) to clear the conversation history when switching users or ending a session (e.g., when the user types "exit").

### Streaming

- **Streaming Response Handling:** Modified the `PeopleAgent.process_query()` method to accept a stream flag and, if enabled, return a generator yielding response chunks as they are generated.
- **Incremental Data Delivery:** Implemented an internal `_stream_response()` method in `PeopleAgent` to interact with the LLM in streaming mode, appending each chunk to the conversation history while yielding it.
- **Real-Time UI Updates:** Updated the UI's `bot()` function to iterate over the streaming generator, logging each chunk along with a timestamp.
The UI appends each received chunk to the conversation history, enabling real-time display of the response.

### Parallel API calls with API-level caching

- **Parallel Execution:** Modified the `PeopleAgent.process_query()` method to initiate multiple API calls concurrently using `asyncio.create_task`.Runs various API calls (e.g., user profile, manager, devices, etc.) in parallel to reduce latency.
- **API-Level Caching:** Decorated individual API methods with a TTL cache (e.g., 60 seconds) to store and reuse responses.Cached results are returned for repeated calls within the TTL, avoiding redundant API requests.
- **Final Response Caching:** The final combined response is hashed (based on the query and the aggregated context) to create a unique cache key.
If a response is cached and still valid, it is reused instead of invoking the LLM again.

> **NOTE:** This will be further improved using advanced caching strategies, such as Semantic Caching or Conversion History/Context Caching.


## Key File and Code Changes

#### Memory Management:
- **people_agent.py**: Now maintains a conversation history and offers a `clear_memory()` method.
- **response_generation.py**: Appends both the user query and agent response to the history.
- **UI_v3_memory_streaming.py**: Caches `PeopleAgent` instances per user and clears memory when sessions end or users switch.

#### Streaming:
- **people_agent.py**: Supports streaming responses via `process_query()`, yielding response chunks.
- **response_generation.py**: Includes a generator function to yield updated responses. (optional, no changes)
- **UI_v3_memory_streaming.py**: Iterates over the streaming generator, logs each chunk with timing details, and updates the UI in real time.

#### Parallel API calls with API-level caching:
- **PeopleAgent.process_query():** Initiates multiple API calls concurrently using `asyncio.create_task()` to fetch various data (e.g., user profile, manager, devices, etc.) in parallel, thereby reducing overall latency.
- **API-Level Caching:**  Individual API methods (such as `get_user_profile()`, `get_manager_info()`, `get_direct_reports()`, etc.) have been decorated with a TTL cache (e.g., 60 seconds). This ensures that repeated calls with the same parameters within the TTL return cached results, avoiding redundant API requests.
- **Final Response Caching:**  After aggregating data from all parallel API calls, the final combined response is generated. A unique cache key is built based on the query and a hash of the aggregated context; if a valid cached response exists, it is returned directly instead of invoking the LLM again.

> **NOTE:** Caching, Streaming will be further improved.

## Deployment Steps

1. Install the required Python packages using `pip install -r requirements.txt`.
2. Set up environment variables for Microsoft Graph, Azure OpenAI, and streaming configurations.
3. Deploy the application using your preferred method (App Service, Docker etc.).
4. Monitor logs and performance metrics post-deployment for any necessary tuning.

> **NOTE:** For full details on Deployment, please navigate to [Readme_deployment.md](./Readme_deployment.md).