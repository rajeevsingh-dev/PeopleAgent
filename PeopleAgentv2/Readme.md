# PeopleAgent_v2 (Enhanced Version)

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

```
PeopleAgentv2/

├── CORE/
|   |__ main.py                 # serves as the primary entry point for the PeopleAgent application.
│   ├── people_agent.py         # Main application entry point that orchestrates the enhanced conversation flow.
│   ├── ai_analysis.py          # Used for query processing, file is a core component of the PeopleAgent system that handles natural language query analysis.
│   ├── response_generation.py  # Used for converting structured data into natural language responses using Azure OpenAI.
|   |__ ms_grapg_client.py      # Used for Microsoft Graph API interactions.
|   |__ auth.py                 # Used for Microsoft authentication, Acquire access token using MSAL (client credentials).
|   |__ data_service.py         # to be used for Data Caching (Redis-based caching, Reduces API calls to Microsoft Graph etc.)
|   |__ services.py             # to be designed as a service layer module for handling user-related operations in the PeopleAgent application
├── UTIL/
│   ├── logging_setup.py        # The purpose of logging_setup.py is to configure the application's logging system. 
├── UI/
│   ├── UI.py                   # Front end related code
```

The v2 implementation features a modular architecture that separates concerns for better maintainability, improved error handling, and enhanced performance when processing user queries about Microsoft 365 users.