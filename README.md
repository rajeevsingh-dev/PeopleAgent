# PeopleAgent

An AI assistant analyzing Microsoft 365 user queries and providing below information.
        - profile: Basic user information, timezone, location
        - manager: Manager details and location
        - reports: Direct reports information
        - devices: User's device information
        - colleagues: Team members and collaborators
        - documents: Authored documents and publications
        - access: System access information

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

- Python 3.9 or higher

- MS Graph SDK: https://pypi.org/project/msgraph-sdk/

- App Registartion : https://learn.microsoft.com/en-us/entra/identity-platform/scenario-daemon-app-registration

- Azure Identity (MSAL) : https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-daemon-app-call-api?pivots=workforce&tab=python-workforce&tabs=asp-dot-net-core-workforce%2Cnode-external

- Graph API : https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0&tabs=http

- Azure OpenAI : For natural language processing and response generation



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

GetUserDetails-Delegates/GetUser.py : Get specific user details using delegated permissions
GetUserDetails-Application/GetAllUsers.py :  Retrieve all users in your organization using Application permissions

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