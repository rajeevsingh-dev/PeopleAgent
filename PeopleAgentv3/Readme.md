# PeopleAgent_v3

## Overview
This version introduces advanced memory management and streaming capabilities to maintain conversation context and deliver real-time responses. It builds on previous implementations by integrating persistent storage, context sharing, and enhanced logging to optimize conversational interactions.

### Memory/Chat History

**Memory Storage:**
- Added a conversation history array in the `PeopleAgent` class (e.g., `self.conversation_history`) to store each interaction.
**History Management:**
- Introduced methods to add new entries and clear the conversation history (e.g., `clear_memory()`).
- Optionally, limits on history size can be implemented later.
**Agent Persistence:**
- Created a global dictionary in the UI code (`user_agents`) to store `PeopleAgent` instances keyed by user identifier.
- Ensures each user session maintains its context between interactions.
**Context Sharing:**
- Modified response generation (in `response_generation.py` and `PeopleAgent.process_query`) to include relevant conversation history in the prompt for the LLM, ensuring contextual responses.
**Memory Lifecycle:**
- Implemented logic in the UI (`sync_handle` and `clear_conversation` functions) to clear the conversation history when switching users or ending a session (e.g., when the user types "exit").
**Logging:**
- Added informative logging (`info`/`debug`) in both `PeopleAgent` and UI code to monitor when memory is created, updated, or cleared.

### Streaming

**Streaming Response Handling:**
- Modified the `PeopleAgent.process_query()` method to accept a stream flag and, if enabled, return a generator yielding response chunks as they are generated.
**Incremental Data Delivery:**
- Implemented an internal `_stream_response()` method in `PeopleAgent` to interact with the LLM in streaming mode, appending each chunk to the conversation history while yielding it.
**Real-Time UI Updates:**
- Updated the UI's `bot()` function to iterate over the streaming generator, logging each chunk along with a timestamp.
- The UI appends each received chunk to the conversation history, enabling real-time display of the response.

**Logging for Streaming:**
- Added detailed logging within the streaming loop (including each chunk's timestamp and length) to monitor and debug the streaming process.

## Key File and Code Changes

#### Memory Management:
- **people_agent.py**: Now maintains a conversation history and offers a `clear_memory()` method.
- **response_generation.py**: Appends both the user query and agent response to the history.
- **UI_v1_1_memory_streaming.py**: Caches `PeopleAgent` instances per user and clears memory when sessions end or users switch.

#### Streaming:
- **people_agent.py**: Supports streaming responses via `process_query()`, yielding response chunks.
- **response_generation.py**: Includes a generator function to yield updated responses.
- **UI_v1_1_memory_streaming.py**: Iterates over the streaming generator, logs each chunk with timing details, and updates the UI in real time.

> **NOTE:** For full details on all code changes, please navigate to [Readme_codechanges.md](./Readme_codechanges.md).

## Deployment Steps

1. Install the required Python packages using `pip install -r requirements.txt`.
2. Set up environment variables for Microsoft Graph, Azure OpenAI, and streaming configurations.
3. Run tests to confirm module integration using `pytest`.
4. Deploy the application using your preferred method (Docker, cloud service, etc.).
5. Monitor logs and performance metrics post-deployment for any necessary tuning.

> **NOTE:** For full details on Deployment, please navigate to [Readme_deployment.md](./Readme_deployment.md).