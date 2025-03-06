import sys
import json
import os
import asyncio
import logging
import requests
import msal
from datetime import datetime


from langchain_openai import AzureChatOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_logging(config):
    """
    Configure logging based on parameters from config file
    """
    log_config = config.get("logging", {})
    
    if not log_config.get("enabled", False):
        # Disable all logging if not enabled
        logging.getLogger().setLevel(logging.CRITICAL)
        return

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Generate log filename with timestamp if specified
    log_file = log_config.get("log_file", "people_agent.log")
    if "{timestamp}" in log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_file.format(timestamp=timestamp)
    
    log_path = os.path.join(log_dir, log_file)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config.get("level", "INFO").upper()),
        format=log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_path}")


def load_config():
    """
    Load configuration from parameters.json in this directory.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'parameters.json')
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logger.error("Config file not found.")
        sys.exit(1)

def get_access_token(config):
    """
    Acquire access token using MSAL (client credentials approach).
    """
    app = msal.ConfidentialClientApplication(
        client_id=config["client_id"],
        authority=config["authority"],
        client_credential=config["secret"]
    )

    # Try to get token from cache first
    result = app.acquire_token_silent(config["scope"], account=None)
    if not result:
        logger.info("No token in cache. Getting new token...")
        result = app.acquire_token_for_client(scopes=config["scope"])

    if "access_token" in result:
        return result["access_token"]
    else:
        logger.error(f"Error getting token: {result.get('error')}")
        logger.error(f"Error description: {result.get('error_description')}")
        return None

class PeopleAgent:
    def __init__(self, user_identifier):
        """
        This agent uses a client credentials flow for Graph API queries,
        and loads Azure OpenAI settings from parameters.json.
        'user_identifier' is the email or object ID to retrieve data for.
        """
       
        self.logger = logging.getLogger(__name__)
        self.config = load_config()

        self.access_token = get_access_token(self.config)
        if not self.access_token:
            self.logger.error("Failed to acquire access token.")
            sys.exit(1)

        self.logger.info(f"Initializing PeopleAgent for user: {user_identifier}")
        
        self.user_identifier = user_identifier

        # Read Azure OpenAI settings from parameters.json
        self.openai_client = AzureChatOpenAI(
            azure_deployment=self.config.get("AOAI_DEPLOYMENT", ""),
            api_version=self.config.get("AOAI_API_VERSION", "2024-02-15-preview"),
            api_key=self.config.get("AOAI_KEY", ""),
            azure_endpoint=self.config.get("AOAI_ENDPOINT", "")
        )

    # -----------------------------------------------------------------------
    # 1. Query Analysis (using Azure OpenAI)
    # -----------------------------------------------------------------------
    async def analyze_query(self, user_query):
        """
        Determine the intent of the user query using Azure OpenAI.
        """
        system_prompt = """
        You are an AI assistant analyzing Microsoft 365 user queries.
        Determine which data needs to be fetched based on the query.
        Return one or more of these categories (comma-separated):
        - profile: Basic user information, timezone, location
        - manager: Manager details and location
        - reports: Direct reports information
        - devices: User's device information
        - colleagues: Team members and collaborators
        - documents: Authored documents and publications
        - access: System access information
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]

        intent = self.openai_client.invoke(messages).content.strip().lower()
        return intent.split(',')

    # -----------------------------------------------------------------------
    # 2. Data Fetching (using Microsoft Graph API) & formatting
    # -----------------------------------------------------------------------
    async def get_all_users(self):
        """
        Get all users in the tenant using '/users' with app-only permissions.
        """
        try:
            endpoint = self.config.get("endpoint", "https://graph.microsoft.com/v1.0/users")
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting all users: {str(e)}"
    
    async def find_user_by_name(self, name):
        """
         Search for users by display name and return matching users.
        """
        try:
            # Use $filter to search by displayName
            endpoint = f"{self.config.get('endpoint', 'https://graph.microsoft.com/v1.0/users')}?$filter=startswith(displayName,'{name}')"
            headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error searching users: {str(e)}"


    async def get_user_profile(self):
        """
        Fetch the user's profile using '/users/{userIdOrUPN}' 
        instead of '/me' for app-only permission.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self.user_identifier}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting profile: {str(e)}"

    async def get_manager_info(self):
        """
        Fetch the user's manager using '/users/{userIdOrUPN}/manager'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self.user_identifier}/manager"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting manager info: {str(e)}"

    async def get_direct_reports(self):
        """
        Fetch the user's direct reports using '/users/{userIdOrUPN}/directReports'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self.user_identifier}/directReports"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting direct reports: {str(e)}"

    async def get_devices(self):
        """
        Fetch the user's devices using '/users/{userIdOrUPN}/managedDevices'
        in app-only mode.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self.user_identifier}/managedDevices"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting devices: {str(e)}"

    async def get_colleagues(self):
        """
        The /people endpoint usually needs delegated permissions to reflect "people relevant to this user."
        For an app-only token, it may not be fully supported.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self.user_identifier}/people"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting colleagues: {str(e)}"

    async def get_documents(self):
        """
        Fetch the user's recent documents with '/users/{userIdOrUPN}/drive/recent'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self.user_identifier}/drive/recent"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting documents: {str(e)}"

    def format_data(self, data_type, data):
        """
        Format different types of Graph API responses into a more readable structure.
        """
        if isinstance(data, str):
            return data  # Likely an error message

        formatted = {}
        try:
            if data_type == "profile":
                formatted = {
                    "name": data.get("displayName"),
                    "email": data.get("mail"),
                    "title": data.get("jobTitle"),
                    "location": data.get("officeLocation", "Unknown"),
                    "timezone": data.get("mailboxSettings", {}).get("timeZone", "Unknown")
                }
            elif data_type == "manager":
                formatted = {
                    "name": data.get("displayName"),
                    "title": data.get("jobTitle"),
                    "email": data.get("mail"),
                    "location": data.get("officeLocation", "Unknown")
                }
            elif data_type == "devices":
                value_list = data.get("value", [])
                formatted = [
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
                # Data from "users/{id}/people"
                formatted = data.get("value", [])
            elif data_type == "documents":
                # Data from "users/{id}/drive/recent"
                formatted = data.get("value", [])
            elif data_type == "reports":
                # Data from "users/{id}/directReports"
                formatted = data.get("value", [])
            elif data_type == "all_users":
                # Format the JSON from /v1.0/users
                user_list = data.get("value", [])
                formatted_users = []
                for user_entry in user_list:
                    formatted_users.append({
                        "displayName": user_entry.get("displayName"),
                        "userPrincipalName": user_entry.get("userPrincipalName"),
                        "mail": user_entry.get("mail"),
                        "jobTitle": user_entry.get("jobTitle", ""),
                        # Add more fields here as needed
                    })
                formatted = formatted_users
        except Exception as e:
            return f"Error formatting {data_type} data: {str(e)}"

        return formatted

    # -----------------------------------------------------------------------
    # 3. Response Generation (using Azure OpenAI)
    # -----------------------------------------------------------------------
    def generate_response(self, query, context):
        """
        Generate a natural language response from the structured data using Azure OpenAI.
        """
        system_prompt = """
        You are an AI assistant specializing in Microsoft 365 user information.
        You can provide detailed information about:
        1. User identity, profile, and location details
        2. Manager information including their location/region
        3. Time zone and working hours
        4. Reporting structure (both up and down)
        5. Team members and frequent collaborators
        6. System access and permissions
        7. Device inventory and status
        8. Document authorship and publications

        Provide natural, professional responses based on the available data.
        If information is missing, acknowledge it clearly.
        Format complex data in an easily readable way.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {query}\nAvailable Data: {context}"}
        ]
        return self.openai_client.invoke(messages).content

    async def process_query(self, user_query):
        """
        Main method tying together:
        1) Query analysis
        2) Data fetching
        3) Response generation
        """
        # Determine required data types
        intents = await self.analyze_query(user_query)

        # Collect all relevant data
        context = {}
        for intent in intents:
            intent = intent.strip()
            if intent == "profile":
                data = await self.get_user_profile()
                context["profile"] = self.format_data("profile", data)
            elif intent == "manager":
                data = await self.get_manager_info()
                context["manager"] = self.format_data("manager", data)
            elif intent == "reports":
                data = await self.get_direct_reports()
                context["reports"] = self.format_data("reports", data)
            elif intent == "devices":
                data = await self.get_devices()
                context["devices"] = self.format_data("devices", data)
            elif intent == "colleagues":
                data = await self.get_colleagues()
                context["colleagues"] = self.format_data("colleagues", data)
            elif intent == "documents":
                data = await self.get_documents()
                context["documents"] = self.format_data("documents", data)
            elif intent == "all_users":
                # Optionally handle an "all_users" intent
                data = await self.get_all_users()
                context["all_users"] = self.format_data("all_users", data)

        # Generate final response
        return self.generate_response(user_query, context)

async def main():
    """
    Entry point for user interaction in a loop.
    This function will create an instance of PeopleAgent,
    handle user input, and display the generated response.
    """
    try:
        print("USERS MUST ENTER A SPECIFIC USER IDENTIFIER (email, ID, or name) FOR APP-ONLY QUERIES.\n")
        target_user = input("Enter the user's email, Azure AD object ID, or name (leave blank to get all users): ")
        # Load config and setup logging first
        config = load_config()
        setup_logging(config)

        # Create initial agent
        if not target_user:
            agent = PeopleAgent("")
        else:
            # If input doesn't look like email or GUID, try name search
            if "@" not in target_user and len(target_user) != 36:
                temp_agent = PeopleAgent("")  # Temporary agent for search
                print("\nSearching users by name...")
                search_results = await temp_agent.find_user_by_name(target_user)
                
                if isinstance(search_results, str):  # Error occurred
                    print(f"\nError: {search_results}")
                    return 1
                    
                matches = search_results.get("value", [])
                if not matches:
                    print("\nNo users found with that name.")
                    return 1
                    
                if len(matches) > 1:
                    print("\nMultiple users found:")
                    for i, user in enumerate(matches, 1):
                        print(f"{i}. {user.get('displayName')} ({user.get('mail')})")
                    choice = input("\nEnter the number of the user you want to inspect (or 0 to exit): ")
                    if not choice.isdigit() or int(choice) == 0:
                        print("\nExiting...")
                        return 0
                    if int(choice) < 1 or int(choice) > len(matches):
                        print("\nInvalid choice. Exiting...")
                        return 1
                    target_user = matches[int(choice)-1].get('mail')
                else:
                    target_user = matches[0].get('mail')
                    print(f"\nFound user: {matches[0].get('displayName')} ({target_user})")

            agent = PeopleAgent(target_user)

        print("\nWelcome to the Microsoft 365 People Agent!")
        print("You can ask about a person's profile, manager, devices, or switch to another user.")
        print("Type 'exit' to quit.\n")

        while True:
            try:
                # If the user identifier is empty, show all users
                if not agent.user_identifier.strip():
                    print("\nFetching all users (app-only mode)...")
                    all_users_raw = await agent.get_all_users()
                    all_users_formatted = agent.format_data("all_users", all_users_raw)
                    print("\nAll Users:", all_users_formatted)
                    print('\n(Enter a valid user ID/email/name to inspect a particular user, or type "exit")')
                    new_identifier = input("\nUser ID/Email/Name to inspect? ").strip()
                    if new_identifier.lower() == "exit":
                        print("\nGracefully shutting down...")
                        break

                    # If new identifier isn't email/GUID, try name search
                    if "@" not in new_identifier and len(new_identifier) != 36:
                        print("\nSearching users by name...")
                        search_results = await agent.find_user_by_name(new_identifier)
                        matches = search_results.get("value", [])
                        
                        if matches:
                            if len(matches) > 1:
                                print("\nMultiple users found:")
                                for i, user in enumerate(matches, 1):
                                    print(f"{i}. {user.get('displayName')} ({user.get('mail')})")
                                choice = input("\nEnter the number of the user you want to inspect (or 0 to exit): ")
                                if not choice.isdigit() or int(choice) == 0:
                                    continue
                                if int(choice) < 1 or int(choice) > len(matches):
                                    print("\nInvalid choice.")
                                    continue
                                new_identifier = matches[int(choice)-1].get('mail')
                            else:
                                new_identifier = matches[0].get('mail')
                                print(f"\nFound user: {matches[0].get('displayName')} ({new_identifier})")
                        else:
                            print("\nNo users found with that name.")
                            continue

                    # Update agent with new user
                    agent = PeopleAgent(new_identifier)
                    continue

                # Either ask about current user, or switch to a new one
                prompt_msg = (
                    "\nAsk a question about this user, "
                    "enter another user's email/ID/name to switch, "
                    "or type 'exit' to quit:\n"
                )
                user_input = input(prompt_msg).strip()

                # Check for exit
                if user_input.lower() == 'exit':
                    print("\nGracefully shutting down...")
                    break

                # If input might be a user identifier, try switching users
                if "@" in user_input or len(user_input) == 36 or (user_input and not user_input.startswith("what") and not user_input.startswith("who")):
                    if "@" not in user_input and len(user_input) != 36:
                        # Try name search
                        print("\nSearching users by name...")
                        search_results = await agent.find_user_by_name(user_input)
                        matches = search_results.get("value", [])
                        
                        if matches:
                            if len(matches) > 1:
                                print("\nMultiple users found:")
                                for i, user in enumerate(matches, 1):
                                    print(f"{i}. {user.get('displayName')} ({user.get('mail')})")
                                choice = input("\nEnter the number of the user you want to inspect (or 0 to cancel): ")
                                if not choice.isdigit() or int(choice) == 0:
                                    continue
                                if int(choice) < 1 or int(choice) > len(matches):
                                    print("\nInvalid choice.")
                                    continue
                                user_input = matches[int(choice)-1].get('mail')
                            else:
                                user_input = matches[0].get('mail')
                                print(f"\nFound user: {matches[0].get('displayName')} ({user_input})")
                        else:
                            print("\nNo users found with that name. Treating as a question.")
                            print("\nProcessing your query...")
                            response = await agent.process_query(user_input)
                            print("\nResponse:", response)
                            continue

                    print(f"\nSwitching to user: {user_input}")
                    agent = PeopleAgent(user_input)
                    continue

                # Otherwise, treat it as a question about the current user
                print("\nProcessing your query...")
                response = await agent.process_query(user_input)
                print("\nResponse:", response)

            except KeyboardInterrupt:
                print("\n\nReceived keyboard interrupt. Shutting down gracefully...")
                break
            except Exception as e:
                print(f"\nError processing query: {str(e)}")
                print("Please try again or type 'exit' to quit.")

    except KeyboardInterrupt:
        print("\n\nShutdown requested. Exiting...")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        return 1
    finally:
        print("\nThank you for using the People Agent!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)