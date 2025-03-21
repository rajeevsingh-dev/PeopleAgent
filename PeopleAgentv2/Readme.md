
#### PeopleAgent_v2 (Enhanced Version)
The improved version with additional features:

- Module based code
- Enhanced performance and reliability
- Improved context management for more natural conversations
- Additional data endpoints including team memberships and document access
- Better error handling and logging capabilities
- Support for more complex queries and relationship mapping
- Optimized API usage to reduce latency and token consumption

Example queries you can ask:
- "Who is the manager of Jane Smith?"
- "What devices does John Doe use?"
- "Show me all users in the Marketing department"
- "What projects is Alex working on?"

## PeopleAgentv2 Directory Structure

The PeopleAgentv2 folder contains the enhanced version of our solution with improved architecture and capabilities:

```
PeopleAgentv2/

├── CORE/
│   ├── authentication.py       # Microsoft Graph authentication handler
│   ├── conversation.py         # Conversation state management
│   ├── graph_client.py         # Microsoft Graph API client wrapper
│   ├── llm_processor.py        # Azure OpenAI integration for language processing
│   └── query_analyzer.py       # User query analysis and intent detection
|   |__ 
├── UTIL/
│   ├── error_handler.py        # Centralized error handling
│   ├── logger.py               # Logging utility functions
│   └── response_formatter.py   # Output formatting for different response types
├── UI/
│   ├── error_handler.py        # Centralized error handling
│   ├── logger.py               # Logging utility functions
│   └── response_formatter.py   # Output formatting for different response types


```

### Key Files in PeopleAgentv2

- **PeopleAgent_v2.py**: Main application entry point that orchestrates the enhanced conversation flow
- **authentication.py**: Handles secure authentication with Microsoft Graph using MSAL
- **graph_client.py**: Manages all Graph API requests with improved caching and error handling
- **llm_processor.py**: Processes natural language through Azure OpenAI with enhanced prompt engineering
- **query_analyzer.py**: Analyzes user queries to determine intent and required Graph API endpoints
- **conversation.py**: Maintains conversation state and history for contextual responses
- **response_formatter.py**: Formats API responses into natural language with improved readability

The v2 implementation features a modular architecture that separates concerns for better maintainability, improved error handling, and enhanced performance when processing user queries about Microsoft 365 users.