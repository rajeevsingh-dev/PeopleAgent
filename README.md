# PeopleAgent

PeopleAgent - Intelligent Microsoft 365 User Information Assistant
A GenAI-powered conversational Chat AI that combines Microsoft Graph API data with Azure OpenAI to provide natural language interactions about Microsoft 365 users.


## Core Architecture
The application operates in three main flows:

#### 1. Query Analysis (Azure OpenAI)

- Interprets natural language queries
- Determines required data categories (profile, manager, devices, etc.)
- Converts user intent into structured API requests

#### 2. Data Retrieval (Microsoft Graph API)

- Fetches user information using application permissions
- Supports multiple data endpoints:
- User profiles and basic information
- Organizational structure (managers/reports)
- Device inventory
- Document access
- Team collaborations

#### 3. Response Generation (Azure OpenAI)

- Processes raw API data through LLM
- Generates natural language responses
- Provides conversational context management

## Features

- Microsoft Graph API integration
- User information retrieval
- Delegated access - sample code
- Application-level - sample code
- PeopleAgent - to provide user information


## Project Structure

```
PeopleAgent/
├── PeopleAgent/
│   ├── logs/
│   ├── parameters.json
│   └── PeopleAgent_v1.py
├── Samples/
│   ├── GetUserDetails-Application/
│   │   ├── GetAllUsers.py
│   │   └── parameters.json
│   └── GetUserDetails-Delegates/
│       └── GetUser.py
└── requirements.txt
```

## Prerequisites

- [Python 3.9 or higher](https://www.python.org/downloads/)

- [Microsoft Graph SDK](https://pypi.org/project/msgraph-sdk/) Use the Microsoft Graph SDK for Python

- [App Registration Guide](https://learn.microsoft.com/en-us/entra/identity-platform/scenario-daemon-app-registration) Register your application in Entra ID

- [Authentication Guide](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-daemon-app-call-api?pivots=workforce&tab=python-workforce&tabs=asp-dot-net-core-workforce%2Cnode-external) - Microsoft MSAL with client credentials flow

- [Graph API Documentation](https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0&tabs=http) Access user data using Microsoft Graph API.

- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service/) - For query analysis and response generation



## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PeopleAgent.git
   cd PeopleAgent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure parameters.json with your Entra ID credentials: 
   ```json
   {
    "authority": "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here",
    "client_id": "your_client_id",
    "scope": [ "https://graph.microsoft.com/.default" ],
    "secret": "The secret generated by AAD during your confidential app registration",
    "endpoint": "https://graph.microsoft.com/v1.0/users",
    "AOAI_ENDPOINT": "your_aoai_endpoint",
    "AOAI_KEY": "our_aoai_key",
    "AOAI_DEPLOYMENT": "your_deployment_name"
    }
   ```


### Sample Applications

##### GetUserDetails-Delegates/GetUser.py : 
Get specific user details using delegated permissions
##### GetUserDetails-Application/GetAllUsers.py :  
Retrieve all users in your organization using Application permissions

### PeopleAgent Code

Uses Client Credentials approach to fetch userDetails using Graph API. 
Data is ingested to LLM to get the interactive response.


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.


## Quick Links

[![Graph API](https://img.shields.io/badge/Graph%20API-Documentation-blue)](https://learn.microsoft.com/en-us/graph/api/overview)
[![Python SDK](https://img.shields.io/badge/Python-SDK-yellow)](https://github.com/microsoftgraph/msgraph-sdk-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)