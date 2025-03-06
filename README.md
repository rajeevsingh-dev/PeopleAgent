# PeopleAgent

A Python-based solution for interacting with Microsoft Graph API to manage user information and permissions.

## Features

- Microsoft Graph API integration
- User information retrieval
- Delegated access - sample code
- Application-level - sample code


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
- Entra ID registration
- Appropriate Microsoft Graph API permissions
- MSAL

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
     "tenant_id": "your-tenant-id",
     "client_id": "your-client-id",
     "client_secret": "your-client-secret"
   }
   ```

## Usage

### Basic Implementation

```python
from PeopleAgent import PeopleAgent

agent = PeopleAgent()
users = agent.get_all_users()
```

### Sample Applications

1. GetAllUsers.py - Retrieve all users in your organization
2. GetUser.py - Get specific user details using delegated permissions

## Documentation

Detailed documentation for each module can be found in the respective directories.

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